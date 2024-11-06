# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import struct
import zlib
from functions import data_bytes
from objects.data_bytes import bytereader
from objects.inst_params import fm_opn2
from objects.inst_params import chip_sid
from objects.exceptions import ProjectFileParserException

import logging
logger_projparse = logging.getLogger('projparse')

class deflemask_envelope:
	def __init__(self):
		self.values = []
		self.looppos = 0

	def readenv(self, bio_dmf):
		env_size = bio_dmf.uint8()
		self.values = bio_dmf.l_uint32(env_size)
		if env_size != 0: self.looppos = bio_dmf.int8()

class deflemask_instrument:
	def __init__(self, bio_dmf, system):
		self.name = bio_dmf.c_string__int8()
		self.mode = bio_dmf.uint8()
		self.fm_data = fm_opn2.opn2_inst()
		self.sid_data = chip_sid.sid_inst()
		self.sid_data.num_oscs = 1
		self.arpeggio_mode = 0
		self.sound_length = 0
		self.env_volume = deflemask_envelope()
		self.env_arpeggio = deflemask_envelope()
		self.env_duty = deflemask_envelope()
		self.env_wavetable = deflemask_envelope()

		self.gb_env_volume = 0
		self.gb_env_direction = 0
		self.gb_env_length = 0
		self.sound_length = 0

		if self.mode == 1:
			self.fm_data.algorithm = bio_dmf.uint8()
			self.fm_data.feedback = bio_dmf.uint8()
			self.fm_data.fms = bio_dmf.uint8() #(FMS on YM2612, PMS on YM2151)
			self.fm_data.ams = bio_dmf.uint8() #(AMS on YM2612, AMS on YM2151)
			for opnum in [0,2,1,3]:
				op_obj = self.fm_data.ops[opnum]
				op_obj.am = bio_dmf.uint8()
				op_obj.env_attack = bio_dmf.uint8()
				op_obj.env_decay = bio_dmf.uint8()
				op_obj.freqmul = bio_dmf.uint8()
				op_obj.env_release = bio_dmf.uint8()
				op_obj.env_sustain = bio_dmf.uint8()
				op_obj.level = (bio_dmf.uint8()*-1)+127
				op_obj.detune2 = bio_dmf.uint8()
				op_obj.ratescale = bio_dmf.uint8()
				op_obj.detune = bio_dmf.uint8()
				op_obj.env_decay2 = bio_dmf.uint8()
				op_obj.ssg_byte(bio_dmf.uint8())
		else:
			if system != int("04",16): self.env_volume.readenv(bio_dmf)
			self.env_arpeggio.readenv(bio_dmf)
			self.arpeggio_mode = bio_dmf.uint8()
			self.env_duty.readenv(bio_dmf)
			self.env_wavetable.readenv(bio_dmf)
			if system == int("07",16) or system == int("47",16):
				op_obj = self.sid_data.ops[0]
				op_obj.wave_triangle = bio_dmf.uint8()
				op_obj.wave_saw = bio_dmf.uint8()
				op_obj.wave_pulse = bio_dmf.uint8()
				op_obj.wave_noise = bio_dmf.uint8()
				op_obj.attack = bio_dmf.uint8()
				op_obj.decay = bio_dmf.uint8()
				op_obj.sustain = bio_dmf.uint8()
				op_obj.release = bio_dmf.uint8()
				op_obj.pulse_width = bio_dmf.uint8()
				op_obj.ringmod = bio_dmf.uint8()
				op_obj.syncmod = bio_dmf.uint8()
				op_obj.to_filter = bio_dmf.uint8()
				op_obj.volume_macro_to_filter_cutoff = bio_dmf.uint8()
				op_obj.use_filter_values_from_instrument = bio_dmf.uint8()
				op_obj.filter_resonance = bio_dmf.uint8()
				op_obj.filter_cutoff = bio_dmf.uint8()
				op_obj.filter_highpass = bio_dmf.uint8()
				op_obj.filter_lowpass = bio_dmf.uint8()
				op_obj.filter_CH2off = bio_dmf.uint8()
			if system == int("04",16):
				self.gb_env_volume = bio_dmf.uint8()
				self.gb_env_direction = bio_dmf.uint8()
				self.gb_env_length = bio_dmf.uint8()
				self.sound_length = bio_dmf.uint8()

class deflemask_channel:
	def __init__(self, i_type):
		self.type = i_type
		self.visname = None
		self.patterns = {}
		self.orders = []

class deflemask_project:
	def __init__(self):
		self.version = None
		self.system = 0
		self.chantype = []
		self.channames = []
		self.total_channels = 0

		self.song_name = ''
		self.song_author = ''
		self.highlight_a_pat = 0
		self.highlight_b_pat = 0

		self.timebase = 0
		self.ticktime1 = 0
		self.ticktime2 = 0
		self.frames_mode = 0
		self.custom_hz_using = 0
		self.custom_hz_1 = 0
		self.custom_hz_2 = 0
		self.custom_hz_3 = 0
		self.total_rows_per_pattern = 0
		self.total_rows_in_pattern_matrix = 0
		self.insts = []
		self.wavetables = []
		self.patterns = {}
		self.samples = []

	def load_from_file(self, input_file):
		bytestream = open(input_file, 'rb')

		bio_dmf = bytereader.bytereader()
		try:
			decompdata = zlib.decompress(bytestream.read())
		except zlib.error as t:
			raise ProjectFileParserException('deflemask: '+str(t))
		bio_dmf.load_raw(decompdata)
		bio_dmf.magic_check(b'.DelekDefleMask.')
		self.version = bio_dmf.uint8()

		if self.version != 24:
			raise ProjectFileParserException('deflemask: only version 24 is supported.')

		self.system = bio_dmf.uint8()

		# SYSTEM SET
		if self.system == int("02",16): #GENESIS
			self.chantype = ['opn2','opn2','opn2','opn2','opn2','opn2','square','square','square','noise']
			self.channames = ['FM 1','FM 2','FM 3','FM 4','FM 5','FM 6','Square 1','Square 2','Square 3','Noise']
		if self.system == int("42",16): #SYSTEM_GENESIS (mode EXT. CH3) 
			self.chantype = ['opn2','opn2','opn2-op','opn2-op','opn2-op','opn2-op','opn2','opn2','opn2','square','square','square','noise']
			self.channames = ['FM 1','FM 2','FM 3 OP 1','FM 3 OP 2','FM 3 OP 3','FM 3 OP 4','FM 4','FM 5','FM 6','Square 1','Square 2','Square 3','Noise']
		if self.system == int("03",16): #SMS
			self.chantype = ['square','square','square','noise']
			self.channames = ['Square 1','Square 2','Square 3','Noise']
		if self.system == int("04",16): #GAMEBOY
			self.chantype = ['gameboy_pulse','gameboy_pulse','gameboy_wavetable','gameboy_noise']
			self.channames = ['Pulse 1','Pulse 2','Wavetable','Noise']
		if self.system == int("05",16): #PCENGINE
			self.chantype = ['pce','pce','pce','pce','pce','pce']
			self.channames = ['Channel 1','Channel 2','Channel 3','Channel 4','Channel 5','Channel 6']
		if self.system == int("06",16): #NES
			self.chantype = ['pulse','pulse','triangle','noise','pcm']
			self.channames = ['Pulse 1','Pulse 2','Triangle','Noise','PCM']
		if self.system == int("07",16): #C64 (SID 8580)
			self.chantype = ['c64','c64','c64']
			self.channames = ['Channel 1','Channel 2','Channel 3']
		if self.system == int("47",16): #C64 (mode SID 6581)
			self.chantype = ['c64','c64','c64']
			self.channames = ['Channel 1','Channel 2','Channel 3']
		if self.system == int("08",16): #ARCADE
			self.chantype = ['opn2','opn2','opn2','opn2','opn2','opn2','opn2','opn2','sample','sample','sample','sample','sample']
			self.channames = ['FM 1','FM 2','FM 3','FM 4','FM 5','FM 6','FM 7','FM 8','Channel 1','Channel 2','Channel 3','Channel 4','Channel 5']
		if self.system == int("09",16): #NEOGEO
			self.chantype = ['opn2','opn2','opn2','opn2','psg','psg','psg','adpcma','adpcma','adpcma','adpcma','adpcma','adpcma']
			self.channames = ['FM 1','FM 2','FM 3','FM 4','PSG 1','PSG 2','PSG 3','ADPCM-A 1','ADPCM-A 2','ADPCM-A 3','ADPCM-A 4','ADPCM-A 5','ADPCM-A 6']
		if self.system == int("49",16): #NEOGEO (mode EXT. CH2)
			self.chantype = ['opn2','opn2','opn2_op','opn2_op','opn2_op','opn2_op','opn2','psg','psg','psg','adpcma','adpcma','adpcma','adpcma','adpcma','adpcma']
			self.channames = ['FM 1','FM 2 OP 1','FM 2 OP 2','FM 2 OP 3','FM 2 OP 4','FM 3','FM 4','PSG 1','PSG 2','PSG 3','ADPCM-A 1','ADPCM-A 2','ADPCM-A 3','ADPCM-A 4','ADPCM-A 5','ADPCM-A 6']

		self.channels = []
		for n, x in enumerate(self.chantype):
			chan_obj = deflemask_channel(x)
			chan_obj.visname = self.channames[n]
			self.channels.append(chan_obj)

		self.total_channels = len(self.channels)

		# VISUAL INFORMATION
		self.song_name = bio_dmf.c_string__int8()
		self.song_author = bio_dmf.c_string__int8()
		self.highlight_a_pat = bio_dmf.uint8()
		self.highlight_b_pat = bio_dmf.uint8()

		# MODULE INFORMATION
		self.timebase = bio_dmf.uint8()
		self.ticktime1 = bio_dmf.uint8()
		self.ticktime2 = bio_dmf.uint8()
		self.frames_mode = bio_dmf.uint8()
		self.custom_hz_using = bio_dmf.uint8()
		self.custom_hz_1 = bio_dmf.uint8()
		self.custom_hz_2 = bio_dmf.uint8()
		self.custom_hz_3 = bio_dmf.uint8()
		self.total_rows_per_pattern = bio_dmf.uint32()
		self.total_rows_in_pattern_matrix = bio_dmf.uint8()

		self.pat_orders = []
		for c in self.channels: c.orders = bio_dmf.l_uint8(self.total_rows_in_pattern_matrix)

		num_insts = bio_dmf.uint8()
		self.insts = [deflemask_instrument(bio_dmf, self.system) for _ in range(num_insts)]

		self.wavetables = []
		for _ in range(bio_dmf.uint8()):
			wavesize = bio_dmf.uint32()
			self.wavetables.append(bio_dmf.l_uint32(wavesize))
 
		for num, chan_obj in enumerate(self.channels):
			fx_columns_count = bio_dmf.uint8()
			for patnum in chan_obj.orders:
				table_rows = []
				for rownum in range(self.total_rows_per_pattern):
					r_note = bio_dmf.uint16()
					r_oct = bio_dmf.uint16()
					r_vol = bio_dmf.int16()
					r_fx = [bio_dmf.l_int16(2) for _ in range(fx_columns_count)]
					r_inst = bio_dmf.int16()
					table_rows.append([r_note, r_oct, r_vol, r_inst, r_fx])
				chan_obj.patterns[patnum] = table_rows

		num_samples = bio_dmf.uint8()

		for _ in range(num_samples):
			sample_obj = deflemask_sample()
			sample_obj.size = bio_dmf.uint32()
			sample_obj.name = bio_dmf.c_string__int8()
			sample_obj.rate = bio_dmf.uint8()
			sample_obj.pitch = bio_dmf.uint8()
			sample_obj.amp = bio_dmf.uint8()
			sample_obj.bits = bio_dmf.uint8()
			if sample_obj.bits == 16: sample_obj.data = bio_dmf.l_int16(sample_obj.size)
			if sample_obj.bits == 8: sample_obj.data = bio_dmf.l_int8(sample_obj.size)
			self.samples.append(sample_obj)

		return True

class deflemask_sample:
	def __init__(self):
		self.size = 0
		self.name = 0
		self.rate = 0
		self.pitch = 0
		self.amp = 0
		self.bits = 0
		self.data = []
