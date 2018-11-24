import subprocess
import threading
import os
import time

class mplayer:
	def __init__(self,mus_dir=None,muted=False,init_vol=100):
		self.mus_dir = mus_dir
		self.muted = muted
		self.volume = init_vol
		self.IOlock = threading.Lock()
		self.player = None
		if self.muted:
			self.player = subprocess.Popen(['mplayer','-slave','-quiet','-idle','-nosound'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.mus_dir)
		else:
			self.player = subprocess.Popen(['mplayer','-slave','-quiet','-idle'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.mus_dir)
		self.getPaused()
		if self.muted:
			self.getCmdOutput('mute 1')
		self.ensureVolumeSet()
	
	def __del__(self):
		# stop all music playback here
		with self.IOlock:
			self.sendCmd('quit')
		self.player.wait()
	
	def sendCmd(self,cmd):
		self.player.stdin.write('\n')
		time.sleep(0.1)
		self.player.stdin.write(cmd)
		self.player.stdin.write('\n')
	
	def getLine(self):
		return self.player.stdout.readline()
	
	def getOutputData(self):
		out_data = []
		self.sendCmd('get_property pause')
		line = self.getLine()
		while not line.startswith('ANS_pause='):
			out_data.append(line.rstrip())
			line = self.getLine()
		return out_data
	
	def getPaused(self):
		with self.IOlock:
			self.sendCmd('get_property pause')
			line = self.getLine()
			while not line.startswith('ANS_pause='):
				line = self.getLine()
		return [line.rstrip()]
	
	def isPaused(self):
		return self.parseResults(self.getPaused())['ANS_pause']=='yes'
	
	def getCmdOutput(self,cmd):
		self.getPaused()
		if cmd=='get_property pause':
			return self.getPaused()
		else:
			with self.IOlock:
				self.sendCmd(cmd)
				return self.getOutputData()
	
	def parseResults(self,results):
		info = {}
		for item in results:
			spl = item.split('=',1)
			if len(spl)>=2:
				info[spl[0].strip()] = spl[1].strip()
		return info
	
	def getFirstResult(self,results):
		parsed = self.parseResults(results)
		keys = parsed.keys()
		if len(keys)>0:
			key = keys[0]
			return parsed[key]
		else:
			return None
	
	def getCmdProperty(self,cmd):
		return self.getFirstResult(self.getCmdOutput(cmd))
	
	def getProperty(self,property):
		return self.getCmdProperty('get_property '+property)
	
	def fileExists(self,filename):
		path = filename
		if not self.mus_dir is None:
			path = os.path.join(self.mus_dir,path)
		return os.path.isfile(path)
	
	def stop(self):
		self.getCmdOutput('stop')
	
	def pause(self):
		while not self.isPaused():
			self.getCmdOutput('pause')
	
	def unpause(self):
		while self.isPaused():
			self.getCmdOutput('pause')
	
	def ensureVolumeSet(self):
		if self.muted:
			self.getCmdOutput('volume 0 1')
			self.getCmdOutput('mute 1')
		else:
			self.getCmdOutput('volume '+str(int(self.volume))+' 1')
			self.getCmdOutput('mute 0')
	
	def setVolume(self,volume):
		self.volume = int(volume)
		if self.volume<0:
			self.volume = 0
		if self.volume>100:
			self.volume = 100
		self.ensureVolumeSet()
	
	def playFile(self,filename):
		if self.fileExists(filename):
			out = self.getCmdOutput('loadfile "'+filename+'"')
			try:
				info = {'filename': filename}
				ind = out.index('Clip info:')
				for item in out[ind+1:]:
					if item.startswith(' '):
						spl = item.split(':',1)
						if len(spl)>=2:
							info[spl[0].strip()] = spl[1].strip()
				self.ensureVolumeSet()
				return info
			except:
				print(out)
				self.ensureVolumeSet()
				return {'filename': filename}
		else:
			return None
	
	def getPos(self):
		length = self.getCmdProperty('get_time_length')
		pos = self.getCmdProperty('get_time_pos')
		paused = self.isPaused()
		vol = self.volume
		if length == None:
			length = 1.0
		else:
			length = float(length)
		if pos == None:
			pos = 1.0
		else:
			pos = float(pos)
		fraction = pos/length
		return {
			'length'	: length,
			'pos'		: pos,
			'fraction'	: fraction,
			'paused'	: paused,
			'vol'		: vol,
		}
	
	def getFinished(self):
		return self.getPos()['fraction']==1.0
	