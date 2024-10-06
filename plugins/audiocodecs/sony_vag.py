# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import numpy as np
import io

class input_codec(plugins.base):
	def is_dawvert_plugin(self): return 'audiocodec'
	def get_shortname(self): return 'sony_vag'

	def get_name(self): return 'Sony VAG'
	def get_priority(self): return 0
	def get_prop(self, in_dict): 
		in_dict['decode_supported'] = True

	def decode(self, in_bytes, audio_obj):
		import av
		vag_audio = io.BytesIO(in_bytes)

		container = av.open(vag_audio, format='vag')

		data = np.empty(shape=0)
		for packet in container.demux():
			for frame in packet.decode():
				if isinstance(frame, av.audio.frame.AudioFrame):
					array = frame.to_ndarray()[0]
					data = np.concatenate([data, array])

		audio_obj.set_codec('int16')
		audio_obj.pcm_from_list(data)
