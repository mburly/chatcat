import configparser
import os

import mysql.connector

import constants
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
            createDb(channel_name)
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

def createDb(channel_name):
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
        cursor.execute(stmtCreateDatabase(channel_name))
        db = connect(channel_name)
        cursor = db.cursor()
        cursor.execute(stmtCreateChattersTable())
        cursor.execute(stmtCreateSessionsTable())
        cursor.execute(stmtCreateMessagesTable())
        cursor.execute(stmtCreateEmotesTable())
        cursor.execute(stmtCreateLogsTable())
        cursor.execute(stmtCreateTopEmotesProcedure(channel_name))
        cursor.execute(stmtCreateTopChattersProcedure(channel_name))
        cursor.execute(stmtCreateRecentSessionsProcedure(channel_name))
        try:
            cursor.execute(stmtCreateEmoteStatusChangeTrigger())
        except:
            pass
        cursor.close()
        db.close()
        populateEmotesTable(channel_name)
        downloadEmotes(channel_name)
    except:
        cursor.close()
        db.close()
        return None

def downloadEmotesHelper(db, channel_name):
    utils.printInfo(channel_name, STATUS_MESSAGES['downloading'])
    cursor = db.cursor(buffered=True)
    cursor.execute(stmtSelectEmotesToDownload())
    rows = cursor.fetchall()
    channel_emotes_dir = f'{DIRS["emotes"]}/{channel_name}'
    global_emotes_dir = f'{DIRS["emotes"]}/{DIRS["global"]}'
    for row in rows:
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
            path = f'{global_emotes_dir}/{emote_name}-{row[1]}.{extension}'
        else:
            path = f'{channel_emotes_dir}/{emote_name}-{row[1]}.{extension}'
        cursor.execute(stmtUpdateEmotePath(path, row[1], source))
        db.commit()
        utils.downloadFile(url, path)
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

def endSession(channel_name):
    channel_name = channel_name.lower()
    if twitch.getChannelId(channel_name) is None:
        return None
    db = connect(channel_name)
    if(db is None):
        return None
    cursor = db.cursor()
    cursor.execute(stmtSelectMostRecentSession())
    rows = cursor.fetchall()
    id = rows[0][0]
    cursor.execute(stmtUpdateSessionEndDatetime(id))
    db.commit()
    cursor.close()
    db.close()
    return id

def getChannelActiveEmotes(channel_name):
    emotes = []
    db = connect(channel_name)
    updateEmotes(channel_name)
    cursor = db.cursor()
    cursor.execute(stmtSelectActiveEmotes())
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
        cursor.execute(stmtSelectEmoteByStatus(active))
        rows = cursor.fetchall()
        for row in rows:
            source = int(row[1])
            emotes.append(f'{EMOTE_TYPES[source-1]}-{row[0]}')
        return emotes

def getChatterId(db, cursor, username):
    id = None
    cursor.execute(stmtSelectChatterIdByUsername(username))
    for row in cursor:
        id = row[0]
        return id
    id = logChatter(db, cursor, username)
    return id

def logChatter(db, cursor, username):
    cursor.execute(stmtInsertNewChatter(username))
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
    cursor.execute(stmtInsertNewEmote(emote.code, id, emote.url, source))
    db.commit()

def logMessage(db, cursor, chatter_id, message, session_id):
    if "\"" in message:
        message = message.replace("\"", "\'")
    if '\\' in message:
        message = message.replace('\\', '\\\\')
    cursor.execute(stmtInsertNewMessage(message, session_id, chatter_id))
    db.commit()
    cursor.execute(stmtUpdateChatterLastDate(chatter_id))
    db.commit()
    
def logMessageEmotes(db, cursor, channel_emotes, message):
    message_emotes = utils.parseMessageEmotes(channel_emotes, message)
    for emote in message_emotes:
        if '\\' in emote:
            emote = emote.replace('\\','\\\\')
        cursor.execute(stmtUpdateEmoteCount(emote))
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
    for emote_type in EMOTE_TYPES:
        if(emotes[emote_type] is None):         # No emotes from source found
            source += 1
            continue
        for emote in emotes[emote_type]:
            emote_name = emote.code
            if '\\' in emote_name:
                emote_name = emote_name.replace('\\', '\\\\')
            if(source == 1):
                cursor.execute(stmtInsertNewGlobalEmote(emote_name, emote.id, emote.url, source))
            else:
                cursor.execute(stmtInsertNewThirdPartyEmote(emote_name, emote.id, emote.url, source))
            db.commit()
        source += 1
    cursor.close()
    db.close()

def setEmotesStatus(channel_name, db, cursor, emotes, active):
    for emote in emotes:
        id = emote.split('-')[1]
        cursor.execute(stmtUpdateEmoteStatus(active, id))
        db.commit()
        if(active):
            utils.printInfo(channel_name, f'{DEBUG_MESSAGES["set_emote"]} {emote} {DEBUG_MESSAGES["reactivated"]}')
        else:
            utils.printInfo(channel_name, f'{DEBUG_MESSAGES["set_emote"]} {emote} {DEBUG_MESSAGES["inactive"]}')

def startSession(channel_name):
    if(twitch.getChannelId(channel_name) is None):
        utils.printError(ERROR_MESSAGES['channel'])
        return None
    db = connect(channel_name)
    if(db == -1):
        utils.printError(ERROR_MESSAGES['database'])
        return None
    if(db is None):
        return None
    cursor = db.cursor()
    stream_title = twitch.getStreamTitle(channel_name)
    cursor.execute(stmtInsertNewSession(stream_title))
    db.commit()
    id = cursor.lastrowid
    cursor.close()
    db.close()
    return id

def updateEmotes(channel_name):
    utils.printInfo(channel_name, STATUS_MESSAGES['updates'])
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
        utils.printInfo(channel_name, f'Logging {emote}')
        logEmote(db, cursor, emote, channel_id)
        new_emote_count += 1
    setEmotesStatus(channel_name, db, cursor, removed_emotes, 0)
    setEmotesStatus(channel_name, db, cursor, reactivated_emotes, 1)
    if(new_emote_count > 0):
        downloadEmotes(channel_name)
        utils.printInfo(channel_name, f'Downloaded {new_emote_count} newly active emotes.')
    cursor.close()
    db.close()
    utils.printInfo(channel_name, STATUS_MESSAGES['updates_complete'])


def stmtCreateDatabase(channel_name):
    return f'CREATE DATABASE IF NOT EXISTS cc_{channel_name} COLLATE utf8mb4_general_ci;'

def stmtCreateChattersTable():
    return f'CREATE TABLE chatters (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(512), first_date DATE, last_date DATE) COLLATE utf8mb4_general_ci;'

def stmtCreateSessionsTable():
    return f'CREATE TABLE sessions (id INT AUTO_INCREMENT PRIMARY KEY, stream_title VARCHAR(512) COLLATE utf8mb4_general_ci, start_datetime DATETIME, end_datetime DATETIME) COLLATE utf8mb4_general_ci;'

def stmtCreateMessagesTable():
    return  f'CREATE TABLE messages (id INT AUTO_INCREMENT PRIMARY KEY, message VARCHAR(512) COLLATE utf8mb4_general_ci, session_id INT, chatter_id INT, datetime DATETIME, FOREIGN KEY (session_id) REFERENCES sessions(id), FOREIGN KEY (chatter_id) REFERENCES chatters(id)) COLLATE utf8mb4_general_ci;'

def stmtCreateEmotesTable():
    return f'CREATE TABLE emotes (id INT AUTO_INCREMENT PRIMARY KEY, code VARCHAR(255) COLLATE utf8mb4_general_ci, emote_id VARCHAR(255) COLLATE utf8mb4_general_ci, count INT DEFAULT 0, url VARCHAR(512) COLLATE utf8mb4_general_ci, path VARCHAR(512) COLLATE utf8mb4_general_ci, date_added DATE, source VARCHAR(255) COLLATE utf8mb4_general_ci, active BOOLEAN) COLLATE utf8mb4_general_ci;'

def stmtCreateTopEmotesProcedure(channel_name):
    return f'CREATE PROCEDURE cc_{channel_name}.topEmotes() BEGIN SELECT code, count, path FROM cc_{channel_name}.EMOTES GROUP BY code ORDER BY count DESC LIMIT 10; END'

def stmtCreateTopChattersProcedure(channel_name):
    return f'CREATE PROCEDURE cc_{channel_name}.topChatters() BEGIN SELECT c.username, COUNT(m.id) FROM cc_{channel_name}.MESSAGES m INNER JOIN cc_{channel_name}.CHATTERS c ON m.chatter_id=c.id GROUP BY c.username ORDER BY COUNT(m.id) DESC LIMIT 10; END'

def stmtCreateRecentSessionsProcedure(channel_name):
    return f'CREATE PROCEDURE cc_{channel_name}.recentSessions() BEGIN SELECT id, stream_title, DATE_FORMAT(end_datetime, "%c/%e/%Y"), TIMEDIFF(end_datetime, start_datetime) FROM cc_{channel_name}.SESSIONS ORDER BY id DESC LIMIT 5; END'

def stmtCreateLogsTable():
    return f'CREATE TABLE logs (id INT AUTO_INCREMENT PRIMARY KEY, emote_id INT, old INT, new INT, datetime DATETIME) COLLATE utf8mb4_general_ci;'

def stmtCreateEmoteStatusChangeTrigger():
    return f'CREATE TRIGGER emote_status_change AFTER UPDATE ON emotes FOR EACH ROW IF OLD.active != NEW.active THEN INSERT INTO logs (emote_id, new, old, datetime) VALUES (OLD.id, NEW.active, OLD.active, UTC_TIMESTAMP()); END IF;//'

def stmtSelectEmotesToDownload():
    return f'SELECT url, emote_id, code, source FROM emotes WHERE path IS NULL;'

def stmtUpdateEmotePath(path, emote_id, source):
    return f'UPDATE emotes SET path = "{path}" WHERE emote_id LIKE "{emote_id}" AND source LIKE "{source}";'

def stmtSelectMostRecentSession():
    return f'SELECT MAX(id) FROM sessions'

def stmtUpdateSessionEndDatetime(session_id):
    return f'UPDATE sessions SET end_datetime = "{utils.getDateTime()}" WHERE id = {session_id}'

def stmtSelectActiveEmotes():
    return f'SELECT code FROM emotes WHERE ACTIVE = 1;'

def stmtSelectEmoteByStatus(active):
    return f'SELECT emote_id, source FROM emotes WHERE active = {active};'

def stmtSelectChatterIdByUsername(username):
    return f'SELECT id FROM chatters WHERE username = "{username}";'

def stmtInsertNewChatter(username):
    return f'INSERT INTO chatters (username, first_date, last_date) VALUES ("{username}", "{utils.getDate()}", "{utils.getDate()}");'

def stmtInsertNewEmote(code, emote_id, url, source):
    return f'INSERT INTO emotes (code, emote_id, url, date_added, source, active) VALUES ("{code}","{emote_id}","{url}","{utils.getDate()}","{source}",1);'    

def stmtInsertNewMessage(message, session_id, chatter_id):
    return f'INSERT INTO messages (message, session_id, chatter_id, datetime) VALUES ("{message}", {session_id}, {chatter_id}, "{utils.getDateTime()}");'    

def stmtUpdateChatterLastDate(chatter_id):
    return f'UPDATE chatters SET last_date = "{utils.getDate()}" WHERE id = {chatter_id};'

def stmtUpdateEmoteCount(emote):
    return f'UPDATE emotes SET count = count + 1 WHERE code = BINARY "{emote}" AND active = 1;'

def stmtInsertNewGlobalEmote(emote_name, emote_id, url, source):
    return f'INSERT INTO emotes (code, emote_id, url, path, date_added, source, active) VALUES ("{emote_name}","{emote_id}","{url}","{DIRS["global_emotes"]}/{utils.removeSymbolsFromName(emote_name)}-{emote_id}.png","{utils.getDate()}","{source}",1);'

def stmtInsertNewThirdPartyEmote(emote_name, emote_id, url, source):
    return f'INSERT INTO emotes (code, emote_id, url, date_added, source, active) VALUES ("{emote_name}","{emote_id}","{url}","{utils.getDate()}","{source}",1);'  

def stmtUpdateEmoteStatus(active, emote_id):
    return f'UPDATE emotes SET active = {active} WHERE emote_id = "{emote_id}";'

def stmtInsertNewSession(stream_title):
    return f'INSERT INTO sessions (stream_title, start_datetime) VALUES ("{stream_title}", "{utils.getDateTime()}")'