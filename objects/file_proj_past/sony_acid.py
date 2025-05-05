# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.data_bytes import riff_chunks
from objects import audio_data
import zlib
import logging
import numpy as np

class sdml_env:
	def __init__(self):
		self.type = 0
		self.points = []

	def read(self, riffchunk, byr_stream):
		with byr_stream.isolate_size(riffchunk.size, False) as bye_stream:
			try:
				bye_stream.magic_check(b' env')
				bye_stream.skip(4)
				bye_stream.skip(4)
				self.type = bye_stream.uint32()
				for _ in range(bye_stream.uint32()):
					p_pos = bye_stream.uint32()
					p_val = bye_stream.float()
					p_type = bye_stream.int32()
					self.points.append([p_pos, p_val, p_type])
			except:
				pass

class sdml_region:
	def __init__(self):
		self.start = 0
		self.end = 0
		self.unk3 = 0
		self.offset = 0
		self.unk5 = 0
		self.unk6 = 0
		self.pitch = 0
		self.unk8 = 0
		self.envs = []

	def read(self, riffchunk, byr_stream):
		for i in riffchunk.iter_wseek(byr_stream):
			if i.name == b'rgnh':
				with byr_stream.isolate_size(i.size, False) as bye_stream:
					self.unknowndata = []
					size = bye_stream.int32()
					self.start = bye_stream.int32()
					self.end = bye_stream.int32()
					self.unknowndata.append( bye_stream.int32() )
					self.offset = bye_stream.int32()
					self.unknowndata.append( bye_stream.int32() )
					self.unknowndata.append( bye_stream.int32() )
					self.pitch = bye_stream.int32()
					self.unknowndata.append( bye_stream.int32() )
			elif i.name == b'xlst':
				for x in i.iter_wseek(byr_stream):
					if x.name == b' env':
						env_obj = sdml_env()
						env_obj.read(x, byr_stream)
						self.envs.append(env_obj)

warp_dtype = np.dtype([
	('1', '<I'),
	('2', '>f'),
	('3', 'int64'),
	('5', 'int64'),
	('7', '<f'),
	('8', '<I')
	])

class sdml_track_send:
	def __init__(self):
		self.id = 0
		self.vol = 0

	def read(self, byr_stream):
		self.id = byr_stream.uint32()
		self.vol = byr_stream.float()

class sdml_track:
	def __init__(self):
		self.warpp = np.zeros(0, dtype=warp_dtype)
		self.path = ''
		self.name = ''
		self.device = ''
		self.color = 0
		self.num_samples = 0
		self.num_beats = 4
		self.stretch__trans_detect = 0
		self.stretch__force_divisions = 0
		self.stretch__tempo = 100
		self.stretch__type = 1
		self.pitch = 0
		self.mutesolo = 0
		self.audio_device = 0
		self.root_note = 60
		self.regions = []
		self.vol = 1
		self.pan = 0
		self.sends = []
		self.flags = []

	def read(self, riffchunk, byr_stream):
		for x in riffchunk.iter_wseek(byr_stream):

			if x.name == b'strc':
				with byr_stream.isolate_size(x.size, False) as bye_stream:
					unk1 = bye_stream.uint32()
					size = bye_stream.uint32()
					unk2 = bye_stream.uint32()
					unk3 = bye_stream.uint32()
					self.stretch__method = bye_stream.uint32()
					self.stretch__trans_detect = bye_stream.uint32()
					self.stretch__force_divisions = bye_stream.uint32()
					self.warpp = np.frombuffer(byr_stream.raw(32*size), dtype=warp_dtype)

			elif x.name == b'trkh':
				with byr_stream.isolate_size(x.size, False) as bye_stream:
					self.unknowndata = []
					self.unknowndata.append( bye_stream.uint32() )
					self.stretch__type = bye_stream.uint32()
					self.color = bye_stream.uint32()
					self.unknowndata.append( bye_stream.uint32() )
					self.num_samples = bye_stream.uint32()
					self.pitch = bye_stream.int32()
					self.unknowndata.append( bye_stream.uint32() )
					self.unknowndata.append( bye_stream.uint32() )
					self.mutesolo = bye_stream.int32()
					self.audio_device = bye_stream.int32()
					strsize_path = bye_stream.uint32()
					strsize_device = bye_stream.uint32()
					strsize_name = bye_stream.uint32()
					self.path = bye_stream.string16(strsize_path)
					self.name = bye_stream.string16(strsize_name)
					self.device = bye_stream.string16(strsize_device)

			elif x.name == b'acid':
				with byr_stream.isolate_size(x.size, False) as bye_stream:
					self.unknowndata = []
					self.flags = bye_stream.flags8()
					self.unknowndata.append( bye_stream.uint8() )
					self.unknowndata.append( bye_stream.uint8() )
					self.unknowndata.append( bye_stream.uint8() )
					self.root_note = bye_stream.uint8()
					self.unknowndata.append( bye_stream.uint8() )
					self.unknowndata.append( bye_stream.uint8() )
					self.unknowndata.append( bye_stream.uint8() )
					self.unknowndata.append( bye_stream.uint32() )
					self.num_beats = bye_stream.uint32()
					self.unknowndata.append( bye_stream.uint16() )
					self.unknowndata.append( bye_stream.uint16() )
					self.stretch__tempo = bye_stream.float()

			elif x.name == b'rlst':
				for i in x.iter_wseek(byr_stream):
					if i.name == b'rgn ':
						r_obj = sdml_region()
						r_obj.read(i, byr_stream)
						self.regions.append(r_obj)

			elif x.name == b'xlst':
				for i in x.iter_wseek(byr_stream):
					if i.name == b'gain':
						try:
							with byr_stream.isolate_size(i.size, False) as bye_stream:
								bye_stream.magic_check(b'gain')
								bye_stream.skip(8)
								self.vol = bye_stream.float()
								self.pan = bye_stream.float()
						except:
							pass
					if i.name == b'send':
						try:
							with byr_stream.isolate_size(i.size, False) as bye_stream:
								bye_stream.magic_check(b'send')
								bye_stream.skip(8)
								send_obj = sdml_track_send()
								send_obj.read(bye_stream)
								self.sends.append(send_obj)
						except:
							pass

class sdml_port:
	def __init__(self):
		self.type = 0
		self.points = []
		self.vol_left = 1
		self.vol_right = 1
		self.num = 0

	def read(self, byr_stream):
		size = byr_stream.uint32()
		byr_stream.skip(4)
		self.vol_left = byr_stream.float()
		self.vol_right = byr_stream.float()
		self.num = byr_stream.uint32()
		self.name = byr_stream.string16(byr_stream.uint32())

class sdml_marker:
	def __init__(self):
		self.pos = 0
		self.id = 0
		self.text = ''

	def read(self, byr_stream):
		size = byr_stream.uint32()
		self.pos = byr_stream.uint64()
		byr_stream.skip(8)
		self.id = byr_stream.uint32()
		self.text = byr_stream.string16(byr_stream.uint32())

tempmap_dtype = np.dtype([
	('unk1', 'int32'),
	('unk2', 'int32'),
	('pos', 'int32'),
	('tempo', 'int32'),
	('base_note', 'int32'),
	])

class sony_acid_file:
	def __init__(self):
		self.tracks = []
		self.audios = []
		self.markers = []
		self.name = ''
		self.artist = ''
		self.createdBy = ''
		self.comments = ''
		self.copyright = ''
		self.tempo = 120
		self.ports = []
		self.root_note = 60
		self.ppq = 768
		self.filename = ''
		self.tempmap = np.zeros(0, dtype=tempmap_dtype)
		self.loop_enable = 0
		self.loop_start = 0
		self.loop_end = 0

	def load_from_file(self, input_file):
		acidchunks = riff_chunks.riff_chunk()
		byr_stream = acidchunks.load_from_file(input_file, False)

		for x in acidchunks.iter_wseek(byr_stream):

			if x.name == b'fmt ':
				with byr_stream.isolate_size(x.size, False) as bye_stream:
					unk = []
					bye_stream.skip(25)
					self.loop_enable = bye_stream.uint32()
					bye_stream.skip(7)
					self.filename = bye_stream.string16(256)
					bye_stream.skip(8)
					self.loop_start = bye_stream.uint32()
					self.loop_end = bye_stream.uint32()

			elif x.name == b'tlst':
				for i in x.iter_wseek(byr_stream):
					if i.name == b'trak': 
						track_obj = sdml_track()
						track_obj.read(i, byr_stream)
						self.tracks.append(track_obj)
			elif x.name == b'WVPL':
				for i in x.iter_wseek(byr_stream):
					if i.name == b'wave':
						self.audios.append(i.dump_list(byr_stream))
			elif x.name == b'INFO':
				for i in x.iter_wseek(byr_stream):
					try:
						if i.name == b'INAM': self.name = byr_stream.string(i.size)
						if i.name == b'IART': self.artist = byr_stream.string(i.size)
						if i.name == b'ISFT': self.createdBy = byr_stream.string(i.size)
						if i.name == b'ICMT': self.comments = byr_stream.string(i.size)
						if i.name == b'ICOP': self.copyright = byr_stream.string(i.size)
					except:
						pass
			elif x.name == b'tmap':
				with byr_stream.isolate_size(x.size, False) as bye_stream:
					_size = bye_stream.uint32()
					self.ppq = bye_stream.uint32()
					self.tempo = (500000/bye_stream.uint32())*120
					self.root_note = bye_stream.uint32()
					numtp = bye_stream.uint32()
					self.tempmap = np.frombuffer(byr_stream.raw(tempmap_dtype.itemsize*numtp), dtype=tempmap_dtype)
			elif x.name == b'prts':
				for i in x.iter_wseek(byr_stream):
					if i.name == b'port':
						with byr_stream.isolate_size(i.size, False) as bye_stream:
							port_obj = sdml_port()
							port_obj.read(bye_stream)
							self.ports.append(port_obj)
			elif x.name == b'mkls':
				for i in x.iter_wseek(byr_stream):
					if i.name == b'mark':
						with byr_stream.isolate_size(i.size, False) as bye_stream:
							marker_obj = sdml_marker()
							marker_obj.read(bye_stream)
							self.markers.append(marker_obj)
		return True