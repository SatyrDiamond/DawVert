# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
import struct
from io import BytesIO

class caustic_controls:
	def __init__(self):
		self.data = {}

	def parse(self, bio_in):
		print('[format-caustic] CCOL |', end=' ')
		if bio_in.read(4) != b'CCOL': exit('[error] CCOL magic mismatch')
		CCOL_size = int.from_bytes(bio_in.read(4), "little")
		CCOL_data = bio_in.read(CCOL_size)
		CCOL_chunks = data_bytes.iff_read(CCOL_data, 0)
		for part in CCOL_chunks:
			con_id, con_val = struct.unpack('<If', part[1][0:8])
			self.data[con_id] = con_val
		print(str(len(self.data))+' Controls')

class caustic_modularslot:
	def __init__(self):
		self.slot_type = 0
		self.params = []

class caustic_modular:
	def __init__(self):
		self.slots = [caustic_modularslot() for x in range(16)]
		self.main = caustic_modularslot()
		self.connections = []

class caustic_machine:
	def __init__(self):
		self.mach_id = 'NULL'
		self.name = ''
		self.data = None

		self.unknown1 = None
		self.unknown2 = None
		self.unknown3 = None
		self.unknown4 = None
		self.unknown5 = None

		self.poly = 8
		self.presetname = ''
		self.presetpath = ''

		self.customwaveform1 = []
		self.customwaveform2 = []

		self.controls = caustic_controls()

		self.controls_noauto = {}
		self.visual = {}

		self.samples = []

		self.patterns = caustic_patterns()

		self.extra = None

	def parse(self):
		data_str = BytesIO(self.data)
		# -------------------------------- SubSynth --------------------------------
		if self.mach_id == 'SSYN':
			self.unknown1 = int.from_bytes(data_str.read(2), "little")
			self.unknown2 = int.from_bytes(data_str.read(1), "little")
			self.unknown3 = int.from_bytes(data_str.read(1), "little")
			self.controls.parse(data_str)
			self.presetname = data_str.read(32).split(b'\x00')[0].decode('ascii')
			presetpath_size = int.from_bytes(data_str.read(4), "little")
			self.presetpath = data_str.read(presetpath_size).split(b'\x00')[0].decode('ascii')
			self.unknown4 = int.from_bytes(data_str.read(4), "little")
			self.customwaveform1 = data_str.read(1320)
			self.customwaveform2 = data_str.read(1320)
			self.controls_noauto['poly'] = int.from_bytes(data_str.read(4), "little")
			self.controls_noauto['osc1_mode'] = int.from_bytes(data_str.read(4), "little")
			self.controls_noauto['osc2_mode'] = int.from_bytes(data_str.read(4), "little")
			self.patterns.parse(data_str)
		# -------------------------------- BassLine --------------------------------
		elif self.mach_id == 'BLNE':
			self.unknown1 = int.from_bytes(data_str.read(2), "little")
			self.unknown2 = int.from_bytes(data_str.read(1), "little")
			self.unknown3 = int.from_bytes(data_str.read(1), "little")
			self.controls.parse(data_str)
			self.presetname = data_str.read(32).split(b'\x00')[0].decode('ascii')
			presetpath_size = int.from_bytes(data_str.read(4), "little")
			self.presetpath = data_str.read(presetpath_size).split(b'\x00')[0].decode('ascii')
			self.visual['keyboard_octave'] = int.from_bytes(data_str.read(4), "little")
			self.patterns.parse(data_str)
			self.controls_noauto['legacy_glide'] = struct.unpack('f', data_str.read(4))[0]
			self.customwaveform1 = data_str.read(1320)
		# -------------------------------- PadSynth --------------------------------
		elif self.mach_id == 'PADS':
			self.controls.parse(data_str)
			self.presetname = data_str.read(32).split(b'\x00')[0].decode('ascii')
			presetpath_size = int.from_bytes(data_str.read(4), "little")
			self.presetpath = data_str.read(presetpath_size).split(b'\x00')[0].decode('ascii')
			self.visual['keyboard_octave'] = int.from_bytes(data_str.read(4), "little")
			self.unknown1 = int.from_bytes(data_str.read(4), "little")
			self.visual['visual'] = int.from_bytes(data_str.read(4), "little")
			self.controls_noauto['harm1'] = struct.unpack("ffffffffffffffffffffffff", data_str.read(96))
			self.controls_noauto['harm1vol'] = struct.unpack("f", data_str.read(4))[0]
			self.controls_noauto['harm2'] = struct.unpack("ffffffffffffffffffffffff", data_str.read(96))
			self.controls_noauto['harm2vol'] = struct.unpack("f", data_str.read(4))[0]
			self.patterns.parse(data_str)
		# -------------------------------- Organ --------------------------------
		elif self.mach_id == 'ORGN':
			self.controls.parse(data_str)
			self.presetname = data_str.read(32).split(b'\x00')[0].decode('ascii')
			presetpath_size = int.from_bytes(data_str.read(4), "little")
			self.presetpath = data_str.read(presetpath_size).split(b'\x00')[0].decode('ascii')
			self.visual['keyboard_octave'] = int.from_bytes(data_str.read(4), "little")
			self.unknown1 = int.from_bytes(data_str.read(4), "little")
		# -------------------------------- FMSynth --------------------------------
		elif self.mach_id == 'FMSN':
			self.unknown1 = int.from_bytes(data_str.read(2), "little")
			self.unknown2 = int.from_bytes(data_str.read(1), "little")
			self.unknown3 = int.from_bytes(data_str.read(1), "little")
			self.controls.parse(data_str)
			self.controls_noauto['algo'] = int.from_bytes(data_str.read(4), "little")
			self.poly = int.from_bytes(data_str.read(4), "little")
			self.presetname = data_str.read(32).split(b'\x00')[0].decode('ascii')
			presetpath_size = int.from_bytes(data_str.read(4), "little")
			self.presetpath = data_str.read(presetpath_size).split(b'\x00')[0].decode('ascii')
			self.visual['keyboard_octave'] = int.from_bytes(data_str.read(4), "little")
			self.patterns.parse(data_str)
		# -------------------------------- KSSynth --------------------------------
		elif self.mach_id == 'KSSN':
			self.unknown1 = int.from_bytes(data_str.read(2), "little")
			self.unknown2 = int.from_bytes(data_str.read(1), "little")
			self.unknown3 = int.from_bytes(data_str.read(1), "little")
			self.controls.parse(data_str)
			self.presetname = data_str.read(32).split(b'\x00')[0].decode('ascii')
			presetpath_size = int.from_bytes(data_str.read(4), "little")
			self.presetpath = data_str.read(presetpath_size).split(b'\x00')[0].decode('ascii')
			self.visual['keyboard_octave'] = int.from_bytes(data_str.read(4), "little")
			self.patterns.parse(data_str)
		# -------------------------------- SawSynth --------------------------------
		elif self.mach_id == 'SAWS':
			self.unknown1 = int.from_bytes(data_str.read(2), "little")
			self.unknown2 = int.from_bytes(data_str.read(1), "little")
			self.unknown3 = int.from_bytes(data_str.read(1), "little")
			self.controls.parse(data_str)
			self.presetname = data_str.read(32).split(b'\x00')[0].decode('ascii')
			presetpath_size = int.from_bytes(data_str.read(4), "little")
			self.presetpath = data_str.read(presetpath_size).split(b'\x00')[0].decode('ascii')
			self.visual['keyboard_octave'] = int.from_bytes(data_str.read(4), "little")
			self.poly = int.from_bytes(data_str.read(4), "little")
			self.patterns.parse(data_str)
		# -------------------------------- 8BitSynth --------------------------------
		elif self.mach_id == '8SYN':
			self.unknown1 = int.from_bytes(data_str.read(2), "little")
			self.unknown2 = int.from_bytes(data_str.read(1), "little")
			self.unknown3 = int.from_bytes(data_str.read(1), "little")
			self.controls.parse(data_str)
			self.controls_noauto['bitcode1'] = data_str.read(128).split(b'\x00')[0].decode('ascii')
			self.controls_noauto['bitcode2'] = data_str.read(128).split(b'\x00')[0].decode('ascii')
			self.unknown4 = int.from_bytes(data_str.read(4), "little")
			self.unknown5 = int.from_bytes(data_str.read(4), "little")
			self.presetname = data_str.read(32).split(b'\x00')[0].decode('ascii')
			presetpath_size = int.from_bytes(data_str.read(4), "little")
			self.presetpath = data_str.read(presetpath_size).split(b'\x00')[0].decode('ascii')
			self.visual['keyboard_octave'] = int.from_bytes(data_str.read(4), "little")
			self.patterns.parse(data_str)
		# -------------------------------- BeatBox --------------------------------
		elif self.mach_id == 'BBOX':
			self.unknown1 = int.from_bytes(data_str.read(2), "little")
			self.unknown2 = int.from_bytes(data_str.read(1), "little")
			self.unknown3 = int.from_bytes(data_str.read(1), "little")
			self.controls.parse(data_str)
			self.patterns.parse(data_str)
			data_str.read(4)
			self.presetpath = data_str.read(256).split(b'\x00')[0].decode('ascii')
			data_str.read(4)
			for _ in range(8):
				sampledata = {}
				sample_name = data_str.read(32).split(b'\x00')[0].decode('ascii')
				sample_len = int.from_bytes(data_str.read(4), "little")
				sample_hz = int.from_bytes(data_str.read(4), "little")
				sample_chan = int.from_bytes(data_str.read(4), "little")
				sample_data = data_str.read((sample_len*2)*sample_chan)
				print('[format-caustic] BBOX | len:'+str(sample_len)+', hz:'+str(sample_hz)+', ch:'+str(sample_chan))
				sampleinfo = {}
				sampleinfo['name'] = sample_name
				sampleinfo['hz'] = sample_hz
				sampleinfo['len'] = sample_len
				sampleinfo['chan'] = sample_chan
				self.samples.append([sampleinfo, sample_data])
		# -------------------------------- Vocoder --------------------------------
		elif self.mach_id == 'VCDR':
			self.unknown1 = int.from_bytes(data_str.read(2), "little")
			self.unknown2 = int.from_bytes(data_str.read(1), "little")
			self.unknown3 = int.from_bytes(data_str.read(1), "little")
			self.controls.parse(data_str)
			self.controls_noauto['currentnumber'] = int.from_bytes(data_str.read(4), "little")
			data_str.read(28)
			data_str.read(8)

			for _ in range(6):
				sample_name = data_str.read(256).split(b'\x00')[0].decode('ascii')
				data_str.read(4)
				sample_len = int.from_bytes(data_str.read(4), "little")
				sample_hz = int.from_bytes(data_str.read(4), "little")
				sample_data = data_str.read(sample_len*2)
				print('[format-caustic] VCDR | len:'+str(sample_len)+', hz:'+str(sample_hz))
				sampleinfo = {}
				sampleinfo['name'] = sample_name
				sampleinfo['len'] = sample_len
				sampleinfo['hz'] = sample_hz
				sampleinfo['data'] = sample_data
				self.samples.append([sampleinfo, sample_data])

			self.visual['keyboard_octave'] = int.from_bytes(data_str.read(4), "little")
			self.patterns.parse(data_str)
		# -------------------------------- Modular --------------------------------
		elif self.mach_id == 'MDLR': 
			modular_obj = caustic_modular()
			for m in modular_obj.slots: 
				m.slot_type = int.from_bytes(data_str.read(4), "little")

			for m in modular_obj.slots: 
				if m.slot_type != 0:
					if data_str.read(4) != b'MCOM': exit('[error] MCOM magic mismatch')
					MCOM_size = int.from_bytes(data_str.read(4), "little")
					m.params = struct.unpack("f"*(MCOM_size//4), data_str.read(MCOM_size))

			if data_str.read(4) != b'MCOM': exit('[error] MCOM magic mismatch')
			MCOM_size = int.from_bytes(data_str.read(4), "little")
			modular_obj.main.params = struct.unpack("f"*(MCOM_size//4), data_str.read(MCOM_size))

			self.controls.parse(data_str)
			data_str.read(5)
			self.unknown1 = int.from_bytes(data_str.read(4), "little")

			for linknum in range(int.from_bytes(data_str.read(4), "little")): modular_obj.connections.append(struct.unpack("i"*9, data_str.read(4*9)))

			self.extra = modular_obj
			self.patterns.parse(data_str)

		# -------------------------------- PCMSynth --------------------------------
		elif self.mach_id == 'PCMS': 
			self.unknown1 = int.from_bytes(data_str.read(2), "little")
			self.unknown2 = int.from_bytes(data_str.read(1), "little")
			self.unknown3 = int.from_bytes(data_str.read(1), "little")
			self.controls.parse(data_str)
			self.presetname = data_str.read(32).split(b'\x00')[0].decode('ascii')
			presetpath_size = int.from_bytes(data_str.read(4), "little")
			self.presetpath = data_str.read(presetpath_size).split(b'\x00')[0].decode('ascii')
			data_str.read(4)
			numsamples = int.from_bytes(data_str.read(4), "little")
			#print(numsamples)
			for _ in range(numsamples):
				region = {}
				region['volume'] = struct.unpack("f", data_str.read(4))[0]
				data_str.read(4)
				region['pan'] = struct.unpack("f", data_str.read(4))[0]
				region['key_root'] = int.from_bytes(data_str.read(4), "little")
				region['key_lo'] = int.from_bytes(data_str.read(4), "little")
				region['key_hi'] = int.from_bytes(data_str.read(4), "little")
				region['mode'] = int.from_bytes(data_str.read(4), "little")
				region['start'] = int.from_bytes(data_str.read(4), "little")
				region['end'] = int.from_bytes(data_str.read(4), "little")-1
				region['path'] = data_str.read(256).split(b'\x00')[0].decode('ascii')
				data_str.read(4)
				sample_len = int.from_bytes(data_str.read(4), "little")
				region['samp_hz'] = int.from_bytes(data_str.read(4), "little")
				data_str.read(4)
				sample_chan = int.from_bytes(data_str.read(4), "little")
				region['samp_len'] = sample_len
				region['samp_ch'] = sample_chan
				samp_data = data_str.read((sample_len*2)*sample_chan)
				self.samples.append([region, samp_data])
			data_str.read(9)
			self.patterns.parse(data_str)

class caustic_mixer:
	def __init__(self):
		self.data = None
		self.controls = caustic_controls()
		self.solo_mute = [0 for x in range(28)]
		self.controls = []
		self.chainnum = 0

	def parse(self):
		self.data.read(4)
		controls = caustic_controls()
		controls.parse(self.data)
		self.controls.append(controls)
		for n in range(14): self.solo_mute[(self.chainnum*2)+n] = self.data.read(1)[0]

		self.chainnum += 7

class caustic_fxslot:
	def __init__(self):
		self.controls = caustic_controls()
		self.mode = None
		self.fx_type = -1

	def parse(self, bio_in):
		self.fx_type = int.from_bytes(bio_in.read(4), "little")
		if self.fx_type == 0: #Delay
			self.controls.parse(bio_in)
			self.mode = int.from_bytes(bio_in.read(4), "little")
		if self.fx_type == 1: #Reverb
			self.controls.parse(bio_in)
		if self.fx_type == 2: #Distortion
			self.controls.parse(bio_in)
		if self.fx_type == 3: #Compresser
			self.controls.parse(bio_in)
			self.mode = int.from_bytes(bio_in.read(4), "little")
		if self.fx_type == 4: #Bitcrush
			self.controls.parse(bio_in)
		if self.fx_type == 5: #Flanger
			self.controls.parse(bio_in)
			self.mode = int.from_bytes(bio_in.read(4), "little")
		if self.fx_type == 6: #Phaser
			self.controls.parse(bio_in)
		if self.fx_type == 7: #Chorus
			self.controls.parse(bio_in)
			self.mode = int.from_bytes(bio_in.read(4), "little")
		if self.fx_type == 8: #AutoWah
			self.controls.parse(bio_in)
		if self.fx_type == 9: #Param EQ
			self.controls.parse(bio_in)
		if self.fx_type == 10: #Limiter
			self.controls.parse(bio_in)
		if self.fx_type == 11: #VInylSim
			self.controls.parse(bio_in)
		if self.fx_type == 12: #Comb
			self.controls.parse(bio_in)
		if self.fx_type == 14: #Cab Sim
			self.controls.parse(bio_in)
		if self.fx_type == 16: #StaticFlanger
			self.controls.parse(bio_in)
			self.mode = int.from_bytes(bio_in.read(4), "little")
		if self.fx_type == 17: #Filter
			self.controls.parse(bio_in)
			self.mode = int.from_bytes(bio_in.read(4), "little")
		if self.fx_type == 18: #Octaver
			self.controls.parse(bio_in)
		if self.fx_type == 19: #Vibrato
			self.controls.parse(bio_in)
			self.mode = int.from_bytes(bio_in.read(4), "little")
		if self.fx_type == 20: #Tremolo
			self.controls.parse(bio_in)
		if self.fx_type == 21: #AutoPan
			self.controls.parse(bio_in)

class caustic_fxchain:
	def __init__(self):
		self.data = None
		self.chainnum = 0
		self.fxslots = [caustic_fxslot() for x in range(28)]
	def parse(self):
		for n in range(14): self.fxslots[n+self.chainnum].parse(self.data)
		if self.chainnum == 0: self.data.read(4)
		self.chainnum += 14

class caustic_master:
	def __init__(self):
		self.data = None
		self.fxslots = [caustic_fxslot() for x in range(2)]
		self.controls = caustic_controls()
	def parse(self):
		for n in range(2): self.fxslots[n].parse(self.data)
		self.controls.parse(self.data)

class caustic_autoblocks:
	def __init__(self):
		self.ctrl_id = 0
		self.smooth = 0.5
		self.data = []

class caustic_pattern:
	def __init__(self):
		self.measures = 0
		self.numnote = 0
		self.notes = []

class caustic_patterns:
	def __init__(self):
		self.data = [caustic_pattern() for x in range(16*4)]
		self.auto = [{} for x in range(16*4)]

	def parse(self, data):
		print('[format-caustic] SPAT')
		if data.read(4) != b'SPAT': exit('[error] SPAT magic mismatch')

		SPAT_size = int.from_bytes(data.read(4), "little")
		SPAT_str = BytesIO(data.read(SPAT_size))

		for n in range(16*4): self.data[n].measures = int.from_bytes(SPAT_str.read(4), "little")
		for n in range(16*4): self.data[n].numnote = int.from_bytes(SPAT_str.read(4), "little")
		for n in range(16*4):
			for _ in range(self.data[n].numnote):
				plndata = struct.unpack("IIffIfBBBBfffffff", SPAT_str.read(56))
				if plndata[1] == 0:
					cnote = caustic_note()
					cnote.parse(plndata)
					self.data[n].notes.append(cnote)

		SPAT_str.read(512)
		unknown1 = struct.unpack("f", SPAT_str.read(4))
		autoctrlid = struct.unpack("I"*64, SPAT_str.read(4*64))

		SPAT_str.read(256) #print(struct.unpack("I"*64, SPAT_str.read(4*64)))
		SPAT_str.read(512)

		for n, i in enumerate(autoctrlid):
			for v in range(i):
				blockobj = caustic_autoblocks()
				blockobj.ctrl_id, blockobj.smooth = struct.unpack("I xxxx xxxx xxxx f xxxx", SPAT_str.read(24))
				patauto_measure = self.data[n].measures*32
				blockobj.data = struct.unpack("f"*patauto_measure, SPAT_str.read(4*patauto_measure))
				self.auto[n][blockobj.ctrl_id] = blockobj

class caustic_autoset:
	def __init__(self):
		self.data = {}

	def parse(self, data):
		numofautoctrl = int.from_bytes(data.read(4), "little")
		for ctrlauto_num in range(numofautoctrl):
			ctrlid = int.from_bytes(data.read(4), "little")
			n = int.from_bytes(data.read(4), "little")
			self.data[ctrlid] = []
			for _ in range(n):
				d = struct.unpack("IIIff", data.read(20))
				self.data[ctrlid].append([d[3], d[4]])

class caustic_note:
	def __init__(self):
		self.pos = None
		self.dur = None
		self.key = None
		self.vol = None
		self.mode = None

	def parse(self, plndata):
		self.pos = plndata[2]
		self.dur = plndata[3]
		self.key = plndata[6]
		self.mode = plndata[8]
		self.vol = plndata[16]

class caustic_placement:
	def __init__(self):
		self.pos = None
		self.dur = None
		self.mach = None
		self.pat = None

class caustic_arrangement:
	def __init__(self):
		self.pl = None

class caustic_sequence:
	def __init__(self):
		self.data = None
		self.parts = []
		self.notes = []
		self.tempoauto = []

		self.auto_mach = [caustic_autoset() for x in range(14)]
		self.auto_fx = [caustic_autoset() for x in range(2)]
		self.auto_mixer = [caustic_autoset() for x in range(2)]
		self.auto_master = caustic_autoset()

	def parse(self):
		header = struct.unpack("II", self.data.read(8))
		pl_count = header[1]
		pln = []
		for _ in range(pl_count):
			plndata = struct.unpack("IIffIfBBBBfffffff", self.data.read(56))
			if plndata[1] == 2:
				mpl = caustic_placement()
				mpl.pos = plndata[2]
				mpl.dur = plndata[3]
				mpl.mach = plndata[0]
				mpl.pat = plndata[6]+plndata[7]*256
				self.parts.append(mpl)
			if plndata[1] == 0:
				cnote = caustic_note()
				cnote.parse(plndata)
				self.notes.append(cnote)
		self.data.read(46)

		for m in self.auto_mach: m.parse(self.data)
		for m in self.auto_fx: m.parse(self.data)
		for m in self.auto_mixer: m.parse(self.data)
		self.auto_master.parse(self.data)
		self.data.read(2)
		n, s = struct.unpack("II", self.data.read(8))
		for _ in range(n): 
			p, v = struct.unpack("ff", self.data.read(8))
			self.tempoauto.append([p, v])

class caustic_project:

	def __init__(self, filestream):
		self.effx = caustic_fxchain()
		self.mixr = caustic_mixer()
		self.mstr = caustic_master()
		self.seqn = caustic_sequence()

		self.machines = [caustic_machine() for x in range(14)]

		self.tempo = 120
		self.numerator = 4

		self.effxnum = 0
		self.mixrnum = 0
		headername = filestream.read(4)
		ro_rack = data_bytes.iff_read(filestream, 0)

		for rod_rack in ro_rack:
			if rod_rack[0] == b'RACK':
				rackdata = rod_rack[1]
				bi_rack = data_bytes.to_bytesio(rackdata)

		racksize = len(bi_rack.getvalue())

		header = bi_rack.read(264)
		while racksize > bi_rack.tell():
			chunk_datatype = bi_rack.read(4)
			print('[format-caustic] main | chunk:', chunk_datatype)
			if chunk_datatype == b'OUTP': self.read_OUTP(bi_rack)
			elif chunk_datatype == b'EFFX': self.read_EFFX(bi_rack)
			elif chunk_datatype == b'MIXR': self.read_MIXR(bi_rack)
			elif chunk_datatype == b'MSTR': self.read_MSTR(bi_rack)
			elif chunk_datatype == b'SEQN': self.read_SEQN(bi_rack)
			else: 
				break

	def read_OUTP(self, bi_rack):
		OUTP_size = int.from_bytes(bi_rack.read(4), "little")
		OUTP_data = bi_rack.read(OUTP_size)

		self.tempo = struct.unpack("f", OUTP_data[82:86])[0]
		self.numerator = OUTP_data[86]

		for n in range(14):
			self.machines[n].mach_id = bi_rack.read(4).decode("utf-8")
			bi_rack.read(1)

		for n, machdata in enumerate(self.machines):
			print('[format-caustic] OUTP |', end=' ')
			print(machdata.mach_id, end='')
			if machdata.mach_id != 'NULL':
				machdata.name = bi_rack.read(10).decode().rstrip('\x00')
				mach_head = bi_rack.read(4)
				data_size = int.from_bytes(bi_rack.read(4), "little")
				print(', '+str(data_size))
				machdata.data = bi_rack.read(data_size)
			else: print()
			machdata.parse()

	def read_EFFX(self, bi_rack):
		data_size = int.from_bytes(bi_rack.read(4), "little")
		self.effx.data = BytesIO(bi_rack.read(data_size))
		self.effx.parse()
		if self.effxnum == 0: bi_rack.read(4)
		self.effxnum += 1

	def read_MIXR(self, bi_rack):
		data_size = int.from_bytes(bi_rack.read(4), "little")
		self.mixr.data = BytesIO(bi_rack.read(data_size))
		self.mixr.parse()
		if self.mixrnum == 0: bi_rack.read(4)
		self.mixrnum += 1

	def read_MSTR(self, bi_rack):
		data_size = int.from_bytes(bi_rack.read(4), "little")
		self.mstr.data = BytesIO(bi_rack.read(data_size))
		self.mstr.parse()

	def read_SEQN(self, bi_rack):
		data_size = int.from_bytes(bi_rack.read(4), "little")
		self.seqn.data = BytesIO(bi_rack.read(data_size))
		self.seqn.parse()
