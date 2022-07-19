import configparser
import os
import random
import sys

import constants
import db
import utils

COLORS = constants.COLORS
CONFIG_NAME = constants.CONFIG_NAME
CONFIG_SECTIONS = constants.CONFIG_SECTIONS
OPTIONS_VARIABLES = constants.OPTIONS_VARIABLES
ERROR_MESSAGES = constants.ERROR_MESSAGES
INPUT_MESSAGES = constants.INPUT_MESSAGES

def cls():
    if not utils.getDebugMode():
        os.system('cls' if os.name=='nt' else 'clear')

def handleConfigMenu():
    printLogo()
    printLabel(1)
    host = input(f'{INPUT_MESSAGES["host"]} ')
    user = input(f'{INPUT_MESSAGES["db_user"]} ')
    password = input(f'{INPUT_MESSAGES["db_pass"]} ')
    printLogo()
    printLabel(2)
    nickname = input(f'{INPUT_MESSAGES["twitch_user"]} ')
    token = input(f'{INPUT_MESSAGES["oauth"]} ')
    key = input(f'{INPUT_MESSAGES["secret"]} ')
    printLogo()
    return utils.createConfig(host, user, password, nickname, token, key)

def handleDatabaseMenu():
    databases = db.getDatabases()
    num_databases = len(databases)
    if(num_databases == 0):
        printOptionsHeader()
        printError(ERROR_MESSAGES['no_databases'])
        input()
        return 0
    for i in range(0, num_databases):
        print(f'[{i+1}] {databases[i]}')
    else:
        if(num_databases != 1):
            print(f'[{num_databases+1}] {constants.DATABASE_OPTIONS_MENU[0]}\n[{num_databases+2}] {constants.DATABASE_OPTIONS_MENU[1]}')
            selection = input(f'{INPUT_MESSAGES["selection"]} ')
            try:
                selection = int(selection)
            except:
                printError(ERROR_MESSAGES['selection'])
                return 0
            if(selection == num_databases+1):
                db.dropDatabaseHandler(databases)
                return 0
            if(selection == num_databases+2):
                return 0
        else:
            print(f'[{num_databases+1}] Back')
            selection = input(f'{INPUT_MESSAGES["selection"]} ')
            try:
                selection = int(selection)
            except:
                printError(ERROR_MESSAGES['selection'])
                return 0
            if(selection == num_databases+1):
                return 0
    try:
        if(selection <= 0):
            printError(ERROR_MESSAGES['selection'])
            return 0
        db.dropDatabaseHandler(databases[int(selection)-1])
        return 0
    except:
        printError(ERROR_MESSAGES['selection'])
        return 0

def handleDebugMenu(selection):
    config = configparser.ConfigParser()
    config.read(CONFIG_NAME)
    debug = utils.getDebugMode()
    if(selection == 1):
        if(debug == False):
            config[CONFIG_SECTIONS[2]] = {
            OPTIONS_VARIABLES[0]:config[CONFIG_SECTIONS[2]][OPTIONS_VARIABLES[0]],
            OPTIONS_VARIABLES[1]:True
            }
        else:
            return 0
    elif(selection == 2):
        if(debug == True):
            config[CONFIG_SECTIONS[2]] = {
            OPTIONS_VARIABLES[0]:config[CONFIG_SECTIONS[2]][OPTIONS_VARIABLES[0]],
            OPTIONS_VARIABLES[1]:False
            }
        else:
            return 0
    else:
        return -1
    with open(CONFIG_NAME, 'w') as configfile:
        config.write(configfile)
    return 0

def handleDownloadMenu(selection):
    config = configparser.ConfigParser()
    config.read(CONFIG_NAME)
    if(selection == 1):
        if(config[CONFIG_SECTIONS[2]] == True):
            return 0
        else:
            config[CONFIG_SECTIONS[2]] = {
                OPTIONS_VARIABLES[0]:True,
                OPTIONS_VARIABLES[1]:config[CONFIG_SECTIONS[2]][OPTIONS_VARIABLES[1]]
            }
    elif(selection == 2):
        if(config[CONFIG_SECTIONS[2]] == False):
            return 0
        config[CONFIG_SECTIONS[2]] = {
            OPTIONS_VARIABLES[0]:False,
            OPTIONS_VARIABLES[1]:config[CONFIG_SECTIONS[2]][OPTIONS_VARIABLES[1]]
        }
    else:
        return -1
    with open(CONFIG_NAME, 'w') as configfile:
        config.write(configfile)
    return 0

def handleMainMenu(channel_name=None):
    while(channel_name is None):
        printMainMenu()
        try:
            selection = int(input(f'{INPUT_MESSAGES["selection"]} '))
        except:
            printError(ERROR_MESSAGES['selection'])
            continue
        if(selection == 1):
            channel_name = input(f'{INPUT_MESSAGES["channel_name"]} ')
        elif(selection == 2):
            while(handleOptionsMenu() != 0):
                continue
        elif(selection == 3):
            cls()
            return None
        else:
            printError(ERROR_MESSAGES['selection'])
            continue
    return channel_name

def printLogo():
    cls()
    print(f'\n{constants.BANNER}')

def printBanner():
    config = configparser.ConfigParser()
    config.read(CONFIG_NAME)
    cls()
    print(f'\n{constants.BANNER}')
    if(utils.getDownloadMode() == True):
        print(f'\t\t\t\t\tDownload emotes: [{COLORS["green"]}ON{COLORS["clear"]}]\n')
    else:
        print(f'\t\t\t\t\tDownload emotes: [{COLORS["red"]}OFF{COLORS["clear"]}]')

def printLabel(flag):
    if(flag == 1):
        print(f'Version [v{constants.VERSION}]\n')
        text = f'{COLORS["bg_pink"]}{constants.LABEL_TITLES[0]}{COLORS["clear"]}'
        printSpaces('[0;105m', len(text)-9)
        print(text)
        printSpaces('[0;105m', len(text)-9)
    elif(flag == 2):
        print(f'Version [v{constants.VERSION}]\n')
        text = f'{COLORS["bg_green"]}{constants.LABEL_TITLES[1]}{COLORS["clear"]}'
        printSpaces('[0;102m',len(text)-9)
        print(text)
        printSpaces('[0;102m',len(text)-9)
    elif(flag == 3):
        print(f'Version [v{constants.VERSION}]\n')
        text = f'{COLORS["bg_blue"]}{constants.LABEL_TITLES[2]}{COLORS["clear"]}'
        printSpaces('[0;104m',len(text)-9)
        print(text)
        printSpaces('[0;104m',len(text)-9)
    else:
        return None

def printMainMenu():
    printBanner()
    print(constants.MAIN_MENU)

def printOptionsHeader():
    cls()
    print(f'\n{constants.BANNER}')
    printLabel(3)

def handleOptionsMenu():
    printOptionsHeader()
    print(constants.OPTIONS_MENU)
    selection = input(f'{INPUT_MESSAGES["selection"]} ')
    try:
        selection = int(selection)
    except:
        printError(ERROR_MESSAGES['selection'])
        return -1
    if(selection == 1):      # Download menu 
        printOptionsHeader()
        print(constants.DOWNLOAD_OPTIONS_MENU)
        selection = input(f'{INPUT_MESSAGES["selection"]} ')
        try:
            selection = int(selection)
        except:
            printError(ERROR_MESSAGES['selection'])
            return -1
        if(selection == 1 or selection == 2):
            handleDownloadMenu(selection)
        else:
            printError(ERROR_MESSAGES['selection'])
            return -1
        return 1
    elif(selection == 2):   # Database menu
        printOptionsHeader()
        print(constants.DATABASE_OPTIONS_HEADER)
        handleDatabaseMenu()
        return 1
    elif(selection == 3):   # Debug menu
        printOptionsHeader()
        print(constants.DEBUG_OPTIONS_MENU)
        selection = input(f'{INPUT_MESSAGES["selection"]} ')
        try:
            selection = int(selection)
        except:
            printError(ERROR_MESSAGES['selection'])
            return -1
        if(selection == 1 or selection == 2):
            handleDebugMenu(selection)
        else:
            printError(ERROR_MESSAGES['selection'])
            return -1
        return 1
    elif(selection == 4):
        return 0
    else:
        printError(ERROR_MESSAGES['selection'])
        return -1

def printDebug(text, channel_name=None):
    if(channel_name is None):
        print(f'[{COLORS["bold_blue"]}{utils.getDateTime()}{COLORS["clear"]}] [{COLORS["bold_yellow"]}DEBUG{COLORS["clear"]}] {text}')
    else:
        print(f'[{COLORS["bold_green"]}{channel_name}{COLORS["clear"]}] [{COLORS["bold_blue"]}{utils.getDateTime()}{COLORS["clear"]}] [{COLORS["bold_yellow"]}DEBUG{COLORS["clear"]}] {text}')

def printError(text):
    print(f'[{COLORS["bold_blue"]}{utils.getDateTime()}{COLORS["clear"]}] [{COLORS["hi_red"]}ERROR{COLORS["clear"]}] {text}')
    input()

def printInfo(channel_name, text):
    print(f'[{COLORS["bold_blue"]}{utils.getDateTime()}{COLORS["clear"]}] [{COLORS["bold_purple"]}{channel_name}{COLORS["clear"]}] [{COLORS["hi_green"]}INFO{COLORS["clear"]}] {text}')

def printLog(channel_name, username, message):
    if '\\\\' in message:
        message = message.replace('\\\\', '\\')
    print(f'[{COLORS["bold_green"]}{channel_name}{COLORS["clear"]}] [{COLORS["bold_blue"]}{utils.getDateTime()}{COLORS["clear"]}] [{COLORS["hi_blue"]}LOG{COLORS["clear"]}] {constants.USERNAME_COLORS[random.choice(list(constants.USERNAME_COLORS.keys()))]}{username}{COLORS["clear"]}: {message}')

def printSpaces(color, num):
    for i in range(0, num):
        print(f'\033{color} ', end="")
    print(COLORS['clear'])

def progressbar(it, prefix="", size=60, file=sys.stdout):
    count = len(it)
    def show(j):
        if((j/count)*100 <= 10):
            color = COLORS['bold_red']
        elif((j/count)*100 < 100):
            color = COLORS['bold_yellow']
        else:
            color = COLORS['bold_green']
        x = int(size*j/count)
        file.write("%s[%s%s%s%s] %s%i/%i%s\r" % (prefix, color, "●"*x, " "*(size-x), COLORS['clear'], color, j, count, COLORS['clear']))
        file.flush()        
    show(0)
    for i, item in enumerate(it):
        yield item
        show(i+1)
    file.write("\n")
    file.flush()