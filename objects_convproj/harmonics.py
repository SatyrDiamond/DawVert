# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_values
from functions import data_bytes
from functions import xtramath
from functions import audio_wav
from objects_convproj import wave

import struct
import math

class cvpj_harmonics:
	def __init__(self):
		self.waves = {}

	def add(self, num, vol, data):
		self.waves[num] = [vol, data]

	def to_audio(self, fileloc):
		audiowavdata = [int(i*65535) for i in do_wave(self.waves)]
		wave_data = data_bytes.unsign_16(struct.pack('H'*len(audiowavdata), *audiowavdata))
		audio_wav.generate(fileloc, wave_data, 1, 44100, 16, None)

	def to_wave(self):
		wave_obj = wave.cvpj_wave()
		wave_obj.set_all_range(do_wave(self.waves), 0, 1)
		return wave_obj

def do_wave(harm_in):
	tempdata = [0 for x in range(2048)]
	for num, data in harm_in.items():
		vol = data[0]
		phase = data[1]['phase'] if 'phase' in data[1] else 0
		for x in range(2048):
			sinv = (x/2048)
			tempdata[x] = tempdata[x]*(1-(data[0]/2))
			tempdata[x] += (math.sin(((sinv+phase)*(math.pi*2))*num)*(data[0])/2)
	tempdata = [xtramath.between_to_one(-1, 1, x) for x in tempdata]
	return tempdata