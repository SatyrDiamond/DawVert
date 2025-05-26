# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins

class input_soundfile(plugins.base):
	def is_dawvert_plugin(self):
		return 'audiofile'
	
	def get_shortname(self):
		return 'soundfile'
	
	def get_name(self):
		return 'SoundFile'
	
	def get_priority(self):
		return 0
	
	def usable(self): 
		import importlib.util
		usable = importlib.util.find_spec('soundfile')
		usable_meg = '"soundfile" package is not installed.' if not usable else ''
		return usable, usable_meg

	def get_prop(self, in_dict):
		in_dict['file_formats'] = ['wav', 'mp3', 'flac', 'ogg']
		
	def getinfo(self, input_file, sampleref_obj, fileextlow):
		from soundfile import SoundFile
		sf_audio = SoundFile(input_file)

		sampleref_obj.set_hz(sf_audio.samplerate)
		sampleref_obj.set_channels(sf_audio.channels)

		if fileextlow == 'mp3': 
			sampleref_obj.set_dur_samples(sf_audio.frames*320)
			sampleref_obj.timebase *= 320
		else:
			sampleref_obj.set_dur_samples(sf_audio.frames)

		sampleref_obj.set_fileformat(sampleref_obj.fileref.file.extension.lower())
		return True