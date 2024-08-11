# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import numpy as np
from functions import xtramath

class input_codec(plugins.base):
	def is_dawvert_plugin(self): return 'audiocodec'
	def getshortname(self): return 'dpcm'
	def getaudiocodecinfo(self, audiocodecinfo_obj):
		audiocodecinfo_obj.name = "DPCM"
		audiocodecinfo_obj.decode_supported = True

	def decode(self, in_bytes, audio_obj):
		dpcm_samp = np.zeros(len(in_bytes)*8, dtype=np.float32)
		dpcm_current = 0

		bytenum = 0
		for dpcm_byte in in_bytes:
			for bitnum in range(8):
				dpcm_current += 2 if ((dpcm_byte >> bitnum) & 1) else -2
				dpcm_current = xtramath.clamp(dpcm_current,-128,127) 
				dpcm_samp[bytenum] = dpcm_current
				bytenum += 1

		if len(dpcm_samp): dpcm_samp[1:] = dpcm_samp[:-1]/2 + dpcm_samp[1:]/2

		audio_obj.set_codec('float')
		audio_obj.pcm_from_list(dpcm_samp/128)
		audio_obj.pcm_changecodec('uint8')
