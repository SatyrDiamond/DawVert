# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins

class input_soundfile(plugins.base):
	try:
		from soundfile import SoundFile
		usable = True
	except:
		usable = False

	def is_dawvert_plugin(self): return 'audiofile'
	def getshortname(self): return 'soundfile'
	def getaudiofileinfo(self, audiofileinfo_obj):
		audiofileinfo_obj.file_formats = ['wav', 'mp3', 'flac', 'ogg']
	def getinfo(self, input_file, sampleref_obj, fileextlow):
		valid = False
		if self.usable:
			sf_audio = self.SoundFile(input_file)
			sampleref_obj.hz = sf_audio.samplerate
			sampleref_obj.timebase = sf_audio.samplerate
			sampleref_obj.dur_samples = sf_audio.frames
			sampleref_obj.dur_sec = sf_audio.frames/sf_audio.samplerate
			sampleref_obj.channels = sf_audio.channels
			if fileextlow == 'mp3': 
				sampleref_obj.timebase *= 320
				sampleref_obj.dur_samples *= 320
			sampleref_obj.fileformat = sampleref_obj.fileref.extension.lower()
			return True

		return valid