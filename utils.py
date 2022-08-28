import configparser
import os
import socket
import time

import requests

import constants
import db
import twitch

COLORS = constants.COLORS
CONFIG_NAME = constants.CONFIG_NAME
CONFIG_SECTIONS = constants.CONFIG_SECTIONS
DIRS = constants.DIRS
TWITCH_VARIABLES = constants.TWITCH_VARIABLES
ERROR_MESSAGES = constants.ERROR_MESSAGES

class Chattercat:
    executing = True
    running = True
    def __init__(self, channel_name):
        self.channel_name = channel_name.lower()
        self.live = twitch.isStreamLive(self.channel_name)
        try:
            while(self.executing):
                if(self.live):
                    if(self.start() is None):
                        return -1
                    while(self.running):
                        self.run()
                    self.end()
                else:
                    self.live = twitch.isStreamLive(self.channel_name)
                    time.sleep(15)
        except KeyboardInterrupt:
            return None

    def run(self):
        self.sock = self.startSocket()
        self.live_clock = time.time()
        self.socket_clock = time.time()
        self.channel_emotes = self.db.getChannelActiveEmotes()
        try:
            while self.running:
                self.resp = ''
                if(elapsedTime(self.live_clock) >= 1):
                    if(twitch.isStreamLive(self.channel_name)):
                        self.live_clock = time.time()
                    else:
                        self.sock.close()
                        self.running = False
                if(elapsedTime(self.socket_clock) >= 5):
                    self.sock = self.restartSocket()
                try:
                    self.resp = self.sock.recv(2048).decode('utf-8', errors='ignore')
                    if self.resp == '' :
                        self.sock = self.restartSocket()
                except KeyboardInterrupt:
                    try:
                        self.sock.close()
                        self.endExecution()
                    except:
                        self.endExecution()
                except:
                    self.sock = self.restartSocket()
                self.parseResponse()
        except:
            self.sock.close()
            self.endExecution()

    def start(self):
        printInfo(self.channel_name, f'{self.channel_name} just went live!')
        try:
            self.db = db.Database(self.channel_name)
            self.session_id = self.db.startSession()
            self.running = True
            return None if self.session_id is None else self.session_id
        except:
            return None

    def end(self):
        printInfo(self.channel_name, f'{self.channel_name} is now offline.')
        self.db.endSession()
        self.db.cursor.close()
        self.db.db.close()
        self.live = False

    def endExecution(self):
        self.db.endSession()
        self.running = False
        self.executing = False

    def startSocket(self):
        config = configparser.ConfigParser()
        config.read(CONFIG_NAME)
        nickname = config[CONFIG_SECTIONS['twitch']][TWITCH_VARIABLES['nickname']]
        token = config[CONFIG_SECTIONS['twitch']][TWITCH_VARIABLES['token']]
        sock = socket.socket()
        try:
            sock.connect(constants.ADDRESS)
        except:
            printError(f'[{constants.COLORS["bold_green"]}{self.channel_name}{constants.COLORS["clear"]}] ' + ERROR_MESSAGES['host'])
            self.db.endSession()
            return -1
        sock.send(f'PASS {token}\n'.encode('utf-8'))
        sock.send(f'NICK {nickname}\n'.encode('utf-8'))
        sock.send(f'JOIN #{self.channel_name}\n'.encode('utf-8'))
        return sock

    def restartSocket(self):
        self.sock.close()
        self.socket_clock = time.time()
        return self.startSocket()

    def getResponses(self):
        try:
            return self.resp.split('\r\n')[:-1]
        except:
            return None

    def parseResponse(self):
        for response in self.getResponses():
            username = self.parseUsername(response)
            message = self.parseMessage(response)
            if(username is None or ' ' in username or message is None):
                return None
            self.db.log(username, message, self.channel_emotes, self.session_id)

    def parseUsername(self, resp):
        try:
            return resp.split('!')[0].split(':')[1]
        except:
            return None

    def parseMessage(self, resp):
        try:
            return resp.split(f'#{self.channel_name} :')[1]
        except:
            return None

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

def createAndDownloadGlobalEmotes():
    try:
        if not os.path.exists(DIRS['emotes']):
            os.mkdir(DIRS['emotes'])
        os.mkdir(DIRS['global_emotes'])
    except:
        printError(ERROR_MESSAGES['directory'])
    printInfo(None, constants.STATUS_MESSAGES['global'])
    downloadGlobalEmotes()

def downloadFile(url, fileName):
    r = requests.get(url)
    with open(fileName, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk:
                f.write(chunk)
    return None

def downloadGlobalEmotes():
    emotes = twitch.getTwitchEmotes()
    global_emotes_dir = f'{DIRS["emotes"]}/{DIRS["global"]}'
    counter = 0
    for emote in emotes:
        emote_name = emote.code
        for character in constants.BAD_FILE_CHARS:
            if character in emote_name:
                emote_name = emote_name.replace(character, str(counter))
                counter += 1
        filename = f'{global_emotes_dir}/{emote_name}-{emote.id}.png'
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

def globalEmotesDirectoryExists():
    return os.path.exists(f'{os.getcwd()}/global')

def isBadUsername(username):
    for phrase in constants.BAD_USERNAMES:
        if phrase in username:
            return True
    return False

def isDirectoryEmpty(path):
    return True if len(os.listdir(path)) == 0 else False

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
    print(f'[{COLORS["bold_blue"]}{getDateTime(True)}{COLORS["clear"]}] [{COLORS["bold_purple"]}{channel_name}{COLORS["clear"]}] [{COLORS["hi_red"]}ERROR{COLORS["clear"]}] {text}')

def printInfo(channel_name, text):
    print(f'[{COLORS["bold_blue"]}{getDateTime(True)}{COLORS["clear"]}] [{COLORS["bold_purple"]}{channel_name if(channel_name is not None) else "Chattercat"}{COLORS["clear"]}] [{COLORS["hi_green"]}INFO{COLORS["clear"]}] {text}')