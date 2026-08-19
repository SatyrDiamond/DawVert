# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import struct
from external.easybinrw import easybinrw
from objects.inst_params import openmpt_plugin
from objects.exceptions import ProjectFileParserException
from objects.file_proj_tracker._it import samplecomp as it214
from objects import audio_data
import numpy as np

import logging
logger_projparse = logging.getLogger('projparse')

# ============================================= instrument ============================================= 

class it_env:
	def __init__(self, ebrw_readstr): 
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
	def __init__(self, ebrw_readstr, ptr, num): 
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
		self.resampling = -1
		self.ebrw_readstr = ebrw_readstr

	def rip_sample(self, samplefolder, wave_path):
		ebrw_readstr = self.ebrw_readstr
		compressed = 3 in self.flags
		stereo = 2 in self.flags
		double = 1 in self.flags
		samp_len = self.length

		audio_obj = audio_data.audio_obj()
		audio_obj.rate = self.C5_speed
		audio_obj.channels = 2 if stereo else 1

		datasize_schan = samp_len*(double+1)

		outdata = None

		ebrw_readstr.seek(self.sample_pointer)
		if compressed:
			remlen = samp_len
			xdata = []

			while remlen > 0:
				blkcomplen = ebrw_readstr.int_u16()
				data = ebrw_readstr.raw(blkcomplen)
				decomp = it214.IT214Decompressor(data, remlen, double)
				xdata += decomp.get_data()
				blkdecomplen = decomp.get_length()
				remlen -= blkdecomplen

			outd = np.zeros(samp_len, dtype=(np.uint16 if double else np.uint8))
			outd[0:len(xdata)] = xdata
			ebrw_readstr = easybinrw.binread()
			ebrw_readstr.load_data(outd.tobytes())

		if double == 0:
			audio_obj.set_codec('int8')
			if not stereo: 
				outdata = np.zeros(samp_len, dtype=np.uint8)
				outdata[:samp_len] = np.frombuffer(ebrw_readstr.read(datasize_schan), dtype=np.uint8)
			else:
				outdata = np.zeros(samp_len*2, dtype=np.uint8)
				outdata[:samp_len*2][0::2] = np.frombuffer(ebrw_readstr.raw(datasize_schan), dtype=np.uint8)
				outdata[:samp_len*2][1::2] = np.frombuffer(ebrw_readstr.raw(datasize_schan), dtype=np.uint8)
		else: 
			audio_obj.set_codec('int16')
			if not stereo: 
				outdata = np.zeros(samp_len, dtype=np.uint16)
				outdata[:samp_len] = np.frombuffer(ebrw_readstr.read(datasize_schan), dtype=np.uint16)
			else:
				outdata = np.zeros(samp_len*2, dtype=np.uint16)
				outdata[:samp_len*2][0::2] = np.frombuffer(ebrw_readstr.raw(datasize_schan), dtype=np.uint16)
				outdata[:samp_len*2][1::2] = np.frombuffer(ebrw_readstr.raw(datasize_schan), dtype=np.uint16)

		if outdata is not None: 
			audio_obj.pcm_from_list(outdata)
			if 4 in self.flags: audio_obj.loop = [self.loop_start, self.loop_end-1]

		audio_obj.to_file_wav(wave_path)

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
	def __init__(self, ebrw_readstr, ptr, num): 
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

		self.env_vol = it_env(ebrw_readstr)
		self.env_pan = it_env(ebrw_readstr)
		self.env_pitch = it_env(ebrw_readstr)

		self.ramping = 0
		self.resampling = -1

		self.randomvariation_cutoff = 0
		self.randomvariation_reso = 0
		self.filtermode = 255
		self.pluginnum = 0

# ============================================= song ============================================= 

class it_pattern:
	def __init__(self, ebrw_readstr, ptr, num):
		logger_projparse.info("IT: Pattern " + str(num))
		self.data = []
		self.used = False

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
		self.num_order = 0
		self.num_instruments = 0
		self.num_samples = 0
		self.num_patterns = 0

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
		self.msglength = ebrw_readstr.int_u16()
		self.msgoffset = ebrw_readstr.int_u32()
		self.reserved = ebrw_readstr.int_u32()

		self.l_chnpan = ebrw_readstr.list_int_s8(64)
		self.l_chnvol = ebrw_readstr.list_int_s8(64)

		self.l_order = ebrw_readstr.list_int_s8(self.num_orders)
		logger_projparse.info("IT: Order List: " + str(self.l_order))
		self.ptrs_insts = ebrw_readstr.list_int_s32(self.num_instruments)
		self.ptrs_samples = ebrw_readstr.list_int_s32(self.num_samples)
		self.ptrs_patterns = ebrw_readstr.list_int_s32(self.num_patterns)

		ptrall = self.ptrs_insts.tolist()+self.ptrs_samples.tolist()+self.ptrs_patterns.tolist()

		self.ompt_cnam = None
		self.ompt_pnam = None
		self.ompt_chfx = None
		self.plugins = {}

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

		self.instruments = [it_instrument(ebrw_readstr, x, n) for n, x in enumerate(self.ptrs_insts)]
		self.samples = [it_sample(ebrw_readstr, x, n) for n, x in enumerate(self.ptrs_samples)]
		self.patterns = [it_pattern(ebrw_readstr, x, n) for n, x in enumerate(self.ptrs_patterns)]

		ebrw_readstr.seek(self.msgoffset)
		self.songmessage = ebrw_readstr.string(self.msglength, encoding='windows-1252')
 