# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_values
from functions import data_bytes
from functions import xtramath
from objects.convproj import wave
from objects import audio_data

import struct
import math

class cvpj_harmonics:
	def __init__(self):
		self.waves = {}

	def add(self, num, vol, data):
		self.waves[num] = [vol, data]

	def to_audio(self, wave_path):
		audio_obj = audio_data.audio_obj()
		audio_obj.set_codec('uint16')
		audio_obj.pcm_from_list([int(i*65535) for i in do_wave(self.waves)])
		audio_obj.to_file_wav(wave_path)

	def to_wave(self):
		wave_obj = wave.cvpj_wave()
		wave_obj.set_all_range(do_wave(self.waves), 0, 1)
		return wave_obj

def do_wave(harm_in):
	tempdata = [0 for x in range(2048)]
	for num, data in harm_in.items():
		vol = data[0]
		phase = data[1]['phase'] if 'phase' in data[1] else 0.5
		for x in range(2048):
			sinv = (x/2048)
			tempdata[x] = tempdata[x]*(1-(data[0]/2))
			tempdata[x] += (math.sin(((sinv+phase)*(math.pi*2))*num)*(data[0])/2)
	tempdata = [xtramath.between_to_one(-1, 1, x) for x in tempdata]
	return tempdata