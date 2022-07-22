import configparser

import requests

import constants
import interface

API_URLS = constants.API_URLS
CDN_URLS = constants.CDN_URLS
EMOTE_TYPES = constants.EMOTE_TYPES
STATUS_MESSAGES = constants.STATUS_MESSAGES

def getAllChannelEmotes(channel_name):
    channel_id = getChannelId(channel_name)
    channel_emotes = {}
    interface.printInfo(channel_name, STATUS_MESSAGES['twitch'])
    channel_emotes[EMOTE_TYPES[0]] = getTwitchEmotes()
    interface.printInfo(channel_name, STATUS_MESSAGES['subscriber'])
    channel_emotes[EMOTE_TYPES[1]] = getTwitchEmotes(channel_name)
    interface.printInfo(channel_name, STATUS_MESSAGES['ffz_global'])
    channel_emotes[EMOTE_TYPES[2]] = getFFZEmotes()
    interface.printInfo(channel_name, STATUS_MESSAGES['ffz_channel'])
    channel_emotes[EMOTE_TYPES[3]] = getFFZEmotes(channel_id)
    interface.printInfo(channel_name, STATUS_MESSAGES['bttv_global'])
    channel_emotes[EMOTE_TYPES[4]] = getBTTVEmotes()
    interface.printInfo(channel_name, STATUS_MESSAGES['bttv_channel'])
    channel_emotes[EMOTE_TYPES[5]] = getBTTVEmotes(channel_id)
    return channel_emotes

def getBTTVEmotes(channel_id=None):
    emote_set = []
    if(channel_id is None):
        url = f'{API_URLS["bttv"]}/emotes/global'
        emotes = requests.get(url,params=None,headers=None).json()
        for i in range(0, len(emotes)):
            info = getBTTVEmoteInfo(emotes[i])
            emote_set.append(info)
    else:
        url = f'{API_URLS["bttv"]}/users/twitch/{channel_id}'
        emotes = requests.get(url,params=None,headers=None).json()
        try:
            channel_emotes = emotes['channelEmotes']
        except:
            return None
        if(len(channel_emotes) != 0):
            for i in range(0, len(channel_emotes)):
                info = getBTTVEmoteInfo(channel_emotes[i])
                emote_set.append(info)
        try:
            shared_emotes = emotes['sharedEmotes']
        except:
            if(emote_set == []):
                return None
            return emote_set
        if(len(shared_emotes) != 0):
            for i in range(0, len(shared_emotes)):
                info = getBTTVEmoteInfo(shared_emotes[i])
                emote_set.append(info)
    return emote_set

def getChannelId(channel_name):
    url = f'{API_URLS["twitch"]}/users?login={channel_name}'
    try:
        return int(requests.get(url,params=None,headers=getHeaders()).json()['data'][0]['id'])
    except:
        return None

def getBTTVEmoteInfo(emote):
    info = {}
    info['id'] = emote['id']
    info['code'] = emote['code']
    info['url'] = f'{CDN_URLS["bttv"]}/{emote["id"]}/3x.{emote["imageType"]}'
    return info

def getEmoteInfoById(source, channel_id, emote_id):
    info = {}
    if(source == 1 or source == 2):
        if(source == 1):
            url = f'{API_URLS["twitch"]}/chat/emotes/global'
        else:
            url = f'{API_URLS["twitch"]}/chat/emotes?broadcaster_id={channel_id}'
        try:
            emotes = requests.get(url,params=None,headers=getHeaders()).json()['data']
            for emote in emotes:
                if(emote_id == emote['id']):
                    info['code'] = emote['name']
                    info['url'] = emote['images']['url_4x']
        except:
            return None
    elif(source == 3 or source == 4):
        url = f'{API_URLS["ffz"]}/emote/{emote_id}'
        emote = requests.get(url,params=None,headers=None).json()
        info['code'] = emote['emote']['name']
        if(len(emote['emote']['urls']) == 1):
            info['url'] = f'{CDN_URLS["ffz"]}/{emote_id}/1'
        else:
            info['url'] = f'{CDN_URLS["ffz"]}/{emote_id}/4'
    else:
        found = 0
        url = f'{API_URLS["bttv"]}/users/twitch/{channel_id}'
        emote = requests.get(url,params=None,headers=None).json()
        emotes = emote['sharedEmotes']
        for emote in emotes:
            if(emote['id'] == emote_id):
                info['code'] = emote['code']
                info['url'] = f'{CDN_URLS["bttv"]}/{emote_id}/3x.{emote["imageType"]}'
                found = 1
                break
        try:
            emote = requests.get(url,params=None,headers=None).json()
            emotes = emote['channelEmotes']
        except:
            if(found == 0):
                return None
            info['id'] = emote_id
            return info
        for emote in emotes:
            if(found):
                break
            if(emote['id'] == emote_id):
                info['code'] = emote['code']
                info['url'] = f'{CDN_URLS["bttv"]}/{emote_id}/3x.{emote["imageType"]}'
                break
        if(found == 0):
            url = f'{API_URLS["bttv"]}/emotes/global'
            emotes = requests.get(url,params=None,headers=None).json()
            for emote in emotes:
                if(emote['id'] == emote_id):
                    info['code'] = emote['code']
                    info['url'] = f'{CDN_URLS["bttv"]}/{emote_id}/3x.{emote["imageType"]}'
                    break
    info['id'] = emote_id
    return info

def getFFZEmotes(channel_id=None):
    emote_set = []
    if(channel_id is None):
        url = f'{API_URLS["ffz"]}/set/global'
        emotes = requests.get(url,params=None,headers=None).json()
        emotes = emotes['sets']['3']['emoticons']
    else:
        url = f'{API_URLS["ffz"]}/room/id/{channel_id}'
        emotes = requests.get(url,params=None,headers=None).json()
        try:
            emote_set_id = str(emotes['room']['set'])
        except:
            return None
        emotes = emotes['sets'][emote_set_id]['emoticons']
    if(emotes == []):
        return None
    for i in range(0, len(emotes)):
        info = {}
        info['id'] = emotes[i]['id']
        info['code'] = emotes[i]['name']
        if(len(emotes[i]['urls']) == 1):
            info['url'] = f'{CDN_URLS["ffz"]}/{emotes[i]["id"]}/1'
        else:
            info['url'] = f'{CDN_URLS["ffz"]}/{emotes[i]["id"]}/4'
        emote_set.append(info)
    return emote_set

def getHeaders():
    config = configparser.ConfigParser()
    config.read(constants.CONFIG_NAME)
    return {"Authorization": f"Bearer {getOAuth(constants.CLIENT_ID, config[constants.CONFIG_SECTIONS[1]][constants.TWITCH_VARIABLES[2]])}",
            "Client-Id": constants.CLIENT_ID}

def getOAuth(client_id, client_secret):
    try:
        response = requests.post(
            constants.OAUTH_URL + f'/token?client_id={client_id}&client_secret={client_secret}&grant_type=client_credentials'
        )
        return response.json()['access_token']
    except:
        return None

def getOnlineStreams(channel_names):
    online_streams = []
    for stream in getStreams(channel_names):
        online_streams.append(stream['user_login'])
    return online_streams

def getStreams(channel_names):
    url = f'{API_URLS["twitch"]}/streams?'
    for name in channel_names:
        url += f'user_login={name}&'
    return requests.get(url.strip('&'),params=None,headers=getHeaders()).json()['data']

def getStreamTitle(channel_name):
    url = f'{API_URLS["twitch"]}/streams?user_login={channel_name}'
    try:
        return requests.get(url,params=None,headers=getHeaders()).json()['data'][0]['title'].replace('\"','\'')
    except:
        return None

def getTwitchEmotes(channel_name=None):
    emote_set = []
    if(channel_name is None):
        url = f'{API_URLS["twitch"]}/chat/emotes/global'
    else:
        url = f'{API_URLS["twitch"]}/chat/emotes?broadcaster_id={getChannelId(channel_name)}'
    try:
        emotes = requests.get(url,params=None,headers=getHeaders()).json()['data']
        if(emotes == []):
            return None
        for i in range(0, len(emotes)):
            info = {}
            info['id'] = emotes[i]['id']
            info['code'] = emotes[i]['name']
            if '3.0' in emotes[i]['scale']:
                if 'animated' in emotes[i]['format']:
                    url = f'{CDN_URLS["twitch"]}/{emotes[i]["id"]}/animated/light/3.0'
                else:
                    url = f'{CDN_URLS["twitch"]}/{emotes[i]["id"]}/static/light/3.0'
            else:
                url = f'{CDN_URLS["twitch"]}/{emotes[i]["id"]}/static/light/1.0'
            info['url'] = url
            emote_set.append(info)
        return emote_set
    except:
        return None

def isStreamLive(channel_name):
    url = f'{API_URLS["twitch"]}/streams?user_login={channel_name}'
    try:
        return requests.get(url,params=None,headers=getHeaders()).json()['data'] != []
    except:
        return False

def validateToken():
    config = configparser.ConfigParser()
    config.read(constants.CONFIG_NAME)
    headers = {"Authorization": f"OAuth {getOAuth(constants.CLIENT_ID, config[constants.CONFIG_SECTIONS[1]][constants.TWITCH_VARIABLES[2]])}"}
    try:
        return requests.get(f'{constants.OAUTH_URL}/validate',params=None,headers=headers).json()['client_id'] != None
    except requests.ConnectionError:
        interface.printError(constants.ERROR_MESSAGES['connection'])
        return False
    except:
        interface.printError(constants.ERROR_MESSAGES['client_id'])
        return False