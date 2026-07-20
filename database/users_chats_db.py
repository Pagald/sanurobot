# https://github.com/odysseusmax/animated-lamp/blob/master/bot/database/database.py
import motor.motor_asyncio
# import datetime
from info import DATABASE_NAME,DAILY_LIMIT, DATABASE_URI, IMDB, IMDB_TEMPLATE, MELCOW_NEW_USERS, P_TTI_SHOW_OFF, SINGLE_BUTTON, SPELL_CHECK_REPLY, PROTECT_CONTENT, MAX_BTN, URL_MODE, TUTORIAL, IS_TUTORIAL, URL_SHORTENR_WEBSITE, URL_SHORTNER_WEBSITE_API
from datetime import datetime, timedelta, date
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatJoinRequest
# Free limit per user
FREE_LIMIT = 3
JOIN_REQUIRED = 2  # Number of channels user must join for unlimited access
import pytz
timezone = pytz.timezone("Asia/Kolkata")

class Database:
    
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users
        self.grp = self.db.groups
        self.users = self.db.userdata
        self.req = self.db.requests
        self.top_search = self.db.top_search
        # 
        self.brutal = self.db.brutal
        self.channels = self.db.channels
        self.authchannels = self.db.authchannels
        self._auth_channels_cache = None
        self._limit_status_cache = None
        self._pm_search_status_cache = None
        self._send_mode_cache = None
        self._global_limit_cache = None

    def new_user(self, id, name):
        return dict(    
            id = id,
            name = name,
            _id=int(id),                                   
            file_id=None,
            caption=None,
            lazy_caption=None,
            join_date=date.today().isoformat(),
            apply_caption=True,
            upload_as_doc=False,
            thumbnail=None,
            ban_status=dict(
                is_banned=False,
                ban_reason="",
            ),
        )

    def new_group(self, id, title):
        return dict(
            id = id,
            title = title,
            chat_status=dict(
                is_disabled=False,
                is_lazy_verified=False,
                reason="",
            ),
        )



# 

    # async def is_subscribed(self, user_id):
    #     user = self.brutal.find_one({'user_id': user_id})
    #     if user and user.get('subscribed_channels'):
    #         return True
    #     return False
    async def get_auth_channels(self):
        if self._auth_channels_cache is not None:
            return self._auth_channels_cache
        channels_cursor = self.authchannels.find().sort('_id', -1)  # Fetch channels
        channels = await channels_cursor.to_list(length=None)  # Convert to list
        self._auth_channels_cache = [int(channel['channel_id']) for channel in channels]  # Ensure all IDs are integers
        return self._auth_channels_cache
    
    async def add_new_auth_channel(self, channel_id):
        # Check if the channel_id already exists
        existing_channel = await self.authchannels.find_one({"channel_id": channel_id})
        
        if existing_channel:
            return None  # Channel already exists, so don't insert
        
        # Insert only if it's not in the database
        result = await self.authchannels.insert_one({"channel_id": channel_id})
        self._auth_channels_cache = None # Invalidate cache
        return result.inserted_id  # Return the inserted channel's ID

    async def remove_auth_channel(self, channel_id):
        result = await self.authchannels.delete_one({"channel_id": channel_id})
        self._auth_channels_cache = None # Invalidate cache
        return result.deleted_count > 0  # Returns True if a channel was removed

    async def del_all_auth_channels(self):
        await self.authchannels.delete_many({})
        self._auth_channels_cache = [] # Set cache to empty

    async def get_global_limit(self):
        if self._global_limit_cache is not None:
            return self._global_limit_cache
        config = await self.db.config.find_one({"key": "global_limit"})
        if config:
            self._global_limit_cache = int(config.get("value", DAILY_LIMIT))
        else:
            self._global_limit_cache = DAILY_LIMIT
        return self._global_limit_cache

    async def set_global_limit(self, limit):
        await self.db.config.update_one(
            {"key": "global_limit"},
            {"$set": {"value": int(limit)}},
            upsert=True
        )
        self._global_limit_cache = int(limit)

    async def set_user_limit(self, user_id, limit):
        result = await self.users.update_one(
            {"id": int(user_id)},
            {"$set": {"daily_limit": int(limit)}}
        )
        return result.matched_count > 0

    async def get_limit_status(self):
        if self._limit_status_cache is not None:
            return self._limit_status_cache
        config = await self.db.config.find_one({"key": "limit_status"})
        if config:
            self._limit_status_cache = bool(config.get("enabled", True))
        else:
            self._limit_status_cache = True
        return self._limit_status_cache

    async def set_limit_status(self, enabled):
        await self.db.config.update_one(
            {"key": "limit_status"},
            {"$set": {"enabled": bool(enabled)}},
            upsert=True
        )
        self._limit_status_cache = bool(enabled)

    async def get_pm_search_status(self):
        if self._pm_search_status_cache is not None:
            return self._pm_search_status_cache
        config = await self.db.config.find_one({"key": "pm_search"})
        if config:
            self._pm_search_status_cache = bool(config.get("enabled", True))
        else:
            self._pm_search_status_cache = True
        return self._pm_search_status_cache

    async def set_pm_search_status(self, enabled):
        await self.db.config.update_one(
            {"key": "pm_search"},
            {"$set": {"enabled": bool(enabled)}},
            upsert=True
        )
        self._pm_search_status_cache = bool(enabled)

    async def get_send_mode(self):
        if self._send_mode_cache is not None:
            return self._send_mode_cache
        config = await self.db.config.find_one({"key": "send_mode"})
        if config:
            self._send_mode_cache = config.get("value", "channel")
        else:
            self._send_mode_cache = "channel"
        return self._send_mode_cache

    async def set_send_mode(self, mode):
        await self.db.config.update_one(
            {"key": "send_mode"},
            {"$set": {"value": mode}},
            upsert=True
        )
        self._send_mode_cache = mode


    async def get_required_channels(self):
        channels_cursor = self.channels.find().sort('_id', -1)  # Fetch channels
        channels = await channels_cursor.to_list(length=None)  # Convert to list
        return [int(channel['channel_id']) for channel in channels]  # Ensure all IDs are integers
    
    async def add_new_required_channel(self, channel_id):
        # Check if the channel_id already exists
        existing_channel = await self.channels.find_one({"channel_id": channel_id})
        
        if existing_channel:
            return None  # Channel already exists, so don't insert
        
        # Insert only if it's not in the database
        result = await self.channels.insert_one({"channel_id": channel_id})
        return result.inserted_id  # Return the inserted channel's ID

        # New method to deduct the daily limit for free users

    async def remove_required_channel(self, channel_id):
        result = await self.channels.delete_one({"channel_id": channel_id})
        return result.deleted_count > 0  # Returns True if a channel was removed

    async def deduct_limit(self, user_id):
        if not await self.get_limit_status():
            return True
        user = await self.get_user(user_id)
        if user:
            subscription = user.get("subscription", "free")
            limit_val = await self.get_global_limit()
            daily_limit = user.get("daily_limit", limit_val)
            
            # Check if the user is a free user
            if subscription == "free":
                if daily_limit > 0:
                    await self.users.update_one(
                        {"id": user_id},
                        {"$inc": {"daily_limit": -1}}
                    )
                    return True
                else:
                    return False  # No daily limit left
            return True  # No deduction for paid users
        return False  # User not found
   
    async def update_user(self, user_data):
        await self.users.update_one({"id": user_data["id"]}, {"$set": user_data}, upsert=True)
   
    async def get_user(self, user_id):
        user_data = await self.users.find_one({"id": user_id})
        return user_data
    
    async def get_all_joins(self):
        return self.users.find({})
    


    async def has_prime_status(self, user_id):
        user_data = await self.get_user(user_id)
        if user_data:
            expiry_time_str = user_data.get("subscription_expiry")

            if expiry_time_str is None:
                print("NO SUBSCRIPTION ")
                return False

            try:
                # Convert expiry time string back to datetime (assumes it's in UTC)
                expiry_time = datetime.strptime(expiry_time_str, "%Y-%m-%d %H:%M:%S")

                # Ensure the datetime is in UTC (or another timezone if needed)
                expiry_time = pytz.utc.localize(expiry_time)

                # Get current time in UTC
                current_time = datetime.now(pytz.utc)

                # Check if the current time is still within the expiry time
                if current_time <= expiry_time:
                    return True
                else:
                    # If expired, reset the expiry field in the database
                    limit_val = await self.get_global_limit()
                    await self.users.update_one({"id": user_id}, {"$set": {"subscription": "free", "daily_limit": limit_val, "subscription_expiry": None}})
                    return False  # Subscription has expired

            except ValueError:
                print(f"⚠️ Invalid expiry time format for user {user_id}: {expiry_time_str}")
            
        return False

    # async def has_prime_status(self, user_id):
    #     user_data = await self.get_user(user_id)
    #     if user_data:
    #         expiry_time_str = user_data.get("subscription_expiry")

    #         if expiry_time_str is None:
    #             # ❌ User previously used the free trial, but it has ended.
    #             return False

    #         try:
    #             # ⏳ Convert expiry time string back to datetime
    #             expiry_time = datetime.strptime(expiry_time_str, "%Y-%m-%d %H:%M:%S")

    #             # ✅ Check if current time is still within expiry time
    #             if datetime.now() <= expiry_time:
    #                 return True
    #             else:
    #                 # ❌ Expired, reset the expiry field
    #                 await self.users.update_one({"id": user_id}, {"$set": {"subscription_expiry": None}})
    #         except ValueError:
    #             print(f"⚠️ Invalid expiry time format for user {user_id}: {expiry_time_str}")
        
    #     return False

#     async def has_prime_status(self, user_id):
#         user_data = await self.get_user(user_id)

#         if user_data:
#             expiry_time = user_data.get("subscription_expiry")
#             if expiry_time is None:
#                 # User previously used the free trial, but it has ended.
#                 return False
#             elif isinstance(expiry_time, datetime) and datetime.now(timezone) <= expiry_time:
#                 return True
#             else:
#                 await self.users.update_one({"id": user_id}, {"$set": {"subscription_expiry": None}})
#         return False
      
# # 
    async def get_user_data(self, user_id):
        return self.brutal.find_one({'user_id': user_id})

    async def update_user_subscription(self, user_id, channels_joined):
        expiry_time = datetime.timezone.utc() + timedelta(hours=24)
        self.brutal.update_one(
            {'user_id': user_id},
            {'$set': {'subscribed_channels': channels_joined, 'expiry': expiry_time}},
            upsert=True
        )
        
    async def handle_subscription_check(self, client, message):
        user_id = message.from_user.id
        user_data = await self.get_user_data(user_id)
        
        if not user_data:
            self.brutal.insert_one({'user_id': user_id, 'free_videos': 0, 'subscribed_channels': [], 'expiry': None})
            user_data = {'free_videos': 0, 'subscribed_channels': [], 'expiry': None}
        
        if user_data['free_videos'] < FREE_LIMIT:
            self.brutal.update_one({'user_id': user_id}, {'$inc': {'free_videos': 1}})
            return True
        
        if user_data['expiry'] and datetime.now() < user_data['expiry']:
            return True
        
        required_channels = await self.get_required_channels()
        joined_channels = user_data.get('subscribed_channels', [])
        left_channels = list(set(required_channels) - set(joined_channels))
        
        if len(joined_channels) >= JOIN_REQUIRED:
            await self.update_user_subscription(user_id, joined_channels)
            return True
        
        btns = [[InlineKeyboardButton("Join Channel", url=f"https://t.me/{channel}")] for channel in left_channels[:JOIN_REQUIRED]]
        btns.append([InlineKeyboardButton("🔄 Try Again", callback_data="check_subscription")])
        await client.send_message(
            chat_id=user_id,
            text="🚨 You must join at least 2 channels to continue!",
            reply_markup=InlineKeyboardMarkup(btns)
        )
        return False



# 

    async def increment_search_count(self, query, user_id):
        """Increment search count for a query if the user hasn't searched it before."""
        query = query.strip()  # Remove leading/trailing spaces
        
        if not query:  # If query is empty, don't save it
            return  

        result = await self.top_search.find_one({'query': query})

        if result:
            if user_id not in result.get('user_ids', []):
                await self.top_search.update_one(
                    {'query': query},
                    {
                        '$addToSet': {'user_ids': user_id},
                        '$inc': {'count': 1}
                    }
                )
        else:
            await self.top_search.insert_one({
                'query': query,
                'user_ids': [user_id],
                'count': 1,
                'emoji': "🎬"
            })

        await self.update_emoji_for_all_queries()

    async def update_emoji_for_all_queries(self):
        """Update the emoji field for all queries based on their count values."""
        top_queries = await self.top_search.find().sort('count', -1).to_list(length=3)

        emojis = ["1ˢᵗ 👑 ⢾", "2ⁿᵈ 🔥 ⢾", "3ʳᵈ ❤ ⢾"]

        # Reset all emojis to default first
        await self.top_search.update_many({}, {'$set': {'emoji': "🎬"}})

        # Assign emojis to the top 3 queries
        for idx, query_data in enumerate(top_queries):
            emoji = emojis[idx] if idx < len(emojis) else "🎬"
            await self.top_search.update_one(
                {'query': query_data['query']},
                {'$set': {'emoji': emoji}}
            )


    # async def increment_search_count(self, query, user_id):
    #     """Increment search count for a query if the user hasn't searched it before."""
    #     result = await self.top_search.find_one({'query': query})

    #     if result:
    #         # Check if user_id is already in the list of users
    #         if user_id not in result.get('user_ids', []):
    #             # Add user_id and increment count
    #             await self.top_search.update_one(
    #                 {'query': query},
    #                 {
    #                     '$addToSet': {'user_ids': user_id},  # Add user_id if not already present
    #                     '$inc': {'count': 1}  # Increment the count
    #                 }
    #             )
    #     else:
    #         # Insert a new query entry if it doesn't exist
    #         await self.top_search.insert_one({
    #             'query': query,
    #             'user_ids': [user_id],  # Start with the current user
    #             'count': 1,
    #             'emoji': "🎬"  # 🎬 emoji assigned initially
    #         })

    #     # After increment, update the emoji based on the latest counts
    #     await self.update_emoji_for_all_queries()

    # async def update_emoji_for_all_queries(self):
    #     """Update the emoji field for all queries based on their count values."""
    #     # Fetch all queries sorted by count in descending order
    #     top_queries = await self.top_search.find().sort('count', -1).to_list(length=3)

    #     # Define emoji rankings
    #     emojis = ["1ˢᵗ 👑 ⢾", "2ⁿᵈ 🔥 ⢾", "3ʳᵈ ❤ ⢾"]
        
    #     # Update emojis for the top 3 queries
    #     for idx, query_data in enumerate(top_queries):
    #         emoji = emojis[idx] if idx < len(emojis) else "🎬"
    #         await self.top_search.update_one(
    #             {'query': query_data['query']},
    #             {'$set': {'emoji': emoji}}
    #         )

    async def get_top_searches(self, limit=100):
        """Retrieve the top 'n' searches."""
        cursor = self.top_search.find().sort('count', -1).limit(limit)
        results = await cursor.to_list(length=limit)
        
        # Format the results with emojis
        return [{'query': res['query'], 'count': res['count'], 'emoji': res.get('emoji')} for res in results]


# 

    # async def increment_search_count(self, query, user_id):
    #     """Increment search count for a query if the user hasn't searched it before."""
    #     result = await self.top_search.find_one({'query': query})

    #     if result:
    #         # Check if user_id is already in the list of users
    #         if user_id not in result.get('user_ids', []):
    #             # Add user_id and increment count
    #             await self.top_search.update_one(
    #                 {'query': query},
    #                 {
    #                     '$addToSet': {'user_ids': user_id},  # Add user_id if not already present
    #                     '$inc': {'count': 1}  # Increment the count
    #                 }
    #             )
    #     else:
    #         # Insert a new query entry if it doesn't exist
    #         await self.top_search.insert_one({
    #             'query': query,
    #             'user_ids': [user_id],  # Start with the current user
    #             'count': 1
    #         })
    
    # async def get_top_searches(self, limit=10):
    #     """Retrieve the top 'n' searches."""
    #     cursor = self.top_search.find().sort('count', -1).limit(limit)
    #     results = await cursor.to_list(length=limit)
    #     # Format the results if needed
    #     return [{'query': res['query'], 'count': res['count']} for res in results]

    # async def clear_user_searches(self, user_id):
    #     """Remove a user's searches."""
    #     await self.top_search.update_many(
    #         {'user_ids': user_id},
    #         {
    #             '$pull': {'user_ids': user_id},  # Remove the user_id from user_ids
    #             '$inc': {'count': -1}  # Decrement the count
    #         }
    #     )
    #     # Remove queries with count <= 0
    #     await self.top_search.delete_many({'count': {'$lte': 0}})

# 
    # async def find_join_req(self, id):
    #     return bool(await self.req.find_one({'id': id}))
        
    # async def add_join_req(self, id):
    #     await self.req.insert_one({'id': id})
    
    async def find_join_req(self, user_id, chat_id):
        return bool(await self.req.find_one({'user_id': user_id, 'chat_id': chat_id}))
        
    async def add_join_req(self, user_id, chat_id):
        await self.req.insert_one({'user_id': user_id, 'chat_id': chat_id})

    async def del_join_req(self):
        await self.req.delete_many({})
    
    # async def del_join_req(self):
    #     await self.req.drop()
    
    async def add_user(self, id, name):
        user = self.new_user(id, name)
        await self.col.insert_one(user)
    
    async def is_user_exist(self, id):
        user = await self.col.find_one({'id':int(id)})
        return bool(user)
    
    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count
    
    async def remove_ban(self, id):
        ban_status = dict(
            is_banned=False,
            ban_reason=''
        )
        await self.col.update_one({'id': id}, {'$set': {'ban_status': ban_status}})
    
   
    async def ban_user(self, user_id, ban_reason="No Reason"):
        ban_status = dict(
            is_banned=True,
            ban_reason=ban_reason
        )
        await self.col.update_one({'id': user_id}, {'$set': {'ban_status': ban_status}})

    async def get_ban_status(self, id):
        default = dict(
            is_banned=False,
            ban_reason=''
        )
        user = await self.col.find_one({'id':int(id)})
        if not user:
            return default
        return user.get('ban_status', default)

    async def get_all_users(self):
        return self.col.find({})
    
  
    async def remove_prime_status(self, user_id):
        return await self.update_one(
            {"id": user_id}, {"$set": {"expiry_time": None}}
        )
    
    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})
                
    async def get_banned(self):
        users = self.col.find({'ban_status.is_banned': True})
        chats = self.grp.find({'chat_status.is_disabled': True})
        is_verified = self.grp.find({'chat_status.is_lazy_verified': True})
        b_chats = [chat['id'] async for chat in chats]
        b_users = [user['id'] async for user in users]
        lz_verified = [chat['id'] async for chat in is_verified]
        return b_users, b_chats, lz_verified

    async def add_chat(self, chat, title):
        chat = self.new_group(chat, title)
        await self.grp.insert_one(chat)
    
    async def get_chat(self, chat):
        chat = await self.grp.find_one({'id':int(chat)})
        return False if not chat else chat.get('chat_status')
    
    async def re_enable_chat(self, id):
        chat_status=dict(
            is_disabled=False,
            reason="",
            )
        await self.grp.update_one({'id': int(id)}, {'$set': {'chat_status': chat_status}})
        
    async def update_settings(self, id, settings):
        await self.grp.update_one({'id': int(id)}, {'$set': {'settings': settings}})
    
    async def get_settings(self, id):
        default = {
            'button': SINGLE_BUTTON,
            'botpm': P_TTI_SHOW_OFF,
            'file_secure': PROTECT_CONTENT,
            'imdb': IMDB,
            'spell_check': SPELL_CHECK_REPLY,
            'welcome': MELCOW_NEW_USERS,
            'template': IMDB_TEMPLATE,
            'max_btn': MAX_BTN,
            'shortlink': URL_SHORTENR_WEBSITE,
            'shortlink_api': URL_SHORTNER_WEBSITE_API,
            'url_mode': URL_MODE,
            'tutorial': TUTORIAL,
            'is_tutorial': IS_TUTORIAL

        }
        chat = await self.grp.find_one({'id':int(id)})
        if chat:
            return chat.get('settings', default)
        return default

    async def disable_chat(self, chat, reason="No Reason"):
        chat_status=dict(
            is_disabled=True,
            reason=reason,
            )
        await self.grp.update_one({'id': int(chat)}, {'$set': {'chat_status': chat_status}})

    async def verify_lazy_chat(self, chat):
        chat_status=dict(
            is_lazy_verified=True,
            )
        await self.grp.update_one({'id': int(chat)}, {'$set': {'chat_status': chat_status}})
    
    async def total_chat_count(self):
        count = await self.grp.count_documents({})
        return count
    
    async def get_all_chats(self):
        return self.grp.find({})

    async def get_db_size(self):
        return (await self.db.command("dbstats"))['dataSize']
    
    async def set_apply_caption(self, id, apply_caption):
        await self.col.update_one({'id': id}, {'$set': {'apply_caption': apply_caption}})

    async def get_apply_caption(self, id):
        user = await self.col.find_one({'id': int(id)})
        return user.get('apply_caption', True)

    async def set_upload_as_doc(self, id, upload_as_doc):
        await self.col.update_one({'id': id}, {'$set': {'upload_as_doc': upload_as_doc}})

    async def get_upload_as_doc(self, id):
        user = await self.col.find_one({'id': int(id)})
        return user.get('upload_as_doc', False)

    async def set_lazy_thumbnail(self, id, thumbnail):
        await self.col.update_one({'id': id}, {'$set': {'thumbnail': thumbnail}})

    async def get_lazy_thumbnail(self, id):
        user = await self.col.find_one({'id': int(id)})
        return user.get('thumbnail', None)

    async def get_lazy_caption(self, id):
        user = await self.col.find_one({'id': int(id)})
        return user.get('lazy_caption', None)

    async def get_user_data(self, id) -> dict:
        user = await self.col.find_one({'id': int(id)})
        return user or None
        
    # Thank you LazyDeveloper for helping us in this Journey
    # Just for renamer @LazyDeveloper 
    async def set_thumbnail(self, id, file_id):
        await self.col.update_one({'id': int(id)}, {'$set': {'file_id': file_id}})
        
    async def get_thumbnail(self, id):
        try:
            thumbnail = await self.col.find_one({'id': int(id)})
            if thumbnail:
                return thumbnail.get('file_id')
            else:
                return None
        except Exception as e:
            print(e)
    # Born to make history @LazyDeveloper ! => Remember this name forever <=

    async def set_caption(self, id, caption):
        await self.col.update_one({'id': int(id)}, {'$set': {'caption': caption}})

    async def get_caption(self, id):
        user = await self.col.find_one({'id': int(id)})
        return user.get('caption', None)


db = Database(DATABASE_URI, DATABASE_NAME)
