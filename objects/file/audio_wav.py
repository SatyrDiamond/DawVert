# https://gist.github.com/josephernest/3f22c5ed5dabf1815f16efa8fa53d476

import numpy
import struct
import collections
import sys
import pathlib
import os
import copy
import logging
from objects.data_bytes import riff_chunks

logger_audiofile = logging.getLogger('audiofile')

class wav_loop:
	def __init__(self, bye_stream):
		self.identifier = 0
		self.type = 0
		self.start = 0
		self.end = 0
		self.fraction = 0
		self.playcount = 0
		if bye_stream != None:
			self.identifier = bye_stream.int32()
			self.type = bye_stream.int32()
			self.start = bye_stream.int32()
			self.end = bye_stream.int32()
			self.fraction = bye_stream.int32()
			self.playcount = bye_stream.int32()

	def write(self):
		return struct.pack('<iiiiii', self.identifier, self.type, self.start, self.end, self.fraction, self.playcount)

class wav_slice:
	def __init__(self):
		self.header = 0
		self.id1 = 0
		self.samplePositionUpper = 0
		self.samplePositionLower = 0
		self.samplePosition2Upper = 0
		self.samplePosition2Lower = 0
		self.data3 = 0
		self.id2 = 0

	def read(self, bye_stream):
		self.id1 = bye_stream.uint32()
		self.samplePositionUpper = bye_stream.uint32()
		self.samplePositionLower = bye_stream.uint32()
		self.samplePosition2Upper = bye_stream.uint32()
		self.samplePosition2Lower = bye_stream.uint32()
		self.id2 = bye_stream.uint32()

		print(self.header, self.id1, self.samplePositionUpper, self.samplePositionLower, self.samplePosition2Upper, self.samplePosition2Lower, self.data3, self.id2)

class wav_marker:
	def __init__(self):
		self.id = 0
		self.position = 0
		self.datachunkid = 0
		self.chunkstart = 0
		self.blockstart = 0
		self.sampleoffset = 0
		self.label = None

	def read(self, bye_stream):
		self.id = bye_stream.uint32()
		self.position = bye_stream.uint32()
		self.datachunkid = bye_stream.raw(4)
		self.chunkstart = bye_stream.uint32()
		self.blockstart = bye_stream.uint32()
		self.sampleoffset = bye_stream.uint32()

	def write(self):
		return struct.pack('<iiiiii', self.id, self.position, self.datachunkid, self.chunkstart, self.blockstart, self.sampleoffset)

class wav_smpl:
	def __init__(self):
		self.manu = 0
		self.product = 0
		self.sampleperiod = 20833
		self.note_middle = 60
		self.midi_pitchfrac = 0
		self.smpte_format = 0
		self.smpte_offset = 0
		self.sampler_specific = b''
		self.loops = []

	def read(self, bye_stream, size):
		self.manu = bye_stream.int32()
		self.product = bye_stream.int32()
		self.sampleperiod = bye_stream.int32()
		self.note_middle = bye_stream.int32()
		self.midi_pitchfrac = bye_stream.uint32()
		self.smpte_format = bye_stream.int32()
		self.smpte_offset = bye_stream.int32()
		numloops = bye_stream.int32()
		sampspecsize = bye_stream.int32()
		for _ in range(numloops): self.loops.append(wav_loop(bye_stream))
		self.sampler_specific = bye_stream.raw(sampspecsize)

	def write(self):
		outdata = struct.pack('<iiiiIiiii', self.manu, self.product, self.sampleperiod, self.note_middle, self.midi_pitchfrac, self.smpte_format, self.smpte_offset, len(self.loops), len(self.sampler_specific))
		for l in self.loops: outdata += l.write()
		outdata += self.sampler_specific
		return outdata

class wav_inst:
	def __init__(self):
		self.rootnote = 60
		self.finetune = 0
		self.gain = 0
		self.note_low = 0
		self.note_high = 127
		self.vel_low = 0
		self.vel_high = 127
		self.found = False

	def read(self, bye_stream, size):
		self.found = True
		self.rootnote = bye_stream.uint8()
		self.finetune = bye_stream.uint8()
		self.gain = bye_stream.int8()
		self.note_low = bye_stream.uint8()
		self.note_high = bye_stream.uint8()
		self.vel_low = bye_stream.uint8()
		self.vel_high = bye_stream.uint8()

	def write(self):
		return struct.pack('<BBBBBBB', self.rootnote, self.finetune, self.gain, self.note_low, self.note_high, self.vel_low, self.vel_high)

class wav_main:
	def __init__(self):
		self.format = 1
		self.channels = 1
		self.rate = 44100
		self.bytessec = 44100
		self.bits = 8
		self.datablocksize = int((self.bits/8)*self.channels)
		self.rawdata = b''
		self.data = numpy.float32([])
		self.smpl = wav_smpl()
		self.inst = wav_inst()
		self.uses_float = False
		self.markers = {}
		self.slices = {}
		self.other_chunks = {}

	def set_blksize(self):
		self.datablocksize = int((self.bits/8)*self.channels)

	def add_loop(self, start, end):
		loop_obj = wav_loop(None)
		loop_obj.start = start
		loop_obj.end = end
		self.smpl.loops.append(loop_obj)

	def set_freq(self, freq):
		self.rate = freq
		self.bytessec = freq
		self.set_blksize()

	def _read_chunk_fmt(self, fid):
		size, self.format, self.channels, self.rate, self.bytessec, self.datablocksize, self.bits = struct.unpack('<ihHIIHH',fid.read(20))
		if (self.format != 1 or size > 16):
			if (self.format == 3): self.uses_float = True
			if (size>16): fid.read(size-16)

	def read_chunk_data(self, bye_stream, size, normalized=False):
		if self.bits in [8, 24]:
			bytes = 1
			dtype = 'u1'
		else:
			bytes = self.bits//8
			dtype = '<i%d' % bytes
			
		if self.bits == 32 and self.uses_float: dtype = 'float32'
			
		self.data = numpy.frombuffer(bye_stream.raw(size), dtype=dtype, count=size//bytes)
		
		if self.bits == 24:
			a = numpy.empty((len(self.data) // 3, 4), dtype='u1')
			a[:, :3] = self.data.reshape((-1, 3))
			a[:, 3:] = (a[:, 3 - 1:3] >> 7) * 255
			self.data = a.view('<i4').reshape(a.shape[:-1])
		
		if self.channels > 1: self.data = self.data.reshape(-1,self.channels)
		if bool(size & 1): fid.seek(1,1)	
		if normalized:
			if self.bits == 8 or self.bits == 16 or self.bits == 24: normfactor = 2 ** (self.bits-1)
			self.data = numpy.float32(self.data) * 1.0 / normfactor

	def read_audioobj(self, audio_obj):
		audio_obj = copy.deepcopy(audio_obj)
		if audio_obj.is_pcm:
			self.channels = audio_obj.channels
			self.rate = int(audio_obj.rate)
			self.bits = audio_obj.codec.pcm_bits
			if not audio_obj.codec.pcm_uses_float:
				if self.bits == 8: 
					audio_obj.pcm_to_unsigned()
					self.data = numpy.asarray(audio_obj.data, dtype=numpy.int8)
				if self.bits == 16: 
					audio_obj.pcm_to_signed()
					self.data = numpy.asarray(audio_obj.data, dtype=numpy.int16)
				if self.bits == 32: 
					audio_obj.pcm_to_signed()
					self.data = numpy.asarray(audio_obj.data, dtype=numpy.int32)
		self.set_blksize()

	def read_bytes(self, rawdata):
		riff_data = riff_chunks.riff_chunk()
		byr_stream = riff_data.load_from_bytes(rawdata, False)
		self.read_internal(byr_stream, riff_data, True)

	def read(self, wavfile):
		riff_data = riff_chunks.riff_chunk()
		byr_stream = riff_data.load_from_file(wavfile, False)
		self.read_internal(byr_stream, riff_data, True)

	def readinfo_bytes(self, rawdata):
		riff_data = riff_chunks.riff_chunk()
		byr_stream = riff_data.load_from_bytes(rawdata, False)
		self.read_internal(byr_stream, riff_data, False)

	def readinfo(self, wavfile):
		riff_data = riff_chunks.riff_chunk()
		byr_stream = riff_data.load_from_file(wavfile, False)
		self.read_internal(byr_stream, riff_data, False)

	def read_internal(self, byr_stream, riff_data, parsedata):
		for riff_part in riff_data.in_data:

			if riff_part.name == b'fmt ': 
				with byr_stream.isolate_range(riff_part.start, riff_part.end, False) as bye_stream: 
					self.format = bye_stream.uint16()
					self.channels = bye_stream.uint16()
					self.rate = bye_stream.uint32()
					self.bytessec = bye_stream.uint32()
					self.datablocksize = bye_stream.uint16()
					self.bits = bye_stream.uint16()
					if (self.format == 3): self.uses_float = True

			elif riff_part.name == b'data': 
				if parsedata:
					with byr_stream.isolate_range(riff_part.start, riff_part.end, False) as bye_stream: 
						self.read_chunk_data(bye_stream, riff_part.size)

			elif riff_part.name == b'smpl':
				with byr_stream.isolate_range(riff_part.start, riff_part.end, False) as bye_stream: 
					self.smpl.read(bye_stream, riff_part.size)

			elif riff_part.name == b'inst':
				with byr_stream.isolate_range(riff_part.start, riff_part.end, False) as bye_stream: 
					self.inst.read(bye_stream, riff_part.size)

			elif riff_part.name == b'cue ':
				with byr_stream.isolate_range(riff_part.start, riff_part.end, False) as bye_stream: 
					numcue = bye_stream.int32()
					for c in range(numcue): 
						marker_obj = wav_marker()
						marker_obj.read(bye_stream)
						self.markers[marker_obj.id] = marker_obj

			#else:
			#	logger_audiofile.warning('WAV: Unknown Chunk: '+str(riff_part.name))

				#with byr_stream.isolate_range(riff_part.start, riff_part.end, False) as bye_stream: 
				#	print(byr_stream.raw(riff_part.size))

	def write(self, wavfile, normalized=False):
		filepath = pathlib.Path(wavfile)
		if not os.path.exists(filepath.parent): os.makedirs(filepath.parent)
		logger_audiofile.info('WAV: Generating Sample: Channels: '+str(self.channels)+', Freq: '+str(self.rate)+', Bits: '+str(self.bits))
		data = self.data

		if self.bits == 24:
			if normalized:
				data[data > 1.0] = 1.0
				data[data < -1.0] = -1.0
				a32 = numpy.asarray(data * (2 ** 23 - 1), dtype=numpy.int32)
			else:
				a32 = numpy.asarray(data, dtype=numpy.int32)
			if a32.ndim == 1:			   
				a32.shape = a32.shape + (1,)
			a8 = (a32.reshape(a32.shape + (1,)) >> numpy.array([0, 8, 16])) & 255  # By shifting first 0 bits, then 8, then 16, the resulting output is 24 bit little-endian.
			data = a8.astype(numpy.uint8)
		else:
			if normalized:
				data[data > 1.0] = 1.0
				data[data < -1.0] = -1.0
				data = numpy.asarray(data * (2 ** 31 - 1), dtype=numpy.int32)

		riff_data = riff_chunks.riff_chunk()
		riff_data.name = b'WAVE'

		noc = 1 if data.ndim == 1 else data.shape[1]
		bits = data.dtype.itemsize * 8 if self.bits != 24 else 24
		sbytes = self.rate * (bits // 8) * noc
		ba = noc * (bits // 8)

		in_riff = riff_data.add_part(b'fmt ')
		in_riff.data = struct.pack('<hHIIHH', self.format, self.channels, self.rate, self.bytessec, self.datablocksize, self.bits)

		if self.inst.found:
			in_riff = riff_data.add_part(b'inst')
			in_riff.data = self.inst.write()

		in_riff = riff_data.add_part(b'smpl')
		in_riff.data = self.smpl.write()

		in_riff = riff_data.add_part(b'data')
		if data.dtype.byteorder == '>' or (data.dtype.byteorder == '=' and sys.byteorder == 'big'): data = data.byteswap()
		in_riff.data = data.tobytes()

		try:
			riff_data.write_to_file(filepath)
		except PermissionError:
			pass


