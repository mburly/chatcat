import multiprocessing
import os
import time

import constants
import db
import twitch
import utils

class Chattercat:
    executing = True
    running = True
    def __init__(self, channel_name):
        self.channel_name = channel_name.lower()
        self.live = twitch.isStreamLive(self.channel_name)
        try:
            while(self.executing):
                if(self.live):
                    utils.printInfo(self.channel_name, f'{self.channel_name} just went live!')
                    self.running = True
                    self.session_id = db.startSession(self.channel_name)
                    if(self.session_id is None):
                        return -1
                    while(self.running):
                        self.run()
                    db.endSession(self.channel_name)
                    self.live = False
                    utils.printInfo(self.channel_name, f'{self.channel_name} is now offline.')
                else:
                    self.live = twitch.isStreamLive(self.channel_name)
                    time.sleep(15)
        except KeyboardInterrupt:
            return None

    def run(self):
        self.sock = utils.startSocket(self.channel_name)
        self.live_clock = time.time()
        self.socket_clock = time.time()
        self.channel_emotes = db.getChannelActiveEmotes(self.channel_name)
        try:
            while self.running:
                if(utils.elapsedTime(self.live_clock) >= 1):
                    if(twitch.isStreamLive(self.channel_name)):
                        self.live_clock = time.time()
                    else:
                        self.sock.close()
                        self.running = False
                if(utils.elapsedTime(self.socket_clock) >= 5):
                    self.sock = utils.restartSocket(self)
                try:
                    resp = self.sock.recv(2048).decode('utf-8', errors='ignore')
                    if resp == '' :
                        self.sock = utils.restartSocket(self)
                except KeyboardInterrupt:
                    try:
                        self.sock.close()
                        utils.endExecution(self)
                    except:
                        utils.endExecution(self)
                except:
                    self.sock = utils.restartSocket(self)
                utils.parseResponse(resp, self)
        except:
            utils.printInfo(self.channel_name, 'Entered exception in main.')
            self.sock.close()

if __name__ == '__main__':
    os.system("")
    streams = utils.getStreamNames()
    pool = multiprocessing.Pool(processes=len(streams))
    if(utils.getDownloadMode() and not os.path.exists(constants.DIRS['global_emotes'])):
        utils.createAndDownloadGlobalEmotes()
    try:
        utils.printBanner()
        out = pool.map(Chattercat,streams)
        pool.close()
    except KeyboardInterrupt:
        pool.close()