# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.data_bytes import bytereader
import numpy as np
from objects.exceptions import ProjectFileParserException

import logging
logger_projparse = logging.getLogger('projparse')

class caustic_controls:
	def __init__(self):
		self.data = {}

	def parse(self, song_data):
		song_data.magic_check(b'CCOL')
		CCOL_size = song_data.uint32()
		startpos = song_data.tell()
		trk_iff_obj = song_data.chunk_objmake()
		for chunk_obj in trk_iff_obj.iter(startpos, startpos+CCOL_size):
			pid = song_data.uint32()
			self.data[pid] = song_data.float()
		song_data.skip(CCOL_size)
		logger_projparse.info('caustic3: CCOL | '+str(len(self.data))+' Controls')

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

	def parse(self, song_data):
		# -------------------------------- SubSynth --------------------------------
		if self.mach_id == 'SSYN':
			self.unknown1 = song_data.uint16()
			self.unknown2 = song_data.uint8()
			self.unknown3 = song_data.uint8()
			self.controls.parse(song_data)
			self.presetname = song_data.string(32)
			self.presetpath = song_data.c_string__int32(False)
			self.unknown4 = song_data.uint32()
			self.customwaveform1 = song_data.l_int16(660)
			self.customwaveform2 = song_data.l_int16(660)
			self.controls_noauto['poly'] = song_data.uint32()
			self.controls_noauto['osc1_mode'] = song_data.uint32()
			self.controls_noauto['osc2_mode'] = song_data.uint32()
			self.patterns.parse(song_data)
		# -------------------------------- BassLine --------------------------------
		elif self.mach_id == 'BLNE':
			self.unknown1 = song_data.uint16()
			self.unknown2 = song_data.uint8()
			self.unknown3 = song_data.uint8()
			self.controls.parse(song_data)
			self.presetname = song_data.string(32)
			self.presetpath = song_data.c_string__int32(False)
			self.visual['keyboard_octave'] = song_data.uint32()
			self.patterns.parse(song_data)
			self.controls_noauto['legacy_glide'] = song_data.float()
			self.customwaveform1 = song_data.l_int16(660)
		# -------------------------------- PadSynth --------------------------------
		elif self.mach_id == 'PADS':
			self.controls.parse(song_data)
			self.presetname = song_data.string(32)
			self.presetpath = song_data.c_string__int32(False)
			self.visual['keyboard_octave'] = song_data.uint32()
			self.unknown1 = song_data.uint32()
			self.visual['visual'] = song_data.uint32()
			self.controls_noauto['harm1'] = song_data.l_float(24)
			self.controls_noauto['harm1vol'] = song_data.float()
			self.controls_noauto['harm2'] = song_data.l_float(24)
			self.controls_noauto['harm2vol'] = song_data.float()
			self.patterns.parse(song_data)
		# -------------------------------- Organ --------------------------------
		elif self.mach_id == 'ORGN':
			self.controls.parse(song_data)
			self.presetname = song_data.string(32)
			self.presetpath = song_data.c_string__int32(False)
			self.visual['keyboard_octave'] = song_data.uint32()
			self.unknown1 = song_data.uint32()
		# -------------------------------- FMSynth --------------------------------
		elif self.mach_id == 'FMSN':
			self.unknown1 = song_data.uint16()
			self.unknown2 = song_data.uint8()
			self.unknown3 = song_data.uint8()
			self.controls.parse(song_data)
			self.controls_noauto['algo'] = song_data.uint32()
			self.poly = song_data.uint32()
			self.presetname = song_data.string(32)
			self.presetpath = song_data.c_string__int32(False)
			self.visual['keyboard_octave'] = song_data.uint32()
			self.patterns.parse(song_data)
		# -------------------------------- KSSynth --------------------------------
		elif self.mach_id == 'KSSN':
			self.unknown1 = song_data.uint16()
			self.unknown2 = song_data.uint8()
			self.unknown3 = song_data.uint8()
			self.controls.parse(song_data)
			self.presetname = song_data.string(32)
			self.presetpath = song_data.c_string__int32(False)
			self.visual['keyboard_octave'] = song_data.uint32()
			self.patterns.parse(song_data)
		# -------------------------------- SawSynth --------------------------------
		elif self.mach_id == 'SAWS':
			self.unknown1 = song_data.uint16()
			self.unknown2 = song_data.uint8()
			self.unknown3 = song_data.uint8()
			self.controls.parse(song_data)
			self.presetname = song_data.string(32)
			self.presetpath = song_data.c_string__int32(False)
			self.visual['keyboard_octave'] = song_data.uint32()
			self.poly = song_data.uint32()
			self.patterns.parse(song_data)
		# -------------------------------- 8BitSynth --------------------------------
		elif self.mach_id == '8SYN':
			self.unknown1 = song_data.uint16()
			self.unknown2 = song_data.uint8()
			self.unknown3 = song_data.uint8()
			self.controls.parse(song_data)
			self.controls_noauto['bitcode1'] = song_data.string(128)
			self.controls_noauto['bitcode2'] = song_data.string(128)
			self.unknown4 = song_data.uint32()
			self.unknown5 = song_data.uint32()
			self.presetname = song_data.string(32)
			self.presetpath = song_data.c_string__int32(False)
			self.visual['keyboard_octave'] = song_data.uint32()
			self.patterns.parse(song_data)
		# -------------------------------- BeatBox --------------------------------
		elif self.mach_id == 'BBOX':
			self.unknown1 = song_data.uint16()
			self.unknown2 = song_data.uint8()
			self.unknown3 = song_data.uint8()
			self.controls.parse(song_data)
			self.patterns.parse(song_data)
			song_data.skip(4)
			self.presetpath = song_data.string(256)
			song_data.skip(4)
			for _ in range(8):
				sampledata = {}
				sample_name = song_data.string(32)
				sample_len = song_data.uint32()
				sample_hz = song_data.uint32()
				sample_chan = song_data.uint32()
				sample_data = song_data.read((sample_len*2)*sample_chan)
				logger_projparse.info('caustic3: BBOX | len:'+str(sample_len)+', hz:'+str(sample_hz)+', ch:'+str(sample_chan))
				sampleinfo = {}
				sampleinfo['name'] = sample_name
				sampleinfo['hz'] = sample_hz
				sampleinfo['len'] = sample_len
				sampleinfo['chan'] = sample_chan
				self.samples.append([sampleinfo, sample_data])
		# -------------------------------- Vocoder --------------------------------
		elif self.mach_id == 'VCDR':
			self.unknown1 = song_data.uint16()
			self.unknown2 = song_data.uint8()
			self.unknown3 = song_data.uint8()
			self.controls.parse(song_data)
			self.controls_noauto['currentnumber'] = song_data.uint32()
			song_data.read(28)
			song_data.read(8)

			for _ in range(6):
				sample_name = song_data.string(256)
				song_data.skip(4)
				sample_len = song_data.uint32()
				sample_hz = song_data.uint32()
				sample_data = song_data.read(sample_len*2)
				logger_projparse.info('caustic3: VCDR | len:'+str(sample_len)+', hz:'+str(sample_hz))
				sampleinfo = {}
				sampleinfo['name'] = sample_name
				sampleinfo['len'] = sample_len
				sampleinfo['hz'] = sample_hz
				sampleinfo['data'] = sample_data
				self.samples.append([sampleinfo, sample_data])

			self.visual['keyboard_octave'] = song_data.uint32()
			self.patterns.parse(song_data)
		# -------------------------------- Modular --------------------------------
		elif self.mach_id == 'MDLR': 
			modular_obj = caustic_modular()
			for m in modular_obj.slots:  m.slot_type = song_data.uint32()

			for m in modular_obj.slots: 
				if m.slot_type != 0:
					song_data.magic_check(b'MCOM')
					m.params = song_data.l_float(song_data.uint32()//4)

			song_data.magic_check(b'MCOM')
			modular_obj.main.params = song_data.l_float(song_data.uint32()//4)
			self.controls.parse(song_data)
			song_data.read(5)
			self.unknown1 = song_data.uint32()
			for linknum in range(song_data.uint32()): modular_obj.connections.append( song_data.l_uint32(9) )
			self.extra = modular_obj
			self.patterns.parse(song_data)

		# -------------------------------- PCMSynth --------------------------------
		elif self.mach_id == 'PCMS': 
			self.unknown1 = song_data.uint16()
			self.unknown2 = song_data.uint8()
			self.unknown3 = song_data.uint8()
			self.controls.parse(song_data)
			self.presetname = song_data.string(32)
			presetpath_size = song_data.uint32()
			self.presetpath = song_data.string(presetpath_size)
			song_data.skip(4)
			numsamples = song_data.uint32()
			#print(numsamples)
			for _ in range(numsamples):
				region = {}
				region['volume'] = song_data.float()
				song_data.skip(4)
				region['pan'] = song_data.float()
				region['key_root'] = song_data.uint32()
				region['key_lo'] = song_data.uint32()
				region['key_hi'] = song_data.uint32()
				region['mode'] = song_data.uint32()
				region['start'] = song_data.uint32()
				region['end'] = song_data.uint32()-1
				region['path'] = song_data.string(256)
				song_data.skip(4)
				sample_len = song_data.uint32()
				region['samp_hz'] = song_data.uint32()
				song_data.skip(4)
				sample_chan = song_data.uint32()
				region['samp_len'] = sample_len
				region['samp_ch'] = sample_chan
				samp_data = song_data.read((sample_len*2)*sample_chan)
				self.samples.append([region, samp_data])
			song_data.read(9)
			self.patterns.parse(song_data)

class caustic_mixer:
	def __init__(self):
		self.controls = caustic_controls()
		self.solo_mute = [0 for x in range(28)]
		self.controls = []
		self.chainnum = 0

	def parse(self, song_data):
		song_data.skip(4)
		controls = caustic_controls()
		controls.parse(song_data)
		self.controls.append(controls)
		for n in range(14): self.solo_mute[(self.chainnum*2)+n] = song_data.uint8()
		self.chainnum += 7

class caustic_fxslot:
	def __init__(self):
		self.controls = caustic_controls()
		self.mode = 0
		self.fx_type = -1

	def parse(self, song_data):
		self.fx_type = song_data.uint32()
		if self.fx_type == 0: #Delay
			self.controls.parse(song_data)
			self.mode = song_data.uint32()
		if self.fx_type == 1: #Reverb
			self.controls.parse(song_data)
		if self.fx_type == 2: #Distortion
			self.controls.parse(song_data)
		if self.fx_type == 3: #Compresser
			self.controls.parse(song_data)
			self.mode = song_data.uint32()
		if self.fx_type == 4: #Bitcrush
			self.controls.parse(song_data)
		if self.fx_type == 5: #Flanger
			self.controls.parse(song_data)
			self.mode = song_data.uint32()
		if self.fx_type == 6: #Phaser
			self.controls.parse(song_data)
		if self.fx_type == 7: #Chorus
			self.controls.parse(song_data)
			self.mode = song_data.uint32()
		if self.fx_type == 8: #AutoWah
			self.controls.parse(song_data)
		if self.fx_type == 9: #Param EQ
			self.controls.parse(song_data)
		if self.fx_type == 10: #Limiter
			self.controls.parse(song_data)
		if self.fx_type == 11: #VInylSim
			self.controls.parse(song_data)
		if self.fx_type == 12: #Comb
			self.controls.parse(song_data)
		if self.fx_type == 14: #Cab Sim
			self.controls.parse(song_data)
		if self.fx_type == 16: #StaticFlanger
			self.controls.parse(song_data)
			self.mode = song_data.uint32()
		if self.fx_type == 17: #Filter
			self.controls.parse(song_data)
			self.mode = song_data.uint32()
		if self.fx_type == 18: #Octaver
			self.controls.parse(song_data)
		if self.fx_type == 19: #Vibrato
			self.controls.parse(song_data)
			self.mode = song_data.uint32()
		if self.fx_type == 20: #Tremolo
			self.controls.parse(song_data)
		if self.fx_type == 21: #AutoPan
			self.controls.parse(song_data)

class caustic_fxchain:
	def __init__(self):
		self.chainnum = 0
		self.fxslots = [caustic_fxslot() for x in range(28)]
	def parse(self, song_data):
		for n in range(14): 
			self.fxslots[n+self.chainnum].parse(song_data)
		if self.chainnum == 0: song_data.read(4)
		self.chainnum += 14

class caustic_master:
	def __init__(self):
		self.fxslots = [caustic_fxslot() for x in range(2)]
		self.controls = caustic_controls()
	def parse(self, song_data):
		for n in range(2): self.fxslots[n].parse(song_data)
		self.controls.parse(song_data)

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

	def parse(self, song_data):
		logger_projparse.info('caustic3: SPAT')
		song_data.magic_check(b'SPAT')

		SPAT_size = song_data.uint32()
		end_pos = song_data.tell()+SPAT_size

		for n in range(16*4): self.data[n].measures = song_data.uint32()
		for n in range(16*4): self.data[n].numnote = song_data.uint32()
		for n in range(16*4):
			pln = np.frombuffer(song_data.read(56*self.data[n].numnote), dtype=dtype_notearr)
			self.data[n].notes = pln[np.where(pln['type']==0)]

		song_data.skip(512)
		unknown1 = song_data.float()
		autoctrlid = song_data.l_uint32(64)

		song_data.skip(256)
		song_data.skip(512)

		for n, i in enumerate(autoctrlid):
			for v in range(i):
				blockobj = caustic_autoblocks()
				autoblkhdr = np.frombuffer(song_data.read(24), dtype=[('ctrl_id', np.int32),('unk2', np.single),('unk3', np.single),('unk4', np.single),('smooth', np.single),('unk6', np.single)])[0]
				blockobj.ctrl_id = autoblkhdr['ctrl_id']
				blockobj.smooth = autoblkhdr['smooth']
				blockobj.data = song_data.l_float(self.data[n].measures*32)
				self.auto[n][blockobj.ctrl_id] = blockobj

		song_data.seek(end_pos)

dtype_notearr = np.dtype([
	('mach', np.int32), 
	('type', np.int32), 
	('pos', np.single), 
	('dur', np.single),

	('unk1', np.int32),
	('unk2', np.single), 

	('key', np.int8), 
	('unk4', np.int8), 
	('mode', np.int8), 
	('unk6', np.int8), 

	('unk7', np.single), 
	('unk8', np.int32), 
	('unk9', np.single), 
	('unk10', np.single), 
	('unk11', np.single), 
	('unk12', np.single), 
	('vol', np.single), 
	]) 

dtype_autoset = np.dtype([
	('unk1', np.int32),
	('unk2', np.int32),
	('id', np.int32),
	('pos', np.single),
	('val', np.single)
	]) 

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
				ctrldata = data.read(20)
				ctrlp = np.frombuffer(ctrldata, dtype=dtype_autoset)
				self.data[ctrlid].append(ctrlp)

class caustic_sequence:
	def __init__(self):
		self.parts = []
		self.notes = []
		self.tempoauto = []

		self.auto_mach = [caustic_autoset() for x in range(14)]
		self.auto_fx = [caustic_autoset() for x in range(2)]
		self.auto_mixer = [caustic_autoset() for x in range(2)]
		self.auto_master = caustic_autoset()

	def parse(self, song_data):
		song_data.skip(4)
		pl_count = song_data.uint32()

		pln = np.frombuffer(song_data.read(56*pl_count), dtype=dtype_notearr)

		for _ in range(pl_count):
			np.where(pln['type']==2)
			self.parts = pln[np.where(pln['type']==2)]
			self.notes = pln[np.where(pln['type']==0)]

		song_data.read(46)

		for m in self.auto_mach: m.parse(song_data)
		for m in self.auto_fx: m.parse(song_data)
		for m in self.auto_mixer: m.parse(song_data)
		self.auto_master.parse(song_data)
		song_data.skip(2)
		n = song_data.uint32()
		s = song_data.uint32()
		for _ in range(n): self.tempoauto.append(song_data.l_float(2))

class caustic_project:

	def load_from_file(self, input_file):
		song_data = bytereader.bytereader()
		song_data.load_file(input_file)

		self.effx = caustic_fxchain()
		self.mixr = caustic_mixer()
		self.mstr = caustic_master()
		self.seqn = caustic_sequence()

		self.machines = [caustic_machine() for x in range(14)]

		self.tempo = 120
		self.numerator = 4

		self.effxnum = 0
		self.mixrnum = 0

		rackchunkfound = False
		main_iff_obj = song_data.chunk_objmake()
		for chunk_obj in main_iff_obj.iter(0, song_data.end):
			if chunk_obj.id == b'RACK':
				rackchunkfound = True
				header = song_data.read(4)
				name = song_data.read(260)
				while chunk_obj.end > song_data.tell():
					chunk_datatype = song_data.read(4)
					logger_projparse.info('caustic3: main | chunk: '+str(chunk_datatype))
					if chunk_datatype == b'OUTP': self.read_OUTP(song_data)
					elif chunk_datatype == b'EFFX': self.read_EFFX(song_data)
					elif chunk_datatype == b'MIXR': self.read_MIXR(song_data)
					elif chunk_datatype == b'MSTR': self.read_MSTR(song_data)
					elif chunk_datatype == b'SEQN': self.read_SEQN(song_data)
					else: break
		if not rackchunkfound:
			raise ProjectFileParserException('Caustic3: RACK chunk not found')
		else:
			return True

	def read_OUTP(self, song_data):
		OUTP_size = song_data.uint32()

		with song_data.isolate_size(OUTP_size, True) as outp_data:
			outp_data.skip(82)
			self.tempo = outp_data.float()
			self.numerator = outp_data.uint8()

		for n in range(14):
			self.machines[n].mach_id = song_data.string(4)
			song_data.skip(1)

		for n, machdata in enumerate(self.machines):
			logger_projparse.info('caustic3: OUTP | '+machdata.mach_id)
			if machdata.mach_id != 'NULL':
				machdata.name = song_data.string(10)
				mach_head = song_data.raw(4)
				data_size = song_data.uint32()
				with song_data.isolate_size(data_size, True) as mach_data: machdata.parse(mach_data)

	def read_EFFX(self, song_data):
		data_size = song_data.uint32()
		with song_data.isolate_size(data_size, True) as effx_data:
			self.effx.parse(effx_data)
			if self.effxnum == 0: effx_data.read(4)
		if self.effxnum == 0: song_data.read(4)
		self.effxnum += 1

	def read_MIXR(self, song_data):
		data_size = song_data.uint32()
		with song_data.isolate_size(data_size, True) as mixr_data: self.mixr.parse(mixr_data)
		if self.mixrnum == 0: song_data.read(4)
		self.mixrnum += 1

	def read_MSTR(self, song_data):
		data_size = song_data.uint32()
		with song_data.isolate_size(data_size, True) as mstr_data: self.mstr.parse(mstr_data)

	def read_SEQN(self, song_data):
		data_size = song_data.uint32()
		with song_data.isolate_size(data_size, True) as seqn_data: self.seqn.parse(seqn_data)