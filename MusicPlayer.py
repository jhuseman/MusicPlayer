#! /usr/bin/env python

from Music import *
from WebHost import *
import random
import threading
import time

def decode_song_id(id):
	return id.replace('|','/')

class MusicInterface(WebInterface):
	def __init__(self,host,music):
		self.host = host
		self.music = music
		self.connect('/songs/','GET_SONGS','GET')
		self.connect('/add_song/:song','ADD_SONG','GET')
		self.connect('/add_song/:song/:pos','ADD_SONG_POS','GET')
		self.connect('/del_song/:song','DEL_SONG','GET')
		self.connect('/set_vol/:vol','SET_VOL','GET')
		self.connect('/skip_song/','DEL_TOP_SONG','GET')
		self.connect('/clear_playlist/','CLEAR_SONGS','GET')
		self.connect('/avail_songs/','GET_AVAIL_SONGS','GET')
		self.connect('/song_info/:song','GET_SONG_INFO','GET')
		self.connect('/song_info/','GET_ALL_SONG_INFO','GET')
		self.connect('/pause/','PAUSE','GET')
		self.connect('/unpause/','UNPAUSE','GET')
	
	def GET_SONGS(self):
		"""return list of current music information"""
		return json.dumps(self.music.getDict(), indent=4)
	
	def ADD_SONG(self,song):
		"""add song to end of playlist"""
		self.music.addSong(decode_song_id(song))
		return json.dumps(self.music.getDict(), indent=4)
	
	def ADD_SONG_POS(self,song,pos):
		"""add song to playlist at pos"""
		self.music.addSongPos(int(pos),decode_song_id(song))
		return json.dumps(self.music.getDict(), indent=4)
	
	def DEL_SONG(self,song):
		"""remove song from playlist"""
		self.music.removeSong(decode_song_id(song))
		return json.dumps(self.music.getDict(), indent=4)
	
	def SET_VOL(self,vol):
		"""set volume of playback"""
		self.music.setVol(int(vol))
		return json.dumps(self.music.getDict(), indent=4)
	
	def DEL_TOP_SONG(self):
		"""skip first song in playlist"""
		self.music.removeTopSong()
		return json.dumps(self.music.getDict(), indent=4)
	
	def CLEAR_SONGS(self):
		"""remove all songs in playlist"""
		self.music.setSongList([])
		return json.dumps(self.music.getDict(), indent=4)
	
	def GET_AVAIL_SONGS(self):
		"""list all songs that can be played"""
		return json.dumps(self.music.getAvailableSongs(), indent=4)
	
	def GET_SONG_INFO(self,song):
		"""get information about song"""
		return json.dumps(self.music.getSongInfo(decode_song_id(song)), indent=4)
	
	def GET_ALL_SONG_INFO(self):
		"""get information about all songs"""
		info = {}
		for song in self.music.getAvailableSongs():
			info[song] = self.music.getSongInfo(song)
		return json.dumps(info, indent=4)
	
	def PAUSE(self):
		"""pause the current song"""
		self.music.pause()
		return json.dumps(self.music.getDict(), indent=4)
	
	def UNPAUSE(self):
		"""unpause the current song"""
		self.music.unpause()
		return json.dumps(self.music.getDict(), indent=4)


def playlist_maintain(music,min_items):
	try:
		while True:
			if len(music.getSongList())<min_items:
				avail = music.getAvailableSongs()
				rand = random.randint(0,len(avail)-1)
				music.addSong(avail[rand])
			time.sleep(0.5)
	except KeyboardInterrupt:
		pass

def startMusicInterface(port,mus_dir, init_vol=75, init_paused=True):
	host = WebHost(port)
	music = Music(mus_dir=mus_dir, init_vol=init_vol, init_paused=init_paused)
	MusicInterface(host,music)
	thr = threading.Thread(target=host.start_service)
	thr.start()
	playlist_maintain(music,5)
	# exiting after returns - shut everything down!
	del music
	host.stop_service()

if __name__=="__main__":
	mus_dir='/mnt/usb/Christmas/'
	# mus_dir='/mnt/c/Users/jdhus/OneDrive/Music/Christmas/'
	startMusicInterface(80,mus_dir, init_vol=75, init_paused=True)
