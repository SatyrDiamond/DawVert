# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from ctypes import *
from objects import globalstore
from objects.extlib import helperfunc

def decfunc16byte(dllfunc, indata):
	p_inp = helperfunc.castptr_ubyte_data(indata)
	p_outp = helperfunc.castptr_int16_blank(len(indata))
	dllfunc(p_inp, p_outp, len(indata)*2)
	return p_outp[0:len(indata)*2]

def encfunc16byte(dllfunc, indata):
	p_inp = helperfunc.castptr_int16_data(indata)
	p_outp = helperfunc.castptr_ubyte_blank(len(indata))
	dllfunc(p_inp, p_outp, len(indata)//2)
	return p_outp[0:len(indata)//4]

class qsound():
	def __init__(self):
		self.codec_lib = None

	def load_lib(self):
		libloadstat = globalstore.extlib.load_native('adpcm_qsound', "bs_codec")
		self.codec_lib = globalstore.extlib.get('adpcm_qsound')
		if libloadstat == 1: 
			self.codec_lib.bs_decode.argtypes = [POINTER(c_ubyte), POINTER(c_int16), c_long]
			self.codec_lib.bs_encode.argtypes = [POINTER(c_int16), POINTER(c_ubyte), c_long]

	def decode(self, indata, audio_obj):
		self.load_lib()
		audio_obj.set_codec('int16')
		if self.codec_lib: audio_obj.pcm_from_list(decfunc16byte(self.codec_lib.bs_decode, indata))

	def encode(self, audio_obj):
		self.load_lib()
		audio_obj.pcm_changecodec('int16')
		if self.codec_lib: return encfunc16byte(self.codec_lib.bs_encode, audio_obj.to_raw())

class oki():
	def __init__(self):
		self.codec_lib = None

	def load_lib(self):
		libloadstat = globalstore.extlib.load_native('adpcm_oki', "oki_codec")
		self.codec_lib = globalstore.extlib.get('adpcm_oki')
		if libloadstat == 1: 
			self.codec_lib.oki6258_decode.argtypes = [POINTER(c_ubyte), POINTER(c_int16), c_long]
			self.codec_lib.oki_decode.argtypes = [POINTER(c_ubyte), POINTER(c_int16), c_long]
			self.codec_lib.oki6258_encode.argtypes = [POINTER(c_int16), POINTER(c_ubyte), c_long]
			self.codec_lib.oki_encode.argtypes = [POINTER(c_int16), POINTER(c_ubyte), c_long]

	def decode_oki6258(self, indata, audio_obj):
		self.load_lib()
		audio_obj.set_codec('int16')
		if self.codec_lib: audio_obj.pcm_from_list(decfunc16byte(self.codec_lib.oki6258_decode, indata))

	def decode(self, indata, audio_obj):
		self.load_lib()
		audio_obj.set_codec('int16')
		if self.codec_lib: audio_obj.pcm_from_list(decfunc16byte(self.codec_lib.oki_decode, indata))

	def encode_oki6258(self, audio_obj):
		self.load_lib()
		audio_obj.pcm_changecodec('int16')
		if self.codec_lib: return encfunc16byte(self.codec_lib.oki6258_encode, audio_obj.to_raw())

	def encode(self, audio_obj):
		self.load_lib()
		audio_obj.pcm_changecodec('int16')
		if self.codec_lib: return encfunc16byte(self.codec_lib.oki_encode, audio_obj.to_raw())

class yamaha_a():
	def __init__(self):
		self.codec_lib = None

	def load_lib(self):
		libloadstat = globalstore.extlib.load_native('adpcm_yamaha_a', "yma_codec")
		self.codec_lib = globalstore.extlib.get('adpcm_yamaha_a')
		if libloadstat == 1: 
			self.codec_lib.yma_decode.argtypes = [POINTER(c_ubyte), POINTER(c_int16), c_long]
			self.codec_lib.yma_encode.argtypes = [POINTER(c_int16), POINTER(c_ubyte), c_long]

	def decode(self, indata, audio_obj):
		self.load_lib()
		audio_obj.set_codec('int16')
		if self.codec_lib: audio_obj.pcm_from_list(decfunc16byte(self.codec_lib.yma_decode, indata))

	def encode(self, audio_obj):
		self.load_lib()
		audio_obj.pcm_changecodec('int16')
		if self.codec_lib: return encfunc16byte(self.codec_lib.yma_encode, audio_obj.to_raw())

class yamaha_b():
	def __init__(self):
		self.codec_lib = None

	def load_lib(self):
		libloadstat = globalstore.extlib.load_native('adpcm_yamaha_b', "ymb_codec")
		self.codec_lib = globalstore.extlib.get('adpcm_yamaha_b')
		if libloadstat == 1: 
			self.codec_lib.ymb_decode.argtypes = [POINTER(c_ubyte), POINTER(c_int16), c_long]
			self.codec_lib.ymb_encode.argtypes = [POINTER(c_int16), POINTER(c_ubyte), c_long]

	def decode(self, indata, audio_obj):
		self.load_lib()
		audio_obj.set_codec('int16')
		if self.codec_lib: audio_obj.pcm_from_list(decfunc16byte(self.codec_lib.ymb_decode, indata))

	def encode(self, audio_obj):
		self.load_lib()
		audio_obj.pcm_changecodec('int16')
		if self.codec_lib: return encfunc16byte(self.codec_lib.ymb_encode, audio_obj.to_raw())

class yamaha_z():
	def __init__(self):
		self.codec_lib = None

	def load_lib(self):
		libloadstat = globalstore.extlib.load_native('adpcm_yamaha_z', "ymz_codec")
		self.codec_lib = globalstore.extlib.get('adpcm_yamaha_z')
		if libloadstat == 1:
			self.codec_lib.aica_decode.argtypes = [POINTER(c_ubyte), POINTER(c_int16), c_long]
			self.codec_lib.aica_encode.argtypes = [POINTER(c_int16), POINTER(c_ubyte), c_long]
			self.codec_lib.ymz_decode.argtypes = [POINTER(c_ubyte), POINTER(c_int16), c_long]
			self.codec_lib.ymz_encode.argtypes = [POINTER(c_int16), POINTER(c_ubyte), c_long]

	def decode_aica(self, indata, audio_obj):
		self.load_lib()
		audio_obj.set_codec('int16')
		if self.codec_lib: audio_obj.pcm_from_list(decfunc16byte(self.codec_lib.aica_decode, indata))

	def decode(self, indata, audio_obj):
		self.load_lib()
		audio_obj.set_codec('int16')
		if self.codec_lib: audio_obj.pcm_from_list(decfunc16byte(self.codec_lib.ymz_decode, indata))

	def encode_aica(self, audio_obj):
		self.load_lib()
		audio_obj.pcm_changecodec('int16')
		if self.codec_lib: return encfunc16byte(self.codec_lib.aica_encode, audio_obj.to_raw())

	def encode(self, audio_obj):
		self.load_lib()
		audio_obj.pcm_changecodec('int16')
		if self.codec_lib: return encfunc16byte(self.codec_lib.ymz_encode, audio_obj.to_raw())
