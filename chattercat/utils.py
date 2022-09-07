import configparser
import os
import time

import requests

import chattercat.constants as constants
import chattercat.twitch as twitch

COLORS = constants.COLORS
CONFIG_SECTIONS = constants.CONFIG_SECTIONS
DB_VARIABLES = constants.DB_VARIABLES
DIRS = constants.DIRS
ERROR_MESSAGES = constants.ERROR_MESSAGES
TWITCH_VARIABLES = constants.TWITCH_VARIABLES

class Config:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read(constants.CONFIG_NAME)
        self.host= self.config[CONFIG_SECTIONS['db']][DB_VARIABLES['host']]
        self.user= self.config[CONFIG_SECTIONS['db']][DB_VARIABLES['user']]
        self.password = self.config[CONFIG_SECTIONS['db']][DB_VARIABLES['password']]
        self.nickname = self.config[CONFIG_SECTIONS['twitch']][TWITCH_VARIABLES['nickname']]
        self.token = self.config[CONFIG_SECTIONS['twitch']][TWITCH_VARIABLES['token']]
        self.secret_key = self.config[CONFIG_SECTIONS['twitch']][TWITCH_VARIABLES['secret_key']]

class Response:
    def __init__(self, channel_name, response):
        self.response = response
        self.channel_name = channel_name
        self.username = self.parseUsername()
        self.message = self.parseMessage()
        if(self.username == self.message):
            self.username = self.parseIncompleteResponse()

    def parseIncompleteResponse(self):
        if('PRIVMSG' in self.response):
            if('@' in self.response.split('PRIVMSG')[0]):
                return self.response.split("PRIVMSG")[0].split("@")[1].split(".")[0]
        return None

    def parseUsername(self):
        try:
            return self.response.split('!')[0].split(':')[1]
        except:
            return None

    def parseMessage(self):
        try:
            return self.response.split(f'#{self.channel_name} :')[1]
        except:
            return None

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

def createAndDownloadGlobalEmotes():
    try:
        if not os.path.exists(DIRS['emotes']):
            os.mkdir(DIRS['emotes'])
        os.mkdir(DIRS['twitch'])
    except:
        printError(None, ERROR_MESSAGES['directory'])
    downloadGlobalEmotes()

def downloadFile(url, fileName):
    r = requests.get(url)
    if not os.path.exists(fileName):
        with open(fileName, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024): 
                if chunk:
                    f.write(chunk)
    return None

def downloadGlobalEmotes():
    printInfo(None, constants.STATUS_MESSAGES['global'])
    emotes = twitch.getTwitchEmotes()
    counter = 0
    for emote in emotes:
        for character in constants.BAD_FILE_CHARS:
            if character in emote.code:
                emote.code = emote.code.replace(character, str(counter))
                counter += 1
        filename = f'{DIRS["twitch"]}/{emote.code}-{emote.id}.png'
        downloadFile(emote.url, filename)
        counter = 0

def elapsedTime(start):
    return (time.time() - start) / 60

def getDate():
    cur = time.gmtime()
    mon = '0' if cur.tm_mon < 10 else ''
    day = '0' if cur.tm_mday < 10 else ''
    return f'{str(cur.tm_year)}-{mon}{str(cur.tm_mon)}-{day}{str(cur.tm_mday)}'

def getDateTime(sys=False):
    cur = time.localtime() if sys else time.gmtime()
    mon = '0' if cur.tm_mon < 10 else ''
    day = '0' if cur.tm_mday < 10 else ''
    hour = '0' if cur.tm_hour < 10 else ''
    min = '0' if cur.tm_min < 10 else ''
    sec = '0' if cur.tm_sec < 10 else ''
    return f'{str(cur.tm_year)}-{mon}{str(cur.tm_mon)}-{day}{str(cur.tm_mday)} {hour}{str(cur.tm_hour)}:{min}{str(cur.tm_min)}:{sec}{str(cur.tm_sec)}'

def getIndices(list, text):
    indices = []
    for i in range(0, len(list)):
        if text in list[i]:
            indices.append(i)
    return indices

def getStreamNames():
    streams = []
    file = open(constants.STREAMS, 'r')
    for stream in file:
        streams.append(stream.replace('\n',''))
    return streams

def removeSymbolsFromName(emote_name):
    counter = 0
    for character in constants.BAD_FILE_CHARS:
        if character in emote_name:
            emote_name = emote_name.replace(character, str(counter))
            counter += 1
    return emote_name
            
def parseMessageEmotes(channel_emotes, message):
    if(type(message) == list):
        return []
    words = message.split(' ')
    parsed_emotes = []
    for word in words:
        if word in channel_emotes and word not in parsed_emotes:
            parsed_emotes.append(word)
    return parsed_emotes

def printBanner():
    cls()
    print(f'\n{constants.BANNER}')

def printError(channel_name, text):
    print(f'[{COLORS["bold_blue"]}{getDateTime(True)}{COLORS["clear"]}] [{COLORS["bold_purple"]}{channel_name if(channel_name is not None) else "Chattercat"}{COLORS["clear"]}] [{COLORS["hi_red"]}ERROR{COLORS["clear"]}] {text}')

def printInfo(channel_name, text):
    print(f'[{COLORS["bold_blue"]}{getDateTime(True)}{COLORS["clear"]}] [{COLORS["bold_purple"]}{channel_name if(channel_name is not None) else "Chattercat"}{COLORS["clear"]}] [{COLORS["hi_green"]}INFO{COLORS["clear"]}] {text}')

def statusMessage(channel_name, online=True):
    return f'{channel_name} just went live!' if online else f'{channel_name} is now offline.'