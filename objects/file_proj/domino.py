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
				note = [0,0,0,0]
				for subchunk_obj in trk_chunk_obj.iter(0):
					if subchunk_obj.id == 1001: note[0] = song_data.uint32()
					if subchunk_obj.id == 2001: note[1] = song_data.uint8()
					if subchunk_obj.id == 2002: note[2] = song_data.uint8()
					if subchunk_obj.id == 2003: note[3] = song_data.uint32()
				self.notes.append(note)

			elif chunkid == 2003:
				control = [0,0,0,0]
				for subchunk_obj in trk_chunk_obj.iter(0):
					if subchunk_obj.id == 1001: control[0] = song_data.uint32()
					if subchunk_obj.id == 2001: control[1] = song_data.uint16()
					if subchunk_obj.id == 2002: control[2] = song_data.raw(subchunk_obj.size)
					if subchunk_obj.id == 2003: control[3] = song_data.raw(subchunk_obj.size)
				self.ctrls.append(control)

			elif chunkid == 2004:
				sysex = [0,b'',0]
				for subchunk_obj in trk_chunk_obj.iter(0):
					if subchunk_obj.id == 1001: sysex[0] = song_data.uint32()
					if subchunk_obj.id == 2001: sysex[1] = song_data.string(subchunk_obj.size)
					if subchunk_obj.id == 2002: sysex[2] = song_data.raw(subchunk_obj.size)
				self.sysex.append(sysex)

			elif chunkid == 2005:
				text = [0,None]
				for subchunk_obj in trk_chunk_obj.iter(0):
					if subchunk_obj.id == 1001: text[0] = song_data.uint32()
					if subchunk_obj.id == 2001: text[1] = song_data.string(subchunk_obj.size)
				self.texts.append(text)

			elif chunkid == 2011:
				lyric = [0,None]
				for subchunk_obj in trk_chunk_obj.iter(0):
					if subchunk_obj.id == 1001: lyric[0] = song_data.uint32()
					if subchunk_obj.id == 2001: lyric[1] = song_data.string(subchunk_obj.size)
				self.lyrics.append(lyric)

			elif chunkid == 2017:
				marker = [0,None]
				for subchunk_obj in trk_chunk_obj.iter(0):
					if subchunk_obj.id == 1001: marker[0] = song_data.uint32()
					if subchunk_obj.id == 2001: marker[1] = song_data.string(subchunk_obj.size)
				self.markers.append(marker)

			elif chunkid == 2012:
				cuepoint = [0,None]
				for subchunk_obj in trk_chunk_obj.iter(0):
					if subchunk_obj.id == 1001: cuepoint[0] = song_data.uint32()
					if subchunk_obj.id == 2001: cuepoint[1] = song_data.string(subchunk_obj.size)
				self.cuepoints.append(cuepoint)

			elif chunkid == 2007:
				expression = [0,None,None]
				for subchunk_obj in trk_chunk_obj.iter(0):
					if subchunk_obj.id == 1001: expression[0] = song_data.uint32()
					if subchunk_obj.id == 2001: expression[1] = song_data.string(subchunk_obj.size)
					if subchunk_obj.id == 2002: expression[2] = song_data.string(subchunk_obj.size)
				self.expressions.append(expression)

			elif chunkid == 2014:
				measurelink = [0,0,0]
				for subchunk_obj in trk_chunk_obj.iter(0):
					if subchunk_obj.id == 1001: measurelink[0] = song_data.uint32()
					if subchunk_obj.id == 2001: measurelink[1] = song_data.uint32()
					if subchunk_obj.id == 2002: measurelink[2] = song_data.uint32()
				self.measurelinks.append(measurelink)

			elif chunkid == 2015:
				timesig = [0,0,0]
				for subchunk_obj in trk_chunk_obj.iter(0):
					if subchunk_obj.id == 1001: timesig[0] = song_data.uint32()
					if subchunk_obj.id == 2001: timesig[1] = song_data.uint8()
					if subchunk_obj.id == 2002: timesig[2] = song_data.uint8()
				self.timesigs.append(timesig)

			elif chunkid == 2016:
				keysig = [0,None,None]
				for subchunk_obj in trk_chunk_obj.iter(0):
					if subchunk_obj.id == 1001: keysig[0] = song_data.uint32()
					if subchunk_obj.id == 2001: keysig[1] = song_data.uint8()
				self.keysigs.append(keysig)

			elif chunkid == 2018:
				keyscale = [0,None,None]
				for subchunk_obj in trk_chunk_obj.iter(0):
					if subchunk_obj.id == 1001: keyscale[0] = song_data.uint32()
					if subchunk_obj.id == 2001: keyscale[1] = song_data.uint8()
					if subchunk_obj.id == 2001: keyscale[2] = song_data.uint32()
				self.keyscales.append(keyscale)

			elif chunkid == 2002:
				programchange = [0,0,0,0,0,0,0]
				for subchunk_obj in trk_chunk_obj.iter(0):
					if subchunk_obj.id == 1001: programchange[0] = song_data.uint32()
					if subchunk_obj.id == 2003: programchange[1] = song_data.uint8()
					if subchunk_obj.id == 2004: programchange[2] = song_data.raw(subchunk_obj.size)
					if subchunk_obj.id == 2005: programchange[3] = song_data.uint8()
					if subchunk_obj.id == 2001: programchange[4] = song_data.int8()
					if subchunk_obj.id == 2002: programchange[5] = song_data.int8()
					if subchunk_obj.id == 2006: programchange[6] = song_data.int16()
				self.programchanges.append(programchange)

			elif chunkid == 2019:
				chord = [0,0,0,0,0]
				for subchunk_obj in trk_chunk_obj.iter(0):
					if subchunk_obj.id == 1001: chord[0] = song_data.uint32()
					if subchunk_obj.id == 2001: chord[1] = song_data.uint8()
					if subchunk_obj.id == 2002: chord[2] = song_data.uint32()
					if subchunk_obj.id == 2003: chord[3] = song_data.raw(subchunk_obj.size)
					if subchunk_obj.id == 2004: chord[4] = song_data.string(subchunk_obj.size)
				self.chords.append(chord)

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
