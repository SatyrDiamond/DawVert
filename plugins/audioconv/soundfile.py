# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import io
import os

class input_soundfile(plugins.base):
	try:
		import soundfile
		usable = True
	except:
		usable = False

	def is_dawvert_plugin(self): return 'audioconv'
	def getshortname(self): return 'soundfile'
	def getaudioconvinfo(self, audioconvinfo_obj):
		audioconvinfo_obj.in_file_formats = ['wav', 'mp3', 'flac', 'ogg', 'wav_codec']
		audioconvinfo_obj.out_file_formats = ['wav', 'mp3', 'flac', 'ogg']
	def convert_file(self, sampleref_obj, to_type, outpath):
		if self.usable:
			inpath = sampleref_obj.fileref.get_path(None, False)
			inputbuf = open(inpath, 'rb')
			data, samplerate = self.soundfile.read(inputbuf)
			sampleref_obj.fileref.set_folder(None, outpath, 0)
			outpath = sampleref_obj.fileref.get_path(None, False)
			wav_buf = io.BytesIO()
			self.soundfile.write(outpath, data, samplerate)
			wav_buf.seek(0)
		return False