import logging
import asyncio
import re
import time
import humanize
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait
from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, ChatAdminRequired, UsernameInvalid, UsernameNotModified
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from info import ADMINS, LAZY_RENAMERS, LAZY_MODE
from info import INDEX_REQ_CHANNEL as LOG_CHANNEL
from database.ia_filterdb import save_file, save_files_batch
from utils import temp, to_small_caps
from lazybot import LazyPrincessBot

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
lock = asyncio.Lock()


# ─── DB-size choice step: ask Large or Small before indexing ──────────────────

@Client.on_callback_query(filters.regex(r'^dbsize#'))
async def dbsize_choice(bot, query):
    _, db_type, chat, lst_msg_id, from_user = query.data.split("#")

    if lock.locked():
        return await query.answer('Wait until previous process complete.', show_alert=True)

    await query.answer(f"Starting {db_type.title()} DB indexing…", show_alert=True)

    msg = query.message
    await msg.edit(
        f"⏳ Starting Indexing (<b>{'🐘 Large' if db_type == 'large' else '🐇 Small'} Database</b> mode)…",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(f"🛑 {to_small_caps('Cancel')}", callback_data='index_cancel')]]
        )
    )

    try:
        chat_int = int(chat)
    except Exception:
        chat_int = chat

    await index_files_to_db(int(lst_msg_id), chat_int, msg, bot, large_mode=(db_type == "large"))


@Client.on_callback_query(filters.regex(r'^index'))
async def index_files(bot, query):
    if query.data.startswith('index_cancel'):
        temp.CANCEL = True
        return await query.answer("Cancelling Indexing")
    
    if query.data.startswith('index_dbsize#'):
        parts = query.data.split("#")
        db_type = parts[1]
        chat = parts[3]
        lst_msg_id = parts[4]
        from_user = parts[5]

        if lock.locked():
            return await query.answer('Wait until previous process complete.', show_alert=True)

        msg = query.message
        await query.answer('Processing...⏳', show_alert=True)
        try:
            chat_int = int(chat)
        except Exception:
            chat_int = chat

        await index_files_to_db(int(lst_msg_id), chat_int, msg, bot, large_mode=(db_type == "large"))
        return

    _, lazydeveloperr, chat, lst_msg_id, from_user = query.data.split("#")
    if lazydeveloperr == 'reject':
        await query.message.delete()
        await bot.send_message(int(from_user),
                               f'Your Submission for indexing {chat} has been decliened by our moderators.',
                               reply_to_message_id=int(lst_msg_id))
        return

    if lock.locked():
        return await query.answer('Wait until previous process complete.', show_alert=True)
    msg = query.message

    await query.answer('Processing...⏳', show_alert=True)
    if int(from_user) not in ADMINS:
        await bot.send_message(int(from_user),
                               f'Your Submission for indexing {chat} has been accepted by our moderators and will be added soon.',
                               reply_to_message_id=int(lst_msg_id))

    buttons = [
        [InlineKeyboardButton(
            f"🐇 {to_small_caps('Small Database')} (< 30k files)",
            callback_data=f"dbsize#small#{chat}#{lst_msg_id}#{from_user}"
        )],
        [InlineKeyboardButton(
            f"🐘 {to_small_caps('Large Database')} (30k+ files)",
            callback_data=f"dbsize#large#{chat}#{lst_msg_id}#{from_user}"
        )],
        [InlineKeyboardButton(f"⨳ {to_small_caps('Cancel')}", callback_data="index_cancel")]
    ]
    await msg.edit(
        "📦 <b>What type of database is this?</b>\n\n"
        "• <b>Small Database</b> — updates progress every 250 files.\n"
        "• <b>Large Database</b> — 4-worker parallel partitioning engine (1500+ files/min).",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@Client.on_message((filters.forwarded | (filters.regex("(https://)?(t\\.me/|telegram\\.me/|telegram\\.dog/)(c/)?(\\d+|[a-zA-Z_0-9]+)/(\\d+)$")) & filters.text) & filters.private & filters.incoming)
async def send_for_index(bot, message):
    if message.text:
        regex = re.compile("(https://)?(t\\.me/|telegram\\.me/|telegram\\.dog/)(c/)?(\\d+|[a-zA-Z_0-9]+)/(\\d+)$")
        match = regex.match(message.text)
        if not match:
            return await message.reply('Invalid link')
        chat_id = match.group(4)
        last_msg_id = int(match.group(5))
        if chat_id.isnumeric():
            chat_id = int(("-100" + chat_id))
    elif message.forward_from_chat.type == enums.ChatType.CHANNEL:
        last_msg_id = message.forward_from_message_id
        chat_id = message.forward_from_chat.username or message.forward_from_chat.id
    else:
        return
    try:
        await bot.get_chat(chat_id)
    except ChannelInvalid:
        return await message.reply('This may be a private channel / group. Make me an admin over there to index the files.')
    except (UsernameInvalid, UsernameNotModified):
        return await message.reply('Invalid Link specified.')
    except Exception as e:
        logger.exception(e)
        return await message.reply(f'Errors - {e}')
    try:
        k = await bot.get_messages(chat_id, last_msg_id)
    except Exception:
        return await message.reply('Make Sure That i am An Admin In The Channel, if channel is private')
    if k.empty:
        return await message.reply('This may be group and i am not a admin of the group.')

    if message.from_user.id in ADMINS:
        if LAZY_MODE:
            file = getattr(message, message.media.value)
            filename = file.file_name
            filesize = humanize.naturalsize(file.file_size)
            buttons = [
                [InlineKeyboardButton(f"📝 {to_small_caps('Start Renaming')} 📝", callback_data="rename")],
                [InlineKeyboardButton(f"📇 {to_small_caps('Start Indexing')} 𓍻", callback_data=f'index#accept#{chat_id}#{last_msg_id}#{message.from_user.id}')],
                [InlineKeyboardButton(f"⨳ {to_small_caps('Close')} ⨳", callback_data='cancel')],
            ]
            return await message.reply(
                f'\n⨳ Rename Mode ⨳\n\n**__What do you want me to do with this file.?__**\n\n'
                f'🪬Chat ID/ Username: <code>{chat_id}</code>\nℹ️Last Message ID: <code>{last_msg_id}</code>\n\n'
                f'🎞**File Name** :- `{filename}`\n\n⚙️**File Size** :- `{filesize}`',
                reply_to_message_id=message.id,
                reply_markup=InlineKeyboardMarkup(buttons))
        else:
            buttons = [
                [InlineKeyboardButton(f"{to_small_caps('Yes')}", callback_data=f'index#accept#{chat_id}#{last_msg_id}#{message.from_user.id}')],
                [InlineKeyboardButton(f"⨳ {to_small_caps('Close')} ⨳", callback_data='close_data')],
            ]
            return await message.reply(
                f'Do you Want To Index This Channel/ Group ?\n\nChat ID/ Username: <code>{chat_id}</code>\nLast Message ID: <code>{last_msg_id}</code>',
                reply_markup=InlineKeyboardMarkup(buttons))

    if type(chat_id) is int:
        try:
            link = (await bot.create_chat_invite_link(chat_id)).invite_link
        except ChatAdminRequired:
            return await message.reply('Make sure i am an admin in the chat and have permission to invite users.')
    else:
        link = f"@{message.forward_from_chat.username}"
    buttons = [
        [InlineKeyboardButton(f"📩 {to_small_caps('Request Index')}", callback_data=f'index#accept#{chat_id}#{last_msg_id}#{message.from_user.id}')],
        [InlineKeyboardButton(f"❌ {to_small_caps('Reject Index')}", callback_data=f'index#reject#{chat_id}#{message.id}#{message.from_user.id}')],
    ]
    await bot.send_message(LOG_CHANNEL,
                           f'#IndexRequest\n\nBy : {message.from_user.mention} (<code>{message.from_user.id}</code>)\n'
                           f'Chat ID/ Username - <code>{chat_id}</code>\nLast Message ID - <code>{last_msg_id}</code>\nInviteLink - {link}',
                           reply_markup=InlineKeyboardMarkup(buttons))
    if LAZY_MODE:
        if message.from_user.id in LAZY_RENAMERS:
            k = await message.reply('🎉\n\n❤️ Thank You For the Contribution, Wait For My Moderators to verify the files.\n\n\n🎁')
            buttons = [
                [InlineKeyboardButton("📝✧✧ S𝚝ar𝚝 Renaming ✧✧📝", callback_data="rename")],
                [InlineKeyboardButton('⨳  C L Ф S Ξ  ⨳', callback_data='cancel')]
            ]
            file = getattr(message, message.media.value)
            filename = file.file_name
            filesize = humanize.naturalsize(file.file_size)
            await message.reply(
                f".\n⨳ Rename Mode ⨳\n\nSince you are an Authentic user, please don't hesitate to ask me for any other help...\n\n"
                f"🪬Chat ID/ Username: <code>{chat_id}</code>\nℹ️Last Message ID: <code>{last_msg_id}</code>\n\n"
                f"🎞**File Name** :- `{filename}`\n\n⚙️**File Size** :- `{filesize}`\n\nYou can simply close this window or perform following actions, it's upon you",
                reply_to_message_id=message.id,
                reply_markup=InlineKeyboardMarkup(buttons))
            await asyncio.sleep(600)
            await k.delete()
        else:
            await message.reply('🎉\n\n❤️ Thank You For the Contribution, Wait For My Moderators to verify the files.\n\n\n🎁')
            buttons = [
                [InlineKeyboardButton("📝✧✧ S𝚝ar𝚝 Renaming ✧✧📝", callback_data="requireauth")],
                [InlineKeyboardButton('⨳  C L Ф S Ξ  ⨳', callback_data='cancel')]
            ]
            file = getattr(message, message.media.value)
            filename = file.file_name
            filesize = humanize.naturalsize(file.file_size)
            k = await message.reply(
                f"\n⨳ Rename Mode ⨳\n\n🤩 Do you know I can do a lot of things at a time...\nWould you like to try some of it's amazing features...\n\n"
                f"🪬Chat ID/ Username: <code>{chat_id}</code>\nℹ️Last Message ID: <code>{last_msg_id}</code>\n\n"
                f"🎞**File Name** :- `{filename}`\n\n⚙️**File Size** :- `{filesize}`",
                reply_to_message_id=message.id,
                reply_markup=InlineKeyboardMarkup(buttons))
            await asyncio.sleep(600)
            await k.delete()
    else:
        await message.reply('🎉\n\n❤️ Thank You For the Contribution, Wait For My Moderators to verify the files.\n\n\n🎁')


@Client.on_message(filters.command('setskip') & filters.user(ADMINS))
async def set_skip_number(bot, message):
    if ' ' in message.text:
        _, skip = message.text.split(" ")
        try:
            skip = int(skip)
        except Exception:
            return await message.reply("Skip number should be an integer.")
        await message.reply(f"Successfully set SKIP number as {skip}")
        temp.CURRENT = int(skip)
    else:
        await message.reply("Give me a skip number")


# ─── 4-Worker Parallel Partitioning Indexing Engine ───────────────────────────

async def index_files_to_db(lst_msg_id, chat, msg, bot, large_mode: bool = False, large_db: bool = False):
    """
    ⚡ 4-Worker Parallel Partitioning Indexing Engine (Target: 1500+ files/min)
    Splits message ID range into 4 parallel workers streaming simultaneously.
    """
    stats = {
        "total": 0,
        "dup": 0,
        "err": 0,
        "deleted": 0,
        "no_media": 0,
        "bad": 0,
        "processed": 0,
        "done": False,
    }

    UPDATE_EVERY_FILES = 250
    last_ui_update_files = -1  # -1 triggers UI update on FIRST loop immediately

    cancel_btn = InlineKeyboardMarkup([[InlineKeyboardButton('🛑 Cancel', callback_data='index_cancel')]])
    mode_label = '🐘 Large DB' if (large_mode or large_db) else '🐇 Small DB'
    
    batch_media = []
    batch_lock = asyncio.Lock()

    async with lock:
        start_time = time.time()
        try:
            temp.CANCEL = False
            skip_from = max(temp.CURRENT, 1)
            total_range = max(1, lst_msg_id - skip_from + 1)
            
            NUM_WORKERS = 4
            step = max(1, total_range // NUM_WORKERS)

            # Generate 4 parallel worker range partitions
            partitions = []
            for w in range(NUM_WORKERS):
                w_start = skip_from + (w * step)
                w_end = lst_msg_id if (w == NUM_WORKERS - 1) else (w_start + step - 1)
                if w_start <= lst_msg_id:
                    partitions.append((w_start, min(w_end, lst_msg_id)))

            logger.info(f"[INDEX] Launching {len(partitions)} Parallel Workers for chat={chat}, skip={skip_from}, last={lst_msg_id}")

            # ── Background UI Updater Task ────────────────────────────────────
            async def _ui_task():
                nonlocal last_ui_update_files
                while not stats["done"]:
                    if last_ui_update_files == -1 or (stats["total"] - last_ui_update_files >= UPDATE_EVERY_FILES) or (stats["processed"] % 1000 < 50):
                        last_ui_update_files = stats["total"]
                        current_id = skip_from + stats["processed"] - 1
                        progress_text = (
                            f"{mode_label} Mode (⚡ {len(partitions)}-Worker Parallel Engine)\n\n"
                            f"📨 Processed: <code>{current_id}</code> / <code>{lst_msg_id}</code>\n"
                            f"💾 Saved: <code>{stats['total']}</code>\n"
                            f"🔁 Duplicates: <code>{stats['dup']}</code>\n"
                            f"🗑 Deleted: <code>{stats['deleted']}</code>\n"
                            f"📵 Non-media: <code>{stats['no_media'] + stats['bad']}</code>\n"
                            f"❌ Errors: <code>{stats['err']}</code>"
                        )
                        try:
                            await msg.edit_text(text=progress_text, reply_markup=cancel_btn)
                        except FloodWait as fw:
                            await asyncio.sleep(fw.value + 1)
                        except Exception:
                            pass
                    await asyncio.sleep(2)

            ui_task_handle = asyncio.create_task(_ui_task())

            # ── Worker Routine ────────────────────────────────────────────────
            async def _worker_partition(p_start, p_end):
                current = p_start
                while current <= p_end and not temp.CANCEL:
                    chunk_end = min(current + 200 - 1, p_end)
                    id_list = list(range(current, chunk_end + 1))

                    try:
                        msgs = await bot.get_messages(chat, id_list)
                    except FloodWait as fw:
                        await asyncio.sleep(fw.value + 1)
                        continue
                    except Exception as exc:
                        stats["err"] += len(id_list)
                        current = chunk_end + 1
                        continue

                    if not msgs:
                        current = chunk_end + 1
                        continue

                    msgs_list = msgs if isinstance(msgs, list) else [msgs]
                    for message in msgs_list:
                        stats["processed"] += 1
                        if not message or message.empty:
                            stats["deleted"] += 1
                            continue
                        if not message.media:
                            stats["no_media"] += 1
                            continue
                        if message.media not in (
                            enums.MessageMediaType.VIDEO,
                            enums.MessageMediaType.AUDIO,
                            enums.MessageMediaType.DOCUMENT,
                        ):
                            stats["bad"] += 1
                            continue

                        media = getattr(message, message.media.value, None)
                        if not media:
                            stats["bad"] += 1
                            continue

                        media.file_type = message.media.value
                        media.caption = message.caption

                        async with batch_lock:
                            batch_media.append(media)
                            if len(batch_media) >= 250:
                                flush_batch = list(batch_media)
                                batch_media.clear()
                                s_cnt, d_cnt, e_cnt = await save_files_batch(flush_batch)
                                stats["total"] += s_cnt
                                stats["dup"] += d_cnt
                                stats["err"] += e_cnt

                    current = chunk_end + 1
                    await asyncio.sleep(0.005)

            # Gather all 4 parallel partition workers
            await asyncio.gather(*[_worker_partition(p[0], p[1]) for p in partitions])

            stats["done"] = True
            ui_task_handle.cancel()

            # Flush any remaining media items
            if batch_media:
                s_cnt, d_cnt, e_cnt = await save_files_batch(batch_media)
                stats["total"] += s_cnt
                stats["dup"] += d_cnt
                stats["err"] += e_cnt
                batch_media.clear()

        except Exception as e:
            logger.exception(e)
            stats["done"] = True
            elapsed_sec = int(time.time() - start_time)
            d, rem = divmod(elapsed_sec, 86400)
            h, rem = divmod(rem, 3600)
            m, s = divmod(rem, 60)
            time_taken_str = to_small_caps(f"Completed in : {d} : {h} : {m} : {s}")
            await msg.edit(f'❌ Error: <code>{e}</code>\n\n⏱️ <b>{time_taken_str}</b>')
            return

        elapsed_sec = int(time.time() - start_time)
        d, rem = divmod(elapsed_sec, 86400)
        h, rem = divmod(rem, 3600)
        m, s = divmod(rem, 60)
        time_taken_str = to_small_caps(f"Completed in : {d} : {h} : {m} : {s}")

        _status = "Cancelled! ✋" if temp.CANCEL else "Indexing Complete! ✅"
        await msg.edit(
            f"{'✋' if temp.CANCEL else '✅'} <b>{_status}</b>\n\n"
            f"⏱️ <b>{time_taken_str}</b>\n\n"
            f"💾 Saved <code>{stats['total']}</code> files to database!\n"
            f"🔁 Duplicates skipped: <code>{stats['dup']}</code>\n"
            f"🗑 Deleted skipped: <code>{stats['deleted']}</code>\n"
            f"📵 Non-media skipped: <code>{stats['no_media'] + stats['bad']}</code>\n"
            f"📦 Total scanned: <code>{stats['processed']}</code> messages\n"
            f"❌ Errors: <code>{stats['err']}</code>"
        )
