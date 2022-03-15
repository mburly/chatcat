import os

import db
import utils

def main():
    if(utils.setup() == -1):
        return -1

    channel_name = utils.getChannelName()
    if(channel_name is None):
        return 0

    session_id = db.startSession(channel_name)
    while(session_id is None):
        channel_name = utils.getChannelName(True)
        if(channel_name is None):
            return 0
        session_id = db.startSession(channel_name)
        
    success = utils.run(channel_name, session_id, 1)
    while(success):
        success = utils.run(channel_name, session_id, 2)
    db.endSession(channel_name)


if __name__ == "__main__":
    os.system("")
    main()