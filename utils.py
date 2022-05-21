import configparser
import os
import socket
import sys
import time

import requests

import constants
import db
import interface
import twitch

config_name = constants.CONFIG_NAME
config_sections = constants.CONFIG_SECTIONS
db_variables = constants.DB_VARIABLES
twitch_variables = constants.TWITCH_VARIABLES
options_variables = constants.OPTIONS_VARIABLES
error_messages = constants.ERROR_MESSAGES
input_messages = constants.INPUT_MESSAGES
status_messages = constants.STATUS_MESSAGES

def createConfig(host, user, password, nickname, token, key):
    if host == '':
        host = 'localhost'
    if user == '':
        user = 'root'
    config = configparser.ConfigParser()
    config[config_sections[0]] = {
        db_variables[0]:host,
        db_variables[1]:user,
        db_variables[2]:password
    }
    config[config_sections[1]] = {
        twitch_variables[0]:nickname,
        twitch_variables[1]:token,
        twitch_variables[2]:key
    }
    config[config_sections[2]] = {
        options_variables[0]:True,
        options_variables[1]:False
    }
    try:
        with open(config_name, 'w') as configfile:
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

def elapsedTime(start):
    return (time.time() - start) / 60

def getChannelNameInput(initial_run=True):
    if(len(sys.argv) < 2 or initial_run is False):
        channel_name = interface.handleMainMenu()
        if(channel_name is None):
            return None
    else:
        channel_name = sys.argv[1]
    return channel_name.lower()

def getDate():
    cur = time.gmtime()
    mon = ''
    day = ''
    if(cur.tm_mon < 10):
        mon = '0'
    if(cur.tm_mday < 10):
        day = '0'
    return f'{mon}{str(cur.tm_mon)}-{day}{str(cur.tm_mday)}-{str(cur.tm_year)}'

def getDateTime():
    cur = time.gmtime()
    mon = ''
    day = ''
    hour = ''
    min = ''
    sec = ''
    if(cur.tm_mon < 10):
        mon = '0'
    if(cur.tm_mday < 10):
        day = '0'
    if(cur.tm_hour < 10):
        hour = '0'
    if(cur.tm_min < 10):
        min = '0'
    if(cur.tm_sec < 10):
        sec = '0'
    return f'{mon}{str(cur.tm_mon)}-{day}{str(cur.tm_mday)}-{str(cur.tm_year)} {hour}{str(cur.tm_hour)}:{min}{str(cur.tm_min)}:{sec}{str(cur.tm_sec)}'

def getDebugMode():
    config = configparser.ConfigParser()
    config.read(config_name)
    try:
        return True if config[config_sections[2]][options_variables[1]] == 'True' else False
    except:
        return None

def getDownloadMode():
    config = configparser.ConfigParser()
    try:
        config.read(config_name)
    except:
        return False
    return True if config[config_sections[2]][options_variables[0]] == 'True' else False

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
        parsed_response['message'] = parseMessage(unparsed_resp[3:])
        db.log(channel_name, parsed_response['username'], parsed_response['message'], channel_emotes, session_id)
    else:
        for i in range(0, num_messages):
            parsed_response['username'] = parseUsername(unparsed_resp[username_indices[i]])
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
    return username

# (flag) 1 = first run after execution, 2 = otherwise
def run(channel_name, session_id, flag):
    channel = f'#{channel_name}'
    sock = startSocket(channel)
    live_clock = time.time()
    socket_clock = time.time()
    channel_emotes = db.getChannelActiveEmotes(channel_name, flag)
    if(flag == 1):
        interface.printBanner()
    try:
        while True:
            if(elapsedTime(live_clock) >= 1):
                if(twitch.isStreamLive(channel_name)):
                    live_clock = time.time()
                else:
                    sock.close()
                    return False
            if(elapsedTime(socket_clock) >= 5):
                sock.close()
                sock = startSocket(channel)
                socket_clock = time.time()
            try:
                resp = sock.recv(2048).decode('utf-8', errors='ignore')
                if resp == '' :
                    sock.close()
                    return True
            except KeyboardInterrupt:
                try:
                    sock.close()
                    return False
                except:
                    return False
            except:
                sock.close()
                return True
            parseResponse(resp, channel_name, channel_emotes, session_id)
    except:
        sock.close()
        return True

def setup():
    if not os.path.exists(config_name):
        if(interface.handleConfigMenu() is None):   # Error creating config file
            return None
    return 0

def startSocket(channel):
    config = configparser.ConfigParser()
    config.read(config_name)
    nickname = config[config_sections[1]][twitch_variables[0]]
    token = config[config_sections[1]][twitch_variables[1]]
    sock = socket.socket()
    try:
        sock.connect(constants.ADDRESS)
    except:
        interface.printError(error_messages['host'])
        return -1
    sock.send(f'PASS {token}\n'.encode('utf-8'))
    sock.send(f'NICK {nickname}\n'.encode('utf-8'))
    sock.send(f'JOIN {channel}\n'.encode('utf-8'))
    return sock