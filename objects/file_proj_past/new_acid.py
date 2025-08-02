# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.data_bytes import bytereader
from objects.data_bytes import bytewriter
import logging
import zipfile
from objects.exceptions import ProjectFileParserException

VERBOSE = False
SHOWALL = False

# ---------------------- CHUNKS ----------------------

class chunk__unknown_data:
	def __init__(self, byr_stream):
		size = byr_stream.int32()
		self.unknowndata = []
		self.data_a = byr_stream.int32()
		self.data_b = byr_stream.float()
		self.data_c = byr_stream.int32()

class chunk__regiondata:
	def __init__(self, byr_stream):
		self.unknowndata = []
		self.unknowndata.append( byr_stream.uint32() )
		numchars1 = byr_stream.uint32()
		self.unknowndata.append( byr_stream.uint32() )
		self.unknowndata.append( byr_stream.uint32() )
		numchars2 = byr_stream.uint32()
		self.filename = byr_stream.string16(numchars1//2)
		self.filename2 = byr_stream.string16(numchars2//2)
		self.unknowndata.append( byr_stream.uint32() )
		self.unknowndata.append( byr_stream.uint32() )

class chunk__peak:
	def __init__(self, byr_stream):
		self.unknowndata = []
		self.unknowndata.append( byr_stream.int32() )
		self.unknowndata.append( byr_stream.int32() )
		self.unknowndata.append( byr_stream.int64() )
		self.unknowndata.append( byr_stream.float() )

class chunk__region:
	def __init__(self, byr_stream):
		size = byr_stream.int32()
		self.unknowndata = []
		self.unknowndata.append( byr_stream.int32() )
		self.flags = byr_stream.flags64()
		self.pos = byr_stream.int64()
		self.size = byr_stream.int64()
		self.offset = byr_stream.int64()
		self.pitch = byr_stream.double()
		self.unknowndata.append( byr_stream.double() )
		self.unknowndata.append( byr_stream.int32() )
		self.unknowndata.append( byr_stream.int32() )
		self.id = byr_stream.int32()
		self.unknowndata.append( byr_stream.int32() )
		self.index = byr_stream.int32()
		self.unknowndata.append( byr_stream.int32() )
		self.unknowndata.append( byr_stream.int32() )
		self.unknowndata.append( byr_stream.int32() )
		self.fade_in = byr_stream.int64()
		self.fade_out = byr_stream.int64()
		self.vol = byr_stream.float()

class chunk__maindata:
	def __init__(self, byr_stream):
		self.unknowndata = []
		size = byr_stream.int32()
		self.version = byr_stream.uint16()
		#if self.version>5:
		#	raise ProjectFileParserException('new_acid: Version '+str(self.version)+' is not supported.') 
		self.unknowndata.append( byr_stream.uint16() )
		self.unknowndata.append( byr_stream.uint32() )
		self.freq = byr_stream.uint32()
		self.unknowndata.append( byr_stream.double() )
		self.tempo = byr_stream.double()
		self.unknowndata.append( byr_stream.uint64() )
		self.timesig_num = byr_stream.uint16()
		self.timesig_denom = byr_stream.uint16()
		self.ppq = byr_stream.uint32()
		self.unknowndata.append( byr_stream.uint32() )
		self.unknowndata.append( byr_stream.uint32() )
		numchars1 = byr_stream.uint32()//2
		numchars2 = byr_stream.uint32()//2
		self.unknowndata.append( byr_stream.uint32() )
		self.unknowndata.append( byr_stream.uint32() )
		self.unknowndata.append( byr_stream.uint32() )
		self.unknowndata.append( byr_stream.uint32() )
		self.unknowndata.append( byr_stream.uint32() )
		self.unknowndata.append( byr_stream.uint32() )
		self.unknowndata.append( byr_stream.uint8() )
		self.unknowndata.append( byr_stream.uint8() )
		self.unknowndata.append( byr_stream.uint8() )
		self.unknowndata.append( byr_stream.uint8() )
		self.unknowndata.append( byr_stream.uint32() )
		self.file_project = byr_stream.string16(numchars1)
		self.file_prog = byr_stream.string16(numchars2)

class chunk__track_data:
	def __init__(self, byr_stream):
		self.unknowndata = []
		self.unknowndata.append( byr_stream.uint32() )
		self.unknowndata.append( byr_stream.uint32() )
		self.flags = byr_stream.flags32()
		self.size = byr_stream.uint32()
		self.type = byr_stream.uint32()
		self.color = byr_stream.uint32()
		self.stretchtype = byr_stream.uint32()
		self.id = byr_stream.uint32()
		stringsize1 = byr_stream.uint32()//2
		stringsize2 = byr_stream.uint32()//2
		self.numaudio = byr_stream.uint32()
		self.unknowndata.append( byr_stream.uint32() )
		self.seconds = byr_stream.uint32()/10000000
		self.unknowndata.append( byr_stream.uint32() )
		stringsize3 = byr_stream.uint32()//2
		self.unknowndata.append( byr_stream.uint32() )
		self.filename = byr_stream.string16(stringsize1)
		self.name = byr_stream.string16(stringsize2)
		#self.name2 = byr_stream.string16(stringsize3)

class chunk__audioinfo:
	def __init__(self, byr_stream):
		self.unknowndata = []
		self.unknowndata.append( byr_stream.int32() )
		self.unknowndata.append( byr_stream.int32() )
		self.unknowndata.append( byr_stream.int32() )
		self.vol = byr_stream.float()
		self.pan = byr_stream.float()
		self.unknowndata.append( byr_stream.int32() )
		self.unknowndata.append( byr_stream.float() )
		self.unknowndata.append( byr_stream.int32() )
		#self.unknowndata.append( byr_stream.rest() )

class chunk__marker:
	def __init__(self, byr_stream):
		size = byr_stream.uint32()
		byr_stream.skip(4)
		self.pos = byr_stream.int64()
		self.end = byr_stream.int64()
		self.id = byr_stream.int32()
		self.type = byr_stream.int32()
		numchars = byr_stream.int32()//2
		byr_stream.skip(4)
		self.name = byr_stream.string16(numchars)

class chunk__tempokeypoint:
	def __init__(self, byr_stream):
		size = byr_stream.uint32()
		self.unknowndata = []
		byr_stream.skip(4)
		self.pos_synctime = byr_stream.int64()
		self.pos_samples = byr_stream.int64()
		self.tempo = byr_stream.int32()
		self.base_note = byr_stream.int32()

class chunk__audiostretch:
	def __init__(self, byr_stream):
		size = byr_stream.uint32()
		self.unknowndata = []
		self.unknowndata.append( byr_stream.uint32() )
		self.flags = byr_stream.flags32()
		self.root_note = byr_stream.uint8()
		self.unknowndata.append( byr_stream.uint8() )
		self.unknowndata.append( byr_stream.uint8() )
		self.unknowndata.append( byr_stream.uint8() )
		self.unknowndata.append( byr_stream.uint8() )
		self.unknowndata.append( byr_stream.uint8() )
		self.unknowndata.append( byr_stream.uint8() )
		self.unknowndata.append( byr_stream.uint8() )
		self.downbeat_offset = byr_stream.uint32()
		self.timesig_num = byr_stream.uint16()
		self.timesig_denom = byr_stream.uint16()
		self.tempo = byr_stream.float()

class chunk__startingparam:
	def __init__(self, byr_stream):
		size = byr_stream.uint32()
		self.unknowndata = []
		self.unknowndata.append( byr_stream.uint32() )
		self.tempo = byr_stream.uint32()
		self.root_note = byr_stream.uint32()
		self.unknowndata.append( byr_stream.uint32() )
		self.unknowndata.append( byr_stream.uint32() )

class chunk__track_automation:
	def __init__(self, byr_stream):
		version = byr_stream.uint32()

		self.points = []
		self.unknowndata = []
		self.group = byr_stream.uint32()
		self.param = byr_stream.uint32()
		self.min = byr_stream.float()
		self.max = byr_stream.float()
		self.defv = byr_stream.float()
		self.numpoints = byr_stream.uint32()
		self.unknowndata.append( byr_stream.uint32() )

		if version == 80:
			for _ in range(self.numpoints):
				pointdata = []
				pointdata.append( byr_stream.uint32() )
				pointdata.append( byr_stream.int32() )
				pointdata.append( byr_stream.float() )
				pointdata.append( byr_stream.uint32() )
				pointdata.append( byr_stream.uint32() )
				pointdata.append( byr_stream.uint32() )
				#print(pointdata)
				self.points.append(pointdata)
		else:
			for _ in range(self.numpoints):
				pointdata = []
				pointdata.append( byr_stream.uint32() )
				pointdata.append( byr_stream.int32() )
				pointdata.append( byr_stream.float() )
				pointdata.append( byr_stream.uint32() )
				self.points.append(pointdata)

class chunk__audiodefinfo:
	def __init__(self, byr_stream):
		size = byr_stream.uint32()
		self.unknowndata = []
		self.unknowndata.append( byr_stream.uint32() )
		self.unknowndata.append( byr_stream.uint32() )
		self.color = byr_stream.uint32()
		self.unknowndata.append( byr_stream.uint32() )
		numchars1 = byr_stream.uint32()//2
		numchars2 = byr_stream.uint32()//2
		numchars3 = byr_stream.uint32()//2
		self.pitch = byr_stream.float()
		self.filename = byr_stream.string16(numchars1)
		self.filename2 = byr_stream.string16(numchars2)
		self.name = byr_stream.string16(numchars3)
		self.unknowndata.append( byr_stream.uint32() )
		self.unknowndata.append( byr_stream.uint32() )
		self.stretchtype = byr_stream.uint32()
		self.preserve_pitch = byr_stream.uint32()
		self.seconds = byr_stream.uint32()/10000000
		self.unknowndata.append( byr_stream.uint32() )
		self.stretch_algo = byr_stream.uint32()
		self.stretch_algo_mode = byr_stream.uint32()
		self.unknowndata.append( byr_stream.uint32() )
		self.formant_shift = byr_stream.float()
		self.unknowndata.append( byr_stream.float() )
		self.unknowndata.append( byr_stream.uint32() )

class chunk__metadata:
	def __init__(self, byr_stream):
		self.unk1 = byr_stream.uint32()
		self.metadata = {}
		for _ in range(byr_stream.uint32()):
			chunk_name = byr_stream.raw(4)
			chunk_data = byr_stream.string16(byr_stream.uint32()//2)
			self.metadata[chunk_name] = chunk_data

chunksdef = {}
chunksdef['754be33a5ef5ec44a2f0f4eb3c53af7d'] = chunk__peak
chunksdef['6a208d162123d21186b000c04f8edb8a'] = chunk__region
chunksdef['5a2d8fb20f23d21186af00c04f8edb8a'] = chunk__maindata
chunksdef['49076c4d1623d21186b000c04f8edb8a'] = chunk__track_data
chunksdef['276cd4690b7fd211871700c04f8edb8a'] = chunk__audioinfo
chunksdef['4212abe5d43b1e439148fb80c038eaeb'] = chunk__unknown_data
chunksdef['5d2d8fb20f23d21186af00c04f8edb8a'] = chunk__regiondata
chunksdef['5662f7ab2d39d21186c700c04f8edb8a'] = chunk__marker
chunksdef['07521655f6713e4e83be9dee9c5ba303'] = chunk__tempokeypoint
chunksdef['5287535c45e3784f83b8551935b4c6f7'] = chunk__audiostretch
chunksdef['be3967941a398443878538bda35f409a'] = chunk__startingparam
chunksdef['5c1b70846368d21186fd00c04f8edb8a'] = chunk__track_automation
chunksdef['44030abfa7f8f44788cba63c7756ba9e'] = chunk__audiodefinfo
chunksdef['1d4f23715752d21186dc00c04f8edb8a'] = chunk__metadata

# ---------------------- INDATA ----------------------

verboseid = {}
verboseid['5a2d8fb20f23d21186af00c04f8edb8a'] = 'MainData'
verboseid['49076c4d1623d21186b000c04f8edb8a'] = 'TrackData'
verboseid['276cd4690b7fd211871700c04f8edb8a'] = 'TrackAudioInfo'
verboseid['3e0c0223541dfc44aab68330c9121f22'] = 'TrackMIDIInfo'
verboseid['6a208d162123d21186b000c04f8edb8a'] = 'TrackRegion'
verboseid['d0fb0bbbaec4044685662b4bf9cccbb5'] = 'TrackSFolder'
verboseid['2b959c4d344c664295f519126b4420a8'] = 'TrackSTrack'
verboseid['9d74b872ab14884594a939343aeef7cc'] = 'MixerChannel'
verboseid['a132b74c04e40d498806ede87d7d2c4f'] = 'TrackGroove'
verboseid['5c1b70846368d21186fd00c04f8edb8a'] = 'TrackAutomation'
verboseid['1b1ce45016af194e8cdba707237b7921'] = 'GrooveInfo'
verboseid['b5c7e0971f2d46449de8c07ff6f43b3b'] = 'RegionData'
verboseid['5662f7ab2d39d21186c700c04f8edb8a'] = 'Marker'
verboseid['754be33a5ef5ec44a2f0f4eb3c53af7d'] = 'Peak?'
verboseid['4212abe5d43b1e439148fb80c038eaeb'] = 'V3Peak?'
verboseid['5287535c45e3784f83b8551935b4c6f7'] = 'AudioStretch'
verboseid['07521655f6713e4e83be9dee9c5ba303'] = 'TempoKeyPoint'
verboseid['44030abfa7f8f44788cba63c7756ba9e'] = 'AudioDef:Info'
verboseid['5d2d8fb20f23d21186af00c04f8edb8a'] = 'RegionData'
verboseid['be3967941a398443878538bda35f409a'] = 'StartingParams'
verboseid['1d4f23715752d21186dc00c04f8edb8a'] = 'MetaData'

verboseid['a95c808a7402c242b8b9572f6786317c'] = 'Group:AudioDefList'
verboseid['1d54047b1c0adc4faeb3d4935206611d'] = 'Group:AudioDef'
verboseid['5b2d8fb20f23d21186af00c04f8edb8a'] = 'Group:RegionDatas'
verboseid['a59e8054b89bcd458d2b3ef94586a8e0'] = 'Group:GroovePool'
verboseid['48076c4d1623d21186b000c04f8edb8a'] = 'Group:Track'
verboseid['47076c4d1623d21186b000c04f8edb8a'] = 'Group:TrackList'
verboseid['e42b0d22d37fd211871800c04f8edb8a'] = 'Group:Mixer'
verboseid['f40e02902d39d21186c700c04f8edb8a'] = 'Group:Markers'
verboseid['172d16be624d2c48b80bfcf30fa53b02'] = 'Group:Peaks'
verboseid['4a076c4d1623d21186b000c04f8edb8a'] = 'Group:Regions'
verboseid['266cd4690b7fd211871700c04f8edb8a'] = 'Group:AudioInfo'
verboseid['07521655f6713e4e83be9dee9c5ba303'] = 'Group:TempoKeyPoints'
verboseid['5287535c45e3784f83b8551935b4c6f7'] = 'Group:AudioStretch'
verboseid['be3967941a398443878538bda35f409a'] = 'Group:StartingParams'
verboseid['5d1b70846368d21186fd00c04f8edb8a'] = 'Group:TrackAuto'
verboseid['bc945f925a52d21186dc00c04f8edb8a'] = 'Group:MetaData'

class sony_acid_chunk:
	def __init__(self):
		self.id = None
		self.size = 0
		self.start = 0
		self.end = 0
		self.is_list = False
		self.in_data = []
		self.content = None

	def __getitem__(self, v):
		return self.in_data[v]

	def __iter__(self):
		return self.in_data.__iter__()

	def __repr__(self):
		idname = self.id.hex()
		if idname in verboseid: visname = verboseid[idname]
		else: visname = 'UnknownData:'+self.id.hex()
		return '<SF ACID Chunk - %s>' % visname

	def iter_wtypes(self):
		for x in self.in_data.__iter__():
			idname = x.id.hex()
			yield x, verboseid[idname] if idname in verboseid else None

	def read(self, byr_stream, tnum):
		self.id = byr_stream.raw(16)
		self.size = byr_stream.uint64()-24
		self.start = byr_stream.tell_real()
		self.is_list = self.id[0:4] in [b'riff', b'list']

		if self.is_list:
			self.id = byr_stream.raw(16)
			gidname = self.id.hex()
			if gidname in verboseid: gidname = verboseid[gidname]
			if VERBOSE: print('\t'*tnum, '$Group %s \\' % gidname)
			with byr_stream.isolate_size(self.size-16, True) as bye_stream: 
				while bye_stream.remaining():
					inchunk = sony_acid_chunk()
					inchunk.read(bye_stream, tnum+1)
					self.in_data.append(inchunk)
			if VERBOSE: print('\t'*tnum, '       /')

		else:
			idname = self.id.hex()

			if VERBOSE:
				if idname in verboseid: visname = verboseid[idname]
				else: visname = 'UnknownData:'+self.id.hex()
				print('\t'*tnum,  visname)

			if idname in chunksdef and not SHOWALL: 
				with byr_stream.isolate_size(self.size, True) as bye_stream:
					self.content = chunksdef[idname](bye_stream)
				#print(byr_stream.raw(self.size).hex())
			else:
				if VERBOSE: print('\t'*tnum,  byr_stream.raw(self.size).hex())
				else: byr_stream.skip(self.size)

class sony_acid_song:
	def __init__(self):
		self.root = sony_acid_chunk()
		self.zipped = False
		self.zipfile = None

	def load_from_file(self, input_file):
		self.zipped = False
		self.zipfile = None

		byr_stream = bytereader.bytereader()
		byr_stream.load_file(input_file)

		if byr_stream.read(2) == b'PK':
			self.zipped = True
			self.zipfile = zipfile.ZipFile(input_file, 'r')
			acdfound = False
			for filename in self.zipfile.namelist():
				if filename.endswith('.acd'):
					byr_stream.load_raw(self.zipfile.read(filename))
					acdfound = True
			if not acdfound:
				raise ProjectFileParserException('new_acid: ACID file not found in zip')
		byr_stream.seek(0)

		self.root = sony_acid_chunk()
		self.root.read(byr_stream, 0)
		return True

#apeinst_obj = sony_acid_song()
#apeinst_obj.load_from_file("testin.acd")
