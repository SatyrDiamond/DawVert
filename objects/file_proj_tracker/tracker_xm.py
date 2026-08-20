# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from external.easybinrw import easybinrw
from external.easybinrw import chunked
#from objects import openmpt_plugin
import logging
from objects.exceptions import ProjectFileParserException

logger_projparse = logging.getLogger('projparse')

# ============================================= instrument ============================================= 

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
	def __init__(self): 
		self.length = 0
		self.loop_start = 0
		self.loop_end = 0 
		self.vol = 64
		self.fine = 0
		self.type = 0
		self.pan = 128
		self.note = 0
		self.reserved = 0
		self.name = ''

	def read(self, ebrw_readstr): 
		self.length = ebrw_readstr.int_u32()
		self.loop_start = ebrw_readstr.int_u32()
		self.loop_end = ebrw_readstr.int_u32()
		self.vol = ebrw_readstr.int_u8()
		self.fine = ebrw_readstr.int_u8()
		self.type = ebrw_readstr.int_u8()
		self.pan = ebrw_readstr.int_u8()
		self.note = ebrw_readstr.int_u8()
		self.reserved = ebrw_readstr.int_u8()
		self.name = ebrw_readstr.string(22, encoding="windows-1252")

		self.vol /= 64
		if self.type&1: self.loop = 1
		elif self.type&2: self.loop = 2
		else: self.loop = 0
		self.stereo = bool(self.type&32)
		self.loop_on = bool(self.loop)
		self.double = bool(self.type&16)

	def get_len(self):
		outlen = self.length
		if self.double: outlen //= 2
		if self.stereo: outlen //= 2
		return outlen

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
	def __init__(self):
		self.name = ''
		self.type = 152
		self.env_vol = xm_env()
		self.env_pan = xm_env()
		self.vibrato_type = 0
		self.vibrato_sweep = 0
		self.vibrato_depth = 0
		self.vibrato_rate = 0
		self.fadeout = 0
		self.notesampletable = []
		self.samp_head = []
		self.samp_data = []
		self.reserved = 0
		self.pluginnum = 0
		self.num_samples = 0

	def read(self, ebrw_readstr, num): 
		basepos = ebrw_readstr.tell()
		header_length = ebrw_readstr.int_u32()
		self.name = ebrw_readstr.string(22, encoding="latin1")
		self.type = ebrw_readstr.int_u8()
		self.num_samples = ebrw_readstr.int_u8()

		logger_projparse.info("xm: Instrument "+str(num+1)+" | Type: "+str(self.type)+
			" | "+str(self.num_samples)+' Samples'+
			" | Name:"+str(self.name)
			)

		if self.num_samples != 0:
			xm_inst_e_head_size = ebrw_readstr.int_u32()
			self.notesampletable = ebrw_readstr.list_int_u8(96)
			self.env_vol.points = [list(ebrw_readstr.list_int_u16_b(2).tolist()) for x in range(12)]
			self.env_pan.points = [list(ebrw_readstr.list_int_u16_b(2).tolist()) for x in range(12)]

			ebrw_readstr.skip(1)
			self.env_vol.numpoints = ebrw_readstr.int_u8()
			self.env_pan.numpoints = ebrw_readstr.int_u8()
			self.env_vol.sustain = ebrw_readstr.int_u8()
			self.env_vol.loop_start = ebrw_readstr.int_u8()
			self.env_vol.loop_end = ebrw_readstr.int_u8()
			self.env_pan.sustain = ebrw_readstr.int_u8()
			self.env_pan.loop_start = ebrw_readstr.int_u8()
			self.env_pan.loop_end = ebrw_readstr.int_u8()
			self.env_vol.set_type(ebrw_readstr.int_u8())
			self.env_pan.set_type(ebrw_readstr.int_u8())
			self.vibrato_type = ebrw_readstr.int_u8()
			self.vibrato_sweep = ebrw_readstr.int_u8()
			self.vibrato_depth = ebrw_readstr.int_u8()
			self.vibrato_rate = ebrw_readstr.int_u8()
			self.fadeout = ebrw_readstr.int_u16()
			self.reserved = ebrw_readstr.int_u16()

		basepos_end = ebrw_readstr.tell()
		xm_pat_extra_data = ebrw_readstr.raw(header_length - (basepos_end-basepos))

		self.samp_head = [xm_sample_header() for _ in range(self.num_samples)]
		for s in self.samp_head: s.read(ebrw_readstr)
		self.samp_data = [ebrw_readstr.raw(x.length) for x in self.samp_head]

	def vibrato_lfo(self): 
		return self.vibrato_rate, (self.vibrato_depth/15)*0.23, ['sine','square','ramp_up','ramp_down'][self.vibrato_type&3], self.vibrato_sweep/50

# ============================================= song ============================================= 

class xm_pattern:
	def __init__(self):
		self.data = []
		self.used = False
		self.rows = 64
		self.extra_data = b''

	def read(self, ebrw_readstr, num, num_channels): 
		#logger_projparse.info("xm: Pattern " + str(num))
		basepos = ebrw_readstr.tell()
		header_length = ebrw_readstr.int_u32()
		pak_type = ebrw_readstr.int_u8()
		self.rows = ebrw_readstr.int_u16()
		patterndata_size = ebrw_readstr.int_u16()
		basepos_end = ebrw_readstr.tell()
		self.extra_data = ebrw_readstr.raw(header_length - (basepos_end-basepos))
		end_pos = patterndata_size+ebrw_readstr.tell()

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

					packed_first = ebrw_readstr.int_u8()

					packed_note = bool(packed_first&1)
					packed_inst = bool(packed_first&2)
					packed_vol = bool(packed_first&4)
					packed_effect = bool(packed_first&8)
					packed_param = bool(packed_first&16)
					packed_msb = bool(packed_first&128)

					if packed_msb == 1:
						if packed_note == 1: cell_note = ebrw_readstr.int_u8()
						if packed_inst == 1: cell_inst = ebrw_readstr.int_u8()
						if packed_vol == 1: cell_vol = ebrw_readstr.int_u8()
						if packed_effect == 1: cell_effect = ebrw_readstr.int_u8()
						if packed_param == 1: cell_param = ebrw_readstr.int_u8()
					else:
						cell_note = packed_first
						cell_inst = ebrw_readstr.int_u8()
						cell_vol = ebrw_readstr.int_u8()
						cell_effect = ebrw_readstr.int_u8()
						cell_param = ebrw_readstr.int_u8()

					if not (cell_note == cell_inst == cell_vol == cell_effect == cell_param == None):
						rowdata.append([channel, cell_note, cell_inst, cell_vol, cell_effect, cell_param])

				self.data.append(rowdata)

class xm_song:
	def __init__(self):
		self.title = ''
		self.tracker_name = ''
		self.version = [4,1]
		self.num_channels = 0
		self.num_patterns = 0
		self.num_instruments = 0
		self.length = 0
		self.restart_pos = 0
		self.flags = []
		self.speed = 6
		self.bpm = 120
		self.l_order = []

		self.extra_data = b''

		self.patterns = []
		self.instruments = []

		self.ompt_artist = None
		self.ompt_cnam = None
		self.ompt_pnam = None
		self.ompt_chfx = None
		self.ompt_ccol = []
		self.plugins = {}

	def load_from_raw(self, input_file):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_data(input_file)
		return self.load(ebrw_readstr)

	def load_from_file(self, input_file):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_file(input_file)
		return self.load(ebrw_readstr)

	def load(self, ebrw_readstr):
		try: ebrw_readstr.magic_check(b'Extended Module: ')
		except ValueError as t: raise ProjectFileParserException('xm: '+str(t))

		self.title = ebrw_readstr.string(20, encoding="windows-1252")
		logger_projparse.info("xm: Song Name: " + self.title)
		ebrw_readstr.skip(1)
		self.tracker_name = ebrw_readstr.string(20, encoding="windows-1252")
		logger_projparse.info("xm: Tracker Name: " + self.tracker_name)
		self.version = ebrw_readstr.list_int_u8(2)
		logger_projparse.info("xm: Version: " + str(self.version[1])+','+str(self.version[0]))

		xm_headersize = ebrw_readstr.int_u32()
		xm_headersize_pos = ebrw_readstr.tell()

		self.length = ebrw_readstr.int_u16()
		self.restart_pos = ebrw_readstr.int_u16()
		self.num_channels = ebrw_readstr.int_u16()
		self.num_patterns = ebrw_readstr.int_u16()
		self.num_instruments = ebrw_readstr.int_u16()
		self.flags = ebrw_readstr.flags_i16()
		self.speed = ebrw_readstr.int_u16()
		self.bpm = ebrw_readstr.int_u16()
		
		logger_projparse.info("xm: Song Length: " + str(self.length))
		logger_projparse.info("xm: Song Restart Position: " + str(self.restart_pos))
		logger_projparse.info("xm: Number of channels: " + str(self.num_channels))
		logger_projparse.info("xm: Number of patterns: " + str(self.num_patterns))
		logger_projparse.info("xm: Number of instruments: " + str(self.num_instruments))
		logger_projparse.info("xm: Flags: " + str(self.flags))
		logger_projparse.info("xm: Speed: " + str(self.speed))
		logger_projparse.info("xm: BPM: " + str(self.bpm))

		self.l_order = ebrw_readstr.list_int_u8(self.length)
		logger_projparse.info("xm: Order: " + str(self.l_order))

		findpat = ebrw_readstr.tell()
		calc_pos = xm_headersize+xm_headersize_pos-4

		self.extra_data = ebrw_readstr.raw(calc_pos-findpat)

		self.patterns = [xm_pattern() for n in range(self.num_patterns)]
		for n, p in enumerate(self.patterns): p.read(ebrw_readstr, n, self.num_channels)
		self.instruments = [xm_instrument() for n in range(self.num_instruments)]
		for n, s in enumerate(self.instruments): s.read(ebrw_readstr, n)

		endd = 0
		for part_obj in chunked.chunk_part_read_all_iso(ebrw_readstr, None):
			if chunk_obj.id == b'CNAM': 
				self.ompt_cnam = ebrw_readstr.l_string(chunk_obj.size//20, 20)
				print('[xm] Channel Names:',self.ompt_cnam)
			elif chunk_obj.id == b'PNAM': 
				self.ompt_pnam = ebrw_readstr.l_string(chunk_obj.size//32, 32)
				print('[xm] Pattern Names:',self.ompt_pnam)
			elif chunk_obj.id == b'CHFX': 
				self.ompt_chfx = ebrw_readstr.list_int_s32(chunk_obj.size//4)
				print('[xm] Channel FX:',self.ompt_chfx)
			#elif chunk_obj.id[0:2] == b'FX':
			#	plugnum = int(chunk_obj.id[2:4].decode())+1
			#	plug_obj = openmpt_plugin.openmpt_plugin()
			#	plug_obj.read(ebrw_readstr)
			#	print('[xm] '+chunk_obj.id.decode()+':',plug_obj.type.decode())
			#	self.plugins[plugnum] = plug_obj
			else: 
				break
			endd = ebrw_readstr.tell()

		ebrw_readstr.seek(endd)

		return True

		#if ebrw_readstr.raw(4) == b'STPM':
		#	if ebrw_readstr.tell()<ebrw_readstr.end:
		#		main_iff_obj = ebrw_readstr.chunk_objmake()
		#		main_iff_obj.set_sizes(4, 2, False)
		#		for chunk_obj in main_iff_obj.iter(ebrw_readstr.tell(), ebrw_readstr.end):

		#			print(chunk_obj.id)

		#			if chunk_obj.id == b'CCOL': self.ompt_ccol = ebrw_readstr.table8([chunk_obj.size//4, 4])
		#			if chunk_obj.id == b'AUTH': self.ompt_artist = ebrw_readstr.string(chunk_obj.size)
