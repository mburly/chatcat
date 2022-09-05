import configparser
import os

import mysql.connector

import chattercat.constants as constants
import chattercat.twitch as twitch
import chattercat.utils as utils

CONFIG_SECTIONS = constants.CONFIG_SECTIONS
DB_VARIABLES = constants.DB_VARIABLES
DEBUG_MESSAGES = constants.DEBUG_MESSAGES
ERROR_MESSAGES = constants.ERROR_MESSAGES
STATUS_MESSAGES = constants.STATUS_MESSAGES
DIRS = constants.DIRS
EMOTE_TYPES = constants.EMOTE_TYPES

class Database:
    def __init__(self, channel_name):
        self.channel_name = channel_name
        self.db_name = f'cc_{channel_name}'
        self.db = self.connect()
        self.cursor = self.db.cursor()

    def connect(self):
        try:
            db = self.connectHelper(self.db_name)
            return db
        except:
            try:
                self.createDb()
                db = self.connectHelper(self.db_name)
                self.populateEmotesTable(db)
                self.downloadEmotes(db)
                return db
            except:
                return None

    def connectHelper(self, db_name=None):
        config = configparser.ConfigParser()
        config.read(constants.CONFIG_NAME)
        db = mysql.connector.connect(
            host=config[CONFIG_SECTIONS['db']][DB_VARIABLES['host']],
            user=config[CONFIG_SECTIONS['db']][DB_VARIABLES['user']],
            password=config[CONFIG_SECTIONS['db']][DB_VARIABLES['password']],
            database=db_name if(db_name is not None) else None
        )
        return db

    def createDb(self):
        try:
            db = self.connectHelper()
            cursor = db.cursor()
            cursor.execute(stmtCreateDatabase(self.channel_name))
            db = self.connect()
            cursor = db.cursor()
            cursor.execute(stmtCreateChattersTable())
            cursor.execute(stmtCreateSessionsTable())
            cursor.execute(stmtCreateGamesTable())
            cursor.execute(stmtCreateSegmentsTable())
            cursor.execute(stmtCreateMessagesTable())
            cursor.execute(stmtCreateEmotesTable())
            cursor.execute(stmtCreateLogsTable())
            cursor.execute(stmtCreateTopEmotesProcedure(self.channel_name))
            cursor.execute(stmtCreateTopChattersProcedure(self.channel_name))
            cursor.execute(stmtCreateRecentSessionsProcedure(self.channel_name))
            try:
                cursor.execute(stmtCreateEmoteStatusChangeTrigger())
            except:
                pass
            cursor.close()
            db.close()
        except:
            cursor.close()
            db.close()
            return None

    def startSession(self):
        self.stream = twitch.getStreamInfo(self.channel_name)
        if(twitch.getChannelId(self.channel_name) is None):
            utils.printError(None, ERROR_MESSAGES['channel'])
            return None
        self.segment = 0
        self.stream_title = self.stream['title']
        self.cursor.execute(stmtInsertNewSession())        
        self.db.commit()
        self.session_id = self.cursor.lastrowid
        self.addSegment(int(self.stream['game_id']))
        return self.session_id

    def endSession(self):
        self.cursor.execute(stmtUpdateSessionEndDatetime(self.session_id))
        self.cursor.execute(stmtUpdateSessionLength(self.session_id))
        self.cursor.execute(stmtUpdateSegmentEndDatetime(self.segment_id))
        self.cursor.execute(stmtUpdateSegmentLength(self.segment_id))
        self.db.commit()

    def log(self, resp):
        if(resp is None or resp.username is None or resp.message is None or resp.username == '' or ' ' in resp.username):
            return None
        self.logMessage(self.getChatterId(resp.username), resp.message)
        self.logMessageEmotes(resp.message)

    def logChatter(self, username):
        self.cursor.execute(stmtInsertNewChatter(username))
        self.db.commit()
        return self.cursor.lastrowid

    def logEmote(self, emote, channel_id):
        source_name = emote.split('-')[0]
        id = emote.split('-')[1]
        source = EMOTE_TYPES.index(source_name)+1
        emote = twitch.getEmoteById(channel_id, id, source)
        if(emote is None):
            return None
        if('\\' in emote.code):
            emote.code = emote.code.replace('\\', '\\\\')
        self.cursor.execute(stmtInsertNewEmote(emote.code, id, emote.url, source))
        self.db.commit()

    def logMessage(self, chatter_id, message):
        if "\"" in message:
            message = message.replace("\"", "\'")
        if '\\' in message:
            message = message.replace('\\', '\\\\')
        self.cursor.execute(stmtInsertNewMessage(message, self.session_id, self.segment_id, chatter_id))
        self.db.commit()
        self.cursor.execute(stmtUpdateChatterLastDate(chatter_id))
        self.db.commit()
        
    def logMessageEmotes(self, message):
        message_emotes = utils.parseMessageEmotes(self.channel_emotes, message)
        for emote in message_emotes:
            if '\\' in emote:
                emote = emote.replace('\\','\\\\')
            self.cursor.execute(stmtUpdateEmoteCount(emote))
            self.db.commit()

    def populateEmotesTable(self, db):
        cursor = db.cursor()
        emotes = twitch.getAllChannelEmotes(self.channel_name)
        source = 1
        for emote_type in EMOTE_TYPES:
            if(emotes[emote_type] is None):         # No emotes from source found
                source += 1
                continue
            for emote in emotes[emote_type]:
                if '\\' in emote.code:
                    emote.code = emote.code.replace('\\', '\\\\')
                if(source == 1):
                    cursor.execute(stmtInsertNewGlobalEmote(emote, source))
                else:
                    cursor.execute(stmtInsertNewThirdPartyEmote(emote, source))
                db.commit()
            source += 1
        cursor.close()

    def updateEmotes(self):
        utils.printInfo(self.channel_name, STATUS_MESSAGES['updates'])
        new_emote_count = 0
        channel_id = twitch.getChannelId(self.channel_name)
        channel_emotes = twitch.getAllChannelEmotes(self.channel_name)
        current_emotes = self.getEmotes(channel_emotes=channel_emotes)
        previous_emotes = self.getEmotes(active=1)
        inactive_emotes = self.getEmotes(active=0)
        A = set(current_emotes)
        B = set(previous_emotes)
        C = set(inactive_emotes)
        new_emotes = A-B
        removed_emotes = B-A
        reactivated_emotes = A.intersection(C)
        for emote in new_emotes:
            if(emote in reactivated_emotes):
                continue
            utils.printInfo(self.channel_name, f'Logging {emote}')
            self.logEmote(emote, channel_id)
            new_emote_count += 1
        self.setEmotesStatus(removed_emotes, 0)
        self.setEmotesStatus(reactivated_emotes, 1)
        if(new_emote_count > 0):
            self.downloadEmotes(self.db)
            utils.printInfo(self.channel_name, f'Downloaded {new_emote_count} newly active emotes.')
        utils.printInfo(self.channel_name, STATUS_MESSAGES['updates_complete'])

    def downloadEmotesHelper(self, db):
        utils.printInfo(self.channel_name, STATUS_MESSAGES['downloading'])
        cursor = db.cursor(buffered=True)
        cursor.execute(stmtSelectEmotesToDownload())
        for row in cursor.fetchall():
            url = row[0]
            emote_name = utils.removeSymbolsFromName(row[2])
            source = int(row[3])
            if(source == 1 or source == 2):
                if('animated' in url):
                    extension = 'gif'
                else:
                    extension = 'png'
                path = path = f'{DIRS["twitch"]}/{emote_name}-{row[1]}.{extension}'
            elif(source == 3 or source == 4):
                extension = 'png'
                path = f'{DIRS["ffz"]}/{emote_name}-{row[1]}.{extension}'
            elif(source == 5 or source == 6):
                extension = url.split('.')[3]
                url = url.split(f'.{extension}')[0]
                path = f'{DIRS["bttv"]}/{emote_name}-{row[1]}.{extension}'
            cursor.execute(stmtUpdateEmotePath(path, row[1], source))
            db.commit()
            utils.downloadFile(url, path)
        cursor.close()

    def downloadEmotes(self, db):
        for dir in DIRS.values():
            if not os.path.exists(dir):
                os.mkdir(dir)
        self.downloadEmotesHelper(db)

    def getChannelActiveEmotes(self):
        emotes = []
        self.updateEmotes()
        self.cursor.execute(stmtSelectActiveEmotes())
        for emote in self.cursor.fetchall():
            emotes.append(str(emote[0]))
        return emotes

    def getChatterId(self, username):
        id = None
        self.cursor.execute(stmtSelectChatterIdByUsername(username))
        for row in self.cursor:
            id = row[0]
            return id
        id = self.logChatter(username)
        return id

    # Returns in format: <source>-<emote_id>
    def getEmotes(self, active=None, channel_emotes=None):
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
            self.cursor.execute(stmtSelectEmoteByStatus(active))
            for row in self.cursor.fetchall():
                source = int(row[1])
                emotes.append(f'{EMOTE_TYPES[source-1]}-{row[0]}')
            return emotes

    def setEmotesStatus(self, emotes, active):
        for emote in emotes:
            id = emote.split('-')[1]
            self.cursor.execute(stmtUpdateEmoteStatus(active, id))
            self.db.commit()
            if(active):
                utils.printInfo(self.channel_name, f'{STATUS_MESSAGES["set_emote"]} {emote} {STATUS_MESSAGES["reactivated"]}')
            else:
                utils.printInfo(self.channel_name, f'{STATUS_MESSAGES["set_emote"]} {emote} {STATUS_MESSAGES["inactive"]}')
                
    def addSegment(self, new_game_id):
        if(self.segment != 0):
            self.cursor.execute(stmtUpdateSegmentEndDatetime(self.segment_id))
            self.cursor.execute(stmtUpdateSegmentLength(self.segment_id))
        self.stream_title = self.stream['title']
        self.game_id = new_game_id
        self.cursor.execute(stmtSelectGameById(self.game_id))
        if(len(self.cursor.fetchall()) == 0):
            self.cursor.execute(stmtInsertNewGame(self.game_id, self.stream['game_name']))
            self.db.commit()
        self.segment += 1
        self.cursor.execute(stmtInsertNewSegment(self.session_id, self.stream_title, self.segment, self.game_id))
        self.db.commit()
        self.segment_id = self.cursor.lastrowid
        
def stmtCreateDatabase(channel_name):
    return f'CREATE DATABASE IF NOT EXISTS cc_{channel_name} COLLATE utf8mb4_general_ci;'

def stmtCreateChattersTable():
    return f'CREATE TABLE chatters (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(512), first_date DATE, last_date DATE) COLLATE utf8mb4_general_ci;'

def stmtCreateSessionsTable():
    return f'CREATE TABLE sessions (id INT AUTO_INCREMENT PRIMARY KEY, start_datetime DATETIME, end_datetime DATETIME, length TIME) COLLATE utf8mb4_general_ci;'

def stmtCreateMessagesTable():
    return  f'CREATE TABLE messages (id INT AUTO_INCREMENT PRIMARY KEY, message VARCHAR(512) COLLATE utf8mb4_general_ci, session_id INT, segment_id INT, chatter_id INT, datetime DATETIME, FOREIGN KEY (session_id) REFERENCES sessions(id), FOREIGN KEY (segment_id) REFERENCES segments(id), FOREIGN KEY (chatter_id) REFERENCES chatters(id)) COLLATE utf8mb4_general_ci;'

def stmtCreateEmotesTable():
    return f'CREATE TABLE emotes (id INT AUTO_INCREMENT PRIMARY KEY, code VARCHAR(255) COLLATE utf8mb4_general_ci, emote_id VARCHAR(255) COLLATE utf8mb4_general_ci, count INT DEFAULT 0, url VARCHAR(512) COLLATE utf8mb4_general_ci, path VARCHAR(512) COLLATE utf8mb4_general_ci, date_added DATE, source VARCHAR(255) COLLATE utf8mb4_general_ci, active BOOLEAN) COLLATE utf8mb4_general_ci;'

def stmtCreateTopEmotesProcedure(channel_name):
    return f'CREATE PROCEDURE cc_{channel_name}.topEmotes() BEGIN SELECT code, count, path FROM cc_{channel_name}.EMOTES GROUP BY code ORDER BY count DESC LIMIT 10; END'

def stmtCreateTopChattersProcedure(channel_name):
    return f'CREATE PROCEDURE cc_{channel_name}.topChatters() BEGIN SELECT c.username, COUNT(m.id) FROM cc_{channel_name}.MESSAGES m INNER JOIN cc_{channel_name}.CHATTERS c ON m.chatter_id=c.id GROUP BY c.username ORDER BY COUNT(m.id) DESC LIMIT 10; END'

def stmtCreateRecentSessionsProcedure(channel_name):
    return f'CREATE PROCEDURE cc_{channel_name}.recentSessions() BEGIN SELECT id, (SELECT seg.stream_title FROM cc_{channel_name}.sessions ses INNER JOIN cc_{channel_name}.segments seg ON ses.id = seg.session_id ORDER BY seg.id DESC LIMIT 1), DATE_FORMAT(end_datetime, "%c/%e/%Y"), length FROM cc_{channel_name}.sessions ORDER BY id DESC LIMIT 5; END'

def stmtCreateLogsTable():
    return f'CREATE TABLE logs (id INT AUTO_INCREMENT PRIMARY KEY, emote_id INT, old INT, new INT, user_id VARCHAR(512), datetime DATETIME, FOREIGN KEY (emote_id) REFERENCES emotes(id)) COLLATE utf8mb4_general_ci;'

def stmtCreateGamesTable():
    return f'CREATE TABLE games (id INT PRIMARY KEY, name VARCHAR(255)) COLLATE utf8mb4_general_ci;'

def stmtCreateSegmentsTable():
    return f'CREATE TABLE segments (id INT AUTO_INCREMENT PRIMARY KEY, segment INT, stream_title VARCHAR(512), start_datetime DATETIME, end_datetime DATETIME, length TIME, session_id INT, game_id INT, FOREIGN KEY (session_id) REFERENCES sessions(id), FOREIGN KEY (game_id) REFERENCES games(id)) COLLATE utf8mb4_general_ci;'

def stmtCreateEmoteStatusChangeTrigger():
    return f'CREATE TRIGGER emote_status_change AFTER UPDATE ON emotes FOR EACH ROW IF OLD.active != NEW.active THEN INSERT INTO logs (emote_id, new, old, user_id, datetime) VALUES (OLD.id, NEW.active, OLD.active, NULL, UTC_TIMESTAMP()); END IF;//'

def stmtSelectEmotesToDownload():
    return f'SELECT url, emote_id, code, source FROM emotes WHERE path IS NULL;'

def stmtUpdateEmotePath(path, emote_id, source):
    return f'UPDATE emotes SET path = "{path}" WHERE emote_id LIKE "{emote_id}" AND source LIKE "{source}";'

def stmtSelectMostRecentSession():
    return f'SELECT MAX(id) FROM sessions'

def stmtUpdateSessionEndDatetime(session_id):
    return f'UPDATE sessions SET end_datetime = "{utils.getDateTime()}" WHERE id = {session_id}'

def stmtUpdateSessionLength(session_id):
    return f'UPDATE sessions SET length = (SELECT TIMEDIFF(end_datetime, start_datetime)) WHERE id = {session_id}'

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
    
def stmtInsertNewMessage(message, session_id, segment_id, chatter_id):
    return f'INSERT INTO messages (message, session_id, segment_id, chatter_id, datetime) VALUES ("{message}", {session_id}, {segment_id}, {chatter_id}, "{utils.getDateTime()}");'    

def stmtUpdateChatterLastDate(chatter_id):
    return f'UPDATE chatters SET last_date = "{utils.getDate()}" WHERE id = {chatter_id};'

def stmtUpdateEmoteCount(emote):
    return f'UPDATE emotes SET count = count + 1 WHERE code = BINARY "{emote}" AND active = 1;'

def stmtInsertNewGlobalEmote(emote, source):
    return f'INSERT INTO emotes (code, emote_id, url, path, date_added, source, active) VALUES ("{emote.code}","{emote.id}","{emote.url}","{DIRS["twitch"]}/{utils.removeSymbolsFromName(emote.code)}-{emote.id}.png","{utils.getDate()}","{source}",1);'

def stmtInsertNewThirdPartyEmote(emote, source):
    return f'INSERT INTO emotes (code, emote_id, url, date_added, source, active) VALUES ("{emote.code}","{emote.id}","{emote.url}","{utils.getDate()}","{source}",1);'

def stmtUpdateEmoteStatus(active, emote_id):
    return f'UPDATE emotes SET active = {active} WHERE emote_id = "{emote_id}";'

def stmtInsertNewSession():
    return f'INSERT INTO sessions (start_datetime, end_datetime, length) VALUES ("{utils.getDateTime()}", NULL, NULL);'

def stmtSelectGameById(game_id):
    return f'SELECT id FROM games WHERE id = {game_id};'

def stmtInsertNewGame(game_id, game_name):
    if('\"' in game_name):
        game_name = game_name.replace('"', '\\"')
    return f'INSERT INTO games (id, name) VALUES ({game_id}, "{game_name}");'

def stmtInsertNewSegment(session_id, stream_title, segment, game_id):
    return f'INSERT INTO segments (session_id, stream_title, segment, start_datetime, end_datetime, length, game_id) VALUES ({session_id}, "{stream_title}", {segment}, "{utils.getDateTime()}", NULL, NULL, {game_id});'

def stmtSelectSegmentNumberBySessionId(session_id):
    return f'SELECT MAX(segment) FROM segments WHERE session_id = {session_id};'

def stmtUpdateSegmentEndDatetime(segment_id):
    return f'UPDATE segments SET end_datetime = "{utils.getDateTime()}" WHERE id = {segment_id};'

def stmtUpdateSegmentLength(segment_id):
    return f'UPDATE segments SET length = (SELECT TIMEDIFF(end_datetime, start_datetime)) WHERE id = {segment_id}'