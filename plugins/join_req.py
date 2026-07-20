from pyrogram import Client, filters, enums
from pyrogram.types import ChatJoinRequest
from database.users_chats_db import db
from info import ADMINS,MAX_SUBSCRIPTION_TIME,LAZYCONTAINER
from utils import temp,to_small_caps,lazy_readable
from datetime import datetime, timedelta
import pytz
import logging
import asyncio
from Script import script
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.ia_filterdb import get_file_details
from database.users_chats_db import db
from info import *
#5 => verification_steps ! [Youtube@LazyDeveloperr]
from utils import  get_size, temp
from urllib.parse import quote
from utils import schedule_deletion, to_small_caps
from plugins.commands import send_lazy_video
import base64
logger = logging.getLogger(__name__)
from utils import temp
import pytz  # Make sure to handle timezone correctly

timezone = pytz.timezone("Asia/Kolkata")

class MockMessage:
    def __init__(self, user, client):
        self.from_user = user
        self.chat = user
        self.chat.type = enums.ChatType.PRIVATE
        self.chat.title = user.first_name if user.first_name else "User"
        self.command = ["start"]
        self.message_id = 0
        self.id = 0
        self.client = client
        self.loading_message_id = None
        
    async def reply_photo(self, photo, caption=None, reply_markup=None, *args, **kwargs):
        return await self.client.send_photo(
            chat_id=self.from_user.id,
            photo=photo,
            caption=caption,
            reply_markup=reply_markup,
            *args, **kwargs
        )

    async def reply_text(self, text, reply_markup=None, *args, **kwargs):
        return await self.client.send_message(
            chat_id=self.from_user.id,
            text=text,
            reply_markup=reply_markup,
            *args, **kwargs
        )

    async def reply(self, text, reply_markup=None, *args, **kwargs):
        return await self.client.send_message(
            chat_id=self.from_user.id,
            text=text,
            reply_markup=reply_markup,
            *args, **kwargs
        )

    async def delete(self, *args, **kwargs):
        pass

@Client.on_chat_join_request()
async def join_reqs(client, message: ChatJoinRequest):
  auth_channels = await db.get_auth_channels()
  if not auth_channels:
    auth_channels = AUTH_CHANNEL
    
  if message.chat.id in auth_channels:
    if not await db.find_join_req(message.from_user.id, message.chat.id):
      await db.add_join_req(message.from_user.id, message.chat.id)
      
      user_data = await db.get_user(message.from_user.id)
      if user_data:
          last_file = user_data.get("last_requested_file")
          if last_file:
              # Clear the last requested file and assigned channel first to prevent duplicate sends
              await db.users.update_one(
                  {"id": message.from_user.id},
                  {"$unset": {
                      "last_requested_file": "",
                      "assigned_channel": ""
                  }}
              )
              
              # Send a loading/processing message
              loading_msg = None
              try:
                  loading_msg = await client.send_message(
                      chat_id=message.from_user.id,
                      text="🔄 **Request received! Verifying join status and preparing your file... Please wait...**"
                  )
              except Exception as e:
                  logger.error(f"Failed to send loading message: {e}")

              from plugins.commands import deliver_file_directly
              loading_id = loading_msg.id if loading_msg else None
              await deliver_file_directly(client, message.from_user, last_file, loading_message_id=loading_id, user_data=user_data)

@Client.on_message(filters.command("delreq") & filters.private & filters.user(ADMINS))
async def del_requests(client, message):
    await db.del_join_req()   
    await message.reply("<b>⚙ ꜱᴜᴄᴄᴇꜱꜱғᴜʟʟʏ ᴄʜᴀɴɴᴇʟ ʟᴇғᴛ ᴜꜱᴇʀꜱ ᴅᴇʟᴇᴛᴇᴅ</b>")

# lazydeloper

# @Client.on_message(filters.command("delreq") & filters.private & filters.user(ADMINS))
# async def del_requests(client, message):
#     await db.del_join_req()    
#     await message.reply("<b>⚙ ꜱᴜᴄᴄᴇꜱꜱғᴜʟʟʏ ᴄʜᴀɴɴᴇʟ ʟᴇғᴛ ᴜꜱᴇʀꜱ ᴅᴇʟᴇᴛᴇᴅ</b>")
