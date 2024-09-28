# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.data_bytes import bytereader
from objects import openmpt_plugin

import logging
logger_projparse = logging.getLogger('projparse')
from objects.exceptions import ProjectFileParserException

class xm_pattern:
	def __init__(self, song_file, num, num_channels):
		#logger_projparse.info("xm: Pattern " + str(num))
		self.data = []
		self.used = False

		basepos = song_file.tell()
		header_length = song_file.uint32()
		self.pak_type = song_file.uint8()
		self.rows = song_file.uint16()
		patterndata_size = song_file.uint16()
		basepos_end = song_file.tell()
		self.extra_data = song_file.raw(header_length - (basepos_end-basepos))
		end_pos = patterndata_size+song_file.tell()

		if patterndata_size != 0:
			self.used = True
			for rownum in range(self.rows):
				rowdata = []
				for channel in range(num_channels):
					cell_note = None
					cell_inst = None
					cell_vol = None
					cell_effect = None
					cell_param = None

					packed_first = song_file.uint8()

					packed_note = bool(packed_first&1)
					packed_inst = bool(packed_first&2)
					packed_vol = bool(packed_first&4)
					packed_effect = bool(packed_first&8)
					packed_param = bool(packed_first&16)
					packed_msb = bool(packed_first&128)

					if packed_msb == 1:
						if packed_note == 1: cell_note = song_file.uint8()
						if packed_inst == 1: cell_inst = song_file.uint8()
						if packed_vol == 1: cell_vol = song_file.uint8()
						if packed_effect == 1: cell_effect = song_file.uint8()
						if packed_param == 1: cell_param = song_file.uint8()
					else:
						cell_note = packed_first
						cell_inst = song_file.uint8()
						cell_vol = song_file.uint8()
						cell_effect = song_file.uint8()
						cell_param = song_file.uint8()

					if not (cell_note == cell_inst == cell_vol == cell_effect == cell_param == None):
						rowdata.append([channel, cell_note, cell_inst, cell_vol, cell_effect, cell_param])

				self.data.append(rowdata)

class xm_env:
	def __init__(self): 
		self.points = []
		self.numpoints = 0
		self.sustain = 0
		self.type = 0
		self.loop_start = 0
		self.loop_end = 0
		self.enabled = False
		self.sustain_on = False
		self.loop_on = False

	def set_type(self, i_type): 
		self.type = i_type
		self.enabled = bool(i_type&1)
		self.sustain_on = bool(i_type&2)
		self.loop_on = bool(i_type&4)

class xm_sample_header:
	def __init__(self, song_file): 
		self.length = song_file.uint32()
		self.loop_start = song_file.uint32()
		self.loop_end = song_file.uint32()
		self.vol = song_file.uint8()
		self.fine = song_file.uint8()
		self.type = song_file.uint8()
		self.pan = song_file.uint8()
		self.note = song_file.uint8()
		self.reserved = song_file.uint8()
		self.name = song_file.string(22, encoding="windows-1252")
		self.vol /= 64
		if self.type&1: self.loop = 1
		elif self.type&2: self.loop = 2
		else: self.loop = 0
		self.stereo = self.type&32
		self.loop_on = bool(self.loop)
		self.double = bool(self.type&16)

	def get_loop(self): 
		looptype = 'normal' if self.loop != 2 else 'pingpong'
		loop_start = self.loop_start
		loop_end = (self.loop_start+self.loop_end)
		if self.double: loop_start /= 2
		if self.double: loop_end /= 2
		if self.stereo: loop_start /= 2
		if self.stereo: loop_end /= 2
		return self.loop!=0, looptype, loop_start, loop_end if self.loop_end else self.length

class xm_instrument:
	def __init__(self, song_file, num):
		basepos = song_file.tell()
		header_length = song_file.uint32()
		self.name = song_file.string(22, encoding="latin1")
		self.type = song_file.uint8()
		self.num_samples = song_file.uint8()

		logger_projparse.info("xm: Instrument "+str(num+1)+" | Type: "+str(self.type)+
			" | "+str(self.num_samples)+' Samples'+
			" | Name:"+str(self.name)
			)
		self.env_vol = xm_env()
		self.env_pan = xm_env()
		self.vibrato_type = 0
		self.vibrato_sweep = 0
		self.vibrato_depth = 0
		self.vibrato_rate = 0
		self.fadeout = 0

		self.notesampletable = []

		if self.num_samples != 0:
			xm_inst_e_head_size = song_file.uint32()
			self.notesampletable = song_file.l_uint8(96)
			self.env_vol.points = [song_file.l_uint16_b(2) for x in range(12)]
			self.env_pan.points = [song_file.l_uint16_b(2) for x in range(12)]

			song_file.skip(1)
			self.env_vol.numpoints = song_file.uint8()
			self.env_pan.numpoints = song_file.uint8()
			self.env_vol.sustain = song_file.uint8()
			self.env_vol.loop_start = song_file.uint8()
			self.env_vol.loop_end = song_file.uint8()
			self.env_pan.sustain = song_file.uint8()
			self.env_pan.loop_start = song_file.uint8()
			self.env_pan.loop_end = song_file.uint8()
			self.env_vol.set_type(song_file.uint8())
			self.env_pan.set_type(song_file.uint8())
			self.vibrato_type = song_file.uint8()
			self.vibrato_sweep = song_file.uint8()
			self.vibrato_depth = song_file.uint8()
			self.vibrato_rate = song_file.uint8()
			self.fadeout = song_file.uint16()
			self.reserved = song_file.uint16()

		basepos_end = song_file.tell()
		xm_pat_extra_data = song_file.read(header_length - (basepos_end-basepos))

		self.pluginnum = 0

		self.samp_head = [xm_sample_header(song_file) for _ in range(self.num_samples)]
		self.samp_data = [song_file.read(x.length) for x in self.samp_head]

	def vibrato_lfo(self): 
		return self.vibrato_rate, (self.vibrato_depth/15)*0.23, ['sine','square','ramp_up','ramp_down'][self.vibrato_type&3], self.vibrato_sweep/50

class xm_song:
	def __init__(self):
		pass

	def load_from_raw(self, input_file):
		song_file = bytereader.bytereader()
		song_file.load_raw(input_file)
		return self.load(song_file)

	def load_from_file(self, input_file):
		song_file = bytereader.bytereader()
		song_file.load_file(input_file)
		return self.load(song_file)

	def load(self, song_file):
		try: song_file.magic_check(b'Extended Module: ')
		except ValueError as t: raise ProjectFileParserException('xm: '+str(t))

		self.title = song_file.string(20, encoding="windows-1252")
		logger_projparse.info("xm: Song Name: " + self.title)
		song_file.skip(1)
		self.tracker_name = song_file.string(20, encoding="windows-1252")
		logger_projparse.info("xm: Tracker Name: " + self.tracker_name)
		self.version = song_file.l_uint8(2)
		logger_projparse.info("xm: Version: " + str(self.version[1])+','+str(self.version[0]))

		xm_headersize = song_file.uint32()
		xm_headersize_pos = song_file.tell()

		self.length = song_file.uint16()
		self.restart_pos = song_file.uint16()
		self.num_channels = song_file.uint16()
		self.num_patterns = song_file.uint16()
		self.num_instruments = song_file.uint16()
		self.flags = song_file.flags16()
		self.speed = song_file.uint16()
		self.bpm = song_file.uint16()
		
		logger_projparse.info("xm: Song Length: " + str(self.length))
		logger_projparse.info("xm: Song Restart Position: " + str(self.restart_pos))
		logger_projparse.info("xm: Number of channels: " + str(self.num_channels))
		logger_projparse.info("xm: Number of patterns: " + str(self.num_patterns))
		logger_projparse.info("xm: Number of instruments: " + str(self.num_instruments))
		logger_projparse.info("xm: Flags: " + str(self.flags))
		logger_projparse.info("xm: Speed: " + str(self.speed))
		logger_projparse.info("xm: BPM: " + str(self.bpm))

		self.l_order = song_file.l_uint8(self.length)
		logger_projparse.info("xm: Order: " + str(self.l_order))

		findpat = song_file.tell()
		calc_pos = xm_headersize+xm_headersize_pos-4

		self.extra_data = song_file.raw(calc_pos-findpat)

		self.patterns = [xm_pattern(song_file, n, self.num_channels) for n in range(self.num_patterns)]
		self.instruments = [xm_instrument(song_file, n) for n in range(self.num_instruments)]

		self.ompt_artist = None
		self.ompt_cnam = None
		self.ompt_pnam = None
		self.ompt_chfx = None
		self.ompt_ccol = []
		self.plugins = {}

		endd = 0
		if song_file.tell()<song_file.end:
			main_iff_obj = song_file.chunk_objmake()
			for chunk_obj in main_iff_obj.iter(song_file.tell(), song_file.end):
				if chunk_obj.id == b'CNAM': 
					self.ompt_cnam = song_file.l_string(chunk_obj.size//20, 20)
					print('[xm] Channel Names:',self.ompt_cnam)
				elif chunk_obj.id == b'PNAM': 
					self.ompt_pnam = song_file.l_string(chunk_obj.size//32, 32)
					print('[xm] Pattern Names:',self.ompt_pnam)
				elif chunk_obj.id == b'CHFX': 
					self.ompt_chfx = song_file.l_int32(chunk_obj.size//4)
					print('[xm] Channel FX:',self.ompt_chfx)
				elif chunk_obj.id[0:2] == b'FX':
					plugnum = int(chunk_obj.id[2:4].decode())+1
					plug_obj = openmpt_plugin.openmpt_plugin()
					plug_obj.read(song_file)
					print('[xm] '+chunk_obj.id.decode()+':',plug_obj.type.decode())
					self.plugins[plugnum] = plug_obj
				else: 
					break
				endd = song_file.tell()

		song_file.seek(endd)

		return True

		#if song_file.raw(4) == b'STPM':
		#	if song_file.tell()<song_file.end:
		#		main_iff_obj = song_file.chunk_objmake()
		#		main_iff_obj.set_sizes(4, 2, False)
		#		for chunk_obj in main_iff_obj.iter(song_file.tell(), song_file.end):

		#			print(chunk_obj.id)

		#			if chunk_obj.id == b'CCOL': self.ompt_ccol = song_file.table8([chunk_obj.size//4, 4])
		#			if chunk_obj.id == b'AUTH': self.ompt_artist = song_file.string(chunk_obj.size)
