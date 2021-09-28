import configparser
import os
import socket
import sys
import time

import constants
import db

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

def run(channel_name):
    if not os.path.exists('conf.ini'):
        db.createConfig()

    channel = '#' + channel_name
    sock = start_socket(channel)
    message_count = -1

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
                message_count = -1
            try:
                resp = sock.recv(2048).decode('utf-8', errors='ignore')
            except:
                file.write(f'{db.getDate()} Returned 2 - TIMEOUT/OVERFLOW ERROR.')
                return 2
            if(len(resp) > 0):
                username = resp.split('!')[0]
                username = username.split(':')
                username = username[len(username)-1]
                message = resp.split(':')[2:]
            if(len(message) > 0):
                message = message[0].split('\r\n')[0]
            if(prev_username == username and len(message) == 1):
                file.write(f'{db.getDate()} Returned 1 - SOCKET ERROR.')
                return 1
            if(message_count > 0):
                if(len(message) == 0):
                    continue
                message_count = message_count + 1
                if '\\' in message:
                    message = message.replace('\\', '')
                db.log(channel_name, username, message)
                prev_username = username
            else:
                message_count = message_count + 1
    except KeyboardInterrupt:
        stop()
    
def main():
    if(len(sys.argv) < 2):
        channel_name = input(f'Enter channel name: ')
    else:
        channel_name = sys.argv[1]
    success = run(channel_name)
    while(success == 1 or success == 2):
        success = run(channel_name)
    

main()