import multiprocessing
import os

from constants import DIRS
from utils import Chattercat, getStreamNames, createAndDownloadGlobalEmotes, printBanner

if __name__ == '__main__':
    os.system("")
    streams = getStreamNames()
    pool = multiprocessing.Pool(processes=len(streams))
    printBanner()
    if not os.path.exists(DIRS['global_emotes']):
        createAndDownloadGlobalEmotes()
    try:
        out = pool.map(Chattercat,streams)
        pool.close()
    except KeyboardInterrupt:
        pool.close()