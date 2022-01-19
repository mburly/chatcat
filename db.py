import os

import mysql.connector

import constants
import twitch
import utils

def downloadAllEmotes(channel_name):
    db = connect(channel_name)
    cursor = db.cursor(buffered=True)
    bad_file_chars = ['\\','/',':','*','?','"','<','>','|']
    if not os.path.exists('emotes'):
        os.mkdir('emotes')
    os.chdir('emotes')
    if not os.path.exists(channel_name):
        os.mkdir(channel_name)
    os.chdir(channel_name)
    stmt = 'SELECT url, emote_id, code FROM emotes WHERE source NOT LIKE "1" AND path IS NULL;'
    cursor.execute(stmt)
    rows = cursor.fetchall()
    counter = 0
    for row in rows:
        emote_name = row[2]
        for character in bad_file_chars:
            if character in emote_name:
                emote_name = emote_name.replace(character, str(counter))
                counter += 1
        file_name = f'{emote_name}-{row[1]}.gif'
        stmt = f'UPDATE emotes SET path = "{file_name}" WHERE emote_id LIKE "{row[1]}" AND source NOT LIKE "1";'
        try:
            cursor.execute(stmt)
            db.commit()
        except mysql.connector.Error as err:
            print(err)
        utils.downloadFile(row[0], file_name)
    os.chdir('../../')

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

        print("Populating emotes table...")
        populateEmotes(channel_name)
        downloadAllEmotes(channel_name)

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
    
    for i in range(1, len(constants.emote_types)+1):
        update_emotes(channel_name, i)

    cursor = db.cursor()
    stmt = 'SELECT code FROM emotes WHERE ACTIVE = 1;'
    cursor.execute(stmt)
    rows = cursor.fetchall()
    for emote in rows:
        emotes.append(str(emote[0]))
    return emotes

# for first time inserting into emotes table only
def populateEmotes(channel_name):
    emotes = twitch.get_all_channel_emote_info(channel_name)
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
    return 0

def update_emotes(channel_name, source):
    if(constants.debug):
        utils.print_debug('Entering (update_emotes) function')
    channel_id = twitch.get_channel_id(channel_name)

    if(source == 1):
        emotes = twitch.get_global_emotes()
    elif(source == 2):
        emotes = twitch.get_subscriber_emotes(channel_id)
    elif(source == 3):
        emotes = twitch.get_global_ffz_emotes()
    elif(source == 4):
        emotes = twitch.get_channel_ffz_emotes(channel_id)
    elif(source == 5):
        emotes = twitch.get_bttv_global_emote_info()
    elif(source == 6):
        emotes = twitch.get_bttv_channel_emote_info(channel_id)
    else:
        return -1

    if(emotes == None):
        return -1

    db = connect(channel_name)
    cursor = db.cursor()
    stmt = f'SELECT emote_id FROM emotes WHERE source = {source} AND active = 1;'
    cursor.execute(stmt)
    rows = cursor.fetchall()
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
        for emote in newly_added_emotes:
            if(source == 1):
                info = twitch.get_global_emote_info(emote)
            elif(source == 2):
                info = twitch.get_subscriber_emote_info(channel_id, emote)
            elif(source == 3 or source == 4):
                info = twitch.get_ffz_emote_info(emote)
            if(len(info["url"]) == 3):
                url = info["url"][2]
            else:
                url = info["url"][0]
            stmt = f'INSERT INTO emotes (code, emote_id, variant, url, date_added, source, active) VALUES ("{info["code"]}","{emote}",0,"{url}","{utils.getDate()}","{source}",1);'
            cursor.execute(stmt)
            db.commit()
        for emote in reactivated_emotes:
            stmt = f'UPDATE emotes SET active = 1 WHERE emote_id = "{emote}";'
            cursor.execute(stmt)
            db.commit()
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
        for emote in newly_added_emotes:
            info = twitch.get_bttv_emote_info(emote)
            print(info)
            print(len(info))
            stmt = f'INSERT INTO emotes (code, emote_id, variant, url, date_added, source, active) VALUES ("{info["code"]}","{emote}",0,"{info["url"]}","{utils.getDate()}","{source}",1);'
            cursor.execute(stmt)
            db.commit()
        for emote in reactivated_emotes:
            stmt = f'UPDATE emotes SET active = 1 WHERE emote_id = "{emote}";'
            cursor.execute(stmt)
            db.commit()

    downloadAllEmotes(channel_name)
    return 0  

def log(channel_name, username, message, emotes, session_id):
    if username in constants.blacklisted_names:
        return
    if constants.blacklisted_messages[0] in message:
        return
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
        
    message = message.replace("\"", "\'")

    stmt = f'INSERT INTO messages (message, session_id, chatter_id, datetime) VALUES ("{message}", {session_id}, {id}, "{datetime}");'
    cursor.execute(stmt)
    db.commit()

    stmt = f'UPDATE chatters SET last_date = "{date}" WHERE id = {id};'
    cursor.execute(stmt)
    db.commit()

    for emote in emotes:
        stmt = f'UPDATE emotes SET count = count + 1 WHERE code = "{emote}" AND active = 1;'
        cursor.execute(stmt)
        db.commit()

    utils.print_log(channel_name, username, message)

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