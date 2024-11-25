# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import importlib.util

class input_pyav(plugins.base):
	def is_dawvert_plugin(self):
		return 'audiofile'
	
	def get_shortname(self):
		return 'ffmpeg'
	
	def get_name(self):
		return 'FFmpeg'
	
	def get_priority(self):
		return 0
	
	def usable(self): 
		usable = importlib.util.find_spec('av')
		usable_meg = '"av" package is not installed.' if not usable else ''
		return usable, usable_meg
		
	def get_prop(self, in_dict): 
		in_dict['file_formats'] = ['wav', 'mp3', 'flac', 'ogg', 'wv']

	def getinfo(self, input_file, sampleref_obj, fileextlow):
		import av
		valid = False
		if self.usable:
			avdata = av.open(input_file)
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