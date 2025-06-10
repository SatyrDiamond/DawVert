# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions.dawspecific import flp_plugchunks
from objects.data_bytes import bytewriter
from objects.dawspecific import flp_plugins
from dataclasses import dataclass
from dataclasses import field

VERBOSE = False

dw_chunks = {}

dw_chunks[1] = 'Main:Program'
dw_chunks[6] = 'Main:Main'
dw_chunks[5] = 'Main:Channel'
dw_chunks[518] = 'Main:Settings'

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
dw_chunks[517] = 'Region:PCMData'

dw_chunks[100] = 'Program:Main'
dw_chunks[102] = 'Program:Name'
dw_chunks[103] = 'Program:PresetPath'
dw_chunks[104] = 'Program:FX_Drive'
dw_chunks[105] = 'Program:FX_Delay'
dw_chunks[106] = 'Program:FX_Reverb'
dw_chunks[107] = 'Program:FX_Chorus'
dw_chunks[108] = 'Program:LFO'
dw_chunks[109] = 'Program:ModVal'

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
	unk_5: int = 0

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

	def dump(self):
		byw_stream = bytewriter.bytewriter()
		byw_stream.uint8(self.key_root)
		byw_stream.uint8(self.key_min)
		byw_stream.uint8(self.key_max)
		byw_stream.uint8(self.vel_min)
		byw_stream.uint8(self.vel_max)
		byw_stream.uint16(self.mute)
		byw_stream.flags16(self.flags)
		byw_stream.float(self.gain)
		byw_stream.float(self.pan)
		byw_stream.float(self.unk_2)
		byw_stream.uint8(self.unk_3)
		byw_stream.uint8(self.unk_4)
		byw_stream.uint16(self.unk_5)
		return byw_stream.getvalue()

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
		#print(  byr_stream.rest()  )

	def dump(self):
		byw_stream = bytewriter.bytewriter()
		byw_stream.uint32(max(0, self.num_samples))
		byw_stream.uint32(0)
		byw_stream.uint32(self.channels)
		byw_stream.uint32(self.bits)
		byw_stream.float(self.hz)
		byw_stream.uint32(self.loop_type)
		byw_stream.uint32(int(self.loop_start))
		byw_stream.uint32(int(self.loop_end))
		byw_stream.uint32(int(self.start))
		byw_stream.raw(b'\x10\x00\x00\x00')
		return byw_stream.getvalue()

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

	def dump(self):
		byw_stream = bytewriter.bytewriter()
		byw_stream.float(self.tune)
		byw_stream.int8(self.semi)
		byw_stream.int8(self.fine)
		byw_stream.uint16(self.k_trk)
		return byw_stream.getvalue()

@dataclass
class directwave_region_timestretch:
	time: int = 0
	sync: int = 0
	stretch: float = 0.5
	grain: float = 0.5
	smooth: float = 1

	def from_byr(self, byr_stream): 
		self.time = byr_stream.uint8()
		self.sync = byr_stream.uint8()
		self.stretch = byr_stream.float()
		self.grain = byr_stream.float()
		self.smooth = byr_stream.float()

	def dump(self):
		byw_stream = bytewriter.bytewriter()
		byw_stream.uint8(self.time)
		byw_stream.uint8(self.sync)
		byw_stream.float(self.stretch)
		byw_stream.float(self.grain)
		byw_stream.float(self.smooth)
		return byw_stream.getvalue()

@dataclass
class directwave_region_filter:
	cutoff: float = 0.4724409580230713
	reso: float = 0.5
	shape: float = 0
	type: int = 0

	def from_byr(self, byr_stream): 
		self.type = byr_stream.uint32()
		self.cutoff = byr_stream.float()
		self.reso = byr_stream.float()
		self.shape = byr_stream.float()

	def dump(self):
		byw_stream = bytewriter.bytewriter()
		byw_stream.uint32(self.type)
		byw_stream.float(self.cutoff)
		byw_stream.float(self.reso)
		byw_stream.float(self.shape)
		byw_stream.uint32(0)
		return byw_stream.getvalue()

@dataclass
class directwave_region_sysl:
	sy: int = 0
	sl: int = 0

	def from_byr(self, byr_stream): 
		self.sy = byr_stream.uint8()
		self.sl = byr_stream.uint8()

	def dump(self):
		byw_stream = bytewriter.bytewriter()
		byw_stream.uint8(self.sy)
		byw_stream.uint8(self.sl)
		return byw_stream.getvalue()

@dataclass
class directwave_region_adsr:
	attack: float = 0
	decay: float = 0.5
	sustain: float = 0.5
	release: float = 0.25

	def from_byr(self, byr_stream): 
		self.attack = byr_stream.float()
		self.decay = byr_stream.float()
		self.sustain = byr_stream.float()
		self.release = byr_stream.float()

	def dump(self):
		byw_stream = bytewriter.bytewriter()
		byw_stream.float(self.attack)
		byw_stream.float(self.decay)
		byw_stream.float(self.sustain)
		byw_stream.float(self.release)
		return byw_stream.getvalue()

@dataclass
class directwave_region_fx_2param:
	enable: int = 0
	param1: float = 0
	param2: float = 1

	def from_byr(self, byr_stream): 
		self.enable = byr_stream.uint8()
		self.param1 = byr_stream.float()
		self.param2 = byr_stream.float()

	def dump(self):
		byw_stream = bytewriter.bytewriter()
		byw_stream.uint8(self.enable)
		byw_stream.float(self.param1)
		byw_stream.float(self.param2)
		return byw_stream.getvalue()

@dataclass
class directwave_region_lfo:
	wave: int = 0
	ratetype: int = 0
	rate: float = 0.10000000149011612
	phase: float = 1
	attack: float = 0

	def from_byr(self, byr_stream): 
		self.wave = byr_stream.uint8()
		self.ratetype = byr_stream.uint16()
		byr_stream.skip(1)
		self.rate = byr_stream.float()
		self.phase = byr_stream.float()
		self.attack = byr_stream.float()

	def dump(self):
		byw_stream = bytewriter.bytewriter()
		byw_stream.uint8(self.wave)
		byw_stream.uint16(self.ratetype)
		byw_stream.uint8(0)
		byw_stream.float(self.rate)
		byw_stream.float(self.phase)
		byw_stream.float(self.attack)
		byw_stream.uint32(0)
		return byw_stream.getvalue()

@dataclass
class directwave_region_mod:
	mod_from: int = 0
	mod_to: int = 0
	amount: float = 0.5

	def from_byr(self, byr_stream): 
		self.mod_from = byr_stream.uint16()
		self.mod_to = byr_stream.uint16()
		self.amount = byr_stream.float()

	def dump(self):
		byw_stream = bytewriter.bytewriter()
		byw_stream.uint16(self.mod_from)
		byw_stream.uint16(self.mod_to)
		byw_stream.float(self.amount)
		return byw_stream.getvalue()

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

		self.modmatrix = [directwave_region_mod() for x in range(16)]

		self.fx_phaser.param1 = 0.5

		self.modmatrix[0].mod_from = 2
		self.modmatrix[0].mod_to = 2
		self.modmatrix[0].amount = 1

		self.modmatrix[1].mod_from = 3
		self.modmatrix[1].mod_to = 34
		self.modmatrix[1].amount = 0.75

		self.modmatrix[2].mod_from = 12
		self.modmatrix[2].mod_to = 1

		self.lfo2.rate = 0.550000011920929

		self.env_main.sustain = 1

		self.sends_fx = [.5,.5,.5,1]
		self.name = b''
		self.path = b''
		self.pcmdata = None
		self.flacdata = None

	def read(self, byr_stream):
		self.modmatrix = []
		filternum = 0
		altenvnum = 0
		lfonum = 0
		while byr_stream.remaining():
			chunktype, chunksize = flp_plugchunks.read_header(byr_stream)
			with byr_stream.isolate_size(chunksize, True) as bye_stream: 
				if VERBOSE: 
					print('\t\t\t', getname(chunktype), chunksize, end='')
					print(bye_stream.rest().hex())
					bye_stream.seek(0)
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
				elif chunktype == 510: self.fx_ringmod.from_byr(bye_stream)
				elif chunktype == 511: self.fx_decimator.from_byr(bye_stream)
				elif chunktype == 512: self.fx_quantizer.from_byr(bye_stream)
				elif chunktype == 513: self.fx_phaser.from_byr(bye_stream)
				elif chunktype == 514:
					if altenvnum == 0: self.env_alt1.from_byr(bye_stream)
					if altenvnum == 1: self.env_alt2.from_byr(bye_stream)
					altenvnum += 1
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
				elif chunktype == 518:
					self.flacdata = bye_stream.raw(chunksize)

	def dump(self):
		byw_stream = bytewriter.bytewriter()
		flp_plugchunks.write_chunk(byw_stream, 500, self.main.dump())
		flp_plugchunks.write_chunk(byw_stream, 501, self.name)
		flp_plugchunks.write_chunk(byw_stream, 502, self.path)
		flp_plugchunks.write_chunk(byw_stream, 503, self.sample.dump())
		flp_plugchunks.write_chunk(byw_stream, 504, self.pitch.dump())
		flp_plugchunks.write_chunk(byw_stream, 505, self.timestretch.dump())

		info_sendsfx = bytewriter.bytewriter()
		info_sendsfx.l_float(self.sends_fx, 4)
		info_sendsfx.raw(b'\0'*32)
		flp_plugchunks.write_chunk(byw_stream, 506, info_sendsfx.getvalue())
		flp_plugchunks.write_chunk(byw_stream, 507, self.filter_a.dump())
		flp_plugchunks.write_chunk(byw_stream, 507, self.filter_b.dump())
		flp_plugchunks.write_chunk(byw_stream, 508, self.sysl.dump())
		flp_plugchunks.write_chunk(byw_stream, 509, self.env_main.dump())
		flp_plugchunks.write_chunk(byw_stream, 510, self.fx_ringmod.dump())
		flp_plugchunks.write_chunk(byw_stream, 511, self.fx_decimator.dump())
		flp_plugchunks.write_chunk(byw_stream, 512, self.fx_quantizer.dump())
		flp_plugchunks.write_chunk(byw_stream, 513, self.fx_phaser.dump())
		flp_plugchunks.write_chunk(byw_stream, 514, self.env_alt1.dump())
		flp_plugchunks.write_chunk(byw_stream, 514, self.env_alt2.dump())
		flp_plugchunks.write_chunk(byw_stream, 515, self.lfo1.dump())
		flp_plugchunks.write_chunk(byw_stream, 515, self.lfo2.dump())
		for mod_obj in self.modmatrix:
			flp_plugchunks.write_chunk(byw_stream, 516, mod_obj.dump())
		if self.pcmdata is not None:
			flp_plugchunks.write_chunk(byw_stream, 517, self.pcmdata)
		if self.flacdata is not None:
			flp_plugchunks.write_chunk(byw_stream, 518, self.flacdata)
		flp_plugchunks.write_chunk(byw_stream, 4, b'')

		return byw_stream.getvalue()

# ============================================= Program ============================================= 

@dataclass
class directwave_program_fx_drive:
	a_enable: int = 0
	b_enable: int = 0
	a_amount: float = 0
	b_amount: float = 0

	def from_byr(self, byr_stream): 
		self.a_enable = byr_stream.uint8()
		self.b_enable = byr_stream.uint8()
		self.a_amount = byr_stream.float()
		self.b_amount = byr_stream.float()

	def dump(self):
		byw_stream = bytewriter.bytewriter()
		byw_stream.uint8(self.a_enable)
		byw_stream.uint8(self.b_enable)
		byw_stream.float(self.a_amount)
		byw_stream.float(self.b_amount)
		return byw_stream.getvalue()

@dataclass
class directwave_program_fx_delay:
	enable: int = 0
	mode: int = 0
	delay: float = 0.75
	feedback: float = 0.75
	low_cut: float = 0.5
	high_cut: float = 0.75

	def from_byr(self, byr_stream): 
		self.enable = byr_stream.uint8()
		self.mode = byr_stream.uint8()
		self.delay = byr_stream.float()
		self.feedback = byr_stream.float()
		self.low_cut = byr_stream.float()
		self.high_cut = byr_stream.float()

	def dump(self):
		byw_stream = bytewriter.bytewriter()
		byw_stream.uint8(self.enable)
		byw_stream.uint8(self.mode)
		byw_stream.float(self.delay)
		byw_stream.float(self.feedback)
		byw_stream.float(self.low_cut)
		byw_stream.float(self.high_cut)
		return byw_stream.getvalue()

@dataclass
class directwave_program_fx_reverb:
	enable: int = 0
	room: float = 0.25
	damp: float = 0.5
	diffusion: float = 0.75
	decay: float = 0.25

	def from_byr(self, byr_stream): 
		self.enable = byr_stream.uint8()
		self.room = byr_stream.float()
		self.damp = byr_stream.float()
		self.diffusion = byr_stream.float()
		self.decay = byr_stream.float()

	def dump(self):
		byw_stream = bytewriter.bytewriter()
		byw_stream.uint8(self.enable)
		byw_stream.float(self.room)
		byw_stream.float(self.damp)
		byw_stream.float(self.diffusion)
		byw_stream.float(self.decay)
		return byw_stream.getvalue()

@dataclass
class directwave_program_fx_chorus:
	enable: int = 0
	delay: float = 0.25
	depth: float = 0.5
	rate: float = 0.25
	feedback: float = 0

	def from_byr(self, byr_stream): 
		self.enable = byr_stream.uint8()
		self.delay = byr_stream.float()
		self.depth = byr_stream.float()
		self.rate = byr_stream.float()
		self.feedback = byr_stream.float()

	def dump(self):
		byw_stream = bytewriter.bytewriter()
		byw_stream.uint8(self.enable)
		byw_stream.float(self.delay)
		byw_stream.float(self.depth)
		byw_stream.float(self.rate)
		byw_stream.float(self.feedback)
		return byw_stream.getvalue()

@dataclass
class directwave_program_lfo:
	enable: int = 0
	wave: int = 0
	rate: float = 0.1
	phase: float = 1
	attack: float = 0

	def from_byr(self, byr_stream): 
		self.enable = byr_stream.uint8()
		self.wave = byr_stream.uint8()
		byr_stream.skip(2)
		self.rate = byr_stream.float()
		self.phase = byr_stream.float()
		self.attack = byr_stream.float()

	def dump(self):
		byw_stream = bytewriter.bytewriter()
		byw_stream.uint8(self.enable)
		byw_stream.uint8(self.wave)
		byw_stream.raw(b'\0'*2)
		byw_stream.float(self.rate)
		byw_stream.float(self.phase)
		byw_stream.float(self.attack)
		byw_stream.raw(b'\0'*4)
		return byw_stream.getvalue()

@dataclass
class directwave_program_main:
	num: int = 0
	playmode: int = 0
	glidemode: int = 0
	vol: float = 1
	glidetime: float = 0
	used: int = 0

	def from_byr(self, byr_stream): 
		self.num = byr_stream.uint32()
		self.playmode = byr_stream.uint8()
		self.glidemode = byr_stream.uint8()
		self.vol = byr_stream.float()
		self.glidetime = byr_stream.float()
		self.used = byr_stream.uint32()

	def dump(self):
		byw_stream = bytewriter.bytewriter()
		byw_stream.uint32(self.num)
		byw_stream.uint8(self.playmode)
		byw_stream.uint8(self.glidemode)
		byw_stream.float(self.vol)
		byw_stream.float(self.glidetime)
		byw_stream.uint32(self.used)
		byw_stream.uint32(0)
		byw_stream.uint32(0)
		byw_stream.uint32(0)
		return byw_stream.getvalue()

class directwave_program:
	def __init__(self):
		self.regions = []
		self.name = b'---'
		self.path = b''
		self.main = directwave_program_main()
		self.fx_drive = directwave_program_fx_drive()
		self.fx_delay = directwave_program_fx_delay()
		self.fx_reverb = directwave_program_fx_reverb()
		self.fx_chorus = directwave_program_fx_chorus()
		self.lfo1 = directwave_program_lfo()
		self.lfo2 = directwave_program_lfo()
		self.modvals = [0,0,0,0]

	def add_region(self):
		region_obj = directwave_region()
		self.regions.append(region_obj)
		return region_obj

	def read(self, byr_stream):
		self.regions = []
		self.modvals = []
		lfonum = 0
		while byr_stream.remaining():
			chunktype, chunksize = flp_plugchunks.read_header(byr_stream)
			with byr_stream.isolate_size(chunksize, True) as bye_stream: 
				if VERBOSE: print('\t\t', getname(chunktype), chunksize, end=' > ')
				if chunktype == 100:
					self.main.from_byr(bye_stream)
					if VERBOSE: print(self.main)
				elif chunktype == 102:
					self.name = bye_stream.raw(chunksize)
					if VERBOSE: print(self.name)
				elif chunktype == 103:
					self.path = bye_stream.raw(chunksize)
					if VERBOSE: print(self.path)
				elif chunktype == 104:
					self.fx_drive.from_byr(bye_stream)
					if VERBOSE: print(self.fx_drive)
				elif chunktype == 105:
					self.fx_delay.from_byr(bye_stream)
					if VERBOSE: print(self.fx_delay)
				elif chunktype == 106:
					self.fx_reverb.from_byr(bye_stream)
					if VERBOSE: print(self.fx_reverb)
				elif chunktype == 107:
					self.fx_chorus.from_byr(bye_stream)
					if VERBOSE: print(self.fx_chorus)
				elif chunktype == 108:
					if VERBOSE: print()
					if lfonum == 0: self.lfo1.from_byr(bye_stream)
					if lfonum == 1: self.lfo2.from_byr(bye_stream)
					lfonum += 1
				elif chunktype == 109:
					if VERBOSE: print()
					self.modvals.append(bye_stream.float())
				elif chunktype == 3:
					if VERBOSE: print()
					region_obj = directwave_region()
					region_obj.read(bye_stream)
					self.regions.append(region_obj)
				else:
					if VERBOSE: print(bye_stream.raw(chunksize).hex())

	def dump(self):
		byw_stream = bytewriter.bytewriter()
		flp_plugchunks.write_chunk(byw_stream, 100, self.main.dump())
		flp_plugchunks.write_chunk(byw_stream, 102, self.name)
		flp_plugchunks.write_chunk(byw_stream, 103, self.path)
		flp_plugchunks.write_chunk(byw_stream, 104, self.fx_drive.dump())
		flp_plugchunks.write_chunk(byw_stream, 105, self.fx_delay.dump())
		flp_plugchunks.write_chunk(byw_stream, 106, self.fx_reverb.dump())
		flp_plugchunks.write_chunk(byw_stream, 107, self.fx_chorus.dump())
		flp_plugchunks.write_chunk(byw_stream, 108, self.lfo1.dump())
		flp_plugchunks.write_chunk(byw_stream, 108, self.lfo2.dump())
		for x in self.modvals:
			info_modvals = bytewriter.bytewriter()
			info_modvals.float(x)
			flp_plugchunks.write_chunk(byw_stream, 109, info_modvals.getvalue())
		for x in range(100):
			info_modvals = bytewriter.bytewriter()
			info_modvals.uint8(x)
			info_modvals.uint32(0)
			info_modvals.float(1)
			info_modvals.uint32(0)
			flp_plugchunks.write_chunk(byw_stream, 110, info_modvals.getvalue())
		for region in self.regions:
			flp_plugchunks.write_chunk(byw_stream, 3, region.dump())
		flp_plugchunks.write_chunk(byw_stream, 2, b'')
		return byw_stream.getvalue()

# ============================================= Main ============================================= 

@dataclass
class directwave_channel:
	channelid: int = 0
	unk1: float = 0.0078125
	prognum: int = 0
	output: int = 0
	mute: int = 0
	solo: int = 0
	pitchbend_range: int = 200
	pitch_bend: float = 0
	mod_wheel: float = 0
	mast_vol: float = 0.787401556968689
	mast_pan: float = 0.5
	mast_exp: float = 1
	res_005: float = 0
	res_006: float = 0
	res_007: float = 0
	res_008: float = 0
	res_009: float = 0
	res_010: float = 0
	res_011: float = 0
	res_012: float = 0
	res_013: float = 0
	res_014: float = 0
	res_015: float = 0

	def from_byr(self, byr_stream): 
		self.channelid = byr_stream.uint8()
		self.unk1 = byr_stream.float()
		byr_stream.skip(515)
		self.prognum = byr_stream.uint8()
		self.output = byr_stream.uint8()
		byr_stream.skip(2)
		self.mute = byr_stream.uint8()
		self.solo = byr_stream.uint8()
		byr_stream.skip(2)
		byr_stream.skip(4)
		self.pitchbend_range = byr_stream.int32()
		byr_stream.skip(28)
		self.pitch_bend = byr_stream.float()
		self.mod_wheel = byr_stream.float()
		self.mast_vol = byr_stream.float()
		self.mast_pan = byr_stream.float()
		self.mast_exp = byr_stream.float()
		self.res_005 = byr_stream.float()
		self.res_006 = byr_stream.float()
		self.res_007 = byr_stream.float()
		self.res_008 = byr_stream.float()
		self.res_009 = byr_stream.float()
		self.res_010 = byr_stream.float()
		self.res_011 = byr_stream.float()
		self.res_012 = byr_stream.float()
		self.res_013 = byr_stream.float()
		self.res_014 = byr_stream.float()
		self.res_015 = byr_stream.float()

	def dump(self):
		byw_stream = bytewriter.bytewriter()
		byw_stream.uint8(self.channelid)
		byw_stream.float(self.unk1)
		byw_stream.raw(b'\0'*515)
		byw_stream.uint8(self.prognum)
		byw_stream.uint8(self.output)
		byw_stream.raw(b'\0'*2)
		byw_stream.uint8(self.mute)
		byw_stream.uint8(self.solo)
		byw_stream.raw(b'\0'*2)
		byw_stream.raw(b'\0'*4)
		byw_stream.int32(self.pitchbend_range)
		byw_stream.raw(b'\0'*28)
		byw_stream.float(self.pitch_bend)
		byw_stream.float(self.mod_wheel)
		byw_stream.float(self.mast_vol)
		byw_stream.float(self.mast_pan)
		byw_stream.float(self.mast_exp)
		byw_stream.float(self.res_005)
		byw_stream.float(self.res_006)
		byw_stream.float(self.res_007)
		byw_stream.float(self.res_008)
		byw_stream.float(self.res_009)
		byw_stream.float(self.res_010)
		byw_stream.float(self.res_011)
		byw_stream.float(self.res_012)
		byw_stream.float(self.res_013)
		byw_stream.float(self.res_014)
		byw_stream.float(self.res_015)
		return byw_stream.getvalue()

class directwave_plugin:
	def __init__(self):
		self.version = 38
		self.programs = []
		self.channels = []
		for x in range(16):
			channel_obj = directwave_channel()
			channel_obj.channelid = x
			channel_obj.prognum = x
			self.channels.append(channel_obj)
		for x in range(128):
			program_obj = directwave_program()
			#program_obj.name = str(x).encode()
			program_obj.main.num = x
			self.programs.append(program_obj)

	def read(self, byr_stream):
		self.programs = []
		self.channels = []
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
				elif chunktype == 5:
					if VERBOSE: print()
					channel_obj = directwave_channel()
					channel_obj.from_byr(bye_stream)
					self.channels.append(channel_obj)
				else:
					if VERBOSE: print(bye_stream.raw(chunksize).hex())

	def dump(self):
		byw_stream = bytewriter.bytewriter()
		byw_stream.uint32(self.version)
		flp_plugchunks.write_chunk(byw_stream, 6, b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
		flp_plugchunks.write_chunk(byw_stream, 518, b'\x01\x00\x00\x00\x00\x00\x00')
		for channel_obj in self.channels:
			flp_plugchunks.write_chunk(byw_stream, 5, channel_obj.dump())
		for program_obj in self.programs:
			flp_plugchunks.write_chunk(byw_stream, 1, program_obj.dump())
		return byw_stream.getvalue()