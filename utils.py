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
status_messages = constants.status_messages
bg_colors = constants.bg_colors
bold_colors = constants.bold_colors
colors = constants.colors
high_int_colors = constants.high_int_colors
os.system("")

def cls():
    if not getDebugMode():
        os.system('cls' if os.name=='nt' else 'clear')
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
    key = input(f'{input_messages[7]} ')
    cls()
    print(f'\n{constants.banner}')

    if host == '':
        host = 'localhost'

    if user == '':
        user = 'root'
    
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
        with open(constants.config_name, 'w') as configfile:
            config.write(configfile)
            configfile.close()
    except:
        return -1

def downloadFile(url, fileName):
    r = requests.get(url)
    with open(fileName, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk:
                f.write(chunk)
    return None

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
    config.read(constants.config_name)
    try:
        if(config[constants.config_sections[2]][options_variables[1]] == 'True'):
            return True
        else:
            return False
    except:
        return False

def getDownloadOption():
    config = configparser.ConfigParser()
    config.read(constants.config_name)
    if(config[config_sections[2]][constants.options_variables[0]] == 'True'):
        return True
    else:
        return False

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

def globalEmotesDirectoryExists():
    return os.path.exists(f'{os.getcwd()}/global')

def handleDatabaseOption():
    databases = db.getDatabases()
    num_databases = len(databases)
    if(num_databases == 0):
        printOptionsHeader()
        printInfo(status_messages[7])
        input()
        return 0
    for i in range(0, num_databases):
        print(f'[{i+1}] {databases[i]}')
    else:
        if(num_databases != 1):
            print(f'[{num_databases+1}] {constants.database_options_menu[0]}\n[{num_databases+2}] {constants.database_options_menu[1]}')
            selection = input(f'{input_messages[6]} ')
            try:
                selection = int(selection)
            except:
                printError(error_messages[3])
                input()
                return 0
            if(selection == num_databases+1):
                db.dropDatabase(databases)
                return 0
            if(selection == num_databases+2):
                return 0
        else:
            print(f'[{num_databases+1}] Back')
            selection = input(f'{input_messages[6]} ')
            try:
                selection = int(selection)
            except:
                printError(error_messages[3])
                input()
                return 0
            if(selection == num_databases+1):
                return 0
    try:
        if(selection <= 0):
            printError(error_messages[3])
            input()
            return 0
        db.dropDatabase(databases[int(selection)-1])
        return 0
    except:
        printError(error_messages[3])
        input()
        return 0

def handleDebugOption(selection):
    config = configparser.ConfigParser()
    config.read(constants.config_name)
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
    with open(constants.config_name, 'w') as configfile:
        config.write(configfile)
    return 0

def handleDownloadOption(selection):
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
    else:
        return -1
    with open(constants.config_name, 'w') as configfile:
        config.write(configfile)
    return 0

def parseMessage(message):
    parsed_message = ''
    for i in range(0, len(message)):
        if '\r\n' in message[i]:
            message[i] = message[i].split('\r\n')[0]
        if constants.server_url in message[i]:
            continue
        if i == 0:
            parsed_message = message[i]
        else:
            parsed_message = parsed_message + ' ' + message[i]
    return parsed_message[1:]

def parseUsername(message):
    if message == f':{constants.server_url}\r\n':
        return None
    if f':{constants.server_url}\r\n' in message:
        message = message.split('\r\n')[1]
    if constants.server_url in message:
        if '@' not in message:
            username = message.split(f'.{constants.server_url}')[0]
        else:
            username = message.split(constants.server_url)[0].split('@')[1].split('.')[0]
    if ' ' in username:
        return None
    return username

def printBanner():
    config = configparser.ConfigParser()
    config.read(constants.config_name)
    cls()
    print(f'\n{constants.banner}')
    if(getDownloadOption() == True):
        print(f'\t\t\t\t\tDownload emotes: [{colors["green"]}ON{colors["clear"]}]\n')
    else:
        print(f'\t\t\t\t\tDownload emotes: [{colors["red"]}OFF{colors["clear"]}]')

def printLabel(flag):
    if(flag == 1):
        print(f'Version [v{constants.version}]\n')
        text = f'{bg_colors["pink"]}{constants.label_titles[0]}{colors["clear"]}'
        printSpaces('[0;105m', len(text)-9)
        print(text)
        printSpaces('[0;105m', len(text)-9)
    elif(flag == 2):
        print(f'Version [v{constants.version}]\n')
        text = f'{bg_colors["green"]}{constants.label_titles[1]}{colors["clear"]}'
        printSpaces('[0;102m',len(text)-9)
        print(text)
        printSpaces('[0;102m',len(text)-9)
    elif(flag == 3):
        print(f'Version [v{constants.version}]\n')
        text = f'{bg_colors["blue"]}{constants.label_titles[2]}{colors["clear"]}'
        printSpaces('[0;104m',len(text)-9)
        print(text)
        printSpaces('[0;104m',len(text)-9)
    else:
        return None

def printDebug(text):
    print(f'[{bold_colors["blue"]}{getDateTime()}{colors["clear"]}] [{colors["yellow"]}DEBUG{colors["clear"]}] {text}')

def printError(text):
    print(f'[{bold_colors["blue"]}{getDateTime()}{colors["clear"]}] [{high_int_colors["red"]}ERROR{colors["clear"]}] {text}')

def printInfo(text):
    print(f'[{bold_colors["blue"]}{getDateTime()}{colors["clear"]}] [{high_int_colors["green"]}INFO{colors["clear"]}] {text}')

def printLog(channel_name, username, message, username_color):
    print(f'[{bold_colors["green"]}{channel_name}{colors["clear"]}] [{bold_colors["blue"]}{getDateTime()}{colors["clear"]}] [{high_int_colors["blue"]}LOG{colors["clear"]}] {username_color}{username}{colors["clear"]}: {message}')

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
            while(code != 0):
                if(code == -1):
                    printError(error_messages[3])
                    input()
                code = printOptions()
            return 1
        elif(selection == 3):
            cls()
            return 0
        else:
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
        if(handleDownloadOption(selection) == -1):
            return -1
        return 1
    elif(selection == 2):
        printOptionsHeader()
        print(constants.database_options_header)
        handleDatabaseOption()
        return 1
    elif(selection == 3):
        printOptionsHeader()
        print(constants.debug_options_menu)
        selection = input(f'{input_messages[6]} ')
        try:
            selection = int(selection)
        except:
            return -1
        if(handleDebugOption(selection) == -1):
            return -1
        return 1
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
    print(colors['clear'])

def progressbar(it, prefix="", size=60, file=sys.stdout):
    count = len(it)
    def show(j):
        if((j/count)*100 <= 10):
            color = bold_colors['red']
        elif((j/count)*100 < 100):
            color = bold_colors['yellow']
        else:
            color = bold_colors['green']
        x = int(size*j/count)
        file.write("%s[%s%s%s%s] %s%i/%i%s\r" % (prefix, color, "●"*x, " "*(size-x), colors['clear'], color, j, count, colors['clear']))
        file.flush()        
    show(0)
    for i, item in enumerate(it):
        yield item
        show(i+1)
    file.write("\n")
    file.flush()