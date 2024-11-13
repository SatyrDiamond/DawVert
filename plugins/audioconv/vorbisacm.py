# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import io
import importlib.util

class input_soundfile(plugins.base):
	def is_dawvert_plugin(self): return 'audioconv'
	def get_shortname(self): return 'vorbisacm'
	def get_name(self): return 'VorbisACM'
	def get_priority(self): return -100
	def supported_autodetect(self): return False
	def get_prop(self, in_dict): 
		in_dict['in_file_formats'] = ['wav_ogg']
		in_dict['out_file_formats'] = ['wav', 'mp3', 'flac', 'ogg']
	def usable(self): 
		usable = importlib.util.find_spec('soundfile')
		usable_meg = '"soundfile" package is not installed.' if not usable else ''
		return usable, usable_meg
	def convert_file(self, sampleref_obj, to_type, outpath):
		import soundfile
		from objects.data_bytes import riff_chunks
		if sampleref_obj.fileref.file.extension == 'wav':
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
				samples, samplerate = soundfile.read(io.BytesIO(audiodata))
				sampleref_obj.fileref.set_folder(None, outpath, 0)
				sampleref_obj.fileformat = to_type
				sampleref_obj.fileref.file.extension = to_type
				output_file = sampleref_obj.fileref.get_path(None, False)
				f = open(output_file, 'wb')
				soundfile.write(f, samples, samplerate)
				return True
			return False
		return False