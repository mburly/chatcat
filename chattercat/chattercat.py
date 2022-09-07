import configparser
import socket
import time

import chattercat.constants as constants
from chattercat.db import Database
import chattercat.twitch as twitch
from chattercat.utils import Response, elapsedTime, printError, printInfo, statusMessage

CONFIG_SECTIONS = constants.CONFIG_SECTIONS
ERROR_MESSAGES = constants.ERROR_MESSAGES
TWITCH_VARIABLES = constants.TWITCH_VARIABLES

class Chattercat:
    executing = True
    running = True
    def __init__(self, channel_name):
        self.channel_name = channel_name.lower()
        self.live = twitch.isStreamLive(self.channel_name)
        try:
            while(self.executing):
                if(self.live):
                    if(self.start() is None):
                        return None
                    while(self.running):
                        self.run()
                    self.end()
                else:
                    self.live = twitch.isStreamLive(self.channel_name)
                    time.sleep(15)
        except KeyboardInterrupt:
            return None

    def run(self):
        self.startSocket()
        self.live_clock = time.time()
        self.socket_clock = time.time()
        self.db.getChannelActiveEmotes()
        try:
            while self.running:
                self.resp = ''
                if(elapsedTime(self.live_clock) >= 1):
                    self.db.stream = twitch.getStreamInfo(self.channel_name)
                    if(self.db.stream is not None):
                        game_id = int(self.db.stream['game_id'])
                        if(self.db.game_id != game_id):
                            self.db.addSegment(game_id)
                        self.live_clock = time.time()
                    else:
                        if(self.sock is not None):
                            self.sock.close()
                        self.running = False
                if(elapsedTime(self.socket_clock) >= 5):
                    self.restartSocket()
                try:
                    self.resp = self.sock.recv(2048).decode('utf-8', errors='ignore')
                    if self.resp == '' :
                        self.restartSocket()
                except KeyboardInterrupt:
                    self.endExecution()
                except:
                    self.restartSocket()
                self.parseResponse()
        except:
            self.endExecution()

    def start(self):
        printInfo(self.channel_name, statusMessage(self.channel_name))
        try:
            self.db = Database(self.channel_name)
            self.db.startSession()
            self.running = True
            return None if self.db.session_id is None else self.db.session_id
        except:
            return None

    def end(self):
        printInfo(self.channel_name, statusMessage(self.channel_name, online=False))
        self.db.endSession()
        self.db.cursor.close()
        self.db.db.close()
        self.live = False

    def endExecution(self):
        if(self.sock is not None):
                self.sock.close()
        self.db.endSession()
        self.running = False
        self.executing = False

    def startSocket(self):
        config = configparser.ConfigParser()
        config.read(constants.CONFIG_NAME)
        nickname = config[CONFIG_SECTIONS['twitch']][TWITCH_VARIABLES['nickname']]
        token = config[CONFIG_SECTIONS['twitch']][TWITCH_VARIABLES['token']]
        self.sock = socket.socket()
        try:
            self.sock.connect(constants.ADDRESS)
        except:
            printError(self.channel_name, ERROR_MESSAGES['host'])
            self.db.endSession()
            return None
        self.sock.send(f'PASS {token}\n'.encode('utf-8'))
        self.sock.send(f'NICK {nickname}\n'.encode('utf-8'))
        self.sock.send(f'JOIN #{self.channel_name}\n'.encode('utf-8'))

    def restartSocket(self):
        self.sock.close()
        self.socket_clock = time.time()
        self.startSocket()

    def getResponses(self):
        try:
            return self.resp.split('\r\n')[:-1]
        except:
            return None

    def parseResponse(self):
        for resp in self.getResponses():
            self.db.log(Response(self.channel_name, resp))