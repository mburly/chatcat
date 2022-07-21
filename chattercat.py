import os

import constants
import db
import interface
import twitch
import utils

def main():
    if(utils.setup() is None):
        return 0
    if(twitch.validateToken() == False):
        return 0
    channel_name = utils.getChannelNameInput()
    if(channel_name is None):
        return 0
    if(twitch.isStreamLive(channel_name) == False):
        interface.printError(constants.ERROR_MESSAGES['offline'])
        return 0
    session_id = db.startSession(channel_name)
    while(session_id is None):
        interface.printBanner()
        channel_name = utils.getChannelNameInput(initial_run=False)
        if(channel_name is None):
            return 0
        session_id = db.startSession(channel_name)
    running = utils.run(channel_name, session_id, 1)
    while(running):
        running = utils.run(channel_name, session_id, 2)
    db.endSession(channel_name)


if __name__ == "__main__":
    os.system("")
    main()