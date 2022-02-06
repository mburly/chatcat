import pyfiglet

banner = pyfiglet.figlet_format('Chattercat', font='speed')
config_name = 'conf.ini'
server = 'irc.chat.twitch.tv'
port = 6667
address = (server, port)
bad_file_chars = ['\\','/',':','*','?','"','<','>','|']
blacklisted_symbols = ['#', '!', ':', '.']
config_sections = ['db', 'twitch', 'options']
db_variables = ['host', 'user', 'password']
twitch_variables = ['nickname', 'token']
options_variables = ['download', 'debug']
dirs = ['emotes', 'logs']
bttv_emote_class_name = 'Emote_headerText__3r74d'
twitch_live_class_name = 'ScAnimatedNumber-sc-acnd2k-0 bHSmOZ'
unknown_stream_title = 'Unable to get stream title.'
server_url = 'tmi.twitch.tv'
label_titles = ['DATABASE INFORMATION', 'TWITCH INFORMATION', 'OPTIONS']
bg_colors = {'pink':'\033[45m',
          'green':'\033[42m',
          'blue':'\033[44m'}
bold_colors = {'red':'\033[1;31m',
               'green':'\033[1;32m',
               'yellow':'\033[1;33m',
               'blue':'\033[1;34m',
               'purple':'\033[1;35m'}
colors = {'clear':'\033[0m',
          'red':'\033[0;31m',
          'green':'\033[0;32m',
          'yellow':'\033[0;33m'}
high_int_colors = {
            'red':'\033[0;91m',
            'green':'\033[0;92m',
            'blue':'\033[0;94m'}
main_menu = '[1] Enter channel name\n[2] Options\n[3] Exit'
options_menu = '[1] Download settings\n[2] Delete databases\n[3] Set debug mode\n[4] Back'
download_options_menu = 'Download emotes to chatcat folder?\n[1] Yes *DEFAULT*\n[2] No'
database_options_menu = 'Please select which databases to delete. They are NOT recoverable.'
debug_options_menu = '[1] On\n[2] Off'
version = 'DEV1'
emote_types = ['twitch','subscriber','ffz','ffz_channel','bttv','bttv_channel']
log_errors = ['TIMEOUT/OVERFLOW ERROR']
debug_messages = ['Checking if offline with counter =', 'Detected online. Counter now =', 'Detected offline. Counter now =',
'Stream ended. Now ending session...', 'Entering update_emotes function for source =', 'Setting emote:', 'now inactive.',
'now reactivated.']
error_messages = ['Error fetching stream title. Still trying...', 'Unable to connect to host. Likely lost internet connection.',
'Channel not found on FrankerFaceZ API. Press any key to return to the previous menu.', 'Invalid selection. Press any key to return to the previous menu.']
input_messages = ['Enter hostname (default is typically localhost):', 'Enter DB account username:', 'Enter DB account password:',
'Enter your twitch username:', 'Please visit the URL \033[4;37mhttps://twitchapps.com/tmi/\033[0m and enter the token after pressing Connect:',
'Enter channel name:', 'Please make a selection:']
status_messages = ['Getting Twitch emotes...', 'Getting Subscriber emotes...', 'Getting FFZ Global emotes...',
'Getting FFZ Channel emotes...', 'Getting BTTV Global emotes...', 'Getting BTTV Channel emotes...', 'Downloading emotes...', 'No databases found! Press any key to go back.']