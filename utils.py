import configparser
import os
import random
import socket
import sys
import time

import requests

import constants
import db
import twitch

colors = constants.COLORS
config_name = constants.CONFIG_NAME
config_sections = constants.CONFIG_SECTIONS
db_variables = constants.DB_VARIABLES
twitch_variables = constants.TWITCH_VARIABLES
options_variables = constants.OPTIONS_VARIABLES
error_messages = constants.ERROR_MESSAGES
input_messages = constants.INPUT_MESSAGES
status_messages = constants.STATUS_MESSAGES

def cls():
    if not getDebugMode():
        os.system('cls' if os.name=='nt' else 'clear')

def createConfig():
    printLogo()
    printLabel(1)
    host = input(f'{input_messages["host"]} ')
    user = input(f'{input_messages["db_user"]} ')
    password = input(f'{input_messages["db_pass"]} ')
    printLogo()
    printLabel(2)
    nickname = input(f'{input_messages["twitch_user"]} ')
    token = input(f'{input_messages["oauth"]} ')
    key = input(f'{input_messages["secret"]} ')
    printLogo()

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
        channel_name = handleMainMenu()
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
    try:
        config.read(config_name)
    except:
        return False
    return True if config[config_sections[2]][options_variables[1]] == 'True' else False

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

def globalEmotesDirectoryExists():
    return os.path.exists(f'{os.getcwd()}/global')

def handleDatabaseOption():
    databases = db.getDatabases()
    num_databases = len(databases)
    if(num_databases == 0):
        printOptionsHeader()
        printInfo(status_messages['no_databases'])
        input()
        return 0
    for i in range(0, num_databases):
        print(f'[{i+1}] {databases[i]}')
    else:
        if(num_databases != 1):
            print(f'[{num_databases+1}] {constants.DATABASE_OPTIONS_MENU[0]}\n[{num_databases+2}] {constants.DATABASE_OPTIONS_MENU[1]}')
            selection = input(f'{input_messages["selection"]} ')
            try:
                selection = int(selection)
            except:
                printError(error_messages['selection'])
                return 0
            if(selection == num_databases+1):
                db.dropDatabaseHandler(databases)
                return 0
            if(selection == num_databases+2):
                return 0
        else:
            print(f'[{num_databases+1}] Back')
            selection = input(f'{input_messages["selection"]} ')
            try:
                selection = int(selection)
            except:
                printError(error_messages['selection'])
                return 0
            if(selection == num_databases+1):
                return 0
    try:
        if(selection <= 0):
            printError(error_messages['selection'])
            return 0
        db.dropDatabaseHandler(databases[int(selection)-1])
        return 0
    except:
        printError(error_messages['selection'])
        return 0

def handleDebugOption(selection):
    config = configparser.ConfigParser()
    config.read(config_name)
    debug = getDebugMode()
    if(selection == 1):
        if(debug == False):
            config[config_sections[2]] = {
            options_variables[0]:config[config_sections[2]][options_variables[0]],
            options_variables[1]:True
            }
        else:
            return 0
    elif(selection == 2):
        if(debug == True):
            config[config_sections[2]] = {
            options_variables[0]:config[config_sections[2]][options_variables[0]],
            options_variables[1]:False
            }
        else:
            return 0
    else:
        return -1
    with open(config_name, 'w') as configfile:
        config.write(configfile)
    return 0

def handleDownloadOption(selection):
    config = configparser.ConfigParser()
    config.read(config_name)
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
    else:
        return -1
    with open(config_name, 'w') as configfile:
        config.write(configfile)
    return 0

def handleMainMenu(channel_name=None):
    while(channel_name is None):
        printMainMenu()
        try:
            selection = int(input(f'{input_messages["selection"]} '))
        except:
            printError(error_messages['selection'])
            continue
        if(selection == 1):
            channel_name = input(f'{input_messages["channel_name"]} ')
        elif(selection == 2):
            while(handleOptionsMenu() != 0):
                continue
        elif(selection == 3):
            cls()
            return None
        else:
            printError(error_messages['selection'])
            continue
    return channel_name

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

def printLogo():
    cls()
    print(f'\n{constants.BANNER}')

def printBanner():
    config = configparser.ConfigParser()
    config.read(config_name)
    cls()
    print(f'\n{constants.BANNER}')
    if(getDownloadMode() == True):
        print(f'\t\t\t\t\tDownload emotes: [{colors["green"]}ON{colors["clear"]}]\n')
    else:
        print(f'\t\t\t\t\tDownload emotes: [{colors["red"]}OFF{colors["clear"]}]')

def printLabel(flag):
    if(flag == 1):
        print(f'Version [v{constants.VERSION}]\n')
        text = f'{colors["bg_pink"]}{constants.LABEL_TITLES[0]}{colors["clear"]}'
        printSpaces('[0;105m', len(text)-9)
        print(text)
        printSpaces('[0;105m', len(text)-9)
    elif(flag == 2):
        print(f'Version [v{constants.VERSION}]\n')
        text = f'{colors["bg_green"]}{constants.LABEL_TITLES[1]}{colors["clear"]}'
        printSpaces('[0;102m',len(text)-9)
        print(text)
        printSpaces('[0;102m',len(text)-9)
    elif(flag == 3):
        print(f'Version [v{constants.VERSION}]\n')
        text = f'{colors["bg_blue"]}{constants.LABEL_TITLES[2]}{colors["clear"]}'
        printSpaces('[0;104m',len(text)-9)
        print(text)
        printSpaces('[0;104m',len(text)-9)
    else:
        return None

def printDebug(text):
    print(f'[{colors["bold_blue"]}{getDateTime()}{colors["clear"]}] [{colors["yellow"]}DEBUG{colors["clear"]}] {text}')

def printError(text):
    print(f'[{colors["bold_blue"]}{getDateTime()}{colors["clear"]}] [{colors["hi_red"]}ERROR{colors["clear"]}] {text}')
    input()

def printInfo(text):
    print(f'[{colors["bold_blue"]}{getDateTime()}{colors["clear"]}] [{colors["hi_green"]}INFO{colors["clear"]}] {text}')

def printLog(channel_name, username, message):
    if '\\\\' in message:
        message = message.replace('\\\\', '\\')
    rand = random.Random()
    username_color = rand.randrange(0,5)
    print(f'[{colors["bold_green"]}{channel_name}{colors["clear"]}] [{colors["bold_blue"]}{getDateTime()}{colors["clear"]}] [{colors["hi_blue"]}LOG{colors["clear"]}] {constants.USERNAME_COLORS[username_color]}{username}{colors["clear"]}: {message}')

def printMainMenu():
    printBanner()
    print(constants.MAIN_MENU)

def handleOptionsMenu():
    printOptionsHeader()
    print(constants.OPTIONS_MENU)
    selection = input(f'{input_messages["selection"]} ')
    try:
        selection = int(selection)
    except:
        printError(error_messages['selection'])
        return -1
    if(selection == 1):      # Download menu 
        printOptionsHeader()
        print(constants.DOWNLOAD_OPTIONS_MENU)
        selection = input(f'{input_messages["selection"]} ')
        try:
            selection = int(selection)
        except:
            printError(error_messages['selection'])
            return -1
        if(selection == 1 or selection == 2):
            handleDownloadOption(selection)
        else:
            printError(error_messages['selection'])
            return -1
        return 1
    elif(selection == 2):   # Database menu
        printOptionsHeader()
        print(constants.DATABASE_OPTIONS_HEADER)
        handleDatabaseOption()
        return 1
    elif(selection == 3):   # Debug menu
        printOptionsHeader()
        print(constants.DEBUG_OPTIONS_MENU)
        selection = input(f'{input_messages["selection"]} ')
        try:
            selection = int(selection)
        except:
            printError(error_messages['selection'])
            return -1
        if(selection == 1 or selection == 2):
            handleDebugOption(selection)
        else:
            printError(error_messages['selection'])
            return -1
        return 1
    elif(selection == 4):
        return 0
    else:
        printError(error_messages['selection'])
        return -1

def printOptionsHeader():
    cls()
    print(f'\n{constants.BANNER}')
    printLabel(3)

def printSpaces(color, num):
    for i in range(0, num):
        print(f'\033{color} ', end="")
    print(colors['clear'])

def progressbar(it, prefix="", size=60, file=sys.stdout):
    count = len(it)
    def show(j):
        if((j/count)*100 <= 10):
            color = colors['bold_red']
        elif((j/count)*100 < 100):
            color = colors['bold_yellow']
        else:
            color = colors['bold_green']
        x = int(size*j/count)
        file.write("%s[%s%s%s%s] %s%i/%i%s\r" % (prefix, color, "●"*x, " "*(size-x), colors['clear'], color, j, count, colors['clear']))
        file.flush()        
    show(0)
    for i, item in enumerate(it):
        yield item
        show(i+1)
    file.write("\n")
    file.flush()

# (flag) 1 = first run after execution, 2 = otherwise
def run(channel_name, session_id, flag):
    channel = f'#{channel_name}'
    sock = startSocket(channel)
    live_clock = time.time()
    socket_clock = time.time()
    channel_emotes = db.getChannelActiveEmotes(channel_name, flag)
    if(flag == 1):
        printBanner()
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
        if(createConfig() is None):   # Error creating config file
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
        printError(error_messages['host'])
        return -1
    sock.send(f'PASS {token}\n'.encode('utf-8'))
    sock.send(f'NICK {nickname}\n'.encode('utf-8'))
    sock.send(f'JOIN {channel}\n'.encode('utf-8'))
    return sock