# https://gist.github.com/josephernest/3f22c5ed5dabf1815f16efa8fa53d476

import numpy
import struct
import collections
import sys
import pathlib
import os

class wav_loop:
	def __init__(self, fid):
		self.identifier = 0
		self.type = 0
		self.start = 0
		self.end = 0
		self.fraction = 0
		self.playcount = 0
		if fid != None:
			self.identifier, self.type, self.start, self.end, self.fraction, self.playcount = struct.unpack('<iiiiii', fid.read(24))
			print(self.identifier, self.type, self.start, self.end, self.fraction, self.playcount)

	def write(self):
		return struct.pack('<iiiiii', self.identifier, self.type, self.start, self.end, self.fraction, self.playcount)

class wav_marker:
	def __init__(self, fid):
		self.id = 0
		self.position = 0
		self.datachunkid = 0
		self.chunkstart = 0
		self.blockstart = 0
		self.sampleoffset = 0
		self.label = None
		if fid != None:
			self.id, self.position, self.datachunkid, self.chunkstart, self.blockstart, self.sampleoffset = struct.unpack('<iiiiii', fid.read(24))

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

	def read(self, fid, size):
		endpoint = fid.tell()+size
		self.manu, self.product, self.sampleperiod, self.note_middle, self.midi_pitchfrac, self.smpte_format, self.smpte_offset, numloops, sampspecsize = struct.unpack('<iiiiIiiii', fid.read(36))
		for _ in range(numloops): self.loops.append(wav_loop(fid))
		self.sampler_specific = fid.read(sampspecsize)
		fid.seek(endpoint)

	def write(self):
		size = 36 + len(self.loops) * 24 + len(self.sampler_specific)
		outdata = struct.pack('<iiiiiIiiii', size, self.manu, self.product, self.sampleperiod, self.note_middle, self.midi_pitchfrac, self.smpte_format, self.smpte_offset, len(self.loops), len(self.sampler_specific))
		for l in self.loops: outdata += l.write()
		outdata += self.sampler_specific
		return outdata

class wav_main:
	def __init__(self):
		self.format = 1
		self.channels = 1
		self.rate = 44100
		self.bytessec = 44100
		self.bits = 8
		self.datablocksize = int((self.bits/8)*self.channels)
		self.data = numpy.float32([])
		self.smpl = wav_smpl()
		#self.inst_finetune = 0
		#self.inst_gain = 0
		#self.inst_note_low = 0
		#self.inst_note_high = 127
		#self.inst_vel_low = 0
		#self.inst_vel_high = 127
		self.uses_float = False
		self.markers = {}
		self.unknown_chunks = {}

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

	def data_add_data(self, bits, channels, signed, data):
		self.channels = channels
		self.bits = bits
		if self.bits == 8:
			if not signed: self.data = numpy.frombuffer(data, dtype=numpy.int8)
			else: self.data = numpy.frombuffer(data, dtype=numpy.uint8) - 128
		if self.bits == 16:
			if not signed: self.data = numpy.frombuffer(data, dtype=numpy.int16)
			else: self.data = numpy.array(data, dtype=numpy.uint16) - 32768
		self.set_blksize()

	def _read_chunk_fmt(self, fid):
		size, self.format, self.channels, self.rate, self.bytessec, self.datablocksize, self.bits = struct.unpack('<ihHIIHH',fid.read(20))
		if (self.format != 1 or size > 16):
			if (self.format == 3): self.uses_float = True
			if (size>16): fid.read(size-16)

	def _read_chunk_data(self, fid, normalized=False):
		size = struct.unpack('<i',fid.read(4))[0]

		if self.bits in [8, 24]:
			bytes = 1
			dtype = 'u1'
		else:
			bytes = self.bits//8
			dtype = '<i%d' % bytes
			
		if self.bits == 32 and self.uses_float: dtype = 'float32'
			
		self.data = numpy.fromfile(fid, dtype=dtype, count=size//bytes)
		
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

	def _read_chunk_unknown(self, fid):
		data = fid.read(4)
		size = struct.unpack('<i', data)[0]
		if bool(size & 1): size += 1 
		fid.seek(size, 1)

	def _read_chunk_riff(self, fid):
		if fid.read(4) != b'RIFF': raise ValueError("Not a WAV file.")
		fsize = struct.unpack('<I', fid.read(4))[0] + 8
		if fid.read(4) != b'WAVE': raise ValueError("Not a WAV file.")
		return fsize


	def read(self, wavfile):
		fid = open(wavfile, 'rb')
		fsize = self._read_chunk_riff(fid)
		while (fid.tell() < fsize):
			chunk_id = fid.read(4)
			#print('[audio_wav] Chunk:', chunk_id)
			if chunk_id == b'fmt ': self._read_chunk_fmt(fid)
			elif chunk_id == b'data': self._read_chunk_data(fid)
			elif chunk_id == b'cue ':
				size, numcue = struct.unpack('<ii',fid.read(8))
				for c in range(numcue): 
					marker_obj = wav_marker(fid)
					self.markers[marker_obj.id] = marker_obj
			elif chunk_id == b'LIST': size, type = struct.unpack('<ii', fid.read(8))
			#elif chunk_id in [b'ICRD', b'IENG', b'ISFT', b'ISTJ', b'acid']: self._read_chunk_unknown(fid)
			elif chunk_id == b'labl':
				size, marker_id = struct.unpack('<ii',fid.read(8))
				size = size+(size%2)
				self.markers[marker_id].label = fid.read(size-4).decode().rstrip('\x00')
			elif chunk_id == b'smpl':
				size = struct.unpack('<i',fid.read(4))[0]
				self.smpl.read(fid, size)
			#elif chunk_id == b'inst':
			#	size, _, self.inst_finetune, self.inst_gain, self.inst_note_low, self.inst_note_high, self.inst_vel_low, self.inst_vel_high = struct.unpack('IBbbBBBB', fid.read(11))
			#	if bool(size & 1): fid.seek(1,1)
			else:
				print('[audio-wav] Unknown Chunk:', chunk_id)
				size = struct.unpack('I',fid.read(4))[0]
				self.unknown_chunks[chunk_id] = fid.read(size)
				if bool(size & 1): fid.seek(1,1)

	def write(self, wavfile, normalized=False):
		filepath = pathlib.Path(wavfile)
		if not os.path.exists(filepath.parent): os.makedirs(filepath.parent)
		print('[audio-wav] Generating Sample: Channels: '+str(self.channels)+', Freq: '+str(self.rate)+', Bits: '+str(self.bits))
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

		fid = open(wavfile, 'wb')
		fid.write(b'RIFF')
		fid.write(b'\x00\x00\x00\x00')
		fid.write(b'WAVE')
		fid.write(b'fmt ')
		noc = 1 if data.ndim == 1 else data.shape[1]
		bits = data.dtype.itemsize * 8 if self.bits != 24 else 24
		sbytes = self.rate * (bits // 8) * noc
		ba = noc * (bits // 8)
		fid.write(struct.pack('<ihHIIHH', 16, self.format, self.channels, self.rate, self.bytessec, self.datablocksize, self.bits))
		fid.write(b'smpl' + self.smpl.write())
		fid.write(b'data')
		fid.write(struct.pack('<i', data.nbytes))
		if data.dtype.byteorder == '>' or (data.dtype.byteorder == '=' and sys.byteorder == 'big'): data = data.byteswap()
		data.tofile(fid)
		if data.nbytes % 2 == 1: fid.write(b'\x00')
		size = fid.tell()
		fid.seek(4)
		fid.write(struct.pack('<i', size-8))
		fid.close()

