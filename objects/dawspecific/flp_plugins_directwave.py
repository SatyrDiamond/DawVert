# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions.dawspecific import flp_plugchunks
from objects.data_bytes import bytewriter
from objects.dawspecific import flp_plugins
from dataclasses import dataclass
from dataclasses import field

VERBOSE = False

dw_chunks = {}


dw_chunks[500] = 'Region:Main'
dw_chunks[501] = 'Region:Name'
dw_chunks[502] = 'Region:Path'
dw_chunks[503] = 'Region:Sample'
dw_chunks[504] = 'Region:PitchKtrkTicks'
dw_chunks[505] = 'Region:Time'
dw_chunks[506] = 'Region:Sends_FX'
dw_chunks[507] = 'Region:Filter'
dw_chunks[508] = 'Region:SySl'
dw_chunks[509] = 'Region:ASDREnv_Main'
dw_chunks[510] = 'Region:FX_Ringmod'
dw_chunks[511] = 'Region:FX_Decimator'
dw_chunks[512] = 'Region:FX_Quantizer'
dw_chunks[513] = 'Region:FX_Phaser'
dw_chunks[514] = 'Region:ASDREnv_Alt'
dw_chunks[515] = 'Region:LFO'
dw_chunks[516] = 'Region:ModMatrix'

dw_chunks[100] = 'Program:Main'
dw_chunks[102] = 'Program:Name'
dw_chunks[104] = 'Program:FX_Drive'
dw_chunks[105] = 'Program:FX_Delay'
dw_chunks[106] = 'Program:FX_Reverb'
dw_chunks[107] = 'Program:FX_Chorus'
dw_chunks[108] = 'Program:LFO'

def getname(num): 
	return dw_chunks[num] if num in dw_chunks else '?Unknown:%i?' % num

# ============================================= region ============================================= 

@dataclass
class directwave_region_main:
	key_root: int = 60
	key_min: int = 0
	key_max: int = 127
	vel_min: int = 0
	vel_max: int = 127
	mute: int = 0
	flags: list = field(default_factory=list)
	gain: float = 1.0
	pan: float = 0.5
	unk_2: float = 0.0
	unk_3: int = 0
	unk_4: int = 0
	unk_4: int = 0

	def from_byr(self, byr_stream): 
		self.key_root = byr_stream.uint8()
		self.key_min = byr_stream.uint8()
		self.key_max = byr_stream.uint8()
		self.vel_min = byr_stream.uint8()
		self.vel_max = byr_stream.uint8()
		self.mute = byr_stream.uint16()
		self.flags = byr_stream.flags16()
		self.gain = byr_stream.float()
		self.pan = byr_stream.float()
		self.unk_2 = byr_stream.float()
		self.unk_3 = byr_stream.uint8()
		self.unk_4 = byr_stream.uint8()
		self.unk_5 = byr_stream.uint16()

@dataclass
class directwave_region_sample:
	num_samples: int = 1
	channels: int = 0
	bits: int = 0
	hz: float = 44100
	loop_type: int = 0
	loop_start: int = 0
	loop_end: int = 0
	start: int = 0

	def from_byr(self, byr_stream): 
		self.num_samples = byr_stream.uint32()
		byr_stream.skip(4)
		self.channels = byr_stream.uint32()
		self.bits = byr_stream.uint32()
		self.hz = byr_stream.float()
		self.loop_type = byr_stream.uint32()
		self.loop_start = byr_stream.uint32()
		self.loop_end = byr_stream.uint32()
		self.start = byr_stream.uint32()

@dataclass
class directwave_region_pitch:
	tune: float = 0.5
	semi: int = 0
	fine: int = 0
	k_trk: int = 100

	def from_byr(self, byr_stream): 
		self.tune = byr_stream.float()
		self.semi = byr_stream.int8()
		self.fine = byr_stream.int8()
		self.k_trk = byr_stream.uint16()

@dataclass
class directwave_region_timestretch:
	time: int = 0
	sync: int = 0
	stretch: float = 0.5
	grain: float = 0.5
	smooth: float = 0.5

	def from_byr(self, byr_stream): 
		self.time = byr_stream.uint8()
		self.sync = byr_stream.uint8()
		self.stretch = byr_stream.float()
		self.grain = byr_stream.float()
		self.smooth = byr_stream.float()

@dataclass
class directwave_region_filter:
	cutoff: float = 0.5
	reso: float = 0.5
	shape: float = 0.5
	type: int = 0

	def from_byr(self, byr_stream): 
		self.type = byr_stream.uint32()
		self.cutoff = byr_stream.float()
		self.reso = byr_stream.float()
		self.shape = byr_stream.float()

@dataclass
class directwave_region_sysl:
	sy: int = 0
	sl: int = 0

	def from_byr(self, byr_stream): 
		self.sy = byr_stream.uint8()
		self.sl = byr_stream.uint8()

@dataclass
class directwave_region_adsr:
	attack: float = 0
	decay: float = 0
	sustain: float = 1
	release: float = 0

	def from_byr(self, byr_stream): 
		self.attack = byr_stream.float()
		self.decay = byr_stream.float()
		self.sustain = byr_stream.float()
		self.release = byr_stream.float()

@dataclass
class directwave_region_fx_2param:
	enable: int = 0
	param1: float = 0
	param2: float = 0

	def from_byr(self, byr_stream): 
		self.enable = byr_stream.uint8()
		self.param1 = byr_stream.float()
		self.param2 = byr_stream.float()

@dataclass
class directwave_region_lfo:
	wave: int = 0
	ratetype: int = 0
	rate: float = 0
	phase: float = 0
	attack: float = 0

	def from_byr(self, byr_stream): 
		self.wave = byr_stream.uint8()
		self.ratetype = byr_stream.uint16()
		byr_stream.skip(1)
		self.rate = byr_stream.float()
		self.phase = byr_stream.float()
		self.attack = byr_stream.float()

@dataclass
class directwave_region_mod:
	mod_from: int = 0
	mod_to: int = 0
	amount: float = 0

	def from_byr(self, byr_stream): 
		self.mod_from = byr_stream.uint16()
		self.mod_to = byr_stream.uint16()
		self.amount = byr_stream.float()

class directwave_region:
	def __init__(self):
		self.main = directwave_region_main()
		self.sample = directwave_region_sample()
		self.pitch = directwave_region_pitch()
		self.timestretch = directwave_region_timestretch()
		self.filter_a = directwave_region_filter()
		self.filter_b = directwave_region_filter()
		self.sysl = directwave_region_sysl()
		self.env_main = directwave_region_adsr()
		self.env_alt1 = directwave_region_adsr()
		self.env_alt2 = directwave_region_adsr()

		self.lfo1 = directwave_region_lfo()
		self.lfo2 = directwave_region_lfo()

		self.fx_ringmod = directwave_region_fx_2param()
		self.fx_decimator = directwave_region_fx_2param()
		self.fx_quantizer = directwave_region_fx_2param()
		self.fx_phaser = directwave_region_fx_2param()

		self.modmatrix = []

		self.sends_fx = [1,1,1,1]
		self.name = b''
		self.path = b''
		self.pcmdata = None

	def read(self, byr_stream):
		self.modmatrix = []
		filternum = 0
		altenvnum = 0
		lfonum = 0
		while byr_stream.remaining():
			chunktype, chunksize = flp_plugchunks.read_header(byr_stream)
			with byr_stream.isolate_size(chunksize, True) as bye_stream: 
				if chunktype == 500: self.main.from_byr(bye_stream)
				elif chunktype == 501: self.name = bye_stream.raw(chunksize)
				elif chunktype == 502: self.path = bye_stream.raw(chunksize)
				elif chunktype == 503: self.sample.from_byr(bye_stream)
				elif chunktype == 504: self.pitch.from_byr(bye_stream)
				elif chunktype == 505: self.timestretch.from_byr(bye_stream)
				elif chunktype == 506: self.sends_fx = bye_stream.l_float(4)
				elif chunktype == 507:
					if filternum == 0: self.filter_a.from_byr(bye_stream)
					if filternum == 1: self.filter_b.from_byr(bye_stream)
					filternum += 1
				elif chunktype == 508: self.sysl.from_byr(bye_stream)
				elif chunktype == 509: self.env_main.from_byr(bye_stream)
				elif chunktype == 514:
					if altenvnum == 0: self.env_alt1.from_byr(bye_stream)
					if altenvnum == 1: self.env_alt2.from_byr(bye_stream)
					altenvnum += 1
				elif chunktype == 510: self.fx_ringmod.from_byr(bye_stream)
				elif chunktype == 511: self.fx_decimator.from_byr(bye_stream)
				elif chunktype == 512: self.fx_quantizer.from_byr(bye_stream)
				elif chunktype == 513: self.fx_phaser.from_byr(bye_stream)
				elif chunktype == 515:
					if lfonum == 0: self.lfo1.from_byr(bye_stream)
					if lfonum == 1: self.lfo2.from_byr(bye_stream)
					lfonum += 1
				elif chunktype == 516:
					mod_obj = directwave_region_mod()
					mod_obj.from_byr(bye_stream)
					self.modmatrix.append(mod_obj)
				elif chunktype == 517:
					self.pcmdata = bye_stream.raw(chunksize)

# ============================================= Program ============================================= 

class directwave_program:
	def __init__(self):
		self.regions = []
		pass

	def read(self, byr_stream):
		self.regions = []
		while byr_stream.remaining():
			chunktype, chunksize = flp_plugchunks.read_header(byr_stream)
			with byr_stream.isolate_size(chunksize, True) as bye_stream: 
				if VERBOSE: print('\t\t', getname(chunktype), chunksize, end=' > ')
				if chunktype == 3:
					if VERBOSE: print()
					region_obj = directwave_region()
					region_obj.read(bye_stream)
					self.regions.append(region_obj)
				else:
					if VERBOSE: print(bye_stream.raw(chunksize).hex())

class directwave_plugin:
	def __init__(self):
		self.version = 36
		self.programs = []

	def read(self, byr_stream):
		self.programs = []
		self.version = byr_stream.uint32()
		while byr_stream.remaining():
			chunktype, chunksize = flp_plugchunks.read_header(byr_stream)
			with byr_stream.isolate_size(chunksize, True) as bye_stream:
				if VERBOSE: print('\t', getname(chunktype), chunksize, end=' > ')
				if chunktype == 1:
					if VERBOSE: print()
					program_obj = directwave_program()
					program_obj.read(bye_stream)
					self.programs.append(program_obj)
				else:
					if VERBOSE: print(bye_stream.raw(chunksize).hex())