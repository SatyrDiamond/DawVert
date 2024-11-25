# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins

class input_codec(plugins.base):
	def is_dawvert_plugin(self):
		return 'audiocodec'
	
	def get_shortname(self):
		return 'brr'

	def get_name(self):
		return 'SNES BRR'
	
	def get_priority(self):
		return 0
	
	def supported_autodetect(self):
		return False

	def get_prop(self, in_dict): 
		in_dict['encode_supported'] = True
		in_dict['decode_supported'] = True

	def decode(self, in_bytes, audio_obj):
		from objects.extlib import c700_brr
		decode_object = c700_brr.brr()
		decode_object.decode(in_bytes, audio_obj)

	def encode(self, audio_obj):
		from objects.extlib import c700_brr
		decode_object = c700_brr.brr()
		outchar = decode_object.encode(audio_obj)
		return bytes(outchar)