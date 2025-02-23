# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import numpy
import os
import copy

class codec_obj:
	def __init__(self, codectype):
		self.is_pcm = True
		self.pcm_bits = 8
		self.pcm_uses_float = False
		self.pcm_signed = False

	def set_codec(self, codectype):
		self.is_pcm, self.pcm_uses_float, self.pcm_bits, self.pcm_signed = self.codectxt_from(codectype)

	def codectxt_from(self, codectype):
		is_pcm = (codectype in ['uint8','int8','uint16','int16','uint32','int32', 'float'])
		pcm_uses_float = (codectype == 'float')
		pcm_bits, pcm_signed = 8, False
		if is_pcm:
			if codectype == 'uint8': pcm_bits, pcm_signed = 8, False
			if codectype == 'int8': pcm_bits, pcm_signed = 8, True
			if codectype == 'uint16': pcm_bits, pcm_signed = 16, False
			if codectype == 'int16': pcm_bits, pcm_signed = 16, True
			if codectype == 'uint32': pcm_bits, pcm_signed = 32, False
			if codectype == 'int32': pcm_bits, pcm_signed = 32, True
			if codectype == 'float': pcm_bits, pcm_signed = 32, True
		return is_pcm, pcm_uses_float, pcm_bits, pcm_signed

	def codectxt_to(self):
		if self.is_pcm:
			if self.pcm_uses_float: return 'float'
			else: return ('u' if not self.pcm_signed else '')+'int'+str(self.pcm_bits)

	def get_dtype(self):
		if self.is_pcm:
			if self.pcm_uses_float: return numpy.float32
			elif self.pcm_bits == 8: return numpy.int8 if self.pcm_signed else numpy.uint8
			elif self.pcm_bits == 16: return numpy.int16 if self.pcm_signed else numpy.uint16
			elif self.pcm_bits == 32: return numpy.int32 if self.pcm_signed else numpy.uint32


VERBOSE = False

class audio_obj:

	audiocodec_selector = None

	def __init__(self):
		self.is_pcm = True
		self.data = numpy.zeros(0)

		self.loop = None

		self.channels = 1
		self.rate = 44100
		self.codec = codec_obj(None)

	def __len__(self):
		return len(self.data)

	def set_codec(self, codectype): 
		if VERBOSE: print("set_codec", codectype)
		self.codec.set_codec(codectype)
		self.pcm_from_list([])

# -------------------------------- data --------------------------------

	def pcm_from_stream(self, in_arr, in_size): 
		self.data = numpy.fromfile(in_arr, dtype=self.codec.get_dtype(), count=in_size*(self.codec.pcm_bits//8))
		self.pcm_from_postproc()

	def pcm_from_bytes(self, in_arr): 
		self.data = numpy.frombuffer(in_arr, dtype=self.codec.get_dtype())
		self.pcm_from_postproc()

	def pcm_from_list(self, in_arr): 
		self.data = numpy.asarray(in_arr, dtype=self.codec.get_dtype())
		self.pcm_from_postproc()

	def pcm_from_postproc(self): 
		self.data = self.data.flatten()
		removeend = len(self.data)%(self.channels)
		if removeend: self.data = self.data[0:-removeend]
		numpy.reshape(self.data, (-1, self.channels))

# -------------------------------- signed --------------------------------

	def pcm_to_signed(self):
		if VERBOSE: print("> pcm_to_signed")
		codec_obj = self.codec
		if not codec_obj.pcm_signed and codec_obj.is_pcm:
			codec_obj.pcm_signed = True
			if codec_obj.pcm_bits == 8: self.data = (self.data-128).astype('int8')
			if codec_obj.pcm_bits == 16: self.data = (self.data-32768).astype('int16')
			if codec_obj.pcm_bits == 32: self.data = (self.data-2147483648).astype('int32')

	def pcm_to_unsigned(self):
		if VERBOSE: print("> pcm_to_unsigned")
		codec_obj = self.codec
		if codec_obj.pcm_signed and codec_obj.is_pcm:
			codec_obj.pcm_signed = False
			if codec_obj.pcm_bits == 8: self.data = (self.data+128).astype('uint8')
			if codec_obj.pcm_bits == 16: self.data = (self.data+32768).astype('uint16')
			if codec_obj.pcm_bits == 32: self.data = (self.data+2147483648).astype('uint32')

# -------------------------------- bits --------------------------------

	def pcm_bits_up(self, n_bits):
		if VERBOSE: print("> pcm_bits_up")
		codec_obj = self.codec
		if not codec_obj.pcm_uses_float and codec_obj.is_pcm:
			if codec_obj.pcm_bits == 8:
				if n_bits == 16: self.data = self.data.astype('uint16' if not codec_obj.pcm_signed else 'int16')*(256)
				if n_bits == 32: self.data = self.data.astype('uint32' if not codec_obj.pcm_signed else 'int32')*((1<<24)+(1<<16)+(1<<8)+1)
			if codec_obj.pcm_bits == 16:
				if n_bits == 32: self.data = self.data.astype('uint32' if not codec_obj.pcm_signed else 'int32')*((256*256)+1)
			codec_obj.pcm_bits = n_bits

	def pcm_bits_down(self, n_bits):
		if VERBOSE: print("> pcm_bits_down")
		codec_obj = self.codec
		if not codec_obj.pcm_uses_float and codec_obj.is_pcm:
			if codec_obj.pcm_bits == 16:
				if n_bits == 8: self.data = (self.data//256).astype('uint8' if not codec_obj.pcm_signed else 'int8')
			if codec_obj.pcm_bits == 32:
				if n_bits == 16: self.data = (self.data>>16).astype('uint16' if not codec_obj.pcm_signed else 'int16')
				if n_bits == 8: self.data = (self.data>>24).astype('uint8' if not codec_obj.pcm_signed else 'int8')
			codec_obj.pcm_bits = n_bits

	def pcm_change_bits(self, n_bits):
		if VERBOSE: print("> pcm_change_bits")
		codec_obj = self.codec
		#print("pcm_change_bits", codec_obj.pcm_bits, n_bits)
		if codec_obj.pcm_bits < n_bits: self.pcm_bits_up(n_bits)
		if codec_obj.pcm_bits > n_bits: self.pcm_bits_down(n_bits)

# -------------------------------- codec --------------------------------

	def pcm_to_float(self):
		if VERBOSE: print("> pcm_to_float")
		codec_obj = self.codec
		if not codec_obj.pcm_uses_float and codec_obj.is_pcm:
			self.pcm_to_signed()
			codec_obj.pcm_uses_float = True
			if codec_obj.pcm_bits == 8: self.data = self.data.astype('float32')/127
			if codec_obj.pcm_bits == 16: self.data = self.data.astype('float32')/32768
			if codec_obj.pcm_bits == 32: self.data = self.data.astype('float32')/2147483648

	def pcm_from_float(self, n_bits):
		if VERBOSE: print("> pcm_to_float")
		codec_obj = self.codec
		if codec_obj.pcm_uses_float and codec_obj.is_pcm:
			codec_obj.pcm_signed = True
			codec_obj.pcm_bits = n_bits
			codec_obj.pcm_uses_float = False
			if n_bits == 8: self.data = (self.data*127).astype('int8')
			if n_bits == 16: self.data = (self.data*32768).astype('int16')
			if n_bits == 32: self.data = (self.data*2147483648).astype('int32')

	def pcm_changecodec(self, newcodec):
		if VERBOSE: print("pcm_changecodec", newcodec)
		codec_obj = self.codec
		o_pcm, o_float, o_bits, o_signed = codec_obj.is_pcm, codec_obj.pcm_uses_float, codec_obj.pcm_bits, codec_obj.pcm_signed
		is_pcm, pcm_uses_float, pcm_bits, pcm_signed = codec_obj.codectxt_from(newcodec)

		if o_pcm and is_pcm:
			if (not o_float) and (not pcm_uses_float):
				if [o_signed, pcm_signed] == [False, True]: self.pcm_to_signed()
				if [o_signed, pcm_signed] == [True, False]: self.pcm_to_unsigned()
				if o_bits != pcm_bits: self.pcm_change_bits(pcm_bits)
			if (not o_float) and pcm_uses_float:
				self.pcm_to_float()
			if o_float and (not pcm_uses_float):
				self.pcm_from_float(pcm_bits)
				if not pcm_signed: self.pcm_to_unsigned()

# -------------------------------- channels --------------------------------

	def pcm_chan_from_one(self, channels):
		if VERBOSE: print("pcm_chan_from_one", channels)
		oldd = self.data
		self.data = numpy.zeros((len(self), channels), dtype=self.data.dtype)
		for x in range(channels): self.data[:,x] = oldd

	def pcm_chan_to_one(self, channels):
		if VERBOSE: print("pcm_chan_to_one", channels)
		numchans = self.channels/channels
		oldcodec = self.codec.codectxt_to()
		self.pcm_to_float()
		olddata = self.data.copy()
		self.data = self.data[:,0]/numchans
		for x in range(channels): self.data += (olddata[:,x+1]/numchans)
		self.pcm_changecodec(oldcodec)

	def pcm_changechannels(self, channels):
		if VERBOSE: print("pcm_changechannels", channels)
		if channels < self.channels:
			if channels == 1:
				self.pcm_chan_to_one(channels)
			else:
				self.pcm_chan_to_one(channels)
				self.pcm_chan_from_one(channels)

		elif self.channels < channels:
			if self.channels == 1:
				self.pcm_chan_from_one(channels)
			else:
				self.pcm_chan_to_one(channels)
				self.pcm_chan_from_one(channels)

		self.channels = channels

# -------------------------------- resample --------------------------------

	def resample(self, samplerate):
		from scipy import signal
		if len(self.data):
			if samplerate != self.rate:
				self.pcm_changecodec('float')
				orgnumsamples = len(self.data)
				numsamples = int(orgnumsamples*(samplerate/self.rate))
				codec_obj = self.codec
				codectxt = codec_obj.codectxt_to()
				self.data = signal.resample_poly(self.data, numsamples, orgnumsamples)
				self.rate = samplerate
				self.pcm_changecodec(codectxt)

# -------------------------------- codec --------------------------------

	def load_plugins(self):
		if audio_obj.audiocodec_selector is None:
			from plugins import base as dv_plugins
			audio_obj.audiocodec_selector = dv_plugins.create_selector('audiocodec')

	def decode_from_codec(self, codecname, in_bytes):
		self.load_plugins()
		self.data = numpy.zeros(0)
		codecname = audio_obj.audiocodec_selector.set(codecname)
		if codecname:
			selected_plugin = audio_obj.audiocodec_selector.selected_plugin
			if selected_plugin.prop_obj.decode_supported: selected_plugin.plug_obj.decode(in_bytes, self)
			else: print('[plugins] codec: decoding unsupported:', codecname)
		else: print('[plugins] codec: not found', codecname)

	def encode_to_codec(self, codecname):
		self.load_plugins()
		if audio_obj.audiocodec_selector is None:
			from plugins import base as dv_plugins
			audio_obj.audiocodec_selector = dv_plugins.create_selector('audiocodec')
		codecname = audio_obj.audiocodec_selector.set(codecname)
		if codecname:
			selected_plugin = audio_obj.audiocodec_selector.selected_plugin
			if selected_plugin.prop_obj.encode_supported: return selected_plugin.plug_obj.encode(self)
			else: print('[plugins] codec: encoding unsupported:', codecname)
		else: print('[plugins] codec: not found', codecname)

# -------------------------------- codec --------------------------------

	def output_as(self, codec, channels, samplerate):
		c = copy.deepcopy(self)
		if codec: c.pcm_changecodec(codec)
		if channels: c.pcm_changechannels(channels)
		if samplerate: c.resample(samplerate)
		return c

	def change(self, codec, channels, samplerate):
		if codec: self.pcm_changecodec(codec)
		if channels: self.pcm_changechannels(channels)
		if samplerate: self.resample(samplerate)

# -------------------------------- raw --------------------------------

	def to_raw(self):
		return self.data.tobytes() if len(self.data) else b''

	def to_file_raw(self, file_path):
		fid = open(file_path, 'wb')
		fid.write(self.to_raw())

# -------------------------------- wav --------------------------------

	def from_file_wav(self, wavfile):
		from objects.file import audio_wav
		if os.path.exists(wavfile):
			wavfile_obj = audio_wav.wav_main()
			wavfile_obj.read(wavfile)

			self.channels = wavfile_obj.channels
			self.rate = wavfile_obj.rate

			if wavfile_obj.format != 3:
				if wavfile_obj.bits == 32: self.set_codec('int32')
				if wavfile_obj.bits == 24: self.set_codec('int32')
				if wavfile_obj.bits == 16: self.set_codec('int16')
				if wavfile_obj.bits == 8: self.set_codec('uint8')
			else:
				self.set_codec('float')

			self.pcm_from_list(wavfile_obj.data.copy())

	def to_file_wav(self, file_path):
		from objects.file import audio_wav
		wavfile_obj = audio_wav.wav_main()
		wavfile_obj.read_audioobj(self)
		if self.loop: wavfile_obj.add_loop(self.loop[0], self.loop[1])
		wavfile_obj.write(file_path)
