# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins

class input_codec(plugins.base):
	def is_dawvert_plugin(self):
		return 'audiocodec'
	
	def get_shortname(self):
		return 'oki6258'
	
	def get_name(self):
		return 'OKI6258'
	
	def get_prop(self, in_dict): 
		in_dict['encode_supported'] = True
		in_dict['decode_supported'] = True

	def decode(self, in_bytes, audio_obj):
		from objects.extlib import superctr_adpcm
		decode_object = superctr_adpcm.oki()
		decode_object.decode_oki6258(in_bytes, audio_obj)

	def encode(self, audio_obj):
		from objects.extlib import superctr_adpcm
		encode_object = superctr_adpcm.oki()
		outchar = encode_object.encode_oki6258(audio_obj)
		return bytes(outchar)