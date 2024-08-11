# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins

class input_codec(plugins.base):
	def is_dawvert_plugin(self): return 'audiocodec'
	def getshortname(self): return 'yamaha_a'
	def getaudiocodecinfo(self, audiocodecinfo_obj):
		audiocodecinfo_obj.name = "Yamaha ADPCM-A"
		audiocodecinfo_obj.encode_supported = True
		audiocodecinfo_obj.decode_supported = True

	def decode(self, in_bytes, audio_obj):
		from objects.extlib import superctr_adpcm
		decode_object = superctr_adpcm.yamaha_a()
		decode_object.decode(in_bytes, audio_obj)

	def encode(self, audio_obj):
		from objects.extlib import superctr_adpcm
		encode_object = superctr_adpcm.yamaha_a()
		outchar = encode_object.encode(audio_obj)
		return bytes(outchar)