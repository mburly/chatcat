import configparser
import os

import mysql.connector

import constants
import twitch
import utils

debug = constants.debug
debug_messages = constants.debug_messages

def connect(channel_name):
    config = configparser.ConfigParser()
    config.read(constants.config_name)
    db_name = f'cc_{channel_name}'
    if(os.name == 'nt'):
        try:
            db = mysql.connector.connect(
                host=config['db']['host'],
                user=config['db']['user'],
                password=config['db']['password'],
                database=db_name
            )
            return db
        except:
            createDB(channel_name)
            db = mysql.connector.connect(
                host=config['db']['host'],
                user=config['db']['user'],
                password=config['db']['password'],
                database=db_name
            )
            return db
    else:
        try:
            db = mysql.connector.connect(
                host=config['db']['host'],
                user=config['db']['user'],
                password=config['db']['password'],
                database=db_name,
                charset='utf8mb4'
            )
            return db
        except:
            createDB(channel_name)
            db = mysql.connector.connect(
                host=config['db']['host'],
                user=config['db']['user'],
                password=config['db']['password'],
                database=db_name,
                charset='utf8mb4'
            )
            return db

def createDB(channel_name):
    config = configparser.ConfigParser()
    config.read(constants.config_name)
    host = config['db']['host']
    user = config['db']['user']
    password = config['db']['password']
    db = mysql.connector.connect(
        host=host,
        user=user,
        password=password
    )
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
        stmt = f'CREATE TABLE emotes (id INT AUTO_INCREMENT PRIMARY KEY, code VARCHAR(255) COLLATE utf8mb4_general_ci, emote_id VARCHAR(255) COLLATE utf8mb4_general_ci, variant INT, count INT DEFAULT 0, url VARCHAR(512) COLLATE utf8mb4_general_ci, path VARCHAR(512) COLLATE utf8mb4_general_ci, date_added VARCHAR(255) COLLATE utf8mb4_general_ci, source VARCHAR(255) COLLATE utf8mb4_general_ci, active BOOLEAN) COLLATE utf8mb4_general_ci;'
        cursor.execute(stmt)
        cursor.close()
        db.close()
        populateEmotes(channel_name)
        downloadAllEmotes(channel_name)
        return 0
    except:
        return -1

def downloadAllEmotes(channel_name):
    db = connect(channel_name)
    cursor = db.cursor(buffered=True)
    if not os.path.exists(constants.dirs[0]):
        os.mkdir(constants.dirs[0])
    os.chdir(constants.dirs[0])
    if not os.path.exists(channel_name):
        os.mkdir(channel_name)
    os.chdir(channel_name)
    stmt = 'SELECT url, emote_id, code FROM emotes WHERE source NOT LIKE "1" AND path IS NULL;'
    cursor.execute(stmt)
    rows = cursor.fetchall()
    counter = 0
    print(constants.status_messages[6])
    for row in utils.progressbar(rows):
        emote_name = row[2]
        for character in constants.bad_file_chars:
            if character in emote_name:
                emote_name = emote_name.replace(character, str(counter))
                counter += 1
        file_name = f'{emote_name}-{row[1]}.gif'
        stmt = f'UPDATE emotes SET path = "{file_name}" WHERE emote_id LIKE "{row[1]}" AND source NOT LIKE "1";'
        cursor.execute(stmt)
        db.commit()
        utils.downloadFile(row[0], file_name)
    cursor.close()
    db.close()
    os.chdir('../../')

def getEmotes(channel_name, flag):
    emotes = []
    db = connect(channel_name)
    
    if(flag == 1):
        for i in range(1, len(constants.emote_types)+1):
            updateEmotes(channel_name, i)

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
    if(username == config['twitch']['nickname'] and message == ''):
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

    utils.printLog(channel_name, username, message)

def populateEmotes(channel_name):
    emotes = twitch.getAllChannelEmoteInfo(channel_name)
    emote_types = list(emotes.keys())
    db = connect(channel_name)
    cursor = db.cursor()
    source = 1
    for emote_type in emote_types:
        for emote in emotes[emote_type]:
            emote_name = emote['code']
            if(len(emote['url']) > 2):
                url = emote['url'][2]
            else:
                url = emote['url'][0]
            if '\\' in emote_name:
                emote_name = emote_name.replace('\\', '\\\\')
            emote_id = emote['id']
            stmt = f'INSERT INTO emotes (code, emote_id, variant, url, date_added, source, active) VALUES ("{emote_name}","{emote_id}",0,"{url}","{utils.getDate()}","{source}",1);'
            cursor.execute(stmt)
            db.commit()
        source += 1
    cursor.close()
    db.close()
    return 0

def updateEmotes(channel_name, source):
    if(constants.debug):
        utils.printDebug(f'{debug_messages[4]} {constants.emote_types[source-1]}')
    channel_id = twitch.getChannelId(channel_name)
    if(source == 1):
        emotes = twitch.getGlobalEmotes()
    elif(source == 2):
        emotes = twitch.getSubscriberEmotes(channel_id)
    elif(source == 3):
        emotes = twitch.getGlobalFFZEmotes()
    elif(source == 4):
        emotes = twitch.getChannelFFZEmotes(channel_id)
    elif(source == 5):
        emotes = twitch.getBTTVGlobalEmoteInfo()
    elif(source == 6):
        emotes = twitch.getBTTVChannelEmoteInfo(channel_id)
    else:
        return -1

    if(emotes == None):
        return -1

    db = connect(channel_name)
    cursor = db.cursor()
    stmt = f'SELECT emote_id FROM emotes WHERE source = {source} AND active = 1;'
    cursor.execute(stmt)
    rows = cursor.fetchall()
    new_emotes = 0
    nonactive_emotes = []
    previous_emotes = []

    if(source != 5 and source != 6):
        for row in rows:
            previous_emotes.append(row[0])
        stmt = f'SELECT emote_id FROM emotes WHERE source = {source} AND active = 0;'
        cursor.execute(stmt)
        rows = cursor.fetchall()
        
        for row in rows:
            nonactive_emotes.append(row[0])

        A = set(emotes)
        B = set(previous_emotes)
        C = set(nonactive_emotes)
        now_inactive_emotes = B-A
        newly_added_emotes = A-B
        reactivated_emotes = A.intersection(C)

        for emote in now_inactive_emotes:
            stmt = f'UPDATE emotes SET active = 0 WHERE emote_id = "{emote}";'
            cursor.execute(stmt)
            db.commit()
            if(debug):
                utils.printDebug(f'{debug_messages[5]} {emote} {debug_messages[6]}')
        for emote in newly_added_emotes:
            if(source == 1):
                info = twitch.getGlobalEmoteInfo(emote)
            elif(source == 2):
                info = twitch.getSubscriberEmoteInfo(channel_id, emote)
            elif(source == 3 or source == 4):
                info = twitch.getFFZEmoteInfo(emote)
            if(len(info["url"]) == 3):
                url = info["url"][2]
            else:
                url = info["url"][0]
            if('\\' in info["code"]):
                info["code"] = info["code"].replace('\\', '\\\\')
            stmt = f'INSERT INTO emotes (code, emote_id, variant, url, date_added, source, active) VALUES ("{info["code"]}","{emote}",0,"{url}","{utils.getDate()}","{source}",1);'
            cursor.execute(stmt)
            db.commit()
            new_emotes += 1
        for emote in reactivated_emotes:
            stmt = f'UPDATE emotes SET active = 1 WHERE emote_id = "{emote}";'
            cursor.execute(stmt)
            db.commit()
            if(debug):
                utils.printDebug(f'{debug_messages[5]} {emote} {debug_messages[7]}')
    else:
        current_emotes = []
        for emote in emotes:
            current_emotes.append(emote['id'])
        for row in rows:
            previous_emotes.append(row[0])
        
        stmt = f'SELECT emote_id FROM emotes WHERE source = {source} AND active = 0;'
        cursor.execute(stmt)
        rows = cursor.fetchall()

        for row in rows:
            nonactive_emotes.append(row[0])

        A = set(current_emotes)
        B = set(previous_emotes)
        C = set(nonactive_emotes)
        now_inactive_emotes = B-A
        newly_added_emotes = A-B
        reactivated_emotes = A.intersection(C)
        
        for emote in now_inactive_emotes:
            stmt = f'UPDATE emotes SET active = 0 WHERE emote_id = "{emote}";'
            cursor.execute(stmt)
            db.commit()
            if(debug):
                utils.printDebug(f'{debug_messages[5]} {emote} {debug_messages[6]}')
        for emote in newly_added_emotes:
            info = twitch.getBTTVEmoteInfo(emote)
            stmt = f'INSERT INTO emotes (code, emote_id, variant, url, date_added, source, active) VALUES ("{info["code"]}","{emote}",0,"{info["url"]}","{utils.getDate()}","{source}",1);'
            cursor.execute(stmt)
            db.commit()
            new_emotes += 1
        for emote in reactivated_emotes:
            stmt = f'UPDATE emotes SET active = 1 WHERE emote_id = "{emote}";'
            cursor.execute(stmt)
            db.commit()
            if(debug):
                utils.printDebug(f'{debug_messages[5]} {emote} {debug_messages[7]}')

    if(new_emotes > 0):
        downloadAllEmotes(channel_name)

    cursor.close()
    db.close()
    return 0