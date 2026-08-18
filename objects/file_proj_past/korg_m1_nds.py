#code from https://github.com/LameGrape/hamkorger

from external.easybinrw import easybinrw

# ============================================= pattern ============================================= 

class korg_m1_note:
	def __init__(self):
		self.length = 0
		self.velocity = 0
		self.pitch = 0
		self.offset = 0

class korg_m1_block:
	def __init__(self):
		self.offset = 0
		self.notes = []

# ============================================= channel ============================================= 

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
		self.flags = []
		self.blocks = []
		self.set = 0
		self.bank = 0
		self.patch = 0
		self.drumparams = [korg_m1_channel_drumsettings() for _ in range(12)]
		self.unk1 = 0
		self.unk2 = 0
		self.mode = 0

# ============================================= savefile ============================================= 

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

class korg_m1_proj:
	def __init__(self):
		self.songs = [korg_m1_song() for _ in range(10)]

	def load_from_file(self, input_file):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_file(input_file)
		ebrw_readstr.skip(4)
		ebrw_readstr.magic_check(b'M01W')
		ebrw_readstr.skip(4)

		for n in range(10):
			self.songs[n].modified = ebrw_readstr.int_u8()
			self.songs[n].name = ebrw_readstr.string(8)
			ebrw_readstr.skip(31) 

		for i, song_obj in enumerate(self.songs):
			ebrw_readstr.seek(0x1000 + 0xC000 * i)
			if self.songs[i].modified:
				ebrw_readstr.raw(8)
				for channel_obj in song_obj.channels:
					channel_obj.mode = ebrw_readstr.int_u8()
					channel_obj.cat = ebrw_readstr.int_u8()
					channel_obj.patch = ebrw_readstr.int_u8()
					channel_obj.unk1 = ebrw_readstr.int_u8()
					channel_obj.unk2 = ebrw_readstr.int_u8()
					channel_obj.attack = ebrw_readstr.int_u8()
					channel_obj.release = ebrw_readstr.int_u8()
					channel_obj.volume = ebrw_readstr.int_u8()
					channel_obj.pan = ebrw_readstr.int_s8()
					channel_obj.flags = ebrw_readstr.flags_i8()
					ebrw_readstr.skip(5)
					for drumset_obj in channel_obj.drumparams:
						drumset_obj.pan, drumset_obj.level = ebrw_readstr.int_u4_2()
						drumset_obj.tune = ebrw_readstr.int_s8()
					ebrw_readstr.skip(17)

				ebrw_readstr.skip(5)
				song_obj.reverb_time = ebrw_readstr.int_s8()
				song_obj.reverb_level = ebrw_readstr.int_s8()

				ebrw_readstr.skip(1)

				song_obj.delay_tempo = ebrw_readstr.int_u8()
				song_obj.delay_time = ebrw_readstr.int_u8()
				song_obj.delay_lr_ratio = ebrw_readstr.int_s8()
				song_obj.delay_fb = ebrw_readstr.int_u8()
				song_obj.delay_level = ebrw_readstr.int_u8()

				ebrw_readstr.skip(3)
				song_obj.fx_type = ebrw_readstr.int_u8()&1
				ebrw_readstr.skip(45)

				song_obj.tempo = ebrw_readstr.int_u16()
				song_obj.swing = ebrw_readstr.int_u8()
				song_obj.steps = ebrw_readstr.int_u8()
				ebrw_readstr.skip(4)
	
				musicPos = ebrw_readstr.int_u16() + ebrw_readstr.tell()
	
				for i in range(99):
					song_obj.blockTempos.append(ebrw_readstr.int_u16())
					song_obj.blockSteps.append(ebrw_readstr.int_u8())
					ebrw_readstr.skip(5)
	
				ebrw_readstr.seek(musicPos)
				for i in range(99): ## 99 blocks per 8 channes
					for j in range(8):
						block_obj = korg_m1_block()
	
						ebrw_readstr.skip(4)
						block_obj.offset = ebrw_readstr.int_u8()
						ebrw_readstr.skip(1)
		
						noteCount = ebrw_readstr.int_u16()
						if noteCount <= 0: continue # empty :(
						
						for i in range(noteCount):
							note_obj = korg_m1_note()
							note_obj.length = (ebrw_readstr.int_u8() + 1) / 4
							note_obj.velocity = ebrw_readstr.int_u8()
							note_obj.pitch = ebrw_readstr.int_u8()
							note_obj.offset = ebrw_readstr.int_u8()
							block_obj.notes.append(note_obj)
						song_obj.channels[j].blocks.append(block_obj)
		return True