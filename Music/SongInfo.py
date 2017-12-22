# from mplayer import *
import songdetails

class SongInfo:
	def __init__(self):
		self.songdict = {}
		# self.mplay = mplayer(muted=True)
	
	def __del__(self):
		for song in self.songdict:
			self.remove(song)
		# del self.mplay
	
	def remove(self,song):
		if song in self.songdict:
			del self.songdict[song]
	
	def getInfo(self,song):
		if song in self.songdict:
			return self.songdict[song]
		else:
			details = songdetails.scan(song)
			info = {'filename': song}
			attributes = [
				'album',
				'artist',
				'bitrate',
				'composer',
				'duration',
				'filepath',
				'genre',
				'is_lossless',
				'language',
				'published',
				'recorded',
				'title',
				'track',
				'year',
			]
			for attr in attributes:
				try:
					if attr=='duration':
						info[attr] = getattr(details,attr).total_seconds()
					else:
						info[attr] = getattr(details,attr)
				except:
					info[attr] = None
			# info = self.mplay.playFile(song)
			self.songdict[song] = info
			return info
	
	def getInfoList(self,list):
		ret = {}
		for song in list:
			ret[song] = self.getInfo(song)
		return ret
	
	def getDict(self):
		return self.songdict
	
