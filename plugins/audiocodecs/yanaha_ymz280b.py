# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins

class input_codec(plugins.base):
	def is_dawvert_plugin(self): return 'audiocodec'
	def getshortname(self): return 'yamaha_ymz280b'
	def getaudiocodecinfo(self, audiocodecinfo_obj):
		audiocodecinfo_obj.name = "Yamaha YMZ280B"
		audiocodecinfo_obj.encode_supported = True
		audiocodecinfo_obj.decode_supported = True

	def decode(self, in_bytes, audio_obj):
		from objects.extlib import superctr_adpcm
		decode_object = superctr_adpcm.yamaha_z()
		decode_object.decode(in_bytes, audio_obj)

	def encode(self, audio_obj):
		from objects.extlib import superctr_adpcm
		encode_object = superctr_adpcm.yamaha_z()
		outchar = encode_object.encode(audio_obj)
		return bytes(outchar)