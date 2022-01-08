# TODO
# Update emotes function
# On keyboardinterrupt, fill in rest of session info and cleanly exit (make sure everything is closed socket, etc)
# Download animated emotes properly (Twitch animated emotes, currently using only 'static' in the url)
# Correct the 'tmi' logs, detecting bugs (0 length message etc)

import configparser
import keyboard
import os
import socket
import sys
import time

import constants
import db
import twitch

def start_socket(channel):
    config = configparser.ConfigParser()
    config.read('conf.ini')
    nickname = config['twitch']['nickname']
    token = config['twitch']['token']
    sock = socket.socket()
    sock.connect(constants.address)
    sock.send(f'PASS {token}\n'.encode('utf-8'))
    sock.send(f'NICK {nickname}\n'.encode('utf-8'))
    sock.send(f'JOIN {channel}\n'.encode('utf-8'))
    return sock

# (flag) 1 = start, 2 = end
def handle_session(flag, channel_name):
    database = db.connect(channel_name)
    cursor = database.cursor()
    
    datetime = db.getDateTime()

    if(flag == 1):
        counter = 0
        stream_title = twitch.get_channel_title(channel_name)
        if(len(stream_title) > 140):
            print("Error fetching stream title. Still trying...")
            while(len(stream_title) > 140):
                if(counter >= 20):
                    stream_title = 'Unable to get stream title.'
                    break
                stream_title = twitch.get_channel_title(channel_name)
                counter += 1
        print(stream_title)
        stmt = f'INSERT INTO sessions (stream_title, start_datetime) VALUES ("{stream_title}", "{datetime}")'
        cursor.execute(stmt)
        database.commit()
        for i in range(1, len(constants.emote_types)+1):
            db.update_emotes(channel_name, i)
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

def parseMessage(emotes, message):
        words = message.split(' ')
        parsed_emotes = []
        for word in words:
            if word in emotes and word not in parsed_emotes:
                parsed_emotes.append(word)
        return parsed_emotes

def run(channel_name, session_id):
    channel = '#' + channel_name
    sock = start_socket(channel)
    if(os.path.exists('logs/') is False):
        os.mkdir('logs/')

    filename = 'logs/' + channel_name + '.log'
    if not os.path.exists(filename):
        file = open(filename, 'w')
    else:
        file = open(filename, 'a')

    start = time.time()
    username = ''
    message = ''

    emotes = db.getEmotes(channel_name)

    try:
        prev_username = ''
        while True:
            if(keyboard.is_pressed("ctrl+space")):
                print("Ending session...")
                return -1
            if(((time.time() - start) / 60) >= 5):
                sock.close()
                sock = start_socket(channel)
                start = time.time()
            try:
                resp = sock.recv(2048).decode('utf-8', errors='ignore')
            except:
                file.write(f'{db.getDateTime()} Returned 2 - TIMEOUT/OVERFLOW ERROR.\n')
                return 2
            if(len(resp) > 0):
                username = resp.split('!')[0]
                username = username.split(':')
                username = username[len(username)-1]
                message = resp.split(':')[2:]
            if(len(message) > 0):
                message = message[0].split('\r\n')[0]
            if(prev_username == username and len(message) == 1):
                file.write(f'{db.getDateTime()} Returned 1 - SOCKET ERROR.\n')
                return 1
            if(message == []):
                continue
            if '\\' in message:
                message = message.replace('\\', '')
            message_emotes = parseMessage(emotes, message)
            db.log(channel_name, username, message, message_emotes, session_id)
            prev_username = username
    except KeyboardInterrupt:
        sock.close()
    
def main():
    if not os.path.exists(constants.config_name):
        db.createConfig()
    if(len(sys.argv) < 2):
        channel_name = input('Enter channel name: ')
    else:
        channel_name = sys.argv[1]
    session_id = handle_session(1, channel_name)
    success = run(channel_name, session_id)
    while(success == 1 or success == 2):
        success = run(channel_name, session_id)
    handle_session(2, channel_name)

main()