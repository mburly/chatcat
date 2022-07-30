import configparser

import requests

import constants
import interface

API_URLS = constants.API_URLS
CDN_URLS = constants.CDN_URLS
EMOTE_TYPES = constants.EMOTE_TYPES
STATUS_MESSAGES = constants.STATUS_MESSAGES

class Emote:
    def __init__(self, id, code, url):
        self.id = id
        self.code = code
        self.url = url

def getAllChannelEmotes(channel_name):
    channel_id = getChannelId(channel_name)
    channel_emotes = {}
    channel_emotes[EMOTE_TYPES[0]] = getTwitchEmotes()
    channel_emotes[EMOTE_TYPES[1]] = getTwitchEmotes(channel_name)
    channel_emotes[EMOTE_TYPES[2]] = getFFZEmotes()
    channel_emotes[EMOTE_TYPES[3]] = getFFZEmotes(channel_id)
    channel_emotes[EMOTE_TYPES[4]] = getBTTVEmotes()
    channel_emotes[EMOTE_TYPES[5]] = getBTTVEmotes(channel_id)
    return channel_emotes

def getBTTVEmotes(channel_id=None):
    emote_set = []
    if(channel_id is None):
        url = f'{API_URLS["bttv"]}/emotes/global'
        emotes = requests.get(url,params=None,headers=None).json()
        for i in range(0, len(emotes)):
            emote_set.append(Emote(emotes[i]['id'], emotes[i]['code'], f'{CDN_URLS["bttv"]}/{emotes[i]["id"]}/3x.{emotes[i]["imageType"]}'))
    else:
        url = f'{API_URLS["bttv"]}/users/twitch/{channel_id}'
        emotes = requests.get(url,params=None,headers=None).json()
        try:
            channel_emotes = emotes['channelEmotes']
        except:
            return None
        if(len(channel_emotes) != 0):
            for i in range(0, len(channel_emotes)):
                emote_set.append(Emote(channel_emotes[i]['id'], channel_emotes[i]['code'], f'{CDN_URLS["bttv"]}/{channel_emotes[i]["id"]}/3x.{channel_emotes[i]["imageType"]}'))
        try:
            shared_emotes = emotes['sharedEmotes']
        except:
            if(emote_set == []):
                return None
            return emote_set
        if(len(shared_emotes) != 0):
            for i in range(0, len(shared_emotes)):
                emote_set.append(Emote(shared_emotes[i]['id'], shared_emotes[i]['code'], f'{CDN_URLS["bttv"]}/{shared_emotes[i]["id"]}/3x.{shared_emotes[i]["imageType"]}'))
    return emote_set

def getChannelId(channel_name):
    url = f'{API_URLS["twitch"]}/users?login={channel_name}'
    try:
        return int(requests.get(url,params=None,headers=getHeaders()).json()['data'][0]['id'])
    except:
        return None

def getEmoteInfoById(source, channel_id, emote_id) -> Emote:
    if(source == 1 or source == 2):
        if(source == 1):
            url = f'{API_URLS["twitch"]}/chat/emotes/global'
        else:
            url = f'{API_URLS["twitch"]}/chat/emotes?broadcaster_id={channel_id}'
        try:
            emotes = requests.get(url,params=None,headers=getHeaders()).json()['data']
            for emote in emotes:
                if(emote_id == emote['id']):
                    e = Emote(emote_id, emote['name'], emote['images']['url_4x'])
        except:
            return None
    elif(source == 3 or source == 4):
        url = f'{API_URLS["ffz"]}/emote/{emote_id}'
        emote = requests.get(url,params=None,headers=None).json()
        if(len(emote['emote']['urls']) == 1):
            e = Emote(emote_id, emote['emote']['name'], f'{CDN_URLS["ffz"]}/{emote_id}/1')
        else:
            e = Emote(emote_id, emote['emote']['name'], f'{CDN_URLS["ffz"]}/{emote_id}/4')
    else:
        found = False
        url = f'{API_URLS["bttv"]}/users/twitch/{channel_id}'
        emote = requests.get(url,params=None,headers=None).json()
        emotes = emote['sharedEmotes']
        for emote in emotes:
            if(emote['id'] == emote_id):
                e = Emote(emote_id, emote['code'], f'{CDN_URLS["bttv"]}/{emote_id}/3x.{emote["imageType"]}')
                found = True
                break
        try:
            emote = requests.get(url,params=None,headers=None).json()
            emotes = emote['channelEmotes']
        except:
            if(found == False):
                return None
            return e
        for emote in emotes:
            if(found):
                break
            if(emote['id'] == emote_id):
                e = Emote(emote_id, emote['code'], f'{CDN_URLS["bttv"]}/{emote_id}/3x.{emote["imageType"]}')
                break
        if(found == 0):
            url = f'{API_URLS["bttv"]}/emotes/global'
            emotes = requests.get(url,params=None,headers=None).json()
            for emote in emotes:
                if(emote['id'] == emote_id):
                    e = Emote(emote_id, emote['code'], f'{CDN_URLS["bttv"]}/{emote_id}/3x.{emote["imageType"]}')
                    break
    return e

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
        if(len(emotes[i]['urls']) == 1):
            emote = Emote(emotes[i]['id'], emotes[i]['name'], f'{CDN_URLS["ffz"]}/{emotes[i]["id"]}/1')
        else:
            emote = Emote(emotes[i]['id'], emotes[i]['name'], f'{CDN_URLS["ffz"]}/{emotes[i]["id"]}/4')
        emote_set.append(emote)
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
            if '3.0' in emotes[i]['scale']:
                if 'animated' in emotes[i]['format']:
                    url = f'{CDN_URLS["twitch"]}/{emotes[i]["id"]}/animated/light/3.0'
                else:
                    url = f'{CDN_URLS["twitch"]}/{emotes[i]["id"]}/static/light/3.0'
            else:
                url = f'{CDN_URLS["twitch"]}/{emotes[i]["id"]}/static/light/1.0'
            emote = Emote(emotes[i]['id'], emotes[i]['name'], url)
            emote_set.append(emote)
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