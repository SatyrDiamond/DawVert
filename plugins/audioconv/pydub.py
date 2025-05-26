# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins

class input_soundfile(plugins.base):
	def is_dawvert_plugin(self):
		return 'audioconv'
	
	def get_shortname(self):
		return 'pydub'
	
	def get_name(self):
		return 'pydub'
	
	def get_prop(self, in_dict): 
		in_dict['in_file_formats'] = ['m4a']
		in_dict['out_file_formats'] = ['wav']

	def usable(self): 
		import importlib.util
		usable = importlib.util.find_spec('pydub')
		usable_meg = '"pydub" package is not installed.' if not usable else ''
		return usable, usable_meg
		
	def convert_file(self, sampleref_obj, to_type, outpath):
		from pydub import AudioSegment

		in_path = sampleref_obj.fileref.get_path(None, False)

		sound = AudioSegment.from_file(in_path)

		outfileref = sampleref_obj.fileref.copy()
		outfileref.set_folder(None, outpath, False)
		sampleref_obj.fileref.set_folder(None, outpath, 0)
		outpath = sampleref_obj.fileref.copy()
		outpath.file.extension = 'wav'
		outpath = outpath.get_path(None, False)

		file_handle = sound.export(outpath, format='wav')

		sampleref_obj.fileref.file.extension = 'wav'
		return outpath