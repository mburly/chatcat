import configparser
import os
import socket
import sys
import time

import constants
import db
import twitch

def stop():
    minutes = str((time.time() - init_start) / 60)
    file.write(minutes)
    sock.close()

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

    stream_title = twitch.get_channel_title(channel_name)

    if(flag == 1):
        stmt = f'INSERT INTO sessions (stream_title, start_datetime) VALUES ("{stream_title}", "{datetime}")'
        cursor.execute(stmt)
        database.commit()
        return cursor.lastrowid
    else:
        stmt = f'UPDATE sessions SET end_datetime = "{datetime}" WHERE id = {id}'

def run(channel_name, session_id):
    channel = '#' + channel_name
    sock = start_socket(channel)

    if(os.path.exists('logs/') is False):
        os.mkdir('logs/')

    filename = 'logs/' + channel_name + '.log'
    file = open(filename, 'w')

    init_start = time.time()
    start = time.time()
    username = ''
    message = ''

    try:
        prev_username = ''
        while True:
            if(((time.time() - start) / 60) >= 5):
                sock.close()
                sock = start_socket(channel)
                start = time.time()
            try:
                resp = sock.recv(2048).decode('utf-8', errors='ignore')
            except:
                file.write(f'{db.getDateTime()} Returned 2 - TIMEOUT/OVERFLOW ERROR.')
                return 2
            if(len(resp) > 0):
                username = resp.split('!')[0]
                username = username.split(':')
                username = username[len(username)-1]
                message = resp.split(':')[2:]
            if(len(message) > 0):
                message = message[0].split('\r\n')[0]
            if(prev_username == username and len(message) == 1):
                file.write(f'{db.getDateTime()} Returned 1 - SOCKET ERROR.')
                return 1
            if '\\' in message:
                message = message.replace('\\', '')
            db.log(channel_name, username, message, session_id)
            prev_username = username
    except KeyboardInterrupt:
        stop()
    
def main():
    if not os.path.exists('conf.ini'):
        db.createConfig()
    if(len(sys.argv) < 2):
        channel_name = input(f'Enter channel name: ')
    else:
        channel_name = sys.argv[1]
    session_id = handle_session(1, channel_name)
    success = run(channel_name, session_id)
    while(success == 1 or success == 2):
        success = run(channel_name, session_id)
    

main()