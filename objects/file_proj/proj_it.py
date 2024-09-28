# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import struct
from objects.data_bytes import bytereader
from objects import openmpt_plugin
from objects.exceptions import ProjectFileParserException

import logging
logger_projparse = logging.getLogger('projparse')

class it_env:
	def __init__(self, song_file): 
		self.flags = song_file.flags8()
		self.env_numpoints = song_file.uint8()
		self.loop_start = song_file.uint8()
		self.loop_end = song_file.uint8()
		self.susloop_start = song_file.uint8()
		self.susloop_end = song_file.uint8()

		self.env_points = [[song_file.int8(), song_file.uint16()] for _ in range(self.env_numpoints)]
		song_file.raw(76-(self.env_numpoints*3))

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
	def __init__(self, song_file, ptr, num): 
		logger_projparse.info("IT: Sample " + str(num) + ': at offset ' + str(ptr))
		song_file.seek(ptr)
		song_file.magic_check(b'IMPS')
		self.dosfilename = song_file.string(12, encoding="cp437")
		song_file.skip(1)
		self.globalvol = song_file.uint8()
		self.flags = song_file.flags8()
		self.defualtvolume = song_file.uint8()
		self.name = song_file.string(26, encoding="cp437")
		song_file.skip(2)
		self.length = song_file.uint32()
		self.loop_start = song_file.uint32()
		self.loop_end = song_file.uint32()
		self.C5_speed = song_file.uint32()
		self.susloop_start = song_file.uint32()
		self.susloop_end = song_file.uint32()
		self.sample_pointer = song_file.uint32()
		self.vibrato_speed = song_file.uint8()
		self.vibrato_depth = song_file.uint8()
		self.vibrato_sweep = song_file.uint8()
		self.vibrato_wave = song_file.uint8()
		self.resampling = -1

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

class it_pattern:
	def __init__(self, song_file, ptr, num):
		logger_projparse.info("IT: Pattern " + str(num))
		self.data = []
		self.used = False

		if ptr != 0:
			self.used = True
			song_file.seek(ptr)
			self.length = song_file.uint16()
			self.rows = song_file.uint16()

			logger_projparse.info("IT: Pattern Rows: " + str(self.rows))
			logger_projparse.info('IT: Pattern Size: ' + str(self.length) + ' at offset ' + str(ptr))

			song_file.skip(4)
			t_lastnote = [None for _ in range(127)]
			t_lastinstrument = [None for _ in range(127)]
			t_lastvolpan = [None for _ in range(127)]
			t_lastcommand = [[None, None] for _ in range(127)]
			t_previousmaskvariable = [[] for _ in range(127)]
			for rownum in range(self.rows):
				rowdata = []
				pattern_done = 0
				while pattern_done == 0:
					chanp = song_file.uint8()
					cell_previous_maskvariable = bool(chanp&128)
					cell_channel = chanp&127
					if not cell_channel: 
						pattern_done = 1
					else:
						if cell_previous_maskvariable == 1: t_previousmaskvariable[cell_channel] = maskvariable = song_file.flags8()
						else: 
							if cell_channel<len(t_previousmaskvariable):
								maskvariable = t_previousmaskvariable[cell_channel]
	
						cell_note = None
						cell_instrument = None
						cell_volpan = None
						cell_commandtype = None
						cell_commandval = None
	
						if 0 in maskvariable:
							cell_note = song_file.uint8()
							if cell_channel<len(t_lastnote):
								t_lastnote[cell_channel] = cell_note
						if 1 in maskvariable:
							cell_instrument = song_file.uint8()
							t_lastinstrument[cell_channel] = cell_instrument
						if 2 in maskvariable:
							cell_volpan = song_file.uint8()
							t_lastvolpan[cell_channel] = cell_volpan
						if 3 in maskvariable:
							cell_commandtype = song_file.uint8()
							cell_commandval = song_file.uint8()
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

class it_instrument:
	def __init__(self, song_file, ptr, num): 
		logger_projparse.info("IT: Instrument " + str(num) + ": at offset " + str(ptr))
		song_file.seek(ptr)
		song_file.magic_check(b'IMPI')

		self.dosfilename = song_file.string(12, encoding="cp437")
		song_file.skip(1)
		self.new_note_action = song_file.uint8()
		self.duplicate_check_type = song_file.uint8()
		self.duplicate_check_action = song_file.uint8()
		self.fadeout = song_file.uint16()
		self.pitch_pan_separation = song_file.uint8()
		self.pitch_pan_center = song_file.uint8()
		self.global_vol = song_file.uint8()
		self.default_pan = song_file.uint8()
		self.randomvariation_volume = song_file.uint8()
		self.randomvariation_pan = song_file.uint8()
		self.cwtv = song_file.uint16()
		self.num_samples = song_file.uint8()

		song_file.skip(1)
		self.name = song_file.string(26, encoding="cp437")
		self.filtercutoff = song_file.uint8()
		self.filterresonance = song_file.uint8()
		self.midi_chan = song_file.uint8()
		self.midi_inst = song_file.uint8()
		self.midi_bank = song_file.uint16()

		self.notesampletable = [song_file.l_uint8(2) for _ in range(120)]

		self.env_vol = it_env(song_file)
		self.env_pan = it_env(song_file)
		self.env_pitch = it_env(song_file)

		self.ramping = 0
		self.resampling = -1

		self.randomvariation_cutoff = 0
		self.randomvariation_reso = 0
		self.filtermode = 255
		self.pluginnum = 0

class it_song:
	def __init__(self):
		self.title = ''
		self.hilight_minor = 4
		self.hilight_major = 16
		self.num_order = 0
		self.num_instruments = 0
		self.num_samples = 0
		self.num_patterns = 0

	def load_from_raw(self, raw_data):
		song_file = bytereader.bytereader()
		song_file.load_raw(raw_data)
		
		try: 
			self.load(song_file)
			return True
		except ValueError as t:
			raise ProjectFileParserException('IT: '+str(t))

	def load_from_file(self, input_file):
		song_file = bytereader.bytereader()
		song_file.load_file(input_file)
		
		try: 
			self.load(song_file)
			return True
		except ValueError as t:
			raise ProjectFileParserException('IT: '+str(t))

	def load(self, song_file):
		song_file.magic_check(b'IMPM')

		self.title = song_file.string(26, encoding="cp437")
		logger_projparse.info("IT: Song Name: " + str(self.title))

		self.hilight_minor = song_file.uint8()
		self.hilight_major = song_file.uint8()
		self.num_orders = song_file.uint16()
		self.num_instruments = song_file.uint16()
		self.num_samples = song_file.uint16()
		self.num_patterns = song_file.uint16()
		logger_projparse.info("IT: # of Orders: " + str(self.num_orders))
		logger_projparse.info("IT: # of Instruments: " + str(self.num_instruments))
		logger_projparse.info("IT: # of Samples: " + str(self.num_samples))
		logger_projparse.info("IT: # of Patterns: " + str(self.num_patterns))
		self.cwtv = song_file.bytesplit16()
		logger_projparse.info("IT: Cwt/v: " + str(self.cwtv))
		self.cmwt = song_file.raw(2)
		self.flags = song_file.flags16()
		self.special = song_file.uint16()
		self.globalvol = song_file.uint8()
		self.mv = song_file.uint8()
		self.speed = song_file.uint8()
		self.tempo = song_file.uint8()
		logger_projparse.info("IT: Speed: " + str(self.speed))
		logger_projparse.info("IT: Tempo: " + str(self.tempo))
		self.sep = song_file.uint8()
		self.pwd = song_file.uint8()
		self.msglength = song_file.uint16()
		self.msgoffset = song_file.uint32()
		self.reserved = song_file.uint32()

		self.l_chnpan = song_file.l_int8(64)
		self.l_chnvol = song_file.l_int8(64)

		self.l_order = song_file.l_int8(self.num_orders)
		logger_projparse.info("IT: Order List: " + str(self.l_order))
		self.ptrs_insts = song_file.l_int32(self.num_instruments)
		self.ptrs_samples = song_file.l_int32(self.num_samples)
		self.ptrs_patterns = song_file.l_int32(self.num_patterns)

		ptrall = self.ptrs_insts+self.ptrs_samples+self.ptrs_patterns

		self.ompt_cnam = None
		self.ompt_pnam = None
		self.ompt_chfx = None
		self.plugins = {}

		if ptrall:
			song_file.skip(10)
			main_iff_obj = song_file.chunk_objmake()
			for chunk_obj in main_iff_obj.iter(song_file.tell(), max(ptrall)):
				if chunk_obj.id == b'CNAM': 
					self.ompt_cnam = song_file.l_string(chunk_obj.size//20, 20)
					logger_projparse.info('IT: Channel Names:'+str(self.ompt_cnam))
				elif chunk_obj.id == b'PNAM': 
					self.ompt_pnam = song_file.l_string(chunk_obj.size//32, 32)
					logger_projparse.info('IT: Pattern Names:'+str(self.ompt_pnam))
				elif chunk_obj.id == b'CHFX': 
					self.ompt_chfx = song_file.l_int32(chunk_obj.size//4)
					logger_projparse.info('IT: Channel FX:'+str(self.ompt_chfx))
				elif chunk_obj.id[0:2] == b'FX':
					plugnum = int(chunk_obj.id[2:4].decode())+1
					plug_obj = openmpt_plugin.openmpt_plugin()
					plug_obj.read(song_file)
					logger_projparse.info('IT: '+chunk_obj.id.decode()+':',plug_obj.type.decode())
					self.plugins[plugnum] = plug_obj
				else: 
					#print(chunk_obj.id)
					break

		self.instruments = [it_instrument(song_file, x, n) for n, x in enumerate(self.ptrs_insts)]
		self.samples = [it_sample(song_file, x, n) for n, x in enumerate(self.ptrs_samples)]
		self.patterns = [it_pattern(song_file, x, n) for n, x in enumerate(self.ptrs_patterns)]

		song_file.seek(self.msgoffset)
		self.songmessage = song_file.string(self.msglength, encoding='windows-1252')
 