import logging
from pyrogram.errors import InputUserDeactivated, UserNotParticipant, FloodWait, UserIsBlocked, PeerIdInvalid
from info import *
from imdb import IMDb, Movie
import asyncio
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import enums, filters
from typing import Union
import re
import os
from typing import List
from database.users_chats_db import db
from bs4 import BeautifulSoup
import requests
import aiohttp

#3 => verification_steps ! [Youtube@LazyDeveloperr]
from Script import script #add this
import pytz #add this
from datetime import datetime, date #add this
import random 
import string
import time
from pyrogram.enums import ChatMemberStatus

# ./done_lazy_baby 
from imdb import Cinemagoer

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

BTN_URL_REGEX = re.compile(
    r"(\[([^\[]+?)\]\((buttonurl|buttonalert):(?:/{0,2})(.+?)(:same)?\))"
)

imdb = IMDb() 
# imdb = Cinemagoer() 

BANNED = {}
SMART_OPEN = '“'
SMART_CLOSE = '”'
START_CHAR = ('\'', '"', SMART_OPEN)
START_CHAR = ('\'', '"', SMART_OPEN)

VERIFIED = {} 
TOKENS = {} 


class temp(object):
    BANNED_USERS = []
    BANNED_CHATS = []
    LAZY_VERIFIED_CHATS = []
    ME = None
    CURRENT=int(os.environ.get("SKIP", 2))
    CANCEL = False
    MELCOW = {}
    GETALL = {}
    SHORT = {}
    IMDB_CAP = {}
    U_NAME = None
    B_NAME = None
    SETTINGS = {}

    # Cache for popular movies
    POPULAR_MOVIES = []
    POPULAR_MOVIES_TIMESTAMP = 0  # Timestamp for last update
    
    # Cache for popular movies
    LAZYGOAT_MOVIES = []
    LAZYGOAT_MOVIES_TIMESTAMP = 0  # Timestamp for last update
    # Cache for popular movies
    LAZYTRENDING_MOVIES = []
    TRENDING_MOVIES_TIMESTAMP = 0  # Timestamp for last update
    TRENDING_CACHE_DURATION = 60 # isko 1 minute hi rehne do 
    CACHE_DURATION = 86400   # 24 hours in seconds
    ASSIGNED_CHANNEL = []
    LAZY_LOCAL_FILES = {}

def lazy_readable(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, sec = divmod(remainder, 60)
    parts = []
    if hours > 0:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes > 0:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    if sec > 0 or not parts:  # Show seconds if no other parts
        parts.append(f"{sec} second{'s' if sec != 1 else ''}")
    return ", ".join(parts)

async def schedule_deletion(client, chat_id, lazyfiles, BATCH=False):
    try:
        # Wait for -- minutes
        # Lmg = await client.send_message(chat_id = chat_id, text=f"<b>❗️ <u>ɪᴍᴘᴏʀᴛᴀɴᴛ</u> ❗️</b>\n\n<b>ᴛʜᴇꜱᴇ ᴠɪᴅᴇᴏ / ᴠɪᴅᴇᴏꜱ  ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ɪɴ</b> <b><u>{lazy_readable(FILE_AUTO_DELETE_TIME)}</u></b><b>(ᴅᴜᴇ ᴛᴏ ᴄᴏᴘʏʀɪɢʜᴛ ɪꜱꜱᴜᴇꜱ).</b>\n\n<b><i>📌 ᴘʟᴇᴀꜱᴇ ꜰᴏʀᴡᴀʀᴅ ᴛʜᴇꜱᴇ ᴠɪᴅᴇᴏꜱ / ꜰɪʟᴇꜱ ᴛᴏ ꜱᴏᴍᴇᴡʜᴇʀᴇ ᴇʟꜱᴇ ᴀɴᴅ ꜱᴛᴀʀᴛ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ᴛʜᴇʀᴇ.</i></b>")
        await asyncio.sleep(FILE_AUTO_DELETE_TIME)  # -- minutes in seconds
        if BATCH:
            for x in lazyfiles:
                await x.delete()
            # print("🚩 LAZY DELETION DONE ::>> For BATCH File ✅")
        else:
            await lazyfiles.delete()
            # print("🚩 LAZY DELETION DONE ::>> For Single File ✅")
    except Exception as e:
        logging.info(f"Error in deletion task: {e}")

def to_small_caps(text):
    small_caps = {
        'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ', 'f': 'ғ', 'g': 'ɢ', 'h': 'ʜ', 'i': 'ɪ', 'j': 'ᴊ', 
        'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ', 'o': 'ᴏ', 'p': 'ᴘ', 'q': 'ǫ', 'r': 'ʀ', 's': 's', 't': 'ᴛ', 
        'u': 'ᴜ', 'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x', 'y': 'ʏ', 'z': 'ᴢ'
    }
    return ''.join([small_caps.get(c, c) for c in text.lower()])

# lazy Function to fetch popular movies
async def get_popular_movies():
    current_time = time.time()
    if current_time - temp.POPULAR_MOVIES_TIMESTAMP > temp.CACHE_DURATION:
        list1 = []
        list2 = []
        list3 = []
        movies= []
        # Fetch popular TV shows

        try:
            list3 = imdb.get_popular100_movies() #😢 Not working well #lazydeveloper
        
            # print(f"list3 => {list3}")
        except Exception as lazydeveloper:
            logging.info(f"Try again later : No data available for Movies: {lazydeveloper}")

        try:
            list1 = imdb.get_popular100_tv()#working  -- Popular Webseries - #worldwide list !#Lazydeveloper add more here as u wish 
        
            # print(f"list1 => {list1}")
        except Exception as lazydeveloper:
            logging.info(f"Try again later : No data available for TV shows: {lazydeveloper}")

        try:
            list2 = imdb.get_boxoffice_movies()#working -- ! List of top box-office movies
            # print(f"list2 => {list2}")
        except Exception as lazydeveloper:
            logging.info(f"Try again later : No data available for BOX-OFFICE: {lazydeveloper}")
        

        # Extend movies only if the lists have data
        if list3:
            movies.extend(list3)
        if list1:
            movies.extend(list1)
        if list2:
            movies.extend(list2)

        popular_movies = []
        for movie in movies:
            try:
                title = movie.get('title')
                movie_id = movie.movieID

                # Validate title and movieID
                if isinstance(title, str) and title.strip() and isinstance(movie_id, str):
                    popular_movies.append((title, movie_id))
                else:
                    logging.info(f"Invalid movie data: {movie}")
            except Exception as e:
                logging.info(f"Error processing movie: {movie}, Error: {e}")

        temp.POPULAR_MOVIES = popular_movies
        temp.POPULAR_MOVIES_TIMESTAMP = current_time

    return temp.POPULAR_MOVIES

# lazy Function to fetch greatest of all time movies
async def get_lazy_goat_movies():
    current_time = time.time()
    
    if current_time - temp.LAZYGOAT_MOVIES_TIMESTAMP > temp.CACHE_DURATION:
        list1 = []
        list2 = []
        list3 = []
        movies= []
        try:
            list1 = imdb.get_top250_movies()
        except Exception as lazydeveloper:
            logging.info(f"No data available for G.O.A.T movie list1 : {lazydeveloper}")
        
        try:
            list2 = imdb.get_bottom100_movies()
        except Exception as lazydeveloper:
            logging.info(f"No data available for G.O.A.T movie list2 : {lazydeveloper}")
        
        try:
            list3 = imdb.get_top250_tv()
        except Exception as lazydeveloper:
            logging.info(f"No data available for G.O.A.T tv list : {lazydeveloper}")
        
        try:
            list4 = imdb.get_top250_indian_movies()
        except Exception as lazydeveloper:
            logging.info(f"No data available for [INDIAN] G.O.A.T movie list4 : {lazydeveloper}")

        # extend movies only if the lists have data 😢#lazydeveloperr find any better way
        if list1:
            movies.extend(list1)
        if list2:
            movies.extend(list2)
        if list3:
            movies.extend(list3)
        if list4:
            movies.extend(list4)

        lazygoat_movies = [(movie.get('title'), movie.movieID) for movie in movies]  # Fetch top 5 movies
        temp.LAZYGOAT_MOVIES = lazygoat_movies
        temp.LAZYGOAT_MOVIES_TIMESTAMP = current_time

    return temp.LAZYGOAT_MOVIES

# lazy Function to fetch trending movies
async def get_lazy_trending_movies():
    current_time = time.time()
    if current_time - temp.TRENDING_MOVIES_TIMESTAMP > temp.TRENDING_CACHE_DURATION:
        lazytrends = await db.get_top_searches()
        lazygoat_movies = [(movie.get('query'), movie.get('emoji')) for movie in lazytrends]  # Fetch top 5 movies
        temp.LAZYTRENDING_MOVIES = lazygoat_movies
        temp.TRENDING_MOVIES_TIMESTAMP = current_time
        # print(temp.LAZYTRENDING_MOVIES)
    return temp.LAZYTRENDING_MOVIES


# ==============================================================================
async def is_subscribed(bot, channel, lazyuserr):
    try:
        user = await bot.get_chat_member(channel, lazyuserr)
    except UserNotParticipant:
        pass
    except Exception as e:
        logger.exception(e)
    else:
        if user.status != enums.ChatMemberStatus.BANNED:
            return True

    return False

# # ==============================================================================
# async def lazy_has_subscribed(client, update):
#     if not AUTH_CHANNEL: 
#         return True

#     lazydeveloperIDS = update.from_user.id
#     if lazydeveloperIDS in ADMINS:
#         return True

#     for channel in AUTH_CHANNEL:
#         if await db.find_join_req(update.from_user.id):
#             return True
#         try:
#             lazydeveloperMBS = await client.get_chat_member(chat_id=channel, user_id=lazydeveloperIDS)
#         except UserNotParticipant:
#             return False
#         if lazydeveloperMBS.status not in [ChatMemberStatus.OWNER, 
#                                 ChatMemberStatus.ADMINISTRATOR, 
#                                 ChatMemberStatus.MEMBER]:
#             return False

#     return True
# # ==============================================================================

# [[[[[[[[[[[[[[[[[[[]]]]]]]]]]]]]]]]]]]
# ==============================================================================
async def get_first_unjoined_channel(client, user_id):
    if user_id in ADMINS:
        return None

    auth_channels = await db.get_auth_channels()
    if not auth_channels:
        auth_channels = AUTH_CHANNEL
    if not auth_channels:
        return None

    for channel in auth_channels:
        # check DB if user already has a record for this channel
        if await db.find_join_req(user_id, int(channel)):
            continue

        try:
            lazydeveloperMBS = await client.get_chat_member(
                chat_id=int(channel), 
                user_id=user_id
            )
            if lazydeveloperMBS.status in [
                ChatMemberStatus.OWNER, 
                ChatMemberStatus.ADMINISTRATOR, 
                ChatMemberStatus.MEMBER
            ]:
                continue
        except UserNotParticipant:
            return int(channel)
        except Exception as e:
            logger.error(f"Error checking chat member for channel {channel}: {e}")
            return int(channel)

    return None

async def lazy_has_subscribed(client, update):
    user_id = update.from_user.id
    unjoined = await get_first_unjoined_channel(client, user_id)
    return unjoined is None
# ==============================================================================

# [[[[[[[[[[[[[[[[[[[]]]]]]]]]]]]]]]]]]]


# no use
async def get_poster2(query, bulk=False, id=False, file=None):
    if not id:
        query = (query.strip()).lower()
        title = query
        year = re.findall(r'[1-2]\d{3}$', query, re.IGNORECASE)
        if year:
            year = list_to_str(year[:1])
            title = (query.replace(year, "")).strip()
        elif file is not None:
            year = re.findall(r'[1-2]\d{3}', file, re.IGNORECASE)
            if year:
                year = list_to_str(year[:1]) 
        else:
            year = None
        movieid = imdb.search_movie(title.lower(), results=10)
        if not movieid:
            return None
        if year:
            filtered=list(filter(lambda k: str(k.get('year')) == str(year), movieid))
            if not filtered:
                filtered = movieid
        else:
            filtered = movieid
        movieid=list(filter(lambda k: k.get('kind') in ['movie', 'tv series'], filtered))
        if not movieid:
            movieid = filtered
        if bulk:
            return movieid
        movieid = movieid[0].movieID
    else:
        movieid = query
    movie = imdb.get_movie(movieid)
    if movie.get("original air date"):
        date = movie["original air date"]
    elif movie.get("year"):
        date = movie.get("year")
    else:
        date = "N/A"
    plot = ""
    if not LONG_IMDB_DESCRIPTION:
        plot = movie.get('plot')
        if plot and len(plot) > 0:
            plot = plot[0]
    else:
        plot = movie.get('plot outline')
    if plot and len(plot) > 800:
        plot = plot[0:800] + "..."

    return {
        'title': movie.get('title'),
        'votes': movie.get('votes'),
        "aka": list_to_str(movie.get("akas")),
        "seasons": movie.get("number of seasons"),
        "box_office": movie.get('box office'),
        'localized_title': movie.get('localized title'),
        'kind': movie.get("kind"),
        "imdb_id": f"tt{movie.get('imdbID')}",
        "cast": list_to_str(movie.get("cast")),
        "runtime": list_to_str(movie.get("runtimes")),
        "countries": list_to_str(movie.get("countries")),
        "certificates": list_to_str(movie.get("certificates")),
        "languages": list_to_str(movie.get("languages")),
        "director": list_to_str(movie.get("director")),
        "writer":list_to_str(movie.get("writer")),
        "producer":list_to_str(movie.get("producer")),
        "composer":list_to_str(movie.get("composer")) ,
        "cinematographer":list_to_str(movie.get("cinematographer")),
        "music_team": list_to_str(movie.get("music department")),
        "distributors": list_to_str(movie.get("distributors")),
        'release_date': date,
        'year': movie.get('year'),
        'genres': list_to_str(movie.get("genres")),
        'poster': movie.get('full-size cover url'),
        'plot': plot,
        'rating': str(movie.get("rating")),
        'url':f'https://www.imdb.com/title/tt{movieid}'
    }

# 🚩 currently using this logic
async def get_poster(query, bulk=False, id=False, file=None):
    if not id:
        query = (query.strip()).lower()
        title = query
        year = re.findall(r'[1-2]\d{3}$', query, re.IGNORECASE)
        if year:
            year = list_to_str(year[:1])
            title = (query.replace(year, "")).strip()
        elif file is not None:
            year = re.findall(r'[1-2]\d{3}', file, re.IGNORECASE)
            if year:
                year = list_to_str(year[:1]) 
        else:
            year = None
        movieid = imdb.search_movie(title.lower(), results=10)
        if not movieid:
            return None
        if year:
            filtered=list(filter(lambda k: str(k.get('year')) == str(year), movieid))
            if not filtered:
                filtered = movieid
        else:
            filtered = movieid
        movieid=list(filter(lambda k: k.get('kind') in ['movie', 'tv series'], filtered))
        if not movieid:
            movieid = filtered
        if bulk:
            return movieid
        movieid = movieid[0].movieID
    else:
        movieid = query
    movie = imdb.get_movie(movieid)
    if movie.get("original air date"):
        date = movie["original air date"]
    elif movie.get("year"):
        date = movie.get("year")
    else:
        date = "N/A"
    plot = ""
    if not LONG_IMDB_DESCRIPTION:
        plot = movie.get('plot')
        if plot and len(plot) > 0:
            plot = plot[0]
    else:
        plot = movie.get('plot outline')
    if plot and len(plot) > 800:
        plot = plot[0:800] + "..."
    
    return {
        'title': movie.get('title'),
        'votes': movie.get('votes'),
        "aka": list_to_str(movie.get("akas")),
        "seasons": movie.get("number of seasons"),
        "box_office": movie.get('box office'),
        'localized_title': movie.get('localized title'),
        'kind': movie.get("kind"),
        "imdb_id": f"tt{movie.get('imdbID')}",
        "cast": list_to_str(movie.get("cast")),
        "runtime": list_to_str(movie.get("runtimes")),
        "countries": list_to_str(movie.get("countries")),
        "certificates": list_to_str(movie.get("certificates")),
        "languages": list_to_str(movie.get("languages")),
        "director": list_to_str(movie.get("director")),
        "writer":list_to_str(movie.get("writer")),
        "producer":list_to_str(movie.get("producer")),
        "composer":list_to_str(movie.get("composer")) ,
        "cinematographer":list_to_str(movie.get("cinematographer")),
        "music_team": list_to_str(movie.get("music department")),
        "distributors": list_to_str(movie.get("distributors")),
        'release_date': date,
        'year': movie.get('year'),
        'genres': list_to_str(movie.get("genres")),
        'poster': movie.get('full-size cover url', PICS),
        'plot': plot,
        'rating': str(movie.get("rating")),
        'url':f'https://www.imdb.com/title/tt{movieid}'
    }

# ONLY TITLE POSTER 
async def get_poster3(query, bulk=False, id=False):
    if not id:
        query = query.strip().lower()
        title = query
        year = re.findall(r'[1-2]\d{3}$', query, re.IGNORECASE)
        if year:
            year = year[0]
            title = query.replace(year, "").strip()
        movieid = imdb.search_movie(title, results=10)
        if not movieid:
            return None
        if year:
            movieid = [m for m in movieid if str(m.get('year')) == str(year)]
        movieid = [m for m in movieid if m.get('kind') in ['movie', 'tv series']]
        if not movieid:
            return None
        if bulk:
            return movieid
        movieid = movieid[0].movieID
    else:
        movieid = query

    movie = imdb.get_movie(movieid)
    return {
        'title': movie.get('title'),
        'poster': movie.get('full-size cover url', PICS)
    }

# no use
async def get_poster4x(query, bulk=False, id=False, file=None):
    if not id:
        query = (query.strip()).lower()
        title = query
        year = None

        # Extract year from the file name if provided
        if file is not None:
            year = re.findall(r'[1-2]\d{3}', file, re.IGNORECASE)
            if year:
                year = list_to_str(year[:1])

        # Extract year from query if not found in file
        if not year:
            year = re.findall(r'[1-2]\d{3}$', query, re.IGNORECASE)
            if year:
                year = list_to_str(year[:1])
                title = (query.replace(year, "")).strip()

        # Search for movie using IMDb
        movieid = imdb.search_movie(title.lower(), results=10)
        if not movieid:
            return None

        # Filter by year if available
        if year:
            filtered = list(filter(lambda k: str(k.get('year')) == str(year), movieid))
            if not filtered:
                filtered = movieid
        else:
            filtered = movieid

        # Filter for movies or TV series
        movieid = list(filter(lambda k: k.get('kind') in ['movie', 'tv series'], filtered))
        if not movieid:
            movieid = filtered

        if bulk:
            return movieid

        movieid = movieid[0].movieID
    else:
        movieid = query

    # Fetch movie details
    movie = imdb.get_movie(movieid)

    # Return required fields
    return {
        'title': movie.get('title'),
        'poster': movie.get('full-size cover url', PICS),
        'rating': str(movie.get('rating')),
        'url': f'https://www.imdb.com/title/tt{movieid}'
    }

# no use
async def get_poster4as(query, bulk=False, id=False):
    query = query.strip().lower()

    # Search for movie
    movieid = imdb.search_movie(query, results=10)
    if not movieid:
        return None

    # Filter for movies or TV series
    filtered = list(filter(lambda k: k.get('kind') in ['movie', 'tv series'], movieid))
    if not filtered:
        filtered = movieid

    if bulk:
        return filtered

    movieid = filtered[0].movieID
    movie = imdb.get_movie(movieid)

    return {
        'title': movie.get('title'),
        'poster': movie.get('full-size cover url', PICS),
        'rating': str(movie.get('rating')),
        'url': f'https://www.imdb.com/title/tt{movieid}'
    }

# no use
async def get_poster4(query, bulk=False, id=False):
    query = query.strip().lower()

    # Perform a more restricted search to minimize the response size
    movieid = imdb.search_movie(query, results=1)  # Limit results to 1 if you're sure the query is unique
    if not movieid:
        return None

    movieid = movieid[0].movieID  # Get the ID of the first result

    # Retrieve only the necessary fields instead of all movie details
    movie = imdb.get_movie(movieid)

    return {
        'title': movie.get('title'),
        'poster': movie.get('full-size cover url', PICS),
        'rating': str(movie.get('rating')),
        'url': f'https://www.imdb.com/title/tt{movieid}'
    }


async def broadcast_messages(user_id, message):
    try:
        await message.copy(chat_id=user_id)
        return True, "Success"
    except FloodWait as e:
        await asyncio.sleep(e.x)
        return await broadcast_messages(user_id, message)
    except InputUserDeactivated:
        await db.delete_user(int(user_id))
        logging.info(f"{user_id}-Removed from Database, since deleted account.")
        return False, "Deleted"
    except UserIsBlocked:
        logging.info(f"{user_id} -Blocked the bot.")
        return False, "Blocked"
    except PeerIdInvalid:
        await db.delete_user(int(user_id))
        logging.info(f"{user_id} - PeerIdInvalid")
        return False, "Error"
    except Exception as e:
        return False, "Error"

async def search_gagala(text):
    usr_agent = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/109.0.5414.120 Safari/537.36'
        }
    text = text.replace(" ", '+')
    url = f'https://www.google.com/search?q={text}'
    response = requests.get(url, headers=usr_agent)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    titles = soup.find_all( 'h3' )
    return [title.getText() for title in titles]

async def get_settings(group_id):
    settings = temp.SETTINGS.get(group_id)
    if not settings:
        settings = await db.get_settings(group_id)
        temp.SETTINGS[group_id] = settings
    return settings
    
async def save_group_settings(group_id, key, value):
    current = await get_settings(group_id)
    current[key] = value
    temp.SETTINGS[group_id] = current
    await db.update_settings(group_id, current)

def get_size(file_size):
    """converting file to GB // as per client reuirement 🚀"""
    gb_size = file_size / (1024 ** 3)  # Convert bytes to GB
    return "%.2fᴳᴮ" % gb_size  # Format the output with superscript GB

def get_size_mb_gb(size):
    """Get size in readable format"""
    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
    size = float(size)
    i = 0
    while size >= 1024.0 and i < len(units):
        i += 1
        size /= 1024.0
    return "%.2f %s" % (size, units[i])

def split_list(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]  

def get_file_id(msg: Message):
    if msg.media:
        for message_type in (
            "photo",
            "animation",
            "audio",
            "document",
            "video",
            "video_note",
            "voice",
            "sticker"
        ):
            obj = getattr(msg, message_type)
            if obj:
                setattr(obj, "message_type", message_type)
                return obj

def extract_user(message: Message) -> Union[int, str]:
    """extracts the user from a message"""
    # https://github.com/SpEcHiDe/PyroGramBot/blob/f30e2cca12002121bad1982f68cd0ff9814ce027/pyrobot/helper_functions/extract_user.py#L7
    user_id = None
    user_first_name = None
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        user_first_name = message.reply_to_message.from_user.first_name

    elif len(message.command) > 1:
        if (
            len(message.entities) > 1 and
            message.entities[1].type == enums.MessageEntityType.TEXT_MENTION
        ):
           
            required_entity = message.entities[1]
            user_id = required_entity.user.id
            user_first_name = required_entity.user.first_name
        else:
            user_id = message.command[1]
            # don't want to make a request -_-
            user_first_name = user_id
        try:
            user_id = int(user_id)
        except ValueError:
            pass
    else:
        user_id = message.from_user.id
        user_first_name = message.from_user.first_name
    return (user_id, user_first_name)

def list_to_str(k):
    if not k:
        return "N/A"
    elif len(k) == 1:
        return str(k[0])
    elif MAX_LIST_ELM:
        k = k[:int(MAX_LIST_ELM)]
        return ' '.join(f'{elem}, ' for elem in k)
    else:
        return ' '.join(f'{elem}, ' for elem in k)

def last_online(from_user):
    time = ""
    if from_user.is_bot:
        time += "🤖 Bot :("
    elif from_user.status == enums.UserStatus.RECENTLY:
        time += "Recently"
    elif from_user.status == enums.UserStatus.LAST_WEEK:
        time += "Within the last week"
    elif from_user.status == enums.UserStatus.LAST_MONTH:
        time += "Within the last month"
    elif from_user.status == enums.UserStatus.LONG_AGO:
        time += "A long time ago :("
    elif from_user.status == enums.UserStatus.ONLINE:
        time += "Currently Online"
    elif from_user.status == enums.UserStatus.OFFLINE:
        time += from_user.last_online_date.strftime("%a, %d %b %Y, %H:%M:%S")
    return time


def split_quotes(text: str) -> List:
    if not any(text.startswith(char) for char in START_CHAR):
        return text.split(None, 1)
    counter = 1  # ignore first char -> is some kind of quote
    while counter < len(text):
        if text[counter] == "\\":
            counter += 1
        elif text[counter] == text[0] or (text[0] == SMART_OPEN and text[counter] == SMART_CLOSE):
            break
        counter += 1
    else:
        return text.split(None, 1)

    # 1 to avoid starting quote, and counter is exclusive so avoids ending
    key = remove_escapes(text[1:counter].strip())
    # index will be in range, or `else` would have been executed and returned
    rest = text[counter + 1:].strip()
    if not key:
        key = text[0] + text[0]
    return list(filter(None, [key, rest]))

def parser(text, keyword):
    if "buttonalert" in text:
        text = (text.replace("\n", "\\n").replace("\t", "\\t"))
    buttons = []
    note_data = ""
    prev = 0
    i = 0
    alerts = []
    for match in BTN_URL_REGEX.finditer(text):
        # Check if btnurl is escaped
        n_escapes = 0
        to_check = match.start(1) - 1
        while to_check > 0 and text[to_check] == "\\":
            n_escapes += 1
            to_check -= 1

        # if even, not escaped -> create button
        if n_escapes % 2 == 0:
            note_data += text[prev:match.start(1)]
            prev = match.end(1)
            if match.group(3) == "buttonalert":
                # create a thruple with button label, url, and newline status
                if bool(match.group(5)) and buttons:
                    buttons[-1].append(InlineKeyboardButton(
                        text=match.group(2),
                        callback_data=f"alertmessage:{i}:{keyword}"
                    ))
                else:
                    buttons.append([InlineKeyboardButton(
                        text=match.group(2),
                        callback_data=f"alertmessage:{i}:{keyword}"
                    )])
                i += 1
                alerts.append(match.group(4))
            elif bool(match.group(5)) and buttons:
                buttons[-1].append(InlineKeyboardButton(
                    text=match.group(2),
                    url=match.group(4).replace(" ", "")
                ))
            else:
                buttons.append([InlineKeyboardButton(
                    text=match.group(2),
                    url=match.group(4).replace(" ", "")
                )])

        else:
            note_data += text[prev:to_check]
            prev = match.start(1) - 1
    else:
        note_data += text[prev:]

    try:
        return note_data, buttons, alerts
    except:
        return note_data, buttons, None

def remove_escapes(text: str) -> str:
    res = ""
    is_escaped = False
    for counter in range(len(text)):
        if is_escaped:
            res += text[counter]
            is_escaped = False
        elif text[counter] == "\\":
            is_escaped = True
        else:
            res += text[counter]
    return res

async def get_seconds(time_string):
    def extract_value_and_unit(ts):
        value = ""
        unit = ""

        index = 0
        while index < len(ts) and ts[index].isdigit():
            value += ts[index]
            index += 1

        unit = ts[index:].lstrip()

        if value:
            value = int(value)

        return value, unit

    value, unit = extract_value_and_unit(time_string)

    if unit == 's':
        return value
    elif unit == 'min':
        return value * 60
    elif unit == 'hour':
        return value * 3600
    elif unit == 'day':
        return value * 86400
    elif unit == 'month':
        return value * 86400 * 30
    elif unit == 'year':
        return value * 86400 * 365
    else:
        return 0

def humanbytes(size):
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'Ki', 2: 'Mi', 3: 'Gi', 4: 'Ti'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'

import base64

async def get_shortlink(chat_id, link):
    original_url = link  # URL from the request
    if not original_url:
        return "Error: URL not provided!", 400
    # Encode URL into Base64
    DOMAIN = URL
    encoded_url = base64.urlsafe_b64encode(original_url.encode()).decode()
    short_url = f"{DOMAIN}getfile/{encoded_url}"
    # print(f"This is encoded url ==>{short_url}")
    return short_url
   
def get_readable_time(seconds: int) -> str:
    count = 0
    readable_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", " days"]
    while count < 4:
        count += 1
        if count < 3:
            remainder, result = divmod(seconds, 60)
        else:
            remainder, result = divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)
    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        readable_time += time_list.pop() + ", "
    time_list.reverse()
    readable_time += ": ".join(time_list)
    return readable_time 

async def get_tutorial(chat_id):
    settings = await get_settings(chat_id) #fetching settings for group
    if 'tutorial' in settings.keys():
        if settings['is_tutorial']:
            TUTORIAL_URL = settings['tutorial']
        else:
            TUTORIAL_URL = TUTORIAL
    else:
        TUTORIAL_URL = TUTORIAL
    return TUTORIAL_URL

# check verification // methods

#1 => verification_steps ! [Youtube@LazyDeveloperr] - 
async def extract_verified_short_link(link):
    API = LAZY_SHORTNER_API if LAZY_SHORTNER_API else URL_SHORTNER_WEBSITE_API
    URL = LAZY_SHORTNER_URL if LAZY_SHORTNER_URL else URL_SHORTENR_WEBSITE
    https = link.split(":")[0]
    if "http" == https:
        https = "https"
        link = link.replace("http", https)

    if URL == "api.shareus.in":
        url = f"https://{URL}/shortLink"
        params = {"token": API,
                  "format": "json",
                  "link": link,
                  }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, raise_for_status=True, ssl=False) as response:
                    data = await response.json(content_type="text/html")
                    if data["status"] == "success":
                        return data["shortlink"]
                    else:
                        logger.error(f"Error: {data['message']}")
                        return f'https://{URL}/shortLink?token={API}&format=json&link={link}'

        except Exception as e:
            logger.error(e)
            return f'https://{URL}/shortLink?token={API}&format=json&link={link}'
    else:
        url = f'https://{URL}/api'
        params = {'api': API,
                  'url': link,
                  }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, raise_for_status=True, ssl=False) as response:
                    data = await response.json()
                    if data["status"] == "success":
                        return data['shortenedUrl']
                    else:
                        logger.error(f"Error: {data['message']}")
                        return f'https://{URL}/api?api={API}&link={link}'

        except Exception as e:
            logger.error(e)
            print(e)
            return f'{URL}/api?api={API}&link={link}'

async def check_token(bot, userid, token):
    user = await bot.get_users(userid)
    if not await db.is_user_exist(user.id):
        await db.add_user(user.id, user.first_name)
        await bot.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(user.id, user.mention))
    if user.id in TOKENS.keys():
        TKN = TOKENS[user.id]
        if token in TKN.keys():
            is_used = TKN[token]
            if is_used == True:
                return False
            else:
                return True
    else:
        return False

async def get_token(bot, userid, link):
    user = await bot.get_users(userid)
    if not await db.is_user_exist(user.id):
        await db.add_user(user.id, user.first_name)
        await bot.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(user.id, user.mention))
    token = ''.join(random.choices(string.ascii_letters + string.digits, k=7))
    TOKENS[user.id] = {token: False}
    link = f"{link}verify-{user.id}-{token}"
    print(link)
    final_verified_lazy_link = await get_shortlink(user.id, link)
    return str(final_verified_lazy_link)

from datetime import datetime, timedelta
async def verify_user(bot, userid, token):
    user = await bot.get_users(userid)
    if not await db.is_user_exist(user.id):
        await db.add_user(user.id, user.first_name)
        await bot.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(user.id, user.mention))
    TOKENS[user.id] = {token: True}
    timezone = pytz.timezone("Asia/Kolkata")
    expiry_time = datetime.now(timezone) + timedelta(hours=MAX_SUBSCRIPTION_TIME)  # 24 hours from now
    expiry_str = expiry_time.strftime("%Y-%m-%d %H:%M:%S")  # Format as YYYY-MM-DD HH:MM:SS

    xx = await db.update_user({"id": user.id, "subscription": "limited", "subscription_expiry": expiry_str})
    print(xx)
    
async def check_verification(bot, userid):
    user = await bot.get_users(userid)
    if not await db.is_user_exist(user.id):
        await db.add_user(user.id, user.first_name)
        await bot.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(user.id, user.mention))
    tz = pytz.timezone('Asia/Kolkata')
    today = date.today()
    if user.id in VERIFIED.keys():
        EXP = VERIFIED[user.id]
        years, month, day = EXP.split('-')
        comp = date(int(years), int(month), int(day))
        if comp<today:
            return False
        else:
            return True
    else:
        return False

# Credit @LazyDeveloper.
# Please Don't remove credit.
# Born to make history @LazyDeveloper !
# Thank you LazyDeveloper for helping us in this Journey
# 🥰  Thank you for giving me credit @LazyDeveloperr  🥰
# for any error please contact me -> telegram@LazyDeveloperr or insta @LazyDeveloperr 
# rip paid developers 🤣 - >> No need to buy paid source code while @LazyDeveloperr is here 😍😍
