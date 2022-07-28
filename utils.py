import configparser
import os
import socket
import time

import requests

import constants
import db
import interface
import twitch

CONFIG_NAME = constants.CONFIG_NAME
CONFIG_SECTIONS = constants.CONFIG_SECTIONS
DIRS = constants.DIRS
DB_VARIABLES = constants.DB_VARIABLES
TWITCH_VARIABLES = constants.TWITCH_VARIABLES
OPTIONS_VARIABLES = constants.OPTIONS_VARIABLES
ERROR_MESSAGES = constants.ERROR_MESSAGES

def createConfig(host, user, password, nickname, token, key):
    if host == '':
        host = 'localhost'
    if user == '':
        user = 'root'
    config = configparser.ConfigParser()
    config[CONFIG_SECTIONS[0]] = {
        DB_VARIABLES[0]:host,
        DB_VARIABLES[1]:user,
        DB_VARIABLES[2]:password
    }
    config[CONFIG_SECTIONS[1]] = {
        TWITCH_VARIABLES[0]:nickname,
        TWITCH_VARIABLES[1]:token,
        TWITCH_VARIABLES[2]:key
    }
    config[CONFIG_SECTIONS[2]] = {
        OPTIONS_VARIABLES[0]:True,
        OPTIONS_VARIABLES[1]:False
    }
    try:
        with open(CONFIG_NAME, 'w') as configfile:
            config.write(configfile)
            configfile.close()
        return 0
    except:
        return None

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
    return f'{mon}{str(cur.tm_mon)}-{day}{str(cur.tm_mday)}-{str(cur.tm_year)}'

def getDateTime():
    cur = time.gmtime()
    mon = '0' if cur.tm_mon < 10 else ''
    day = '0' if cur.tm_mday < 10 else ''
    hour = '0' if cur.tm_hour < 10 else ''
    min = '0' if cur.tm_min < 10 else ''
    sec = '0' if cur.tm_sec < 10 else ''
    return f'{mon}{str(cur.tm_mon)}-{day}{str(cur.tm_mday)}-{str(cur.tm_year)} {hour}{str(cur.tm_hour)}:{min}{str(cur.tm_min)}:{sec}{str(cur.tm_sec)}'

def getDebugMode():
    config = configparser.ConfigParser()
    config.read(CONFIG_NAME)
    try:
        return True if config[CONFIG_SECTIONS[2]][OPTIONS_VARIABLES[1]] == 'True' else False
    except:
        return None

def getDownloadMode():
    config = configparser.ConfigParser()
    try:
        config.read(CONFIG_NAME)
    except:
        return False
    return True if config[CONFIG_SECTIONS[2]][OPTIONS_VARIABLES[0]] == 'True' else False

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

def parseResponse(resp, channel_name, channel_emotes, session_id):
    unparsed_resp = resp.split(' ')
    username_indices = getIndices(unparsed_resp, constants.SERVER_URL)
    num_messages = len(username_indices)
    parsed_response = {}
    if(num_messages == 1):
        parsed_response['username'] = parseUsername(unparsed_resp[0])
        if(parsed_response['username'] is None):
            return
        parsed_response['message'] = parseMessage(unparsed_resp[3:])
        db.log(channel_name, parsed_response['username'], parsed_response['message'], channel_emotes, session_id)
    else:
        for i in range(0, num_messages):
            parsed_response['username'] = parseUsername(unparsed_resp[username_indices[i]])
            if(parsed_response['username'] is None):
                continue
            if(i != num_messages-1):
                parsed_response['message'] = parseMessage(unparsed_resp[username_indices[i]:username_indices[i+1]+1][3:]).split('\r\n')[0]
            else:
                parsed_response['message'] = parseMessage(unparsed_resp[username_indices[i]:][3:]).split('\r\n')[0]
            db.log(channel_name, parsed_response['username'], parsed_response['message'], channel_emotes, session_id)

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

def setup():
    if not os.path.exists(CONFIG_NAME):
        if(interface.handleConfigMenu() is None):   # Error creating config file
            return None
    return 0

def startSocket(channel):
    config = configparser.ConfigParser()
    config.read(CONFIG_NAME)
    nickname = config[CONFIG_SECTIONS[1]][TWITCH_VARIABLES[0]]
    token = config[CONFIG_SECTIONS[1]][TWITCH_VARIABLES[1]]
    sock = socket.socket()
    try:
        sock.connect(constants.ADDRESS)
    except:
        interface.printError(f'[{constants.COLORS["bold_green"]}{channel.strip("#")}{constants.COLORS["clear"]}] ' + ERROR_MESSAGES['host'])
        db.endSession(channel)
        return -1
    sock.send(f'PASS {token}\n'.encode('utf-8'))
    sock.send(f'NICK {nickname}\n'.encode('utf-8'))
    sock.send(f'JOIN {channel}\n'.encode('utf-8'))
    return sock