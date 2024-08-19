# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import io

class input_soundfile(plugins.base):
	try:
		import soundfile
		usable = True
	except:
		usable = False

	def is_dawvert_plugin(self): return 'audioconv'
	def getshortname(self): return 'soundfile'
	def getaudioconvinfo(self, audioconvinfo_obj):
		audioconvinfo_obj.in_file_formats = ['wav', 'mp3', 'flac', 'ogg']
		audioconvinfo_obj.out_file_formats = ['wav', 'mp3', 'flac', 'ogg']
	def convert_file(self, sampleref_obj, to_type, outpath):
		if self.usable:
			inpath = sampleref_obj.fileref.get_path(None, False)
			inputbuf = open(inpath, 'rb')
			data, samplerate = self.soundfile.read(inputbuf)
			wav_buf = io.BytesIO()
			self.soundfile.write(wav_buf, data, samplerate)
			wav_buf.seek(0)
		return False