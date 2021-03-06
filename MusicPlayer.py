#! /usr/bin/env python

from Music import Music
import random
import threading
import time
import json
import guavacado
import os
import argparse

class MusicInterface():
	def __init__(self,port,mus_dir, init_vol=75, init_paused=True, queue_size=5):
		self.host = guavacado.WebHost()
		self.host.add_addr(port=port)
		self.queue_size = queue_size
		self.music = Music.Music(mus_dir=mus_dir, init_vol=init_vol, init_paused=init_paused)
		self.web_interface = guavacado.WebInterface(host=self.host)
		self.web_files = guavacado.WebFileInterface(host=self.host, staticdir='static')
		self.web_interface.connect('/songs/',self.GET_SONGS,'GET')
		self.web_interface.connect('/add_song/:song',self.ADD_SONG,'GET')
		self.web_interface.connect('/add_song/:song/:pos',self.ADD_SONG_POS,'GET')
		self.web_interface.connect('/del_song/:song',self.DEL_SONG,'GET')
		self.web_interface.connect('/set_vol/:vol',self.SET_VOL,'GET')
		self.web_interface.connect('/skip_song/',self.DEL_TOP_SONG,'GET')
		self.web_interface.connect('/clear_playlist/',self.CLEAR_SONGS,'GET')
		self.web_interface.connect('/avail_songs/',self.GET_AVAIL_SONGS,'GET')
		self.web_interface.connect('/song_info/:song',self.GET_SONG_INFO,'GET')
		self.web_interface.connect('/song_info/',self.GET_ALL_SONG_INFO,'GET')
		self.web_interface.connect('/pause/',self.PAUSE,'GET')
		self.web_interface.connect('/unpause/',self.UNPAUSE,'GET')
	
	def GET_SONGS(self):
		"""return list of current music information"""
		return json.dumps(self.music.getDict(), indent=4)
	
	def ADD_SONG(self,song):
		"""add song to end of playlist"""
		self.music.addSong(song)
		return json.dumps(self.music.getDict(), indent=4)
	
	def ADD_SONG_POS(self,song,pos):
		"""add song to playlist at pos"""
		self.music.addSongPos(int(pos),song)
		return json.dumps(self.music.getDict(), indent=4)
	
	def DEL_SONG(self,song):
		"""remove song from playlist"""
		self.music.removeSong(song)
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
		return json.dumps(self.music.getSongInfo(song), indent=4)
	
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

	def playlist_maintain(self):
		while not self.stopping:
			if len(self.music.getSongList())<self.queue_size:
				avail = self.music.getAvailableSongs()
				if len(avail) > 0:
					rand = random.randint(0,len(avail)-1)
					if avail[rand] not in self.music.getSongList():
						self.music.addSong(avail[rand])
			time.sleep(0.5)

	def playlist_maintain_async(self):
		self.playlist_maintain_thread = threading.Thread(target=self.playlist_maintain, name='PlaylistFiller')
		self.playlist_maintain_thread.start()
	
	def start(self):
		self.host.start_service()
		self.stopping = False
		self.playlist_maintain_async()
		guavacado.wait_for_keyboardinterrupt()
		# exiting after returns - shut everything down!
		self.stopping = True
		self.music.shutdown()
		del self.music
		self.host.stop_service()

if __name__=="__main__":
	parser = argparse.ArgumentParser(description='Play music out of a directory and host a web interface to configure it.')
	parser.add_argument('-d', '--dir', '--mus_dir', dest='mus_dir', type=str, default='/mnt/usb/Christmas/',
		help='directory in which to search for music - default: /mnt/usb/Christmas/')
	parser.add_argument('-v', '--vol', '--init_vol', dest='init_vol', type=int, default=75,
		help='initial volume, on a scale of 0 - 100 - default: 75')
	parser.add_argument('-p', '--play', '--playing', '--start_playing', dest='init_paused', action='store_false',
		help='start playing automatically without user input')
	parser.add_argument('-n', '-q', '--num', '--num_queue', '--queue', '--queue_size', dest='queue_size', type=int, default=5,
		help='number of songs to keep in the queue automatically - keep above 1 to play continuously - default: 5')
	parser.add_argument('--port', '--port_no', dest='port_no', type=int, default=80,
		help='port number to run web interface - default: 80')
	args = parser.parse_args()
	# mus_dir='/mnt/usb/Christmas/'
	# mus_dir='/mnt/c/Users/jdhus/OneDrive/Music/Christmas/'
	# mus_dir='C:\\Users\\jdhus\\OneDrive\\Music\\Christmas\\'
	# mus_dir='C:\\Users\\jhuseman\\OneDrive\\Music\\Christmas\\'
	MusicInterface(args.port_no,args.mus_dir, init_vol=args.init_vol, init_paused=args.init_paused, queue_size=args.queue_size).start()
