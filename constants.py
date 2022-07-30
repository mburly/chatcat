import pyfiglet

CLIENT_ID = 'hodl2vsgr34qf7b5kppu7y3669rot7'
CONFIG_NAME = 'conf.ini'
SERVER = 'irc.chat.twitch.tv'
PORT = 6667
ADDRESS = (SERVER, PORT)
BAD_FILE_CHARS = ['\\','/',':','*','?','"','<','>','|']
BAD_USERNAMES = [' ', '.', 'GLHF']
CONFIG_SECTIONS = ['db', 'twitch', 'options']
DB_VARIABLES = ['host', 'user', 'password']
TWITCH_VARIABLES = ['nickname', 'token', 'secret_key']
OPTIONS_VARIABLES = ['download', 'debug']
DIRS = { 'emotes':'emotes', 
         'global':'global',
         'global_emotes':'emotes/global' }
API_URLS = { 'twitch':'https://api.twitch.tv/helix',
             'ffz':'https://api.frankerfacez.com/v1',
             'bttv':'https://api.betterttv.net/3/cached' }
CDN_URLS = { 'twitch':'https://static-cdn.jtvnw.net/emoticons/v2',
             'ffz':'https://cdn.frankerfacez.com/emote',
             'bttv':'https://cdn.betterttv.net/emote' }
OAUTH_URL = 'https://id.twitch.tv/oauth2'
SERVER_URL = 'tmi.twitch.tv'
LABEL_TITLES = ['DATABASE INFORMATION', 'TWITCH INFORMATION', 'OPTIONS']
COLORS = { 'clear':'\033[0m',
           'red':'\033[0;31m',
           'green':'\033[0;32m',
           'bg_blue':'\033[44m',
           'bg_green':'\033[42m',
           'bg_pink':'\033[45m',
           'bold_blue':'\033[1;34m',
           'bold_green':'\033[1;32m',
           'bold_purple':'\033[1;35m',
           'bold_red':'\033[1;31m',
           'bold_yellow':'\033[1;33m',
           'hi_blue':'\033[0;94m',
           'hi_green':'\033[0;92m',
           'hi_red':'\033[0;91m' }
USERNAME_COLORS = { 'red':'\033[0;31m',
                    'green':'\033[0;32m',
                    'yellow':'\033[0;33m',
                    'purple':'\033[0;35m',
                    'cyan':'\033[0;36m' }
BANNER = f'{COLORS["bold_purple"]}{pyfiglet.figlet_format("Chattercat", font="speed")}{COLORS["clear"]}'
VERSION = 'DEV2'
EMOTE_TYPES = ['twitch','subscriber','ffz','ffz_channel','bttv','bttv_channel']
DEBUG_MESSAGES = { 'check_offline':'Checking if offline with counter =',
                   'detect_online':'Detected online. Counter now =',
                   'detect_offline':'Detected offline. Counter now =',
                   'stream_end':'Stream ended. Now ending session...',
                   'update_emotes':'Entering update_emotes function for source =',
                   'set_emote':'Setting emote:',
                   'inactive':'now inactive.',
                   'reactivated':'now reactivated.' }
ERROR_MESSAGES = { 'host':'Unable to connect to host. Likely lost internet connection.',
                   'channel':'Channel not found. Press enter to return to the main menu.',
                   'selection':'Invalid selection. Press enter to return to the previous menu.',
                   'database':'Unable to connect to database. Press enter to return to the main menu.',
                   'no_databases':'No databases found! Press enter to go back.',
                   'directory':'Unable to create emote directories.',
                   'offline':'Stream offline. Please try another channel or try again later.',
                   'client_id':'Bad Client ID. Please provide a different Client ID in the configuration file.',
                   'connection':'No internet connection found. Please try again.' }
INPUT_MESSAGES = { 'host':'Enter hostname (default is typically localhost):',
                   'db_user':'Enter DB account username (default is typically root):',
                   'db_pass':'Enter DB account password:',
                   'twitch_user':'Enter your twitch username:',
                   'oauth':'Please visit the URL \033[4;37mhttps://twitchapps.com/tmi/\033[0m and enter the token after pressing Connect:',
                   'secret':'Enter the secret key:' }
STATUS_MESSAGES = { 'downloading':'Downloading channel emotes...',
                    'global':'Downloading global emotes...',
                    'updates':'Checking for emote updates...',
                    'updates_complete':'Emote update complete.' }