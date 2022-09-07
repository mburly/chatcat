import multiprocessing
import os
import sys

from chattercat.chattercat import Chattercat
from chattercat.constants import ERROR_MESSAGES
from chattercat.utils import getStreamNames, printBanner, printError

if __name__ == '__main__':
    os.system("")
    printBanner()
    streams = getStreamNames()
    if(len(streams) == 0):
        printError(None, ERROR_MESSAGES['no_streams'])
        sys.exit()
    pool = multiprocessing.Pool(processes=len(streams))
    try:
        out = pool.map(Chattercat,streams)
        pool.close()
    except KeyboardInterrupt:
        pool.close()