import configparser
import socket
import time

from chattercat.db import Database
import chattercat.constants as constants
import chattercat.twitch as twitch
from chattercat.utils import printError, elapsedTime, parseIncompleteResponse, printInfo

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
        except Exception as e:
            printError(self.channel_name, e)

    def run(self):
        self.sock = self.startSocket()
        self.live_clock = time.time()
        self.socket_clock = time.time()
        self.channel_emotes = self.db.getChannelActiveEmotes()
        try:
            while self.running:
                self.resp = ''
                if(elapsedTime(self.live_clock) >= 1):
                    if(twitch.isStreamLive(self.channel_name)):
                        self.live_clock = time.time()
                    else:
                        self.sock.close()
                        self.running = False
                if(elapsedTime(self.socket_clock) >= 5):
                    self.sock = self.restartSocket()
                try:
                    self.resp = self.sock.recv(2048).decode('utf-8', errors='ignore')
                    if self.resp == '' :
                        self.sock = self.restartSocket()
                except KeyboardInterrupt:
                    try:
                        self.sock.close()
                        self.endExecution()
                    except:
                        self.endExecution()
                except:
                    self.sock = self.restartSocket()
                self.parseResponse()
        except Exception as e:
            printError(self.channel_name, e)
            if(self.sock is not None):
                self.sock.close()
            self.endExecution()

    def start(self):
        printInfo(self.channel_name, f'{self.channel_name} just went live!')
        try:
            self.db = Database(self.channel_name)
            self.session_id = self.db.startSession()
            self.running = True
            return None if self.session_id is None else self.session_id
        except:
            return None

    def end(self):
        printInfo(self.channel_name, f'{self.channel_name} is now offline.')
        self.db.endSession()
        self.db.cursor.close()
        self.db.db.close()
        self.live = False

    def endExecution(self):
        self.db.endSession()
        self.running = False
        self.executing = False

    def startSocket(self):
        config = configparser.ConfigParser()
        config.read(constants.CONFIG_NAME)
        nickname = config[CONFIG_SECTIONS['twitch']][TWITCH_VARIABLES['nickname']]
        token = config[CONFIG_SECTIONS['twitch']][TWITCH_VARIABLES['token']]
        sock = socket.socket()
        try:
            sock.connect(constants.ADDRESS)
        except:
            printError(self.channel_name, ERROR_MESSAGES['host'])
            self.db.endSession()
            return None
        sock.send(f'PASS {token}\n'.encode('utf-8'))
        sock.send(f'NICK {nickname}\n'.encode('utf-8'))
        sock.send(f'JOIN #{self.channel_name}\n'.encode('utf-8'))
        return sock

    def restartSocket(self):
        self.sock.close()
        self.socket_clock = time.time()
        return self.startSocket()

    def getResponses(self):
        try:
            return self.resp.split('\r\n')[:-1]
        except:
            return None

    def parseResponse(self):
        for response in self.getResponses():
            username = self.parseUsername(response)
            message = self.parseMessage(response)
            if(message is None):
                continue
            if(username == message):
                username = parseIncompleteResponse(response)
            self.db.log(username, message, self.channel_emotes, self.session_id)

    def parseUsername(self, resp):
        try:
            return resp.split('!')[0].split(':')[1]
        except:
            return None

    def parseMessage(self, resp):
        try:
            return resp.split(f'#{self.channel_name} :')[1]
        except:
            return None