# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins

class input_codec(plugins.base):
	def is_dawvert_plugin(self): return 'audiocodec'
	def getshortname(self): return 'oki6258'
	def getaudiocodecinfo(self, audiocodecinfo_obj):
		audiocodecinfo_obj.name = "OKI6258"
		audiocodecinfo_obj.encode_supported = True
		audiocodecinfo_obj.decode_supported = True

	def decode(self, in_bytes, audio_obj):
		from objects.extlib import superctr_adpcm
		decode_object = superctr_adpcm.oki()
		decode_object.decode_oki6258(in_bytes, audio_obj)

	def encode(self, audio_obj):
		from objects.extlib import superctr_adpcm
		encode_object = superctr_adpcm.oki()
		outchar = encode_object.encode_oki6258(audio_obj)
		return bytes(outchar)