import configparser
import os
import time

import mysql.connector

import constants
import twitch

def createConfig():
    config = configparser.ConfigParser()
    host = input("Enter hostname [default: localhost]: ")
    user = input("Enter DB username: ")
    password = input("Enter DB password: ")
    nickname = input("Enter your twitch username: ")
    token = input("Please visit the URL https://twitchapps.com/tmi/ and enter the token after pressing Connect: ")

    if host == '':
        host = 'localhost'
    
    config['db'] = {
        'host':host,
        'user':user,
        'password':password
    }

    config['twitch'] = {
        'nickname':nickname,
        'token':token
    }

    with open(constants.config_name, 'w') as configfile:
        config.write(configfile)

def getDate():
    cur = time.localtime()
    return f'{str(cur.tm_mon)}-{str(cur.tm_mday)}-{str(cur.tm_year)}'

def getDateTime():
    cur = time.localtime()
    return f'{str(cur.tm_mon)}-{str(cur.tm_mday)}-{str(cur.tm_year)} {str(cur.tm_hour)}:{str(cur.tm_min)}:{str(cur.tm_sec)}'

def createDB(channel_name):
    config = constants.config
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
        
        stmt = f'CREATE DATABASE IF NOT EXISTS {db_name}'
    
        cursor.execute(stmt)
        db = connect(channel_name)
        cursor = db.cursor()
    
        stmt = f'CREATE TABLE chatters (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(512), first_date VARCHAR(255), last_date VARCHAR(255))'

        cursor.execute(stmt)

        stmt = f'CREATE TABLE messages (id INT AUTO_INCREMENT PRIMARY KEY, message VARCHAR(512) COLLATE utf8mb4_bin, session_id INT, chatter_id INT, datetime VARCHAR(255))'

        cursor.execute(stmt)

        stmt = f'CREATE TABLE sessions (id INT AUTO_INCREMENT PRIMARY KEY, stream_title VARCHAR(512) COLLATE utf8mb4_bin, start_datetime VARCHAR(255), end_datetime VARCHAR(255))'

        cursor.execute(stmt)

        stmt = f'CREATE TABLE emotes (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255) COLLATE utf8mb4_bin, code VARCHAR(255) COLLATE utf8mb4_bin, emote_id VARCHAR(255) COLLATE utf8mb4_bin, variant INT, count INT DEFAULT 0, path VARCHAR(512) COLLATE utf8mb4_bin, date_added VARCHAR(255) COLLATE utf8mb4_bin, source VARCHAR(255) COLLATE utf8mb4_bin, active BOOLEAN)'

        cursor.execute(stmt)

        populateEmotes(channel_name)

        return 0
    except:
        return -1

def getUserID(cursor, username):
    id = -1
    stmt = f'SELECT id FROM chatters WHERE username = "{username}";'
    cursor.execute(stmt)
    for row in cursor:
        id = row[0]
        return id
    return id

def getEmotes(channel_name):
    emotes = []
    db = connect(channel_name)
    cursor = db.cursor()
    stmt = 'SELECT code FROM emotes;'
    cursor.execute(stmt)
    rows = cursor.fetchall()
    for emote in rows:
        emotes.append(str(emote[0]))
    return emotes

# for first time inserting into emotes table only
def populateEmotes(channel_name):
    print("Populating emotes table...")
    emotes = twitch.get_all_channel_emote_info(channel_name)
    emote_types = list(emotes.keys())
    db = connect(channel_name)
    cursor = db.cursor()
    source = 1
    for emote_type in emote_types:
        for emote in emotes[emote_type]:
            emote_name = emote['code']
            if(len(emote['path']) > 2):
                url = emote['path'][2]
            else:
                url = emote['path'][0]
            if '\\' in emote_name:
                emote_name = emote_name.replace('\\', '\\\\')
            emote_id = emote['id']
            stmt = f'INSERT INTO emotes (name, code, emote_id, variant, path, date_added, source, active) VALUES ("{emote_name}","{emote_name}","{emote_id}",0,"{url}","{getDate()}","{source}",1)'
            cursor.execute(stmt)
            db.commit()
        source += 1
    return 0

def log(channel_name, username, message, emotes, session_id):
    if username in constants.blacklisted_names:
        return
    db = connect(channel_name)
    cursor = db.cursor()
    id = getUserID(cursor, username)

    date = getDate()
    datetime = getDateTime()

    if(id == -1):
        stmt = f'INSERT INTO chatters (username, first_date, last_date) VALUES ("{username}", "{date}", "{date}")'
        cursor.execute(stmt)
        db.commit()
        id = getUserID(cursor, username)
        
    message = message.replace("\"", "\'")

    stmt = f'INSERT INTO messages (message, session_id, chatter_id, datetime) VALUES ("{message}", {session_id}, {id}, "{datetime}")'
    cursor.execute(stmt)
    db.commit()

    stmt = f'UPDATE chatters SET last_date = "{date}" WHERE id = {id}'
    cursor.execute(stmt)
    db.commit()

    for emote in emotes:
        stmt = f'UPDATE emotes SET count = count + 1 WHERE code = "{emote}" AND active = 1;'
        cursor.execute(stmt)
        db.commit()

    print(f'[\033[1;32m{channel_name}\033[0m] [\033[1;34m{datetime}\033[0m] Logged message from {username}: {message}')

def connect(channel_name):
    config = constants.config
    try:
        db_name = f'cc_{channel_name}'
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