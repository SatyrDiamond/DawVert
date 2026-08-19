# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import struct
import zlib
from functions import data_bytes
from external.easybinrw import easybinrw
from objects.inst_params import fm_opn2
from objects.inst_params import chip_sid
from objects.exceptions import ProjectFileParserException

import logging
logger_projparse = logging.getLogger('projparse')

samplePitches = [
  0.1666666666, 0.2, 0.25, 0.333333333, 0.5,
  1,
  2, 3, 4, 5, 6
]

# ============================================= instrument ============================================= 

class deflemask_envelope:
	def __init__(self):
		self.values = []
		self.looppos = 0

	def readenv(self, ebrw_readstr):
		env_size = ebrw_readstr.int_u8()
		self.values = ebrw_readstr.list_int_u32(env_size)
		if env_size != 0: self.looppos = ebrw_readstr.int_s8()

class deflemask_instrument:
	def __init__(self, ebrw_readstr, system):
		self.name = ebrw_readstr.string_i8()
		self.mode = ebrw_readstr.int_u8()
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
			self.fm_data.algorithm = ebrw_readstr.int_u8()
			self.fm_data.feedback = ebrw_readstr.int_u8()
			self.fm_data.fms = ebrw_readstr.int_u8() #(FMS on YM2612, PMS on YM2151)
			self.fm_data.ams = ebrw_readstr.int_u8() #(AMS on YM2612, AMS on YM2151)
			for opnum in [0,2,1,3]:
				op_obj = self.fm_data.ops[opnum]
				op_obj.am = ebrw_readstr.int_u8()
				op_obj.env_attack = ebrw_readstr.int_u8()
				op_obj.env_decay = ebrw_readstr.int_u8()
				op_obj.freqmul = ebrw_readstr.int_u8()
				op_obj.env_release = ebrw_readstr.int_u8()
				op_obj.env_sustain = ebrw_readstr.int_u8()
				op_obj.level = (ebrw_readstr.int_u8()*-1)+127
				op_obj.detune2 = ebrw_readstr.int_u8()
				op_obj.ratescale = ebrw_readstr.int_u8()
				op_obj.detune = ebrw_readstr.int_u8()
				op_obj.env_decay2 = ebrw_readstr.int_u8()
				op_obj.ssg_byte(ebrw_readstr.int_u8())
		else:
			if system != int("04",16): self.env_volume.readenv(ebrw_readstr)
			self.env_arpeggio.readenv(ebrw_readstr)
			self.arpeggio_mode = ebrw_readstr.int_u8()
			self.env_duty.readenv(ebrw_readstr)
			self.env_wavetable.readenv(ebrw_readstr)
			if system == int("07",16) or system == int("47",16):
				op_obj = self.sid_data.ops[0]
				op_obj.wave_triangle = ebrw_readstr.int_u8()
				op_obj.wave_saw = ebrw_readstr.int_u8()
				op_obj.wave_pulse = ebrw_readstr.int_u8()
				op_obj.wave_noise = ebrw_readstr.int_u8()
				op_obj.attack = ebrw_readstr.int_u8()
				op_obj.decay = ebrw_readstr.int_u8()
				op_obj.sustain = ebrw_readstr.int_u8()
				op_obj.release = ebrw_readstr.int_u8()
				op_obj.pulse_width = ebrw_readstr.int_u8()
				op_obj.ringmod = ebrw_readstr.int_u8()
				op_obj.syncmod = ebrw_readstr.int_u8()
				op_obj.to_filter = ebrw_readstr.int_u8()
				op_obj.volume_macro_to_filter_cutoff = ebrw_readstr.int_u8()
				op_obj.use_filter_values_from_instrument = ebrw_readstr.int_u8()
				op_obj.filter_resonance = ebrw_readstr.int_u8()
				op_obj.filter_cutoff = ebrw_readstr.int_u8()
				op_obj.filter_highpass = ebrw_readstr.int_u8()
				op_obj.filter_lowpass = ebrw_readstr.int_u8()
				op_obj.filter_CH2off = ebrw_readstr.int_u8()
			if system == int("04",16):
				self.gb_env_volume = ebrw_readstr.int_u8()
				self.gb_env_direction = ebrw_readstr.int_u8()
				self.gb_env_length = ebrw_readstr.int_u8()
				self.sound_length = ebrw_readstr.int_u8()

class deflemask_sample:
	def __init__(self):
		self.size = 0
		self.name = 0
		self.rate = 0
		self.pitch = 0
		self.amp = 0
		self.bits = 0
		self.data = []
		self.cutStart = 0
		self.cutEnd = 0

# ============================================= project ============================================= 

class deflemask_channel:
	def __init__(self, i_type):
		self.type = i_type
		self.visname = None
		self.patterns = {}
		self.orders = []
		self.names = []

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
		try:
			decompdata = zlib.decompress(bytestream.read())
		except zlib.error as t:
			raise ProjectFileParserException('deflemask: '+str(t))

		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_data(decompdata)
		ebrw_readstr.magic_check(b'.DelekDefleMask.')
		self.version = ebrw_readstr.int_u8()

		if self.version<24:
			raise ProjectFileParserException('deflemask: only version 24+ is supported. not %i.' % self.version)
		logger_projparse.info('deflemask: dmf version %i' % self.version)

		self.system = ebrw_readstr.int_u8()

		# SYSTEM SET
		if self.system == int("02",16): #GENESIS
			self.chantype = ['opn2','opn2','opn2','opn2','opn2','opn2','square','square','square','noise']
			self.channames = ['FM 1','FM 2','FM 3','FM 4','FM 5','FM 6','Square 1','Square 2','Square 3','Noise']
		elif self.system == int("42",16): #SYSTEM_GENESIS (mode EXT. CH3) 
			self.chantype = ['opn2','opn2','opn2-op','opn2-op','opn2-op','opn2-op','opn2','opn2','opn2','square','square','square','noise']
			self.channames = ['FM 1','FM 2','FM 3 OP 1','FM 3 OP 2','FM 3 OP 3','FM 3 OP 4','FM 4','FM 5','FM 6','Square 1','Square 2','Square 3','Noise']
		elif self.system == int("03",16): #SMS
			self.chantype = ['square','square','square','noise']
			self.channames = ['Square 1','Square 2','Square 3','Noise']
		elif self.system == int("04",16): #GAMEBOY
			self.chantype = ['gameboy_pulse','gameboy_pulse','gameboy_wavetable','gameboy_noise']
			self.channames = ['Pulse 1','Pulse 2','Wavetable','Noise']
		elif self.system == int("05",16): #PCENGINE
			self.chantype = ['pce','pce','pce','pce','pce','pce']
			self.channames = ['Channel 1','Channel 2','Channel 3','Channel 4','Channel 5','Channel 6']
		elif self.system == int("06",16): #NES
			self.chantype = ['pulse','pulse','triangle','noise','pcm']
			self.channames = ['Pulse 1','Pulse 2','Triangle','Noise','PCM']
		elif self.system == int("07",16): #C64 (SID 8580)
			self.chantype = ['c64','c64','c64']
			self.channames = ['Channel 1','Channel 2','Channel 3']
		elif self.system == int("47",16): #C64 (mode SID 6581)
			self.chantype = ['c64','c64','c64']
			self.channames = ['Channel 1','Channel 2','Channel 3']
		elif self.system == int("08",16): #ARCADE
			self.chantype = ['opn2','opn2','opn2','opn2','opn2','opn2','opn2','opn2','sample','sample','sample','sample','sample']
			self.channames = ['FM 1','FM 2','FM 3','FM 4','FM 5','FM 6','FM 7','FM 8','Channel 1','Channel 2','Channel 3','Channel 4','Channel 5']
		elif self.system == int("09",16): #NEOGEO
			self.chantype = ['opn2','opn2','opn2','opn2','psg','psg','psg','adpcma','adpcma','adpcma','adpcma','adpcma','adpcma']
			self.channames = ['FM 1','FM 2','FM 3','FM 4','PSG 1','PSG 2','PSG 3','ADPCM-A 1','ADPCM-A 2','ADPCM-A 3','ADPCM-A 4','ADPCM-A 5','ADPCM-A 6']
		elif self.system == int("49",16): #NEOGEO (mode EXT. CH2)
			self.chantype = ['opn2','opn2','opn2_op','opn2_op','opn2_op','opn2_op','opn2','psg','psg','psg','adpcma','adpcma','adpcma','adpcma','adpcma','adpcma']
			self.channames = ['FM 1','FM 2 OP 1','FM 2 OP 2','FM 2 OP 3','FM 2 OP 4','FM 3','FM 4','PSG 1','PSG 2','PSG 3','ADPCM-A 1','ADPCM-A 2','ADPCM-A 3','ADPCM-A 4','ADPCM-A 5','ADPCM-A 6']

		self.channels = []
		for n, x in enumerate(self.chantype):
			chan_obj = deflemask_channel(x)
			chan_obj.visname = self.channames[n]
			self.channels.append(chan_obj)

		self.total_channels = len(self.channels)

		# VISUAL INFORMATION
		self.song_name = ebrw_readstr.string_i8()
		self.song_author = ebrw_readstr.string_i8()
		self.highlight_a_pat = ebrw_readstr.int_u8()
		self.highlight_b_pat = ebrw_readstr.int_u8()

		# MODULE INFORMATION
		self.timebase = ebrw_readstr.int_u8()
		self.ticktime1 = ebrw_readstr.int_u8()
		self.ticktime2 = ebrw_readstr.int_u8()
		self.frames_mode = ebrw_readstr.int_u8()
		self.custom_hz_using = ebrw_readstr.int_u8()
		self.custom_hz_1 = ebrw_readstr.int_u8()
		self.custom_hz_2 = ebrw_readstr.int_u8()
		self.custom_hz_3 = ebrw_readstr.int_u8()
		self.total_rows_per_pattern = ebrw_readstr.int_u32()
		self.total_rows_in_pattern_matrix = ebrw_readstr.int_u8()

		self.pat_orders = []
		for c in self.channels: 
			c.orders = []
			for cp in range(self.total_rows_in_pattern_matrix): 
				num = ebrw_readstr.int_u8()
				c.orders.append(num)
				if (self.version>=25):
					patname = ebrw_readstr.string_i8()
					c.names.append(patname)

		num_insts = ebrw_readstr.int_u8()
		self.insts = [deflemask_instrument(ebrw_readstr, self.system) for _ in range(num_insts)]

		self.wavetables = []
		for _ in range(ebrw_readstr.int_u8()):
			wavesize = ebrw_readstr.int_u32()
			self.wavetables.append(ebrw_readstr.list_int_u32(wavesize))
 
		for num, chan_obj in enumerate(self.channels):
			fx_columns_count = ebrw_readstr.int_u8()
			for patnum in chan_obj.orders:
				table_rows = []
				for rownum in range(self.total_rows_per_pattern):
					r_note = ebrw_readstr.int_u16()
					r_oct = ebrw_readstr.int_u16()
					r_vol = ebrw_readstr.int_s16()
					r_fx = [ebrw_readstr.list_int_s16(2) for _ in range(fx_columns_count)]
					r_inst = ebrw_readstr.int_s16()
					table_rows.append([r_note, r_oct, r_vol, r_inst, r_fx])
				chan_obj.patterns[patnum] = table_rows

		num_samples = ebrw_readstr.int_u8()

		for _ in range(num_samples):
			sample_obj = deflemask_sample()
			sample_obj.size = ebrw_readstr.int_u32()
			sample_obj.name = ebrw_readstr.string_i8()
			sample_obj.rate = ebrw_readstr.int_u8()
			sample_obj.pitch = ebrw_readstr.int_u8()
			sample_obj.amp = ebrw_readstr.int_u8()
			sample_obj.bits = ebrw_readstr.int_u8()
			if self.version>=0x1b:
				sample_obj.cutStart = ebrw_readstr.int_u32()
				sample_obj.cutEnd = ebrw_readstr.int_u32()
			if sample_obj.bits == 16: sample_obj.data = ebrw_readstr.list_int_s16(sample_obj.size)
			if sample_obj.bits == 8: sample_obj.data = ebrw_readstr.list_int_u8(sample_obj.size*2)[0::2]
			self.samples.append(sample_obj)

		return True
