import certifi
import json
import ssl

from bs4 import BeautifulSoup
from requests_html import HTMLSession
from urllib.request import urlopen

import constants

def get_channel_id(channel_name):
    url = f'https://api.frankerfacez.com/v1/user/{channel_name}'
    page = urlopen(url, context=ssl.create_default_context(cafile=certifi.where()))
    html = page.read().decode('utf-8')
    a = json.loads(html)
    return a['user']['twitch_id']

def is_channel_live(channel_name):
    session = HTMLSession()
    url = f'https://twitch.tv/{channel_name}'
    page = session.get(url)
    page.html.render(sleep=1, keep_page=False)
    soup = BeautifulSoup(page.html.raw_html, features='lxml')
    if(len(soup.find_all(class_="live-time")) > 0):
        return True
    return False

# 1 = twitch, 2 = subscriber, 3 = ffz
def get_emote_set_info(emote_set, set_type, channel_id):
    info = []
    for emote in emote_set:
        if(set_type == 1):
            info.append(get_global_emote_info(emote))
        elif(set_type == 2):
            info.append(get_subscriber_emote_info(channel_id, emote))
        elif(set_type == 3):
            info.append(get_ffz_emote_info(emote))
        else:
            return -1
    return info

def get_all_channel_emote_info(channel_name):
    id = get_channel_id(channel_name)
    emotes = {}
    emotes['twitch'] = get_emote_set_info(get_global_emotes(),1,id)
    emotes['subscriber'] = get_emote_set_info(get_subscriber_emotes(id),2,id)
    emotes['ffz'] = get_emote_set_info(get_global_ffz_emotes(),3,id)
    emotes['ffz_channel'] = get_emote_set_info(get_channel_ffz_emotes(id),3,id)
    emotes['bttv'] = get_bttv_global_emote_info()
    emotes['bttv_channel'] = get_bttv_channel_emote_info(id)
    return emotes

def get_channel_ffz_emotes(channel_id):
    url = f'https://api.frankerfacez.com/v1/room/id/{channel_id}'
    page = urlopen(url, context=ssl.create_default_context(cafile=certifi.where()))
    html = page.read().decode('utf-8')
    a = json.loads(html)
    emote_set_id = str(a['room']['set'])
    emote_set = a['sets'][emote_set_id]['emoticons']
    channel_emotes = []
    for i in range(0, len(emote_set)):
        channel_emotes.append(str(emote_set[i]['id']))
    return channel_emotes

def get_global_ffz_emotes():
    url = 'https://api.frankerfacez.com/v1/set/global'
    page = urlopen(url, context=ssl.create_default_context(cafile=certifi.where()))
    html = page.read().decode('utf-8')
    a = json.loads(html)
    emote_set = str(a['default_sets'][0])
    emotes = a['sets'][emote_set]['emoticons']
    global_emotes = []
    for i in range(0, len(emotes)):
        global_emotes.append(str(emotes[i]['id']))
    return global_emotes

def get_channel_bttv_emotes(channel_id):
    url = f'https://api.betterttv.net/3/cached/users/twitch/{channel_id}'
    page = urlopen(url, context=ssl.create_default_context(cafile=certifi.where()))
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

def get_global_bttv_emotes():
    url = 'https://api.betterttv.net/3/cached/emotes/global'
    page = urlopen(url, context=ssl.create_default_context(cafile=certifi.where()))
    html = page.read().decode('utf-8')
    a = json.loads(html)
    global_emotes = []
    for i in range(0, len(a)):
        global_emotes.append(a[i]['id'])
    return global_emotes

def get_ffz_emote_info(emote_id):
    url = f'https://api.frankerfacez.com/v1/emote/{emote_id}'
    page = urlopen(url, context=ssl.create_default_context(cafile=certifi.where()))
    html = page.read().decode('utf-8')
    a = json.loads(html)
    info = {}
    info['id'] = emote_id
    info['code'] = a['emote']['name']
    urls = []
    emote_sizes = ['1','2','4']
    for i in range(0, len(a['emote']['urls'])):
        urls.append(f'https:{a["emote"]["urls"][emote_sizes[i]]}')
    info['url'] = urls
    return info

def get_bttv_global_emote_info():
    url = 'https://api.betterttv.net/3/cached/emotes/global'
    page = urlopen(url, context=ssl.create_default_context(cafile=certifi.where()))
    html = page.read().decode('utf-8')
    a = json.loads(html)
    emote_sizes = ['1x','2x','3x']
    info = []
    for i in range(0, len(a)):
        emote = {}
        urls = []
        emote['id'] = a[i]['id']
        emote['code'] = a[i]['code']
        for j in range(0, len(emote_sizes)):
            urls.append(f'https://cdn.betterttv.net/emote/{a[i]["id"]}/{emote_sizes[j]}')
        emote['url'] = urls
        info.append(emote)
    return info

def get_bttv_channel_emote_info(channel_id):
    url = f'https://api.betterttv.net/3/cached/users/twitch/{channel_id}'
    try:
        page = urlopen(url, context=ssl.create_default_context(cafile=certifi.where()))
    except:
        return
    html = page.read().decode('utf-8')
    a = json.loads(html)
    emotes = a['channelEmotes']
    emote_sizes = ['1x','2x','3x']
    info = []
    for i in range(0, len(emotes)):
        emote = {}
        urls = []
        emote['id'] = emotes[i]['id']
        emote['code'] = emotes[i]['code']
        for j in range(0, len(emote_sizes)):
            urls.append(f'https://cdn.betterttv.net/emote/{emotes[i]["id"]}/{emote_sizes[j]}')
        emote['url'] = urls
        info.append(emote)
    emotes = a['sharedEmotes']
    for i in range(0, len(emotes)):
        emote = {}
        urls = []
        emote['id'] = emotes[i]['id']
        emote['code'] = emotes[i]['code']
        for j in range(0, len(emote_sizes)):
            urls.append(f'https://cdn.betterttv.net/emote/{emotes[i]["id"]}/{emote_sizes[j]}')
        emote['url'] = urls
        info.append(emote)
    return info

def get_bttv_emote_info(emote_id):
    info = {}
    info['url'] = f'https://cdn.betterttv.net/emote/{emote_id}/3x'
    url = f'https://betterttv.com/emotes/{emote_id}'
    session = HTMLSession()
    page = session.get(url)
    page.html.render(sleep=1, keep_page=False)
    soup = BeautifulSoup(page.html.raw_html, features='lxml')
    title_tag = str(soup.findAll('h4'))
    info['id'] = emote_id
    info['code'] = title_tag.split('">')[1].split(' ')[0]
    return info

def get_global_emotes():
    url = 'https://twitchemotes.com/'
    page = urlopen(url, context=ssl.create_default_context(cafile=certifi.where()))
    html = page.read().decode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    emotes = soup.find_all(class_="emote-name")
    global_emotes = []
    for i in range(0, len(emotes)):
        emotes[i] = str(emotes[i])
        global_emotes.append(emotes[i].split('data-image-id="')[1].split('"')[0])
    return global_emotes

def get_global_emote_info(emote_id):
    url = f'https://twitchemotes.com/global/emotes/{emote_id}'
    page = urlopen(url, context=ssl.create_default_context(cafile=certifi.where()))
    html = page.read().decode('utf-8')
    emote_sizes = ['1.0','2.0','3.0']
    urls = []
    info = {}
    info['id'] = emote_id
    undecoded = ['&lt;3','&gt;(']
    info['code'] = html.split('<meta property="og:title" content="')[1].split('"')[0]
    for word in undecoded:
        if word in info['code']:
            if undecoded[0] in word:
                info['code'] = '<3'
            else:
                info['code'] = '>('
    for i in range(0, len(emote_sizes)):
        urls.append(f'https://static-cdn.jtvnw.net/emoticons/v2/{emote_id}/static/light/{emote_sizes[i]}')
    info['url'] = urls
    return info

def get_subscriber_emotes(channel_id):
    url = f'https://twitchemotes.com/channels/{channel_id}'
    page = urlopen(url, context=ssl.create_default_context(cafile=certifi.where()))
    html = page.read().decode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    emotes = soup.find_all(class_="emote")
    subscriber_emotes = []
    for i in range(0, len(emotes)):
        emotes[i] = str(emotes[i])
        subscriber_emotes.append(emotes[i].split('data-image-id="')[1].split('"')[0])
    return subscriber_emotes

def get_subscriber_emote_info(channel_id, emote_id):
    url = f'https://twitchemotes.com/channels/{channel_id}/emotes/{emote_id}'
    page = urlopen(url, context=ssl.create_default_context(cafile=certifi.where()))
    html = page.read().decode('utf-8')
    emote_sizes = ['1.0','2.0','3.0']
    urls = []
    info = {}
    info['id'] = emote_id
    info['code'] = html.split('<meta property="og:title" content="')[1].split('"')[0]
    if(len(html.split('animated')) == 1):
        emote_type = 'static'
    else:
        emote_type = 'animated'
    for i in range(0, len(emote_sizes)):
        urls.append(f'https://static-cdn.jtvnw.net/emoticons/v2/{emote_id}/{emote_type}/light/{emote_sizes[i]}')
    info['url'] = urls
    return info

def get_channel_title(channel_name):
    url = f'https://twitch.tv/{channel_name}'
    page = urlopen(url, context=ssl.create_default_context(cafile=certifi.where()))
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