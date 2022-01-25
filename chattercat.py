import os
import socket
import sys
import time

import constants
import db
import twitch
import utils

debug = constants.debug

def start_socket(channel):
    config = constants.config
    nickname = config['twitch']['nickname']
    token = config['twitch']['token']
    sock = socket.socket()
    try:
        sock.connect(constants.address)
    except:
        utils.print_error("Unable to connect to host. Likely lost internet connection.")
        return -1
    sock.send(f'PASS {token}\n'.encode('utf-8'))
    sock.send(f'NICK {nickname}\n'.encode('utf-8'))
    sock.send(f'JOIN {channel}\n'.encode('utf-8'))
    return sock

# (flag) 1 = start, 2 = end
def handle_session(flag, channel_name):
    database = db.connect(channel_name)
    cursor = database.cursor()
    datetime = utils.getDateTime()
    if(flag == 1):
        counter = 0
        stream_title = twitch.get_channel_title(channel_name)
        if(len(stream_title) > 140 or '<meta' in stream_title):
            utils.print_error("Error fetching stream title. Still trying...")
            while(len(stream_title) > 140 or '<meta' in stream_title):
                if(counter >= 20):
                    stream_title = 'Unable to get stream title.'
                    break
                stream_title = twitch.get_channel_title(channel_name)
                counter += 1
        utils.print_log(channel_name, "Stream Title", stream_title)
        stmt = f'INSERT INTO sessions (stream_title, start_datetime) VALUES ("{stream_title}", "{datetime}")'
        cursor.execute(stmt)
        database.commit()
        return cursor.lastrowid
    else:
        stmt = f'SELECT MAX(id) FROM sessions'
        cursor.execute(stmt)
        rows = cursor.fetchall()
        id = rows[0][0]
        stmt = f'UPDATE sessions SET end_datetime = "{datetime}" WHERE id = {id}'
        cursor.execute(stmt)
        database.commit()
        return id

def parseEmotes(emotes, message):
    if(type(message) == list):
        utils.print_error("[parseEmotes()] Something is wrong.")
        return []
    words = message.split(' ')
    parsed_emotes = []
    for word in words:
        if word in emotes and word not in parsed_emotes:
            parsed_emotes.append(word)
    return parsed_emotes

# flags 1 = first run, 2 = otherwise
def run(channel_name, session_id, flag):
    channel = '#' + channel_name
    sock = start_socket(channel)
    if(os.path.exists('logs/') is False):
        os.mkdir('logs/')

    filename = 'logs/' + channel_name + '.log'
    if not os.path.exists(filename):
        file = open(filename, 'w')
    else:
        file = open(filename, 'a')

    live_start = time.time()
    socket_start = time.time()
    username = ''
    message = ''
    emotes = db.getEmotes(channel_name, flag)

    try:
        counter = 0
        while True:
            if(((time.time() - live_start) / 60) >= (1-(counter*.15))):
                if(debug):
                    utils.print_debug(f'Checking if offline with counter = {counter}')
                if(twitch.is_channel_live(channel_name)):
                    counter = 0
                    if(debug):
                        utils.print_debug(f'Detected online. Counter now = {counter}')
                    live_start = time.time()
                else:
                    counter += 1
                    if(debug):
                        utils.print_debug(f'Detected offline. Counter now = {counter}')
                    if(counter == 5):
                        utils.print_debug("Stream ended. Now ending session...")
                        sock.close()
                        return -1
                    live_start = time.time()
            if(((time.time() - socket_start) / 60) >= 5):
                sock.close()
                sock = start_socket(channel)
                socket_start = time.time()
            try:
                resp = sock.recv(2048).decode('utf-8', errors='ignore')
                if resp == '' :
                    file.write(f'{utils.getDateTime()} - TIMEOUT/OVERFLOW ERROR.\n')
                    sock.close()
                    return 1
            except:
                file.write(f'{utils.getDateTime()} - TIMEOUT/OVERFLOW ERROR.\n')
                sock.close()
                return 2
            if(len(resp) > 0):
                username = resp.split('!')[0]
                username = username.split(':')
                username = username[len(username)-1]
                message = resp.split(' ')
                occurrences = utils.getOccurrences(message, "tmi.twitch.tv")
                if(occurrences == 1):
                    message = utils.parseMessage(message[3:])
                else:
                    username_indices = utils.getIndices(message, 'tmi.twitch.tv')
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
        return -1
    
def main():
    if not os.path.exists(constants.config_name):
        utils.createConfig()
    if(len(sys.argv) < 2):
        channel_name = input('Enter channel name: ')
    else:
        channel_name = sys.argv[1]
    session_id = handle_session(1, channel_name)
    success = run(channel_name, session_id, 1)
    while(success == 1):
        success = run(channel_name, session_id, 2)
    handle_session(2, channel_name)

if __name__ == "__main__":
    main()