import vlc
import os
import time

class vlcplay:
	def __init__(self,mus_dir=None,muted=False,init_vol=100):
		self.mus_dir = mus_dir
		self.muted = muted
		self.volume = init_vol
		self.player = None
		self.ensureVolumeSet()
		self.is_paused = False
	
	def __del__(self):
		if self.player!=None:
			self.player.stop()
	
	def getPaused(self):
		return self.is_paused
	
	def fileExists(self,filename):
		path = filename
		if not self.mus_dir is None:
			path = os.path.join(self.mus_dir,path)
		return os.path.isfile(path)
	
	def stop(self):
		if self.player is not None:
			self.player.stop()
	
	def pause(self):
		self.is_paused = True
		if self.player is not None:
			self.player.pause()
	
	def unpause(self):
		if self.getPaused():
			self.is_paused = False
			if self.player is not None:
				self.player.play()
	
	def ensureVolumeSet(self):
		if self.player is not None:
			if self.muted:
				self.player.audio_set_volume(0)
			else:
				self.player.audio_set_volume(int(self.volume))
	
	def setVolume(self,volume):
		self.volume = int(volume)
		if self.volume<0:
			self.volume = 0
		if self.volume>100:
			self.volume = 100
		self.ensureVolumeSet()
	
	def playFile(self,filename):
		if self.player is not None:
			self.player.stop()
			self.player = None
		print('loading file {}'.format(filename))
		if self.fileExists(filename):
			self.player = vlc.MediaPlayer(filename)
			self.ensureVolumeSet()
			if not self.is_paused:
				self.player.play()
				while self.player.get_state()!=vlc.State.Playing:
					print('waiting for file to load...')
					time.sleep(0.1)
			return {'filename': filename}
		else:
			return None
	
	def getPos(self):
		if self.player is None:
			return {
			'length'	: 0,
			'pos'		: 0,
			'fraction'	: 0,
			'paused'	: True,
			'vol'		: 0,
		}
		return {
			'length'	: float(self.player.get_length())/1000,
			'pos'		: float(self.player.get_time())/1000,
			'fraction'	: self.player.get_position(),
			'paused'	: self.getPaused(),
			'vol'		: self.player.audio_get_volume(),
		}
	
	def getFinished(self):
		if self.player is None:
			return True
		return self.player.get_state()==vlc.State.Ended
	
