# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from ctypes import *
from objects import globalstore
from objects.extlib import helperfunc

class brr():
	def __init__(self):
		self.codec_lib = None

	def load_lib(self):
		libloadstat = globalstore.extlib.load_native('brr', "brr_codec")
		self.codec_lib = globalstore.extlib.get('brr')
		if libloadstat == 1: 
			brr_decode = self.codec_lib._Z9brrdecodePhPsii
			brr_decode.argtypes = [POINTER(c_ubyte), POINTER(c_short), c_int, c_int]
			brr_decode.restype = c_int

			brr_encode = self.codec_lib._Z9brrencodePsPhlbli
			brr_encode.argtypes = [POINTER(c_short), POINTER(c_ubyte), c_long, c_char, c_long, c_int]
			brr_encode.restype = c_int
			
	def decode(self, indata, audio_obj):
		self.load_lib()
		audio_obj.set_codec('int16')
		if self.codec_lib: 
			p_inp = helperfunc.castptr_ubyte_data(indata)
			p_outp = helperfunc.castptr_int16_blank(len(indata)*2)
			outlen = self.codec_lib._Z9brrdecodePhPsii(p_inp, p_outp, 0, 0)
			audio_obj.pcm_from_list(p_outp[0:outlen])

	def encode(self, audio_obj):
		self.load_lib()
		audio_obj.pcm_changecodec('int16')
		if self.codec_lib: 
			rawdata = audio_obj.to_raw()
			outlen = len(rawdata)//2
			p_inp = helperfunc.castptr_int16_data(rawdata)
			p_outp = helperfunc.castptr_ubyte_blank(len(rawdata)*2)
			self.codec_lib._Z9brrencodePsPhlbli(p_inp, p_outp, outlen, 0, 1, 0)

			return p_outp[0:(outlen//2)+(outlen//14)]