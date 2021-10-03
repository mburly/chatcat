import json

from urllib.request import urlopen

import constants

def get_channel_id(channel_name):
    url = f'https://api.frankerfacez.com/v1/user/{channel_name}'
    page = urlopen(url)
    html = page.read().decode('utf-8')
    a = json.loads(html)
    return a['user']['twitch_id']

def get_channel_ffz_emotes(channel_id):
    url = f'https://api.frankerfacez.com/v1/room/id/{channel_id}'
    page = urlopen(url)
    html = page.read().decode('utf-8')
    a = json.loads(html)
    emote_set_id = str(a['room']['set'])
    emote_set = a['sets'][emote_set_id]['emoticons']
    channel_emotes = []
    for i in range(0, len(emote_set)):
        channel_emotes.append(emote_set[i]['id'])
    return channel_emotes

def get_channel_bttv_emotes(channel_id):
    url = f'https://api.betterttv.net/3/cached/users/twitch/{channel_id}'
    page = urlopen(url)
    html = page.read().decode('utf-8')
    a = json.loads(html)
    channel_emotes = []
    channel_emote_set = a['channelEmotes']
    shared_emote_set = a['sharedEmotes']
    for i in range(0, len(channel_emote_set)):
        channel_emotes.append(channel_emote_set[i]['id'])
    for i in range(0, len(shared_emote_set)):
        channel_emotes.append(shared_emote_set[i]['id'])
    return channel_emotes

def get_ffz_emote_info(emote_id):
    url = f'https://api.frankerfacez.com/v1/emote/{emote_id}'
    page = urlopen(url)
    html = page.read().decode('utf-8')
    a = json.loads(html)
    info = {}
    info['code'] = a['emote']['name']
    urls = []
    emote_sizes = ['1','2','4']
    for i in range(0, len(a['emote']['urls'])):
        urls.append(f'https://{a["emote"]["urls"][emote_sizes[i]]}')
    info['path'] = urls
    return info

def get_bttv_emote_codes(channel_id):
    url = f'https://api.betterttv.net/3/cached/users/twitch/{channel_id}'
    page = urlopen(url)
    html = page.read().decode('utf-8')
    a = json.loads(html)
    channel_emotes = []
    channel_emote_set = a['channelEmotes']
    shared_emote_set = a['sharedEmotes']
    for i in range(0, len(channel_emote_set)):
        channel_emotes.append(channel_emote_set[i]['code'])
    for i in range(0, len(shared_emote_set)):
        channel_emotes.append(shared_emote_set[i]['code'])
    return channel_emotes

def get_bttv_emote_info(emote_id, emote_name):
    info = {}
    info['code'] = emote_name
    emote_sizes = ['1x','2x','3x']
    urls = []
    for i in range(0, len(emote_sizes)):
        urls.append(f'https://cdn.betterttv.net/emote/{emote_id}/{emote_sizes[i]}')
    info['path'] = urls
    return info

def get_channel_title(channel_name):
    url = f'https://twitch.tv/{channel_name}'
    page = urlopen(url)
    html = page.read().decode('utf-8')
    tag = "<meta name=\"twitter:description\" content=\""
    title = html.find(tag)
    index = title + len(tag)
    stream_title = ""
    buffer = ""
    while(buffer != "/>"):
        buffer = html[index]
        if(buffer == "\""):
            if(html[index+1] == '/'):
                return stream_title
        stream_title += buffer
        index += 1
    return stream_title