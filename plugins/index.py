import logging
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, MessageNotModified
from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, ChatAdminRequired, UsernameInvalid, UsernameNotModified
from info import ADMINS, LAZY_RENAMERS
from info import INDEX_REQ_CHANNEL as LOG_CHANNEL
from info import LAZY_MODE 
from database.ia_filterdb import save_file
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils import temp
import re
import humanize
from info import ADMINS 
from lazybot import LazyPrincessBot 

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
lock = asyncio.Lock()
semaphore = asyncio.Semaphore(1) # create a semaphore with initial value of 1

# ─────────────────────────────────────────────────────────────────────────────
# Helper: safe edit for Small DB — waits out FloodWait and retries
# ─────────────────────────────────────────────────────────────────────────────
async def safe_edit(msg, text, reply_markup=None):
    """Edit a message and silently wait out any FloodWait before retrying (Small DB mode)."""
    while True:
        try:
            if reply_markup:
                await msg.edit_text(text=text, reply_markup=reply_markup)
            else:
                await msg.edit(text)
            break
        except FloodWait as fw:
            logger.warning(f"FloodWait: sleeping {fw.value}s before retrying edit...")
            await asyncio.sleep(fw.value + 2)
        except Exception:
            break  # non-flood errors — just skip this update


# ─────────────────────────────────────────────────────────────────────────────
# Helper: safe edit for Large DB — SKIPS the edit on FloodWait (non-blocking)
# This is the key difference: we never block the indexing loop waiting for Telegram.
# ─────────────────────────────────────────────────────────────────────────────
async def safe_edit_nonblocking(msg, text, reply_markup=None):
    """Try to edit a message. If FloodWait hits, log and skip — never block (Large DB mode)."""
    try:
        if reply_markup:
            await msg.edit_text(text=text, reply_markup=reply_markup)
        else:
            await msg.edit(text)
    except FloodWait as fw:
        logger.warning(f"[LargeDB] FloodWait {fw.value}s — skipping this progress edit to keep indexing running.")
    except MessageNotModified:
        pass  # text didn't change, harmless
    except Exception as e:
        logger.warning(f"[LargeDB] Edit skipped: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# Step 1: When admin clicks "Start Indexing" → ask DB size first
# ─────────────────────────────────────────────────────────────────────────────
@Client.on_callback_query(filters.regex(r'^index'))
async def index_files(bot, query):
    # ── Cancel button ──────────────────────────────────────────────────────
    if query.data.startswith('index_cancel'):
        temp.CANCEL = True
        return await query.answer("Cancelling Indexing")

    # ── DB-size choice already made → proceed to indexing ─────────────────
    if query.data.startswith('index_dbsize#'):
        # format: index_dbsize#<size>#<lazydeveloperr>#<chat>#<lst_msg_id>#<from_user>
        parts = query.data.split("#")
        # parts[0] = 'index_dbsize'
        db_size   = parts[1]            # 'large' or 'small'
        lazydeveloperr = parts[2]
        chat      = parts[3]
        lst_msg_id = parts[4]
        from_user  = parts[5]

        if lock.locked():
            return await query.answer('Wait until previous process complete.', show_alert=True)

        msg = query.message
        await query.answer('Processing...⏳', show_alert=True)

        if int(from_user) not in ADMINS:
            await bot.send_message(
                int(from_user),
                f'Your Submission for indexing {chat} has been accepted by our moderators and will be added soon.',
                reply_to_message_id=int(lst_msg_id)
            )

        mode_label = "🗂 Large Database Mode" if db_size == "large" else "📁 Small Database Mode"
        await safe_edit(
            msg,
            f"Starting Indexing\n<b>{mode_label}</b>",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton('Cancel', callback_data='index_cancel')]]
            )
        )

        try:
            chat_id = int(chat)
        except:
            chat_id = chat

        is_large = (db_size == "large")
        await index_files_to_db(int(lst_msg_id), chat_id, msg, bot, large_db=is_large)
        return

    # ── Reject button ──────────────────────────────────────────────────────
    _, lazydeveloperr, chat, lst_msg_id, from_user = query.data.split("#")
    if lazydeveloperr == 'reject':
        await query.message.delete()
        await bot.send_message(
            int(from_user),
            f'Your Submission for indexing {chat} has been decliened by our moderators.',
            reply_to_message_id=int(lst_msg_id)
        )
        return

    # ── Accept button → ask Large or Small before starting ────────────────
    if lock.locked():
        return await query.answer('Wait until previous process complete.', show_alert=True)

    msg = query.message
    await query.answer('Choose database size...', show_alert=False)

    size_buttons = [
        [
            InlineKeyboardButton(
                '🗂 Large Database',
                callback_data=f'index_dbsize#large#{lazydeveloperr}#{chat}#{lst_msg_id}#{from_user}'
            ),
            InlineKeyboardButton(
                '📁 Small Database',
                callback_data=f'index_dbsize#small#{lazydeveloperr}#{chat}#{lst_msg_id}#{from_user}'
            ),
        ],
        [InlineKeyboardButton('⨳  C L Ф S Ξ  ⨳', callback_data='close_data')]
    ]
    await safe_edit(
        msg,
        "⚙️ <b>Select Database Type</b>\n\n"
        "📁 <b>Small Database</b> — updates progress every <b>60 messages</b>.\n"
        "Suitable for channels with <b>fewer files</b>.\n\n"
        "🗂 <b>Large Database</b> — updates progress every <b>500 files saved</b>.\n"
        "Never blocks on FloodWait — indexing runs smoothly at full speed.\n"
        "Recommended for large channels with <b>50,000+ files</b> (up to 5 lakh+).",
        reply_markup=InlineKeyboardMarkup(size_buttons)
    )


# ─────────────────────────────────────────────────────────────────────────────
# Index-link / forwarded-message handler (unchanged logic, kept intact)
# ─────────────────────────────────────────────────────────────────────────────
@Client.on_message((filters.forwarded | (filters.regex("(https://)?(t\\.me/|telegram\\.me/|telegram\\.dog/)(c/)?(\\d+|[a-zA-Z_0-9]+)/(\\d+)$")) & filters.text ) & filters.private & filters.incoming)
async def send_for_index(bot, message):
    if message.text:
        regex = re.compile("(https://)?(t\\.me/|telegram\\.me/|telegram\\.dog/)(c/)?(\\d+|[a-zA-Z_0-9]+)/(\\d+)$")
        match = regex.match(message.text)
        if not match:
            return await message.reply('Invalid link')
        chat_id = match.group(4)
        last_msg_id = int(match.group(5))
        if chat_id.isnumeric():
            chat_id  = int(("-100" + chat_id))
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
    except:
        return await message.reply('Make Sure That i am An Admin In The Channel, if channel is private')
    if k.empty:
        return await message.reply('This may be group and i am not a admin of the group.')

    if message.from_user.id in ADMINS:
        if (LAZY_MODE==True):
            file = getattr(message, message.media.value)
            filename = file.file_name
            filesize = humanize.naturalsize(file.file_size) 
            buttons = [
                [ InlineKeyboardButton("📝✧ Start Renaming ✧📝", callback_data="rename") ],
                [ InlineKeyboardButton('📇✧✧  S𝚝ar𝚝 Indexing  ✧✧📇',callback_data=f'index#accept#{chat_id}#{last_msg_id}#{message.from_user.id}')],
                [ InlineKeyboardButton('⨳  C L Ф S Ξ  ⨳', callback_data='cancel'),]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            return await message.reply(
                f'\n⨳ Rename Mode ⨳\n\n**__What do you want me to do with this file.?__**\n\n🪬Chat ID/ Username: <code>{chat_id}</code>\nℹ️Last Message ID: <code>{last_msg_id}</code> \n\n🎞**File Name** :- `{filename}`\n\n⚙️**File Size** :- `{filesize}`',
                reply_to_message_id=message.id,
                reply_markup=reply_markup)
        else:
            buttons = [
                [
                    InlineKeyboardButton('Yes',
                                         callback_data=f'index#accept#{chat_id}#{last_msg_id}#{message.from_user.id}')
                ],
                [
                    InlineKeyboardButton('⨳  C L Ф S Ξ  ⨳', callback_data='close_data'),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            return await message.reply(
                f'Do you Want To Index This Channel/ Group ?\n\nChat ID/ Username: <code>{chat_id}</code>\nLast Message ID: <code>{last_msg_id}</code>',
                reply_markup=reply_markup)

    if type(chat_id) is int:
        try:
            link = (await bot.create_chat_invite_link(chat_id)).invite_link
        except ChatAdminRequired: 
            return await message.reply('Make sure i am an admin in the chat and have permission to invite users.')
    else:
        link = f"@{message.forward_from_chat.username}"
    buttons = [
        [
            InlineKeyboardButton('Request Index',
                                 callback_data=f'index#accept#{chat_id}#{last_msg_id}#{message.from_user.id}')
        ],
        [
            InlineKeyboardButton('Reject Index',
                                 callback_data=f'index#reject#{chat_id}#{message.id}#{message.from_user.id}'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await bot.send_message(LOG_CHANNEL,
                           f'#IndexRequest\n\nBy : {message.from_user.mention} (<code>{message.from_user.id}</code>)\nChat ID/ Username - <code> {chat_id}</code>\nLast Message ID - <code>{last_msg_id}</code>\nInviteLink - {link}',
                           reply_markup=reply_markup)
    if (LAZY_MODE == True):
        if message.from_user.id in LAZY_RENAMERS:
            k = await message.reply('🎉\n\n❤️ Thank You For the Contribution, Wait For My Moderators to verify the files.\n\n\n🎁')
            buttons = [
                        [InlineKeyboardButton("📝✧✧ S𝚝ar𝚝 Renaming ✧✧📝", callback_data="rename") ],
                        [InlineKeyboardButton('⨳  C L Ф S Ξ  ⨳', callback_data='cancel')]]
            reply_markup = InlineKeyboardMarkup(buttons)
            file = getattr(message, message.media.value)
            filename = file.file_name
            filesize = humanize.naturalsize(file.file_size) 
            await message.reply(
                                f".\n⨳ Rename Mode ⨳\n\nSince you are an Authentic user, please don't hesitate to ask me for any other help...\n\n🪬Chat ID/ Username: <code>{chat_id}</code>\nℹ️Last Message ID: <code>{last_msg_id}</code> \n\n🎞**File Name** :- `{filename}`\n\n⚙️**File Size** :- `{filesize}`\n\nYou can simply close this window or perform following actions, it's upon you",
                                reply_to_message_id=message.id,
                                reply_markup=reply_markup)
            await asyncio.sleep(600)
            await k.delete()
        else :      
            await message.reply('🎉\n\n❤️ Thank You For the Contribution, Wait For My Moderators to verify the files.\n\n\n🎁')
            buttons = [
                        [InlineKeyboardButton("📝✧✧ S𝚝ar𝚝 Renaming ✧✧📝", callback_data="requireauth") ],
                        [InlineKeyboardButton('⨳  C L Ф S Ξ  ⨳', callback_data='cancel')]]
            reply_markup = InlineKeyboardMarkup(buttons)
            file = getattr(message, message.media.value)
            filename = file.file_name
            filesize = humanize.naturalsize(file.file_size) 
            k = await message.reply(
                                f"\n⨳ Rename Mode ⨳\n\n🤩 Do you know I can do a lot of things at a time...\nWould you like to try some of it's amazing features... \n\n🪬Chat ID/ Username: <code>{chat_id}</code>\nℹ️Last Message ID: <code>{last_msg_id}</code> \n\n🎞**File Name** :- `{filename}`\n\n⚙️**File Size** :- `{filesize}`",
                                reply_to_message_id=message.id,
                                reply_markup=reply_markup)
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
        except:
            return await message.reply("Skip number should be an integer.")
        await message.reply(f"Successfully set SKIP number as {skip}")
        temp.CURRENT = int(skip)
    else:
        await message.reply("Give me a skip number")


# ─────────────────────────────────────────────────────────────────────────────
# Core indexing function
#
#   large_db=False → SMALL DB MODE
#       • Updates progress every 20 messages (frequent, safe for small channels)
#       • Waits out FloodWait before retrying (safe_edit — blocking)
#
#   large_db=True  → LARGE DB MODE  (the key difference)
#       • Progress is updated every LARGE_DB_NOTIFY_EVERY files SAVED.
#         Triggered by actual saved-file count — so the user is notified
#         after every 500 files land in the database.
#       • On FloodWait: the edit is SKIPPED entirely (safe_edit_nonblocking).
#         The indexing loop NEVER pauses — it just skips that one UI update and
#         keeps running at full speed. This prevents the "message edit flood" error
#         from accumulating when indexing 3 lakh+ files.
#       • asyncio.sleep(0) is yielded every LARGE_DB_YIELD_EVERY messages so the
#         event loop stays responsive (cancel callbacks still work).
# ─────────────────────────────────────────────────────────────────────────────

# Notify user after every N files SAVED in Large DB mode
LARGE_DB_NOTIFY_EVERY = 500
# How often to yield control to the event loop in Large DB mode (every N messages)
LARGE_DB_YIELD_EVERY = 500


async def index_files_to_db(lst_msg_id, chat, msg, bot, large_db=False):
    total_files = 0
    duplicate = 0
    errors = 0
    deleted = 0
    no_media = 0
    unsupported = 0

    # Small DB: update every 60 messages
    SMALL_DB_UPDATE_INTERVAL = 60

    # Counter used for the yield-every-N trick in large DB mode
    msg_counter = 0
    last_notified_files = 0

    async with lock:
        try:
            current = temp.CURRENT
            temp.CANCEL = False

            async for message in bot.iter_messages(chat, lst_msg_id, temp.CURRENT):
                if temp.CANCEL:
                    cancel_text = (
                        f"Successfully Cancelled!!\n\n"
                        f"Saved <code>{total_files}</code> files to dataBase!\n"
                        f"Duplicate Files Skipped: <code>{duplicate}</code>\n"
                        f"Deleted Messages Skipped: <code>{deleted}</code>\n"
                        f"Non-Media messages skipped: <code>{no_media + unsupported}</code>"
                        f"(Unsupported Media - `{unsupported}` )\n"
                        f"Errors Occurred: <code>{errors}</code>"
                    )
                    if large_db:
                        await safe_edit_nonblocking(msg, cancel_text)
                    else:
                        await safe_edit(msg, cancel_text)
                    break

                current += 1
                msg_counter += 1

                # ── Progress update logic ──────────────────────────────────
                if large_db:
                    # LARGE DB: file-count-gated, non-blocking
                    # Yield to event loop every LARGE_DB_YIELD_EVERY messages so
                    # cancel callbacks can still be received.
                    if msg_counter % LARGE_DB_YIELD_EVERY == 0:
                        await asyncio.sleep(0)

                    # Notify after every LARGE_DB_NOTIFY_EVERY files saved (only once per threshold)
                    if total_files > 0 and total_files % LARGE_DB_NOTIFY_EVERY == 0 and total_files != last_notified_files:
                        last_notified_files = total_files
                        can = [[InlineKeyboardButton('Cancel', callback_data='index_cancel')]]
                        reply = InlineKeyboardMarkup(can)
                        progress_text = (
                            f"🗂 <b>Large DB Mode</b> — indexing in progress...\n\n"
                            f"📨 Messages scanned: <code>{current}</code>\n"
                            f"✅ Files saved: <code>{total_files}</code>\n"
                            f"♻️ Duplicates skipped: <code>{duplicate}</code>\n"
                            f"🗑 Deleted msgs skipped: <code>{deleted}</code>\n"
                            f"🚫 Non-media skipped: <code>{no_media + unsupported}</code> "
                            f"(unsupported: <code>{unsupported}</code>)\n"
                            f"⚠️ Errors: <code>{errors}</code>\n\n"
                            f"<i>Notifying every {LARGE_DB_NOTIFY_EVERY} files saved.</i>"
                        )
                        await safe_edit_nonblocking(msg, progress_text, reply_markup=reply)

                else:
                    # SMALL DB: count-gated, blocking (original behaviour)
                    if current % SMALL_DB_UPDATE_INTERVAL == 0:
                        can = [[InlineKeyboardButton('Cancel', callback_data='index_cancel')]]
                        reply = InlineKeyboardMarkup(can)
                        progress_text = (
                            f"Total messages fetched: <code>{current}</code>\n"
                            f"Total messages saved: <code>{total_files}</code>\n"
                            f"Duplicate Files Skipped: <code>{duplicate}</code>\n"
                            f"Deleted Messages Skipped: <code>{deleted}</code>\n"
                            f"Non-Media messages skipped: <code>{no_media + unsupported}</code>"
                            f"(Unsupported Media - `{unsupported}` )\n"
                            f"Errors Occurred: <code>{errors}</code>"
                        )
                        await safe_edit(msg, progress_text, reply_markup=reply)

                # ── Media processing (unchanged) ───────────────────────────
                if message.empty:
                    deleted += 1
                    continue
                elif not message.media:
                    no_media += 1
                    continue
                elif message.media not in [enums.MessageMediaType.VIDEO, enums.MessageMediaType.AUDIO, enums.MessageMediaType.DOCUMENT]:
                # elif message.media != enums.MessageMediaType.VIDEO:   
                    unsupported += 1
                    continue
                media = getattr(message, message.media.value, None)
                if not media:
                    unsupported += 1
                    continue
                media.file_type = message.media.value
                media.caption = message.caption
                aynav, vnay = await save_file(media)
                if aynav:
                    total_files += 1
                elif vnay == 0:
                    duplicate += 1
                elif vnay == 2:
                    errors += 1

        except Exception as e:
            logger.exception(e)
            if large_db:
                await safe_edit_nonblocking(msg, f'Error baby: {e}')
            else:
                await safe_edit(msg, f'Error baby: {e}')
        else:
            done_text = (
                f"✅ <b>Indexing Complete!</b>\n\n"
                f"{'🗂 Large DB Mode\n\n' if large_db else ''}"
                f"Files saved: <code>{total_files}</code>\n"
                f"Duplicate Files Skipped: <code>{duplicate}</code>\n"
                f"Deleted Messages Skipped: <code>{deleted}</code>\n"
                f"Non-Media messages skipped: <code>{no_media + unsupported}</code>"
                f"(Unsupported Media - `{unsupported}` )\n"
                f"Errors Occurred: <code>{errors}</code>"
            )
            if large_db:
                await safe_edit_nonblocking(msg, done_text)
            else:
                await safe_edit(msg, done_text)
