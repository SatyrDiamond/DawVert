# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import io
import os
import importlib.util

class input_soundfile(plugins.base):
	def is_dawvert_plugin(self): return 'audioconv'
	def get_shortname(self): return 'soundfile'
	def get_name(self): return 'SoundFile'
	def get_priority(self): return 0
	def supported_autodetect(self): return False
	def get_prop(self, in_dict): 
		in_dict['in_file_formats'] = ['wav', 'mp3', 'flac', 'ogg', 'wav_codec']
		in_dict['out_file_formats'] = ['wav', 'mp3', 'flac', 'ogg']
	def usable(self): 
		usable = importlib.util.find_spec('soundfile')
		usable_meg = '"soundfile" package is not installed.' if not usable else ''
		return usable, usable_meg
	def convert_file(self, sampleref_obj, to_type, outpath):
		import soundfile
		inpath = sampleref_obj.fileref.get_path(None, False)
		inputbuf = open(inpath, 'rb')
		data, samplerate = soundfile.read(inputbuf)
		sampleref_obj.fileref.set_folder(None, outpath, 0)
		outpath = sampleref_obj.fileref.copy()
		outpath.file.extension = 'wav'
		outpath = outpath.get_path(None, False)
		wav_buf = io.BytesIO()
		soundfile.write(outpath, data, samplerate)
		wav_buf.seek(0)
		sampleref_obj.fileref.file.extension = 'wav'
		return outpath