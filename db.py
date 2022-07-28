import configparser
import os
import shutil

import mysql.connector

import constants
import interface
import twitch
import utils

CONFIG_SECTIONS = constants.CONFIG_SECTIONS
DB_VARIABLES = constants.DB_VARIABLES
DEBUG_MESSAGES = constants.DEBUG_MESSAGES
ERROR_MESSAGES = constants.ERROR_MESSAGES
STATUS_MESSAGES = constants.STATUS_MESSAGES
DIRS = constants.DIRS
EMOTE_TYPES = constants.EMOTE_TYPES

def connect(channel_name=None):
    if(channel_name is None):
        try:
            db = connectHelper()
            return db
        except:
            return None
    db_name = f'cc_{channel_name}'
    try:
        db = connectHelper(db_name)
        return db
    except:
        try:
            createDB(channel_name)
            db = connectHelper(db_name)
            return db
        except:
            return -1

def connectHelper(db_name=None):
    config = configparser.ConfigParser()
    config.read(constants.CONFIG_NAME)
    if(db_name is None):
        db = mysql.connector.connect(
            host=config[CONFIG_SECTIONS[0]][DB_VARIABLES[0]],
            user=config[CONFIG_SECTIONS[0]][DB_VARIABLES[1]],
            password=config[CONFIG_SECTIONS[0]][DB_VARIABLES[2]]
        )
        return db
    else:
        db = mysql.connector.connect(
            host=config[CONFIG_SECTIONS[0]][DB_VARIABLES[0]],
            user=config[CONFIG_SECTIONS[0]][DB_VARIABLES[1]],
            password=config[CONFIG_SECTIONS[0]][DB_VARIABLES[2]],
            database=db_name
        )
        return db

def createDB(channel_name):
    config = configparser.ConfigParser()
    config.read(constants.CONFIG_NAME)
    host = config[CONFIG_SECTIONS[0]][DB_VARIABLES[0]]
    user = config[CONFIG_SECTIONS[0]][DB_VARIABLES[1]]
    password = config[CONFIG_SECTIONS[0]][DB_VARIABLES[2]]
    try:
        db = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
    except:
        return None
    cursor = db.cursor()
    try:
        db_name = f'cc_{channel_name}'
        stmt = f'CREATE DATABASE IF NOT EXISTS {db_name} COLLATE utf8mb4_general_ci;'
        cursor.execute(stmt)
        db = connect(channel_name)
        cursor = db.cursor()
        stmt = f'CREATE TABLE chatters (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(512), first_date VARCHAR(255), last_date VARCHAR(255)) COLLATE utf8mb4_general_ci;'
        cursor.execute(stmt)
        stmt = f'CREATE TABLE messages (id INT AUTO_INCREMENT PRIMARY KEY, message VARCHAR(512) COLLATE utf8mb4_general_ci, session_id INT, chatter_id INT, datetime VARCHAR(255)) COLLATE utf8mb4_general_ci;'
        cursor.execute(stmt)
        stmt = f'CREATE TABLE sessions (id INT AUTO_INCREMENT PRIMARY KEY, stream_title VARCHAR(512) COLLATE utf8mb4_general_ci, start_datetime VARCHAR(255), end_datetime VARCHAR(255)) COLLATE utf8mb4_general_ci;'
        cursor.execute(stmt)
        stmt = f'CREATE TABLE emotes (id INT AUTO_INCREMENT PRIMARY KEY, code VARCHAR(255) COLLATE utf8mb4_general_ci, emote_id VARCHAR(255) COLLATE utf8mb4_general_ci, count INT DEFAULT 0, url VARCHAR(512) COLLATE utf8mb4_general_ci, path VARCHAR(512) COLLATE utf8mb4_general_ci, date_added VARCHAR(255) COLLATE utf8mb4_general_ci, source VARCHAR(255) COLLATE utf8mb4_general_ci, active BOOLEAN) COLLATE utf8mb4_general_ci;'
        cursor.execute(stmt)
        cursor.close()
        db.close()
        populateEmotesTable(channel_name)
        if(utils.getDownloadMode()):
            downloadEmotes(channel_name)
    except:
        cursor.close()
        db.close()
        return None

def downloadEmotesHelper(db, channel_name):
    interface.printInfo(channel_name, STATUS_MESSAGES['downloading'])
    stmt = 'SELECT url, emote_id, code, source FROM emotes WHERE path IS NULL;'
    cursor = db.cursor(buffered=True)
    cursor.execute(stmt)
    rows = cursor.fetchall()
    channel_emotes_dir = f'{DIRS["emotes"]}/{channel_name}'
    global_emotes_dir = f'{DIRS["emotes"]}/{DIRS["global"]}'
    for row in interface.progressbar(rows):
        url = row[0]
        emote_name = utils.removeSymbolsFromName(row[2])
        source = int(row[3])
        if(source == 1 or source == 2):
            if('animated' in url):
                extension = 'gif'
            else:
                extension = 'png'
        elif(source == 5 or source == 6):
            extension = url.split('.')[3]
            url = url.split(f'.{extension}')[0]
        else:
            extension = 'png'
        if(source == 1):
            file_name = f'{global_emotes_dir}/{emote_name}-{row[1]}.{extension}'
        else:
            file_name = f'{channel_emotes_dir}/{emote_name}-{row[1]}.{extension}'
        stmt = f'UPDATE emotes SET path = "{file_name}" WHERE emote_id LIKE "{row[1]}" AND source LIKE "{source}";'
        cursor.execute(stmt)
        db.commit()
        utils.downloadFile(url, file_name)
    cursor.close()

def downloadEmotes(channel_name):
    db = connect(channel_name)
    # Create emotes directory if doesn't exist
    if not os.path.exists(DIRS["emotes"]):
        os.mkdir(DIRS["emotes"])
    # Create channel emotes directory if it doesn't exist
    channel_emotes_dir = f'{DIRS["emotes"]}/{channel_name}'
    if not os.path.exists(channel_emotes_dir):
        os.mkdir(channel_emotes_dir)
    # Create global emotes directory if it doesn't exist
    global_emotes_dir = f'{DIRS["emotes"]}/{DIRS["global"]}'
    if not os.path.exists(global_emotes_dir):
        os.mkdir(global_emotes_dir)
    downloadEmotesHelper(db, channel_name)
    db.close()

def dropDatabase(db, cursor, channel_name):
    stmt = f'DROP DATABASE cc_{channel_name};'
    cursor.execute(stmt)
    db.commit()
    emotes_dir = f'{os.getcwd()}/emotes/{channel_name}'
    if os.path.exists(emotes_dir):
        shutil.rmtree(emotes_dir)

def dropDatabaseHandler(channel_name):
    db = connect()
    cursor = db.cursor()
    if(type(channel_name) == list):
        for channel in channel_name:
            dropDatabase(db, cursor, channel)
    else:
        dropDatabase(db, cursor, channel_name)
    cursor.close()
    db.close()

def endSession(channel_name):
    channel_name = channel_name.lower()
    if twitch.getChannelId(channel_name) is None:
        return None
    db = connect(channel_name)
    if(db is None):
        return None
    datetime = utils.getDateTime()
    cursor = db.cursor()
    stmt = f'SELECT MAX(id) FROM sessions'
    cursor.execute(stmt)
    rows = cursor.fetchall()
    id = rows[0][0]
    stmt = f'UPDATE sessions SET end_datetime = "{datetime}" WHERE id = {id}'
    cursor.execute(stmt)
    db.commit()
    cursor.close()
    db.close()
    return id

def getDatabases():
    db = connect()
    if(db is None):
        return []
    cursor = db.cursor()
    stmt = 'SHOW DATABASES;'
    cursor.execute(stmt)
    databases = []
    for row in cursor.fetchall():
        if 'cc_' in row[0]:
            databases.append(row[0].split('cc_')[1])
    cursor.close()
    db.close()
    return databases

def getChannelActiveEmotes(channel_name, initial_run=False):
    emotes = []
    db = connect(channel_name)
    if(initial_run):
        updateEmotes(channel_name)
    cursor = db.cursor()
    stmt = 'SELECT code FROM emotes WHERE ACTIVE = 1;'
    cursor.execute(stmt)
    rows = cursor.fetchall()
    for emote in rows:
        emotes.append(str(emote[0]))
    cursor.close()
    db.close()
    return emotes

# Returns in format: <source>-<emote_id>
def getEmotes(cursor, active=None, channel_emotes=None):
    emotes = []
    if(channel_emotes is not None):
        for source in EMOTE_TYPES:
            if(channel_emotes[source] is None):
                continue
            else:
                for emote in channel_emotes[source]:
                    emotes.append(f'{source}-{emote.id}')
        return emotes
    else:
        emotes = []
        stmt = f'SELECT emote_id, source FROM emotes WHERE active = {active};'
        cursor.execute(stmt)
        rows = cursor.fetchall()
        for row in rows:
            source = int(row[1])
            emotes.append(f'{EMOTE_TYPES[source-1]}-{row[0]}')
        return emotes

def getChatterId(db, cursor, username):
    id = None
    stmt = f'SELECT id FROM chatters WHERE username = "{username}";'
    cursor.execute(stmt)
    for row in cursor:
        id = row[0]
        return id
    id = logChatter(db, cursor, username)
    return id

def logChatter(db, cursor, username):
    date = utils.getDate()
    stmt = f'INSERT INTO chatters (username, first_date, last_date) VALUES ("{username}", "{date}", "{date}");'
    cursor.execute(stmt)
    db.commit()
    return cursor.lastrowid

def logEmote(db, cursor, emote, channel_id):
    source_name = emote.split('-')[0]
    id = emote.split('-')[1]
    source = EMOTE_TYPES.index(source_name)+1
    emote = twitch.getEmoteInfoById(source, channel_id, id)
    if(emote is None):
        return None
    if('\\' in emote.code):
        emote.code = emote.code.replace('\\', '\\\\')
    stmt = f'INSERT INTO emotes (code, emote_id, url, date_added, source, active) VALUES ("{emote.code}","{id}","{emote.url}","{utils.getDate()}","{source}",1);'
    cursor.execute(stmt)
    db.commit()

def logMessage(db, cursor, chatter_id, message, session_id):
    if "\"" in message:
        message = message.replace("\"", "\'")
    if '\\' in message:
        message = message.replace('\\', '\\\\')
    stmt = f'INSERT INTO messages (message, session_id, chatter_id, datetime) VALUES ("{message}", {session_id}, {chatter_id}, "{utils.getDateTime()}");'
    cursor.execute(stmt)
    db.commit()
    stmt = f'UPDATE chatters SET last_date = "{utils.getDate()}" WHERE id = {chatter_id};'
    cursor.execute(stmt)
    db.commit()
    
def logMessageEmotes(db, cursor, channel_emotes, message):
    message_emotes = utils.parseMessageEmotes(channel_emotes, message)
    for emote in message_emotes:
        if '\\' in emote:
            emote = emote.replace('\\','\\\\')
        stmt = f'UPDATE emotes SET count = count + 1 WHERE code = BINARY "{emote}" AND active = 1;'
        cursor.execute(stmt)
        db.commit()

def log(channel_name, username, message, channel_emotes, session_id):
    if(username is None or message == '' or message == 'tmi.twitch.tv'):
        return None
    db = connect(channel_name)
    cursor = db.cursor()
    id = getChatterId(db, cursor, username)
    logMessage(db, cursor, id, message, session_id)
    logMessageEmotes(db, cursor, channel_emotes, message)
    cursor.close()
    db.close()

def populateEmotesTable(channel_name):
    emotes = twitch.getAllChannelEmotes(channel_name)
    db = connect(channel_name)
    cursor = db.cursor()
    source = 1
    global_emotes_dir = f'{DIRS["emotes"]}/{DIRS["global"]}'
    for emote_type in EMOTE_TYPES:
        if(emotes[emote_type] is None):         # No emotes from source found
            source += 1
            continue
        for emote in emotes[emote_type]:
            emote_name = emote.code
            if '\\' in emote_name:
                emote_name = emote_name.replace('\\', '\\\\')
            if(source == 1):
                stmt = f'INSERT INTO emotes (code, emote_id, url, path, date_added, source, active) VALUES ("{emote_name}","{emote.id}","{emote.url}","{global_emotes_dir}/{utils.removeSymbolsFromName(emote_name)}-{emote.id}.png","{utils.getDate()}","{source}",1);'    
            else:
                stmt = f'INSERT INTO emotes (code, emote_id, url, date_added, source, active) VALUES ("{emote_name}","{emote.id}","{emote.url}","{utils.getDate()}","{source}",1);'    
            cursor.execute(stmt)
            db.commit()
        source += 1
    cursor.close()
    db.close()

def setEmotesStatus(channel_name, db, cursor, emotes, active):
    for emote in emotes:
        id = emote.split('-')[1]
        stmt = f'UPDATE emotes SET active = {active} WHERE emote_id = "{id}";'
        cursor.execute(stmt)
        db.commit()
        if(utils.getDebugMode()):
            if(active):
                interface.printDebug(f'{DEBUG_MESSAGES["set_emote"]} {emote} {DEBUG_MESSAGES["reactivated"]}', channel_name)
            else:
                interface.printDebug(f'{DEBUG_MESSAGES["set_emote"]} {emote} {DEBUG_MESSAGES["inactive"]}', channel_name)

def startSession(channel_name):
    if(twitch.getChannelId(channel_name) is None):
        interface.printError(ERROR_MESSAGES['channel'])
        return None
    db = connect(channel_name)
    if(db == -1):
        interface.printError(ERROR_MESSAGES['database'])
        return None
    if(db is None):
        return None
    cursor = db.cursor()
    stream_title = twitch.getStreamTitle(channel_name)
    stmt = f'INSERT INTO sessions (stream_title, start_datetime) VALUES ("{stream_title}", "{utils.getDateTime()}")'
    cursor.execute(stmt)
    db.commit()
    id = cursor.lastrowid
    cursor.close()
    db.close()
    return id

def updateEmotes(channel_name):
    interface.printInfo(channel_name, STATUS_MESSAGES['updates'])
    new_emote_count = 0
    db = connect(channel_name)
    cursor = db.cursor()
    channel_id = twitch.getChannelId(channel_name)
    channel_emotes = twitch.getAllChannelEmotes(channel_name)
    current_emotes = getEmotes(cursor, channel_emotes=channel_emotes)
    previous_emotes = getEmotes(cursor, active=1)
    inactive_emotes = getEmotes(cursor, active=0)
    A = set(current_emotes)
    B = set(previous_emotes)
    C = set(inactive_emotes)
    new_emotes = A-B
    removed_emotes = B-A
    reactivated_emotes = A.intersection(C)
    for emote in new_emotes:
        if(emote in reactivated_emotes):
            continue
        interface.printInfo(channel_name, f'Logging {emote}')
        logEmote(db, cursor, emote, channel_id)
        new_emote_count += 1
    setEmotesStatus(channel_name, db, cursor, removed_emotes, 0)
    setEmotesStatus(channel_name, db, cursor, reactivated_emotes, 1)
    if(new_emote_count > 0 and utils.getDownloadMode()):
        downloadEmotes(channel_name)
        interface.printInfo(channel_name, f'Downloaded {new_emote_count} newly active emotes.')
    cursor.close()
    db.close()