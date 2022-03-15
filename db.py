import configparser
import os
import random
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
            return None

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
        return -1
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
        return 0
    except:
        cursor.close()
        db.close()
        return -1

def downloadAllEmotes(channel_name):
    db = connect(channel_name)
    cursor = db.cursor(buffered=True)
    if not os.path.exists(constants.dirs[0]):
        os.mkdir(constants.dirs[0])
    os.chdir(constants.dirs[0])
    if not utils.globalEmotesDirectoryExists():
        os.mkdir(constants.dirs[1])
        stmt = 'SELECT url, emote_id, code FROM emotes WHERE source LIKE "1";'
        cursor.execute(stmt)
        rows = cursor.fetchall()
        counter = 0
        utils.printInfo(constants.status_messages[8])
        for row in utils.progressbar(rows):
            emote_name = row[2]
            for character in constants.bad_file_chars:
                if character in emote_name:
                    emote_name = emote_name.replace(character, str(counter))
                    counter += 1
            if('animated' in row[0]):
                extension = 'gif'
            else:
                extension = 'png'
            file_name = f'global/{emote_name}-{row[1]}.{extension}'
            stmt = f'UPDATE emotes SET path = "{file_name}" WHERE emote_id LIKE "{row[1]}" AND source LIKE "1";'
            cursor.execute(stmt)
            db.commit()
            utils.downloadFile(row[0], file_name)
    if not os.path.exists(channel_name):
        os.mkdir(channel_name)
    os.chdir(channel_name)
    stmt = 'SELECT url, emote_id, code, source FROM emotes WHERE path IS NULL;'
    cursor.execute(stmt)
    rows = cursor.fetchall()
    counter = 0
    utils.printInfo(constants.status_messages[6])
    for row in utils.progressbar(rows):
        url = row[0]
        emote_name = row[2]
        source = int(row[3])
        if(source == 2):
            if('animated' in row[0]):
                extension = 'gif'
            else:
                extension = 'png'
        elif(source == 5 or source == 6):
            extension = url.split('.')[3]
            url = url.split(f'.{extension}')[0]
        else:
            extension = 'png'
        for character in constants.bad_file_chars:
            if character in emote_name:
                emote_name = emote_name.replace(character, str(counter))
                counter += 1
        file_name = f'{emote_name}-{row[1]}.{extension}'
        stmt = f'UPDATE emotes SET path = "{file_name}" WHERE emote_id LIKE "{row[1]}" AND source NOT LIKE "1";'
        cursor.execute(stmt)
        db.commit()
        utils.downloadFile(url, file_name)
    cursor.close()
    db.close()
    os.chdir('../../')

def dropDatabase(channel_name):
    db = connect()
    cursor = db.cursor()
    if(type(channel_name) == list):
        for channel in channel_name:
            stmt = f'DROP DATABASE cc_{channel};'
            cursor.execute(stmt)
            db.commit()
            emotes_dir = f'{os.getcwd()}/emotes/{channel}'
            if os.path.exists(emotes_dir):
                shutil.rmtree(emotes_dir)
        cursor.close()
        db.close()
    else:
        stmt = f'DROP DATABASE cc_{channel_name};'
        cursor.execute(stmt)
        db.commit()
        cursor.close()
        db.close()
        emotes_dir = f'{os.getcwd()}/emotes/{channel_name}'
        if os.path.exists(emotes_dir):
            shutil.rmtree(emotes_dir)

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
    if(db == -1):
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

def getEmotes(channel_name, flag):
    emotes = []
    db = connect(channel_name)
    if(flag == 1):
        utils.printBanner()
        if(updateEmotes(channel_name) == -2):
            return -1
    cursor = db.cursor()
    stmt = 'SELECT code FROM emotes WHERE ACTIVE = 1;'
    cursor.execute(stmt)
    rows = cursor.fetchall()
    for emote in rows:
        emotes.append(str(emote[0]))
    cursor.close()
    db.close()
    return emotes

def getUserID(cursor, username):
    id = -1
    stmt = f'SELECT id FROM chatters WHERE username = "{username}";'
    cursor.execute(stmt)
    for row in cursor:
        id = row[0]
        return id
    return id

def log(channel_name, username, message, emotes, session_id):
    config = configparser.ConfigParser()
    config.read(constants.config_name)
    if(message == ''):
        return 1
    if(username == config[config_sections[1]][constants.twitch_variables[0]] and message == ''):
        return 1
    for symbol in constants.blacklisted_symbols:
        if symbol in username:
            return 1
    
    db = connect(channel_name)
    cursor = db.cursor()
    id = getUserID(cursor, username)

    date = utils.getDate()
    datetime = utils.getDateTime()

    if(id == -1):
        stmt = f'INSERT INTO chatters (username, first_date, last_date) VALUES ("{username}", "{date}", "{date}");'
        cursor.execute(stmt)
        db.commit()
        id = getUserID(cursor, username)

    if "\"" in message:
        message = message.replace("\"", "\'")

    if '\\' in message:
        message = message.replace('\\', '\\\\')

    stmt = f'INSERT INTO messages (message, session_id, chatter_id, datetime) VALUES ("{message}", {session_id}, {id}, "{datetime}");'
    cursor.execute(stmt)
    db.commit()

    stmt = f'UPDATE chatters SET last_date = "{date}" WHERE id = {id};'
    cursor.execute(stmt)
    db.commit()

    for emote in emotes:
        if '\\' in emote:
            emote = emote.replace('\\','\\\\')
        stmt = f'UPDATE emotes SET count = count + 1 WHERE code = "{emote}" AND active = 1;'
        cursor.execute(stmt)
        db.commit()

    cursor.close()
    db.close()

    if '\\\\' in message:
        message = message.replace('\\\\', '\\')

    rand = random.Random()
    username_color = rand.randrange(0,5)
    utils.printLog(channel_name, username, message, constants.username_colors[username_color])

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
    return 0

def startSession(channel_name):
    channel_name = channel_name.lower()
    if(twitch.getChannelId(channel_name) is None):
        utils.printError(constants.error_messages[2])
        return None
    db = connect(channel_name)
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
    debug = utils.getDebugMode()
    channel_id = twitch.getChannelId(channel_name)
    channel_emotes = twitch.getAllChannelEmotes(channel_name)
    current_emotes = []
    inactive_emotes = []
    previous_emotes = []
    new_emote_count = 0

    for source in constants.emote_types:
        if(channel_emotes[source] is None):
            continue
        else:
            for emote in channel_emotes[source]:
                current_emotes.append(f'{source}-{emote["id"]}')

    db = connect(channel_name)
    cursor = db.cursor()
    stmt = f'SELECT emote_id, source FROM emotes WHERE active = 1;'
    cursor.execute(stmt)
    rows = cursor.fetchall()
    for row in rows:
        source = int(row[1])
        previous_emotes.append(f'{constants.emote_types[source-1]}-{row[0]}')

    stmt = f'SELECT emote_id, source FROM emotes WHERE active = 0;'
    cursor.execute(stmt)
    rows = cursor.fetchall()
    for row in rows:
        source = int(row[1])
        inactive_emotes.append(f'{constants.emote_types[source-1]}-{row[0]}')

    A = set(current_emotes)
    B = set(previous_emotes)
    C = set(inactive_emotes)
    new_emotes = A-B
    removed_emotes = B-A
    reactivated_emotes = A.intersection(C)

    for emote in new_emotes:
        source_name = emote.split('-')[0]
        id = emote.split('-')[1]
        source = constants.emote_types.index(source_name)+1
        info = twitch.getEmoteInfoById(source, channel_id, id)
        if(info is None):
            break
        if('\\' in info['code']):
            info['code'] = info['code'].replace('\\', '\\\\')
        stmt = f'INSERT INTO emotes (code, emote_id, url, date_added, source, active) VALUES ("{info["code"]}","{id}","{info["url"]}","{utils.getDate()}","{source}",1);'
        cursor.execute(stmt)
        db.commit()
        new_emote_count += 1

    for emote in removed_emotes:
        id = emote.split('-')[1]
        stmt = f'UPDATE emotes SET active = 0 WHERE emote_id = "{id}";'
        cursor.execute(stmt)
        db.commit()
        if(debug):
            utils.printDebug(f'{debug_messages[5]} {emote} {debug_messages[6]}')
    
    for emote in reactivated_emotes:
        id = emote.split('-')[1]
        stmt = f'UPDATE emotes SET active = 1 WHERE emote_id = "{id}";'
        cursor.execute(stmt)
        db.commit()
        if(debug):
            utils.printDebug(f'{debug_messages[5]} {emote} {debug_messages[7]}')

    if(new_emote_count > 0 and utils.getDownloadOption()):
        downloadAllEmotes(channel_name)
        utils.printInfo(f'Downloaded {new_emote_count} newly active emotes.')

    cursor.close()
    db.close()
    return 0