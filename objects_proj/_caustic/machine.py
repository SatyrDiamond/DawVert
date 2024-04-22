
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

		self.controls = controls.caustic_controls()

		self.controls_noauto = {}
		self.visual = {}

		self.samples = []

		self.patterns = sequence.caustic_patterns()

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
					if data_str.read(4) != b'MCOM': exit('Invalid MCOM')
					MCOM_size = int.from_bytes(data_str.read(4), "little")
					m.params = struct.unpack("f"*(MCOM_size//4), data_str.read(MCOM_size))

			if data_str.read(4) != b'MCOM': exit('Invalid MCOM')
			MCOM_size = int.from_bytes(data_str.read(4), "little")
			modular_obj.main.params = struct.unpack("f"*(MCOM_size//4), data_str.read(MCOM_size))

			self.controls.parse(data_str)
			data_str.read(5)
			self.unknown1 = int.from_bytes(data_str.read(4), "little")

			for linknum in range(int.from_bytes(data_str.read(4), "little")): modular_obj.connections.append(struct.unpack("i"*9, data_str.read(4*9)))

			self.extra = modular_obj
			self.patterns.parse(data_str)
