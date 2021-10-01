import configparser

blacklisted_names = ['tmi.twitch.tv', 'Welcome, GLHF', 'End of /NAMES list']
config_name = 'conf.ini'
server = 'irc.chat.twitch.tv'
port = 6667
address = (server, port)
config = configparser.ConfigParser()
config.read(config_name)