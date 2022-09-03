import multiprocessing
import os
import sys

from chattercat.chattercat import Chattercat
from chattercat.constants import ERROR_MESSAGES, DIRS
from chattercat.utils import getStreamNames, createAndDownloadGlobalEmotes, printBanner, printError

if __name__ == '__main__':
    os.system("")
    streams = getStreamNames()
    if(len(streams) == 0):
        printError(None, ERROR_MESSAGES['no_streams'])
        sys.exit()
    pool = multiprocessing.Pool(processes=len(streams))
    printBanner()
    if not os.path.exists(DIRS['emotes']):
        createAndDownloadGlobalEmotes()
    try:
        out = pool.map(Chattercat,streams)
        pool.close()
    except KeyboardInterrupt:
        pool.close()