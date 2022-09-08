import socket
import time

import chattercat.constants as constants
from chattercat.db import Database
import chattercat.twitch as twitch
from chattercat.utils import Response, elapsedTime, printError, printInfo, statusMessage

class Chattercat:
    executing = True
    running = True
    def __init__(self, channel_name):
        self.channel_name = channel_name.lower()
        self.live = twitch.isStreamLive(self.channel_name)
        try:
            while(self.executing):
                if(self.live):
                    self.start()
                    while(self.running):
                        self.run()
                    self.end()
                else:
                    self.live = twitch.isStreamLive(self.channel_name)
                    if not self.live:
                        time.sleep(constants.TIMER_SLEEP)
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
                if(elapsedTime(self.live_clock) >= constants.TIMER_LIVE):
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
                if(elapsedTime(self.socket_clock) >= constants.TIMER_SOCKET):
                    self.restartSocket()
                try:
                    self.resp = self.sock.recv(2048).decode('utf-8', errors='ignore')
                    if self.resp == '' :
                        self.restartSocket()
                except KeyboardInterrupt:
                    self.endExecution()
                except:
                    self.restartSocket()
                for resp in self.getResponses():
                    self.db.log(Response(self.channel_name, resp))
        except:
            self.endExecution()

    def start(self):
        printInfo(self.channel_name, statusMessage(self.channel_name))
        try:
            self.db = Database(self.channel_name)
            if(self.db.startSession() is None):
                return None
            self.running = True
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
        try:
            self.sock = socket.socket()
            self.sock.connect(constants.ADDRESS)
            self.sock.send(f'PASS {self.db.config.token}\n'.encode('utf-8'))
            self.sock.send(f'NICK {self.db.config.nickname}\n'.encode('utf-8'))
            self.sock.send(f'JOIN #{self.channel_name}\n'.encode('utf-8'))
        except:
            printError(self.channel_name, constants.ERROR_MESSAGES['host'])
            self.db.endSession()
            return None

    def restartSocket(self):
        if(self.sock is not None):
            self.sock.close()
        self.socket_clock = time.time()
        self.startSocket()

    def getResponses(self):
        try:
            return self.resp.split('\r\n')[:-1]
        except:
            return None