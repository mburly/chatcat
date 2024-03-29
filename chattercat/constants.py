import pyfiglet

CONFIG_NAME = 'conf.ini'
STREAMS = 'streams.txt'
SERVER = 'irc.chat.twitch.tv'
PORT = 6667
ADDRESS = (SERVER, PORT)
BAD_FILE_CHARS = ['\\','/',':','*','?','"','<','>','|']
CONFIG_SECTIONS = { 'db':'db',
                    'twitch':'twitch' }
DB_VARIABLES = { 'host':'host',
                 'user':'user',
                 'password':'password' }
TWITCH_VARIABLES = { 'nickname':'nickname',
                     'token':'token',
                     'secret_key':'secret_key',
                     'client_id':'client_id' }
DIRS = { 'emotes':'emotes', 
         'twitch':'emotes/twitch', 
         'bttv':'emotes/bttv', 
         'ffz':'emotes/ffz',
         'emotes_download':'chattercat-front/emotes', 
         'twitch_download':'chattercat-front/emotes/twitch', 
         'bttv_download':'chattercat-front/emotes/bttv', 
         'ffz_download':'chattercat-front/emotes/ffz',
         'pictures':'chattercat-front/pictures',
         'pictures_archive':'chattercat-front/pictures/archive' }
API_URLS = { 'twitch':'https://api.twitch.tv/helix',
             'ffz':'https://api.frankerfacez.com/v1',
             'bttv':'https://api.betterttv.net/3/cached' }
CDN_URLS = { 'twitch':'https://static-cdn.jtvnw.net/emoticons/v2',
             'ffz':'https://cdn.frankerfacez.com/emote',
             'bttv':'https://cdn.betterttv.net/emote' }
OAUTH_URL = 'https://id.twitch.tv/oauth2'
SERVER_URL = 'tmi.twitch.tv'
COLORS = { 'clear':'\033[0m',
           'bold_blue':'\033[1;34m',
           'bold_purple':'\033[1;35m',
           'hi_green':'\033[0;92m',
           'hi_red':'\033[0;91m' }
BANNER = f'{COLORS["bold_purple"]}{pyfiglet.figlet_format("Chattercat", font="speed")}{COLORS["clear"]}'
VERSION = '1.1'
EMOTE_TYPES = ['twitch','subscriber','ffz','ffz_channel','bttv','bttv_channel']
DEBUG_MESSAGES = { 'set_emote':'Setting emote:',
                   'inactive':'now inactive.',
                   'reactivated':'now reactivated.' }
ERROR_MESSAGES = { 'host':'Unable to connect to host. Likely lost internet connection.',
                   'channel':'Channel not found.',
                   'database':'Unable to connect to database.',
                   'directory':'Unable to create emote directories.',
                   'offline':'Stream offline. Please try another channel or try again later.',
                   'config':'Bad value(s) provided in the configuration file. Please check and update config.ini.',
                   'connection':'No internet connection found. Please try again.',
                   'no_streams':'No streams provided. Please add at least one channel to streams.txt' }
STATUS_MESSAGES = { 'downloading':'Downloading channel emotes...',
                    'updates':'Checking for updates...',
                    'updates_complete':'Update complete.',
                    'set_emote':'Setting emote:',
                    'inactive':'now inactive.',
                    'reactivated':'now reactivated.' }
TIMERS = { 'sleep':15,
           'live':1,
           'socket':5 }
ADMIN_DB_NAME = 'cc_housekeeping'