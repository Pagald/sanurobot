# 🚀 Global Public DNS Patch to prevent MongoDB SRV DNS Timeouts on Windows/Cloud
try:
    import dns.resolver
    dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
    dns.resolver.default_resolver.nameservers = ['8.8.8.8', '1.1.1.1', '8.8.4.4', '1.0.0.1']
except Exception:
    pass

import re
from os import getenv, environ
import logging
logging.basicConfig(
    format='%(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('log.txt'),
              logging.StreamHandler()],
    level=logging.INFO
)

id_pattern = re.compile(r'^.\d+$')
def is_enabled(value, default):
    if value.lower() in ["true", "yes", "1", "enable", "y"]:
        return True
    elif value.lower() in ["false", "no", "0", "disable", "n"]:
        return False
    else:
        return default

# Bot information *
SESSION = environ.get('SESSION', 'Media_search')
API_ID = environ.get("API_ID", "17319714")
API_HASH = environ.get("API_HASH", "4214385b4b215e55e69ae2746d3421b7")
BOT_TOKEN = environ.get("BOT_TOKEN", "8621562044:AAH-AmU-Lu2EYE1T9GL0bQ8FR2THt1_Rnjg") 
REDIS_URI = environ.get("REDIS_URI", "redis://default:pS1PiMTAbrZ6Eh1Isbk3qGlRYaHSs3Hx@powder-tin-lichen-38833.db.redis.io:14241")

# Bot settings
CACHE_TIME = int(environ.get('CACHE_TIME', 300))
USE_CAPTION_FILTER = bool(environ.get('USE_CAPTION_FILTER', False))
PRIME_LOGO = (environ.get('PRIME_LOGO', 'https://telegra.ph/file/ca18e2c794f4ea1c3135b.jpg'))
MAX_BUDDY_PER_PAGE = int(environ.get('MAX_BUDDY_PER_PAGE', 1))
MAX_TRANSACTION_PER_PAGE = int(environ.get('MAX_TRANSACTION_PER_PAGE', 1))

PICS = (environ.get('PICS', 'https://i.ibb.co/XrFqMH1f/photo-2026-07-21-01-00-50.jpg https://i.ibb.co/XrFqMH1f/photo-2026-07-21-01-00-50.jpg')).split()

# payment
QR_CODE_IMG = environ.get('QR_CODE_IMG','https://telegra.ph/file/ca18e2c794f4ea1c3135b.jpg')
UPI_ID = environ.get('UPI_ID', 'lazydeveloper@ybl')

# Admins, Channels & Users *
ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in environ.get('ADMINS', '5965340120 1132179847 5239277037').split()]
CHANNELS = [int(ch) if id_pattern.search(ch) else ch for ch in environ.get('CHANNELS', '-1002022048540').split()]

auth_users = [int(user) if id_pattern.search(user) else user for user in environ.get('AUTH_USERS', '').split()]
AUTH_USERS = (auth_users + ADMINS) if auth_users else []

auth_grp = environ.get('AUTH_GROUP')
AUTH_GROUPS = [int(ch) for ch in auth_grp.split()] if auth_grp else None

AUTH_CHANNEL = [int(cha) if id_pattern.search(cha) else cha for cha in environ.get('AUTH_CHANNEL', '').split()]
LAZY_DIVERTING_CHANNEL = int(environ.get('LAZY_DIVERTING_CHANNEL', '-1003854193310'))

# MongoDB information *
DATABASE_URI = environ.get('DATABASE_URI', "mongodb+srv://sanuu:sanuu@lazydeveloperr.qegotgx.mongodb.net/?appName=lazydeveloperr")
DATABASE_NAME = environ.get('DATABASE_NAME', "lazydeveloperr")
COLLECTION_NAME = environ.get('COLLECTION_NAME', 'Lazy_files')

# LOG CHANNELS *
LOG_CHANNEL = int(environ.get('LOG_CHANNEL', '-1002196135580'))
STREAM_LOGS = int(environ.get('STREAM_LOGS', '-1002196135580'))
LAZY_GROUP_LOGS = int(environ.get('LAZY_GROUP_LOGS', '-1002196135580'))
REQ_CHANNEL = int(environ.get('REQ_CHANNEL', '-1002196135580'))
PRIME_MEMBERS_LOGS = int(environ.get('PRIME_MEMBERS_LOGS', '-1002196135580'))

# PREMIUM ACCESS *
lazydownloaders = [int(lazydownloaders) if id_pattern.search(lazydownloaders) else lazydownloaders for lazydownloaders in environ.get('PRIME_DOWNLOADERS', '5965340120 6126812037').split()]
PRIME_USERS = (lazydownloaders) if lazydownloaders else []
lazy_renamers = [int(lazrenamers) if id_pattern.search(lazrenamers) else lazrenamers for lazrenamers in environ.get('LAZY_RENAMERS', '5965340120 6126812037').split()]
LAZY_RENAMERS = (lazy_renamers + ADMINS) if lazy_renamers else []
LZURL_PRIME_USERS = [int(lazyurlers) if id_pattern.search(lazyurlers) else lazyurlers for lazyurlers in environ.get('LZURL_PRIME_USERS', '5965340120 6126812037').split()]

# Others
TUTORIAL = environ.get('TUTORIAL', 'https://t.me/real_moviesadda6')
IS_TUTORIAL = bool(environ.get('IS_TUTORIAL', True))
SUPPORT_CHAT = environ.get('SUPPORT_CHAT', '+EpZuHPEWXNswOGY8')
P_TTI_SHOW_OFF = is_enabled((environ.get('P_TTI_SHOW_OFF', "True")), False)
IMDB = is_enabled((environ.get('IMDB', "False")), True)
SINGLE_BUTTON = is_enabled((environ.get('SINGLE_BUTTON', "True")), False)
CUSTOM_FILE_CAPTION = environ.get("CUSTOM_FILE_CAPTION", "⚡<b>File uploaded by [SANU MOVIES02](https://t.me/SANUMovies02)</b>⚡\n\n📂<b>File Name:</b> ⪧ {file_caption}\n❤🔻")
BATCH_FILE_CAPTION = environ.get("BATCH_FILE_CAPTION", CUSTOM_FILE_CAPTION)

IMDB_TEMPLATE = environ.get("IMDB_TEMPLATE", "<a href={url}>{title} {year}</a>\n❤You searched: {query}")

LONG_IMDB_DESCRIPTION = is_enabled(environ.get("LONG_IMDB_DESCRIPTION", "False"), False)
SPELL_CHECK_REPLY = is_enabled(environ.get("SPELL_CHECK_REPLY", "False"), False)
MAX_LIST_ELM = environ.get("MAX_LIST_ELM", None)
INDEX_REQ_CHANNEL = int(environ.get('INDEX_REQ_CHANNEL', LOG_CHANNEL))
FILE_STORE_CHANNEL = [int(ch) for ch in (environ.get('FILE_STORE_CHANNEL', '')).split()]
MELCOW_NEW_USERS = is_enabled((environ.get('MELCOW_NEW_USERS', "True")), True)
PROTECT_CONTENT = is_enabled((environ.get('PROTECT_CONTENT', "False")), False)
PUBLIC_FILE_STORE = is_enabled((environ.get('PUBLIC_FILE_STORE', "False")), False)

# LazyRenamer Configs
FLOOD = int(environ.get("FLOOD", "10"))
LAZY_MODE = bool(environ.get("LAZY_MODE", False))

# Requested Content template variables --- 
ADMIN_USRNM = environ.get('ADMIN_USRNM','Husen751')
MAIN_CHANNEL_USRNM = environ.get('MAIN_CHANNEL_USRNM','SANUMovies02')
DEV_CHANNEL_USRNM = environ.get('DEV_CHANNEL_USRNM','SANUMovies02')
LAZY_YT_HANDLE = environ.get('LAZY_YT_HANDLE','LayDeveloperr')
MOVIE_GROUP_USERNAME = environ.get('MOVIE_GROUP_USERNAME', "WebSeries_Movie_Request_Groups")

# Url Shortner
URL_MODE = is_enabled((environ.get("URL_MODE","True")), False)
URL_SHORTENR_WEBSITE = environ.get('URL_SHORTENR_WEBSITE', 'atglinks.com')
URL_SHORTNER_WEBSITE_API = environ.get('URL_SHORTNER_WEBSITE_API', '72a7f0131e5e657e37cf7e2a9e928a616b671cf5')

IS_LAZYUSER_VERIFICATION = is_enabled((environ.get("IS_LAZYUSER_VERIFICATION","True")), False)
LAZY_SHORTNER_URL = environ.get('LAZY_SHORTNER_URL', 'atglinks.com')
LAZY_SHORTNER_API = environ.get('LAZY_SHORTNER_API', '72a7f0131e5e657e37cf7e2a9e928a616b671cf5')

lazy_groups = environ.get('LAZY_GROUPS','-1002127686518')
LAZY_GROUPS = [int(lazy_groups) for lazy_groups in lazy_groups.split()] if lazy_groups else None
my_users = [int(my_users) if id_pattern.search(my_users) else my_users for my_users in environ.get('MY_USERS', '5965340120 6126812037').split()]
MY_USERS = (my_users) if my_users else []

# Online Stream and Download
PORT = int(environ.get('PORT', 8080))
NO_PORT = bool(environ.get('NO_PORT', False))
APP_NAME = None
if 'DYNO' in environ:
    ON_HEROKU = True
    APP_NAME = environ.get('APP_NAME')
else:
    ON_HEROKU = False
BIND_ADRESS = str(getenv('WEB_SERVER_BIND_ADDRESS', '0.0.0.0'))
FQDN = str(getenv('FQDN', BIND_ADRESS)) if not ON_HEROKU or getenv('FQDN') else APP_NAME+'.herokuapp.com'
URL = "https://{}/".format(FQDN) if ON_HEROKU or NO_PORT else \
    "http://{}:{}/".format(FQDN, PORT)
SLEEP_THRESHOLD = int(environ.get('SLEEP_THRESHOLD', '60'))
WORKERS = int(environ.get('WORKERS', '8'))
SESSION_NAME = str(environ.get('SESSION_NAME', 'LazyBot'))
MULTI_CLIENT = False
name = str(environ.get('name', 'LazyPrincess'))
PING_INTERVAL = int(environ.get("PING_INTERVAL", "1200"))
if 'DYNO' in environ:
    ON_HEROKU = True
    APP_NAME = str(getenv('APP_NAME'))
else:
    ON_HEROKU = False
HAS_SSL=bool(getenv('HAS_SSL',False))
if HAS_SSL:
    URL = "https://{}/".format(FQDN)
else:
    URL = "http://{}/".format(FQDN)
BANNED_CHANNELS = list(set(int(x) for x in str(getenv("BANNED_CHANNELS", "-1001987654567")).split())) 
OWNER_USERNAME = "LazyDeveloper"

templist = []
channel_ids_str = " ".join(map(str, templist))
LAZYDEVELOPER_CHANNELS = [int(c) for c in channel_ids_str.split()]

lazydownloaders = [int(lazydownloaders) if id_pattern.search(lazydownloaders) else lazydownloaders for lazydownloaders in environ.get('PRIME_DOWNLOADERS', '').split()]
PRIME_DOWNLOADERS = (lazydownloaders) if lazydownloaders else []

# URL UPLOADING
BANNED_USERS = set(int(x) for x in environ.get("BANNED_USERS", "").split())
DOWNLOAD_LOCATION = "./DOWNLOADS"
MAX_FILE_SIZE = 4194304000
TG_MAX_FILE_SIZE = 4194304000
FREE_USER_MAX_FILE_SIZE = 4194304000
CHUNK_SIZE = int(environ.get("CHUNK_SIZE", 128))
HTTP_PROXY = environ.get("HTTP_PROXY", "")
OUO_IO_API_KEY = ""
MAX_MESSAGE_LENGTH = 4096
PROCESS_MAX_TIMEOUT = 0
DEF_WATER_MARK_FILE = ""
LOGGER = logging

LANGUAGES = ["hindi", "hin", "english", "eng", "korean", "kor", "urdu", "urd","chinese","chin","tamil", "tam", "malayalam", "mal",  "telugu", "tel", "kannada", "kan"]
SEASONS = ["season 1" , "season 2" , "season 3" , "season 4", "season 5" , "season 6" , "season 7" , "season 8" , "season 9" , "season 10"]
QUALITIES = ["360P", "", "480P", "", "720P", "", "1080P", "", "1440P", "", "2160P", ""]

MAX_LAZY_BTNS = int(environ.get("MAX_LAZY_BTNS", "6"))
MAX_BTN = is_enabled((environ.get('MAX_BTN', "True")), True)

SELF_DELETE_SECONDS = int(environ.get('SELF_DELETE_SECONDS', 300))
SELF_DELETE = environ.get('SELF_DELETE', True)
if SELF_DELETE == "True":
    SELF_DELETE = True

DISCUSSION_TITLE = "Click Here"
DISCUSSION_CHAT_USRNM = "Discusss_Here"

DOWNLOAD_TEXT_NAME = "📥 HOW TO DOWNLOAD 📥"
DOWNLOAD_TEXT_URL = "https://t.me/+tgPf04FXMOllMWVl"

CAPTION_BUTTON = "Get Updates"
CAPTION_BUTTON_URL = "https://t.me/+tgPf04FXMOllMWVl"

MAX_SUBSCRIPTION_TIME = int(environ.get('MAX_SUBSCRIPTION_TIME', '24'))
FILE_AUTO_DELETE_TIME = int(environ.get('FILE_AUTO_DELETE_TIME', '300'))
GROUP_MSG_DELETE_TIME = int(environ.get('GROUP_MSG_DELETE_TIME', '300'))
DONATION_LINK = environ.get("DONATION_LINK","https://buymeacoffee.com/lazyDeveloperr")
CHANNELS_PER_PAGE = 8
DAILY_LIMIT = 2

MAX_SEASONS_PER_PAGE = 12
MAX_EPISODES_LIST = 12
MAX_EPISODES_PER_PAGE = 6

MAX_LANG_PER_PAGE = 10
MAX_LANG_FILE_PER_PAGE = 6

MAX_QUAL_PER_PAGE = 10
MAX_QUAL_FILE_PER_PAGE = 6

CHANNEL_NAME = "Hidden Xman"
BACK_BTN_TXT = "◀️"
NEXT_BTN_TXT = "▶️"

LAZYCONTAINER = {}

LOG_STR = "🚀Current Cusomized Configurations are:-\n"
LOG_STR += ("𓆩ཫ⚙ཀ𓆪 IMDB Results are enabled, Bot will be showing imdb details for you queries.\n" if IMDB else "IMBD Results are disabled.\n")
LOG_STR += ("𓆩ཫ⚙ཀ𓆪 P_TTI_SHOW_OFF found , Users will be redirected to send /start to Bot PM instead of sending file file directly\n" if P_TTI_SHOW_OFF else "P_TTI_SHOW_OFF is disabled files will be send in PM, instead of sending start.\n")
LOG_STR += ("𓆩ཫ⚙ཀ𓆪 SINGLE_BUTTON is Found, filename and files size will be shown in a single button instead of two separate buttons\n" if SINGLE_BUTTON else "SINGLE_BUTTON is disabled , filename and file_sixe will be shown as different buttons\n")
LOG_STR += (f"𓆩ཫ⚙ཀ𓆪 CUSTOM_FILE_CAPTION enabled with value {CUSTOM_FILE_CAPTION}, your files will be send along with this customized caption.\n" if CUSTOM_FILE_CAPTION else "No CUSTOM_FILE_CAPTION Found, Default captions of file will be used.\n")
LOG_STR += ("𓆩ཫ⚙ཀ𓆪 Long IMDB storyline enabled." if LONG_IMDB_DESCRIPTION else "LONG_IMDB_DESCRIPTION is disabled , Plot will be shorter.\n")
LOG_STR += ("𓆩ཫ⚙ཀ𓆪 A.I Spell Check Mode Is Enabled, bot will be suggesting related movies if movie not found\n" if SPELL_CHECK_REPLY else "SPELL_CHECK_REPLY Mode disabled\n")
LOG_STR += (f"𓆩ཫ⚙ཀ𓆪 MAX_LIST_ELM Found, long list will be shortened to first {MAX_LIST_ELM} elements\n" if MAX_LIST_ELM else "Full List of casts and crew will be shown in imdb template, restrict them by adding a value to MAX_LIST_ELM\n")
LOG_STR += f"𓆩ཫ⚙ཀ𓆪 Your current IMDB template is\n:  {IMDB_TEMPLATE}"
