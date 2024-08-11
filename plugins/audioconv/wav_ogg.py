# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import io
from objects.data_bytes import riff_chunks

class input_soundfile(plugins.base):
	try:
		import soundfile
		usable = True
	except:
		usable = False

	def is_dawvert_plugin(self): return 'audioconv'
	def getshortname(self): return 'wav_ogg'
	def getaudioconvinfo(self, audioconvinfo_obj):
		audioconvinfo_obj.in_file_formats = ['wav_ogg']
		audioconvinfo_obj.out_file_formats = ['wav', 'mp3', 'flac', 'ogg']
	def convert_file(self, sampleref_obj, to_type, outpath):
		if sampleref_obj.fileref.extension == 'wav' and self.usable:
			input_file = sampleref_obj.fileref.get_path(None, False)
			riff_data = riff_chunks.riff_chunk()
			byr_stream = riff_data.load_from_file(input_file, False)

			data_pos = 0
			data_end = 0
			fmt_format = 0

			for riff_part in riff_data.in_data:
				if riff_part.name == b'fmt ': 
					with byr_stream.isolate_range(riff_part.start, riff_part.end, False) as bye_stream: fmt_format = bye_stream.uint16()
				elif riff_part.name == b'data': 
					data_pos = riff_part.start
					data_end = riff_part.end

			if fmt_format == 26447:
				with byr_stream.isolate_range(data_pos, data_end, False) as bye_stream: audiodata = bye_stream.raw(data_end-data_pos)
				samples, samplerate = self.soundfile.read(io.BytesIO(audiodata))
				sampleref_obj.fileref.changefolder(outpath)
				sampleref_obj.fileformat = to_type
				sampleref_obj.fileref.extension = to_type
				output_file = sampleref_obj.fileref.get_path(None, False)
				f = open(output_file, 'wb')
				self.soundfile.write(f, samples, samplerate)
				return True
			return False
		return False