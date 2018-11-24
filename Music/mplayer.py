import mpv
# import subprocess
# import threading
import os
# import time

class mplayer:
	def __init__(self,mus_dir=None,muted=False,init_vol=100):
		self.mus_dir = mus_dir
		self.muted = muted
		self.volume = init_vol
		# self.IOlock = threading.Lock()
		# self.player = None
		self.player = mpv.Context()
		self.player.initialize()
		# # # # # # # if self.muted:
		# # # # # # # 	self.player = subprocess.Popen(['mplayer','-slave','-quiet','-idle','-nosound'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.mus_dir)
		# # # # # # # else:
		# # # # # # # 	self.player = subprocess.Popen(['mplayer','-slave','-quiet','-idle'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.mus_dir)
		# self.getPaused()
		if self.muted:
			self.player.set_property('mute',True)
		self.ensureVolumeSet()
	
	def __del__(self):
		# stop all music playback here
		# with self.IOlock:
		self.player.command('stop')
		self.player.command('quit')
		# self.player.wait()
	
	# def runCommand(self,cmd):
	# 	self.player.command(*cmd)
	# 	# self.player.stdin.write('\n')
	# 	# time.sleep(0.1)
	# 	# self.player.stdin.write(cmd)
	# 	# self.player.stdin.write('\n')
	
	# def getLine(self):
	# 	# DEPRECATED!
	# 	return self.player.stdout.readline()
	
	# def getOutputData(self):
	# DEPRECATED!
	# 	out_data = []
	# 	# self.sendCmd('get_property pause')
	# 	line = self.getLine()
	# 	while not line.startswith('ANS_pause='):
	# 		out_data.append(line.rstrip())
	# 		line = self.getLine()
	# 	return out_data
	
	def getPaused(self):
		return self.player.get_property('pause')
	
	# def getPaused(self):
	# 	return self.getPaused()
	
	# def runCommand(self,cmd):
	# 	# self.getPaused()
	# 	# if cmd==['get_property','pause']:
	# 	# 	return self.getPaused()
	# 	# else:
	# 	# with self.IOlock:
	# 	self.sendCmd(cmd)
	# 	# return self.getOutputData()
	
	# def parseResults(self,results):
	# 	# DEPRECATED!
	# 	info = {}
	# 	for item in results:
	# 		spl = item.split('=',1)
	# 		if len(spl)>=2:
	# 			info[spl[0].strip()] = spl[1].strip()
	# 	return info
	
	# def getFirstResult(self,results):
	# 	# DEPRECATED!
	# 	parsed = self.parseResults(results)
	# 	keys = parsed.keys()
	# 	if len(keys)>0:
	# 		key = keys[0]
	# 		return parsed[key]
	# 	else:
	# 		return None
	
	# def getCmdProperty(self,cmd):
	# DEPRECATED!
	# 	return self.getFirstResult(self.runCommand(cmd))
	
	def getProperty(self,property):
		return self.player.get_property(property)
	
	def fileExists(self,filename):
		path = filename
		if not self.mus_dir is None:
			path = os.path.join(self.mus_dir,path)
		return os.path.isfile(path)
	
	def stop(self):
		self.player.command('stop')
	
	def pause(self):
		self.player.set_property('pause',True)
		# while not self.getPaused():
		# 	self.player.command('pause')
	
	def unpause(self):
		self.player.set_property('pause',False)
		# while self.getPaused():
		# 	self.player.command('pause')
	
	def ensureVolumeSet(self):
		if self.muted:
			self.player.set_property('volume',0)
			self.player.set_property('mute',True)
		else:
			self.player.set_property('volume',int(self.volume))
			self.player.set_property('mute',False)
	
	def setVolume(self,volume):
		self.volume = int(volume)
		if self.volume<0:
			self.volume = 0
		if self.volume>100:
			self.volume = 100
		self.ensureVolumeSet()
	
	def playFile(self,filename):
		if self.fileExists(filename):
			self.player.command('loadfile',filename)
			self.ensureVolumeSet()
			return {'filename': filename}
		else:
			return None
	
	def getPos(self):
		try:
			pos = self.getProperty('time-pos')
		except mpv.MPVError as e:
			print("ERROR time-pos: {}".format(e))
			pos = None
		try:
			length = self.getProperty('duration')
		except mpv.MPVError as e:
			if pos is None:
				print("ERROR duration: {}".format(e))
				length = None
			else:
				try:
					rem = self.getProperty('time-remaining')
					length = rem + pos
				except mpv.MPVError as e:
					print("ERROR time-remaining: {}".format(e))
					length = None
		paused = self.getPaused()
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
		return self.getPos()['fraction']>=1.0
	