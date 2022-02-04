import configparser
import os
import sys
import time

import requests

import constants
import db

config_sections = constants.config_sections
db_variables = constants.db_variables
twitch_variables = constants.twitch_variables
options_variables = constants.options_variables
error_messages = constants.error_messages
input_messages = constants.input_messages
os.system("")

def cls(debug_flag=0):
    if(debug_flag == 0):
        os.system('cls' if os.name=='nt' else 'clear')
    else:
        return

def createConfig():
    config = configparser.ConfigParser()
    printLabel(1)
    host = input(f'{input_messages[0]} ')
    user = input(f'{input_messages[1]} ')
    password = input(f'{input_messages[2]} ')
    cls()
    print(f'\n{constants.banner}')
    printLabel(2)
    nickname = input(f'{input_messages[3]} ')
    token = input(f'{input_messages[4]} ')
    cls()
    print(f'\n{constants.banner}')

    if host == '':
        host = 'localhost'
    
    config[config_sections[0]] = {
        db_variables[0]:host,
        db_variables[1]:user,
        db_variables[2]:password
    }

    config[config_sections[1]] = {
        twitch_variables[0]:nickname,
        twitch_variables[1]:token
    }

    config[config_sections[2]] = {
        options_variables[0]:True,
        options_variables[1]:False
    }

    with open(constants.config_name, 'w') as configfile:
        config.write(configfile)
        configfile.close()

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

def getDebugMode():
    config = configparser.ConfigParser()
    config.read(constants.config_name)
    return int(config[constants.config_sections[2]][options_variables[1]])

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
    if ' ' in username:
        return None
    return username

def printBanner():
    config = configparser.ConfigParser()
    config.read(constants.config_name)
    cls()
    print(f'\n{constants.banner}')
    if(config[config_sections[2]][options_variables[0]] == 'True'):
        print(f'\t\t\t\t\tDownload emotes: [\033[0;32mON\033[0m]\n')
    else:
        print(f'\t\t\t\t\tDownload emotes: [\033[0;31mOFF\033[0m]')

def printLabel(flag):
    if(flag == 1):
        text = f'\033[45mDATABASE INFORMATION\033[0m'
        printSpaces('[0;105m', len(text)-9)
        print(text)
        printSpaces('[0;105m', len(text)-9)
    elif(flag == 2):
        text = f'\033[42mTWITCH INFORMATION\033[0m'
        printSpaces('[0;102m',len(text)-9)
        print(text)
        printSpaces('[0;102m',len(text)-9)
    elif(flag == 3):
        print(f'Version [v{constants.version}]\n')
        text = f'\033[44mOPTIONS\033[0m'
        printSpaces('[0;104m',len(text)-9)
        print(text)
        printSpaces('[0;104m',len(text)-9)
    else:
        return None

def printDebug(text):
    print(f'[\033[1;34m{getDateTime()}\033[0m] [\033[0;33mDEBUG\033[0m] {text}')

def printError(text):
    print(f'[\033[1;34m{getDateTime()}\033[0m] [\033[0;91mERROR\033[0m] {text}')

def printLog(channel_name, username, message):
    print(f'[\033[1;32m{channel_name}\033[0m] [\033[1;34m{getDateTime()}\033[0m] [\033[0;94mLOG\033[0m] \033[1;35m{username}\033[0m: {message}')

def printMenu():
    print(constants.main_menu)
    selection = input(f'{input_messages[6]} ')
    try:
        selection = int(selection)
    except:
        return -1
    while(selection != 1):
        if(selection == 2):
            code = printOptions()
            if(code == -1):
                printError(error_messages[3])
                a = input()
            printBanner()
            print(constants.main_menu)
        elif(selection == 3):
            cls()
            return 0
        else:
            printBanner()
            print(constants.main_menu)
        selection = input(f'{input_messages[6]} ')
        try:
            selection = int(selection)
        except:
            return -1
    channel_name = input(f'{input_messages[5]} ')
    return channel_name

def printOptions():
    printOptionsHeader()
    print(constants.options_menu)
    selection = input(f'{input_messages[6]} ')
    try:
        selection = int(selection)
    except:
        return -1
    if(selection == 1):
        printOptionsHeader()
        print(constants.download_options_menu)
        selection = input(f'{input_messages[6]} ')
        try:
            selection = int(selection)
        except:
            return -1
        config = configparser.ConfigParser()
        config.read(constants.config_name)
        if(selection == 1):
            if(config[config_sections[2]] == True):
                return 0
            else:
                config[config_sections[2]] = {
                    options_variables[0]:True,
                    options_variables[1]:config[config_sections[2]][options_variables[1]]
                }
        elif(selection == 2):
            if(config[config_sections[2]] == False):
                return 0
            config[config_sections[2]] = {
                options_variables[0]:False,
                options_variables[1]:config[config_sections[2]][options_variables[1]]
            }
        with open(constants.config_name, 'w') as configfile:
            config.write(configfile)
        return 0
    elif(selection == 2):
        printOptionsHeader()
        print(constants.database_options_menu)
        databases = db.getDatabases()
        for i in range(0, len(databases)):
            print(f'[{i+1}] {databases[i]}')
        if(len(databases) == 0):
            print("No databases found! Press any key to go back.")
            selection = input()
            return 0
        else:
            print(f'[{len(databases)+1}] Delete ALL databases')
            print(f'[{len(databases)+2}] Back')
        selection = input(f'{input_messages[6]} ')
        if(selection == str(len(databases)+1)):
            db.dropDatabase(databases)
            return 0
        if(selection == str(len(databases)+2)):
            return 0
        try:
            db.dropDatabase(databases[int(selection)-1])
            time.sleep(5)
            return 0
        except:
            return 0
    elif(selection == 3):
        printOptionsHeader()
        print(constants.debug_options_menu)
        selection = input(f'{input_messages[6]} ')
        try:
            selection = int(selection)
        except:
            return -1
        config = configparser.ConfigParser()
        config.read(constants.config_name)
        if(selection == 1):
            if(config[config_sections[2]][options_variables[1]] == False):
                config[config_sections[2]] = {
                options_variables[0]:config[config_sections[2]][options_variables[0]],
                options_variables[1]:True
                }
            else:
                return 0
        elif(selection == 2):
            if(config[config_sections[2]][options_variables[1]] == True):
                config[config_sections[2]] = {
                options_variables[0]:config[config_sections[2]][options_variables[0]],
                options_variables[1]:False
                }
            else:
                return 0
        else:
            return -1
        with open(constants.config_name, 'w') as configfile:
            config.write(configfile)
        return 0
    elif(selection == 4):
        return 0
    else:
        return -1

def printOptionsHeader():
    cls()
    print(f'\n{constants.banner}')
    printLabel(3)

def printSpaces(color, num):
    for i in range(0, num):
        print(f'\033{color} ', end="")
    print("\033[0m")

def progressbar(it, prefix="", size=60, file=sys.stdout):
    count = len(it)
    def show(j):
        if((j/count)*100 <= 10):
            color = f'\033[1;31m'
        elif((j/count)*100 < 100):
            color = f'\033[1;33m'
        else:
            color = f'\033[1;32m'
        x = int(size*j/count)
        file.write("%s[%s%s%s%s] %s%i/%i%s\r" % (prefix, color, "●"*x, " "*(size-x), '\033[0m', color, j, count, '\033[0m'))
        file.flush()        
    show(0)
    for i, item in enumerate(it):
        yield item
        show(i+1)
    file.write("\n")
    file.flush()