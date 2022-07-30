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
        self.channel_name = channel_name
        live = twitch.isStreamLive(self.channel_name)
        try:
            while(self.executing):
                if(live):
                    utils.printInfo(self.channel_name, f'{self.channel_name} just went live!')
                    self.running = True
                    self.session_id = db.startSession(self.channel_name)
                    if(self.session_id is None):
                        return -1
                    while(self.running):
                        self.run()
                    db.endSession(self.channel_name)
                    live = False
                    utils.printInfo(self.channel_name, f'{self.channel_name} is now offline.')
                else:
                    live = twitch.isStreamLive(self.channel_name)
                    time.sleep(15)
        except KeyboardInterrupt:
            return None

    def run(self):
        channel = f'#{self.channel_name}'
        sock = utils.startSocket(channel)
        live_clock = time.time()
        socket_clock = time.time()
        channel_emotes = db.getChannelActiveEmotes(self.channel_name)
        try:
            while self.running:
                if(utils.elapsedTime(live_clock) >= 1):
                    if(twitch.isStreamLive(self.channel_name)):
                        live_clock = time.time()
                    else:
                        sock.close()
                        self.running = False
                if(utils.elapsedTime(socket_clock) >= 5):
                    sock.close()
                    sock = utils.startSocket(channel)
                    socket_clock = time.time()
                try:
                    resp = sock.recv(2048).decode('utf-8', errors='ignore')
                    if resp == '' :
                        sock.close()
                        sock = utils.startSocket(channel)
                        socket_clock = time.time()
                except KeyboardInterrupt:
                    try:
                        sock.close()
                        db.endSession(self.channel_name)
                        self.executing = False
                        self.running = False
                    except:
                        db.endSession(self.channel_name)
                        self.executing = False
                        self.running = False
                except:
                    sock.close()
                    sock = utils.startSocket(channel)
                    socket_clock = time.time()
                utils.parseResponse(resp, self.channel_name, channel_emotes, self.session_id)
        except:
            sock.close()

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