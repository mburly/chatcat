import os

import pyfiglet

banner = pyfiglet.figlet_format('Chattercat', font='speed')
debug = 0
config_name = 'conf.ini'
server = 'irc.chat.twitch.tv'
port = 6667
address = (server, port)
bad_file_chars = ['\\','/',':','*','?','"','<','>','|']
blacklisted_symbols = ['#', '!', ':', '.']
config_sections = ['db', 'twitch', 'options']
db_variables = ['host', 'user', 'password']
twitch_variables = ['nickname', 'token']
options_variables = ['download']
dirs = ['emotes', 'logs']
bttv_emote_class_name = 'Emote_headerText__3r74d'
twitch_live_class_name = 'ScAnimatedNumber-sc-acnd2k-0 bHSmOZ'
main_menu = '[1] Enter channel name\n[2] Options\n[3] Exit'
options_menu = '[1] Download settings\n[2] Back'
download_options_menu = 'Download emotes to chatcat folder?\n[1] Yes *DEFAULT*\n[2] No'
version = 'vDEV1'
emote_types = ['twitch','subscriber','ffz','ffz_channel','bttv','bttv_channel']
debug_messages = ['Checking if offline with counter =', 'Detected online. Counter now =', 'Detected offline. Counter now =',
'Stream ended. Now ending session...', 'Entering update_emotes function for source =', 'Setting emote:', 'now inactive.',
'now reactivated.']
error_messages = ['Error fetching stream title. Still trying...', 'Unable to connect to host. Likely lost internet connection.',
'Channel not found on FrankerFaceZ API.']
input_messages = ['Enter hostname (default is typically localhost):', 'Enter DB account username:', 'Enter DB account password:',
'Enter your twitch username:', 'Please visit the URL \033[4;37mhttps://twitchapps.com/tmi/\033[0m and enter the token after pressing Connect:',
'Enter channel name:', 'Please make a selection:']
status_messages = ['Getting Twitch emotes...', 'Getting Subscriber emotes...', 'Getting FFZ Global emotes...',
'Getting FFZ Channel emotes...', 'Getting BTTV Global emotes...', 'Getting BTTV Channel emotes...', 'Downloading emotes...']