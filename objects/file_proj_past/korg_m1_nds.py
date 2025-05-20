
from objects.data_bytes import bytereader

class korg_m1_note:
	def __init__(self):
		self.length = 0
		self.velocity = 0
		self.pitch = 0
		self.offset = 0

class korg_m1_song:
	def __init__(self):
		self.modified = False
		self.name = ''
		self.channels = [korg_m1_channel() for _ in range(8)]
		self.blockTempos = []
		self.blockSteps = []
		self.tempo = 120
		self.swing = 0
		self.steps = 32

class korg_m1_block:
	def __init__(self):
		self.offset = 0
		self.notes = []

class korg_m1_channel_drumsettings:
	def __init__(self):
		self.level = 0
		self.pan = 0
		self.tune = 0

class korg_m1_channel:
	def __init__(self):
		self.attack = 0
		self.release = 0
		self.volume = 0
		self.pan = 0
		self.flags = 0
		self.blocks = []
		self.set = 0
		self.bank = 0
		self.patch = 0
		self.drumparams = [korg_m1_channel_drumsettings() for _ in range(12)]
		self.unk1 = 0
		self.unk2 = 0

class korg_m1_proj:
	def __init__(self):
		self.songs = [korg_m1_song() for _ in range(10)]

	def load_from_file(self, input_file):
		byr_stream = bytereader.bytereader()
		byr_stream.load_file(input_file)
		byr_stream.skip(4)
		byr_stream.magic_check(b'M01W')
		byr_stream.skip(4)

		for n in range(10):
			self.songs[n].modified = byr_stream.uint8()
			self.songs[n].name = byr_stream.string(8)
			byr_stream.skip(31) 

		for i, song_obj in enumerate(self.songs):
			byr_stream.seek(0x1000 + 0xC000 * i)
			if self.songs[i].modified:
				byr_stream.skip(8)
				for channel_obj in song_obj.channels:
					channel_obj.mode = byr_stream.uint8()
					channel_obj.cat = byr_stream.uint8()
					channel_obj.patch = byr_stream.uint8()
					channel_obj.unk1 = byr_stream.uint8()
					channel_obj.unk2 = byr_stream.uint8()
					channel_obj.attack = byr_stream.uint8()
					channel_obj.release = byr_stream.uint8()
					channel_obj.volume = byr_stream.uint8()
					channel_obj.pan = byr_stream.int8()
					channel_obj.flags = byr_stream.flags8()
					byr_stream.skip(5)
					for drumset_obj in channel_obj.drumparams:
						drumset_obj.pan, drumset_obj.level = byr_stream.bytesplit()
						drumset_obj.tune = byr_stream.int8()
					byr_stream.skip(17)

				byr_stream.skip(62)
				song_obj.tempo = byr_stream.uint16()
				song_obj.swing = byr_stream.uint8()
				song_obj.steps = byr_stream.uint8()
				byr_stream.skip(4)
	
				musicPos = byr_stream.uint16() + byr_stream.tell()
	
				for i in range(99):
					song_obj.blockTempos.append(byr_stream.uint16())
					song_obj.blockSteps.append(byr_stream.uint8())
					byr_stream.skip(5)
	
				byr_stream.seek(musicPos)
				for i in range(99): ## 99 blocks per 8 channes
					for j in range(8):
						block_obj = korg_m1_block()
	
						byr_stream.skip(4)
						block_obj.offset = byr_stream.uint8()
						byr_stream.skip(1)
		
						noteCount = byr_stream.uint16()
						if noteCount <= 0: continue # empty :(
						
						for i in range(noteCount):
							note_obj = korg_m1_note()
							note_obj.length = (byr_stream.uint8() + 1) / 4
							note_obj.velocity = byr_stream.uint8()
							note_obj.pitch = byr_stream.uint8()
							note_obj.offset = byr_stream.uint8()
							block_obj.notes.append(note_obj)
						song_obj.channels[j].blocks.append(block_obj)
		return True

input_file = "G:\\RandomMusicFiles\\old\\korg_dsi\\Korg M01 Music Workstation (Japan) (En).sav"
test_obj = korg_m1_proj()
test_obj.load_from_file(input_file)
