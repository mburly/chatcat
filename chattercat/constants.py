import pyfiglet

CLIENT_ID = 'hodl2vsgr34qf7b5kppu7y3669rot7'
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
                     'secret_key':'secret_key' }
DIRS = { 'emotes':'emotes', 
         'twitch':'emotes/twitch', 
         'bttv':'emotes/bttv', 
         'ffz':'emotes/ffz' }
API_URLS = { 'twitch':'https://api.twitch.tv/helix',
             'ffz':'https://api.frankerfacez.com/v1',
             'bttv':'https://api.betterttv.net/3/cached' }
CDN_URLS = { 'twitch':'https://static-cdn.jtvnw.net/emoticons/v2',
             'ffz':'https://cdn.frankerfacez.com/emote',
             'bttv':'https://cdn.betterttv.net/emote' }
OAUTH_URL = 'https://id.twitch.tv/oauth2'
SERVER_URL = 'tmi.twitch.tv'
COLORS = { 'clear':'\033[0m',
           'red':'\033[0;31m',
           'bold_blue':'\033[1;34m',
           'bold_purple':'\033[1;35m',
           'hi_green':'\033[0;92m',
           'hi_red':'\033[0;91m' }
BANNER = f'{COLORS["bold_purple"]}{pyfiglet.figlet_format("Chattercat", font="speed")}{COLORS["clear"]}'
VERSION = '1.0'
EMOTE_TYPES = ['twitch','subscriber','ffz','ffz_channel','bttv','bttv_channel']
DEBUG_MESSAGES = { 'set_emote':'Setting emote:',
                   'inactive':'now inactive.',
                   'reactivated':'now reactivated.' }
ERROR_MESSAGES = { 'host':'Unable to connect to host. Likely lost internet connection.',
                   'channel':'Channel not found.',
                   'database':'Unable to connect to database.',
                   'directory':'Unable to create emote directories.',
                   'offline':'Stream offline. Please try another channel or try again later.',
                   'secret_key':'Bad secret key. Please provide the appropriate secret key in the configuration file.',
                   'connection':'No internet connection found. Please try again.',
                   'no_streams':'No streams provided. Please add at least one channel to streams.txt' }
STATUS_MESSAGES = { 'downloading':'Downloading channel emotes...',
                    'global':'Downloading global emotes...',
                    'updates':'Checking for emote updates...',
                    'updates_complete':'Emote update complete.',
                    'set_emote':'Setting emote:',
                    'inactive':'now inactive.',
                    'reactivated':'now reactivated.' }