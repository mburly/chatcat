import configparser
import os
import random
import sys

import constants
import db
import utils

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
    if not utils.getDebugMode():
        os.system('cls' if os.name=='nt' else 'clear')

def handleConfigMenu():
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
    return utils.createConfig(host, user, password, nickname, token, key)

def handleDatabaseMenu():
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

def handleDebugMenu(selection):
    config = configparser.ConfigParser()
    config.read(config_name)
    debug = utils.getDebugMode()
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

def handleDownloadMenu(selection):
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

def printLogo():
    cls()
    print(f'\n{constants.BANNER}')

def printBanner():
    config = configparser.ConfigParser()
    config.read(config_name)
    cls()
    print(f'\n{constants.BANNER}')
    if(utils.getDownloadMode() == True):
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
            handleDownloadMenu(selection)
        else:
            printError(error_messages['selection'])
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
        selection = input(f'{input_messages["selection"]} ')
        try:
            selection = int(selection)
        except:
            printError(error_messages['selection'])
            return -1
        if(selection == 1 or selection == 2):
            handleDebugMenu(selection)
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

def printDebug(text):
    print(f'[{colors["bold_blue"]}{utils.getDateTime()}{colors["clear"]}] [{colors["yellow"]}DEBUG{colors["clear"]}] {text}')

def printError(text):
    print(f'[{colors["bold_blue"]}{utils.getDateTime()}{colors["clear"]}] [{colors["hi_red"]}ERROR{colors["clear"]}] {text}')
    input()

def printInfo(text):
    print(f'[{colors["bold_blue"]}{utils.getDateTime()}{colors["clear"]}] [{colors["hi_green"]}INFO{colors["clear"]}] {text}')

def printLog(channel_name, username, message):
    if '\\\\' in message:
        message = message.replace('\\\\', '\\')
    rand = random.Random()
    username_color = rand.randrange(0,5)
    print(f'[{colors["bold_green"]}{channel_name}{colors["clear"]}] [{colors["bold_blue"]}{utils.getDateTime()}{colors["clear"]}] [{colors["hi_blue"]}LOG{colors["clear"]}] {constants.USERNAME_COLORS[username_color]}{username}{colors["clear"]}: {message}')

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