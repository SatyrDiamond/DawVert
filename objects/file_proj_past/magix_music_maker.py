# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

VERBOSE = True

# ---------------------- ITEMS ----------------------
class item_svip:
	def __init__(self):
		self.data = None

	@classmethod
	def from_byr_stream(cls, byr_stream, size):
		cls = cls()
		with byr_stream.isolate_size(size, False) as bye_stream:
			cls.data = bye_stream.raw(size)
		return cls


class item_file:
	def __init__(self):
		self.folder = ''
		self.type = 0
		self.file = ''
		self.type2 = 0
		self.file2 = ''

	@classmethod
	def from_byr_stream(cls, byr_stream, size):
		cls = cls()
		with byr_stream.isolate_size(size, False) as bye_stream:
			cls.folder = bye_stream.string(128, errors="ignore")
			bye_stream.skip(2)
			cls.video = bye_stream.string(126, errors="ignore")
			bye_stream.skip(2)
			cls.type = bye_stream.uint16()
			cls.file = bye_stream.string(256, errors="ignore")
			bye_stream.skip(2)
			cls.type2 = bye_stream.uint16()
			cls.file2 = bye_stream.string(256, errors="ignore")
		return cls


class item_trci:
	def __init__(self):
		self.data = None
		self.unknowns = []
		self.vol = 1
		self.pan = 0
		self.name = ''

	@classmethod
	def from_byr_stream(cls, byr_stream, size):
		cls = cls()
		with byr_stream.isolate_size(size, False) as bye_stream:
			if bye_stream.remaining(): cls.unknowns.append( bye_stream.uint16() )
			if bye_stream.remaining(): cls.unknowns.append( bye_stream.uint16() )
			if bye_stream.remaining(): cls.unknowns.append( bye_stream.uint32() )
			if bye_stream.remaining(): cls.unknowns.append( bye_stream.uint32() )
			if bye_stream.remaining(): val1 = bye_stream.float()
			if bye_stream.remaining(): cls.unknowns.append( bye_stream.uint32() )
			if bye_stream.remaining(): cls.unknowns.append( bye_stream.uint32() )
			if bye_stream.remaining(): cls.unknowns.append( bye_stream.uint32() )
			if bye_stream.remaining(): cls.unknowns.append( bye_stream.uint32() )
			if bye_stream.remaining(): cls.unknowns.append( bye_stream.uint16() )
			if bye_stream.remaining(): cls.unknowns.append( bye_stream.uint16() )
			if bye_stream.remaining(): cls.vol = bye_stream.int32()/32767
			if bye_stream.remaining(): cls.unknowns.append( bye_stream.uint16() )
			if bye_stream.remaining(): cls.unknowns.append( bye_stream.uint16() )
			if bye_stream.remaining(): cls.name = bye_stream.string(48)
			if bye_stream.remaining(): cls.unknowns.append( bye_stream.uint32() )
			if bye_stream.remaining(): cls.unknowns.append( bye_stream.uint32() )
			if bye_stream.remaining(): cls.pan = bye_stream.float()/32767
			if bye_stream.remaining(): cls.data = bye_stream.rest()
		return cls


class item_cntr:
	def __init__(self):
		self.data = None

	@classmethod
	def from_byr_stream(cls, byr_stream, size):
		cls = cls()
		with byr_stream.isolate_size(size, False) as bye_stream:
			cls.data = bye_stream.raw(size)
		return cls



class item_objc:
	def __init__(self):
		self.unknowns = []
		self.fileid = 0
		self.offset = 0
		self.size = 0
		self.start = 0
		self.end = 0
		self.unk_color = [0,0,0,0]
		self.fg_color = [0,0,0,0]
		self.bg_color = [0,0,0,0]
		self.fade_in = 0
		self.fade_out = 0
		self.vol = 0
		self.loop_end = 0
		self.name = ''
		self.speed = 1
		self.pitch = 0
		self.group = 0

	@classmethod
	def from_byr_stream(cls, byr_stream, size):
		cls = cls()
		with byr_stream.isolate_size(size, False) as bye_stream:
			cls.fileid = bye_stream.uint32()
			cls.unknowns.append( bye_stream.uint32() )
			cls.offset = byr_stream.uint32()
			cls.size = bye_stream.uint32()
			cls.start = bye_stream.uint64()
			cls.end = bye_stream.uint64()
			cls.unknowns.append( bye_stream.uint8() )
			cls.unknowns.append( bye_stream.uint8() )
			cls.unknowns.append( bye_stream.uint8() )
			cls.unknowns.append( bye_stream.uint8() )
			cls.unknowns.append( bye_stream.uint32() )
			cls.unknowns.append( bye_stream.uint32() )
			cls.unknowns.append( bye_stream.uint32() )
			cls.unk_color = bye_stream.l_uint8(4)
			cls.fg_color = bye_stream.l_uint8(4)
			cls.bg_color = bye_stream.l_uint8(4)
			cls.group = bye_stream.uint32()
			cls.unknowns.append( bye_stream.uint32() )
			cls.unknowns.append( bye_stream.uint32() )
			cls.fade_in = bye_stream.uint64()
			cls.fade_out = bye_stream.uint64()
			cls.vol = byr_stream.uint32()
			cls.unknowns.append( bye_stream.uint32() )
			cls.unknowns.append( bye_stream.uint32() )
			cls.loop_end = bye_stream.uint32()
			cls.unknowns.append( bye_stream.uint32() )
			cls.unknowns.append( bye_stream.uint32() )
			cls.unknowns.append( bye_stream.uint32() )
			cls.unknowns.append( bye_stream.uint32() )
			cls.name = bye_stream.string(32, errors="ignore")
			cls.unknowns.append( bye_stream.uint32() )
			cls.unknowns.append( bye_stream.uint32() )
			cls.unknowns.append( bye_stream.uint32() )
			cls.unknowns.append( bye_stream.uint32() )
			cls.unknowns.append( bye_stream.uint32() )
			cls.unknowns.append( bye_stream.uint32() )
			cls.unknowns.append( bye_stream.int32() )
			cls.unknowns.append( bye_stream.uint32() )
			if bye_stream.remaining(): bye_stream.raw(4)
			if bye_stream.remaining(): cls.speed = bye_stream.float()
			if bye_stream.remaining(): bye_stream.skip(8)
			if bye_stream.remaining(): cls.pitch = bye_stream.float()

		return cls



class item_oeff:
	def __init__(self):
		self.data = None

	@classmethod
	def from_byr_stream(cls, byr_stream, size):
		cls = cls()
		with byr_stream.isolate_size(size, False) as bye_stream:
			cls.data = bye_stream.raw(size)
		return cls


class item_otrn:
	def __init__(self):
		self.data = None

	@classmethod
	def from_byr_stream(cls, byr_stream, size):
		cls = cls()
		with byr_stream.isolate_size(size, False) as bye_stream:
			cls.data = bye_stream.raw(size)
		return cls


class item_rubb:
	def __init__(self):
		self.data = None

	@classmethod
	def from_byr_stream(cls, byr_stream, size):
		cls = cls()
		with byr_stream.isolate_size(size, False) as bye_stream:
			cls.data = bye_stream.raw(size)
		return cls


class item_crsr:
	def __init__(self):
		self.data = None

	@classmethod
	def from_byr_stream(cls, byr_stream, size):
		cls = cls()
		with byr_stream.isolate_size(size, False) as bye_stream:
			cls.data = bye_stream.raw(size)
		return cls


class item_proi:
	def __init__(self):
		self.data = None
		self.sample_rate = 44100
		self.timeisg_num = 4
		self.timeisg_denom = 4
		self.tempo = 120

		self.unknowns = []


	@classmethod
	def from_byr_stream(cls, byr_stream, size):
		cls = cls()
		with byr_stream.isolate_size(size, False) as bye_stream:
			#cls.data = bye_stream.raw(size)
			cls.unknowns.append( bye_stream.uint32() )
			cls.unknowns.append( bye_stream.uint32() )
			cls.unknowns.append( bye_stream.uint32() )
			cls.unknowns.append( bye_stream.uint32() )
			cls.unknowns.append( bye_stream.uint32() )
			cls.sample_rate = bye_stream.uint32()
			cls.timeisg_num = bye_stream.uint32()
			cls.timeisg_denom = bye_stream.uint32()
			cls.tempo = bye_stream.float()
		return cls


class item_teq:
	def __init__(self):
		self.data = None

	@classmethod
	def from_byr_stream(cls, byr_stream, size):
		cls = cls()
		with byr_stream.isolate_size(size, False) as bye_stream:
			cls.data = bye_stream.raw(size)
		return cls


class item_tpq:
	def __init__(self):
		self.data = None

	@classmethod
	def from_byr_stream(cls, byr_stream, size):
		cls = cls()
		with byr_stream.isolate_size(size, False) as bye_stream:
			cls.data = bye_stream.raw(size)
		return cls


class item_comp:
	def __init__(self):
		self.data = None

	@classmethod
	def from_byr_stream(cls, byr_stream, size):
		cls = cls()
		with byr_stream.isolate_size(size, False) as bye_stream:
			cls.data = bye_stream.raw(size)
		return cls


from objects.data_bytes import riff_chunks
# ---------------------- ROOT ----------------------
class root_group:
	def __init__(self):
		self.data_svip = None
		self.data_phys = None
		self.data_trks = None
		self.data_rngs = None
		self.data_crss = None
		self.data_proi = None
		self.data_teq = {}
		self.data_tpq = {}
		self.data_comp = None

	def load_from_file(self, input_file):
		riffchunks = riff_chunks.riff_chunk()
		byr_stream = riffchunks.load_from_file(input_file, False)
		for x in riffchunks.iter_wseek(byr_stream):
			if x.name == b'SVIP':
				if not x.is_list: self.data_svip = item_svip.from_byr_stream(byr_stream, x.size)
				elif VERBOSE: print(x.name, 'is not an item')
			elif x.name == b'phys':
				if x.is_list: self.data_phys = group_phys.from_riffchunks(x, byr_stream)
				elif VERBOSE: print(x.name, 'is not a group')
			elif x.name == b'trks':
				if x.is_list: self.data_trks = group_trks.from_riffchunks(x, byr_stream)
				elif VERBOSE: print(x.name, 'is not a group')
			elif x.name == b'rngs':
				if x.is_list: self.data_rngs = group_rngs.from_riffchunks(x, byr_stream)
				elif VERBOSE: print(x.name, 'is not a group')
			elif x.name == b'crss':
				if x.is_list: self.data_crss = group_crss.from_riffchunks(x, byr_stream)
				elif VERBOSE: print(x.name, 'is not a group')
			elif x.name == b'PROI':
				if not x.is_list: self.data_proi = item_proi.from_byr_stream(byr_stream, x.size)
				elif VERBOSE: print(x.name, 'is not an item')
			elif x.name == b'teq1':
				if not x.is_list: self.data_teq[1] = item_teq.from_byr_stream(byr_stream, x.size)
				elif VERBOSE: print(x.name, 'is not an item')
			elif x.name == b'teq2':
				if not x.is_list: self.data_teq[2] = item_teq.from_byr_stream(byr_stream, x.size)
				elif VERBOSE: print(x.name, 'is not an item')
			elif x.name == b'teq3':
				if not x.is_list: self.data_teq[3] = item_teq.from_byr_stream(byr_stream, x.size)
				elif VERBOSE: print(x.name, 'is not an item')
			elif x.name == b'teq4':
				if not x.is_list: self.data_teq[4] = item_teq.from_byr_stream(byr_stream, x.size)
				elif VERBOSE: print(x.name, 'is not an item')
			elif x.name == b'teq5':
				if not x.is_list: self.data_teq[5] = item_teq.from_byr_stream(byr_stream, x.size)
				elif VERBOSE: print(x.name, 'is not an item')
			elif x.name == b'tpq1':
				if not x.is_list: self.data_tpq[1] = item_tpq.from_byr_stream(byr_stream, x.size)
				elif VERBOSE: print(x.name, 'is not an item')
			elif x.name == b'tpq2':
				if not x.is_list: self.data_tpq[2] = item_tpq.from_byr_stream(byr_stream, x.size)
				elif VERBOSE: print(x.name, 'is not an item')
			elif x.name == b'tpq3':
				if not x.is_list: self.data_tpq[3] = item_tpq.from_byr_stream(byr_stream, x.size)
				elif VERBOSE: print(x.name, 'is not an item')
			elif x.name == b'tpq4':
				if not x.is_list: self.data_tpq[4] = item_tpq.from_byr_stream(byr_stream, x.size)
				elif VERBOSE: print(x.name, 'is not an item')
			elif x.name == b'tpq5':
				if not x.is_list: self.data_tpq[5] = item_tpq.from_byr_stream(byr_stream, x.size)
				elif VERBOSE: print(x.name, 'is not an item')
			elif x.name == b'comp':
				if not x.is_list: self.data_comp = item_comp.from_byr_stream(byr_stream, x.size)
				elif VERBOSE: print(x.name, 'is not an item')
			elif VERBOSE: print('unknown chunk in root: '+str(x.name))
		return True

# ---------------------- GROUP ----------------------
class group_phys:
	def __init__(self):
		self.files = []

	@classmethod
	def from_riffchunks(cls, riffchunks, byr_stream):
		cls = cls()
		for x in riffchunks.iter_wseek(byr_stream):
			if x.name == b'file':
				if not x.is_list: cls.files.append(item_file.from_byr_stream(byr_stream, x.size))
				elif VERBOSE: print(x.name, 'is not an item')
			elif VERBOSE: print('unknown chunk in phys: '+str(x.name))
		return cls


class group_trks:
	def __init__(self):
		self.data_trck = []

	@classmethod
	def from_riffchunks(cls, riffchunks, byr_stream):
		cls = cls()
		for x in riffchunks.iter_wseek(byr_stream):
			if x.name == b'trck':
				if x.is_list:
					cls.data_trck.append(group_trck.from_riffchunks(x, byr_stream))
				elif VERBOSE: print(x.name, 'is not a group')
			elif VERBOSE: print('unknown chunk in trks: '+str(x.name))
		return cls


class group_trck:
	def __init__(self):
		self.data_trci = None
		self.data_cntr = []
		self.data_objs = []
		self.data_rubb = []

	@classmethod
	def from_riffchunks(cls, riffchunks, byr_stream):
		cls = cls()
		for x in riffchunks.iter_wseek(byr_stream):
			if x.name == b'trci':
				if not x.is_list: cls.data_trci = item_trci.from_byr_stream(byr_stream, x.size)
				elif VERBOSE: print(x.name, 'is not an item')
			elif x.name == b'cntr':
				if not x.is_list: cls.data_cntr.append(item_cntr.from_byr_stream(byr_stream, x.size))
				elif VERBOSE: print(x.name, 'is not an item')
			elif x.name == b'objs':
				if x.is_list:
					cls.data_objs.append(group_objs.from_riffchunks(x, byr_stream))
				elif VERBOSE: print(x.name, 'is not a group')
			elif x.name == b'rubb':
				if not x.is_list: cls.data_rubb.append(item_rubb.from_byr_stream(byr_stream, x.size))
				elif VERBOSE: print(x.name, 'is not an item')
			elif VERBOSE: print('unknown chunk in trck: '+str(x.name))
		return cls


class item_3dau:
	def __init__(self):
		self.data = None
		self.unknowns = []

	@classmethod
	def from_byr_stream(cls, byr_stream, size):
		cls = cls()
		with byr_stream.isolate_size(size, False) as bye_stream:
			cls.unknowns.append( bye_stream.uint32() )
			cls.unknowns.append( bye_stream.float() )
			cls.unknowns.append( bye_stream.uint32() )
		return cls

class item_orup:
	def __init__(self):
		self.data = None
		self.unknowns = []

	@classmethod
	def from_byr_stream(cls, byr_stream, size):
		cls = cls()
		with byr_stream.isolate_size(size, False) as bye_stream:
			cls.unknowns.append( bye_stream.uint32() )
			bye_stream.skip(4)
			cls.unknowns.append( bye_stream.int32() )
			bye_stream.skip(4)
			cls.unknowns.append( bye_stream.uint32() )
			bye_stream.skip(4)
			cls.unknowns.append( bye_stream.double() )
		return cls



class group_objs:
	def __init__(self):
		self.data_objc = None
		self.data_oeff = None
		self.data_otrn = None
		self.data_3dau = None
		self.data_orup = []

	@classmethod
	def from_riffchunks(cls, riffchunks, byr_stream):
		cls = cls()
		for x in riffchunks.iter_wseek(byr_stream):
			if x.name == b'objc':
				if not x.is_list: cls.data_objc = item_objc.from_byr_stream(byr_stream, x.size)
				elif VERBOSE: print(x.name, 'is not an item')
			elif x.name == b'oeff':
				if not x.is_list: cls.data_oeff = item_oeff.from_byr_stream(byr_stream, x.size)
				elif VERBOSE: print(x.name, 'is not an item')
			elif x.name == b'otrn':
				if not x.is_list: cls.data_otrn = item_otrn.from_byr_stream(byr_stream, x.size)
				elif VERBOSE: print(x.name, 'is not an item')
			elif x.name == b'3dau':
				if not x.is_list: cls.data_3dau = item_3dau.from_byr_stream(byr_stream, x.size)
				elif VERBOSE: print(x.name, 'is not an item')
			elif x.name == b'orup':
				if not x.is_list: cls.data_orup.append(item_orup.from_byr_stream(byr_stream, x.size))
				elif VERBOSE: print(x.name, 'is not an item')
			elif VERBOSE: print('unknown chunk in objs: '+str(x.name))
		return cls


class group_crss:
	def __init__(self):
		self.data_crsr = []

	@classmethod
	def from_riffchunks(cls, riffchunks, byr_stream):
		cls = cls()
		for x in riffchunks.iter_wseek(byr_stream):
			if x.name == b'crsr':
				if not x.is_list: cls.data_crsr.append(item_crsr.from_byr_stream(byr_stream, x.size))
				elif VERBOSE: print(x.name, 'is not an item')
			elif VERBOSE: print('unknown chunk in crss: '+str(x.name))
		return cls


class group_rngs:
	def __init__(self):
		self.data = []

	@classmethod
	def from_riffchunks(cls, riffchunks, byr_stream):
		cls = cls()
		cls.data  = [x for x in riffchunks.iter_wseek(byr_stream)]
		return cls