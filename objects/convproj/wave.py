# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import xtramath
from functions import data_bytes
from functions import data_values
from objects import audio_data
import struct
import math

def wave_sine(x): return math.sin((x-0.5)*(math.pi*2))
def wave_saw(x): return (x-math.floor(x)-0.5)*2
def wave_tri(x): return (abs((x*2)%(2)-1)-0.5)*2
def wave_squ(x, pw): return 1 if wave_sine(x) > pw else -1

class cvpj_wave:
	def __init__(self):
		self.range_min = -1
		self.range_max = 1
		self.points = [0]
		self.numpoints = 1
		self.smooth = True
		self.visname = ''
		self.author = ''
		self.data = {}

	def set_numpoints(self, numpoints):
		self.points = [0 for x in range(numpoints)]
		self.numpoints = numpoints

	def set_all(self, points):
		self.points = points
		self.numpoints = len(points)
		self.range_min = min(points)
		self.range_max = max(points)
		self.smooth = True if self.numpoints > 32 else False

	def set_all_range(self, points, range_min, range_max):
		self.points = points
		self.numpoints = len(points)
		self.range_min = range_min
		self.range_max = range_max
		self.smooth = True if self.numpoints > 32 else False

	def resize(self, new_size):
		self.points = resizewave(self.points, new_size, self.smooth)
		self.numpoints = len(self.points)

	def balance(self):
		for num in range(self.numpoints):
			self.points[num] = (xtramath.between_to_one(self.range_min, self.range_max, self.points[num])*2)-1
		self.range_min = -1
		self.range_max = 1

	def add_wave(self, shape, pw, mul, mixvol):
		halfpoint = self.numpoints//2
		for num in range(self.numpoints):
			outval = (num/self.numpoints)*mul
			outmod = xtramath.between_from_one(self.range_min, self.range_max, (calc_val(outval, shape, pw)/2)+0.5  )
			self.points[num] = (outmod*mixvol)+((1-mixvol)*self.points[num])

	def add_wave_func(self, i_func, i_var, mul, mixvol):
		halfpoint = self.numpoints//2
		for num in range(self.numpoints):
			outval = ((num/self.numpoints)*mul)%1
			outmod = xtramath.between_from_one(self.range_min, self.range_max, (i_func(outval, i_var)/2)+0.5  )
			self.points[num] = (outmod*mixvol)+((1-mixvol)*self.points[num])

	def to_audio(self, wave_path):
		audio_obj = audio_data.audio_obj()
		self.balance()
		audio_obj.set_codec('uint16')
		audio_obj.pcm_from_list([int(i*65535) for i in self.get_wave(2048)])
		audio_obj.to_file_wav(wave_path)

	def get_wave(self, i_size):
		tempdata = resizewave(self.points, i_size, self.smooth)
		tempdata = [xtramath.between_to_one(self.range_min, self.range_max, x) for x in tempdata]
		return tempdata

	def split(self, i_size):
		outwavesplit = []
		for w in data_values.list__chunks(self.points, i_size):
			if len(w)==i_size:
				split_wave_obj = cvpj_wave()
				split_wave_obj.range_min = self.range_min
				split_wave_obj.range_max = self.range_max
				split_wave_obj.points = w
				split_wave_obj.numpoints = i_size
				split_wave_obj.smooth = self.smooth
				split_wave_obj.visname = self.visname
				split_wave_obj.author = self.author
				split_wave_obj.data = self.data
				outwavesplit.append(split_wave_obj)
		return outwavesplit

def calc_val(inval, shape, pw):
	if shape == 'sine':				  return wave_sine(inval)
	if shape == 'saw':				   return wave_saw(inval)
	if shape == 'triangle':			  return wave_tri(inval)
	if shape == 'square':				return wave_squ(inval, pw)
	return 0

def resizewave(inputwave, new_size, smooth):
	dur_input = len(inputwave)
	wave_data = []

	inputwave = list(inputwave)

	if smooth == False:
		for num in range(new_size): 
			s_pos = num/new_size
			if inputwave:
				wave_data.append(inputwave[math.floor(s_pos*dur_input)])
	else:
		inputwave += inputwave
		if inputwave:
			for num in range(new_size): 
				s_pos = num/new_size
				wpn_float = s_pos*dur_input
				wpn_floor = int(math.floor(wpn_float))
				betweenpoints = wpn_float-wpn_floor
				out_val = xtramath.between_from_one(inputwave[wpn_floor], inputwave[wpn_floor+1], betweenpoints)
				wave_data.append(out_val)
		else:
			wave_data = (0 for _ in range(new_size))

	return wave_data
