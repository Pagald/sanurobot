
import asyncio
import re
import ast
import math
import pytz
import random
from urllib.parse import quote
from datetime import datetime, time
lock = asyncio.Lock()
from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from Script import script
from database.connections_mdb import active_connection, all_connections, delete_connection, if_active, make_active, \
    make_inactive
from info import *
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ForceReply, Message
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid
from urllib.parse import quote_plus
from util.file_properties import get_name, get_hash
from utils import get_size,lazy_readable,lazy_has_subscribed, to_small_caps,get_poster,get_popular_movies, get_lazy_goat_movies, get_lazy_trending_movies, temp,imdb, get_settings, save_group_settings
from database.users_chats_db import db
from database.ia_filterdb import Media, get_file_details,get_search_results_badAss_LazyDeveloperr
from database.lazy_utils import progress_for_pyrogram, convert
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
import os 
from Script import script
import humanize
from PIL import Image
import time
from fuzzywuzzy import process
from plugins.commands import lazybarier
from database.filters_mdb import (
    del_all,
    find_filter,
    get_filters,
)
import uuid 
import logging
logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
from pyrogram.errors import PeerIdInvalid
from collections import defaultdict
from plugins.commands import send_lazy_video
LAZYS_FILE_ID = "CAACAgUAAxkBAAEQ2YpljSvD5sq-Flkm9TV8afTGo7Kr4gACgwMAAjO28FeYSaGKzSOuUTME CAACAgIAAxkBAAEQ2ppljXqrYNVEN_hsFrm72H_tJvwZEQACdgUAAj-VzApFV7w2VozN3TME CAACAgIAAxkBAAEQ2pxljXr88eSrY-fNSv8tWqTsKQXSTwACWgUAAj-VzAobFrmFvSDDnTME CAACAgUAAxkBAAEQ2p5ljXsOArpCEAIuyF_X-cjbcq8y9wACUQMAAn4--FdPtUqUKQy6njME CAACAgUAAxkBAAEQ2qJljXtSW5xxVc0xk6J4dx1TIcReXQACOggAAibGUFalOk-a8Gmc2TME CAACAgIAAxkBAAEQ2qZljXt7emeVhLmGav1fiCUbTVKK6AACyRIAAmA0gEtb-P-xaa3sxjME CAACAgIAAxkBAAEQ2qhljXuRfi61G-Th8T9R7AIO_E-GFQACgBgAAsC2UEmimzNNrlDPPDME CAACAgIAAxkBAAEQ2qpljXuwpjQsCWqkR190gR6vSLrjpgAC7hQAAuNVUEk4S4qtAhNhvDME CAACAgIAAxkBAAEQ2qxljXvF9LzAOBwWqqGxYghZBptPFwACXgUAAj-VzAqq1ncTLO-MOTME CAACAgUAAxkBAAEQ2q5ljXvfjuP7GSEGy5LOIubDdZD24wACdAQAAg0N-VchhV4I8_I1XjME CAACAgUAAxkBAAEQ2rBljXvzM7MpUVZcpRkiYGPiG89UJgACeAMAAqZh-FfxCTpwVzCOEzME CAACAgUAAxkBAAEQ2rJljXwNvgcYFau24iQ57pNx72IbyAACdQQAAmh1-Ffusjt1plc9YzME CAACAgUAAxkBAAEQ2rRljXwhXX-JMs8GFzz2QZRxdUk9lAADBAACXtDwV04PGDy02iQAATME CAACAgUAAxkBAAEQ2rZljXwsAAEr4nU50WP3Hz_0HCxmYSwAAuwDAAISQflXYznjU3iGTvkzBA CAACAgIAAxkBAAEQ2rhljXxPS3Qd-BV9RnA_0OwPiKsSCQACdwUAAj-VzApljNMsSkHZTjME CAACAgIAAxkBAAEQ2rxljXxsaNqc3gMhzW7FovMiXOvYnQAC-hMAAtSF8Etb7jRObi-mqzME CAACAgUAAxkBAAEQ2sBljXzQxfyPIRI4ch3cHPk-rsCzpQACowkAAonICFTwfKVoynUZvzME CAACAgUAAxkBAAEQ2sJljXzqbHl83Fv7n3m0HfNHBrho4QACCwoAAi7EUVfwywxU4Qq7_jME CAACAgUAAxkBAAEQ2sRljXz-3uxQIFRstS3R5W-y0dC5qgAC5QUAAruXSFaWNURJP7tfwjME CAACAgQAAxkBAAEQ2sZljX0jh3vLtJpWZcxxj5bay9t-ZAACKxAAAk1zwFPGlaV1QZjTkTME CAACAgUAAxkBAAEQ23pljX7l5QqJeF5D5N3HZzH11wKW-AAC_QMAAhOM-FfHw6MTc_AX9TME CAACAgUAAxkBAAEQ23hljX7ivAeA9bzizIEtO1zLWdR3cgACQQQAAu-M8FelaJ5dHSa2IjME CAACAgUAAxkBAAEQ23ZljX7g-mO-JJ_zXANWQP_Iu0XSdwADBAACXtDwV04PGDy02iQAATME CAACAgUAAxkBAAEQ23RljX7d5-rssmw93XU3X7DFQ2eQnAACAQQAAjcM8Vc5TYjCrZcv9jME CAACAgIAAxkBAAEQ23BljX7TxvX88ZWgmaCtC69e8oRFtwACyxQAAt2wUUlMYGw0MqQdYTME CAACAgIAAxkBAAEQ225ljX7SHE230w8XkqVhWGnCZCaEywACmxgAApd_GUmWaHhj5QhlhDME CAACAgIAAxkBAAEQ22xljX7NXu_n0gWTgdJbO2WV6LqwCQACFBUAAuCUyEl75qEC_trvQjME CAACAgIAAxkBAAEQ22pljX7LVSnENXQzGww9r62wOqSj8QACYRQAArT6gEs6giPSo52pzjME CAACAgIAAxkBAAEQ22hljX7FZhbAOn2M_Jv_b4_Ekfu4fQACMBMAAuMikUvBPXzxtKbSdTME CAACAgUAAxkBAAEQ22ZljX7BfFC_nYdWmtu05FPnFPnwsAACoQYAAqReUFYvH5-81YCd2TME CAACAgIAAxkBAAEQ22RljX6qPHWpw3uMFsRZThYk7ed1VAACNAADpsrIDFFqS0RzOZ6RMwQ CAACAgIAAxkBAAEQ22JljX6oYwU5DK4iqQOhHKPIJmdItAACNwADpsrIDAe-9Dzoj1lFMwQ CAACAgIAAxkBAAEQ22BljX6mqfCiiq4lkzCy5arscT9chQACMAADpsrIDN5j5wS_ajpFMwQ CAACAgIAAxkBAAEQ215ljX6lCDcQW-CdfWoP82uwvJ-d5gACPQADpsrIDG9X2CRSFUdMMwQ CAACAgIAAxkBAAEQ21xljX6hzov-plccFYwdhZLjCtERtwACYgMAArrAlQUGVK1U7t1DvjME CAACAgIAAxkBAAEQ21pljX6g7JtkVQgJPRZvUuHEeESzFAACYQMAArrAlQWtCQpcpHMj6zME CAACAgIAAxkBAAEQ21hljX6e4T2BXINz9aHC6bbOhN98-AACXwMAArrAlQV3VCzBKTQhzTME CAACAgIAAxkBAAEQ21ZljX6dOiFyPo25z-k3TemJM-AW0AACZAMAArrAlQUCMw3LNvhMBzME CAACAgIAAxkBAAEQ21RljX6aUwXFnLOUckJO6pPsJY7eJQACYwMAArrAlQXFRT6GJ_YYjDME CAACAgIAAxkBAAEQ21JljX6WcSoazCBpf-lSi_JWkRTJcQACXgMAArrAlQVceSrBWv5H7DME CAACAgIAAxkBAAEQ21BljX6TIJxdnk3g2pW4w92UCdGffgACaAMAArrAlQX1qKrummjK4jME CAACAgIAAxkBAAEQ205ljX6Q0uBqgIDVDsUvCNotXNVUxgACVwMAArrAlQVMHrV9flRvYDME CAACAgIAAxkBAAEQ20xljX6PRN-zZQoa_qKWSRtIr-faagACUQMAArrAlQV7yJzLJQ11NTME CAACAgIAAxkBAAEQ20pljX6LO0vO5MGfXTr5raW8awoMCgACZwMAArrAlQUYRInTOvVi5zME CAACAgUAAxkBAAEQ20hljX6CtrJGoRQbkhgunIrnnxmPtgACWAUAAj_q8FQzC8bJrK17oTME CAACAgUAAxkBAAEQ20ZljX56xaIj4yAYphK71XnLiv5piQACMgUAAiH_OFZUebKV2aRk4jME CAACAgUAAxkBAAEQ20JljX5ulp4Hs5GCtcwOoc5tQE5q7AACDgsAAqTleVRk8KSVmKztdTME CAACAgUAAxkBAAEQ20BljX5suhUDAvXCbRW66o_RVL-eLQAC0AUAAmKRSVbH3lZrdPrmzDME CAACAgUAAxkBAAEQ2z5ljX5rZp6rb2npKqJJUZjihq6nfgACEgYAAlHRSVZQOGffLaUQPDME CAACAgUAAxkBAAEQ2zxljX5pCWHmOGS5Kz7xWQFqQHiwIwACfQYAAihQOVXHMR0c722MljME CAACAgUAAxkBAAEQ2zpljX5nMXdpa64FlfpCt55M13RkTQACAgcAAqnwQVUZPTpNSHHYyzME CAACAgUAAxkBAAEQ2zhljX5lvTqj_GdHD0mjE8Gm_yoNuQACkwYAAnSE4FR1rf6moEtC3jME CAACAgQAAxkBAAEQ2zZljX5e9FXfOHq-pfQ--JC1E6f9NAACwgwAApu9YFOto4bf2PBvjjME CAACAgQAAxkBAAEQ2zRljX5c0OUYHcAWTjQsOVviMVVwqAACOxAAArb8IFC1KxiPG8NRXTME CAACAgQAAxkBAAEQ2zJljX5Yvtmjilx1LyeaH_9aFvRabQAClg4AAgpU4FPdiPEnNU-eAzME CAACAgQAAxkBAAEQ2zBljX5VlUhlERMNYflfQ_TFofjlcAAC5gsAAk8cWVNQLKJXQdhgTjME CAACAgUAAxkBAAEQ2y5ljX5HRQ7tY6cNxh1UDp1bek0uSAACRgUAAsVy2VfQ727ilW4Q0TME CAACAgIAAxkBAAEQ2yxljX5BdWIW00GJ7VfNNH84yKol_AACuAwAAu4J0Uju07GbH7xLtjME CAACAgIAAxkBAAEQ2ypljX4_ef4Gvip3zLn9S46-fThs8QACjw8AAnUuOUhbsCYf9OCDLzME CAACAgIAAxkBAAEQ2yhljX4-F93VJ9SI5Nqrw7hkgAuBYAACrA4AApttOUg2JQmaMDgs5DME CAACAgIAAxkBAAEQ2yZljX49k54WbfWZrWrz-XsOn-RLaQACmgsAArKo0EgS53Dn4tBGxjME CAACAgIAAxkBAAEQ2yRljX47vGql9dU1anPD8Gtr21GdDQACxAsAAotw0UgnQqg-jzV7MDME CAACAgIAAxkBAAEQ2yJljX45vhWNHZaM9cz_3A2hTdUcqgACYgwAAoRLUUneeFbkxCAnAzME CAACAgIAAxkBAAEQ2yBljX43ddBRisbLWhf3XCbfq-I6tQACHQ0AAh770Egx8DhQz29keTME CAACAgUAAxkBAAEQ2x5ljX4GJLG--Tdif5GXum4ySAPSUgACPAcAAvRbsVY-RudjcCNnRzME CAACAgUAAxkBAAEQ2xxljX4EJ1zBF-RDDI8Bw9C8TgU-dgACagcAAtOjsVaqe68IYcN1YjME CAACAgUAAxkBAAEQ2xpljX3_JsNCovrCShBKl-XwTMB1WQAC1ggAAtbKwVaoIpJ458lrbzME CAACAgUAAxkBAAEQ2xhljX3-rpUSr-Zysb5jM-UHdtflzwAC8wcAApZv8VZ2tD2uxVCppjME CAACAgUAAxkBAAEQ2xZljX38lCLPiGavo7umPSqqMY37VAACHAgAAsjxwFbq9aiknIndhjME CAACAgUAAxkBAAEQ2xRljX36Xdiuk8Pj_V1alIcWxpstPQAC9gcAAoOYwFbpOHyXHUEwojME CAACAgIAAxkBAAEQ2xJljX3uGw7RTdNeT1kcKleZdN9iWwACAQADwDZPExguczCrPy1RMwQ CAACAgIAAxkBAAEQ2xBljX3teYnVU4XRYcJbFUm29hgmxQACCQADwDZPE-_NG6JK_3GVMwQ CAACAgIAAxkBAAEQ2w5ljX3pISsLZHZG9AGeNJLzMkpgewACBQADwDZPE_lqX5qCa011MwQ CAACAgIAAxkBAAEQ2wxljX3f39-jvHcMId63H9DYQ9mmfwACHgADwDZPE6FgWy2rAAHeBDME CAACAgIAAxkBAAEQ2wpljX3YMNw4lagYeQyyrsm512RZ6gACCgADwDZPE_8Nrj7oDv0IMwQ CAACAgIAAxkBAAEQ2wABZY190jAxdLz3PpozCPddAyED4l4AAhMAA8A2TxOqs4f3fzjKpTME CAACAgIAAxkBAAEQ2v5ljX3RtHBG3Y5NgWNzhP8lCteK1QACAgADwDZPEwj1bkX6hKdZMwQ CAACAgUAAxkBAAEQ2vxljX3G0gxj5pR5rvF17IqbYOce0gACGBsAAhg7sVYEbqcxgVB0BzME CAACAgUAAxkBAAEQ2vpljX3FWN6o0BPvs6t1CsHPSlRY1AACdAoAAj1wsVagMcQaa7DpwDME CAACAgIAAxkBAAEQ2vhljX24IOhI5O_okxvJQLpEQu58DgACchIAAkblqUjyTBtFPtcDUTME CAACAgIAAxkBAAEQ2vZljX2zxFnUYPHtcIoHXkT3ARcV9gACXhIAAuyZKUl879mlR_dkOzME CAACAgIAAxkBAAEQ2vRljX2yJAv_Cu1ILriYIwllOTWzSgACchIAAkblqUjyTBtFPtcDUTME CAACAgIAAxkBAAEQ2vJljX2xNWg1gnxa6xYW4ceNAk7C0AACQhAAAjPFKUmQDtQRpypKgjME CAACAgIAAxkBAAEQ2vBljX2wDLfaSn8v0z5hRi5ygCFQ3gACdhEAAsMAASlJLbkjGWa6DogzBA CAACAgIAAxkBAAEQ2u5ljX2vwTtkxdzk9vx_7sLNQQysxAACvAwAAocoMEntN5GZWCFoBDME CAACAgIAAxkBAAEQ2uxljX2uWkQ0WZuEYqv-ERLKCAgZHgACoxAAAvF3qEh-OxgSw5fVQTME CAACAgIAAxkBAAEQ2upljX2s4GgknJbdiydP1onraOVl0AACaBEAAoWPKEnJ3C01n5I86TME CAACAgIAAxkBAAEQ2uhljX2rpDsEjlPjyvqtgI9HUka2zQACtA4AAnrnsEhInMQI4qVJTzME CAACAgIAAxkBAAEQ2uZljX2qUv5ReJO76qrQs6uuI_w8YAACkBAAAmteqEgcGk7MnoBFmDME CAACAgIAAxkBAAEQ2uRljX2kr05pfviYamDRHv1sV1QBhAACYgwAAoRLUUneeFbkxCAnAzME CAACAgIAAxkBAAEQ2uJljX2hc3ay1OVdOqbAOZSATyPewQACTwsAAiIPqEiffAABWBhYw3gzBA CAACAgIAAxkBAAEQ2uBljX2fD73IIJCnHUhV3C0j3snJ1QACVgwAAtIc2EgGpDcOv3z8XjME CAACAgUAAxkBAAEQ2t5ljX2WDFSnD_cwS5X294G-UrGqUgACxQUAAtKzoFTAWloi3EjAeTME CAACAgUAAxkBAAEQ2txljX2VCFKoA1IkjeNvj3Nq6onA-QACYAQAAioMGFT31AZIdDgfzDME CAACAgUAAxkBAAEQ2tpljX2SoNNnbgE8TH85w2e9wY_aRgACHAsAAjTXKVWSm3iPcbpSVjME CAACAgUAAxkBAAEQ2thljX2RYxSAq_Cayr9ljiDKv6HWZQACHwUAAwYhVsBmt0GBA78hMwQ CAACAgUAAxkBAAEQ2tZljX2OEKazpqSC2yGcvCG9pm882QACzQoAAiDn2VUKLZEKuLBP0DME CAACAgUAAxkBAAEQ2tRljX2L9UzJcL5Ou7F153lNhLaKpgACLwUAAnQ78VeOB3PdfvLh9jME CAACAgUAAxkBAAEQ2tJljX2HCqUHsmfhIrLfI9dc8JwIPQACxQQAAmtnGFRD00nwm6LHDjME CAACAgIAAxkBAAEQ2tBljX1oTRpo7Mu2N_qQSSDUYdHgBwACTwsAAiIPqEiffAABWBhYw3gzBA CAACAgIAAxkBAAEQ2s5ljX1lpq2nIeSMh2ABs7GMWArFvAACagsAArVLqEgy_6fKZOLx5jME CAACAgIAAxkBAAEQ2sxljX1kbYfwmVO0OegtwdAjEN6CGgACrQwAAvGUQUihcDy_-h_T6TME CAACAgIAAxkBAAEQ2spljX1hLlkVpoHdI4SJT7h1_LFTVAACJAwAAviQOEiWAywHzwABlxgzBA CAACAgQAAxkBAAEQ2sZljX0jh3vLtJpWZcxxj5bay9t-ZAACKxAAAk1zwFPGlaV1QZjTkTME CAACAgUAAxkBAAEQ2sRljXz-3uxQIFRstS3R5W-y0dC5qgAC5QUAAruXSFaWNURJP7tfwjME CAACAgUAAxkBAAEQ2sJljXzqbHl83Fv7n3m0HfNHBrho4QACCwoAAi7EUVfwywxU4Qq7_jME CAACAgUAAxkBAAEQ2sBljXzQxfyPIRI4ch3cHPk-rsCzpQACowkAAonICFTwfKVoynUZvzME CAACAgIAAxkBAAEQ2rxljXxsaNqc3gMhzW7FovMiXOvYnQAC-hMAAtSF8Etb7jRObi-mqzME CAACAgUAAxkBAAEQ2sJljXzqbHl83Fv7n3m0HfNHBrho4QACCwoAAi7EUVfwywxU4Qq7_jME CAACAgUAAxkBAAEQ2sBljXzQxfyPIRI4ch3cHPk-rsCzpQACowkAAonICFTwfKVoynUZvzME CAACAgIAAxkBAAEQ2rxljXxsaNqc3gMhzW7FovMiXOvYnQAC-hMAAtSF8Etb7jRObi-mqzME CAACAgIAAxkBAAEQ2rpljXxg0p_h1RoD1tBlVOvwFc-SzwAC_RMAAqrbgEuv3ujuB8gacDME CAACAgIAAxkBAAEQ2rhljXxPS3Qd-BV9RnA_0OwPiKsSCQACdwUAAj-VzApljNMsSkHZTjME CAACAgUAAxkBAAEQ2rZljXwsAAEr4nU50WP3Hz_0HCxmYSwAAuwDAAISQflXYznjU3iGTvkzBA CAACAgUAAxkBAAEQ2rRljXwhXX-JMs8GFzz2QZRxdUk9lAADBAACXtDwV04PGDy02iQAATME CAACAgUAAxkBAAEQ2rJljXwNvgcYFau24iQ57pNx72IbyAACdQQAAmh1-Ffusjt1plc9YzME CAACAgUAAxkBAAEQ2q5ljXvfjuP7GSEGy5LOIubDdZD24wACdAQAAg0N-VchhV4I8_I1XjME CAACAgIAAxkBAAEQ2qxljXvF9LzAOBwWqqGxYghZBptPFwACXgUAAj-VzAqq1ncTLO-MOTME CAACAgIAAxkBAAEQ2qpljXuwpjQsCWqkR190gR6vSLrjpgAC7hQAAuNVUEk4S4qtAhNhvDME CAACAgIAAxkBAAEQ2qhljXuRfi61G-Th8T9R7AIO_E-GFQACgBgAAsC2UEmimzNNrlDPPDME CAACAgIAAxkBAAEQ2qZljXt7emeVhLmGav1fiCUbTVKK6AACyRIAAmA0gEtb-P-xaa3sxjME CAACAgUAAxkBAAEQ2qRljXtnTHB4pmFFoKUQHw7JupE7-wACpwUAAuW4WFaFOaIX4LMhuDME CAACAgUAAxkBAAEQ2p5ljXsOArpCEAIuyF_X-cjbcq8y9wACUQMAAn4--FdPtUqUKQy6njME CAACAgIAAxkBAAEQ2pxljXr88eSrY-fNSv8tWqTsKQXSTwACWgUAAj-VzAobFrmFvSDDnTME CAACAgIAAxkBAAEQ2ppljXqrYNVEN_hsFrm72H_tJvwZEQACdgUAAj-VzApFV7w2VozN3TME CAACAgUAAxkBAAEQ2YpljSvD5sq-Flkm9TV8afTGo7Kr4gACgwMAAjO28FeYSaGKzSOuUTME"
lazystickerset = LAZYS_FILE_ID.split()

req_channel = REQ_CHANNEL
BUTTONS = {}
SPELL_CHECK = {}
# 
BUTTON0 = {}
BUTTON = {}
FRESH = {}
BUTTONS0 = {}
BUTTONS1 = {}
BUTTONS2 = {}
POPDISK = {}
TOPDISK = {}



# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@Client.on_message((filters.group | filters.private) & filters.text & filters.incoming)
async def give_filter(client, message):
    try:
        if message.chat.type == enums.ChatType.PRIVATE:
            if not await db.get_pm_search_status():
                return
        await auto_filter(client, message)
    except Exception as e:
        logging.info(f"ERROR: {e}")

@Client.on_callback_query(filters.regex('rename'))
async def rename(bot,update):
	user_id = update.message.chat.id
	date = update.message.date
	await update.message.delete()
	await update.message.reply_text("<i><b>»» Please enter new file name...</b></i>",	
	reply_to_message_id=update.message.reply_to_message.id,  
	reply_markup=ForceReply(True))  

# Born to make history @LazyDeveloper !
@Client.on_callback_query(filters.regex("upload"))
async def doc(bot, update):
    try:
        type = update.data.split("_")[1]
        new_name = update.message.text
        new_filename = new_name.split(":-")[1]
        file = update.message.reply_to_message
        file_path = f"downloads/{new_filename}"
        ms = await update.message.edit("\n༻☬ད 𝘽𝙪𝙞𝙡𝙙𝙞𝙣𝙜 𝙇𝙖𝙯𝙮 𝙈𝙚𝙩𝙖𝘿𝙖𝙩𝙖...")
        c_time = time.time()
        try:
            path = await bot.download_media(
                    message=file,
                    progress=progress_for_pyrogram,
                    progress_args=("**\n  ღ♡ ꜰɪʟᴇ ᴜɴᴅᴇʀ ᴄᴏɴꜱᴛʀᴜᴄᴛɪᴏɴ... ♡♪**", ms, c_time))
        except Exception as e:
            await ms.edit(e)
            return 
        splitpath = path.split("/downloads/")
        dow_file_name = splitpath[1]
        old_file_name =f"downloads/{dow_file_name}"
        os.rename(old_file_name, file_path)
        duration = 0
        try:
            metadata = extractMetadata(createParser(file_path))
            if metadata.has("duration"):
               duration = metadata.get('duration').seconds
        except:
            pass
        user_id = int(update.message.chat.id) 
        ph_path = None 
        media = getattr(file, file.media.value)
        filesize = humanize.naturalsize(media.file_size) 
        c_caption = await db.get_caption(update.message.chat.id)
        c_thumb = await db.get_thumbnail(update.message.chat.id)
        if c_caption:
             try:
                 caption = c_caption.format(filename=new_filename, filesize=humanize.naturalsize(media.file_size), duration=convert(duration))
             except Exception as e:
                 await ms.edit(text=f"Your caption Error unexpected keyword ●> ({e})")
                 return 
        else:
            caption = f"**{new_filename}** \n\n⚡️Data costs: `{filesize}`"
        if (media.thumbs or c_thumb):
            if c_thumb:
               ph_path = await bot.download_media(c_thumb) 
            else:
               ph_path = await bot.download_media(media.thumbs[0].file_id)
            Image.open(ph_path).convert("RGB").save(ph_path)
            img = Image.open(ph_path)
            img.resize((320, 320))
            img.save(ph_path, "JPEG")
        await ms.edit("三 𝘗𝘳𝘦𝘱𝘢𝘳𝘪𝘯𝘨 𝘵𝘰 𝘳𝘦𝘤𝘦𝘪𝘷𝘦 𝘓𝘢𝘻𝘺 𝘧𝘪𝘭𝘦...︻デ═一")
        c_time = time.time() 
        try:
           if type == "document":
              await bot.send_document(
	            update.message.chat.id,
                       document=file_path,
                       thumb=ph_path, 
                       caption=caption, 
                       progress=progress_for_pyrogram,
                       progress_args=( "**⎝⎝✧ ʀᴇᴄɪᴇᴠɪɴɢ ꜰɪʟᴇ ꜰʀᴏᴍ ʟᴀᴢʏ ꜱᴇʀᴠᴇʀ ✧⎠⎠**",  ms, c_time))
           elif type == "video": 
               await bot.send_video(
	            update.message.chat.id,
	            video=file_path,
	            caption=caption,
	            thumb=ph_path,
	            duration=duration,
	            progress=progress_for_pyrogram,
	            progress_args=( "**⎝⎝✧ ʀᴇᴄɪᴇᴠɪɴɢ ꜰɪʟᴇ ꜰʀᴏᴍ ʟᴀᴢʏ ꜱᴇʀᴠᴇʀ ✧⎠⎠**",  ms, c_time))
           elif type == "audio": 
               await bot.send_audio(
	            update.message.chat.id,
	            audio=file_path,
	            caption=caption,
	            thumb=ph_path,
	            duration=duration,
	            progress=progress_for_pyrogram,
	            progress_args=( "**⎝⎝✧ ʀᴇᴄɪᴇᴠɪɴɢ ꜰɪʟᴇ ꜰʀᴏᴍ ʟᴀᴢʏ ꜱᴇʀᴠᴇʀ ✧⎠⎠**",  ms, c_time   )) 
        except Exception as e: 
            await ms.edit(f" Erro {e}") 
            os.remove(file_path)
            if ph_path:
              os.remove(ph_path)
            return 
        await ms.delete() 
        os.remove(file_path) 
        if ph_path:
           os.remove(ph_path) 
    except Exception as e:
        logger.error(f"error 2 : {e}")

# Born to make history @LazyDeveloper !
@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot, query):
    try:
        if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
            msg1 = to_small_caps(f"♥ It's {query.message.reply_to_message.from_user.first_name}'s files. ♥")
            msg2 = to_small_caps(f"🚩 Please search your own. 📺")
            return await query.answer(
                f"{msg1}\n\n{msg2}",
                show_alert=True,
            )
    except Exception:
        pass
    # 
    ident, req, key, offset = query.data.split("_")
    try:
        offset = int(offset)
    except:
        offset = 0

    if BUTTONS.get(key)!=None:
        search = BUTTONS.get(key)
    else:
        search = FRESH.get(key)
    
    chat_id = query.message.chat.id
    lazy_id = query.message.reply_to_message.id
    lazyuser_id = query.from_user.id
    if not search:
        await query.answer("⚠ Query violation detected! Please send the request again with proper movie name.", show_alert=True)
        return

    files, n_offset, total = await get_search_results_badAss_LazyDeveloperr(chat_id, lazy_id, search, offset=offset, filter=True)
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0

    if not files:
        return
    temp.GETALL[key] = files
    temp.SHORT[query.from_user.id] = query.message.chat.id
    settings = await get_settings(query.message.chat.id)
    pre = 'filep' if settings['file_secure'] else 'file'
    
    try:
        if temp.SHORT.get(lazyuser_id)==None:
            return await query.reply_text(text="<b>Please Search Again in Group</b>")
        else:
            chat_id = temp.SHORT.get(lazyuser_id)
    except Exception as e:
        logging.info(e)
    if settings['button']:    
        btn = [
            [
                InlineKeyboardButton(
                    text=f"{get_size(file.file_size)} | {file.file_name}", callback_data=f'{pre}#{file.file_id}'
                ),
            ]
            for file in files
        ]

    else:
        btn = [
                [
                    InlineKeyboardButton(text=f"{file.file_name}",callback_data=f'{pre}#{file.file_id}',),
                    InlineKeyboardButton(text=f"{get_size(file.file_size)}",callback_data=f'{pre}#{file.file_id}',),
                ]
                for file in files
                ]
        
    btn.insert(0, [
        InlineKeyboardButton(f"🎖 {to_small_caps('LATEST MOVIE UPLOADED')}🎖", url=f"https://t.me/+rYEsBW04zHY0MDg1")
    ])
    # btn.insert(0, [
    #     InlineKeyboardButton(f"𓆩ཫ🔻 {to_small_caps('Select Season')} 🔻ཀ𓆪", callback_data=f"seasons#{key}")
    # ])
    # btn.insert(0, 
    #     [
    #         InlineKeyboardButton(f'𓆩ཫ⭕• ǫᴜᴀʟɪᴛʏ', callback_data=f"qualities#{key}"),
    #         InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇ •⭕ཀ𓆪", callback_data=f"languages#{key}"),
    #     ])
    # # btn.insert(0, [
    # #         InlineKeyboardButton("♨️ ꜱᴇɴᴅ ᴀʟʟ ꜰɪʟᴇꜱ ♨️", callback_data=f"sendfiles#{key}")
    # #     ])
    # btn.insert(0,
    #         [ 
    #         InlineKeyboardButton(text="🚀Trending", callback_data=f"trending#lazytrends#{key}"),
    #         InlineKeyboardButton(text="♥ᴘᴏᴘᴜʟᴀʀ", callback_data=f"popular#lazyshort#{key}"),
    #         # InlineKeyboardButton(text="# ʀᴇQᴜᴇsᴛ", url=f'https://t.me/{temp.U_NAME}?start=requestmovie'),
    #         ])
    # # btn.insert(0,
    # #     [ 
	# #     InlineKeyboardButton(text="⚡ ʜᴏᴡ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ⚡", url='https://telegram.me/+lI9zStHfHlllNjQ1'),
    # #     ] 
    # # )
    if 0 < offset <= 10:
        off_set = 0
    elif offset == 0:
        off_set = None
    else:
        off_set = offset - 10
    if n_offset == 0:
        btn.append(
            [InlineKeyboardButton(f"{BACK_BTN_TXT}", callback_data=f"next_{req}_{key}_{off_set}"),
             InlineKeyboardButton(f"📃 Pages {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}",
                                  callback_data="pages")]
        )
    elif off_set is None:
        btn.append(
            [InlineKeyboardButton(f"🗓 {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}", callback_data="pages"),
             InlineKeyboardButton(f"{NEXT_BTN_TXT}", callback_data=f"next_{req}_{key}_{n_offset}")])
    else:
        btn.append(
            [
                InlineKeyboardButton(f"{BACK_BTN_TXT}", callback_data=f"next_{req}_{key}_{off_set}"),
                InlineKeyboardButton(f"🗓 {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}", callback_data="pages"),
                InlineKeyboardButton(f"{NEXT_BTN_TXT}", callback_data=f"next_{req}_{key}_{n_offset}")
            ],
        )
    try:
        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(btn)
        )
    except FloodWait as lazydeveloper:
        # e.seconds is available in Pyrogram's FloodWait error.
        wait_time = lazydeveloper.value
        await query.answer(
            f"💔 Whoa, slow down, my love! You've been clicking too fast.\n\n"
            f"Please wait {wait_time} seconds before trying again.\n\n"
            f"Take a deep breath and come back soon ❤️",
            show_alert=True
        ) 
    except MessageNotModified:
        pass
    await query.answer()

# Born to make history @LazyDeveloper !
@Client.on_callback_query(filters.regex(r"^current#"))
async def currentpage_handler(client: Client, query: CallbackQuery):
    try:
        try:
            if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
                msg1 = to_small_caps(f"♥ It's {query.message.reply_to_message.from_user.first_name}'s files. ♥")
                msg2 = to_small_caps(f"🚩 Please search your own. 📺")
                return await query.answer(
                    f"{msg1}\n\n{msg2}",
                    show_alert=True,
                )
        except Exception:
            pass
        _, page = query.data.split("#")

        if page == "goat":
            await query.answer(f"Hey {query.from_user.first_name},\n\n{to_small_caps('You are viewing 👑 G.O.A.T menu!')}\n{to_small_caps('Choose another option if you want to leave this menu')}", show_alert=True)
        elif page == "popular":
            await query.answer(f"Hey {query.from_user.first_name},\n\n{to_small_caps('You are viewing ❤ POPULAR menu!')}\n{to_small_caps('Choose another option if you want to leave this menu')}", show_alert=True)
        elif page == "trending":
            await query.answer(f"Hey {query.from_user.first_name},\n\n{to_small_caps('You are viewing 🚀 TRENDING menu!')}\n{to_small_caps('Choose another option if you want to leave this menu')}", show_alert=True)
        elif page == "trendingon":
            await query.answer(f"Hey {query.from_user.first_name},\n\n{to_small_caps('These are top trending topic on our channel')}\n\n{to_small_caps(f'✅ Last update: 1 minute ago')}\n{to_small_caps('(⚠ Note: Updates every minute...)')}", show_alert=True)
        else:
            await query.answer(f"Hey {query.from_user.first_name},\n{to_small_caps('How are you ❤ ?')}", show_alert=True)
    except FloodWait as lazydeveloper:
        # e.seconds is available in Pyrogram's FloodWait error.
        wait_time = lazydeveloper.value
        await query.answer(
            f"💔 Whoa, slow down, my love! You've been clicking too fast.\n\n"
            f"Please wait {wait_time} seconds before trying again.\n\n"
            f"Take a deep breath and come back soon ❤️",
            show_alert=True
        ) 
    except Exception as lazyDeveloperr:
        logging.info(lazyDeveloperr)

@Client.on_callback_query(filters.regex(r"^spol"))
async def advantage_spoll_choker(bot, query):
    try:
        await query.message.edit("🚀 wait...")
        _, id, user = query.data.split('#')
        if int(user) != 0 and query.from_user.id != int(user):
            msg1 = to_small_caps(f"♥ It's {query.message.reply_to_message.from_user.first_name}'s files. ♥")
            msg2 = to_small_caps(f"🚩 Please search your own. 📺")
            return await query.answer(
                f"{msg1}\n\n{msg2}",
                show_alert=True,
            )
        ok = await query.message.edit("🚀 wait... \nChecking files in our Databse 🔎")
        movie = await get_poster(id, id=True)
        search = movie.get('title')
        user_id = query.from_user.id   
        lazy_id = query.message.reply_to_message.id     
        files, offset, total_results = await get_search_results_badAss_LazyDeveloperr(query.message.chat.id, lazy_id, search)
        if files:
            k = (search, files, offset, total_results)
            await auto_filter(bot, query, k)
        else:
            k = await query.message.edit("Oops! No results found for your query\nPlease request another...")
            await asyncio.sleep(60)
            await k.delete()
            try:
                await query.message.reply_to_message.delete()
            except:
                pass
    except FloodWait as lazydeveloper:
        # e.seconds is available in Pyrogram's FloodWait error.
        wait_time = lazydeveloper.value
        await query.answer(
            f"💔 Whoa, slow down, my love! You've been clicking too fast.\n\n"
            f"Please wait {wait_time} seconds before trying again.\n\n"
            f"Take a deep breath and come back soon ❤️",
            show_alert=True
        ) 
    except Exception as lazydeveloperr:
        logging.info(lazydeveloperr)


# Helper: Group files by season dynamically.
def extract_Lazydeveloperr(files):
    season_files = defaultdict(list)
    for file in files:
        # Use regex to capture patterns like "s1", "S01", "season 1", etc.
        match = re.search(r'(?:season\s*|s)(\d{1,3})', file["file_name"], re.IGNORECASE)
        if match:
            season_num = match.group(1).lstrip("0") or "0"
            season_key = f"season {season_num}"
        else:
            season_key = "unknown"
        season_files[season_key].append({
            "file_id": file["file_id"],
            "file_name": file["file_name"],
            "file_size": file["file_size"],
            "caption": file["caption"]
        })
    return dict(season_files)

# Helper: Group files by episode dynamically.
def extract_episode_files(files):
    episode_files = defaultdict(list)
    for file in files:
        # Use regex to capture patterns like "e1", "E01", "episode 1", etc.
        match = re.search(r'(?:episode\s*|e)(\d{1,3})', file["file_name"], re.IGNORECASE)
        if match:
            ep_num = match.group(1).lstrip("0") or "0"
            ep_key = f"episode {ep_num}"
        else:
            ep_key = "unknown"
        episode_files[ep_key].append({
            "file_id": file["file_id"],
            "file_name": file["file_name"],
            "file_size": file["file_size"],
            "caption": file["caption"]
        })
    return dict(episode_files)


@Client.on_callback_query(filters.regex(r"^show_episode_details\|"))
async def show_episode_details_handler(client, query: CallbackQuery):
    try:
        try:
            if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
                msg1 = to_small_caps(f"♥ It's {query.message.reply_to_message.from_user.first_name}'s files. ♥")
                msg2 = to_small_caps(f"🚩 Please search your own. 📺")
                return await query.answer(
                    f"{msg1}\n\n{msg2}",
                    show_alert=True,
                )
        except Exception:
            pass
        # Expected callback data: "show_episode_details|<key>|<season_key>|<episode_key>|<offset>"
        parts = query.data.split("|")
        if len(parts) not in [4, 5]:
            return await query.answer("💔 Invalid data format.", show_alert=True)
        
        key = parts[1]
        season_key = parts[2].lower().strip()
        episode_key = parts[3].lower().strip()  # e.g., "episode 3"
        offset = int(parts[4]) if len(parts) == 5 else 0

        # Retrieve files from the stored search results.
        # files = temp.GETALL.get(key)
        files = temp.LAZY_LOCAL_FILES.get(key)
        settings = await get_settings(query.message.chat.id)
        pre = 'filep' if settings['file_secure'] else 'file'

        if not files:
            return await query.answer("No files found. Please search again.", show_alert=True)

        # Group files by season, then by episode.
        season_dict = extract_Lazydeveloperr(files)
        if season_key not in season_dict:
            return await query.answer(f"No episodes found for {season_key}.", show_alert=True)

        episode_dict = extract_episode_files(season_dict[season_key])
        if episode_key not in episode_dict:
            return await query.answer(f"No files found for {episode_key}.", show_alert=True)

        episode_files = episode_dict[episode_key]
        total_files = len(episode_files)
        page_size = MAX_EPISODES_PER_PAGE
        files_page = episode_files[offset: offset + page_size]

        # Build inline buttons for each file option.
        buttons = []
        for f in files_page:
            button_text = f"{get_size(f['file_size'])} |⫶̊ {f['file_name']}"
            buttons.append([
                InlineKeyboardButton(text=button_text, callback_data=f"{pre}#{f['file_id']}")
            ])

        # Pagination controls
        pagination_buttons = []
        if offset > 0:
            prev_offset = max(0, offset - page_size)
            pagination_buttons.append(
                InlineKeyboardButton(f"{BACK_BTN_TXT}", callback_data=f"show_episode_details|{key}|{season_key}|{episode_key}|{prev_offset}")
            )
        current_page = (offset // page_size) + 1
        total_pages = math.ceil(total_files / page_size)
        pagination_buttons.append(
            InlineKeyboardButton(f"🗓 {current_page}/{total_pages}", callback_data="pages")
        )
        if offset + page_size < total_files:
            next_offset = offset + page_size
            pagination_buttons.append(
                InlineKeyboardButton(f"{NEXT_BTN_TXT}", callback_data=f"show_episode_details|{key}|{season_key}|{episode_key}|{next_offset}")
            )
        if pagination_buttons:
            buttons.append(pagination_buttons)

        # Add a Back button to return to the episode selection menu for the season.
        buttons.insert(0,[InlineKeyboardButton(f"𓆩ཫ📺 {to_small_caps(f'{season_key}  ⫶̊  {episode_key}')}  🎞️ཀ𓆪", callback_data=f"lazydeveloperr")])
        buttons.insert(0,[
                InlineKeyboardButton(text="🚀Trending", callback_data=f"trending#lazytrends#{key}"),
                InlineKeyboardButton(text="♥ᴘᴏᴘᴜʟᴀʀ", callback_data=f"popular#lazyshort#{key}"),
                # InlineKeyboardButton(text="# ʀᴇQᴜᴇsᴛ", url=f'https://t.me/{temp.U_NAME}?start=requestmovie'),
                        ])
        # mnn kiya mera isiliye 2 buttons add kr diya 🙄
        buttons.append([InlineKeyboardButton(f"𓆩ཫ𐰌  🔙 Back 🎞️  𐰌ཀ𓆪", callback_data=f"show_lazydeveloperr|{key}|{season_key}")])

        await query.edit_message_reply_markup(InlineKeyboardMarkup(buttons))
        await query.answer("Select a file option.")
    except FloodWait as lazydeveloper:
        # e.seconds is available in Pyrogram's FloodWait error.
        wait_time = lazydeveloper.value
        await query.answer(
            f"💔 Whoa, slow down, my love! You've been clicking too fast.\n\n"
            f"Please wait {wait_time} seconds before trying again.\n\n"
            f"Take a deep breath and come back soon ❤️",
            show_alert=True
        )    
    except Exception as e:
        logger.error(f"Error in show_episode_details_handler: {e}")
        await query.answer("An error occurred while processing episode data.", show_alert=True)


@Client.on_callback_query(filters.regex(r"^show_lazydeveloperr\|"))
async def show_lazydeveloperr_handler(client, query: CallbackQuery):
    try:
        try:
            if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
                msg1 = to_small_caps(f"♥ It's {query.message.reply_to_message.from_user.first_name}'s files. ♥")
                msg2 = to_small_caps(f"🚩 Please search your own. 📺")
                return await query.answer(
                    f"{msg1}\n\n{msg2}",
                    show_alert=True,
                )
        except Exception:
            pass
        parts = query.data.split("|")
        if len(parts) == 3:
            key = parts[1]
            season_key = parts[2].lower().strip()  # e.g., "season 5"
            offset = 0
        elif len(parts) == 4:
            key = parts[1]
            season_key = parts[2].lower().strip()
            offset = int(parts[3])
        else:
            return await query.answer("💔 Invalid data format.", show_alert=True)
        
        # Retrieve file list from stored search results.
        # files = temp.GETALL.get(key)
        files = temp.LAZY_LOCAL_FILES.get(key)
        if not files:
            return await query.answer("No files found. Please search again.", show_alert=True)
        
        # Group files by season.
        season_dict = extract_Lazydeveloperr(files)
        if season_key not in season_dict:
            return await query.answer(f"No episodes found for {season_key}.", show_alert=True)
        
        # Now group the files for the selected season by episode.
        episode_dict = extract_episode_files(season_dict[season_key])
        # Filter out unknown episodes.
        valid_episodes = [ep for ep in episode_dict.keys() if ep != "unknown"]
        if not valid_episodes:
            return await query.answer("No episodes detected for this season.", show_alert=True)
        
        # Sort episode keys numerically (assuming format "episode X")
        sorted_episodes = sorted(valid_episodes, key=lambda x: int(x.split()[1]))
        
        # Pagination: show 10 episodes per page.
        page_size = MAX_EPISODES_LIST
        total_episodes = len(sorted_episodes)
        episodes_page = sorted_episodes[offset: offset + page_size]
        
        # Build inline buttons for each episode on this page.
        episode_buttons = []
        for episode in episodes_page:
            episode_buttons.append(
                InlineKeyboardButton(
                    text=f"🎞️ {episode.capitalize()}",
                    # Callback includes offset parameter so that further pagination can be handled.
                    callback_data=f"show_episode_details|{key}|{season_key}|{episode}|0"
                )
            )
        
        # Arrange episode buttons in rows of two.
        rows = []
        for i in range(0, len(episode_buttons), 2):
            row = episode_buttons[i:i+2]
            if len(row) == 1:
                row.append(InlineKeyboardButton(" ", callback_data="noop_LazyDeveloper_noop"))
            rows.append(row)
        
        # Pagination controls for episodes.
        pagination_buttons = []
        if offset > 0:
            prev_offset = max(0, offset - page_size)
            pagination_buttons.append(
                InlineKeyboardButton(f"{BACK_BTN_TXT}", callback_data=f"show_lazydeveloperr|{key}|{season_key}|{prev_offset}")
            )
        current_page = (offset // page_size) + 1
        total_pages = math.ceil(total_episodes / page_size)
        pagination_buttons.append(
            InlineKeyboardButton(f"🗓 {current_page}/{total_pages}", callback_data="pages")
        )
        if offset + page_size < total_episodes:
            next_offset = offset + page_size
            pagination_buttons.append(
                InlineKeyboardButton(f"{NEXT_BTN_TXT}", callback_data=f"show_lazydeveloperr|{key}|{season_key}|{next_offset}")
            )
        if pagination_buttons:
            rows.append(pagination_buttons)
        
        # Add a Back button row to return to season selection.
        header_row = [InlineKeyboardButton(f"𓆩ཫ🔻 {to_small_caps(f'{season_key} Episodes')} 🔻ཀ𓆪", callback_data=f"lazydeveloper")]
        footer_row = [InlineKeyboardButton(f"𓆩ཫ𐰌  🔙 Back 📺  𐰌ཀ𓆪", callback_data=f"seasons#{key}")]
        rows.insert(0, header_row)
        rows.append(footer_row)
        
        await query.edit_message_reply_markup(InlineKeyboardMarkup(rows))
        await query.answer("Select an episode.")
    except FloodWait as lazydeveloper:
        # e.seconds is available in Pyrogram's FloodWait error.
        wait_time = lazydeveloper.value
        await query.answer(
            f"💔 Whoa, slow down, my love! You've been clicking too fast.\n\n"
            f"Please wait {wait_time} seconds before trying again.\n\n"
            f"Take a deep breath and come back soon ❤️",
            show_alert=True
        )
    except Exception as e:
        logger.error(f"Error in show_lazydeveloperr_handler: {e}")
        # await query.answer("An error occurred while processing season data.", show_alert=True)


@Client.on_callback_query(filters.regex(r"^seasons#"))
async def seasons_cb_handler(client: Client, query: CallbackQuery):
    try:
        try:
            if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
                msg1 = to_small_caps(f"♥ It's {query.message.reply_to_message.from_user.first_name}'s files. ♥")
                msg2 = to_small_caps(f"🚩 Please search your own. 📺")
                return await query.answer(
                    f"{msg1}\n\n{msg2}",
                    show_alert=True,
                )
        except Exception:
            pass

        _, key = query.data.split("#")

        files = temp.LAZY_LOCAL_FILES.get(key)
        # print(f"KEY ==> {key} \nSEARCH = {search} \n files = {files}")
        if not files:
            return await query.answer("❌ No seasons found.", show_alert=True)
        
        season_dict = extract_Lazydeveloperr(files)
        # Filter out unknown seasons.
        valid_seasons = [s for s in season_dict.keys() if s != "unknown"]
        if not valid_seasons:
            return await query.answer("❌ No seasons detected.", show_alert=True)
        
        # Create season buttons (2 per row)
        season_buttons = []
        for season in sorted(valid_seasons, key=lambda x: int(x.split()[1])):
            season_buttons.append(InlineKeyboardButton(
                text=f"📺 {season.capitalize()}",
                callback_data=f"show_lazydeveloperr|{key}|{season}"
            ))
        
        rows = []
        for i in range(0, len(season_buttons), 2):
            row = season_buttons[i:i+2]
            if len(row) == 1:
                row.append(InlineKeyboardButton(" ", callback_data="noop_LazyDeveloper_noop"))
            rows.append(row)
        
        # Add header and footer
        rows.insert(0, [InlineKeyboardButton(f"𓆩ཫ📺 {to_small_caps('Select Season')} 📺ཀ𓆪", callback_data="select_option")])
        rows.append([InlineKeyboardButton(f"𓆩ཫ🔺 {to_small_caps('BACK TO 卄OME')} 🔺ཀ𓆪", callback_data=f"lazyhome#{key}")])
        
        await query.edit_message_reply_markup(InlineKeyboardMarkup(rows))
        await query.answer()
    except FloodWait as lazydeveloper:
        # e.seconds is available in Pyrogram's FloodWait error.
        wait_time = lazydeveloper.value
        await query.answer(
            f"💔 Whoa, slow down, my love! You've been clicking too fast.\n\n"
            f"Please wait {wait_time} seconds before trying again.\n\n"
            f"Take a deep breath and come back soon ❤️",
            show_alert=True
        )
    except Exception as e:
        logger.error(f"Got an unexpected error in seasons_cb_handler: {e}")



# ========================================
# ==============[  languages ]==========================
# ========================================
# Mapping for languages (keys are normalized language names)
LANGUAGE_MAPPING = {
    "english": ["english", "eng"],
    "hindi": ["hindi", "hin"],
    "tamil": ["tamil", "tam"],
    "telugu": ["telugu", "tel"],
    "kannada": ["kannada"],
    "malayalam": ["malayalam", "mal"],
    "spainish": ["spainish", "spa"],
    "japanese": ["japanese", "jap"],
    "korean": ["korean", "kor"],
    "urdu": ["urdu", "urdu"],
    "Bangali": ["Bangali", "Bangla"],
    # Add more languages as needed
}

# Mapping for qualities (keys are normalized quality labels)
QUALITY_MAPPING = {
    "1440p": ["1440p", "1440"],
    "2160p": ["2160p", "2160"],
    "1080p": ["1080p", "1080"],
    "540p": ["540p", "540"],
    "640p": ["640p", "540"],
    "720p": ["720p", "720"],
    "480p": ["480p", "480"],
    "360p": ["360p", "360"],
    "4k": ["4k", "4k"],
    "2k": ["2k", "4k"],
    # Add more qualities as needed
}

def detect_language(file_name: str) -> str:
    """Detects language from file name using LANGUAGE_MAPPING."""
    name = file_name.lower()
    for lang, keywords in LANGUAGE_MAPPING.items():
        for word in keywords:
            if word in name:
                return lang  # Return the normalized language key
    return "unknown"

def detect_quality(file_name: str) -> str:
    """Detects quality from file name using QUALITY_MAPPING."""
    name = file_name.lower()
    for quality, keywords in QUALITY_MAPPING.items():
        for word in keywords:
            if word in name:
                return quality  # Return the normalized quality key
    return "unknown"

from collections import defaultdict

def extract_languages(files):
    """
    Groups files by all detected languages from the file name.
    If a file has multiple language keywords, it will be added to each corresponding language bucket.
    
    Returns a dictionary like:
    {
        "english": [ { "file_id": ..., "file_name": ..., "file_size": ..., "caption": ... }, ... ],
        "hindi": [...],
        "malayalam": [...],
        "unknown": [...]
    }
    """
    language_files = defaultdict(list)
    for file in files:
        file_name = file["file_name"].lower()
        found_languages = set()
        # Check each language mapping against the file name
        for lang, keywords in LANGUAGE_MAPPING.items():
            for keyword in keywords:
                # If keyword appears in the file name (with a preceding '#' or a space, etc.), add it.
                if f"#{keyword}" in file_name or keyword in file_name:
                    found_languages.add(lang)
        # If no language is detected, mark as "unknown"
        if not found_languages:
            found_languages.add("unknown")
        # Add the file to every detected language bucket
        for lang in found_languages:
            language_files[lang].append({
                "file_id": file["file_id"],
                "file_name": file["file_name"],
                "file_size": file["file_size"],
                "caption": file["caption"]
            })
    return dict(language_files)

def extract_qualities(files) -> dict:
    """
    Groups files by detected quality from the file name.
    Returns a dictionary:
      {
         "1080p": [ { "file_id": ..., "file_name": ..., ... }, ... ],
         "720p": [...],
         "unknown": [...]
      }
    """
    quality_files = defaultdict(list)
    for file in files:
        qual = detect_quality(file["file_name"])
        quality_files[qual].append({
            "file_id": file["file_id"],
            "file_name": file["file_name"],
            "caption": file["caption"],
            "file_size": file["file_size"],
        })
    return dict(quality_files)

# 
@Client.on_callback_query(filters.regex(r"^languages#"))
async def languages_cb_handler(client: Client, query: CallbackQuery):
    try:
        try:
            if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
                msg1 = to_small_caps(f"♥ It's {query.message.reply_to_message.from_user.first_name}'s files. ♥")
                msg2 = to_small_caps(f"🚩 Please search your own. 📺")
                return await query.answer(
                    f"{msg1}\n\n{msg2}",
                    show_alert=True,
                )
        except Exception:
            pass
        # Extract key from callback data.
        _, key = query.data.split("#")
                
        files = temp.LAZY_LOCAL_FILES.get(key)
        
        if not files:
            return await query.answer("No files found. Please search again.", show_alert=True)
        
        language_dict = extract_languages(files)
        # Optionally, filter out "unknown" if you don't want to show it:
        valid_languages = [lang for lang in language_dict.keys() if lang != "unknown"]
        if not valid_languages:
            return await query.answer("❌ No language data detected.", show_alert=True)
        
        language_buttons = [
            InlineKeyboardButton(f"🪩 {lang.capitalize()}", callback_data=f"show_language_files|{key}|{lang}")
            for lang in valid_languages
        ]
        # Arrange in rows (2 per row)
        # rows = [language_buttons[i:i+2] for i in range(0, len(language_buttons), 2)]
        rows = []
        for i in range(0, len(language_buttons), 2):
            row = language_buttons[i:i+2]
            if len(row) == 1:
                row.append(InlineKeyboardButton(" ", callback_data="noop_LazyDeveloper_noop"))
            rows.append(row)
        
        # rows.insert(0, [InlineKeyboardButton("🔙 Back", callback_data=f"back_to_main#{key}")])
        # Add header and footer
        rows.insert(0, [InlineKeyboardButton(f"𓆩ཫ🪩 {to_small_caps('Select Languages')} 🪩ཀ𓆪", callback_data="select_option")])
        rows.append([InlineKeyboardButton(f"𓆩ཫ🔺 {to_small_caps('BACK TO 卄OME')} 🔺ཀ𓆪", callback_data=f"lazyhome#{key}")])
        
        await query.edit_message_reply_markup(InlineKeyboardMarkup(rows))
        await query.answer("Select a language.")
    except FloodWait as lazydeveloper:
        wait_time = lazydeveloper.value
        await query.answer(
            f"💔 Whoa, slow down, my love! You've been clicking too fast.\n\n"
            f"Please wait {wait_time} seconds before trying again.\n\n"
            f"Take a deep breath and come back soon ❤️",
            show_alert=True
        ) 
    except Exception as e:
        logger.error(f"Error in languages_cb_handler: {e}")


@Client.on_callback_query(filters.regex(r"^show_language_files\|"))
async def show_language_files_handler(client, query: CallbackQuery):
    try:
        try:
            if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
                msg1 = to_small_caps(f"♥ It's {query.message.reply_to_message.from_user.first_name}'s files. ♥")
                msg2 = to_small_caps(f"🚩 Please search your own. 📺")
                return await query.answer(
                    f"{msg1}\n\n{msg2}",
                    show_alert=True,
                )
        except Exception:
            pass
        parts = query.data.split("|")
        # Expected format: "show_language_files|<key>|<language>|<offset>" or without offset (default to 0)
        if len(parts) == 3:
            key, language = parts[1], parts[2].lower().strip()
            offset = 0
        elif len(parts) == 4:
            key, language = parts[1], parts[2].lower().strip()
            offset = int(parts[3])
        else:
            return await query.answer("💔 Invalid data format.", show_alert=True)

        # Retrieve files from the local storage (or temp variable)
        files = temp.LAZY_LOCAL_FILES.get(key)  # or temp.GETALL.get(key) if you're using that
        settings = await get_settings(query.message.chat.id)
        pre = 'filep' if settings['file_secure'] else 'file'
        if not files:
            return await query.answer("No files found.", show_alert=True)
        
        # Group files by language using your mapping helper
        language_dict = extract_languages(files)
        if language not in language_dict:
            return await query.answer(f"No files found for {language.capitalize()}.", show_alert=True)
        
        matching_files = language_dict[language]
        total_files = len(matching_files)
        
        # Calculate pagination
        files_page = matching_files[offset: offset + MAX_LANG_FILE_PER_PAGE]
        current_page = (offset // MAX_LANG_FILE_PER_PAGE) + 1
        total_pages = math.ceil(total_files / MAX_LANG_FILE_PER_PAGE)

        # Build inline buttons for each file in the current page
        buttons = []
        for file in files_page:
            button_text = f"{get_size(file['file_size'])} | 🪩 {file['file_name']}"
            buttons.append([
                InlineKeyboardButton(text=button_text, callback_data=f"{pre}#{file['file_id']}")
            ])
        
        # Build pagination controls
        pagination_buttons = []
        if offset > 0:
            prev_offset = max(0, offset - MAX_LANG_FILE_PER_PAGE)
            pagination_buttons.append(
                InlineKeyboardButton(BACK_BTN_TXT, callback_data=f"show_language_files|{key}|{language}|{prev_offset}")
            )
        pagination_buttons.append(
            InlineKeyboardButton(f"Page {current_page}/{total_pages}", callback_data="pages")
        )
        if offset + MAX_LANG_FILE_PER_PAGE < total_files:
            next_offset = offset + MAX_LANG_FILE_PER_PAGE
            pagination_buttons.append(
                InlineKeyboardButton(NEXT_BTN_TXT, callback_data=f"show_language_files|{key}|{language}|{next_offset}")
            )
        if pagination_buttons:
            buttons.append(pagination_buttons)
        
        # Add a Back button row to return to language selection.
        # buttons.insert(0, [InlineKeyboardButton("🔙 Back", callback_data=f"languages#{key}")])
        buttons.insert(0,[
                InlineKeyboardButton(text="🚀Trending", callback_data=f"trending#lazytrends#{key}"),
                InlineKeyboardButton(text="♥ᴘᴏᴘᴜʟᴀʀ", callback_data=f"popular#lazyshort#{key}"),
                # InlineKeyboardButton(text="# ʀᴇQᴜᴇsᴛ", url=f'https://t.me/{temp.U_NAME}?start=requestmovie'),
                        ])
        # mnn kiya mera isiliye 2 buttons add kr diya 🙄
        buttons.insert(0, [InlineKeyboardButton(f"𓆩ཫ🪩 {to_small_caps(f'All {language} Files')} 🪩ཀ𓆪", callback_data="select_option")])
        buttons.append([InlineKeyboardButton(f"𓆩ཫ𐰌  🔙 Back 🪩  𐰌ཀ𓆪", callback_data=f"languages#{key}")])
                
        await query.edit_message_reply_markup(InlineKeyboardMarkup(buttons))
        await query.answer("Here are the files for the selected language.")
    except FloodWait as lazydeveloper:
        # e.seconds is available in Pyrogram's FloodWait error.
        wait_time = lazydeveloper.value
        await query.answer(
            f"💔 Whoa, slow down, my love! You've been clicking too fast.\n\n"
            f"Please wait {wait_time} seconds before trying again.\n\n"
            f"Take a deep breath and come back soon ❤️",
            show_alert=True
        ) 
    except Exception as e:
        logger.error(f"Error in show_language_files_handler: {e}")

# 
@Client.on_callback_query(filters.regex(r"^qualities#"))
async def qualities_cb_handler(client: Client, query: CallbackQuery):
    try:
        try:
            if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
                msg1 = to_small_caps(f"♥ It's {query.message.reply_to_message.from_user.first_name}'s files. ♥")
                msg2 = to_small_caps(f"🚩 Please search your own. 📺")
                return await query.answer(
                    f"{msg1}\n\n{msg2}",
                    show_alert=True,
                )
        except Exception:
            pass
        _, key = query.data.split("#")
        
        # files = temp.GETALL.get(key)
        files = temp.LAZY_LOCAL_FILES.get(key)
        if not files:
            return await query.answer("No files found. Please search again.", show_alert=True)
        
        quality_dict = extract_qualities(files)
        valid_qualities = [q for q in quality_dict.keys() if q != "unknown"]
        if not valid_qualities:
            return await query.answer("❌ No quality data detected.", show_alert=True)
        
        quality_buttons = [
            InlineKeyboardButton(f"🫧 {q.upper()}", callback_data=f"show_quality_files|{key}|{q}")
            for q in valid_qualities
        ]

        rows = []
        for i in range(0, len(quality_buttons), 2):
            row = quality_buttons[i:i+2]
            if len(row) == 1:
                row.append(InlineKeyboardButton(" ", callback_data="noop_LazyDeveloper_noop"))
            rows.append(row)

        # rows = [quality_buttons[i:i+2] for i in range(0, len(quality_buttons), 2)]
        rows.insert(0, [InlineKeyboardButton(f"𓆩ཫ🫧 {to_small_caps('Select Qualities')} 🫧ཀ𓆪", callback_data="select_option")])
        rows.append([InlineKeyboardButton(f"𓆩ཫ🔺 {to_small_caps('BACK TO 卄OME')} 🔺ཀ𓆪", callback_data=f"lazyhome#{key}")])

        await query.edit_message_reply_markup(InlineKeyboardMarkup(rows))
        await query.answer("Select a quality.")
    except FloodWait as lazydeveloper:
        # e.seconds is available in Pyrogram's FloodWait error.
        wait_time = lazydeveloper.value
        await query.answer(
            f"💔 Whoa, slow down, my love! You've been clicking too fast.\n\n"
            f"Please wait {wait_time} seconds before trying again.\n\n"
            f"Take a deep breath and come back soon ❤️",
            show_alert=True
        ) 
    except Exception as e:
        logger.error(f"Error in qualities_cb_handler: {e}")

@Client.on_callback_query(filters.regex(r"^show_quality_files\|"))
async def show_quality_files_handler(client, query: CallbackQuery):
    try:
        try:
            if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
                msg1 = to_small_caps(f"♥ It's {query.message.reply_to_message.from_user.first_name}'s files. ♥")
                msg2 = to_small_caps(f"🚩 Please search your own. 📺")
                return await query.answer(
                    f"{msg1}\n\n{msg2}",
                    show_alert=True,
                )
        except Exception:
            pass
        parts = query.data.split("|")
        # Expected format: "show_quality_files|<key>|<quality>|<offset>" or without offset (default to 0)
        if len(parts) == 3:
            key, quality = parts[1], parts[2].lower().strip()
            offset = 0
        elif len(parts) == 4:
            key, quality = parts[1], parts[2].lower().strip()
            offset = int(parts[3])
        else:
            return await query.answer("💔 Invalid data format.", show_alert=True)

        # Retrieve files from storage
        files = temp.GETALL.get(key)
        settings = await get_settings(query.message.chat.id)
        pre = 'filep' if settings['file_secure'] else 'file'

        if not files:
            return await query.answer("No files found.", show_alert=True)
        
        # Group files by quality using your mapping helper
        quality_dict = extract_qualities(files)
        if quality not in quality_dict:
            return await query.answer(f"No files found for quality {quality.upper()}.", show_alert=True)
        
        matching_files = quality_dict[quality]
        total_files = len(matching_files)
        
        # Calculate pagination
        files_page = matching_files[offset: offset + MAX_QUAL_FILE_PER_PAGE]
        current_page = (offset // MAX_QUAL_FILE_PER_PAGE) + 1
        total_pages = math.ceil(total_files / MAX_QUAL_FILE_PER_PAGE)
        
        # Build inline buttons for each file option
        buttons = []
        for file in files_page:
            button_text = f"{get_size(file['file_size'])} | 🫧 {file['file_name']}"
            buttons.append([
                InlineKeyboardButton(text=button_text, callback_data=f"{pre}#{file['file_id']}")
            ])
        
        # Pagination controls
        pagination_buttons = []
        if offset > 0:
            prev_offset = max(0, offset - MAX_QUAL_FILE_PER_PAGE)
            pagination_buttons.append(
                InlineKeyboardButton(BACK_BTN_TXT, callback_data=f"show_quality_files|{key}|{quality}|{prev_offset}")
            )
        pagination_buttons.append(
            InlineKeyboardButton(f"Page {current_page}/{total_pages}", callback_data="pages")
        )
        if offset + MAX_QUAL_FILE_PER_PAGE < total_files:
            next_offset = offset + MAX_QUAL_FILE_PER_PAGE
            pagination_buttons.append(
                InlineKeyboardButton(NEXT_BTN_TXT, callback_data=f"show_quality_files|{key}|{quality}|{next_offset}")
            )
        if pagination_buttons:
            buttons.append(pagination_buttons)
        
        # Add a Back button row to return to quality selection.
        # buttons.insert(0, [InlineKeyboardButton("🔙 Back", callback_data=f"qualities#{key}")])
        buttons.insert(0,[
                InlineKeyboardButton(text="🚀Trending", callback_data=f"trending#lazytrends#{key}"),
                InlineKeyboardButton(text="♥ᴘᴏᴘᴜʟᴀʀ", callback_data=f"popular#lazyshort#{key}"),
                # InlineKeyboardButton(text="# ʀᴇQᴜᴇsᴛ", url=f'https://t.me/{temp.U_NAME}?start=requestmovie'),
                        ])
        # mnn kiya mera isiliye 2 buttons add kr diya 🙄
        buttons.insert(0, [InlineKeyboardButton(f"𓆩ཫ🫧 {to_small_caps(f'All {quality} Files')} 🫧ཀ𓆪", callback_data="select_option")])
        buttons.append([InlineKeyboardButton(f"𓆩ཫ𐰌  🔙 Back 🫧  𐰌ཀ𓆪", callback_data=f"qualities#{key}")])

        await query.edit_message_reply_markup(InlineKeyboardMarkup(buttons))
        await query.answer("Here are the files for the selected quality.")
    except FloodWait as lazydeveloper:
        # e.seconds is available in Pyrogram's FloodWait error.
        wait_time = lazydeveloper.value
        await query.answer(
            f"💔 Whoa, slow down, my love! You've been clicking too fast.\n\n"
            f"Please wait {wait_time} seconds before trying again.\n\n"
            f"Take a deep breath and come back soon ❤️",
            show_alert=True
        ) 
    except Exception as e:
        logger.error(f"Error in show_quality_files_handler: {e}")


@Client.on_callback_query(filters.regex(r"^lazyhome#"))
async def lazyhome_cb_handler(client: Client, query: CallbackQuery):
    try:
        try:
            if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
                msg1 = to_small_caps(f"♥ It's {query.message.reply_to_message.from_user.first_name}'s files. ♥")
                msg2 = to_small_caps(f"🚩 Please search your own. 📺")
                return await query.answer(
                    f"{msg1}\n\n{msg2}",
                    show_alert=True,
                )
        except Exception:
            pass
        _, key = query.data.split("#")
        search = FRESH.get(key)
        search = search.replace("_", " ")

        req = query.from_user.id
        chat_id = query.message.chat.id
        message = query.message
        lazy_id = query.message.reply_to_message.id


        files, offset, total_results = await get_search_results_badAss_LazyDeveloperr(chat_id, lazy_id, search, offset=0, filter=True)
        if not files:
            await query.answer(to_small_caps("🚩 Query Expired! Please search again..."), show_alert=1)
            return
        temp.GETALL[key] = files
        settings = await get_settings(message.chat.id)
        pre = 'filep' if settings['file_secure'] else 'file'
        temp.SHORT[query.from_user.id] = query.message.chat.id
        lazyuser_id = query.from_user.id
        try:
            if temp.SHORT.get(lazyuser_id)==None:
                return await message.reply_text(text="<b>Please Search Again in Group</b>")
            else:
                chat_id = temp.SHORT.get(lazyuser_id)
        except Exception as lazyerror:
            logging.info(lazyerror)
        if settings["button"]:
            btn = [
                    [
                        InlineKeyboardButton(
                            text=f"{get_size(file.file_size)} | {file.file_name}", callback_data=f'{pre}#{file.file_id}'
                        ),
                    ]
                    for file in files
                    ]

        else:
            btn = [
                    [
                        InlineKeyboardButton(text=f"{file.file_name}",callback_data=f'{pre}#{file.file_id}',),
                        InlineKeyboardButton(text=f"{get_size(file.file_size)}",callback_data=f'{pre}#{file.file_id}',),
                    ]
                    for file in files
                    ]

        btn.insert(0, [
            InlineKeyboardButton(f"🎖 {to_small_caps('LATEST MOVIE UPLOADED')}🎖", url=f"https://t.me/+rYEsBW04zHY0MDg1")
        ])
        # btn.insert(0, [
        #     InlineKeyboardButton(f"𓆩ཫ🔻 {to_small_caps('Select Season')} 🔻ཀ𓆪", callback_data=f"seasons#{key}")
        # ])
        # btn.insert(0, 
        #     [
        #         InlineKeyboardButton(f'𓆩ཫ⭕• ǫᴜᴀʟɪᴛʏ', callback_data=f"qualities#{key}"),
        #         InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇ •⭕ཀ𓆪", callback_data=f"languages#{key}"),
        #     ])
        # # btn.insert(0, [
        # #         InlineKeyboardButton("♨️ ꜱᴇɴᴅ ᴀʟʟ ꜰɪʟᴇꜱ ♨️", callback_data=f"sendfiles#{key}")
        # #     ])
        # btn.insert(0,
        #         [ 
        #         InlineKeyboardButton(text="🚀Trending", callback_data=f"trending#lazytrends#{key}"),
        #         InlineKeyboardButton(text="♥ᴘᴏᴘᴜʟᴀʀ", callback_data=f"popular#lazyshort#{key}"),
        #         # InlineKeyboardButton(text="# ʀᴇQᴜᴇsᴛ", url=f'https://t.me/{temp.U_NAME}?start=requestmovie'),
        #         ])
        # # btn.insert(0,
        # #     [ 
        # #     InlineKeyboardButton(text="⚡ ʜᴏᴡ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ⚡", url='https://telegram.me/+lI9zStHfHlllNjQ1'),
        # #     ] 
        # # )

        if offset != "":
            btn.append(
                [InlineKeyboardButton(text=f"🗓 1/{math.ceil(int(total_results) / 10)}", callback_data="pages"),
                InlineKeyboardButton(text=f"{NEXT_BTN_TXT}", callback_data=f"next_{req}_{key}_{offset}")]
            )
        else:
            btn.append(
                [InlineKeyboardButton(text="🗓 1/1", callback_data="pages")]
            )
        try:
            await query.edit_message_reply_markup(
                reply_markup=InlineKeyboardMarkup(btn)
            )
        except MessageNotModified:
            pass
        await query.answer()
    except FloodWait as lazydeveloper:
        # e.seconds is available in Pyrogram's FloodWait error.
        wait_time = lazydeveloper.value
        await query.answer(
            f"💔 Whoa, slow down, my love! You've been clicking too fast.\n\n"
            f"Please wait {wait_time} seconds before trying again.\n\n"
            f"Take a deep breath and come back soon ❤️",
            show_alert=True
        )    
    except Exception as e:
        logger.error(f"Got an unexpected error : {e}")


#========================================================================= 
#========================================================================= 
#========================================================================= 


# Born to make history @LazyDeveloper !
@Client.on_callback_query(filters.regex(r"^lazynext_"))
async def popular_next_page(bot, query):
    try:
        try:
            if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
                msg1 = to_small_caps(f"♥ It's {query.message.reply_to_message.from_user.first_name}'s files. ♥")
                msg2 = to_small_caps(f"🚩 Please search your own. 📺")
                return await query.answer(
                    f"{msg1}\n\n{msg2}",
                    show_alert=True,
                )
        except Exception:
            pass
        _, lazyshort, key, offset = query.data.split("_")
        try:
            offset = int(offset)
        except ValueError:
            offset = 0

        chat_id = query.from_user.id    

        # Get files, next offset, and total results
        files, n_offset, total = await get_ai_results_lazi(chat_id, offset=offset)

        if not files:
            await query.answer("No more files to display!", show_alert=True)
            return
        buttons = []
        if lazyshort != "lazygoat":
            buttons = [[
                            InlineKeyboardButton(text="⇊ᴘᴏᴘᴜʟᴀʀ", callback_data=f"current#popular"),
                            InlineKeyboardButton(text="🚀Trending", callback_data=f"trending#lazytrends#{key}"),
                            # InlineKeyboardButton(text="# ʀᴇQᴜᴇsᴛ", url=f'https://t.me/{temp.U_NAME}?start=requestmovie'),
                        ],[
                            InlineKeyboardButton(f"ཫ👑𐰌 ᴠɪᴇᴡ ɢʀᴇᴀᴛᴇᏕᴛ ᴏғ ᴀʟʟ ᴛɪᴍᴇ 𐰌👑ཀ", callback_data=f"popular#lazygoat#{key}")
                        ]]
        else:
            buttons = [[
                            InlineKeyboardButton(text=f"⇊{to_small_caps('✬G.O.A.T✬')}", callback_data=f"current#goat"),
                            InlineKeyboardButton(text="🚀Trending", callback_data=f"trending#lazytrends#{key}"),
                            # InlineKeyboardButton(text="# ʀᴇQᴜᴇsᴛ", url=f'https://t.me/{temp.U_NAME}?start=requestmovie'),
                        ],[
                           InlineKeyboardButton(f"𓆩ཫ❤𐰌 ᴠɪᴇᴡ ᴘᴏᴘᴜʟᴀʀ ᴍᴏᴠɪᴇs 𐰌❤ཀ𓆪", callback_data=f"popular#lazyshort#{key}")
                        ]]
        
        for title, imdb_id in files:
            try:
                regex = re.compile(re.escape(title), flags=re.IGNORECASE)
            except:
                continue

            file_available = await Media.find_one({'file_name': regex})
            if file_available:
                keyx = f"{query.message.chat.id}-{imdb_id}"
                POPDISK[keyx] = title
                buttons.append([InlineKeyboardButton(
                    text=f"✅⠐⢾ 🎬 {title}",
                    callback_data=f"fp#lazyshort#lazyfilez#{keyx}"
                )])
            else:
                buttons.append([InlineKeyboardButton(
                    text=f"❌⠐⢾ 🎬 {title}",
                    callback_data=f"na#{title}"  # 'na' for not available
                )])

        # Calculate current page and total pages
        current_page = math.ceil((offset + 1) / int(MAX_LAZY_BTNS))
        total_pages = math.ceil(total / int(MAX_LAZY_BTNS))

        # Pagination Buttons (add them at the end)
        pagination_buttons = []

        if offset > 0:
            prev_offset = max(0, offset - int(MAX_LAZY_BTNS))
            pagination_buttons.append(InlineKeyboardButton(f"{BACK_BTN_TXT}", callback_data=f"lazynext_{lazyshort}_{key}_{prev_offset}"))

        # Display current page
        pagination_buttons.append(
            InlineKeyboardButton(f"🗓 {current_page} / {total_pages}", callback_data="current")
        )

        # Show Next button only if there are more pages
        if n_offset:
            pagination_buttons.append(InlineKeyboardButton(f"{NEXT_BTN_TXT}", callback_data=f"lazynext_{lazyshort}_{key}_{n_offset}"))

        # Append pagination buttons at the end
        buttons.append(pagination_buttons)
        buttons.append([InlineKeyboardButton(text=f"𓆩ཫ🔺  {to_small_caps('BACK TO 卄OME')}  🔺ཀ𓆪", callback_data=f"fp#{lazyshort}#homepage#{key}")])

        try:
            await query.message.edit_reply_markup(
                reply_markup=InlineKeyboardMarkup(buttons),
            )
        except MessageNotModified:
            pass

        await query.answer()
    except FloodWait as lazydeveloper:
        # e.seconds is available in Pyrogram's FloodWait error.
        wait_time = lazydeveloper.value
        await query.answer(
            f"💔 Whoa, slow down, my love! You've been clicking too fast.\n\n"
            f"Please wait {wait_time} seconds before trying again.\n\n"
            f"Take a deep breath and come back soon ❤️",
            show_alert=True
        ) 
    except Exception as lazydeveloper:
        logging.info(lazydeveloper)

@Client.on_callback_query(filters.regex(r"^fp#"))
async def popular_cb_handler(client: Client, query: CallbackQuery):
    try:
        try:
            if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
                msg1 = to_small_caps(f"♥ It's {query.message.reply_to_message.from_user.first_name}'s files. ♥")
                msg2 = to_small_caps(f"🚩 Please search your own. 📺")
                return await query.answer(
                    f"{msg1}\n\n{msg2}",
                    show_alert=True,
                )
        except Exception:
            pass
        _, lazyshort, pop, key = query.data.split("#")
        

        if pop != "lazyfilez":
            search = FRESH.get(key)
        else:
            keyx = f"{query.message.chat.id}-{query.message.reply_to_message.id}"
            securesearch = FRESH.get(keyx)
            if securesearch is not None:
                FRESH[key] = securesearch
                search = POPDISK.get(key)

        search = search.replace("_", " ")

        if pop != "homepage":
            search = f"{search}"

        BUTTONS[key] = search
        req = query.from_user.id
        chat_id = query.message.chat.id
        message = query.message
        lazy_id = query.message.reply_to_message.id
        files, offset, total_results = await get_search_results_badAss_LazyDeveloperr(chat_id, lazy_id, search, offset=0, filter=True)

        if not files:
            await query.answer("🚫 NO files Found 🚫", show_alert=1)
            return
        temp.GETALL[key] = files 
        settings = await get_settings(message.chat.id)
        pre = 'filep' if settings['file_secure'] else 'file'
        temp.SHORT[query.from_user.id] = query.message.chat.id
        lazyuser_id = query.from_user.id
        try:
            if temp.SHORT.get(lazyuser_id)==None:
                return await message.reply_text(text="<b>Please Search Again in Group</b>")
            else:
                chat_id = temp.SHORT.get(lazyuser_id)
        except Exception as lazydeveloper:
            logging.info(lazydeveloper)
        if settings["button"]:

            btn = [
                        [
                            InlineKeyboardButton(
                                text=f"{get_size(file.file_size)} | {file.file_name}", callback_data=f'{pre}#{file.file_id}'
                            ),
                        ]
                        for file in files
                    ]

        else:
            btn = [
                        [
                            InlineKeyboardButton(text=f"{file.file_name}",callback_data=f'files#{file.file_id}',),
                            InlineKeyboardButton(text=f"{get_size(file.file_size)}",callback_data=f'files#{file.file_id}',),
                        ]
                        for file in files
                    ]
        btn.insert(0, [
            InlineKeyboardButton(f"🎖 {to_small_caps('LATEST MOVIE UPLOADED')}🎖", url=f"https://t.me/+rYEsBW04zHY0MDg1")
        ])
        # btn.insert(0, [
        #     InlineKeyboardButton(f"𓆩ཫ🔻 {to_small_caps('Select Season')} 🔻ཀ𓆪", callback_data=f"seasons#{key}")
        # ])
        # btn.insert(0, 
        #     [
        #         InlineKeyboardButton(f'𓆩ཫ⭕• ǫᴜᴀʟɪᴛʏ', callback_data=f"qualities#{key}"),
        #         InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇ •⭕ཀ𓆪", callback_data=f"languages#{key}"),
        #     ])

        # btn.insert(0,
        #     [ 
        #     InlineKeyboardButton(text="🚀Trending", callback_data=f"trending#lazytrends#{key}"),
        #     InlineKeyboardButton(text=f"{'♥ᴘᴏᴘᴜʟᴀʀ' if lazyshort != 'lazygoat' else {to_small_caps('✬G.O.A.T✬')} }", callback_data=f"popular#{lazyshort}#{key}"),
        #     # InlineKeyboardButton(text="# ʀᴇQᴜᴇsᴛ", url=f'https://t.me/{temp.U_NAME}?start=requestmovie'),
        #     ])

        if offset != "":
            btn.append(
                [InlineKeyboardButton(text=f"🗓 1/{math.ceil(int(total_results) / 10)}", callback_data="pages"),
                InlineKeyboardButton(text=f"{NEXT_BTN_TXT}", callback_data=f"next_{req}_{key}_{offset}")]
            )
        else:
            btn.append(
                [InlineKeyboardButton(text="🗓 1/1", callback_data="pages")]
            )
        if pop != "homepage":
            btn.append([InlineKeyboardButton(text=f"𓆩ཫ🔺  {to_small_caps('BACK TO 卄OME')}  🔺ཀ𓆪", callback_data=f"fp#lazyshortt#homepage#{key}")])

        try:
            await query.edit_message_reply_markup(
                reply_markup=InlineKeyboardMarkup(btn)
            )
        except MessageNotModified:
            pass
        await query.answer("♥")
    except FloodWait as lazydeveloper:
        # e.seconds is available in Pyrogram's FloodWait error.
        wait_time = lazydeveloper.value
        await query.answer(
            f"💔 Whoa, slow down, my love! You've been clicking too fast.\n\n"
            f"Please wait {wait_time} seconds before trying again.\n\n"
            f"Take a deep breath and come back soon ❤️",
            show_alert=True
        ) 
    except Exception as e:
        logger.error(f"Got an unexpected error : {e}")

user_popular_movies = {}
@Client.on_callback_query(filters.regex(r"^popular#"))
async def aimdb_popular_movies(client: Client, query: CallbackQuery):
    try:
        user_id = query.from_user.id
        try:
            if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
                msg1 = to_small_caps(f"♥ It's {query.message.reply_to_message.from_user.first_name}'s files. ♥")
                msg2 = to_small_caps(f"🚩 Please search your own. 📺")
                return await query.answer(
                    f"{msg1}\n\n{msg2}",
                    show_alert=True,
                )
        except Exception:
            pass
        _, lazyshort, key = query.data.split("#")
        
        buttons = []
        if lazyshort != "lazygoat":
            try:
                user_popular_movies[user_id] = await get_popular_movies()
                buttons = [[
                            InlineKeyboardButton(text="⇊ᴘᴏᴘᴜʟᴀʀ", callback_data=f"current#popular"),
                            InlineKeyboardButton(text="🚀Trending", callback_data=f"trending#lazytrends#{key}"),
                            # InlineKeyboardButton(text="# ʀᴇQᴜᴇsᴛ", url=f'https://t.me/{temp.U_NAME}?start=requestmovie'),
                        ],[
                            InlineKeyboardButton(f"ཫ👑𐰌 ᴠɪᴇᴡ ɢʀᴇᴀᴛᴇᏕᴛ ᴏғ ᴀʟʟ ᴛɪᴍᴇ 𐰌👑ཀ", callback_data=f"popular#lazygoat#{key}")
                        ]]

            except Exception as lazydeveloperr:
                logging.info(f"Error getting popular movies: {lazydeveloperr}")
        else:
            try:
                user_popular_movies[user_id] = await get_lazy_goat_movies()
                
                buttons = [[
                            InlineKeyboardButton(text=f"⇊{to_small_caps('G.O.A.T')}", callback_data=f"current#goat"),
                            InlineKeyboardButton(text="🚀Trending", callback_data=f"trending#lazytrends#{key}"),
                            # InlineKeyboardButton(text="# ʀᴇQᴜᴇsᴛ", url=f'https://t.me/{temp.U_NAME}?start=requestmovie'),
                        ],[
                           InlineKeyboardButton(f"𓆩ཫ❤𐰌 ᴠɪᴇᴡ ᴘᴏᴘᴜʟᴀʀ ᴍᴏᴠɪᴇs 𐰌❤ཀ𓆪", callback_data=f"popular#lazyshort#{key}")
                        ]]
 
            except Exception as lazydeveloper:
                logging.info(f"Error getting goat movies: {lazydeveloper}")


        files, offset, total_results = await get_ai_results_lazi(user_id , offset=0)

        for title, imdb_id in files:
            try:
                regex = re.compile(re.escape(title), flags=re.IGNORECASE)
            except:
                continue

            file_available = await Media.find_one({'file_name': regex})
            if file_available:
                keyx = f"{query.message.chat.id}-{imdb_id}"
                POPDISK[keyx] = title
                # File is available
                buttons.append([
                    InlineKeyboardButton(
                        text=f"✅⠐⢾ 🎬 {title}",
                        callback_data=f"fp#{lazyshort}#lazyfilez#{keyx}"
                    )
                ])
            else:
                # File is not available
                buttons.append([
                    InlineKeyboardButton(
                        text=f"❌⠐⢾ 🎬 {title}",
                        callback_data=f"na#{title}"  # 'na' for not available
                    )
                ])

        if offset != "":
            buttons.append(
                [InlineKeyboardButton(text=f"🗓 1/{math.ceil(int(total_results) / int(MAX_LAZY_BTNS))}", callback_data="pages"),
                InlineKeyboardButton(text=f"{NEXT_BTN_TXT}", callback_data=f"lazynext_{lazyshort}_{key}_{offset}")]
            )
        else:
            buttons.append(
                [InlineKeyboardButton(text="🗓 1/1", callback_data="pages")]
            )
        
        buttons.append([InlineKeyboardButton(text=f"𓆩ཫ🔺  {to_small_caps('BACK TO 卄OME')}  🔺ཀ𓆪", callback_data=f"fp#lazyshort#homepage#{key}")])
        
        await query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))
    except FloodWait as lazydeveloper:
        # e.seconds is available in Pyrogram's FloodWait error.
        wait_time = lazydeveloper.value
        await query.answer(
            f"💔 Whoa, slow down, my love! You've been clicking too fast.\n\n"
            f"Please wait {wait_time} seconds before trying again.\n\n"
            f"Take a deep breath and come back soon ❤️",
            show_alert=True
        ) 
    except Exception as lazydeveloper:
        logging.info(lazydeveloper)

async def get_ai_results_lazi(user_id, max_results=int(MAX_LAZY_BTNS), offset=0):
    files_data = user_popular_movies.get(user_id, [])
    total_results = len(files_data)

    # Validate offset and slice the list
    if offset < 0 or offset >= total_results:
        return [], None, total_results

    next_offset = offset + max_results
    files = files_data[offset:offset + max_results]

    if next_offset >= total_results:
        next_offset = None

    return files, next_offset, total_results

async def get_trending_results_lazi(user_id, max_results=int(MAX_LAZY_BTNS), offset=0):
    files_data = user_popular_movies.get(user_id, [])
    total_results = len(files_data)

    # Validate offset and slice the list
    if offset < 0 or offset >= total_results:
        return [], None, total_results

    next_offset = offset + max_results
    files = files_data[offset:offset + max_results]

    if next_offset >= total_results:
        next_offset = None

    return files, next_offset, total_results

# trending movies ===============================================
@Client.on_callback_query(filters.regex(r"^lazynexttrend_"))
async def trending_next_page(bot, query):
    try:
        try:
            if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
                msg1 = to_small_caps(f"♥ It's {query.message.reply_to_message.from_user.first_name}'s files. ♥")
                msg2 = to_small_caps(f"🚩 Please search your own. 📺")
                return await query.answer(
                    f"{msg1}\n\n{msg2}",
                    show_alert=True,
                )
        except Exception:
            pass

        _, lazyshort, key, offset = query.data.split("_")
        try:
            offset = int(offset)
        except ValueError:
            offset = 0

        chat_id = query.from_user.id    

        # Get files, next offset, and total results
        files, n_offset, total = await get_ai_results_lazi(chat_id, offset=offset)

        if not files:
            await query.answer("No more files to display!", show_alert=True)
            return

        buttons = [[
                    InlineKeyboardButton(text="⇊Trending", callback_data=f"current#trending"),
                    InlineKeyboardButton(text="♥ᴘᴏᴘᴜʟᴀʀ", callback_data=f"popular#lazyshort#{key}"),
                    # InlineKeyboardButton(text="# ʀᴇQᴜᴇsᴛ", url=f'https://t.me/{temp.U_NAME}?start=requestmovie'),
                ],[
                    InlineKeyboardButton(text=f"{to_small_caps(f'𓆩ཫ🔻 ...Trending Now... 🔻ཀ𓆪')}", callback_data=f"current#trendingon"),
                ]]

        # Lazy emojis based on ranking (buttons in a column)
        for title, emoji in files:
            keyx = f"{query.message.chat.id}-{str(uuid.uuid4()).split('-')[0]}"
            TOPDISK[keyx] = title 
            buttons.append(
                [InlineKeyboardButton(text=f"{emoji}  {to_small_caps(title)}", callback_data=f"ft#lazyfilez#{keyx}")]
            )

        # Calculate current page and total pages
        current_page = math.ceil((offset + 1) / int(MAX_LAZY_BTNS))
        total_pages = math.ceil(total / int(MAX_LAZY_BTNS))

        # Pagination Buttons (add them at the end)
        pagination_buttons = []

        if offset > 0:
            prev_offset = max(0, offset - int(MAX_LAZY_BTNS))
            pagination_buttons.append(InlineKeyboardButton(f"{BACK_BTN_TXT}", callback_data=f"lazynexttrend_{lazyshort}_{key}_{prev_offset}"))

        # Display current page
        pagination_buttons.append(
            InlineKeyboardButton(f"🗓 {current_page} / {total_pages}", callback_data="current")
        )

        # Show Next button only if there are more pages
        if n_offset:
            pagination_buttons.append(InlineKeyboardButton(f"{NEXT_BTN_TXT}", callback_data=f"lazynexttrend_{lazyshort}_{key}_{n_offset}"))

        # Append pagination buttons at the end
        buttons.append(pagination_buttons)
        buttons.append([InlineKeyboardButton(text=f"𓆩ཫ🔺  {to_small_caps('BACK TO 卄OME')}  🔺ཀ𓆪", callback_data=f"ft#homepage#{key}")])

        try:
            await query.message.edit_reply_markup(
                reply_markup=InlineKeyboardMarkup(buttons),
            )
        except MessageNotModified:
            pass

        await query.answer("♥")
    except FloodWait as lazydeveloper:
        # e.seconds is available in Pyrogram's FloodWait error.
        wait_time = lazydeveloper.value
        await query.answer(
            f"💔 Whoa, slow down, my love! You've been clicking too fast.\n\n"
            f"Please wait {wait_time} seconds before trying again.\n\n"
            f"Take a deep breath and come back soon ❤️",
            show_alert=True
        ) 
    except Exception as lazydeveloper:
        logging.info(lazydeveloper)

@Client.on_callback_query(filters.regex(r"^ft#"))
async def trending_cb_handler(client: Client, query: CallbackQuery):
    try:
        try:
            if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
                msg1 = to_small_caps(f"♥ It's {query.message.reply_to_message.from_user.first_name}'s files. ♥")
                msg2 = to_small_caps(f"🚩 Please search your own. 📺")
                return await query.answer(
                    f"{msg1}\n\n{msg2}",
                    show_alert=True,
                )
        except Exception:
            pass
        _, top, key = query.data.split("#")
        
        if top != "lazyfilez":
            search = FRESH.get(key)
        else:
            keyx = f"{query.message.chat.id}-{query.message.reply_to_message.id}"
            securesearch = FRESH.get(keyx)
            if securesearch is not None:
                FRESH[key] = securesearch
                search = TOPDISK.get(key)

        search = search.replace("_", " ")


        if top != "homepage":
            search = f"{search}"

        BUTTONS[key] = search
        req = query.from_user.id
        chat_id = query.message.chat.id
        message = query.message
        lazy_id = query.message.reply_to_message.id
        files, offset, total_results = await get_search_results_badAss_LazyDeveloperr(chat_id, lazy_id, search, offset=0, filter=True)

        if not files:
            await query.answer("🚫 NO files Found 🚫", show_alert=1)
            return
        temp.GETALL[key] = files 
        settings = await get_settings(message.chat.id)
        pre = 'filep' if settings['file_secure'] else 'file'
        temp.SHORT[query.from_user.id] = query.message.chat.id
        lazyuser_id = query.from_user.id
        try:
            if temp.SHORT.get(lazyuser_id)==None:
                return await message.reply_text(text="<b>Please Search Again in Group</b>")
            else:
                chat_id = temp.SHORT.get(lazyuser_id)
        except Exception as lazydeveloper:
            logging.info(lazydeveloper)
        if settings["button"]:

            btn = [
                        [
                            InlineKeyboardButton(
                                text=f"{get_size(file.file_size)} | {file.file_name}", callback_data=f'{pre}#{file.file_id}'
                            ),
                        ]
                        for file in files
                    ]

        else:
            btn = [
                        [
                            InlineKeyboardButton(text=f"{file.file_name}",callback_data=f'files#{file.file_id}',),
                            InlineKeyboardButton(text=f"{get_size(file.file_size)}",callback_data=f'files#{file.file_id}',),
                        ]
                        
                        for file in files
                    ]
        btn.insert(0, [
            InlineKeyboardButton(f"🎖 {to_small_caps('LATEST MOVIE UPLOADED')}🎖", url=f"https://t.me/+rYEsBW04zHY0MDg1")
        ])
        # btn.insert(0, [
        #     InlineKeyboardButton(f"𓆩ཫ🔻 {to_small_caps('Select Season')} 🔻ཀ𓆪", callback_data=f"seasons#{key}")
        # ])
        # btn.insert(0, 
        #     [
        #         InlineKeyboardButton(f'𓆩ཫ⭕• ǫᴜᴀʟɪᴛʏ', callback_data=f"qualities#{key}"),
        #         InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇ •⭕ཀ𓆪", callback_data=f"languages#{key}"),
        #     ])
        # # btn.insert(0, [
        # #     InlineKeyboardButton("♨️ ꜱᴇɴᴅ ᴀʟʟ ꜰɪʟᴇꜱ ♨️", callback_data=f"sendfiles#{key}")
        # # ])
        # btn.insert(0,
        #     [ 
        #     InlineKeyboardButton(text="🚀Trending", callback_data=f"trending#lazytrends#{key}"),
        #     InlineKeyboardButton(text=f"{to_small_caps('♥POPULAR')}", callback_data=f"popular#lazyshort#{key}"),
        #     # InlineKeyboardButton(text="# ʀᴇQᴜᴇsᴛ", url=f'https://t.me/{temp.U_NAME}?start=requestmovie'),
        #     ])
        # # btn.insert(0,
        # # [ 
	    # # InlineKeyboardButton(text="⚡ ʜᴏᴡ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ⚡", url='https://telegram.me/+lI9zStHfHlllNjQ1'),
        # # ])

        if offset != "":
            btn.append(
                [InlineKeyboardButton(text=f"🗓 1/{math.ceil(int(total_results) / 10)}", callback_data="pages"),
                InlineKeyboardButton(text=f"{NEXT_BTN_TXT}", callback_data=f"next_{req}_{key}_{offset}")]
            )
        else:
            btn.append(
                [InlineKeyboardButton(text="🗓 1/1", callback_data="pages")]
            )
        if top != "homepage":
            btn.append([InlineKeyboardButton(text=f"𓆩ཫ🔺  {to_small_caps('BACK TO 卄OME')}  🔺ཀ𓆪", callback_data=f"ft#homepage#{key}")])

        try:
            await query.edit_message_reply_markup(
                reply_markup=InlineKeyboardMarkup(btn)
            )
        except MessageNotModified:
            pass
        await query.answer()  
    except FloodWait as lazydeveloper:
        # e.seconds is available in Pyrogram's FloodWait error.
        wait_time = lazydeveloper.value
        await query.answer(
            f"💔 Whoa, slow down, my love! You've been clicking too fast.\n\n"
            f"Please wait {wait_time} seconds before trying again.\n\n"
            f"Take a deep breath and come back soon ❤️",
            show_alert=True
        ) 
    except Exception as e:
        logger.error(f"Got an unexpected error : {e}")

@Client.on_callback_query(filters.regex(r"^trending#"))
async def aion_trending_movies(client: Client, query: CallbackQuery):
    try:
        user_id = query.from_user.id
        try:
            if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
                msg1 = to_small_caps(f"♥ It's {query.message.reply_to_message.from_user.first_name}'s files. ♥")
                msg2 = to_small_caps(f"🚩 Please search your own. 📺")
                return await query.answer(
                    f"{msg1}\n\n{msg2}",
                    show_alert=True,
                )
        except Exception:
            pass
        _, lazyshort, key = query.data.split("#")

        user_popular_movies[user_id] = await get_lazy_trending_movies()
        files, offset, total_results = await get_trending_results_lazi(user_id , offset=0)
        buttons = [[
                    InlineKeyboardButton(text="⇊Trending", callback_data=f"current#trending"),
                    InlineKeyboardButton(text="❤ᴘᴏᴘᴜʟᴀʀ", callback_data=f"popular#lazyshort#{key}"),
                    # InlineKeyboardButton(text="# ʀᴇQᴜᴇsᴛ", url=f'https://t.me/{temp.U_NAME}?start=requestmovie'),
                ],[
                    InlineKeyboardButton(text=f"{to_small_caps(f'𓆩ཫ🔻 ...Trending Now... 🔻ཀ𓆪')}", callback_data=f"current#trendingon"),
                ]]
        
        # Lazy emojis based on ranking (buttons in a column)
        for title, emoji in files:
            keyx = f"{query.message.chat.id}-{str(uuid.uuid4()).split('-')[0]}"
            TOPDISK[keyx] = title 
            buttons.append(
                [InlineKeyboardButton(text=f"{emoji}  {to_small_caps(title)}", callback_data=f"ft#lazyfilez#{keyx}")]
            )

        if offset != "":
            buttons.append(
                [InlineKeyboardButton(text=f"🗓 1/{math.ceil(int(total_results) / int(MAX_LAZY_BTNS))}", callback_data="pages"),
                InlineKeyboardButton(text=f"{NEXT_BTN_TXT}", callback_data=f"lazynexttrend_{lazyshort}_{key}_{offset}")]
            )
        else:
            buttons.append(
                [InlineKeyboardButton(text="🗓 1/1", callback_data="pages")]
            )
        
        buttons.append([InlineKeyboardButton(text=f"𓆩ཫ🔺  {to_small_caps('BACK TO 卄OME')}  🔺ཀ𓆪", callback_data=f"ft#homepage#{key}")])
        
        await query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))
    except FloodWait as lazydeveloper:
        # e.seconds is available in Pyrogram's FloodWait error.
        wait_time = lazydeveloper.value
        await query.answer(
            f"💔 Whoa, slow down, my love! You've been clicking too fast.\n\n"
            f"Please wait {wait_time} seconds before trying again.\n\n"
            f"Take a deep breath and come back soon ❤️",
            show_alert=True
        ) 
    except Exception as e:
        logging.info(e)


# Born to make history @LazyDeveloper !
@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    data = query.data
    if query.data == "close_data":
        await query.message.delete()
    elif query.data == "reqinfo":
        await query.answer(text=script.REQINFO, show_alert=True)
    elif query.data == "delallconfirm":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == enums.ChatType.PRIVATE:
            grpid = await active_connection(str(userid))
            if grpid is not None:
                grp_id = grpid
                try:
                    chat = await client.get_chat(grpid)
                    title = chat.title
                except:
                    await query.message.edit_text("Make sure I'm present in your group!!", quote=True)
            else:
                await query.message.edit_text(
                    "I'm not connected to any groups!\nCheck /connections or connect to any groups",
                    quote=True
                )
                return await query.answer(f'• With ❤ {temp.B_NAME} ⛱')

        elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            grp_id = query.message.chat.id
            title = query.message.chat.title

        else:
            return await query.answer(f'• With ❤ {temp.B_NAME} ⛱')

        st = await client.get_chat_member(grp_id, userid)
        if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
            await del_all(query.message, grp_id, title)
        else:
            await query.answer("You need to be Group Owner or an Auth User to do that!", show_alert=True)
    elif query.data == "delallcancel":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == enums.ChatType.PRIVATE:
            await query.message.reply_to_message.delete()
            await query.message.delete()

        elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            grp_id = query.message.chat.id
            st = await client.get_chat_member(grp_id, userid)
            if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
                await query.message.delete()
                try:
                    await query.message.reply_to_message.delete()
                except:
                    pass
            else:
                await query.answer("That's not for you!", show_alert=True)
    elif "groupcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        act = query.data.split(":")[2]
        hr = await client.get_chat(int(group_id))
        title = hr.title
        user_id = query.from_user.id

        if act == "":
            stat = "CONNECT"
            cb = "connectcb"
        else:
            stat = "DISCONNECT"
            cb = "disconnect"

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{stat}", callback_data=f"{cb}:{group_id}"),
             InlineKeyboardButton("DELETE", callback_data=f"deletecb:{group_id}")],
            [InlineKeyboardButton("BACK", callback_data="backcb")]
        ])

        await query.message.edit_text(
            f"Group Name : **{title}**\nGroup ID : `{group_id}`",
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.MARKDOWN
        )
        return await query.answer(f'• With ❤ {temp.B_NAME} ⛱')
    elif "connectcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title

        user_id = query.from_user.id

        mkact = await make_active(str(user_id), str(group_id))

        if mkact:
            await query.message.edit_text(
                f"Connected to **{title}**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_text('Some error occurred!!', parse_mode=enums.ParseMode.MARKDOWN)
        return await query.answer(f'• With ❤ {temp.B_NAME} ⛱')
    elif "disconnect" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title
        user_id = query.from_user.id

        mkinact = await make_inactive(str(user_id))

        if mkinact:
            await query.message.edit_text(
                f"Disconnected from **{title}**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_text(
                f"Some error occurred!!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        return await query.answer(f'• With ❤ {temp.B_NAME} ⛱')
    elif "deletecb" in query.data:
        await query.answer()

        user_id = query.from_user.id
        group_id = query.data.split(":")[1]

        delcon = await delete_connection(str(user_id), str(group_id))

        if delcon:
            await query.message.edit_text(
                "Successfully deleted connection"
            )
        else:
            await query.message.edit_text(
                f"Some error occurred!!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        return await query.answer(f'• With ❤ {temp.B_NAME} ⛱')
    elif query.data == "backcb":
        await query.answer()

        userid = query.from_user.id

        groupids = await all_connections(str(userid))
        if groupids is None:
            await query.message.edit_text(
                "There are no active connections!! Connect to some groups first.",
            )
            return await query.answer(f'• With ❤ {temp.B_NAME} ⛱')
        buttons = []
        for groupid in groupids:
            try:
                ttl = await client.get_chat(int(groupid))
                title = ttl.title
                active = await if_active(str(userid), str(groupid))
                act = " - ACTIVE" if active else ""
                buttons.append(
                    [
                        InlineKeyboardButton(
                            text=f"{title}{act}", callback_data=f"groupcb:{groupid}:{act}"
                        )
                    ]
                )
            except:
                pass
        if buttons:
            await query.message.edit_text(
                "Your connected group details ;\n\n",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    elif "alertmessage" in query.data:
        grp_id = query.message.chat.id
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]
        reply_text, btn, alerts, fileid = await find_filter(grp_id, keyword)
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert, show_alert=True)

    if query.data.startswith("grantfreevip"):
        try:
            ident, file_id = query.data.split("#")
            print("hit me grantvip")
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start=grantfreevip_{file_id}")
        except Exception as e:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start=grantfreevip_{file_id}")
    
    if query.data.startswith("file"):
        try:
            ident, file_id = query.data.split("#")
            print("hit me file")
            files_ = await get_file_details(file_id)
            if not files_:
                return await query.answer('No such file exist.')
            files = files_[0]
            title = files.file_name
            size = get_size(files.file_size)
            f_caption = files.caption
            settings = await get_settings(query.message.chat.id)
            laxyuser = query.from_user.id
            user = await db.get_user(laxyuser)
            if user:
                subscription = user.get("subscription", "free")
            else:
                subscription = "free"

            if CUSTOM_FILE_CAPTION:
                try:
                    f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                        file_size='' if size is None else size,
                                                        file_caption='' if f_caption is None else f_caption)
                except Exception as e:
                    logger.exception(e)
                f_caption = f_caption
            if f_caption is None:
                f_caption = f"{files.file_name}"
            
            try:
                try:
                    if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
                        msg1 = to_small_caps(f"♥ It's {query.message.reply_to_message.from_user.first_name}'s files. ♥")
                        msg2 = to_small_caps(f"🚩 Please search your own. 📺")
                        return await query.answer(
                            f"{msg1}\n\n{msg2}",
                            show_alert=True,
                        )
                except Exception:
                    pass

                auth_channels = await db.get_auth_channels()
                if not auth_channels:
                    auth_channels = AUTH_CHANNEL

                if auth_channels and not await lazy_has_subscribed(client, query):
                    print("NO AUTH SUBS")
                    await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
                    return
                if subscription == "free":    
                    await query.answer(url=f"https://t.me/{temp.U_NAME}?start=sendfiles_{file_id}")
                    print("🚩 sendfiles ")
                    return
                elif settings['botpm']:
                    print("bot pm ✅")
                    await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
                    return
                else:
                    print("Else part for premium users ♥")
                    lzy = query.from_user.first_name
                    daily_limit, subscription, diverting_channel = await lazybarier(client, lzy, user_id)
                    
                    along_with_lazy_info = f"<b><u>⚠ DELETING IN {lazy_readable(FILE_AUTO_DELETE_TIME)} ⚠\nꜰᴏʀᴡᴀʀᴅ ᴀɴᴅ ꜱᴛᴀʀᴛ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ᴛʜᴇʀᴇ </u></b>"
                    along_with_lazy_footer = f"<b>Dear {query.from_user.mention} ! {script.FOOTER_TEXT}</b>"
                    lazy_caption_template =f"{along_with_lazy_info}\n\n<b>{f_caption}</b>\n\n{along_with_lazy_footer}"

                    share_url = f"https://t.me/{temp.U_NAME}?start=file_{file_id}"
                    sharelazymsg = f"{to_small_caps('•❤ Access file at your fingertip ❤•')}\n{to_small_caps('🤝 Join us now for the latest movies and entertainment!')}"
                    lazydeveloper_text = quote(sharelazymsg)
                    button = [
                            [
                                InlineKeyboardButton(to_small_caps('📢 Moviebot Updates'), url=f'https://t.me/+9nu0wCcIMgU0ZDBl'),
                            ],[
                                InlineKeyboardButton(to_small_caps('🔗Join Our Groups !'), url=f"https://t.me/+QQipfrVXeEMxYTc9")
                            ]]
                                   
                    send_to_lazy_channel = diverting_channel if diverting_channel is not None else LAZY_DIVERTING_CHANNEL

                    keyboard = InlineKeyboardMarkup(button)
                    lazy_file = await client.send_cached_media(
                        chat_id=send_to_lazy_channel,
                        file_id=file_id,
                        caption=lazy_caption_template,
                        reply_markup=keyboard,
                        protect_content=True if ident == "filep" else False 
                    )
                    
                    await query.answer('Requested file has been sent to you privately. Check PM sweetheart ❤', show_alert=True)
                    # 
                    asyncio.create_task(send_lazy_video(client, query, send_to_lazy_channel, lazy_file))

                    if subscription != "limited":
                        await db.deduct_limit(user_id)
                        logging.info(f"\n\n::::::::::>> Tried to Deduct limit for user [{query.message.from_user.first_name}] :|::> ID ::> {user_id} :|::> AT : {datetime.datetime.now()}")
                    else:
                        logging.info(f"\n\nFailed to deduct limit for user ::> [{query.message.from_user.first_name}] :| ID ::> {user_id} :|::> ERROR AT :  {datetime.datetime.now()}")
                    
                    # asyncio.create_task(schedule_deletion(client, query.message.chat.id, lazy_file))
                    return
            except UserIsBlocked:
                await query.answer('☣Unblock the bot sweetie!', show_alert=True)
            except PeerIdInvalid:
                await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
            except Exception as e:
                await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
        except Exception as e:
            print(e)

    elif query.data.startswith("checksub"):
        auth_channels = await db.get_auth_channels()
        if not auth_channels:
            auth_channels = AUTH_CHANNEL

        if auth_channels and not await lazy_has_subscribed(client, query):
            await query.answer("Over smart is a type of serious disease, so don't be... Please join our force sub channel to continue !", show_alert=True)
            return
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('No such file exist.')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                       file_size='' if size is None else size,
                                                       file_caption='' if f_caption is None else f_caption)
            except Exception as e:
                logger.exception(e)
                f_caption = f_caption
        if f_caption is None:
            f_caption = f"{title}"
        await query.answer()
        await db.get_user(query.from_user.id)
        
        if not user:
            diverting_channel = LAZY_DIVERTING_CHANNEL
        else:
            diverting_channel = user.get("diverting_channel", None)

        send_to_lazy_channel = diverting_channel if diverting_channel is not None else LAZY_DIVERTING_CHANNEL

        along_with_lazy_info = f"<b><u>⚠ DELETING IN {lazy_readable(FILE_AUTO_DELETE_TIME)} ⚠\nꜰᴏʀᴡᴀʀᴅ ᴀɴᴅ ꜱᴛᴀʀᴛ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ᴛʜᴇʀᴇ </u></b>"
        along_with_lazy_footer = f"<b>Dear {query.from_user.mention} ! {script.FOOTER_TEXT}</b>"
        lazy_caption_template =f"{along_with_lazy_info}\n\n<b>{f_caption}</b>\n\n{along_with_lazy_footer}"

        # Create the inline keyboard button with callback_data
        share_url = f"https://t.me/{temp.U_NAME}?start=file_{file_id}"
        sharelazymsg = f"{to_small_caps('•❤ Access file at your fingertip ❤•')}\n{to_small_caps('🤝 Join us now for the latest movies and entertainment!')}"
        lazydeveloper_text = quote(sharelazymsg)
        button = [
            [
                InlineKeyboardButton(to_small_caps('📢 Moviebot Updates'), url=f'https://t.me/+9nu0wCcIMgU0ZDBl'),
            ],[
                InlineKeyboardButton(to_small_caps('🔗Join Our Groups !'), url=f"https://t.me/+QQipfrVXeEMxYTc9")
            ]]     
        # Create the inline keyboard markup with the button
        keyboard = InlineKeyboardMarkup(button)
        lazy_file = await client.send_cached_media(
            chat_id=send_to_lazy_channel,
            file_id=file_id,
            caption=lazy_caption_template,
            # reply_markup=keyboard,
            protect_content=True if ident == 'checksubp' else False
        )
        #
        asyncio.create_task(send_lazy_video(client, query, send_to_lazy_channel, lazy_file)) 
        if await db.deduct_limit(user_id):
            logging.info(f"\n\n::::::::::>> Tried to Deduct limit for user [{query.message.from_user.first_name}] :|::> ID ::> {user_id} :|::> AT : {datetime.datetime.now()}")
        else:
            logging.info(f"\n\nFailed to deduct limit for user ::> [{query.message.from_user.first_name}] :| ID ::> {user_id} :|::> ERROR AT :  {datetime.datetime.now()}")
        
        # asyncio.create_task(schedule_deletion(client, query.message.chat.id, lazy_file))

    elif query.data.startswith("requestmovie"):
        try:
            await query.message.delete()
            # [⚠STOP] 👋 hello its lazydeveloper! dont change the text of reply_text here, else request function will not work ⚠
            await query.message.reply_text("<i><b>»» Please enter movie name...</b></i>",	
            reply_to_message_id=query.message.id,  
            reply_markup=ForceReply(True)) 
        except Exception as lazydeveloper:
            logging.info(lazydeveloper)

    elif query.data.startswith("setdivertingchannel"):
        try:
            await query.message.delete()
            # [⚠STOP] 👋 hello its lazydeveloper! dont change the text of reply_text here, else request function will not work ⚠
            await query.message.reply_text("<i><b>»» Please send your channel id where you want to recieve the Movies/series in format:  -100xxxxx ...</b></i>",	
            reply_to_message_id=query.message.id,  
            reply_markup=ForceReply(True)) 
        except Exception as lazydeveloper:
            logging.info(lazydeveloper)

    elif data.startswith("generate_stream_link"):
        _, file_id = data.split(":")
        try:
            user_id = query.from_user.id
            username =  query.from_user.mention 

            log_msg = await client.send_cached_media(
                chat_id=STREAM_LOGS, 
                file_id=file_id,
            )
            
            fileName = {quote_plus(get_name(log_msg))}
            lazy_stream = f"{URL}watch/{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
            lazy_download = f"{URL}{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"

            xo = await query.message.reply_text(f'🔐')
            await asyncio.sleep(1)
            await xo.delete()

            await log_msg.reply_text(
                text=f"•• ʟɪɴᴋ ɢᴇɴᴇʀᴀᴛᴇᴅ ꜰᴏʀ ɪᴅ #{user_id} \n•• ᴜꜱᴇʀɴᴀᴍᴇ : {username} \n\n•• ᖴᎥᒪᗴ Nᗩᗰᗴ : {fileName}",
                quote=True,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("web Download", url=lazy_download),  # we download Link
                                                    InlineKeyboardButton('▶Stream online', url=lazy_stream)]])  # web stream Link
            )
            await query.message.reply_text(
                text=f"•📺 ʟɪɴᴋ ɢᴇɴᴇʀᴀᴛᴇᴅ  ⏬\n Name: {fileName}",
                quote=True,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("web Download", url=lazy_download),  # we download Link
                                                    InlineKeyboardButton('▶Stream online', url=lazy_stream)]])  # web stream Link
            )
        except Exception as e:
            print(e)  # print the error message
            await query.answer(f"☣something went wrong sweetheart\n\n{e}", show_alert=True)
            return

    elif data.startswith("info_"):
        channel_id = data.split("_")[1]
        try:
            chat = await client.get_chat(channel_id)
            channel_name = f"{to_small_caps(chat.title)}"
        except:
            channel_name = f"{to_small_caps('❌ADMIN❌')}"

        await query.answer(f"📢 CHANNEL NAME: {channel_name}\n🆔 CHANNEL ID: {channel_id}", show_alert=True)

    elif data.startswith("remove_"):
        channel_id = data.split("_")[1]
        removed = await db.remove_required_channel(channel_id)

        if removed:
            await query.message.edit_text(f"✅ Channel ID: {channel_id} has been removed.")
        else:
            await query.answer("❌ Failed to remove the channel.", show_alert=True)

    elif query.data == "pages":
        await query.answer()

    elif query.data == "start":
        buttons = [[
                    InlineKeyboardButton('𓆩• Aᴅᴅ Mᴇ Tᴏ Yᴏᴜʀ Gʀᴏᴜᴘ •𓆪', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
                    ],
                    [
                    InlineKeyboardButton('〄 ꜱᴜᴘᴘᴏʀᴛ', url=f'https://t.me/{SUPPORT_CHAT}'),
                    InlineKeyboardButton('⛱ ɢʀᴏᴜᴘ', url=f'https://t.me/{MOVIE_GROUP_USERNAME}')
                    ]]

        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.START_TXT.format(query.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        await query.answer(f'• With ❤ {temp.B_NAME} ⛱')
    
    elif query.data == "help":
        buttons = [[
            InlineKeyboardButton('• ᴀᴜᴛᴏ ꜰɪʟᴛᴇʀ •', callback_data='autofilter')
        ], [
            InlineKeyboardButton('𓆩• ᴄᴏɴɴᴇᴄᴛɪᴏɴ', callback_data='coct'),
            InlineKeyboardButton('ᴇxᴛʀᴀ ᴍᴏᴅᴇꜱ •𓆪', callback_data='extra')
        ], [
            InlineKeyboardButton('• ꜱᴛᴀᴛᴜꜱ  •', callback_data='stats')
        ],[
            InlineKeyboardButton('𓆩ཫ 🏠 ʜᴏᴍᴇ  ཀ𓆪', callback_data='start'),
        ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.HELP_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "manuelfilter":
        buttons = [[
            InlineKeyboardButton('𓆩• 🚪 ʙᴀᴄᴋ', callback_data='help'),
            InlineKeyboardButton('⏹️ Buttons •𓆪', callback_data='button')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.MANUELFILTER_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    
    elif query.data == "button":
        buttons = [[
            InlineKeyboardButton('𓆩• 🚪 ʙᴀᴄᴋ •𓆪', callback_data='manuelfilter')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.BUTTON_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    
    elif query.data == "autofilter":
        try:
            buttons = [[
            InlineKeyboardButton('𓆩ཫ 🚪 ʙᴀᴄᴋ  ཀ𓆪', callback_data='help')
            ]]
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.message.edit_text(
                text=script.AUTOFILTER_TXT,
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )
        except Exception as lazydeveloper:
            logging.info(lazydeveloper)

    elif query.data.startswith("sendfiles"):
        user = query.from_user.id
        ident, key = query.data.split("#")
        settings = await get_settings(query.message.chat.id)
        try:
            await query.answer(url=f"https://telegram.me/{temp.U_NAME}?start=allfiles_{key}")
            return
        except UserIsBlocked:
            await query.answer('Unblock the bot baby !', show_alert=True)
        except PeerIdInvalid:
            await query.answer(url=f"https://telegram.me/{temp.U_NAME}?start=allfiles_{key}")
        except Exception as e:
            logger.exception(e)
            await query.answer(url=f"https://telegram.me/{temp.U_NAME}?start=allfiles_{key}")
  
    elif query.data.startswith("del"):
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('Nᴏ sᴜᴄʜ ғɪʟᴇ ᴇxɪsᴛ.')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption
        settings = await get_settings(query.message.chat.id)
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                       file_size='' if size is None else size,
                                                       file_caption='' if f_caption is None else f_caption)
            except Exception as e:
                logger.exception(e)
            f_caption = f_caption
        if f_caption is None:
            f_caption = f"{files.file_name}"
        await query.answer(url=f"https://telegram.me/{temp.U_NAME}?start=file_{file_id}")

    elif data.startswith("notify_user_not_avail"):
        _, user_id, movie = data.split(":")
        # Send message to user
        try:
            btn = [[
                InlineKeyboardButton(text=f"🔍 Sᴇᴀʀᴄʜ 🇭​​​​​🇪​​​​​🇷​​​​​🇪​​​​​ 🔎", url=f"https://telegram.me/{MOVIE_GROUP_USERNAME}")
            ],[
                InlineKeyboardButton(text=f"🐞 ══• ʀᴇᴘᴏʀᴛ ɪꜱꜱᴜᴇ •══ 🐞", url=f"https://telegram.me/{SUPPORT_CHAT}")
            ]]
            btn_lzdv = [
                [
                InlineKeyboardButton(text=f"🗑 Delete Log ❌", callback_data = "close_data")
                ]]
            reply_markup_lzdv = InlineKeyboardMarkup(btn_lzdv)
            reply_markup = InlineKeyboardMarkup(btn)
            await client.send_message(int(user_id), f"😒 oops! Your requested content named `{movie}` is not available right now, we are really trying our best to serve you this content, can you please provide us some more details related to your query `{movie}`, \nSend details to Admin : <a href='https://telegram.me/{ADMIN_USRNM}'>**Send here...**</a>\n\n❤ Thank You for the contribution", reply_markup=reply_markup)
            await query.edit_message_text(text=f"- __**User notified successfully sweetie...✅**__\n\n⏳**Status** : Not Available 😒.\n🪪**UserID** : `{user_id}`\n🎞**Content** : `{movie}`\n\n\n🦋",reply_markup=reply_markup_lzdv)
            # Delete callback query message
            await query.answer()
            await query.delete()
        except Exception as e:
            await query.answer(f"☣something went wrong sweetheart\n\n{e}", show_alert=True)
            return
        
    elif data.startswith("notify_user_alrupl"):
        _, user_id, movie = data.split(":")
        # Send message to user
        try:
            btn = [[
                InlineKeyboardButton(text=f"🔍 Sᴇᴀʀᴄʜ 🇭​​​​​🇪​​​​​🇷​​​​​🇪​​​​​ 🔎", url=f"https://telegram.me/{MOVIE_GROUP_USERNAME}")
            ],[
                InlineKeyboardButton(text=f"🐞 ══• ʀᴇᴘᴏʀᴛ ɪꜱꜱᴜᴇ •══ 🐞", url=f"https://telegram.me/{SUPPORT_CHAT}")
            ]]
            btn_lzdv = [
                [
                InlineKeyboardButton(text=f"🗑 Delete Log ❌", callback_data = "close_data")
                ]]
            reply_markup_lzdv = InlineKeyboardMarkup(btn_lzdv)            
            reply_markup = InlineKeyboardMarkup(btn)
            await client.send_message(int(user_id), f"🛋 Hey dear, Your requested content named `{movie}` is already available in our database! You can easily get this movie by searching it's correct name in our official group...\nSend details to Admin : \n\n❤ Thank You for the contribution", reply_markup=reply_markup)
            await query.edit_message_text(text=f"- __**User notified successfully sweetie...✅**__\n\n⏳**Status** : Already Uploaded ⚡.\n🪪**UserID** : `{user_id}`\n🎞**Content** : `{movie}`\n\n\n🦋",reply_markup=reply_markup_lzdv)
            await query.answer()
            await query.delete()
        except Exception as lazydeveloper:
            logging.info(lazydeveloper)
            await query.answer(f"☣something went wrong baby\n\n{lazydeveloper}", show_alert=True)
            return
        
    elif data.startswith("notify_userupl"):
        _, user_id, movie = data.split(":")
        # Send message to user
        try:
            btn = [[
                InlineKeyboardButton(text=f"🔍 Sᴇᴀʀᴄʜ 🇭​​​​​🇪​​​​​🇷​​​​​🇪​​​​​ 🔎", url=f"https://telegram.me/{MOVIE_GROUP_USERNAME}")
            ],[
                InlineKeyboardButton(text=f"🐞 ══• ʀᴇᴘᴏʀᴛ ɪꜱꜱᴜᴇ •══ 🐞", url=f"https://telegram.me/{SUPPORT_CHAT}")
            ]]
            btn_lzdv = [
                [
                InlineKeyboardButton(text=f"🗑 Delete Log ❌", callback_data = "close_data")
                ]]
            reply_markup_lzdv = InlineKeyboardMarkup(btn_lzdv) 
            reply_markup = InlineKeyboardMarkup(btn)
            await client.send_message(int(user_id), f"✅ Hey dear, Your requested content named `{movie}` is now available in our database! You can easily get this movie by searching it's correct name in our official group...\n\n❤ Thank You for the contribution", reply_markup=reply_markup)
            await query.edit_message_text(text=f"- __**User notified successfully sweetie...✅**__\n\n⏳**Status** : Upload done ✅.\n🪪**UserID** : `{user_id}`\n🎞**Content** : `{movie}`\n\n\n🦋", reply_markup=reply_markup_lzdv)
            await query.answer()
            await query.delete()
        except Exception as e:
            await query.answer(f"☣something went wrong\n\n{e}", show_alert=True)
            return
        
    elif data.startswith("notify_user_req_rejected"):
        _, user_id, movie = data.split(":")
        # Send message to user
        try:
            btn = [[
                InlineKeyboardButton(text=f"🔍 Sᴇᴀʀᴄʜ 🇭​​​​​🇪​​​​​🇷​​​​​🇪​​​​​ 🔎", url=f"https://telegram.me/{MOVIE_GROUP_USERNAME}")
            ],[
                InlineKeyboardButton(text=f"🐞 ══• ʀᴇᴘᴏʀᴛ ɪꜱꜱᴜᴇ •══ 🐞", url=f"https://telegram.me/{SUPPORT_CHAT}")
            ]]
            btn_lzdv = [
                [
                InlineKeyboardButton(text=f"🗑 Delete Log ❌", callback_data = "close_data")
                ]]
            reply_markup_lzdv = InlineKeyboardMarkup(btn_lzdv) 
            reply_markup = InlineKeyboardMarkup(btn)
            await client.send_message(int(user_id), f"🙇‍♀️ Sorry Darling! Your requested content named `{movie}` is rejected by our **ADMiN**, we are really very sorry for the inconvenience, we can't process your request at the moment...\n\n❤️‍🩹Keep your search environment friendly, sweetheart!", reply_markup=reply_markup)
            await query.edit_message_text(text=f"- __**User notified successfully sweetie...✅**__\n\n⏳**Status** : Request Rejected ❌.\n🪪**UserID** : `{user_id}`\n🎞**Content** : `{movie}`\n\n\n🦋",reply_markup=reply_markup_lzdv)
        # Delete callback query message
            await query.answer()
            await query.delete()
        except Exception as e:
            await query.answer(f"☣something went wrong darling\n\n{e}", show_alert=True)
            return
        
    elif data.startswith("notify_user_spelling_error"):
        _, user_id, movie = data.split(":")
        # Send message to user
        try:
            btn = [[
                InlineKeyboardButton(text=f"🔍 Sᴇᴀʀᴄʜ 🇭​​​​​🇪​​​​​🇷​​​​​🇪​​​​​ 🔎", url=f"https://telegram.me/{MOVIE_GROUP_USERNAME}")
            ],[
                InlineKeyboardButton(text=f"🐞 ══• ʀᴇᴘᴏʀᴛ ɪꜱꜱᴜᴇ •══ 🐞", url=f"https://telegram.me/{SUPPORT_CHAT}")
            ]]
            btn_lzdv = [
                [
                InlineKeyboardButton(text=f"🗑 Delete Log ❌", callback_data = "close_data")
                ]]
            reply_markup_lzdv = InlineKeyboardMarkup(btn_lzdv) 
            reply_markup = InlineKeyboardMarkup(btn)
            await client.send_message(int(user_id), f"🌍 Your spelling matters.\nThe requested content `{movie}` is available in our database, You were unable to get it because of your spelling mistake.🧐 Please make sure you've spelled correctly while searching content in group...\n\n❤Thank u for supporting us.", reply_markup=reply_markup)
            await query.edit_message_text(text=f"- __**User notified successfully sweetie...✅**__\n\n⏳**Status** : Spelling error 🖊.\n🪪**UserID** : `{user_id}`\n🎞**Content** : `{movie}`\n\n\n🦋",reply_markup=reply_markup_lzdv)
        # Delete callback query message
            await query.answer()
            await query.delete()
        except Exception as e:
            await query.answer(f"☣something went wrong sweetie\n\n{e}", show_alert=True)
            return
    
    elif data.startswith("notify_user_custom"):
        _, user_id, movie = data.split(":")
        # Send message to user
        try:
            btn = [[
                InlineKeyboardButton(text=f"🔍 Sᴇᴀʀᴄʜ 🇭​​​​​🇪​​​​​🇷​​​​​🇪​​​​​ 🔎", url=f"https://telegram.me/{MOVIE_GROUP_USERNAME}")
            ],[
                InlineKeyboardButton(text=f"🐞 ══• ʀᴇᴘᴏʀᴛ ɪꜱꜱᴜᴇ •══ 🐞", url=f"https://telegram.me/{SUPPORT_CHAT}")
            ]]
            btn_lzdv = [
                [
                InlineKeyboardButton(text=f"🗑 Delete Log ❌", callback_data = "close_data")
                ]]
            reply_markup_lzdv = InlineKeyboardMarkup(btn_lzdv) 
            reply_markup = InlineKeyboardMarkup(btn)
            await client.send_message(int(user_id), f"🌍 Your spelling matters.\nThe requested content `{movie}` is available in our database, You were unable to get it because of your spelling mistake.🧐 Please make sure you've spelled correctly while searching content in group...\n\n❤Thank u for supporting us.", reply_markup=reply_markup)
            await query.edit_message_text(text=f"- __**User notified successfully sweetie...✅**__\n\n⏳**Status** : Spelling error 🖊.\n🪪**UserID** : `{user_id}`\n🎞**Content** : `{movie}`\n\n\n🦋",reply_markup=reply_markup_lzdv)
        # Delete callback query message
            await query.answer()
            await query.delete()
        except Exception as e:
            await query.answer(f"☣something went wrong sweetie\n\n{e}", show_alert=True)
            return
    
    elif data.startswith("notify_user_req_rcvd"):
        _, user_id, movie = data.split(":")
        # Send message to user
        try:
            btn = [[
                InlineKeyboardButton(text=f"𓆩ཫ❤𐰌  {to_small_caps('Request More')}  𐰌❤ཀ𓆪", callback_data=f"requestmovie")
            ],[
                InlineKeyboardButton(text=f"🐞 ══• ʀᴇᴘᴏʀᴛ ɪꜱꜱᴜᴇ •══ 🐞", url=f"https://telegram.me/{SUPPORT_CHAT}")
            ]]
            btn_lzdv = [
                        [InlineKeyboardButton(text=f"♻ ̶R̶e̶q̶u̶e̶s̶t̶ ̶R̶e̶c̶i̶e̶v̶e̶d ♻", callback_data=f"notify_user_req_rcvd:{user_id}:{movie}")],
                        [InlineKeyboardButton(text=f"✅Upload Done", callback_data=f"notify_userupl:{user_id}:{movie}")],
                        [InlineKeyboardButton(text=f"⚡Already Upl..", callback_data=f"notify_user_alrupl:{user_id}:{movie}"),InlineKeyboardButton("🖊Spell Error", callback_data=f"notify_user_spelling_error:{user_id}:{movie}")],
                        [InlineKeyboardButton(text=f"😒Not Available", callback_data=f"notify_user_not_avail:{user_id}:{movie}"),InlineKeyboardButton("📃Write Reply", callback_data=f"notify_user_custom:{user_id}:{movie}")],
                        [InlineKeyboardButton("❌Reject Req", callback_data=f"notify_user_req_rejected:{user_id}:{movie}")]
                       ]
            reply_markup_lzdv = InlineKeyboardMarkup(btn_lzdv)
            reply_markup = InlineKeyboardMarkup(btn)
            await client.send_message(int(user_id), f"💞Hello sweetheart ! we have recieved your request for  `{movie}`... \n\nPlease keep some patience, we will upload it as soon as possible. \n❤ Thank u for your Love .❤", reply_markup=reply_markup)
            await query.edit_message_text(text=f"- __**User notified successfully sweetie...✅**__\n\n⏳**Status** : Request Recieved 🖊.\n🪪**UserID** : `{user_id}`\n🎞**Content** : `{movie}`\n\n\n🦋",reply_markup=reply_markup_lzdv)
        # Delete callback query message
            await query.answer()
            await query.delete()
        except Exception as e:
            await query.answer(f"☣something went wrong sweetie\n\n{e}", show_alert=True)
            return

 
    #Adding This feature to the bot to get the controls over the groups  
    elif query.data.startswith("verify_lazy_group"):
        _, chatTitle, chatID = query.data.split(":")
        try:
            await client.send_message(chatID, text=f"Hello users !\n From now i will provide you contents 24X7 💘")
            await db.verify_lazy_chat(int(chatID))
            temp.LAZY_VERIFIED_CHATS.append(int(chatID))
            btn = [
                [
                InlineKeyboardButton(text=f"🚫 BAN Chat 🤐", callback_data=f"bangrpchat:{chatTitle}:{chatID}")
            ],[
                InlineKeyboardButton(text=f"❌ Close ❌", callback_data="close_data")
            ]
            ]
            reply_markup = InlineKeyboardMarkup(btn)
            ms = await query.edit_message_text(f"**🍁 Chat successfully verified 🧡**\n\n**Chat ID**: {chatID}\n**Chat Title**:{chatTitle}", reply_markup=reply_markup)
        except Exception as e:
            ms.edit(f"Got a Lazy error:\n{e}" )
            logger.error(f"Please solve this Error Lazy Bro : {e}")
    # ban group
    elif query.data.startswith("bangrpchat"):
        _, chatTitle, chatID = query.data.split(":")
        try:
            await client.send_message(chatID, text=f"Oops! Sorry, Let's Take a break\nThis is my last and Good Bye message to you all. \n\nContact my admin for more info")
            await db.disable_chat(int(chatID))
            temp.BANNED_CHATS.append(int(chatID))
            btn = [
                [
                InlineKeyboardButton(text=f"⚡ Enable Chat 🍁", callback_data=f"enablelazychat:{chatTitle}:{chatID}")
            ],[
                InlineKeyboardButton(text=f"❌ Close ❌", callback_data="close_data")
            ]
            ]
            reply_markup = InlineKeyboardMarkup(btn)
            ms = await query.edit_message_text(f"**chat successfully disabled** ✅\n\n**Chat ID**: {chatID}\n\n**Chat Title**:{chatTitle}", reply_markup=reply_markup)
        except Exception as e:
            ms.edit(f"Got a Lazy error:\n{e}" )
            logger.error(f"Please solve this Error Lazy Bro : {e}")
    #unban group 
    elif query.data.startswith("enablelazychat"):
        _, chatTitle , chatID = query.data.split(":")
        try:
            sts = await db.get_chat(int(chatID))
            if not sts:
                return await query.answer("Chat Not Found In DB !", show_alert=True)
            if not sts.get('is_disabled'):
                return await query.answer('This chat is not yet disabled.', show_alert=True)
            await db.re_enable_chat(int(chatID))
            temp.BANNED_CHATS.remove(int(chatID))
            btn = [[
                    InlineKeyboardButton(text=f"😜 BAN Again 😂", callback_data=f"bangrpchat:{chatTitle}:{chatID}")
                ],[
                    InlineKeyboardButton(text=f"❌ Close ❌", callback_data="close_data")
            ]]
            reply_markup = InlineKeyboardMarkup(btn)
            ms = await query.edit_message_text(f"**chat successfully Enabled** 💞\n\n**Chat ID**: {chatID}\n\n**Chat Title**:{chatTitle}", reply_markup=reply_markup)
        except Exception as e:
            ms.edit(f"Got a Lazy error:\n{e}" )
            logger.error(f"Please solve this Error Lazy Bro : {e}")

    elif query.data == "select_info":
        await query.answer('Please select anything from above menu to filter files eg: Language, Season, Quality', show_alert=True)
       
    elif query.data == "read_in_hin":
        await query.answer("• सही वर्तनी में पूछें।\n• ओटीटी प्लेटफॉर्म पर रिलीज़ न हुई फिल्मों के बारे में न पूछें।\n• संभवतः [मूवी का नाम भाषा] इस तरह पूछें।", show_alert=True)
    
    elif query.data == "read_in_eng":
        await query.answer("• Ask in correct spelling.\n• Don't ask for movies which are not released on OTT platforms.\n• Possible ask [ Movies name language] like this.", show_alert=True)
    
    elif query.data == "read_in_mal":
        await query.answer('• ശരിയായ അക്ഷരവിന്യാസത്തിൽ ചോദിക്കുക.\n• OTT പ്ലാറ്റ്‌ഫോമിൽ റിലീസ് ചെയ്യാത്ത സിനിമകൾ ചോദിക്കരുത്.\n• ഇതുപോലെ [സിനിമയുടെ പേര് ഭാഷ] ചോദിക്കാം.', show_alert=True)
    
    elif query.data == "read_in_tam":
        await query.answer('சரியான எழுத்துப்பிழையில் கேளுங்கள்.\nOTT பிளாட்ஃபார்மில் வெளியாகாத திரைப்படங்களைக் கேட்காதீர்கள்.\n• இப்படி [படத்தின் பெயர் மொழி] கேட்கலாம்.', show_alert=True)
    
    elif query.data == "read_in_tel":
        await query.answer('సరైన స్పెల్లింగ్‌లో అడగండి.\nOTT ప్లాట్‌ఫారమ్‌లో విడుదల చేయని సినిమాల కోసం అడగవద్దు.\n• ఇలా [సినిమా పేరు భాష] అడగవచ్చు.', show_alert=True)
    
    elif query.data == "read_in_urd":
        await query.answer('صحیح ہجے میں پوچھیں۔ •\nOTT پلیٹ فارم پر ریلیز نہ ہونے والی فلموں کے بارے میں مت پوچھیں۔ •\nممکنہ پوچھیں [ فلم کے نام کی زبان] اس طرح۔ •', show_alert=True)
    
    elif query.data == "read_in_san":
        await query.answer('• सम्यक् वर्तनीरूपेण पृच्छन्तु।\• OTT मञ्चे न विमोचितानि चलच्चित्राणि मा याचयन्तु।\n• संभवं [ Movie name language] इत्येतत् पृच्छन्तु।', show_alert=True)
    
    elif query.data == "select_option":
        await query.answer('👇👇 Please select anyone of the following  options 👇👇', show_alert=True)
    
    elif query.data == "coct":
        buttons = [[
            InlineKeyboardButton('𓆩ཫ 🚪 ʙᴀᴄᴋ  ཀ𓆪', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CONNECTION_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "extra":
        buttons = [[
            InlineKeyboardButton('𓆩ཫ 🚪 ʙᴀᴄᴋ ', callback_data='help'),
            InlineKeyboardButton('👑 ᴀᴅᴍɪɴ  ཀ𓆪', callback_data='admin')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.EXTRAMOD_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "admin":
        buttons = [[
            InlineKeyboardButton('𓆩ཫ 🚪 ʙᴀᴄᴋ  ཀ𓆪', callback_data='extra')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.ADMIN_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "stats":
        buttons = [[
            InlineKeyboardButton('𓆩ཫ 🚪 ʙᴀᴄᴋ', callback_data='help'),
            InlineKeyboardButton('♻️  ཀ𓆪', callback_data='rfrsh')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        total = await Media.count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        await query.message.edit_text(
            text=script.STATUS_TXT.format(total, users, chats, monsize, free),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "alertuser":
        await query.answer(text=f"❤ Thank You {query.from_user.mention} ❤", show_alert=True)

    elif query.data == "donatelazydev":
        buttons = [
            [ InlineKeyboardButton("⨳   Close   ⨳", callback_data="close_data") ]
            ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.DNT_TEXT.format(query.from_user.mention, DONATION_LINK),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "lazyhome":
        text = f"""\n⨳♡ Rename  MⓄde ✅♡⨳\n\n**Please tell, what should i do with this file.?**\n"""
        buttons = [[ InlineKeyboardButton("📝✧✧ S𝚝ar𝚝 re𝚗aᗰi𝚗g ✧✧📝", callback_data="rename") ],
                           [ InlineKeyboardButton("⨳  C L Ф S Ξ  ⨳", callback_data="cancel") ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
                    text=text,
                    reply_markup=reply_markup,
                    parse_mode=enums.ParseMode.HTML
                )    
    elif query.data == "requireauth":
        buttons = [
            [ InlineKeyboardButton("⨳  C L Ф S Ξ  ⨳", callback_data="cancel") ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.REQ_AUTH_TEXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "exit":
        await query.answer("Sorry Darling! You can't make any changes...\n\nOnly my Admin can change this setting...", show_alert = True)
        return
    elif query.data == "invalid_index_process":
        await query.answer("Hey sweetie, please send me the last media with quote from your group.\nAnd also make sure that i am admin in your beloved group...")
        return

    elif query.data == "cancel":
        try:
            await query.message.delete()
        except:
            return
    elif query.data == "rfrsh":
        await query.answer("Fetching MongoDb DataBase")
        buttons = [[
            InlineKeyboardButton('𓆩• 👩‍🦯 Back', callback_data='help'),
            InlineKeyboardButton('refresh •𓆪', callback_data='rfrsh')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        total = await Media.count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        await query.message.edit_text(
            text=script.STATUS_TXT.format(total, users, chats, monsize, free),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    
    elif query.data.startswith("setgs"):
        ident, set_type, status, grp_id = query.data.split("#")
        grpid = await active_connection(str(query.from_user.id))

        if str(grp_id) != str(grpid):
            await query.message.edit("Your Active Connection Has Been Changed. Go To /settings.")
            return await query.answer(f'• With ❤ {temp.B_NAME} ⛱')

        if status == "True":
            await save_group_settings(grpid, set_type, False)
        else:
            await save_group_settings(grpid, set_type, True)

        settings = await get_settings(grpid)

        if settings is not None:
            buttons = [
                    [
                        InlineKeyboardButton('Filter Button',
                                            callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}'),
                        InlineKeyboardButton('Single' if settings["button"] else 'Double',
                                            callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}')
                    ],
                    [
                        InlineKeyboardButton('Bot PM', callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}'),
                        InlineKeyboardButton('✅ Yes' if settings["botpm"] else '❌ No',
                                            callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}')
                    ],
                    [
                        InlineKeyboardButton('File Secure',
                                            callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}'),
                        InlineKeyboardButton('✅ Yes' if settings["file_secure"] else '❌ No',
                                            callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}')
                    ],
                    [
                        InlineKeyboardButton('IMDB', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}'),
                        InlineKeyboardButton('✅ Yes' if settings["imdb"] else '❌ No',
                                            callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}')
                    ],
                    [
                        InlineKeyboardButton('Spell Check',
                                            callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}'),
                        InlineKeyboardButton('✅ Yes' if settings["spell_check"] else '❌ No',
                                            callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}')
                    ],
                    [
                        InlineKeyboardButton('Welcome', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}'),
                        InlineKeyboardButton('✅ Yes' if settings["welcome"] else '❌ No',
                                            callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}')
                    ]
                ]

            reply_markup = InlineKeyboardMarkup(buttons)
            await query.message.edit_reply_markup(reply_markup)
    await query.answer(f'• With ❤ {temp.B_NAME} ⛱')

async def ai_spell_check(wrong_name, msg):
    async def search_movie(wrong_name):
        search_results = imdb.search_movie(wrong_name)
        movie_list = [movie['title'] for movie in search_results]
        return movie_list
    movie_list = await search_movie(wrong_name)
    if not movie_list:
        return
    for _ in range(5):
        closest_match = process.extractOne(wrong_name, movie_list)
        if not closest_match or closest_match[1] <= 80:
            return 
        movie = closest_match[0]
        lazy_id = msg.id
        files, offset, total_results = await get_search_results_badAss_LazyDeveloperr(msg.chat.id, lazy_id, movie)
        if files:
            return movie
        movie_list.remove(movie)
    return

async def auto_filter(client, msg, spoll=False):
    if not spoll:
        message = msg
        settings = await get_settings(message.chat.id)
        if message.text.startswith("/"): return  # ignore commands
        if re.findall("((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", message.text):
            return
        if len(message.text) < 100:
            search = message.text
            requested_movie = search.strip()
            user_id = message.from_user.id
            search = search.lower()
            find = search.split(" ")
            search = ""
            removes = ["in", "series", "full", "horror", "thriller", "mystery", "print", "file", "2k", "4k", "2004", "2024", "2025", "2020", "2021", "2022", "2023","new","movies", "the", "a", "an", "480", "480p", "720p", "720", "1080p", "1080", "hindi","english", "eng", "hin","kor","korean" ]
            for x in find:
                if x in removes:
                    continue
                else:
                    search = search + x + " "
                    # print(f"New search is : {search}")
            search = re.sub(r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|bro|bruh|broh|helo|that|find|dubbed|link|venum|iruka|pannunga|pannungga|anuppunga|anupunga|anuppungga|anupungga|film|undo|kitti|kitty|tharu|kittumo|kittum|movie|any(one)|with\ssubtitle(s)?)", "", search, flags=re.IGNORECASE)
            search = re.sub(r"\s+", " ", search).strip()
            search = search.replace("-", " ")
            search = search.replace(":","")            
            files, offset, total_results = await get_search_results_badAss_LazyDeveloperr(message.chat.id, message.id, search, offset=0, filter=True)
            # print(files)
            if not files:
                if settings["spell_check"]:
                    ai_sts = await msg.reply_text(f'<blockquote>🤖 ʜᴏʟᴅ ᴏɴ! ᴀ.ɪ. ᴀᴛ ᴡᴏʀᴋ!</blockquote>ғɪɴᴅɪɴɢ ᴛʜᴇ ʙᴇsᴛ ᴍᴀᴛᴄʜ ғᴏʀ: <b>{msg.text}</b>... 🔍')
                    is_misspelled = await ai_spell_check(search, msg)
                    if is_misspelled:
                        await asyncio.sleep(2)
                        msg.text = is_misspelled
                        await ai_sts.delete()
                        return await auto_filter(client, msg)
                    await ai_sts.delete()
                    await advantage_spell_chok(msg)
                    return                                                                                                       
                
        else: 
            return
    else:
        settings = await get_settings(msg.message.chat.id)
        message = msg.message.reply_to_message  # msg will be callback query
        search, files, offset, total_results = spoll
    pre = 'filep' if settings['file_secure'] else 'file'
    key = f"{message.chat.id}-{message.id}"
    FRESH[key] = search
    temp.GETALL[key] = files
    temp.SHORT[message.from_user.id] = message.chat.id
    lazyuser_id = message.from_user.id

    try:
        if temp.SHORT.get(lazyuser_id)==None:
            return await message.reply_text(text="<b>Please Search Again in Group</b>")
        else:
            chat_id = temp.SHORT.get(lazyuser_id)
    except Exception as e:
        logging.info(e)
    if settings["button"]:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"{get_size(file.file_size)} | {file.file_name}", callback_data=f'{pre}#{file.file_id}'
                ),
            ]
            for file in files
        ]

    else:
        btn = [
                    [
                        InlineKeyboardButton(text=f"{file.file_name}",callback_data=f'{pre}#{file.file_id}',),
                        InlineKeyboardButton(text=f"{get_size(file.file_size)}",callback_data=f'{pre}#{file.file_id}',),
                    ]
                    for file in files
                ]
    
    btn.insert(0, [
        InlineKeyboardButton(f"🎖 {to_small_caps('LATEST MOVIE UPLOADED')}🎖", url=f"https://t.me/+rYEsBW04zHY0MDg1")
    ])
    # btn.insert(0, [
    #     InlineKeyboardButton(f"𓆩ཫ🔻 {to_small_caps('Select Season')} 🔻ཀ𓆪", callback_data=f"seasons#{key}")
    # ])
    # btn.insert(0, 
    #     [
    #         InlineKeyboardButton(f'𓆩ཫ⭕• ǫᴜᴀʟɪᴛʏ', callback_data=f"qualities#{key}"),
    #         InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇ •⭕ཀ𓆪", callback_data=f"languages#{key}"),
    #     ])
    # btn.insert(0,
    # [ 
    # InlineKeyboardButton(text="🚀Trending", callback_data=f"trending#lazytrends#{key}"),
    # InlineKeyboardButton(text=f"{to_small_caps('♥POPULAR')}", callback_data=f"popular#lazyshort#{key}"),
    # # InlineKeyboardButton(text="# ʀᴇQᴜᴇsᴛ", url=f'https://t.me/{temp.U_NAME}?start=requestmovie'),
    # ])

    if offset != "":
        key = f"{message.chat.id}-{message.id}"
        BUTTONS[key] = search
        req = message.from_user.id if message.from_user else 0
        btn.append(
            [InlineKeyboardButton(text=f"🗓 1/{math.ceil(int(total_results) / 10)}", callback_data="pages"),
             InlineKeyboardButton(text=f"{NEXT_BTN_TXT}", callback_data=f"next_{req}_{key}_{offset}")]
        )
    else:
        btn.append(
            [InlineKeyboardButton(text="🗓 1/1", callback_data="pages")]
        )

    #waiting user to complete imdb process @LazyDeveloperr
    user = message.from_user
    full_name = user.first_name + " " + user.last_name if user.last_name else user.first_name
    # waiting overs here @LazyDeveloperr
    #top = await db.get_top_searches()
    
    waiting_message = await message.reply_text(f"Setting up your request {full_name}...")
    imdb = await get_poster(search, file=(files[0]).file_name) if settings["imdb"] else None
    TEMPLATE = settings['template']
    await waiting_message.delete()
    if imdb:
        cap = TEMPLATE.format(
            query=search,
            title=imdb['title'],
            votes=imdb['votes'],
            aka=imdb["aka"],
            seasons=imdb["seasons"],
            localized_title=imdb['localized_title'],
            kind=imdb['kind'],
            imdb_id=imdb["imdb_id"],
            cast=imdb["cast"],
            runtime=imdb["runtime"],
            countries=imdb["countries"],
            certificates=imdb["certificates"],
            languages=imdb["languages"],
            director=imdb["director"],
            writer=imdb["writer"],
            producer=imdb["producer"],
            composer=imdb["composer"],
            cinematographer=imdb["cinematographer"],
            music_team=imdb["music_team"],
            distributors=imdb["distributors"],
            release_date=imdb['release_date'],
            year=imdb['year'],
            genres=imdb['genres'],
            poster=imdb['poster'],
            plot=imdb['plot'],
            rating=imdb['rating'],
            url=imdb['url'],
            **locals()
        )
    else:
        mention_user = message.from_user.mention
        LAZY_MESSAGES = [
                "Hello {}, How are you?",
                "Come soon again please, {}.",
                "How is your day, {}?",
                "I'm Good and what about you, {}?",
                "Happy to see you, {}.",
                "Let's catch up soon, {}.",
                "Have a nice day, {}.",
                "Take care, {}.",
                "See you later, {}.",
                "Hope you're doing well, {}!",
                "Hey {}, it’s great to have you here!",
                "What’s new with you, {}?",
                "Wishing you an awesome day, {}!",
                "Keep smiling, {}.",
                "Missed you, {}! How’s everything?",
                "It’s always a pleasure talking to you, {}.",
                "You make my day brighter, {}.",
                "Stay safe and sound, {}!",
                "Can’t wait to hear from you again, {}.",
                "Cheers to you, {}! Have a lovely day.",
                "Hope you’re feeling fantastic today, {}!",
                "Hello there, {}! Always good to see you.",
                "Take it easy and enjoy your day, {}.",
                "Sending good vibes your way, {}!"
            ]
        random_message_template = random.choice(LAZY_MESSAGES)
        set_message = random_message_template.format(mention_user)

        cap = f"💃 {set_message}\n\n <b>⚡ Here is what i found for your query {search} 👇</b>"
    if imdb and imdb.get('poster'):
        try:
            z = await message.reply_photo(photo=imdb.get('poster'), caption=cap[:1024],
                                       reply_markup=InlineKeyboardMarkup(btn))
		
            await db.increment_search_count(search, lazyuser_id)
            if SELF_DELETE:
                await asyncio.sleep(SELF_DELETE_SECONDS)
                await z.delete()
                await message.delete()
        except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
            pic = imdb.get('poster')
            poster = pic.replace('.jpg', "._V1_UX360.jpg")

            m = await message.reply_photo(photo=poster, caption=cap[:1024], reply_markup=InlineKeyboardMarkup(btn))
            await db.increment_search_count(search, lazyuser_id)
            if SELF_DELETE:
                await asyncio.sleep(SELF_DELETE_SECONDS)
                await m.delete()
                await message.delete()

        except Exception as e:
            logger.exception(e)
            n = await message.reply_text(cap, reply_markup=InlineKeyboardMarkup(btn))
            #await db.increment_search_count(search, lazyuser_id)
	    
	    #if SELF_DELETE:
                #await asyncio.sleep(SELF_DELETE_SECONDS)
                #await n.delete()
                #await message.delete()
    else:
        
        # p = await message.reply_photo(photo=random.choice(PICS), caption=cap, reply_markup=InlineKeyboardMarkup(btn))
        p = await message.reply_text(cap, reply_markup=InlineKeyboardMarkup(btn))
        await db.increment_search_count(search, lazyuser_id)
        if SELF_DELETE:
            await asyncio.sleep(SELF_DELETE_SECONDS)
            await p.delete()
            await message.delete()
    if spoll:
        await msg.message.delete()
 
# Born to make history @LazyDeveloper !
async def advantage_spell_chok(message):
    mv_id = message.id
    search = message.text
    chat_id = message.chat.id
    settings = await get_settings(chat_id)
    query = re.sub(
        r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|br((o|u)h?)*|^h(e|a)?(l)*(o)*|mal(ayalam)?|t(h)?amil|file|that|find|und(o)*|kit(t(i|y)?)?o(w)?|thar(u)?(o)*w?|kittum(o)*|aya(k)*(um(o)*)?|full\smovie|any(one)|with\ssubtitle(s)?)",
        "", message.text, flags=re.IGNORECASE)
    query = query.strip() + " movie"
    try:
        movies = await get_poster(search, bulk=True)
    except:
        k = await message.reply(script.I_CUDNT.format(message.from_user.mention))
        await asyncio.sleep(60)
        await k.delete()
        try:
            await message.delete()
        except:
            pass
        return
    if not movies:
        google = search.replace(" ", "+")
        button = [[
            InlineKeyboardButton("🔍 ᴄʜᴇᴄᴋ sᴘᴇʟʟɪɴɢ ᴏɴ ɢᴏᴏɢʟᴇ 🔍", url=f"https://www.google.com/search?q={google}")
        ]]
        k = await message.reply_text(text=script.I_CUDNT.format(search), reply_markup=InlineKeyboardMarkup(button))
        await asyncio.sleep(120)
        await k.delete()
        try:
            await message.delete()
        except:
            pass
        return
    user = message.from_user.id if message.from_user else 0
    buttons = [[
        InlineKeyboardButton(text="🎬 "+movie.get('title'), callback_data=f"spol#{movie.movieID}#{user}")
    ]
        for movie in movies
    ]
    generated_link = f"https://google.com/search?q={quote(search)}"
    buttons.append([
        InlineKeyboardButton("🔍 ᴄʜᴇᴄᴋ sᴘᴇʟʟɪɴɢ ᴏɴ ɢᴏᴏɢʟᴇ 🔍", url=generated_link)
    ])
    buttons.append(
        [InlineKeyboardButton(text="🚮 ᴄʟᴏsᴇ 🧺", callback_data='close_data')]
    )
    d = await message.reply_text(text=script.CUDNT_FND.format(message.from_user.mention), reply_markup=InlineKeyboardMarkup(buttons), reply_to_message_id=message.id)
    await asyncio.sleep(120)
    await d.delete()
    try:
        await message.delete()
    except:
        pass


async def manual_filters(client, message, text=False):
    group_id = message.chat.id
    name = text or message.text
    reply_id = message.reply_to_message.id if message.reply_to_message else message.id
    keywords = await get_filters(group_id)
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            reply_text, btn, alert, fileid = await find_filter(group_id, keyword)

            if reply_text:
                reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")

            if btn is not None:
                try:
                    if fileid == "None":
                        if btn == "[]":
                            await client.send_message(group_id, reply_text, disable_web_page_preview=True)
                        else:
                            button = eval(btn)
                            await client.send_message(
                                group_id,
                                reply_text,
                                disable_web_page_preview=True,
                                reply_markup=InlineKeyboardMarkup(button),
                                reply_to_message_id=reply_id
                            )
                    elif btn == "[]":
                        await client.send_cached_media(
                            group_id,
                            fileid,
                            caption=reply_text or "",
                            reply_to_message_id=reply_id
                        )
                    else:
                        button = eval(btn)
                        await message.reply_cached_media(
                            fileid,
                            caption=reply_text or "",
                            reply_markup=InlineKeyboardMarkup(button),
                            reply_to_message_id=reply_id
                        )
                except Exception as e:
                    logger.exception(e)
                break
    else:
        return False


# seperator pattrerns for backup ❤ @LazyDeveloper
# ⦚   |⫶̊   |   |
