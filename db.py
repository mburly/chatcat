import configparser
import os
import shutil

import mysql.connector

import constants
import twitch
import utils

config_sections = constants.config_sections
db_variables = constants.db_variables
debug_messages = constants.debug_messages

def connect(channel_name=None):
    config = configparser.ConfigParser()
    config.read(constants.config_name)
    if(channel_name is None):
        try:
            db = mysql.connector.connect(
                host=config[config_sections[0]][db_variables[0]],
                user=config[config_sections[0]][db_variables[1]],
                password=config[config_sections[0]][db_variables[2]]
            )
            return db
        except:
            return None
    db_name = f'cc_{channel_name}'
    try:
        db = mysql.connector.connect(
            host=config[config_sections[0]][db_variables[0]],
            user=config[config_sections[0]][db_variables[1]],
            password=config[config_sections[0]][db_variables[2]],
            database=db_name
        )
        return db
    except:
        try:
            createDB(channel_name)
            db = mysql.connector.connect(
                host=config[config_sections[0]][db_variables[0]],
                user=config[config_sections[0]][db_variables[1]],
                password=config[config_sections[0]][db_variables[2]],
                database=db_name
            )
            return db
        except:
            return -1

def createDB(channel_name):
    config = configparser.ConfigParser()
    config.read(constants.config_name)
    host = config[config_sections[0]][db_variables[0]]
    user = config[config_sections[0]][db_variables[1]]
    password = config[config_sections[0]][db_variables[2]]
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
        if(utils.getDownloadOption()):
            downloadAllEmotes(channel_name)
        utils.printBanner()
    except:
        cursor.close()
        db.close()
        return None

def downloadAllEmotesHelper(db, cursor, global_flag):
    if(global_flag):
        utils.printInfo(constants.status_messages[8])
        stmt = 'SELECT url, emote_id, code FROM emotes WHERE source LIKE "1";'
    else:
        utils.printInfo(constants.status_messages[6])
        stmt = 'SELECT url, emote_id, code, source FROM emotes WHERE path IS NULL;'
    cursor.execute(stmt)
    rows = cursor.fetchall()
    counter = 0
    for row in utils.progressbar(rows):
        url = row[0]
        emote_name = row[2]
        if(global_flag):
            source = 1
        else:
            source = int(row[3])
        for character in constants.bad_file_chars:
            if character in emote_name:
                emote_name = emote_name.replace(character, str(counter))
                counter += 1
        if(global_flag):
            if('animated' in url):
                extension = 'gif'
            else:
                extension = 'png'
            file_name = f'global/{emote_name}-{row[1]}.{extension}'
        else:
            if(source == 2):
                if('animated' in url):
                    extension = 'gif'
                else:
                    extension = 'png'
            elif(source == 5 or source == 6):
                extension = url.split('.')[3]
                url = url.split(f'.{extension}')[0]
            else:
                extension = 'png'
            file_name = f'{emote_name}-{row[1]}.{extension}'
        stmt = f'UPDATE emotes SET path = "{file_name}" WHERE emote_id LIKE "{row[1]}" AND source LIKE "{source}";'
        cursor.execute(stmt)
        db.commit()
        if(global_flag):
            utils.downloadFile(row[0], file_name)
        else:
            utils.downloadFile(url, file_name)

def downloadAllEmotes(channel_name):
    db = connect(channel_name)
    cursor = db.cursor(buffered=True)
    if not os.path.exists(constants.dirs[0]):
        os.mkdir(constants.dirs[0])
    os.chdir(constants.dirs[0])
    if not utils.globalEmotesDirectoryExists():
        os.mkdir(constants.dirs[1])
        downloadAllEmotesHelper(db, cursor, global_flag=True)
    if not os.path.exists(channel_name):
        os.mkdir(channel_name)
    os.chdir(channel_name)
    downloadAllEmotesHelper(db, cursor, global_flag=False)
    cursor.close()
    db.close()
    os.chdir('../../')

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

def getChannelActiveEmotes(channel_name, flag):
    emotes = []
    db = connect(channel_name)
    if(flag == 1):
        utils.printBanner()
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

def getEmotes(cursor, active=None, channel_emotes=None):
    emotes = []
    if(channel_emotes is not None):
        for source in constants.emote_types:
            if(channel_emotes[source] is None):
                continue
            else:
                for emote in channel_emotes[source]:
                    emotes.append(f'{source}-{emote["id"]}')
        return emotes
    else:
        emotes = []
        stmt = f'SELECT emote_id, source FROM emotes WHERE active = {active};'
        cursor.execute(stmt)
        rows = cursor.fetchall()
        for row in rows:
            source = int(row[1])
            emotes.append(f'{constants.emote_types[source-1]}-{row[0]}')
        return emotes

def getChatterId(cursor, username):
    id = None
    stmt = f'SELECT id FROM chatters WHERE username = "{username}";'
    cursor.execute(stmt)
    for row in cursor:
        id = row[0]
        return id
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
    source = constants.emote_types.index(source_name)+1
    info = twitch.getEmoteInfoById(source, channel_id, id)
    if(info is None):
        return None
    if('\\' in info['code']):
        info['code'] = info['code'].replace('\\', '\\\\')
    stmt = f'INSERT INTO emotes (code, emote_id, url, date_added, source, active) VALUES ("{info["code"]}","{id}","{info["url"]}","{utils.getDate()}","{source}",1);'
    cursor.execute(stmt)
    db.commit()

def logMessage(db, cursor, chatter_id, message, session_id):
    date = utils.getDate()
    datetime = utils.getDateTime()
    if "\"" in message:
        message = message.replace("\"", "\'")
    if '\\' in message:
        message = message.replace('\\', '\\\\')
    stmt = f'INSERT INTO messages (message, session_id, chatter_id, datetime) VALUES ("{message}", {session_id}, {chatter_id}, "{datetime}");'
    cursor.execute(stmt)
    db.commit()
    stmt = f'UPDATE chatters SET last_date = "{date}" WHERE id = {chatter_id};'
    cursor.execute(stmt)
    db.commit()
    
def logMessageEmotes(db, cursor, channel_emotes, message):
    message_emotes = utils.parseMessageEmotes(channel_emotes, message)
    for emote in message_emotes:
        if '\\' in emote:
            emote = emote.replace('\\','\\\\')
        stmt = f'UPDATE emotes SET count = count + 1 WHERE code = "{emote}" AND active = 1;'
        cursor.execute(stmt)
        db.commit()

def log(channel_name, username, message, channel_emotes, session_id):
    if(username is None or message == ''):
        return None
    db = connect(channel_name)
    cursor = db.cursor()
    id = getChatterId(cursor, username)
    if(id is None):
        id = logChatter(db, cursor, username)
    logMessage(db, cursor, id, message, session_id)
    logMessageEmotes(db, cursor, channel_emotes, message)
    cursor.close()
    db.close()
    utils.printLog(channel_name, username, message)

def populateEmotesTable(channel_name):
    emotes = twitch.getAllChannelEmotes(channel_name)
    db = connect(channel_name)
    cursor = db.cursor()
    source = 1
    for emote_type in constants.emote_types:
        if(emotes[emote_type] is None):
            source += 1
            continue
        for emote in emotes[emote_type]:
            emote_name = emote['code']
            if '\\' in emote_name:
                emote_name = emote_name.replace('\\', '\\\\')
            if(source == 1):
                stmt = f'INSERT INTO emotes (code, emote_id, url, path, date_added, source, active) VALUES ("{emote_name}","{emote["id"]}","{emote["url"]}","global/{emote_name}","{utils.getDate()}","{source}",1);'    
            else:
                stmt = f'INSERT INTO emotes (code, emote_id, url, date_added, source, active) VALUES ("{emote_name}","{emote["id"]}","{emote["url"]}","{utils.getDate()}","{source}",1);'
            cursor.execute(stmt)
            db.commit()
        source += 1
    cursor.close()
    db.close()

def setEmotesStatus(db, cursor, emotes, active):
    for emote in emotes:
        id = emote.split('-')[1]
        stmt = f'UPDATE emotes SET active = {active} WHERE emote_id = "{id}";'
        cursor.execute(stmt)
        db.commit()
        if(utils.getDebugMode()):
            if(active):
                utils.printDebug(f'{debug_messages[5]} {emote} {debug_messages[7]}')
            else:
                utils.printDebug(f'{debug_messages[5]} {emote} {debug_messages[6]}')

def startSession(channel_name):
    channel_name = channel_name.lower()
    if(twitch.getChannelId(channel_name) is None):
        utils.printError(constants.error_messages[2])
        return None
    db = connect(channel_name)
    if(db == -1):
        utils.printError(constants.error_messages[4])
        return None
    if(db is None):
        return None
    cursor = db.cursor()
    datetime = utils.getDateTime()
    stream_title = twitch.getStreamTitle(channel_name)
    if(stream_title is None):
        stream_title = constants.unknown_stream_title
    stmt = f'INSERT INTO sessions (stream_title, start_datetime) VALUES ("{stream_title}", "{datetime}")'
    cursor.execute(stmt)
    db.commit()
    id = cursor.lastrowid
    cursor.close()
    db.close()
    return id

def updateEmotes(channel_name):
    utils.printInfo(constants.status_messages[9])
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
        logEmote(db, cursor, emote, channel_id)
        new_emote_count += 1
    setEmotesStatus(db, cursor, removed_emotes, 0)
    setEmotesStatus(db, cursor, reactivated_emotes, 1)
    if(new_emote_count > 0 and utils.getDownloadOption()):
        downloadAllEmotes(channel_name)
        utils.printInfo(f'Downloaded {new_emote_count} newly active emotes.')
    cursor.close()
    db.close()