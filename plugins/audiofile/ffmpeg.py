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
		in_dict['file_formats'] = ['wav', 'mp3', 'flac', 'ogg', 'wv', 'm4a']

	def getinfo(self, input_file, sampleref_obj, fileextlow):
		import av
		valid = False
		if self.usable:
			avdata = av.open(input_file)
			if len(avdata.streams.audio) != 0:
				avaudio = avdata.streams.audio[0]

				if avaudio.rate != None: sampleref_obj.set_hz(avaudio.rate)
				if avaudio.duration != None: sampleref_obj.set_dur_samples(avaudio.duration)
				if avaudio.channels != None: sampleref_obj.set_channels(avaudio.channels)
				sampleref_obj.timebase = avaudio.time_base.denominator

				valid = True
				fileformat = sampleref_obj.fileref.file.extension.lower()
				if fileformat == 'wav':
					if avaudio.codec.name not in ['pcm_f32le', 'pcm_s16le', 'pcm_s24le', 'pcm_u8']:
						fileformat = 'wav_codec'
				sampleref_obj.set_fileformat(fileformat)

		return valid