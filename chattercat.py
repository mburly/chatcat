import configparser
import os
import socket
import sys
import time

import constants
import db
import twitch
import utils

debug_messages = constants.debug_messages
error_messages = constants.error_messages
input_messages = constants.input_messages

# (flag) 1 = start, 2 = end
def handleSession(flag, channel_name):
    if(twitch.getChannelId(channel_name) == None):
        return -1
    database = db.connect(channel_name)
    if(database == -1):
        return -1
    cursor = database.cursor()
    datetime = utils.getDateTime()
    if(flag == 1):
        stream_title = twitch.getStreamTitle(channel_name)
        stmt = f'INSERT INTO sessions (stream_title, start_datetime) VALUES ("{stream_title}", "{datetime}")'
        cursor.execute(stmt)
        database.commit()
        id = cursor.lastrowid
        cursor.close()
        database.close()
        return id
    else:
        stmt = f'SELECT MAX(id) FROM sessions'
        cursor.execute(stmt)
        rows = cursor.fetchall()
        id = rows[0][0]
        stmt = f'UPDATE sessions SET end_datetime = "{datetime}" WHERE id = {id}'
        cursor.execute(stmt)
        database.commit()
        cursor.close()
        database.close()
        return id

def parseEmotes(emotes, message):
    if(type(message) == list):
        return []
    words = message.split(' ')
    parsed_emotes = []
    for word in words:
        if word in emotes and word not in parsed_emotes:
            parsed_emotes.append(word)
    return parsed_emotes

# (flag) 1 = first run, 2 = otherwise
def run(channel_name, session_id, flag):
    channel = '#' + channel_name
    sock = startSocket(channel)
    live_start = time.time()
    socket_start = time.time()
    username = ''
    message = ''
    emotes = db.getEmotes(channel_name, flag)
    if(flag == 1):
        utils.printBanner()
    try:
        while True:
            if(utils.elapsedTime(live_start) >= 1):
                if(twitch.isStreamLive(channel_name)):
                    live_start = time.time()
                else:
                    sock.close()
                    return -1
            if(utils.elapsedTime(socket_start) >= 5):
                sock.close()
                sock = startSocket(channel)
                socket_start = time.time()
            try:
                resp = sock.recv(2048).decode('utf-8', errors='ignore')
                if resp == '' :
                    sock.close()
                    return 1
            except KeyboardInterrupt:
                try:
                    sock.close()
                    return -3
                except:
                    return -3
            except:
                sock.close()
                return 1
            if(len(resp) > 0):
                username = resp.split('!')[0]
                username = username.split(':')
                username = username[len(username)-1]
                message = resp.split(' ')
                occurrences = utils.getOccurrences(message, constants.server_url)
                if(occurrences == 1):
                    message = utils.parseMessage(message[3:])
                else:
                    username_indices = utils.getIndices(message, constants.server_url)
                    occurrences = len(username_indices)
                    for i in range(0, occurrences):
                        if(i == occurrences-1):
                            username = utils.parseUsername(message[username_indices[i]])
                            if username == None:
                                continue
                            current_message = message[3+username_indices[i]:]
                        else:
                            username = utils.parseUsername(message[username_indices[i]])
                            if username == None:
                                continue
                            current_message = message[3+username_indices[i]:username_indices[i+1]+1]
                        current_message = utils.parseMessage(current_message)
                        message_emotes = parseEmotes(emotes, current_message)
                        db.log(channel_name, username, current_message, message_emotes, session_id)
                    continue
            if(message == []):
                continue
            if '\r\n' in message:
                message = message.replace('\r\n', '')
            message_emotes = parseEmotes(emotes, message)
            db.log(channel_name, username, message, message_emotes, session_id)
    except:
        sock.close()
        return 1

def startSocket(channel):
    config = configparser.ConfigParser()
    config.read(constants.config_name)
    nickname = config[constants.config_sections[1]][constants.twitch_variables[0]]
    token = config[constants.config_sections[1]][constants.twitch_variables[1]]
    sock = socket.socket()
    try:
        sock.connect(constants.address)
    except:
        utils.printError(error_messages[1])
        return -1
    sock.send(f'PASS {token}\n'.encode('utf-8'))
    sock.send(f'NICK {nickname}\n'.encode('utf-8'))
    sock.send(f'JOIN {channel}\n'.encode('utf-8'))
    return sock

def main():
    if not os.path.exists(constants.config_name):
        utils.printLogo()
        if(utils.createConfig() == -1):
            return -1
        utils.printBanner()
    else:
        utils.printBanner()
    if(len(sys.argv) < 2):
        channel_name = utils.printMenu()
        while(channel_name == 1 or channel_name == -1):
            if(channel_name == -1):
                utils.printError(error_messages[3])
            utils.printBanner()
            channel_name = utils.printMenu()
        if(channel_name == 0):
            return 0
    else:
        channel_name = sys.argv[1]
    utils.printBanner()
    channel_name = channel_name.lower()
    session_id = handleSession(1, channel_name)
    while(session_id == -1):
        utils.printError(error_messages[2])
        utils.printBanner()
        channel_name = utils.printMenu()
        if(channel_name == 0):
            return 0
        while(channel_name == 1 or channel_name == -1):
            if(channel_name == -1):
                utils.printError(error_messages[3])
            channel_name = utils.printMenu()
        if(channel_name == 0):
            return 0
        utils.printBanner()
        channel_name = channel_name.lower()
        session_id = handleSession(1, channel_name)
    success = run(channel_name, session_id, 1)
    while(success == 1):
        success = run(channel_name, session_id, 2)
    handleSession(2, channel_name)


if __name__ == "__main__":
    main()