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
    return f'{str(cur.tm_mon)}-{str(cur.tm_mday)}-{str(cur.tm_year)}'

def getDateTime():
    cur = time.localtime()
    return f'{str(cur.tm_mon)}-{str(cur.tm_mday)}-{str(cur.tm_year)} {str(cur.tm_hour)}:{str(cur.tm_min)}:{str(cur.tm_sec)}'

def print_debug(text):
    print(f'[\033[1;34m{getDateTime()}\033[0m] [\033[0;33mDEBUG\033[0m] {text}')

def print_error(text):
    print(f'[\033[1;34m{getDateTime()}\033[0m] [\033[0;91mERROR\033[0m] {text}')

def print_log(channel_name, username, message):
    print(f'[\033[1;32m{channel_name}\033[0m] [\033[1;34m{getDateTime()}\033[0m] [\033[0;94mLOG\033[0m] \033[1;35m{username}\033[0m: {message}')