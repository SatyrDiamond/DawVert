import struct
import zlib
from objects.data_bytes import bytereader

def printchunk(num, trk_chunk_obj, song_data, view):

	if view:
		if trk_chunk_obj.size==1: outview = song_data.int8()
		elif trk_chunk_obj.size==2: outview = song_data.uint16()
		elif trk_chunk_obj.size==4: outview = song_data.uint32()
		else: outview = song_data.raw(min(trk_chunk_obj.size, 28))
	else:
		outview = ''

	print('    '*(num) + ('--> ' if (num>0) else '') + str(trk_chunk_obj.id), trk_chunk_obj.size if view else '', outview)

class dms_note:
	def __init__(self):
		self.pos = 0
		self.dur = 0
		self.key = 0
		self.vel = 0

	def read(self, trk_chunk_obj, song_data):
		for subchunk_obj in trk_chunk_obj.iter(0):
			if subchunk_obj.id == 1001: self.pos = song_data.uint32()
			if subchunk_obj.id == 2001: self.key = song_data.uint8()
			if subchunk_obj.id == 2002: self.vel = song_data.uint8()
			if subchunk_obj.id == 2003: self.dur = song_data.uint32()

class dms_ctrl:
	def __init__(self):
		self.pos = 0
		self.cc = 0
		self.data1 = 0
		self.data2 = 0

	def read(self, trk_chunk_obj, song_data):
		for subchunk_obj in trk_chunk_obj.iter(0):
			if subchunk_obj.id == 1001: self.pos = song_data.uint32()
			if subchunk_obj.id == 2001: self.cc = song_data.uint16()
			if subchunk_obj.id == 2002: self.data1 = song_data.raw(subchunk_obj.size)
			if subchunk_obj.id == 2003: self.data2 = song_data.raw(subchunk_obj.size)

class dms_text:
	def __init__(self):
		self.pos = 0
		self.text = ''

	def read(self, trk_chunk_obj, song_data):
		for subchunk_obj in trk_chunk_obj.iter(0):
			if subchunk_obj.id == 1001: self.pos = song_data.uint32()
			if subchunk_obj.id == 2001: self.text = song_data.string(subchunk_obj.size)

class dms_sysex:
	def __init__(self):
		self.pos = 0
		self.text = ''
		self.sysex = b''

	def read(self, trk_chunk_obj, song_data):
		for subchunk_obj in trk_chunk_obj.iter(0):
			if subchunk_obj.id == 1001: self.pos = song_data.uint32()
			if subchunk_obj.id == 2001: self.text = song_data.string(subchunk_obj.size)
			if subchunk_obj.id == 2002: self.sysex = song_data.raw(subchunk_obj.size)

class dms_expression:
	def __init__(self):
		self.pos = 0
		self.var = ''
		self.value = ''

	def read(self, trk_chunk_obj, song_data):
		for subchunk_obj in trk_chunk_obj.iter(0):
			if subchunk_obj.id == 1001: self.pos = song_data.uint32()
			if subchunk_obj.id == 2001: self.var = song_data.string(subchunk_obj.size)
			if subchunk_obj.id == 2002: self.value = song_data.string(subchunk_obj.size)

class dms_measurelink:
	def __init__(self):
		self.pos = 0
		self.measure_dest = 1
		self.key_transpose = 0

	def read(self, trk_chunk_obj, song_data):
		for subchunk_obj in trk_chunk_obj.iter(0):
			if subchunk_obj.id == 1001: self.pos = song_data.uint32()
			if subchunk_obj.id == 2001: self.measure_dest = song_data.uint32()
			if subchunk_obj.id == 2002: self.key_transpose = song_data.int32()

class dms_timesig:
	def __init__(self):
		self.pos = 0
		self.num = 4
		self.nenom = 4

	def read(self, trk_chunk_obj, song_data):
		for subchunk_obj in trk_chunk_obj.iter(0):
			if subchunk_obj.id == 1001: self.pos = song_data.uint32()
			if subchunk_obj.id == 2001: self.num = song_data.uint8()
			if subchunk_obj.id == 2002: self.nenom = song_data.uint8()

class dms_keysig:
	def __init__(self):
		self.pos = 0
		self.key = 0

	def read(self, trk_chunk_obj, song_data):
		for subchunk_obj in trk_chunk_obj.iter(0):
			if subchunk_obj.id == 1001: self.pos = song_data.uint32()
			if subchunk_obj.id == 2001: self.key = song_data.uint8()

class dms_keyscale:
	def __init__(self):
		self.pos = 0
		self.key = 0
		self.chord = 0
		self.custom = None
		self.name = None

	def read(self, trk_chunk_obj, song_data):
		for subchunk_obj in trk_chunk_obj.iter(0):
			if subchunk_obj.id == 1001: self.pos = song_data.uint32()
			if subchunk_obj.id == 2001: self.key = song_data.uint8()
			if subchunk_obj.id == 2002: self.chord = song_data.uint8()
			if subchunk_obj.id == 2003: self.custom = list(song_data.l_uint8(12))
			if subchunk_obj.id == 2004: self.name = song_data.string(subchunk_obj.size)

class dms_program_change:
	def __init__(self):
		self.pos = 0
		self.patch = 0
		self.unk1 = 0
		self.unk2 = 0
		self.unk3 = 0
		self.unk4 = 0
		self.unk5 = 0

	def read(self, trk_chunk_obj, song_data):
		for subchunk_obj in trk_chunk_obj.iter(0):
			if subchunk_obj.id == 1001: self.pos = song_data.uint32()
			if subchunk_obj.id == 2001: self.unk1 = song_data.int8()
			if subchunk_obj.id == 2002: self.unk2 = song_data.int8()
			if subchunk_obj.id == 2003: self.patch = song_data.uint8()
			if subchunk_obj.id == 2004: self.unk3 = song_data.raw(subchunk_obj.size)
			if subchunk_obj.id == 2005: self.unk4 = song_data.uint8()
			if subchunk_obj.id == 2006: self.unk5 = song_data.int16()

class dms_chord:
	def __init__(self):
		self.pos = 0
		self.key = 0
		self.chord = 0
		self.custom = None
		self.name = None

	def read(self, trk_chunk_obj, song_data):
		for subchunk_obj in trk_chunk_obj.iter(0):
			if subchunk_obj.id == 1001: self.pos = song_data.uint32()
			if subchunk_obj.id == 2001: self.key = song_data.uint8()
			if subchunk_obj.id == 2002: self.chord = song_data.uint32()
			if subchunk_obj.id == 2003: self.custom = song_data.raw(subchunk_obj.size)
			if subchunk_obj.id == 2004: self.name = song_data.string(subchunk_obj.size)

class dms_tempo:
	def __init__(self):
		self.pos = 0
		self.val = 120

	def read(self, trk_chunk_obj, song_data):
		for subchunk_obj in trk_chunk_obj.iter(0):
			if subchunk_obj.id == 1001: self.pos = song_data.uint32()
			if subchunk_obj.id == 2001: 
				for inchunk_obj in subchunk_obj.iter(0):
					self.val = song_data.float()

class dms_track:
	def __init__(self, chunk_obj, song_data):
		self.notes = []
		self.ctrls = []
		self.sysex = []
		self.texts = []
		self.markers = []
		self.lyrics = []
		self.cuepoints = []
		self.expressions = []
		self.measurelinks = []
		self.programchanges = []
		self.timesigs = []
		self.keysigs = []
		self.keyscales = []
		self.chords = []
		self.tempos = []

		self.name = ''
		self.channel = 0
		self.tick_adjust = 0
		self.range_low = 0
		self.range_high = 0
		self.transpose = 0
		self.out_port = 0
		self.is_rhythm = 0
		self.rhythm_name = ''
		self.color = 0
		self.volume = 0
		self.gate = 480
		self.gate_adjust = 100
		self.tick_adjust_measure = 0
		self.enabled = 1

		for trk_chunk_obj in chunk_obj.iter(0):
			chunkid = trk_chunk_obj.id

			if chunkid == 1000: self.out_port = song_data.uint16()
			elif chunkid == 1001: self.channel = song_data.uint8()
			elif chunkid == 1002: self.name = song_data.string(trk_chunk_obj.size)
			elif chunkid == 1004: self.is_rhythm = song_data.uint8()
			elif chunkid == 1006: self.volume = song_data.uint8()
			elif chunkid == 1007: self.gate = song_data.int32()
			elif chunkid == 1009: self.rhythm_name = song_data.string(trk_chunk_obj.size)
			elif chunkid == 1012: self.tick_adjust = song_data.uint32()
			elif chunkid == 1015: self.enabled = song_data.int32()
			elif chunkid == 1016: self.gate_adjust = song_data.int32()
			elif chunkid == 1017: self.transpose = song_data.int32()
			elif chunkid == 1018: self.color = song_data.uint8()
			elif chunkid == 1019: self.tick_adjust_measure = song_data.uint32()
			elif chunkid == 1021: self.range_low = song_data.uint8()
			elif chunkid == 1022: self.range_high = song_data.uint8()

			elif chunkid == 2001:
				note_obj = dms_note()
				note_obj.read(trk_chunk_obj, song_data)
				self.notes.append(note_obj)

			elif chunkid == 2003:
				ctrl_obj = dms_ctrl()
				ctrl_obj.read(trk_chunk_obj, song_data)
				self.ctrls.append(ctrl_obj)

			elif chunkid == 2004:
				sysex_obj = dms_sysex()
				sysex_obj.read(trk_chunk_obj, song_data)
				self.sysex.append(sysex_obj)

			elif chunkid == 2005:
				text_obj = dms_text()
				text_obj.read(trk_chunk_obj, song_data)
				self.texts.append(text_obj)

			elif chunkid == 2011:
				text_obj = dms_text()
				text_obj.read(trk_chunk_obj, song_data)
				self.lyrics.append(text_obj)

			elif chunkid == 2017:
				text_obj = dms_text()
				text_obj.read(trk_chunk_obj, song_data)
				self.markers.append(text_obj)

			elif chunkid == 2012:
				text_obj = dms_text()
				text_obj.read(trk_chunk_obj, song_data)
				self.cuepoints.append(text_obj)

			elif chunkid == 2007:
				expression_obj = dms_expression()
				expression_obj.read(trk_chunk_obj, song_data)
				self.expressions.append(expression_obj)

			elif chunkid == 2014:
				measurelink_obj = dms_measurelink()
				measurelink_obj.read(trk_chunk_obj, song_data)
				self.measurelinks.append(measurelink_obj)

			elif chunkid == 2015:
				timesig_obj = dms_timesig()
				timesig_obj.read(trk_chunk_obj, song_data)
				self.timesigs.append(timesig_obj)

			elif chunkid == 2016:
				keysig_obj = dms_keysig()
				keysig_obj.read(trk_chunk_obj, song_data)
				self.keysigs.append(keysig_obj)

			elif chunkid == 2018:
				keyscale_obj = dms_keyscale()
				keyscale_obj.read(trk_chunk_obj, song_data)
				self.keyscales.append(keyscale_obj)

			elif chunkid == 2002:
				program_obj = dms_program_change()
				program_obj.read(trk_chunk_obj, song_data)
				self.programchanges.append(program_obj)

			elif chunkid == 2019:
				chord_obj = dms_chord()
				chord_obj.read(trk_chunk_obj, song_data)
				self.chords.append(chord_obj)

			elif chunkid == 2008:
				tempo_obj = dms_tempo()
				tempo_obj.read(trk_chunk_obj, song_data)
				self.tempos.append(tempo_obj)

			#elif chunkid in [2017, 2009, 1010, 2008]:
			#	printchunk(1, chunkid, trk_chunk_obj, song_data, False)
			#	for subchunk_obj in trk_chunk_obj.iter(0):
			#		subchunk_obj.id = int.from_bytes(subchunk_obj.id, 'little')
			#		printchunk(2, subchunk_obj.id, subchunk_obj, song_data, True)
			#else:
			#	printchunk(1, trk_chunk_obj, song_data, True)

class dms_project:
	def __init__(self):
		self.tracks = []
		self.ppq = 96
		self.name = ''
		self.copyright = ''

	def load_from_file(self, input_file):
		song_file = bytereader.bytereader()
		song_file.load_file(input_file)
		song_file.magic_check(b'PortalSequenceData')
		song_file.skip(4)
		song_data = bytereader.bytereader()
		song_data.load_raw(zlib.decompress(song_file.rest(), zlib.MAX_WBITS|32))

		main_iff_obj = song_data.chunk_objmake()
		main_iff_obj.set_sizes_num(2, 4, False)

		for chunk_obj in main_iff_obj.iter(0, song_data.end):
			if chunk_obj.id == 1003: self.tracks.append(dms_track(chunk_obj, song_data))
			elif chunk_obj.id == 1000: self.name = song_data.string(chunk_obj.size)
			elif chunk_obj.id == 1001: self.copyright = song_data.string(chunk_obj.size)
			elif chunk_obj.id == 1002: self.ppq = song_data.uint16()
			#elif chunk_obj.id == 1008: 
			#	printchunk(0, chunk_obj, song_data, False)
			#	for trk_chunk_obj in chunk_obj.iter(0):
			#		printchunk(1, trk_chunk_obj, song_data, True)
			#elif chunk_obj.id == 1017: 
			#	printchunk(0, chunk_obj, song_data, False)
			#	for trk_chunk_obj in chunk_obj.iter(0):
			#		printchunk(1, trk_chunk_obj, song_data, True)
			#else:
			#	printchunk(0, chunk_obj, song_data, True)
		return True