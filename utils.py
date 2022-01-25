import configparser
import time

import requests

import constants

def createConfig():
    config = configparser.ConfigParser()
    host = input("Enter hostname [default: localhost]: ")
    user = input("Enter DB username: ")
    password = input("Enter DB password: ")
    nickname = input("Enter your twitch username: ")
    token = input("Please visit the URL https://twitchapps.com/tmi/ and enter the token after pressing Connect: ")

    if host == '':
        host = 'localhost'
    
    config['db'] = {
        'host':host,
        'user':user,
        'password':password
    }

    config['twitch'] = {
        'nickname':nickname,
        'token':token
    }

    with open(constants.config_name, 'w') as configfile:
        config.write(configfile)

def downloadFile(url, fileName):
    r = requests.get(url)
    with open(fileName, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk:
                f.write(chunk)
    return None

def getDate():
    cur = time.localtime()
    mon = ''
    day = ''
    if(cur.tm_mon < 10):
        mon = '0'
    if(cur.tm_mday < 10):
        day = '0'
    return f'{mon}{str(cur.tm_mon)}-{day}{str(cur.tm_mday)}-{str(cur.tm_year)}'

def getDateTime():
    cur = time.localtime()
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

def getIndices(list, text):
    indices = []
    for i in range(0, len(list)):
        if text in list[i]:
            indices.append(i)
    return indices

def getOccurrences(list, text):
    occurrences = 0
    for i in range(0, len(list)):
        if text in list[i]:
            occurrences += 1
    return occurrences

def parseMessage(message):
    parsed_message = ''
    for i in range(0, len(message)):
        if '\r\n' in message[i]:
            message[i] = message[i].split('\r\n')[0]
        if 'tmi.twitch.tv' in message[i]:
            continue
        if i == 0:
            parsed_message = message[i]
        else:
            parsed_message = parsed_message + ' ' + message[i]
    return parsed_message[1:]

def parseUsername(message):
    if message == ':tmi.twitch.tv\r\n':
        return None
    if ':tmi.twitch.tv\r\n' in message:
        message = message.split('\r\n')[1]
    if 'tmi.twitch.tv' in message:
        if '@' not in message:
            username = message.split('.tmi.twitch.tv')[0]
        else:
            username = message.split('tmi.twitch.tv')[0].split('@')[1].split('.')[0]
    return username

def print_debug(text):
    print(f'[\033[1;34m{getDateTime()}\033[0m] [\033[0;33mDEBUG\033[0m] {text}')

def print_error(text):
    print(f'[\033[1;34m{getDateTime()}\033[0m] [\033[0;91mERROR\033[0m] {text}')

def print_log(channel_name, username, message):
    print(f'[\033[1;32m{channel_name}\033[0m] [\033[1;34m{getDateTime()}\033[0m] [\033[0;94mLOG\033[0m] \033[1;35m{username}\033[0m: {message}')