import configparser
import os
import sys

import constants
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
    else:
        return None

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