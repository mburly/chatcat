import configparser
import os
import time

import mysql.connector

import constants

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
    
        stmt = f'CREATE TABLE chatters (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255), first_date VARCHAR(255), last_date VARCHAR(255))'

        cursor.execute(stmt)

        stmt = f'CREATE TABLE messages (id INT AUTO_INCREMENT PRIMARY KEY, message VARCHAR(512) COLLATE utf8mb4_bin, sessionID INT, chatterID INT, datetime VARCHAR(255))'

        cursor.execute(stmt)

        stmt = f'CREATE TABLE sessions (id INT AUTO_INCREMENT PRIMARY KEY, stream_title VARCHAR(512) COLLATE utf8mb4_bin, start_datetime VARCHAR(255), end_datetime VARCHAR(255))'

        cursor.execute(stmt)

        stmt = f'CREATE TABLE emotes (id INT AUTO_INCREMENT PRIMARY KEY, emote_name VARCHAR(255) COLLATE utf8mb4_bin, emote_code VARCHAR(255) COLLATE utf8mb4_bin, variant INT, count INT DEFAULT 0, path VARCHAR(512) COLLATE utf8mb4_bin, date_added VARCHAR(255) COLLATE utf8mb4_bin, active BOOLEAN)'

        cursor.execute(stmt)

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

def log(channel_name, username, message, session_id):
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

    stmt = f'INSERT INTO messages (message, sessionID, chatterID, datetime) VALUES ("{message}", {session_id}, {id}, "{datetime}")'
    cursor.execute(stmt)
    db.commit()

    stmt = f'UPDATE chatters SET last_date = "{date}" WHERE id = {id}'
    cursor.execute(stmt)
    db.commit()
    print(f'[{channel_name}] [{datetime}] Logged message from {username}: {message}')

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
        if(createDB(channel_name) == 0):
            db = mysql.connector.connect(
            host=config['db']['host'],
            user=config['db']['user'],
            password=config['db']['password'],
            database=db_name
            )
            return db
        else:
            print("Something went wrong.")
            return -1