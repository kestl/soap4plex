# -*- coding: utf-8 -*-

# created by sergio
# updated by kestl1st@gmail.com (@kestl) v.1.2.1 2014-06-09
# updated by sergio v.1.2.2 2014-08-28

import re,urllib2,base64,hashlib,md5,urllib
import calendar
from datetime import *
import time

VERSION = 2.0
PREFIX = "/video/soap4me"
TITLE = 'soap4.me'
ART = 'art.png'
ICON = 'icon.png'
BASE_URL = 'http://soap4.me/'
API_URL = 'http://soap4.me/api/'
LOGIN_URL = 'http://soap4.me/login/'
USER_AGENT = 'xbmc for soap'
LOGGEDIN = False
TOKEN = False
SID = ''

def Start():
	ObjectContainer.art = R(ART)
	ObjectContainer.title1 = TITLE
	DirectoryObject.thumb = R(ICON)

	HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = USER_AGENT
	HTTP.Headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
	HTTP.Headers['Accept-Encoding'] ='gzip,deflate,sdch'
	HTTP.Headers['Accept-Language'] ='ru-ru,ru;q=0.8,en-us;q=0.5,en;q=0.3'
	HTTP.Headers['x-api-token'] = TOKEN


def Login():
	global LOGGEDIN, SID, TOKEN

	if not Prefs['username'] and not Prefs['password']:
		return 2
	else:

		try:
			values = {
				'login' : Prefs["username"],
				'password' : Prefs["password"]}

			obj = JSON.ObjectFromURL(LOGIN_URL, values, encoding='utf-8', cacheTime=1,)
		except:
			obj=[]
			LOGGEDIN = False
			return 3
		SID = obj['sid']
		TOKEN = obj['token']
		if len(TOKEN) > 0:
			LOGGEDIN = True
			Dict['sid'] = SID
			Dict['token'] = TOKEN

			return 1
		else:
			LOGGEDIN = False
			Dict['sessionid'] = ""

			return 3


def Thumb(url):
	if url=='':
		return Redirect(R(ICON))
	else:
		try:
			data = HTTP.Request(url, cacheTime=CACHE_1WEEK).content
			return DataObject(data, 'image/jpeg')
		except:
			return Redirect(R(ICON))


@handler(PREFIX, TITLE, thumb=ICON, art=ART)
def MainMenu():

	oc = ObjectContainer()
	oc.add(DirectoryObject(key=Callback(Soaps, title2=u'Все сериалы', filter='all'), title=u'Все сериалы'))
	oc.add(DirectoryObject(key=Callback(Soaps, title2=u'Я смотрю', filter='watching'), title=u'Я смотрю'))
	oc.add(DirectoryObject(key=Callback(Soaps, title2=u'Новые эпизоды', filter='unwatched'), title=u'Новые эпизоды'))
	oc.add(PrefsObject(title=u'Настройки', thumb=R('settings.png')))

	return oc


@route(PREFIX+'/{filter}')
def Soaps(title2, filter):

	logged = Login()
	if logged == 2:
		return MessageContainer(
			"Ошибка",
			"Ведите пароль и логин"
		)

	elif logged == 3:
		return MessageContainer(
			"Ошибка",
			"Отказано в доступе"
		)
	else:

		dir = ObjectContainer(title2=title2.decode())
		if filter == 'all':
			url = API_URL + 'soap/'
		else:
			url = API_URL + 'soap/my/'
		obj = GET(url)

		obj=sorted(obj, key=lambda k: k['title'])

		for items in obj:
			if filter == 'unwatched' and items["unwatched"] == None:
				continue
			soap_title = items["title"]
			if filter != 'unwatched':
				title = soap_title
			else:
				title = items["title"]+ " (" +str(items["unwatched"])+ ")"
			summary = items["description"]
			poster = 'http://covers.s4me.ru/soap/big/'+items["sid"]+'.jpg'
			rating = float(items["imdb_rating"])
			summary = summary.replace('&quot;','"')
			fan = 'http://thetvdb.com/banners/fanart/original/'+items['tvdb_id']+'-1.jpg'
			id = items["sid"]
			thumb = Function(Thumb, url=poster)
			dir.add(TVShowObject(key=Callback(show_seasons, id = id, soap_title = soap_title, filter = filter, unwatched = filter=='unwatched'), rating_key = str(id), title = title, summary = summary, art = fan,rating = rating, thumb = thumb))
		return dir


@route(PREFIX+'/{filter}/{id}', unwatched=bool)
def show_seasons(id, soap_title, filter, unwatched = False):

	dir = ObjectContainer(title2 = soap_title)
	url = API_URL + 'episodes/'+id
	data = GET(url)
	season = {}
	useason = {}
	s_length = {}
	
	Log.Debug(str(data))

	if unwatched:
		for episode in data:
			if episode['watched'] == None:
				if int(episode['season']) not in season:
					season[int(episode['season'])] = episode['season_id']
				if int(episode['season']) not in useason.keys():
					useason[int(episode['season'])] = []
					useason[int(episode['season'])].append(int(episode['episode']))
				elif int(episode['episode']) not in useason[int(episode['season'])]:
					useason[int(episode['season'])].append(int(episode['episode']))
	else:
		for episode in data:
			if int(episode['season']) not in season:
				season[int(episode['season'])] = episode['season_id']
				s_length[int(episode['season'])] = [episode['episode'],]
			else:
				if episode['episode'] not in s_length[int(episode['season'])]:
					s_length[int(episode['season'])].append(episode['episode'])

	for row in season:
		if unwatched:
			title = "%s сезон (%s)" % (row, len(useason[row]))
		else:
			title = "%s сезон" % (row)
		season_id = str(row)
		poster = "http://covers.s4me.ru/season/big/%s.jpg" % season[row]
		thumb=Function(Thumb, url=poster)
		dir.add(SeasonObject(key=Callback(show_episodes, sid = id, season = season_id, filter=filter, soap_title=soap_title, unwatched = unwatched), episode_count=len(s_length[row]) if s_length else len(useason[row]), show=soap_title, rating_key=str(row), title = title, thumb = thumb))
	return dir

@route(PREFIX+'/{filter}/{sid}/{season}', allow_sync=True, unwatched=bool)
def show_episodes(sid, season, filter, soap_title, unwatched = False):

	dir = ObjectContainer(title2 = u'%s - %s сезон ' % (soap_title, season))
	url = API_URL + 'episodes/'+sid
	data = GET(url)
	quality = Prefs["quality"]
	sort = Prefs["sorting"]
	show_only_hd = False

	if quality == "HD":
		for episode in data:
			if season == episode['season']:
				if episode['quality'] == '720p':
					show_only_hd = True
					break
	if sort != 'да':
		data = reversed(data)

	for row in data:
		if season == row['season']:

			if quality == "HD" and show_only_hd == True and row['quality'] != '720p':
				continue
			elif quality == "SD" and show_only_hd == False and row['quality'] != 'SD':
				continue
			else:
				if row['watched'] != None and unwatched:
					continue
				else:
					eid = row["eid"]
					ehash = row['hash']
					sid = row['sid']
					title = ''
					if not row['watched'] and not unwatched:
						title += '* '
					title += "S" + str(row['season']) \
							+ "E" + str(row['episode']) + " | " \
							+ row['quality'].encode('utf-8') + " | " \
							+ row['translate'].encode('utf-8') + " | " \
							+ row['title_en'].encode('utf-8').replace('&#039;', "'").replace("&amp;", "&").replace('&quot;','"')
					poster = "http://covers.s4me.ru/season/big/%s.jpg" % row['season_id']
					summary = row['spoiler']
					thumb = Function(Thumb, url=poster)
					dir.add(EpisodeObject(
						key=Callback(play_episode, sid = sid, eid = eid, ehash = ehash, row=row),
						rating_key='soap4me' + row["eid"],
						title=title,
						index=int(row['episode']),
						thumb=thumb,
						summary=summary,
						items=[MediaObject(parts=[PartObject(key=Callback(episode_url, sid=sid, eid=eid, ehash=ehash, part=0)), PartObject(key=Callback(episode_url, sid=sid, eid=eid, ehash=ehash, part=1))])]
					))
	return dir

def play_episode(sid, eid, ehash, row, includeExtras=0, includeRelated=0, includeRelatedCount=0):
	oc = ObjectContainer()
	oc.add(EpisodeObject(
		key=Callback(play_episode, sid = sid, eid = eid, ehash = ehash, row=row),
		rating_key='soap4me' + row["eid"],
		items=[MediaObject(
			video_resolution = 720 if row['quality'].encode('utf-8')=='720p' else 400,
			video_codec = VideoCodec.H264,
			audio_codec = AudioCodec.AAC,
			container = Container.MP4,
			optimized_for_streaming = True,
			audio_channels = 2,
			parts = [PartObject(key=Callback(episode_url, sid=sid, eid=eid, ehash=ehash, part=0)), PartObject(key=Callback(episode_url, sid=sid, eid=eid, ehash=ehash, part=1))]
		)]
	))
	return oc

def episode_url(sid, eid, ehash, part):
	token = Dict['token']
	if part==1:
		if Prefs["mark_watched"]=='да':
			params = {"what": "mark_watched", "eid": eid, "token": token}
			data = JSON.ObjectFromURL("http://soap4.me/callback/", params, headers = {'x-api-token': Dict['token'], 'Cookie': 'PHPSESSID='+Dict['sid']})
		return Redirect('https://soap4.me/assets/blank/blank1.mp4')

	myhash = hashlib.md5(str(token)+str(eid)+str(sid)+str(ehash)).hexdigest()
	params = {"what": "player", "do": "load", "token":token, "eid":eid, "hash":myhash}

	data = JSON.ObjectFromURL("http://soap4.me/callback/", params, headers = {'x-api-token': Dict['token'], 'Cookie': 'PHPSESSID='+Dict['sid']})
	if data["ok"] == 1:
		return Redirect("http://%s.soap4.me/%s/%s/%s/" % (data['server'], token, eid, myhash))

def GET(url):
	return JSON.ObjectFromURL(url, headers = headers = {'x-api-token': Dict['token'], 'Cookie': 'PHPSESSID='+Dict['sid']}, cacheTime = 0)
