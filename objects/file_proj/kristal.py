# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.data_bytes import bytereader
import logging

VERBOSE = False

# ==================================== MAIN CHUNKS ====================================

class CProjectInfo:
	def __init__(self, byr_stream):
		if VERBOSE: print()
		if byr_stream.uint32()!=1: exit('CProjectInfo is not 1')
		self.data = [byr_stream.string_t() for x in range(byr_stream.uint32())]

class CAudioEngine:
	def __init__(self, byr_stream):
		unks = []
		if byr_stream.uint32()!=1: exit('CAudioEngine is not 1')
		self.freq = byr_stream.float()
		self.unk = byr_stream.uint32()
		unks.append(byr_stream.uint32())
		unks.append(byr_stream.uint32())
		self.freq_total = byr_stream.uint32()
		if VERBOSE: print(unks)

class CMixer:
	def __init__(self, byr_stream):
		if byr_stream.uint32()!=1: exit('CMixer is not 1')
		self.vol_l = byr_stream.float()
		self.vol_r = byr_stream.float()
		self.pan = byr_stream.float()
		self.num_tracks = byr_stream.uint32()
		if VERBOSE: print(self.vol_l, self.vol_r)

class CMixerChannel:
	def __init__(self, byr_stream):
		if byr_stream.uint32()!=1: exit('CMixerChannel is not 1')
		self.vol = byr_stream.float()
		self.pan = byr_stream.float()
		self.muted = byr_stream.uint8()
		self.solo = byr_stream.uint8()
		if VERBOSE: print(self.vol, self.pan)

class CInsertProcessor:
	def __init__(self, byr_stream):
		if byr_stream.uint32()!=1: exit('CInsertProcessor is not 1')
		self.slots_enabled = list(byr_stream.l_uint8(byr_stream.uint32()))
		if VERBOSE: print(self.slots_enabled)

class CTransport:
	def __init__(self, byr_stream):
		if byr_stream.uint32()!=2: exit('CTransport is not 2')
		unks = []
		unks.append(byr_stream.uint32())
		unks.append(byr_stream.uint32())
		unks.append(byr_stream.uint32())
		unks.append(byr_stream.uint16())
		unks.append(byr_stream.uint32())
		unks.append(byr_stream.uint32())
		unks.append(byr_stream.uint16())
		unks.append(byr_stream.uint8())
		unks.append(byr_stream.uint32())
		unks.append(byr_stream.uint32())
		unks.append(byr_stream.uint32())
		if VERBOSE: print(unks)

class CMetronome:
	def __init__(self, byr_stream):
		if byr_stream.uint32()!=1: exit('CMetronome is not 1')
		self.enabled = byr_stream.uint8()
		self.bpm = byr_stream.uint32()
		self.vol = byr_stream.float()
		if VERBOSE: print(self.enabled, self.bpm)

class WindowLayout:
	def __init__(self, byr_stream):
		if byr_stream.uint32()!=1: exit('WindowLayout is not 1')
		unks = []
		unks.append(byr_stream.uint32())
		unks.append(byr_stream.uint32())
		unks.append(byr_stream.uint32())
		if VERBOSE: print(unks)

class TransportPanel:
	def __init__(self, byr_stream):
		unks = []
		unks.append(byr_stream.uint8())
		unks.append(byr_stream.uint32())
		unks.append(byr_stream.uint32())
		unks.append(byr_stream.uint32())
		unks.append(byr_stream.uint32())
		if VERBOSE: print(unks)

class Console:
	def __init__(self, byr_stream):
		unks = []
		unks.append(byr_stream.uint8())
		unks.append(byr_stream.uint32())
		unks.append(byr_stream.uint32())
		unks.append(byr_stream.uint32())
		unks.append(byr_stream.uint32())
		if VERBOSE: print(unks)

		#unks = []
		#unks.append(byr_stream.uint32())
		#print(unks)

def iter_stringchunk(byr_stream):
	name = byr_stream.string_t()
	outchunk = None
	if VERBOSE: print('CHUNK >', name.ljust(20), end=' - ')
	if name == 'CProjectInfo': outchunk = CProjectInfo(byr_stream)
	elif name == 'CAudioEngine': outchunk = CAudioEngine(byr_stream)
	elif name == 'CMixer': outchunk = CMixer(byr_stream)
	elif name == 'CMixerChannel': outchunk = CMixerChannel(byr_stream)
	elif name == 'CInsertProcessor': outchunk = CInsertProcessor(byr_stream)
	elif name == 'CTransport': outchunk = CTransport(byr_stream)
	elif name == 'CMetronome': outchunk = CMetronome(byr_stream)
	elif name == 'Window Layout': WindowLayout(byr_stream)
	elif name == 'TransportPanel': outchunk = TransportPanel(byr_stream)
	elif name == 'Console': outchunk = Console(byr_stream)
	else:
		print('unknown chunk', name)
		exit()
	return name, outchunk
		
# ==================================== AUDIOINPUT ====================================

def iter_stringchunk_inp(byr_stream):
	name = byr_stream.string_t()
	outchunk = None
	if VERBOSE: print('CHUNK >', name.ljust(20), end=' - ')
	if name == 'CCrystalInput': outchunk = CCrystalInput(byr_stream)
	else:
		print('unknown chunk', name)
		exit()
	return name, outchunk
		
# ==================================== WAVER ====================================

def iter_stringchunk_waver(byr_stream):
	name = byr_stream.string_t()
	outchunk = None
	if VERBOSE: print('CHUNK >', name.ljust(20), end=' - ')
	if name == 'CAudioTrack': outchunk = CAudioTrack(byr_stream)
	elif name == 'CAudioPart': outchunk = CAudioPart(byr_stream)
	elif name == 'CFolderPart': outchunk = CFolderPart(byr_stream)
	elif name == 'CPath': outchunk = CPath(byr_stream)
	elif name == 'CWaverRecordPort': outchunk = CWaverRecordPort(byr_stream)
	elif name == 'CTimeLine': outchunk = CTimeLine(byr_stream)
	elif name == 'CTimeSnapper': outchunk = CTimeSnapper(byr_stream)
	elif name == 'CConnection': outchunk = CConnection(byr_stream)
	else:
		if name:
			print('unknown chunk', name)
			exit()
	return name, outchunk
		
class CConnection:
	def __init__(self, byr_stream):
		if byr_stream.uint32()!=1: exit('CConnection is not 1')
		unks = []
		unks.append(byr_stream.uint32())
		unks.append(byr_stream.uint32())
		unks.append(byr_stream.int32())
		unks.append(byr_stream.string_t())
		if VERBOSE: print(unks)

class CTimeSnapper:
	def __init__(self, byr_stream):
		if byr_stream.uint32()!=1: exit('CTimeSnapper is not 1')
		unks = []
		unks.append(byr_stream.uint8())
		unks.append(byr_stream.uint32())
		unks.append(byr_stream.uint32())

		if VERBOSE: print(unks)

class CTimeLine:
	def __init__(self, byr_stream):
		if byr_stream.uint32()!=2: exit('CTimeLine is not 2')
		self.zoom = byr_stream.uint64()
		self.offset = byr_stream.uint64()
		self._unk1 = byr_stream.uint64()
		self.mode = byr_stream.uint32()
		if VERBOSE: print(self.zoom, self.offset, self._unk1, self.mode)

class CWaverRecordPort:
	def __init__(self, byr_stream):
		if byr_stream.uint32()!=1: exit('CWaverRecordPort is not 1')
		self.data = byr_stream.string_t()
		if VERBOSE: print(self.data)

class CPath:
	def __init__(self, byr_stream):
		if byr_stream.uint32()!=1: exit('CPath is not 1')
		self.path = byr_stream.string_t()
		if VERBOSE: print(self.path)

class CFolderPart:
	def __init__(self, byr_stream):
		if byr_stream.uint32()!=2: exit('CFolderPart is not 2')
		self.parts = []
		self.position = byr_stream.uint64()
		self.offset = byr_stream.uint64()
		self.duration = byr_stream.uint64()
		self.unk1 = byr_stream.uint32()
		self.unk2 = byr_stream.uint32()
		self.max_size = byr_stream.uint64()
		self.color = list(byr_stream.l_uint8(4))
		self.name = byr_stream.string_t()
		self.flags = byr_stream.flags32()
		if VERBOSE: print(self.name)
		self.parts = [iter_stringchunk_waver(byr_stream) for _ in range(byr_stream.uint32())]

class CAudioPart:
	def __init__(self, byr_stream):
		num = byr_stream.uint32()

		self.position = byr_stream.uint64()
		self.offset = byr_stream.uint64()
		self.duration = byr_stream.uint64()
		self.unk1 = byr_stream.uint32()
		self.unk2 = byr_stream.uint32()
		self.max_size = byr_stream.uint64()
		self.color = list(byr_stream.l_uint8(4))
		self.name = byr_stream.string_t()
		self.flags = byr_stream.flags32()
		self.fade_in = byr_stream.uint64()
		self.fade_out = byr_stream.uint64()
		self.volume = byr_stream.float()
		if VERBOSE: print(self.name)
		self.path = iter_stringchunk_waver(byr_stream)

class CAudioTrack:
	def __init__(self, byr_stream):
		if byr_stream.uint32()!=1: exit('CAudioTrack is not 1')
		self.name = byr_stream.string_t()
		if VERBOSE: print(self.name)
		self.parts = [iter_stringchunk_waver(byr_stream) for _ in range(byr_stream.uint32())]
		self.flags = byr_stream.flags16()

class CCrystalInput:
	def __init__(self, byr_stream):
		self.parts = []
		self.tracks = []
		self.timeline = None
		self.timesnapper = None
		if byr_stream.uint32()!=1: exit('CCrystalInput is not 1')
		self.type = byr_stream.raw(4)

		if self.type == b'Wavr':
			if VERBOSE: print()
			if byr_stream.uint32()!=1: exit('CCrystalInput is not 1')
			num_tracks = byr_stream.uint32()
			self.tracks = [iter_stringchunk_waver(byr_stream) for _ in range(num_tracks*2)]
			self.timeline = iter_stringchunk_waver(byr_stream)
			self.timesnapper = iter_stringchunk_waver(byr_stream)
			self.connections = [iter_stringchunk_waver(byr_stream) for _ in range(byr_stream.uint32())]

# ==================================== MAIN ====================================

class kristal_plugchunk:
	def __init__(self, byr_stream, chunkid):
		self.name = ''
		self.size = -1
		self.start = -1
		self.type = None
		self.chunkid = chunkid

		self.chunkdata = []
		self.bindata = None

		if byr_stream: self.read(byr_stream, chunkid)

	def read(self, byr_stream, chunkid):
		self.chunkid = chunkid
		self.type = byr_stream.read(4)
		if self.type in [b'VSTf', b'Plug']:
			self.name = byr_stream.string_t()
			type2 = byr_stream.read(4)
			if (self.type==b'Plug' and type2==b'DDat') or (self.type==b'VSTf' and type2==b'FDat'):
				self.size = byr_stream.uint32()-4
				self.start = byr_stream.tell_real()
				byr_stream.skip(self.size)

	def parse(self, byr_stream):
		if self.name:
			byr_stream.seek(self.start)
			with byr_stream.isolate_size(self.size, False) as bye_stream:
				if self.name == 'Waver.cin' and self.chunkid == 4:
					self.chunkdata = iter_stringchunk_inp(bye_stream)

				if self.type == b'VSTf':
					self.bindata = bye_stream.rest()

def decodeplugrack(byr_stream):
	dataout = {}

	chunkid = byr_stream.uint32()
	if chunkid == 1:
		dataout = kristal_plugchunk(byr_stream, chunkid)

	elif chunkid == 3:
		dataout = []
		for num in range(4):
			dataout.append(kristal_plugchunk(byr_stream, chunkid))

	elif chunkid == 4:
		dataout = []
		for num in range(4):
			dataout.append(kristal_plugchunk(byr_stream, chunkid))

	elif chunkid == 16:
		dataout = []
		for num in range(16):
			dataout.append([[], []])
			dataout[num][0] = kristal_plugchunk(byr_stream, chunkid)
			for _ in range(byr_stream.uint32()):
				dataout[num][1].append(kristal_plugchunk(byr_stream, chunkid))
	else:
		print('UNKNOWN PLUGRANK CHUNK', chunkid)
		exit()
	return chunkid, dataout

# ==================================== MAIN ====================================

class kristal_song:
	def __init__(self):
		self.chunks = []
		self.infodata = []
		self.windowdata = []
		self.globalinserts = []
		self.audio_output = None
		self.audio_input = None
		self.mixer = None
		self.master = None

	def parse_chunk(self, byr_stream, name, size):
		with byr_stream.isolate_size(size, False) as bye_stream:

			if name == b'Glob':
				while bye_stream.remaining():
					subname, subchunk = iter_stringchunk(bye_stream)
					self.globalinserts.append([subname, subchunk])

			if name == b'Info':
				while bye_stream.remaining():
					subname, subchunk = iter_stringchunk(bye_stream)
					if subname == 'CProjectInfo': self.infodata = subchunk

			if name == b'Wind':
				while bye_stream.remaining():
					subname, subchunk = iter_stringchunk(bye_stream)
					if subname == 'Window Layout': self.windowdata = subchunk

			if name == b'ADev':
				self.audio_output = decodeplugrack(bye_stream)
				self.audio_input = decodeplugrack(bye_stream)

			if name == b'Mixr':
				self.mixer = decodeplugrack(bye_stream)
				self.master = decodeplugrack(bye_stream)

		if name == b'ADev':
			for x in self.audio_input[1]: x.parse(byr_stream)

		if name == b'Mixr':
			for x in self.mixer[1]: 
				x[0].parse(byr_stream)
				for y in x[1]: y.parse(byr_stream)

			for x in self.master[1]: 
				x.parse(byr_stream)

	def load_from_file(self, input_file):
		byr_stream = bytereader.bytereader()
		byr_stream.load_file(input_file)

		while byr_stream.remaining():
			name = byr_stream.raw(4)
			size = byr_stream.uint32()-4
			start = byr_stream.tell()
			self.chunks.append([name, size, start])
			byr_stream.skip(size)

		for name, size, start in self.chunks:
			byr_stream.seek(start)
			self.parse_chunk(byr_stream, name, size)
		return True
