import tinytag

class SongInfo:
	def __init__(self):
		self.songdict = {}
	
	def __del__(self):
		for song in self.songdict:
			self.remove(song)
	
	def remove(self,song):
		if song in self.songdict:
			del self.songdict[song]
	
	def getInfo(self,song):
		if song in self.songdict:
			return self.songdict[song]
		else:
			details = tinytag.TinyTag.get(song)
			info = {
				'filename': song,
				'album': details.album,
				'artist': details.artist,
				'bitrate': details.bitrate,
				'albumartist': details.albumartist,
				'samplerate': details.samplerate,
				'composer': details.composer,
				'duration': details.duration,
				'filepath': song,
				'genre': details.genre,
				'year': details.year,
				'title': details.title,
				'track': details.track,
				'track_total': details.track_total,
				'audio_offset': details.audio_offset,
				'channels': details.channels,
				'comment': details.comment,
				'disc': details.disc,
				'disc_total': details.disc_total,
				'filesize': details.filesize,
				'samplerate': details.samplerate,
			}
			self.songdict[song] = info
			return info
	
	def getInfoList(self,list):
		ret = {}
		for song in list:
			ret[song] = self.getInfo(song)
		return ret
	
	def getDict(self):
		return self.songdict
	
