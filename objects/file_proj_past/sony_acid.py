# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import numpy as np
from external.easybinrw import easybinrw
from external.easybinrw import riff_chunks

class sdml_env:
	def __init__(self):
		self.type = 0
		self.points = []

	def read(self, riffchunk, ebrw_readstr):
		try:
			ebrw_readstr.magic_check(b' env')
			ebrw_readstr.skip(4)
			ebrw_readstr.skip(4)
			self.type = ebrw_readstr.int_u32()
			for _ in range(ebrw_readstr.int_u32()):
				p_pos = ebrw_readstr.int_u32()
				p_val = ebrw_readstr.float()
				p_type = ebrw_readstr.int_s32()
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

	def read(self, riffchunk, ebrw_readstr):
		for i in riffchunk.iter_reader(ebrw_readstr):
			if i.id == b'rgnh':
					self.unknowndata = []
					size = ebrw_readstr.int_s32()
					self.start = ebrw_readstr.int_s32()
					self.end = ebrw_readstr.int_s32()
					self.unknowndata.append( ebrw_readstr.int_s32() )
					self.offset = ebrw_readstr.int_s32()
					self.unknowndata.append( ebrw_readstr.int_s32() )
					self.unknowndata.append( ebrw_readstr.int_s32() )
					self.pitch = ebrw_readstr.int_s32()
					self.unknowndata.append( ebrw_readstr.int_s32() )
			elif i.id == b'xlst':
				for x in i.iter_reader(ebrw_readstr):
					if x.id == b' env':
						env_obj = sdml_env()
						env_obj.read(x, ebrw_readstr)
						self.envs.append(env_obj)

warp_dtype = np.dtype([
	('1', '<I'),
	('2', '<I'),
	('3', 'int64'),
	('5', 'int64'),
	('7', '<f'),
	('8', '<I')
	])

class sdml_track_send:
	def __init__(self):
		self.id = 0
		self.vol = 0

	def read(self, ebrw_readstr):
		self.id = ebrw_readstr.int_u32()
		self.vol = ebrw_readstr.float()

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

	def read(self, riffchunk, ebrw_readstr):
		for i in riffchunk.iter_reader(ebrw_readstr):

			if i.id == b'strc':
				unk1 = ebrw_readstr.int_u32()
				total = ebrw_readstr.int_u32()
				unk2 = ebrw_readstr.int_u32()
				unk3 = ebrw_readstr.int_u32()
				self.stretch__method = ebrw_readstr.int_u32()
				self.stretch__trans_detect = ebrw_readstr.int_u32()
				self.stretch__force_divisions = ebrw_readstr.int_u32()
				self.warpp = np.frombuffer(ebrw_readstr.raw(32*total), dtype=warp_dtype)

			elif i.id == b'trkh':
				self.unknowndata = []
				self.unknowndata.append( ebrw_readstr.int_u32() )
				self.stretch__type = ebrw_readstr.int_u32()
				self.color = ebrw_readstr.int_u32()
				self.unknowndata.append( ebrw_readstr.int_u32() )
				self.num_samples = ebrw_readstr.int_u32()
				self.pitch = ebrw_readstr.int_s32()
				self.unknowndata.append( ebrw_readstr.int_u32() )
				self.unknowndata.append( ebrw_readstr.int_u32() )
				self.mutesolo = ebrw_readstr.int_s32()
				self.audio_device = ebrw_readstr.int_s32()
				strsize_path = ebrw_readstr.int_u32()
				strsize_device = ebrw_readstr.int_u32()
				strsize_name = ebrw_readstr.int_u32()
				self.path = ebrw_readstr.string16(strsize_path)
				self.name = ebrw_readstr.string16(strsize_name)
				self.device = ebrw_readstr.string16(strsize_device)

			elif i.id == b'acid':
				self.unknowndata = []
				self.flags = ebrw_readstr.flags_i8()
				self.unknowndata.append( ebrw_readstr.int_u8() )
				self.unknowndata.append( ebrw_readstr.int_u8() )
				self.unknowndata.append( ebrw_readstr.int_u8() )
				self.root_note = ebrw_readstr.int_u8()
				self.unknowndata.append( ebrw_readstr.int_u8() )
				self.unknowndata.append( ebrw_readstr.int_u8() )
				self.unknowndata.append( ebrw_readstr.int_u8() )
				self.unknowndata.append( ebrw_readstr.int_u32() )
				self.num_beats = ebrw_readstr.int_u32()
				self.unknowndata.append( ebrw_readstr.int_u16() )
				self.unknowndata.append( ebrw_readstr.int_u16() )
				self.stretch__tempo = ebrw_readstr.float()

			elif i.id == b'rlst':
				for c in i.iter_reader(ebrw_readstr):
					if c.id == b'rgn ':
						r_obj = sdml_region()
						r_obj.read(c, ebrw_readstr)
						self.regions.append(r_obj)

			elif i.id == b'xlst':
				for c in i.iter_reader(ebrw_readstr):
					if c.id == b'gain':
						try:
							ebrw_readstr.magic_check(b'gain')
							ebrw_readstr.skip(8)
							self.vol = ebrw_readstr.float()
							self.pan = ebrw_readstr.float()
						except:
							pass
					if c.id == b'send':
						try:
							ebrw_readstr.magic_check(b'send')
							ebrw_readstr.skip(8)
							send_obj = sdml_track_send()
							send_obj.read(ebrw_readstr)
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

	def read(self, ebrw_readstr):
		size = ebrw_readstr.int_u32()
		ebrw_readstr.skip(4)
		self.vol_left = ebrw_readstr.float()
		self.vol_right = ebrw_readstr.float()
		self.num = ebrw_readstr.int_u32()
		self.name = ebrw_readstr.string16(ebrw_readstr.int_u32())

class sdml_marker:
	def __init__(self):
		self.pos = 0
		self.id = 0
		self.text = ''

	def read(self, ebrw_readstr):
		size = ebrw_readstr.int_u32()
		self.pos = ebrw_readstr.int_u64()
		ebrw_readstr.skip(8)
		self.id = ebrw_readstr.int_u32()
		self.text = ebrw_readstr.string16(ebrw_readstr.int_u32())

class sdml_fxdx:
	def __init__(self):
		from objects.file import preset_dx
		self.preset_obj = preset_dx.dx_preset()
		self.level_l = 1
		self.level_r = 1
		self.fx_num = 0
		self.name = ''
		self.id = None
		self.name2 = ''
		self.preset_name = ''

	def read(self, ebrw_readstr):
		try:
			ebrw_readstr.magic_check(b'fxdx')
			ebrw_readstr.skip(8)
			self.unknowndata = []
			self.unknowndata.append( ebrw_readstr.int_u32() )
			self.unknowndata.append( ebrw_readstr.int_u32() )
			self.level_l = ebrw_readstr.float()
			self.level_r = ebrw_readstr.float()
			self.audio_device = ebrw_readstr.int_u32()
			self.unknowndata.append( ebrw_readstr.int_u32() )
			self.fx_num = ebrw_readstr.int_u32()
			self.unknowndata.append( ebrw_readstr.int_u32() )
			self.unknowndata.append( ebrw_readstr.int_u32() )
			self.unknowndata.append( ebrw_readstr.raw(16) )
			self.unknowndata.append( ebrw_readstr.int_u32() )
			self.name = ebrw_readstr.string16(ebrw_readstr.int_u32()//2)
			self.unknowndata.append( ebrw_readstr.int_u32() )
			self.unknowndata.append( ebrw_readstr.int_u32() )
			self.unknowndata.append( ebrw_readstr.int_u32() )
			self.unknowndata.append( ebrw_readstr.int_u32() )
			self.unknowndata.append( ebrw_readstr.int_u32() )
			self.unknowndata.append( ebrw_readstr.int_u16() )
			self.unknowndata.append( ebrw_readstr.int_u32() )
			self.unknowndata.append( ebrw_readstr.int_u32() )
			self.unknowndata.append( ebrw_readstr.int_u32() )
			self.unknowndata.append( ebrw_readstr.int_u32() )

			self.id = ebrw_readstr.raw(16).hex()
			self.name2 = ebrw_readstr.string16(ebrw_readstr.int_u32()//2)

			self.preset_obj.parse(ebrw_readstr)

			self.unknowndata.append( ebrw_readstr.int_u32() )
			self.unknowndata.append( ebrw_readstr.int_u32() )
			self.unknowndata.append( ebrw_readstr.int_u32() )
			self.unknowndata.append( ebrw_readstr.int_u32() )
			self.unknowndata.append( ebrw_readstr.int_u32() )
			self.preset_name = ebrw_readstr.string16(ebrw_readstr.int_u32()//2)
			self.unknowndata.append( ebrw_readstr.int_u32() )
			self.unknowndata.append( ebrw_readstr.int_u32() )
			self.unknowndata.append( ebrw_readstr.int_u32() )
			self.unknowndata.append( ebrw_readstr.int_u32() )
			self.unknowndata.append( ebrw_readstr.int_u32() )
			self.unknowndata.append( ebrw_readstr.int_u32() )
			self.unknowndata.append( ebrw_readstr.int_u32() )
		except:
			pass

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
		self.fx_dx = []

	def load_from_file(self, input_file):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_file(input_file)
		main_chunk = riff_chunks.riff_chunk()
		main_chunk.read(ebrw_readstr, 0)

		for riffpart in main_chunk.iter_reader(ebrw_readstr):
			if riffpart.id == b'fmt ':
				unk = []
				ebrw_readstr.skip(25)
				self.loop_enable = ebrw_readstr.int_u32()
				ebrw_readstr.skip(7)
				self.filename = ebrw_readstr.string16(256)
				ebrw_readstr.skip(8)
				self.loop_start = ebrw_readstr.int_u32()
				self.loop_end = ebrw_readstr.int_u32()

			elif riffpart.id == b'tlst':
				for i in riffpart.iter_reader(ebrw_readstr):
					if i.id == b'trak': 
						track_obj = sdml_track()
						track_obj.read(i, ebrw_readstr)
						self.tracks.append(track_obj)

			elif riffpart.id == b'WVPL':
				for i in riffpart.iter_reader(ebrw_readstr):
					if i.id == b'wave':
						wave_chunks = riff_chunks.riff_chunk()
						wave_chunks.id = b'WAVE'
						for w in i.iter_reader(ebrw_readstr):
							in_ch = wave_chunks.add_part(w.id)
							in_ch.data = ebrw_readstr.rest()
						self.audios.append( wave_chunks.write_data() )

			elif riffpart.id == b'INFO':
				for i in riffpart.iter_reader(ebrw_readstr):
					try:
						if i.id == b'INAM': self.name = ebrw_readstr.string(i.size)
						elif i.id == b'IART': self.artist = ebrw_readstr.string(i.size)
						elif i.id == b'ISFT': self.createdBy = ebrw_readstr.string(i.size)
						elif i.id == b'ICMT': self.comments = ebrw_readstr.string(i.size)
						elif i.id == b'ICOP': self.copyright = ebrw_readstr.string(i.size)
					except:
						pass

			elif riffpart.id == b'tmap':
				_size = ebrw_readstr.int_u32()
				self.ppq = ebrw_readstr.int_u32()
				self.tempo = (500000/ebrw_readstr.int_u32())*120
				self.root_note = ebrw_readstr.int_u32()
				numtp = ebrw_readstr.int_u32()
				self.tempmap = np.frombuffer(ebrw_readstr.raw(tempmap_dtype.itemsize*numtp), dtype=tempmap_dtype)

			elif riffpart.id == b'prts':
				for i in riffpart.iter_reader(ebrw_readstr):
					if i.id == b'port':
						port_obj = sdml_port()
						port_obj.read(ebrw_readstr)
						self.ports.append(port_obj)

			elif riffpart.id == b'mkls':
				for i in riffpart.iter_reader(ebrw_readstr):
					if i.id == b'mark':
						marker_obj = sdml_marker()
						marker_obj.read(ebrw_readstr)
						self.markers.append(marker_obj)

			elif riffpart.id == b'xlst':
				for i in riffpart.iter_reader(ebrw_readstr):
					if i.id == b'fxdx':
						fxdx_obj = sdml_fxdx()
						fxdx_obj.read(ebrw_readstr)
						self.fx_dx.append(fxdx_obj)

		return True