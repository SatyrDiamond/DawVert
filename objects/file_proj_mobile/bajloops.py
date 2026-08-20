
from external.easybinrw import easybinrw

DEBUGTXT = 0

class bajloop_pattern:
	def __init__(self):
		self.name = ''

	def read_events(self, byr_stream):
		self.events = []
		num_events = byr_stream.int_u16_b()
		#print(num_events, end=' [')
		if num_events:
			num_events_size = byr_stream.int_u16_b()
			for _ in range(num_events): 
				event = byr_stream.list_int_u8(16)
				self.events.append(event)
			byr_stream.skip(16*(num_events_size-num_events))
			self.events = self.events[0:num_events_size]
		#print('', end='] | ')

	def read(self, byr_stream):
		if DEBUGTXT: print('PAT:', end=' ')
		self.unk1 = byr_stream.int_u8()
		if DEBUGTXT: print(self.unk1, end=' | ')
		self.unk2 = byr_stream.int_u8()
		if DEBUGTXT: print(self.unk2, end=' | ')
		self.color = byr_stream.list_int_u8(3)
		if DEBUGTXT: print(self.color.tobytes().hex(), end=' | ')
		self.name = byr_stream.string_t(encoding='iso-8859-1')
		if DEBUGTXT: print(self.name, end=' | ')
		self.read_events(byr_stream)
		if DEBUGTXT: print('')

class bajloop_sample:
	def __init__(self):
		self.name = ''
		self.data = b''

	def read(self, byr_stream):
		assert(byr_stream.int_u8()==6)
		self.bits = byr_stream.int_u8()
		#print(  self.bits, end=' | '  )
		self.channels = byr_stream.int_u8()
		#print(  self.channels, end=' | '  )
		self.unk1 = byr_stream.raw(2).hex()
		#print(  self.unk1, end=' | '  )
		self.freq = byr_stream.int_u16_b()
		#print(  self.freq, end=' | '  )
		self.num_samples = byr_stream.int_u32_b()
		#print(  self.num_samples, end=' | '  )
		self.loop_1 = byr_stream.int_u32()
		#print(  self.loop_1, end=' | '  )
		self.loop_2 = byr_stream.int_u32()
		#print(  self.loop_1+self.loop_2, end=' | '  )
		self.name = byr_stream.string_t(encoding='iso-8859-1')
		#print(  self.name, end=' | '  )
		self.unk3 = byr_stream.raw(4).hex()
		#print(  self.unk3, end=' | '  )
		self.data_size = byr_stream.int_u32_b()
		#print(  self.data_size, end=' | '  )
		self.data = byr_stream.raw(self.data_size)
		#print()

class bajloop_inst:
	def __init__(self):
		self.name = ''
		self.unk = []

	def read(self, byr_stream):
		assert(byr_stream.int_u8()==0)
		self.sample_num = byr_stream.int_u8()
		#print(  self.sample_num, end=' | '  )
		self.unk.append(byr_stream.raw(22).hex())
		self.vol = byr_stream.int_u8()
		self.unk.append(byr_stream.raw(1).hex())
		self.pan = byr_stream.int_u8()
		self.basenote = byr_stream.int_s16()
		self.pitch = byr_stream.int_s16()
		#print( self.basenote , end=' | '  )
		self.unk.append(byr_stream.raw(34).hex())
		#print( self.unk , end=' | '  )
		self.color = byr_stream.list_int_u8(3)
		self.name = byr_stream.string_t(encoding='iso-8859-1')
		#print(  self.name, end=' | '  )

class bajloop_fx:
	def __init__(self):
		self.name = ''
		self.params = []

	def read(self, byr_stream):
		self.unk = byr_stream.raw(5).hex()
		#print(self.unk, end=' ')
		isf = byr_stream.int_u8()
		if isf:
			self.name = byr_stream.string_t()
			self.params = byr_stream.list_int_s16(32)
			if DEBUGTXT: print('FX', self.name, self.params.tolist())

def bajloop_automation_part(byr_stream):
	header1 = byr_stream.int_u8()
	if header1==255:
		assert(byr_stream.int_u8()==1)
		outdata1 = byr_stream.int_u16_b()
		outdata2 = byr_stream.int_u8()
		#print('PART', outdata1)
		return outdata1, outdata2
	else: 
		return None

def bajloop_automations(byr_stream):
	header1 = byr_stream.int_u8()
	if header1==255:
		assert(byr_stream.int_u8()==1)
		tracknum = byr_stream.int_s8()
		paramnum = byr_stream.int_u8()
		data = {}
		while True:
			d = bajloop_automation_part(byr_stream)
			if d==None: break
			else: data[d[0]] = d[1]
		return tracknum, paramnum, data
	else: 
		#print('DONE')
		#print()
		return None

class bajloop_sections:
	def __init__(self):
		self.data1 = []
		self.data2 = b''
		self.data3 = []

	def read(self, byr_stream):
		byr_stream.skip(1)
		num_sections = byr_stream.int_u8()
		for _ in range(num_sections):
			d = byr_stream.raw(7)
			n = byr_stream.string_t()
			self.data1.append([d, n])
		self.data2 = byr_stream.raw(10)
		for x in range(6):
			self.data3.append(  byr_stream.raw(21).hex()  )

class bajloop_file:
	def __init__(self):
		self.name = None
		self.string2 = None
		self.unk1 = None
		self.unk2 = None
		self.unk3 = None
		self.placements = None
		self.unk4 = None
		self.unk5 = None
		self.unk6 = None
		self.fx = []
		self.autos = []
		self.patterns = []
		self.samples = []
		self.insts = []

	def load_from_file(self, input_file):
		byr_stream = easybinrw.binread()
		byr_stream.load_file(input_file)

		self.version = byr_stream.int_u8()
		assert(self.version==10)
		#print('VERSION', self.version)

		if DEBUGTXT: print('--- HEADER ---')
		byr_stream.magic_check(b'Recipe for pure veg song 1.00:\x00')
		self.name = byr_stream.string_t()
		if DEBUGTXT: print('name', self.name)
		self.info = byr_stream.string_t()
		if DEBUGTXT: print('info', self.info)
		self.unk1 = byr_stream.raw(23)
		if DEBUGTXT: print('unk1', self.unk1)
		self.unk2 = byr_stream.raw(15*8)
		if DEBUGTXT: print('unk2', self.unk2)
		self.unk3 = [byr_stream.list_int_u8(2).tolist() for x in range(12)]
		if DEBUGTXT: print('unk3', self.unk3)
		self.unk4 = byr_stream.raw(3)
		self.tempo = byr_stream.int_u8()
		if DEBUGTXT: print('unk4', self.unk4)
		
		self.placements = [byr_stream.list_int_u8(8) for x in range(240)]

		self.unk5 = byr_stream.int_u32()
		if DEBUGTXT: print('unk5', self.unk5)
		self.unk6 = byr_stream.raw(60)

		if DEBUGTXT: print('--- FX ---')
		for _ in range(5):
			fx_obj = bajloop_fx()
			fx_obj.read(byr_stream)
			self.fx.append(fx_obj)

		self.unk7 = byr_stream.raw(2).hex()
		self.unk8 = byr_stream.raw(2).hex()

		#print(self.unk7, self.unk8)

		while True:
			o = bajloop_automations(byr_stream)
			if o==None: break
			else: self.autos.append(o)

		sections = bajloop_sections()
		sections.read(byr_stream)

		if DEBUGTXT: print('--- PATTERN ---')
		for _ in range(128):
			pattern_obj = bajloop_pattern()
			pattern_obj.read(byr_stream)
			self.patterns.append(pattern_obj)

		if DEBUGTXT: print('--- SAMPLES ---')
		num_samples = byr_stream.int_u16_b()
		for _ in range(num_samples):
			sample_obj = bajloop_sample()
			sample_obj.read(byr_stream)
			self.samples.append(sample_obj)
		
		if DEBUGTXT: print('--- INSTRUMENTS ---')
		for _ in range(32):
			inst_obj = bajloop_inst()
			inst_obj.read(byr_stream)
			self.insts.append(inst_obj)

		return True
