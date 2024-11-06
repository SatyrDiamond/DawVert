# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import numpy as np
from io import BytesIO

class input_codec(plugins.base):
	def is_dawvert_plugin(self): return 'audiocodec'
	def get_shortname(self): return 'sony_vag'

	def get_name(self): return 'Sony VAG'
	def get_priority(self): return 0
	def get_prop(self, in_dict): 
		in_dict['decode_supported'] = True

	def decode(self, in_bytes, audio_obj):
		import av
		vag_audio = BytesIO(in_bytes)

		try:
			container = av.open(vag_audio, format='vag')
			data = np.empty(shape=0)
			for packet in container.demux():
				for frame in packet.decode():
					if isinstance(frame, av.audio.frame.AudioFrame):
						array = frame.to_ndarray()[0]
						data = np.concatenate([data, array])
			audio_obj.set_codec('int16')
			audio_obj.pcm_from_list(data)
		except:
			pass

		#vag_flag = np.frombuffer(in_bytes, dtype=np.uint8)[1::16]

		#loop_start = np.nonzero(vag_flag==6)
		#loop_end = np.nonzero(vag_flag==3)

		#if loop_start[0].size or loop_end[0].size: 
#
		#	if not audio_obj.loop: audio_obj.loop = [0, len(data)]
		#	if loop_start[0].size: audio_obj.loop[0] = (loop_start[0][0])*28
		#	if loop_end[0].size: audio_obj.loop[1] = (loop_end[0][0])*28

		#print(audio_obj.loop, len(data))
