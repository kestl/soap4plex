# -*- coding: utf-8 -*-

# created by sergio
# updated by kestl1st@gmail.com (@kestl) v.1.2.1 2014-06-09
# updated by sergio v.1.2.2 2014-08-28

import re,urllib2,base64,hashlib,md5,urllib
import calendar
from datetime import *
import time

VERSION						= 1.3
VIDEO_PREFIX				= "/video/soap4me"
NAME						= 'soap4me'
ART							= 'art.png'
ICON						= 'icon.png'
BASE_URL					= 'http://soap4.me/'
API_URL						= 'http://soap4.me/api/'
LOGIN_URL					= 'http://soap4.me/login/'
USER_AGENT					= 'xbmc for soap'
LOGGEDIN					= False
TOKEN						= False
SID							= ''
title1						= NAME
title2						= ''

def Start():
	Plugin.AddPrefixHandler(VIDEO_PREFIX, MainMenu, NAME, ICON, ART)
	Plugin.AddViewGroup("PanelStream", viewMode = "PanelStream", mediaType = "items")
	Plugin.AddViewGroup("List", viewMode = "List", mediaType = "items")
	MediaContainer.title1 = title1
	MediaContainer.title2 = title2
	MediaContainer.viewGroup = "PanelStream"
	MediaContainer.art = R(ART)
	DirectoryItem.thumb = R(ICON)
	VideoItem.thumb = R(ICON)
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
			#strn = JSON.StringFromObject(obj)
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



def MainMenu():

	dir = MediaContainer(viewGroup="InfoList")
	dir.Append(Function(DirectoryItem(Soaps, title='Все сериалы')))
	dir.Append(Function(DirectoryItem(Watching, title='Я смотрю')))
	dir.Append(Function(DirectoryItem(Unwatched, title='Новые эпизоды')))
	dir.Append(PrefsItem('Настройки ', thumb=R('settings.png')))

	return dir


def Soaps(sender):

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

		dir = MediaContainer(viewGroup='InfoList', title2 = 'список сериалов')
		url = API_URL + 'soap/'
		obj = GET(url)

		for items in obj:
			title = items["title"]
			summary = items["description"]
			poster = 'http://covers.s4me.ru/soap/big/'+items["sid"]+'.jpg'
			rating = items["imdb_rating"]
			summary = summary.replace('&quot;','"')
			fan = 'http://thetvdb.com/banners/fanart/original/'+items['tvdb_id']+'-1.jpg'
			id = items["sid"]
			thumb=Function(Thumb, url=poster)
			dir.Append(Function(DirectoryItem(show_seasons, title = title, summary = summary, art = fan,rating = rating, infoLabel = '', thumb = thumb), id = id, soap_title = title))
		return dir


def Watching(sender):

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

		dir = MediaContainer(viewGroup='InfoList', title2 = 'список сериалов')
		url = API_URL + 'soap/my/'
		obj = GET(url)

		for items in obj:
			#Log.Debug('#####'+str(items).encode('utf-8')+'#####')
			title = items["title"]
			summary = items["description"]
			poster = 'http://covers.s4me.ru/soap/big/'+items["sid"]+'.jpg'
			rating = items["imdb_rating"]
			summary = summary.replace('&quot;','"')
			fan = 'http://thetvdb.com/banners/fanart/original/'+items['tvdb_id']+'-1.jpg'
			id = items["sid"]
			thumb=Function(Thumb, url=poster)
			dir.Append(Function(DirectoryItem(show_seasons, title = title, summary = summary, art = fan,rating = rating, infoLabel = '', thumb = thumb), id = id, soap_title = title))
		return dir

def Unwatched(sender):

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

		dir = MediaContainer(viewGroup='InfoList', title2 = 'список сериалов')
		url = API_URL + 'soap/my/'
		obj = GET(url)

		for items in obj:
			if items["unwatched"]!=None:
				#Log.Debug('#####'+str(items).encode('utf-8')+'#####')
				soap_title = items["title"]
				title = items["title"]+ " (" +str(items["unwatched"])+ ")"
				summary = items["description"]
				poster = 'http://covers.s4me.ru/soap/big/'+items["sid"]+'.jpg'
				rating = items["imdb_rating"]
				summary = summary.replace('&quot;','"')
				fan = 'http://thetvdb.com/banners/fanart/original/'+items['tvdb_id']+'-1.jpg'
				id = items["sid"]
				thumb=Function(Thumb, url=poster)
				dir.Append(Function(DirectoryItem(show_seasons, title = title, summary = summary, art = fan,rating = rating, infoLabel = '', thumb = thumb), id = id, soap_title = soap_title, unwatched = True))
		return dir

def show_seasons(sender, id, soap_title, unwatched = False):

	dir = MediaContainer(viewGroup='InfoList', title2 = 'список сезонов')
	url = API_URL + 'episodes/'+id
	data = GET(url)
	season = {}
	useason = {}
	#Log.Debug('?????'+str(data).encode('utf-8')+'?????')

	if unwatched:
		for episode in data:
			if episode['watched'] == None:
				#Log.Debug(str(episode['episode']))
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

	#Log.Debug(str(useason))

	for row in season:
		#info = {}
		if unwatched:
			title = "%s - Season %s (%s)" % (soap_title, str(row), str(len(useason[row])))
		else:
			title = "%s - Season %s" % (soap_title, str(row))
		season_id = str(row)
		poster = "http://covers.s4me.ru/season/big/%s.jpg"%season[row]
		thumb=Function(Thumb, url=poster)
		dir.Append(Function(DirectoryItem(show_episodes, title = title, thumb = thumb), sid = id, season = season_id, unwatched = unwatched))
	return dir

def show_episodes(sender, sid, season, unwatched = False):

	dir = MediaContainer(viewGroup='InfoList', title2 = 'эпизоды')
	url = API_URL + 'episodes/'+sid
	data = GET(url)
	quality = Prefs["quality"]
	sort = Prefs["sorting"]
	#episode_names = {}
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
					#Log.Debug('!!!!!'+str(row).encode('utf-8')+'!!!!!')
					eid = row["eid"]
					ehash = row['hash']
					sid = row['sid']
					title = ''
					if not row['watched']:
						title += '* ' 
					title += "S" + str(row['season']) \
							+ "E" + str(row['episode']) + " | " \
							+ row['quality'].encode('utf-8') + " | " \
							+ row['translate'].encode('utf-8') + " | " \
							+ row['title_en'].encode('utf-8').replace('&#039;', "'").replace("&amp;", "&").replace('&quot;','"')
					poster = "http://covers.s4me.ru/season/big/%s.jpg"%row['season_id']
					summary = row['spoiler']
					thumb=Function(Thumb, url=poster)
					dir.Append(Function(VideoItem(play_episode, title = title, thumb = thumb, summary = summary), sid = sid, eid = eid, ehash = ehash))
	return dir


def play_episode(sender, sid, eid, ehash):
	token = Dict['token']

	myhash = hashlib.md5(str(token)+str(eid)+str(sid)+str(ehash)).hexdigest()
	params = {"what": "player", "do": "load", "token":token, "eid":eid, "hash":myhash}

	data = JSON.ObjectFromURL("http://soap4.me/callback/", params, headers = {'x-api-token': Dict['token'], 'Cookie': 'PHPSESSID='+Dict['sid']})
	if data["ok"] == 1:
		return Redirect(VideoItem("http://%s.soap4.me/%s/%s/%s/" % (data['server'], token, eid, myhash)))

def GET(url):
	return JSON.ObjectFromURL(url, headers = {'x-api-token': Dict['token']}, cacheTime = 0)

