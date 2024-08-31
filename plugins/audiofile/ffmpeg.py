# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins

class input_pyav(plugins.base):
	try:
		import av
		usable = True
	except:
		usable = False

	def is_dawvert_plugin(self): return 'audiofile'
	def getshortname(self): return 'ffmpeg'
	def getaudiofileinfo(self, audiofileinfo_obj):
		audiofileinfo_obj.file_formats = ['wav', 'mp3', 'flac', 'ogg', 'wv']
	def getinfo(self, input_file, sampleref_obj, fileextlow):
		valid = False
		if self.usable:
			avdata = self.av.open(input_file)
			if len(avdata.streams.audio) != 0:
				avaudio = avdata.streams.audio[0]
				sampleref_obj.dur_samples = avaudio.duration
				if sampleref_obj.dur_samples == None: sampleref_obj.dur_samples = 0
				sampleref_obj.timebase = avaudio.time_base.denominator
				audio_hz_b = avaudio.rate
				if audio_hz_b != None: sampleref_obj.hz = audio_hz_b
				sampleref_obj.dur_sec = (sampleref_obj.dur_samples/sampleref_obj.timebase)
				if avaudio.channels: sampleref_obj.channels = avaudio.channels
				valid = True
				sampleref_obj.fileformat = sampleref_obj.fileref.file.extension.lower()
				if sampleref_obj.fileformat == 'wav':
					if avaudio.codec.name not in ['pcm_f32le', 'pcm_s16le', 'pcm_s24le', 'pcm_u8']:
						sampleref_obj.fileformat = 'wav_codec'

		return valid