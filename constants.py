import os

import pyfiglet

banner = pyfiglet.figlet_format('Chattercat', font='speed')
debug = 1
config_name = 'conf.ini'
server = 'irc.chat.twitch.tv'
port = 6667
address = (server, port)
bad_file_chars = ['\\','/',':','*','?','"','<','>','|']
blacklisted_symbols = ['#', '!', ':', '.']
dirs = ['emotes', 'logs']
bttv_emote_class_name = 'Emote_headerText__3r74d'
twitch_live_class_name = 'ScAnimatedNumber-sc-acnd2k-0 bHSmOZ'
emote_types = ['twitch','subscriber','ffz','ffz_channel','bttv','bttv_channel']
debug_messages = ['Checking if offline with counter =', 'Detected online. Counter now =', 'Detected offline. Counter now =',
'Stream ended. Now ending session...', 'Entering update_emotes function for source =', 'Setting emote:', 'now inactive.',
'now reactivated.']
error_messages = ['Error fetching stream title. Still trying...', 'Unable to connect to host. Likely lost internet connection.',
'Channel not found on FrankerFaceZ API.']
input_messages = ['Enter hostname (default is typically localhost):', 'Enter DB account username:', 'Enter DB account password:',
'Enter your twitch username:', 'Please visit the URL \033[4;37mhttps://twitchapps.com/tmi/\033[0m and enter the token after pressing Connect: ',
'Enter channel name:']
status_messages = ['Getting Twitch emotes...', 'Getting Subscriber emotes...', 'Getting FFZ Global emotes...',
'Getting FFZ Channel emotes...', 'Getting BTTV Global emotes...', 'Getting BTTV Channel emotes...', 'Downloading emotes...']