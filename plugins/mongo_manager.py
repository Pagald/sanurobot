import logging
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply
from info import ADMINS
from database.multi_mongo import multi_db
from database.vps_cache import vps_cache

logger = logging.getLogger(__name__)

def make_pbar(percent: float) -> str:
    filled = int(percent // 10)
    filled = min(max(filled, 0), 10)
    return "█" * filled + "░" * (10 - filled)

async def render_mongo_panel():
    summaries = await multi_db.get_databases_summary()
    vps_stats = await vps_cache.get_stats()

    total_dbs = len(summaries)
    writable_count = sum(1 for d in summaries if not d.get("read_only", False) and d.get("usage_percent", 0) < 90.0)
    ro_count = total_dbs - writable_count

    txt = "🗄 <b><u>MULTI-MONGODB CLUSTER MANAGER</u></b>\n\n"
    txt += f"📊 <b>Total Clusters:</b> <code>{total_dbs}</code> | ✍️ <b>Writable:</b> <code>{writable_count}</code> | 🔒 <b>Read-Only:</b> <code>{ro_count}</code>\n\n"

    for i, doc in enumerate(summaries, 1):
        alias = doc.get("db_alias", f"DB-{i}")
        db_name = doc.get("db_name", "N/A")
        col_name = doc.get("col_name", "N/A")
        usage = doc.get("usage_percent", 0.0)
        curr_mb = doc.get("current_size_mb", 0.0)
        max_mb = doc.get("max_size_mb", 500.0)
        files = doc.get("file_count", 0)
        is_ro = doc.get("read_only", False) or usage >= 90.0
        is_primary = doc.get("is_primary", False)

        pbar = make_pbar(usage)
        tag = "👑 [PRIMARY]" if is_primary else ""
        writer_tag = "⚡ [WRITABLE]" if not is_ro else "🔒 [READ-ONLY / FULL]"

        txt += f"<b>{i}. {alias} ({db_name})</b> {tag}\n"
        txt += f"   • <b>Collection:</b> <code>{col_name}</code>\n"
        txt += f"   • <b>Usage:</b> <code>[{pbar}]</code> <b>{usage}%</b> ({curr_mb} MB / {max_mb} MB)\n"
        txt += f"   • <b>Status:</b> <b>{writer_tag}</b>\n"
        txt += f"   • <b>Files:</b> <code>{files:,}</code>\n\n"

    cached_q = vps_stats.get("total_cached_queries", 0)
    cached_mb = vps_stats.get("disk_size_mb", 0.0)
    cached_hits = vps_stats.get("total_hits", 0)
    txt += f"💾 <b><u>VPS Disk Cache Status</u>:</b>\n"
    txt += f"   • <b>Cached Queries:</b> <code>{cached_q:,}</code>\n"
    txt += f"   • <b>VPS Disk Used:</b> <code>{cached_mb} MB</code>\n"
    txt += f"   • <b>Total Hits:</b> <code>{cached_hits:,}</code> (Zero Atlas Bandwidth!)\n\n"
    txt += "<i>🛡 Auto-Protection: Jab bhi koi DB >= 90% full hoga, bot naye files usme save nahi karega aur next free DB par switch ho jayega!</i>"

    buttons = [
        [
            InlineKeyboardButton("➕ Add Database", callback_data="mongo_add"),
            InlineKeyboardButton("🗑 Remove Database", callback_data="mongo_remove")
        ],
        [
            InlineKeyboardButton("🔒 Toggle Read-Only", callback_data="mongo_toggle"),
            InlineKeyboardButton("🔄 Refresh Stats", callback_data="mongo_refresh")
        ],
        [
            InlineKeyboardButton("🧹 Flush VPS Cache", callback_data="mongo_flush_cache")
        ],
        [
            InlineKeyboardButton("⨳ Close ⨳", callback_data="close_data")
        ]
    ]

    return txt, InlineKeyboardMarkup(buttons)

@Client.on_message(filters.command("mongo") & filters.user(ADMINS))
async def mongo_manager_cmd(client, message):
    msg = await message.reply_text("<b>⏳ Fetching MongoDB Cluster Status...</b>")
    try:
        txt, markup = await render_mongo_panel()
        await msg.edit_text(txt, reply_markup=markup, parse_mode=enums.ParseMode.HTML)
    except Exception as e:
        logger.error(f"[Mongo Command] Error: {e}", exc_info=True)
        await msg.edit_text(f"❌ <b>Error fetching cluster status:</b> <code>{e}</code>")

@Client.on_callback_query(filters.regex(r"^mongo_") & filters.user(ADMINS))
async def mongo_callback_handler(client, query):
    action = query.data

    if action == "mongo_menu" or action == "mongo_refresh":
        await query.answer("Refreshing stats... ⏳")
        txt, markup = await render_mongo_panel()
        try:
            await query.message.edit_text(txt, reply_markup=markup, parse_mode=enums.ParseMode.HTML)
        except Exception:
            pass

    elif action == "mongo_add":
        await query.answer()
        prompt_txt = (
            "➕ <b><u>Add New MongoDB Cluster</u></b>\n\n"
            "Please reply to this message with your Database details in the following format:\n\n"
            "<code>db_url | database_name | collection_name</code>\n\n"
            "<b>Example:</b>\n"
            "<code>mongodb+srv://user:pass@cluster.mongodb.net | SanuBot | Lazy_files</code>\n\n"
            "<i>Note: Storage limit is set to 500 MB (Atlas M0 Free Tier) with 90% auto-protection.</i>"
        )
        await query.message.reply_text(
            prompt_txt,
            reply_markup=ForceReply(selective=True),
            parse_mode=enums.ParseMode.HTML
        )

    elif action == "mongo_remove":
        await query.answer()
        summaries = await multi_db.get_databases_summary()
        buttons = []
        for d in summaries:
            if not d.get("is_primary"):
                alias = d.get("db_alias", "DB")
                db_name = d.get("db_name", "")
                buttons.append([InlineKeyboardButton(f"🗑 Remove {alias} ({db_name})", callback_data=f"mongo_del#{d['_id']}")])
        
        buttons.append([InlineKeyboardButton("◀️ Back", callback_data="mongo_menu")])

        if len(buttons) == 1:
            await query.answer("Sirf Primary Database maujood hai, use delete nahi kiya ja sakta!", show_alert=True)
            return

        await query.message.edit_text(
            "🗑 <b><u>Select Database To Remove</u>:</b>\n\n<i>Note: Yeh database bot se disconnect ho jayega, par actual data delete nahi hoga.</i>",
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML
        )

    elif action == "mongo_toggle":
        await query.answer()
        summaries = await multi_db.get_databases_summary()
        buttons = []
        for d in summaries:
            alias = d.get("db_alias", "DB")
            is_ro = d.get("read_only", False) or d.get("usage_percent", 0) >= 90.0
            status_txt = "🔒 Read-Only" if is_ro else "✍️ Writable"
            buttons.append([InlineKeyboardButton(f"{alias} ({status_txt}) ➡️ Toggle", callback_data=f"mongo_ro#{d['_id']}")])
        
        buttons.append([InlineKeyboardButton("◀️ Back", callback_data="mongo_menu")])
        await query.message.edit_text(
            "🔒 <b><u>Toggle Read-Only / Writable Status</u>:</b>\n\n<i>Kisi bhi database ko manually Read-Only ya Writable set karein:</i>",
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML
        )

    elif action == "mongo_flush_cache":
        deleted = await vps_cache.clear()
        await query.answer(f"🧹 VPS Disk Cache Flushed! ({deleted} queries freed)", show_alert=True)
        txt, markup = await render_mongo_panel()
        try:
            await query.message.edit_text(txt, reply_markup=markup, parse_mode=enums.ParseMode.HTML)
        except Exception:
            pass

@Client.on_callback_query(filters.regex(r"^mongo_del#") & filters.user(ADMINS))
async def mongo_delete_callback(client, query):
    db_id = query.data.split("#")[1]
    success, msg = await multi_db.remove_database(db_id)
    await query.answer(msg, show_alert=True)
    txt, markup = await render_mongo_panel()
    try:
        await query.message.edit_text(txt, reply_markup=markup, parse_mode=enums.ParseMode.HTML)
    except Exception:
        pass

@Client.on_callback_query(filters.regex(r"^mongo_ro#") & filters.user(ADMINS))
async def mongo_toggle_ro_callback(client, query):
    db_id = query.data.split("#")[1]
    success, msg = await multi_db.toggle_read_only(db_id)
    await query.answer(msg, show_alert=True)
    txt, markup = await render_mongo_panel()
    try:
        await query.message.edit_text(txt, reply_markup=markup, parse_mode=enums.ParseMode.HTML)
    except Exception:
        pass

# ForceReply message listener for Adding New MongoDB cluster
@Client.on_message(filters.reply & filters.user(ADMINS) & filters.private)
async def mongo_add_reply_listener(client, message):
    if not message.reply_to_message or not message.reply_to_message.text:
        return

    if "Add New MongoDB Cluster" in message.reply_to_message.text:
        raw_text = message.text.strip()
        parts = [p.strip() for p in raw_text.split("|")]
        if len(parts) != 3:
            return await message.reply_text(
                "❌ <b>Invalid Format!</b>\n\nPlease use exactly this format:\n\n"
                "<code>db_url | database_name | collection_name</code>",
                parse_mode=enums.ParseMode.HTML
            )

        db_url, db_name, col_name = parts
        status_msg = await message.reply_text(
            f"⏳ <b>Connecting and validating cluster <code>{db_name}</code>... Please wait...</b>",
            parse_mode=enums.ParseMode.HTML
        )

        success, res_msg = await multi_db.add_database(db_url, db_name, col_name)
        await status_msg.edit_text(res_msg, parse_mode=enums.ParseMode.HTML)
        if success:
            try:
                txt, markup = await render_mongo_panel()
                await message.reply_text(txt, reply_markup=markup, parse_mode=enums.ParseMode.HTML)
            except Exception:
                pass
