import logging
import logging.config
# Credit @LazyDeveloper.
# Please Don't remove credit.
# Born to make history @LazyDeveloper !
# Thank you LazyDeveloper for helping us in this Journey
# 🥰  Thank you for giving me credit @LazyDeveloperr  🥰
# for any error please contact me -> telegram@LazyDeveloperr or insta @LazyDeveloperr 
# rip paid developers 🤣 - >> No need to buy paid source code while @LazyDeveloperr is here 😍😍
# Get logging configurations
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("imdbpy").setLevel(logging.ERROR)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger("aiohttp").setLevel(logging.ERROR)
logging.getLogger("aiohttp.web").setLevel(logging.ERROR)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

import os
from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from database.ia_filterdb import Media
from database.users_chats_db import db
from info import *
from utils import temp, get_popular_movies, get_lazy_goat_movies, get_lazy_trending_movies
from aiohttp import web
from plugins import web_server

import asyncio
from pyrogram import idle
from lazybot import LazyPrincessBot
from lazybot.clients import initialize_clients
from util.keepalive import ping_server

# Standard asyncio event loop for Pyrogram update listener compatibility
logging.info("⚡ Standard Asyncio Event Loop Active!")

PORT = "8080"
LazyPrincessBot.start()
loop = asyncio.get_event_loop()

async def Lazy_start():
    logging.info('\n⚙...............................................\n\n')
    logging.info('::::[ 🎉 Initializing Your Telegram Bot ⛱ ]::::')
    lazydeveloper_channels = await db.get_required_channels()
    logging.info("🔵⬜⬜⬜⬜ 25% - Just getting started!")
    await get_popular_movies()
    logging.info("🔵🔵⬜⬜⬜ 50% - Halfway there!")
    await get_lazy_goat_movies()
    logging.info("🔵🔵🔵🔵⬜ 70% - Almost done!")
    await get_lazy_trending_movies()
    temp.ASSIGNED_CHANNEL = lazydeveloper_channels

    if not os.path.isdir(DOWNLOAD_LOCATION):
        os.makedirs(DOWNLOAD_LOCATION)
    bot_info = await LazyPrincessBot.get_me()
    LazyPrincessBot.username = bot_info.username
    await initialize_clients()
    if ON_HEROKU:
        asyncio.create_task(ping_server())
    b_users, b_chats , lz_verified = await db.get_banned()
    temp.BANNED_USERS = b_users
    temp.BANNED_CHATS = b_chats
    temp.LAZY_VERIFIED_CHATS = lz_verified
    await Media.ensure_indexes()
    me = await LazyPrincessBot.get_me()
    temp.ME = me.id
    temp.U_NAME = me.username
    temp.B_NAME = me.first_name
    LazyPrincessBot.username = '@' + me.username
    app = web.AppRunner(await web_server())
    await app.setup()
    bind_address = "0.0.0.0" if ON_HEROKU else BIND_ADRESS
    await web.TCPSite(app, bind_address, PORT).start()
    lazylog = "\n\n:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::\n"
    lazylog += (f"{me.first_name} with for Pyrogram v{__version__} (Layer {layer}) started on {me.username}.\n")
    lazylog += (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::\n\n")
    logging.info(LOG_STR)
    lazylog += ("\n\n:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::\n")
    lazylog += (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::\n")
    lazylog += ('xxxx::::[ 🎉Initalized Brutal Force Subscribe  🧮 ]::::xxxx\n')
    lazylog += (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::\n")
    lazylog += (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::\n")
    lazylog += (f"\n\n<<<<::::::::::>>>>xxxxxxxxxxxxxxxxxx<<<<::::::::::>>>>\n")
    lazylog += (f"::::::::::::🔽 ASSIGNED CHANNELS LIST 🔽::::::::::::\n")
    i = 0
    for lazydev in temp.ASSIGNED_CHANNEL:
        i += 1
        lazylog += (f"<<<<:::::::>>>>𓆩ཫ {i} {lazydev} ཀ𓆪<<<<:::::::>>>>\n")
    lazylog += (f"<<<<::::::::::>>>>xxxxxxxxxxxxxxxxxx<<<<::::::::::>>>>\n\n")
    lazylog += ("""
  ╔════════════════════════════════════════╗
  ║  🎉 Everything Started Normally  🎉    ║
  ║   ✨ 𝙏𝙝𝙞𝙨 𝙄𝙨 𝙅𝙪𝙨𝙩 𝙏𝙝𝙚 𝘽𝙚𝙜𝙞𝙣𝙣𝙞𝙣𝙜. ✨    ║
  ║  🚀 𝙎𝙩𝙖𝙮 𝘽𝙤𝙡𝙙, 𝙎𝙩𝙖𝙮 𝙐𝙣𝙨𝙩𝙤𝙥𝙥𝙖𝙗𝙡𝙚! 🚀    ║
  ║════════════════════════════════════════║
  ║     ✅ BOT RUNNING IN LAZY-MODE ❤      ║
  ╚════════════════════════════════════════╝
""")

    logging.info(lazylog)
    logging.info("🔵🔵🔵🔵🔵 100% - Completed! 🎉")
    logging.info("\n\n[ 𓆩ཫ❤ Happy Journery ❤ཀ𓆪 ]")
    await idle()


if __name__ == '__main__':
    try:
        loop.run_until_complete(Lazy_start())
        logging.info('-----------------------🧐 Service running in Lazy Mode 😴-----------------------')
    except KeyboardInterrupt:
        logging.info('-----------------------😜 Service Stopped Sweetheart 😝-----------------------')
