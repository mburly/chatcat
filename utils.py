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
DB_VARIABLES = constants.DB_VARIABLES
TWITCH_VARIABLES = constants.TWITCH_VARIABLES
ERROR_MESSAGES = constants.ERROR_MESSAGES

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

def createAndDownloadGlobalEmotes():
    try:
        if not os.path.exists(DIRS['emotes']):
            os.mkdir(DIRS['emotes'])
        os.mkdir(DIRS['global_emotes'])
    except:
        printError(ERROR_MESSAGES['directory'])
    print(constants.STATUS_MESSAGES['global'])
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

def endExecution(Chattercat):
    db.endSession(Chattercat.channel_name)
    Chattercat.executing = False
    Chattercat.running = False

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
    file = open('streams.txt','r')
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

def parseMessage(message):
    return ' '.join(message).strip('\r\n')[1:]

def parseResponse(resp, Chattercat):
    unparsed_resp = resp.split(' ')
    username_indices = getIndices(unparsed_resp, constants.SERVER_URL)
    num_messages = len(username_indices)
    parsed_response = {}
    if(num_messages == 1):
        parsed_response['username'] = parseUsername(unparsed_resp[0])
        if(parsed_response['username'] is None):
            return
        parsed_response['message'] = parseMessage(unparsed_resp[3:])
        db.log(Chattercat.channel_name, parsed_response['username'], parsed_response['message'], Chattercat.channel_emotes, Chattercat.session_id)
    else:
        for i in range(0, num_messages):
            parsed_response['username'] = parseUsername(unparsed_resp[username_indices[i]])
            if(parsed_response['username'] is None):
                continue
            if(i != num_messages-1):
                parsed_response['message'] = parseMessage(unparsed_resp[username_indices[i]:username_indices[i+1]+1][3:]).split('\r\n')[0]
            else:
                parsed_response['message'] = parseMessage(unparsed_resp[username_indices[i]:][3:]).split('\r\n')[0]
            db.log(Chattercat.channel_name, parsed_response['username'], parsed_response['message'], Chattercat.channel_emotes, Chattercat.session_id)

# [message] format = :<USERNAME>!<USERNAME>@<USERNAME>.tmi.twitch.tv PRIVMSG #<CHANNELNAME> :<MESSAGE>
def parseUsername(message):
    username = message.split('!')[0].split(':')
    username = username[len(username)-1]
    if(isBadUsername(username)):
        return None
    if(username == ''):
        if(message[0] == ':'):
            return parseUsername(message.split(':!')[1])
        elif(message[0] == '!'):
            return parseUsername(message.strip('!'))
        else:
            return None
    return username

def printBanner():
    cls()
    print(f'\n{constants.BANNER}')

def printError(text):
    print(f'[{COLORS["bold_blue"]}{getDateTime(True)}{COLORS["clear"]}] [{COLORS["hi_red"]}ERROR{COLORS["clear"]}] {text}')
    input()

def printInfo(channel_name, text):
    print(f'[{COLORS["bold_blue"]}{getDateTime(True)}{COLORS["clear"]}] [{COLORS["bold_purple"]}{channel_name}{COLORS["clear"]}] [{COLORS["hi_green"]}INFO{COLORS["clear"]}] {text}')

def restartSocket(Chattercat):
    Chattercat.sock.close()
    Chattercat.socket_clock = time.time()
    return startSocket(Chattercat.channel_name)

def startSocket(channel_name):
    channel_name = f'#{channel_name}'
    config = configparser.ConfigParser()
    config.read(CONFIG_NAME)
    nickname = config[CONFIG_SECTIONS[1]][TWITCH_VARIABLES[0]]
    token = config[CONFIG_SECTIONS[1]][TWITCH_VARIABLES[1]]
    sock = socket.socket()
    try:
        sock.connect(constants.ADDRESS)
    except:
        printError(f'[{constants.COLORS["bold_green"]}{channel_name.strip("#")}{constants.COLORS["clear"]}] ' + ERROR_MESSAGES['host'])
        db.endSession(channel_name)
        return -1
    sock.send(f'PASS {token}\n'.encode('utf-8'))
    sock.send(f'NICK {nickname}\n'.encode('utf-8'))
    sock.send(f'JOIN {channel_name}\n'.encode('utf-8'))
    return sock