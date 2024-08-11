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

	def is_dawvert_plugin(self): return 'audiofile'
	def getshortname(self): return 'ogg_in_wav'
	def getaudiofileinfo(self, audiofileinfo_obj):
		audiofileinfo_obj.file_formats = ['wav']
	def getinfo(self, input_file, sampleref_obj, fileextlow):
		if fileextlow == 'wav' and self.usable:
			riff_data = riff_chunks.riff_chunk()
			byr_stream = riff_data.load_from_file(input_file, False)

			data_pos = 0
			data_size = 0

			fmt_format = 0
			fmt_channels = 0
			fmt_rate = 0
			fmt_bytessec = 0
			fmt_datablocksize = 0
			fmt_bits = 0

			for riff_part in riff_data.in_data:
				if riff_part.name == b'fmt ': 
					with byr_stream.isolate_range(riff_part.start, riff_part.end, False) as bye_stream: 
						fmt_format = bye_stream.uint16()
						fmt_channels = bye_stream.uint16()
						fmt_rate = bye_stream.uint32()
						fmt_bytessec = bye_stream.uint32()
						fmt_datablocksize = bye_stream.uint16()
						fmt_bits = bye_stream.uint16()
				elif riff_part.name == b'data': 
					data_pos = riff_part.start
					data_end = riff_part.end

			if fmt_format == 26447:
				with byr_stream.isolate_range(data_pos, data_end, False) as bye_stream:
					audiodata = bye_stream.raw(data_end-data_pos)

				samples, samplerate = self.soundfile.read(io.BytesIO(audiodata))
				frames = len(samples)
				sampleref_obj.hz = samplerate
				sampleref_obj.timebase = samplerate
				sampleref_obj.dur_samples = frames
				sampleref_obj.dur_sec = frames/samplerate
				sampleref_obj.channels = 2
				sampleref_obj.fileformat = 'wav_ogg'
				return True
			return False
		return False