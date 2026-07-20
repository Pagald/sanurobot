class script(object):
    START_TXT = """Hey {} !!\n
I'm the First AI-Powered Lazy's Asset, made for u with ❤\n

💬 Just type the movie name & let A.I do the magic!

""" 
    EXPIRED_TEXT = """Your video Quota is up for today!
💎GET unlimited #FREE Access by Joining our VIP channels.
📆 Or wait until tomorrow... but who likes waiting?😜"""

    UPGRADE_TEXT = """⭕Join these VIP channels to GET #FREE Access! & keep the fun rolling ♥!

📆 Or wait until tomorrow... but who likes waiting? 😜"""
    
    VERIFIED_TEXT = """𓆩ཫ❤ <b><u>ᴄᴏɴɢʀᴀᴛꜱ {} </u></b>❤ཀ𓆪

ʏᴏᴜ ᴀʀᴇ ᴠᴇʀɪꜰɪᴇᴅ ꜰᴏʀ {} ʜᴏᴜʀꜱ! 🎉\n\nɴᴏᴡ ʏᴏᴜ ʜᴀᴠᴇ <b><u>ᴜɴʟɪᴍɪᴛᴇᴅ ᴀᴄᴄᴇꜱꜱ</u></b> ᴜɴᴛɪʟ <b> {} </b>😊"""

    FAILED_VERIFICATION_TEXT = """🚨 <b>ᴏᴏᴘꜱ! ꜱᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ.</b>

😕 ɪᴛ ʟᴏᴏᴋꜱ ʟɪᴋᴇ ɪ ᴄᴀɴ'ᴛ ᴠᴇʀɪꜰʏ ʏᴏᴜʀ ꜱᴜʙꜱᴄʀɪᴘᴛɪᴏɴ ʙᴇᴄᴀᴜꜱᴇ ɪ'ᴍ <b>ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ</b> ɪɴ ᴛʜᴇ ʀᴇQᴜɪʀᴇᴅ ᴄʜᴀɴɴᴇʟ <b>ᴏʀ</b> ꜱᴏᴍᴇ ᴏᴛʜᴇʀ ᴄʀɪᴛɪᴄᴀʟ ɪꜱꜱᴜᴇ.

👤 <b>ᴡʜᴀᴛ ʏᴏᴜ ᴄᴀɴ ᴅᴏ:</b>
1️⃣ ᴀꜱᴋ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ᴏᴡɴᴇʀ ᴛᴏ ᴍᴀᴋᴇ ᴍᴇ ᴀɴ <b>ᴀᴅᴍɪɴ</b>.
2️⃣ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ ᴀꜰᴛᴇʀ ᴛʜᴇ ɪꜱꜱᴜᴇ ɪꜱ ꜰɪxᴇᴅ.

⚡ <b>ᴜɴᴛɪʟ ᴛʜᴇɴ, ꜱᴛᴀʏ ᴀᴡᴇꜱᴏᴍᴇ!</b> 🚀
"""
    FORCESUB_MSG = """<b>👋 ʜᴇʟʟᴏ, {}!
    
Please join below channel to get file! 👇</b>
"""

    DNT_TEXT = """ʜᴇʏ ꜱᴡᴇᴇᴛɪᴇ {},
ᴛʜᴀɴᴋꜱ ꜰᴏʀ ᴛʜɪɴᴋɪɴɢ ᴀʙᴏᴜᴛ ᴜꜱ.\n<b>ꜰᴏʀ ʏᴏᴜʀ ᴋɪɴᴅ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ, ᴡᴇ ᴅᴏ ɴᴏᴛ ᴀꜱᴋ ᴏʀ ꜰᴏʀᴄᴇ ᴀɴʏᴏɴᴇ ꜰᴏʀ ᴀɴʏ ᴋɪɴᴅ ᴏꜰ ᴘᴀʏᴍᴇɴᴛ</b>. ʙᴜᴛ ɪꜰ ʏᴏᴜ ʀᴇᴀʟʟʏ ᴡᴀɴᴛ ᴛᴏ ᴅᴏɴᴀᴛᴇ ᴜꜱ ᴛʜᴇɴ ʏᴏᴜ ᴄᴀɴ ꜱᴇɴᴅ ᴍᴏɴᴇʏ ᴛᴏ ᴜꜱ ꜰʀᴏᴍ ʙᴇʟᴏᴡ ʟɪɴᴋꜱ...\n\n💵 ʀᴇᴀᴄʜ ᴅᴏɴᴀᴛɪᴏɴ ᴘᴀɢᴇ : <b> <a href={}>ᴄʟɪᴄᴋ ʜᴇʀᴇ...</a> </b>\n\nT❤️ ᴛʜᴀɴᴋ ʏᴏᴜ ꜱᴏ ᴍᴜᴄʜ..
"""

    REQ_AUTH_TEXT = """ʜᴇʟʟᴏ {},
ʏᴏᴜ ᴍᴜꜱᴛ ʜᴀᴠᴇ ᴛᴏ ʙᴇ ᴛʜᴇ ᴀᴜᴛʜᴇɴᴛɪᴄ ᴜꜱᴇʀ ᴛᴏ ᴄᴏᴍᴘʟᴇᴛᴇ ᴛʜɪꜱ ᴏᴘᴇʀᴀᴛɪᴏɴ...
"""


    HELP_TXT = """𝙷𝙴𝚈 {}
Here is the help for my COMMANDS."""

    ABOUT_TXT = """✯ 𝕚𝕥𝕤❜𝕤 me: {}
✯ 𝙲𝚁𝙴𝙰𝚃𝙾𝚁: <a href=https://t.me/LazyDeveloperr>🦋 LazyDeveloperr 🦋</a>
✯ 𝙻𝙸𝙱𝚁𝙰𝚁𝚈: 𝙿𝚈𝚁𝙾𝙶𝚁𝙰𝙼
✯ 𝙻𝙰𝙽𝙶𝚄𝙰𝙶𝙴: 𝙿𝚈𝚃𝙷𝙾𝙽 𝟹
✯ 𝙳𝙰𝚃𝙰 𝙱𝙰𝚂𝙴: 𝙼𝙾𝙽𝙶𝙾 𝙳𝙱
✯ 𝙱𝙾𝚃 𝚂𝙴𝚁𝚅𝙴𝚁: 𝙷𝙴𝚁𝙾𝙺𝚄
✯ 𝙱𝚄𝙸𝙻𝙳 𝚂𝚃𝙰𝚃𝚄𝚂: V 12
"""


    MANUELFILTER_TXT = """Help: <b>Filters</b>

- Fɪʟᴛᴇʀ ɪs ᴛʜᴇ ғᴇᴀᴛᴜʀᴇ ᴡᴇʀᴇ ᴜsᴇʀs ᴄᴀɴ sᴇᴛ ᴀᴜᴛᴏᴍᴀᴛᴇᴅ ʀᴇᴘʟɪᴇs ғᴏʀ ᴀ ᴘᴀʀᴛɪᴄᴜʟᴀʀ ᴋᴇʏᴡᴏʀᴅ ᴀɴᴅ LᴀᴢʏPʀɪɴᴇss ᴡɪʟʟ ʀᴇsᴘᴏɴᴅ ᴡʜᴇɴᴇᴠᴇʀ ᴛʜᴀᴛ ᴋᴇʏᴡᴏʀᴅ ʜɪᴛs ᴛʜᴇ ᴍᴇssᴀɢᴇ
<b>NOTE:</b>
1. BOT sʜᴏᴜʟᴅ ʜᴀᴠᴇ ᴀᴅᴍɪɴ ᴘʀɪᴠɪʟʟᴀɢᴇ.
2. Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴀᴅᴅ ғɪʟᴛᴇʀs ɪɴ ᴀ ᴄʜᴀᴛ.
3. Aʟᴇʀᴛ ʙᴜᴛᴛᴏɴs ʜᴀᴠᴇ ᴀ ʟɪᴍɪᴛ ᴏғ 64 ᴄʜᴀʀᴀᴄᴛᴇʀs.

<b>Commands and Usage:</b>
• /filter - <code>ᴀᴅᴅ ᴀ ғɪʟᴛᴇʀ ɪɴ ᴄʜᴀᴛ</code>
• /filters - <code>ʟɪsᴛ ᴀʟʟ ᴛʜᴇ ғɪʟᴛᴇʀs ᴏғ ᴀ ᴄʜᴀᴛ</code>
• /del - <code>ᴅᴇʟᴇᴛᴇ ᴀ sᴘᴇᴄɪғɪᴄ ғɪʟᴛᴇʀ ɪɴ ᴄʜᴀᴛ</code>
• /delall - <code>ᴅᴇʟᴇᴛᴇ ᴛʜᴇ ᴡʜᴏʟᴇ ғɪʟᴛᴇʀs ɪɴ ᴀ ᴄʜᴀᴛ (ᴄʜᴀᴛ ᴏᴡɴᴇʀ ᴏɴʟʏ)</code>"""
    
    BUTTON_TXT = """Help: <b>Buttons</b>

- Supports both url and alert inline buttons.

<b>NOTE:</b>
1. Telegram will not allows you to send buttons without any content, so content is mandatory.
2. BOT supports buttons with any telegram media type.
3. Buttons should be properly parsed as markdown format

<b>URL buttons:</b>
<code>[Button Text](buttonurl:https://t.me/LazyDeveloper)</code>

<b>Alert buttons:</b>
<code>[Button Text](buttonalert:This is an alert message)</code>"""
    
    AUTOFILTER_TXT = """ʜᴇʟᴘ: <b>ᴀᴜᴛᴏ ꜰɪʟᴛᴇʀ</b>
<b>ɴᴏᴛᴇ:</b>
1. ᴍᴀᴋᴇ ᴍᴇ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟ ɪꜰ ɪᴛ'ꜱ ᴘʀɪᴠᴀᴛᴇ.
2. ᴇɴꜱᴜʀᴇ ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟ ᴅᴏᴇꜱ ɴᴏᴛ ᴄᴏɴᴛᴀɪɴ ʀᴇꜱᴛʀɪᴄᴛᴇᴅ ᴄᴏɴᴛᴇɴᴛ (ᴇ.ɢ., ꜱᴘᴀᴍ, ᴘᴏʀɴ, ꜰᴀᴋᴇ ꜰɪʟᴇꜱ).
3. ꜰᴏʀᴡᴀʀᴅ ᴛʜᴇ ʟᴀꜱᴛ ᴍᴇꜱꜱᴀɢᴇ ᴏꜰ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ᴡɪᴛʜ ϙᴜᴏᴛᴇꜱ. ɪ'ʟʟ ᴀᴅᴅ ᴛʜᴇ ꜰɪʟᴇꜱ ᴛᴏ ᴍʏ ᴅᴀᴛᴀʙᴀꜱᴇ.
"""

    CONNECTION_TXT = """Help: <b>Connections</b>
<spoiler>
- Used to connect bot to PM for managing filters
- It helps to avoid spamming in groups

<b>NOTE:</b>
1. Only admins can add a connection.
2. Send <code>/connect</code> for connecting me to ur PM

<b>Commands and Usage:</b>
• /connect  - <code>connect a particular chat to your PM</code>
• /disconnect  - <code>disconnect from a chat</code>
• /connections - <code>list all your connections</code>
</spoiler>
"""
    EXTRAMOD_TXT = """Help: <b>Extra Modules</b>
<blockquote><b>NOTE:</b>
these are the extra features of Lazy Princess

<b>Commands and Usage:</b>
• /id - <code>get id of a specified user.</code>
• /info  - <code>get information about a user.</code>
• /imdb  - <code>get the film information from IMDb source.</code>
• /search  - <code>get the film information from various sources.</code> </blockquote>
"""
    ADMIN_TXT = """ʜᴇʟᴘ: <b>ᴀᴅᴍɪɴ ᴍᴏᴅᴇꜱ</b>
<b>ɴᴏᴛᴇ:</b>
ᴛʜɪꜱ ᴍᴏᴅᴜʟᴇ ᴏɴʟʏ ᴡᴏʀᴋꜱ ꜰᴏʀ ᴍʏ ᴀᴅᴍɪɴꜱ

<spoiler><b>ᴄᴏᴍᴍᴀɴᴅꜱ ᴀɴᴅ ᴜꜱᴀɢᴇ:</b>
• /logs - <code>ᴛᴏ ɢᴇᴛ ᴛʜᴇ ʀᴇᴄᴇɴᴛ ᴇʀʀᴏʀꜱ</code>
• /stats - <code>ᴛᴏ ɢᴇᴛ ꜱᴛᴀᴛᴜꜱ ᴏꜰ ꜰɪʟᴇꜱ ɪɴ ᴅʙ.</code>
• /delete - <code>ᴛᴏ ᴅᴇʟᴇᴛᴇ ᴀ ꜱᴘᴇᴄɪꜰɪᴄ ꜰɪʟᴇ ꜰʀᴏᴍ ᴅʙ.</code>
• /users - <code>ᴛᴏ ɢᴇᴛ ʟɪꜱᴛ ᴏꜰ ᴍʏ ᴜꜱᴇʀꜱ ᴀɴᴅ ɪᴅꜱ.</code>
• /chats - <code>ᴛᴏ ɢᴇᴛ ʟɪꜱᴛ ᴏꜰ ᴛʜᴇ ᴍʏ ᴄʜᴀᴛꜱ ᴀɴᴅ ɪᴅꜱ </code>
• /leave  - <code>ᴛᴏ ʟᴇᴀᴠᴇ ꜰʀᴏᴍ ᴀ ᴄʜᴀᴛ.</code>
• /disable  -  <code>ᴅᴏ ᴅɪꜱᴀʙʟᴇ ᴀ ᴄʜᴀᴛ.</code>
• /ban  - <code>ᴛᴏ ʙᴀɴ ᴀ ᴜꜱᴇʀ.</code>
• /unban  - <code>ᴛᴏ ᴜɴʙᴀɴ ᴀ ᴜꜱᴇʀ.</code>
• /channel - <code>ᴛᴏ ɢᴇᴛ ʟɪꜱᴛ ᴏꜰ ᴛᴏᴛᴀʟ ᴄᴏɴɴᴇᴄᴛᴇᴅ ᴄʜᴀɴɴᴇʟꜱ</code>
• /broadcast - <code>ᴛᴏ ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴀ ᴍᴇꜱꜱᴀɢᴇ ᴛᴏ ᴀʟʟ ᴜꜱᴇʀꜱ</code> </spoiler>
"""

    STATUS_TXT = """<blockquote>★ ᴛᴏᴛᴀʟ ꜰɪʟᴇꜱ: <code>{}</code>
★ ᴛᴏᴛᴀʟ ᴜꜱᴇʀꜱ: <code>{}</code>
★ ᴛᴏᴛᴀʟ ᴄʜᴀᴛꜱ: <code>{}</code>
★ ᴜꜱᴇᴅ ꜱᴛᴏʀᴀɢᴇ: <code>{}</code> 
★ ꜰʀᴇᴇ ꜱᴛᴏʀᴀɢᴇ: <code>{}</code> </blockquote>"""

    LOG_TEXT_G = """#ɴᴇᴡɢʀᴏᴜᴘ
ɢʀᴏᴜᴘ = {}(<code>{}</code>)
ᴛᴏᴛᴀʟ ᴍᴇᴍʙᴇʀꜱ = <code>{}</code>
ᴀᴅᴅᴇᴅ ʙʏ - {}
"""
    I_CUDNT = """🤧 𝗛𝗲𝗹𝗹𝗼 {}

𝗜 𝗰𝗼𝘂𝗹𝗱𝗻'𝘁 𝗳𝗶𝗻𝗱 𝗮𝗻𝘆 𝗺𝗼𝘃𝗶𝗲 𝗼𝗿 𝘀𝗲𝗿𝗶𝗲𝘀 𝗶𝗻 𝘁𝗵𝗮𝘁 𝗻𝗮𝗺𝗲.. 😐"""

    CUDNT_FND = """🤧 𝗛𝗲𝗹𝗹𝗼 {}

𝗜 𝗰𝗼𝘂𝗹𝗱𝗻'𝘁 𝗳𝗶𝗻𝗱 𝗮𝗻𝘆𝘁𝗵𝗶𝗻𝗴 𝗿𝗲𝗹𝗮𝘁𝗲𝗱 𝘁𝗼 𝘁𝗵𝗮𝘁 𝗱𝗶𝗱 𝘆𝗼𝘂 𝗺𝗲𝗮𝗻 𝗮𝗻𝘆 𝗼𝗻𝗲 𝗼𝗳 𝘁𝗵𝗲𝘀𝗲 ?? 👇"""
    
    LOG_TEXT_P = """#ɴᴇᴡᴜꜱᴇʀ
🆔ɪᴅ - <code>{}</code>
🧔ɴᴀᴍᴇ - {}
"""

    FOOTER_TEXT = """"""
    # FOOTER_TEXT = """❤ ɪꜰ ʏᴏᴜ ʟɪᴋᴇ ᴏᴜʀ ʙᴏᴛ ᴘʟᴇᴀꜱᴇ ʜᴇʟᴘ ᴜꜱ ᴍᴀɪɴᴛᴀɪɴɪɴɢ ꜱᴇʀᴠᴇʀ ᴄᴏꜱᴛ ʙʏ ᴅᴏɴᴀᴛɪɴɢ ꜱᴏᴍᴇ ᴀᴍᴏᴜɴᴛ..."""

    PROGRESS_BAR = """\n
╭━━━━❰ ʟᴀᴢʏ ᴘʀᴏɢʀᴇꜱꜱ ❱━➣
┣⪼ 🗂️ : {1} | {2}
┣⪼ ⏳️ : {0}%
┣⪼ 🚀 : {3}/s
┣⪼ ⏱️ : {4}
╰━━━━━━━━━━━━━━━➣ """
