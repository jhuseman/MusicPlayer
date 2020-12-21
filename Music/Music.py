from . import vlcplay
from . import SongInfo
from . import listfiles
import threading
import time

class Music:
	def __init__(self,mus_dir=None, init_vol=75, init_paused=True):
		self.songlist = []
		self.songinfo = SongInfo.SongInfo()
		self.currentsong = ''
		self.mus_dir = mus_dir
		self.mplay = vlcplay.vlcplay(mus_dir=self.mus_dir, init_vol=75)
		if init_paused:
			self.mplay.pause()
		self.keepUpdatedAsync()
	
	def __del__(self):
		self.shutdown()
	
	def shutdown(self):
		# stop all music playback here
		self.updating = False
		if not self.update_thread is None:
			self.update_thread.join()
			self.update_thread = None
		if self.mplay is not None:
			self.mplay.stop()
			del self.mplay
			self.mplay = None
		if self.songinfo is not None:
			del self.songinfo
			self.songinfo = None
	
	def getTime(self):
		return self.mplay.getPos()
	
	def setSongList(self,list):
		self.songlist = list
	
	def appendSongList(self,list):
		self.songlist = self.songlist + list
	
	def getSongList(self):
		return self.songlist
	
	def addSong(self,song):
		self.songlist.append(song)
	
	def addSongPos(self,pos,song):
		self.songlist.insert(pos,song)
	
	def removeSong(self,song):
		self.songlist.remove(song)
		self.songinfo.remove(song)
	
	def removeTopSong(self):
		self.removeSong(self.songlist[0])
	
	def removeSongsBefore(self,song):
		while self.songlist.index(song)>0:
			self.removeTopSong()
	
	def moveSongPos(self,pos,song):
		self.removeSong(song)
		self.addSongPos(pos,song)
	
	def startSong(self,song):
		self.currentsong = song
		if not song in self.songlist:
			self.addSongPos(0,song)
		self.removeSongsBefore(song)
		self.mplay.playFile(song)
	
	def pause(self):
		self.mplay.pause()
	
	def unpause(self):
		self.mplay.unpause()
	
	def setVol(self,vol):
		self.mplay.setVolume(vol)
	
	def update(self):
		if self.mplay.getFinished():
			# finished with current song - play next song in songlist (if there is one)
			if len(self.songlist)>0:
				# songlist not empty - choose next item after currentsong
				if self.currentsong in self.songlist:
					# currentsong in songlist - play next item
					ind = self.songlist.index(self.currentsong)+1 # ind = index of next song after currentsong
					if len(self.songlist)>ind:
						# songlist long enough to contain song at ind - play next song
						self.startSong(self.songlist[ind])
					else:
						# at end of songlist - empty list and don't play anything
						self.songlist = []
				else:
					# currentsong not in songlist - play first song in list
					self.startSong(self.songlist[0])
		else:
			# still playing song - check to make sure is still in songlist
			if not self.currentsong in self.songlist:
				# currentsong not in songlist - skip to first item in list
				if len(self.songlist)>0:
					# songlist not empty - play first song in list
					self.startSong(self.songlist[0])
				else:
					# songlist empty - stop playback
					self.mplay.stop()
	
	def keepUpdated(self):
		self.updating = True
		while self.updating:
			self.update()
			time.sleep(0.25)
	
	def keepUpdatedAsync(self):
		self.update_thread = threading.Thread(target=self.keepUpdated, name='PlaybackManager')
		self.update_thread.start()
	
	def getSongInfo(self,song):
		return self.songinfo.getInfo(song)
	
	def getAllSongInfo(self):
		return self.songinfo.getInfoList(self.songlist)
	
	def getAvailableSongs(self):
		extensions = ['.mp3','.wma']
		dir = self.mus_dir
		if dir is None:
			dir = './'
		return listfiles.limit_ext(listfiles.listfiles(dir),extensions)
	
	def getDict(self):
		return {
			'current_song'	: self.currentsong,
			'pos'			: self.mplay.getPos(),
			'song_list'		: self.songlist,
			'song_info'		: self.getAllSongInfo(),
		}
	