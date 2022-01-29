import configparser
import os

import pyfiglet

import utils

banner = pyfiglet.figlet_format('Chattercat', font='speed')
debug = 1
config_name = 'conf.ini'
server = 'irc.chat.twitch.tv'
port = 6667
address = (server, port)
config = configparser.ConfigParser()
if not os.path.exists(config_name):
    utils.cls()
    print(banner)
    utils.createConfig()
config.read(config_name)
blacklisted_symbols = ['#', '!', ':', '.']
bttv_emote_class_name = 'Emote_headerText__3r74d'
twitch_live_class_name = 'ScAnimatedNumber-sc-acnd2k-0 bHSmOZ'
emote_types = ['twitch','subscriber','ffz','ffz_channel','bttv','bttv_channel']