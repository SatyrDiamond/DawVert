# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import struct
from external.easybinrw import easybinrw
from objects.inst_params import openmpt_plugin
from objects.exceptions import ProjectFileParserException

import logging
logger_projparse = logging.getLogger('projparse')

# ============================================= instrument ============================================= 

class it_env:
	def __init__(self): 
		self.flags = []
		self.env_numpoints = 2
		self.loop_start = 0
		self.loop_end = 0
		self.susloop_start = 0
		self.susloop_end = 0
		self.env_points = []

	def read(self, ebrw_readstr): 
		self.flags = ebrw_readstr.flags_i8()
		self.env_numpoints = ebrw_readstr.int_u8()
		self.loop_start = ebrw_readstr.int_u8()
		self.loop_end = ebrw_readstr.int_u8()
		self.susloop_start = ebrw_readstr.int_u8()
		self.susloop_end = ebrw_readstr.int_u8()

		self.env_points = [[ebrw_readstr.int_s8(), ebrw_readstr.int_u16()] for _ in range(self.env_numpoints)]
		ebrw_readstr.raw(76-(self.env_numpoints*3))

	def ext_ticks_pos(self, i_input):
		unpacked = struct.unpack('H'*(self.env_numpoints), i_input[0:self.env_numpoints*2])
		if self.env_numpoints != len(self.env_points): self.env_points = [[p, 0] for p in unpacked]
		else: 
			for c, v in enumerate(unpacked): self.env_points[c][0] = v

	def ext_ticks_val(self, i_input):
		unpacked = struct.unpack('B'*(self.env_numpoints), i_input[0:self.env_numpoints])
		if self.env_numpoints != len(self.env_points): self.env_points = [[0, v] for v in unpacked]
		else: 
			for c, v in enumerate(unpacked): self.env_points[c][1] = v

class it_sample:
	def __init__(self):
		self.dosfilename = ''
		self.globalvol = 64
		self.flags = []
		self.defualtvolume = 64
		self.name = ''
		self.length = 0
		self.loop_start = 0
		self.loop_end = 0
		self.C5_speed = 8363
		self.susloop_start = 0
		self.susloop_end = 0
		self.sample_pointer = 0
		self.vibrato_speed = 0
		self.vibrato_depth = 0
		self.vibrato_sweep = 0
		self.vibrato_wave = 0
		self.resampling = -1

	def read(self, ebrw_readstr, ptr, num): 
		logger_projparse.info("IT: Sample " + str(num) + ': at offset ' + str(ptr))
		ebrw_readstr.seek(ptr)
		ebrw_readstr.magic_check(b'IMPS')
		self.dosfilename = ebrw_readstr.string(12, encoding="cp437")
		ebrw_readstr.skip(1)
		self.globalvol = ebrw_readstr.int_u8()
		self.flags = ebrw_readstr.flags_i8()
		self.defualtvolume = ebrw_readstr.int_u8()
		self.name = ebrw_readstr.string(26, encoding="cp437")
		ebrw_readstr.skip(2)
		self.length = ebrw_readstr.int_u32()
		self.loop_start = ebrw_readstr.int_u32()
		self.loop_end = ebrw_readstr.int_u32()
		self.C5_speed = ebrw_readstr.int_u32()
		self.susloop_start = ebrw_readstr.int_u32()
		self.susloop_end = ebrw_readstr.int_u32()
		self.sample_pointer = ebrw_readstr.int_u32()
		self.vibrato_speed = ebrw_readstr.int_u8()
		self.vibrato_depth = ebrw_readstr.int_u8()
		self.vibrato_sweep = ebrw_readstr.int_u8()
		self.vibrato_wave = ebrw_readstr.int_u8()

	def vibrato_lfo(self):
		vibrato_on = self.vibrato_sweep != 0 and self.vibrato_speed != 0
		vibrato_wave = ['sine','saw','square','random'][self.vibrato_wave&3]
		vibrato_depth = self.vibrato_depth/64
		if vibrato_on:
			vibrato_speed = 1/((256/self.vibrato_speed)/100)
			vibrato_sweep = (8192/self.vibrato_sweep)/50
		else:
			vibrato_speed = 1
			vibrato_sweep = 0
		return vibrato_on, vibrato_sweep, vibrato_wave, vibrato_speed, vibrato_depth

class it_instrument:
	def __init__(self): 
		self.dosfilename = ''
		self.new_note_action = 0
		self.duplicate_check_type = 0
		self.duplicate_check_action = 0
		self.fadeout = 4
		self.pitch_pan_separation = 0
		self.pitch_pan_center = 60
		self.global_vol = 128
		self.default_pan = 160
		self.randomvariation_volume = 0
		self.randomvariation_pan = 0
		self.cwtv = 20784
		self.num_samples = 0

		self.name = ''
		self.filtercutoff = 0
		self.filterresonance = 0
		self.midi_chan = 0
		self.midi_inst = 30
		self.midi_bank = 65535
		self.notesampletable = [[0,0] for _ in range(120)]

		self.env_vol = it_env()
		self.env_pan = it_env()
		self.env_pitch = it_env()

		self.ramping = 0
		self.resampling = -1

		self.randomvariation_cutoff = 0
		self.randomvariation_reso = 0
		self.filtermode = 255
		self.pluginnum = 0

	def read(self, ebrw_readstr, ptr, num): 
		logger_projparse.info("IT: Instrument " + str(num) + ": at offset " + str(ptr))
		ebrw_readstr.seek(ptr)
		ebrw_readstr.magic_check(b'IMPI')

		self.dosfilename = ebrw_readstr.string(12, encoding="cp437")
		ebrw_readstr.skip(1)
		self.new_note_action = ebrw_readstr.int_u8()
		self.duplicate_check_type = ebrw_readstr.int_u8()
		self.duplicate_check_action = ebrw_readstr.int_u8()
		self.fadeout = ebrw_readstr.int_u16()
		self.pitch_pan_separation = ebrw_readstr.int_u8()
		self.pitch_pan_center = ebrw_readstr.int_u8()
		self.global_vol = ebrw_readstr.int_u8()
		self.default_pan = ebrw_readstr.int_u8()
		self.randomvariation_volume = ebrw_readstr.int_u8()
		self.randomvariation_pan = ebrw_readstr.int_u8()
		self.cwtv = ebrw_readstr.int_u16()
		self.num_samples = ebrw_readstr.int_u8()

		ebrw_readstr.skip(1)
		self.name = ebrw_readstr.string(26, encoding="cp437")
		self.filtercutoff = ebrw_readstr.int_u8()
		self.filterresonance = ebrw_readstr.int_u8()
		self.midi_chan = ebrw_readstr.int_u8()
		self.midi_inst = ebrw_readstr.int_u8()
		self.midi_bank = ebrw_readstr.int_u16()

		self.notesampletable = [ebrw_readstr.list_int_u8(2) for _ in range(120)]

		self.env_vol.read(ebrw_readstr)
		self.env_pan.read(ebrw_readstr)
		self.env_pitch.read(ebrw_readstr)

# ============================================= song ============================================= 

class it_pattern:
	def __init__(self): 
		self.used = False

	def read(self, ebrw_readstr, ptr, num):
		logger_projparse.info("IT: Pattern " + str(num))
		self.data = []
		self.used = False
		self.length = 0
		self.rows = 64

		if ptr != 0:
			self.used = True
			ebrw_readstr.seek(ptr)
			self.length = ebrw_readstr.int_u16()
			self.rows = ebrw_readstr.int_u16()

			logger_projparse.info("IT: Pattern Rows: " + str(self.rows))
			logger_projparse.info('IT: Pattern Size: ' + str(self.length) + ' at offset ' + str(ptr))

			ebrw_readstr.skip(4)
			t_lastnote = [None for _ in range(127)]
			t_lastinstrument = [None for _ in range(127)]
			t_lastvolpan = [None for _ in range(127)]
			t_lastcommand = [[None, None] for _ in range(127)]
			t_previousmaskvariable = [[] for _ in range(127)]
			for rownum in range(self.rows):
				rowdata = []
				pattern_done = 0
				while pattern_done == 0:
					chanp = ebrw_readstr.int_u8()
					cell_previous_maskvariable = bool(chanp&128)
					cell_channel = chanp&127
					if not cell_channel: 
						pattern_done = 1
					else:
						if cell_previous_maskvariable == 1: t_previousmaskvariable[cell_channel] = maskvariable = ebrw_readstr.flags_i8()
						else: 
							if cell_channel<len(t_previousmaskvariable):
								maskvariable = t_previousmaskvariable[cell_channel]
	
						cell_note = None
						cell_instrument = None
						cell_volpan = None
						cell_commandtype = None
						cell_commandval = None
	
						if 0 in maskvariable:
							cell_note = ebrw_readstr.int_u8()
							if cell_channel<len(t_lastnote):
								t_lastnote[cell_channel] = cell_note
						if 1 in maskvariable:
							cell_instrument = ebrw_readstr.int_u8()
							t_lastinstrument[cell_channel] = cell_instrument
						if 2 in maskvariable:
							cell_volpan = ebrw_readstr.int_u8()
							t_lastvolpan[cell_channel] = cell_volpan
						if 3 in maskvariable:
							cell_commandtype = ebrw_readstr.int_u8()
							cell_commandval = ebrw_readstr.int_u8()
							if cell_channel<len(t_lastcommand):
								t_lastcommand[cell_channel] = [cell_commandtype, cell_commandval]
	
						if 4 in maskvariable and cell_channel<len(t_lastnote): cell_note = t_lastnote[cell_channel]
						if 5 in maskvariable and cell_channel<len(t_lastinstrument): cell_instrument = t_lastinstrument[cell_channel]
						if 6 in maskvariable and cell_channel<len(t_lastvolpan): cell_volpan = t_lastvolpan[cell_channel]
						if 7 in maskvariable:
							cell_commandtype = t_lastcommand[cell_channel][0]
							cell_commandval = t_lastcommand[cell_channel][1]
	
						rowdata.append([cell_channel, cell_note, cell_instrument, cell_volpan, cell_commandtype, cell_commandval])
				self.data.append(rowdata)

class it_song:
	def __init__(self):
		self.title = ''
		self.hilight_minor = 4
		self.hilight_major = 16
		self.num_orders = 0
		self.num_instruments = 0
		self.num_samples = 0
		self.num_patterns = 0
		self.cwtv = [3, 0, 5, 1]
		self.cmwt = '\x14\x02'
		self.flags = [0]
		self.special = 14
		self.globalvol = 128
		self.mv = 48
		self.speed = 6
		self.tempo = 120

		self.sep = 128
		self.pwd = 0
		self.msgoffset = 0
		self.reserved = 1414548815

		self.l_chnpan = []
		self.l_chnvol = []
		self.l_order = []

		self.ompt_cnam = None
		self.ompt_pnam = None
		self.ompt_chfx = None
		self.plugins = {}

		self.instruments = []
		self.samples = []
		self.patterns = []

		self.songmessage = ''

	def load_from_raw(self, raw_data):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_raw(raw_data)
		
		try: 
			self.load(ebrw_readstr)
			return True
		except ValueError as t:
			raise ProjectFileParserException('IT: '+str(t))

	def load_from_file(self, input_file):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_file(input_file)
		
		try: 
			self.load(ebrw_readstr)
			return True
		except ValueError as t:
			raise ProjectFileParserException('IT: '+str(t))

	def load(self, ebrw_readstr):
		ebrw_readstr.magic_check(b'IMPM')

		self.title = ebrw_readstr.string(26, encoding="cp437")
		logger_projparse.info("IT: Song Name: " + str(self.title))

		self.hilight_minor = ebrw_readstr.int_u8()
		self.hilight_major = ebrw_readstr.int_u8()
		self.num_orders = ebrw_readstr.int_u16()
		self.num_instruments = ebrw_readstr.int_u16()
		self.num_samples = ebrw_readstr.int_u16()
		self.num_patterns = ebrw_readstr.int_u16()
		logger_projparse.info("IT: # of Orders: " + str(self.num_orders))
		logger_projparse.info("IT: # of Instruments: " + str(self.num_instruments))
		logger_projparse.info("IT: # of Samples: " + str(self.num_samples))
		logger_projparse.info("IT: # of Patterns: " + str(self.num_patterns))
		self.cwtv = ebrw_readstr.list_int_u4(2)
		logger_projparse.info("IT: Cwt/v: " + str(self.cwtv))
		self.cmwt = ebrw_readstr.raw(2)
		self.flags = ebrw_readstr.flags_i16()
		self.special = ebrw_readstr.int_u16()
		self.globalvol = ebrw_readstr.int_u8()
		self.mv = ebrw_readstr.int_u8()
		self.speed = ebrw_readstr.int_u8()
		self.tempo = ebrw_readstr.int_u8()

		logger_projparse.info("IT: Speed: " + str(self.speed))
		logger_projparse.info("IT: Tempo: " + str(self.tempo))
		self.sep = ebrw_readstr.int_u8()
		self.pwd = ebrw_readstr.int_u8()
		msglength = ebrw_readstr.int_u16()
		self.msgoffset = ebrw_readstr.int_u32()
		self.reserved = ebrw_readstr.int_u32()

		self.l_chnpan = ebrw_readstr.list_int_s8(64)
		self.l_chnvol = ebrw_readstr.list_int_s8(64)

		self.l_order = ebrw_readstr.list_int_s8(self.num_orders)
		logger_projparse.info("IT: Order List: " + str(self.l_order))
		ptrs_insts = ebrw_readstr.list_int_s32(self.num_instruments)
		ptrs_samples = ebrw_readstr.list_int_s32(self.num_samples)
		ptrs_patterns = ebrw_readstr.list_int_s32(self.num_patterns)

		ptrall = ptrs_insts.tolist()+ptrs_samples.tolist()+ptrs_patterns.tolist()

		#if ptrall:
		#	ebrw_readstr.skip(10)
		#	main_iff_obj = ebrw_readstr.chunk_objmake()
		#	for chunk_obj in main_iff_obj.iter(ebrw_readstr.tell(), max(ptrall)):
		#		if chunk_obj.id == b'CNAM': 
		#			self.ompt_cnam = ebrw_readstr.l_string(chunk_obj.size//20, 20)
		#			logger_projparse.info('IT: Channel Names:'+str(self.ompt_cnam))
		#		elif chunk_obj.id == b'PNAM': 
		#			self.ompt_pnam = ebrw_readstr.l_string(chunk_obj.size//32, 32)
		#			logger_projparse.info('IT: Pattern Names:'+str(self.ompt_pnam))
		#		elif chunk_obj.id == b'CHFX': 
		#			self.ompt_chfx = ebrw_readstr.list_int_s32(chunk_obj.size//4)
		#			logger_projparse.info('IT: Channel FX:'+str(self.ompt_chfx))
		#		elif chunk_obj.id[0:2] == b'FX':
		#			plugnum = int(chunk_obj.id[2:4].decode())+1
		#			plug_obj = openmpt_plugin.openmpt_plugin()
		#			plug_obj.read(ebrw_readstr)
		#			logger_projparse.info('IT: '+chunk_obj.id.decode()+':',plug_obj.type.decode())
		#			self.plugins[plugnum] = plug_obj
		#		else: 
		#			#print(chunk_obj.id)
		#			break

		self.instruments = [it_instrument() for _ in range(self.num_instruments)]
		self.samples = [it_sample() for _ in range(self.num_samples)]
		self.patterns = [it_pattern() for _ in range(self.num_patterns)]

		for n, x in enumerate(ptrs_insts):
			self.instruments[n].read(ebrw_readstr, x, n)
		for n, x in enumerate(ptrs_samples):
			self.samples[n].read(ebrw_readstr, x, n)
		for n, x in enumerate(ptrs_patterns):
			self.patterns[n].read(ebrw_readstr, x, n)

		ebrw_readstr.seek(self.msgoffset)
		self.songmessage = ebrw_readstr.string(msglength, encoding='windows-1252')
 