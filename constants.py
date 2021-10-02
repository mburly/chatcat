import configparser
import os

import db

config_name = 'conf.ini'
server = 'irc.chat.twitch.tv'
port = 6667
address = (server, port)
if not os.path.exists(config_name):
    db.createConfig()
config = configparser.ConfigParser()
config.read(config_name)
blacklisted_names = ['tmi.twitch.tv', 'Welcome, GLHF', 'End of /NAMES list', config['twitch']['nickname']]