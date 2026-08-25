# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

VERBOSE = 0
from external.easybinrw import easybinrw
from external.easybinrw import riff_chunks

def printtxt(tabnum, riffchunk, supported):
	if VERBOSE:
		outtxt = tabnum*'   '
		outtxt += 'GROUP ' if riffchunk.is_list else 'ITEM '
		outtxt += '- ' if supported else '# '
		outtxt += riffchunk.id.decode()
		print(outtxt)

def check_isitem(x):
	if not x.is_list: return True
	elif VERBOSE: 
		print(x.id, 'is not an item')
		return False

def check_isgroup(x):
	if x.is_list: return True
	elif VERBOSE: 
		print(x.id, 'is not a group')
		return False

# ---------------------- ITEMS ----------------------
class item_svip:
	def __init__(self):
		self.data = None

	@classmethod
	def from_ebrw_readstr(cls, ebrw_readstr):
		cls = cls()
		cls.data = ebrw_readstr.rest()
		return cls

class item_file:
	def __init__(self):
		self.folder = ''
		self.type = 0
		self.file = ''
		self.type2 = 0
		self.file2 = ''

	@classmethod
	def from_ebrw_readstr(cls, ebrw_readstr):
		cls = cls()
		cls.folder = ebrw_readstr.string(128, errors="ignore")
		ebrw_readstr.skip(2)
		cls.video = ebrw_readstr.string(126, errors="ignore")
		ebrw_readstr.skip(2)
		cls.type = ebrw_readstr.int_u16()
		cls.file = ebrw_readstr.string(256, errors="ignore")
		ebrw_readstr.skip(2)
		cls.type2 = ebrw_readstr.int_u16()
		cls.file2 = ebrw_readstr.string(256, errors="ignore")
		return cls

class item_trci:
	def __init__(self):
		self.data = None
		self.unknowns = []
		self.vol = 1
		self.pan = 0
		self.name = ''
		self.flags = []
		self.aux1 = 0
		self.aux2 = 0

	@classmethod
	def from_ebrw_readstr(cls, ebrw_readstr):
		cls = cls()
		if ebrw_readstr.remaining(): cls.flags = ebrw_readstr.flags_i32()
		if ebrw_readstr.remaining(): cls.unknowns.append( ebrw_readstr.float() )
		if ebrw_readstr.remaining(): cls.unknowns.append( ebrw_readstr.float() )
		if ebrw_readstr.remaining(): cls.unknowns.append( ebrw_readstr.float() )
		if ebrw_readstr.remaining(): cls.unknowns.append( ebrw_readstr.int_u32() )
		if ebrw_readstr.remaining(): cls.unknowns.append( ebrw_readstr.int_u32() )
		if ebrw_readstr.remaining(): cls.unknowns.append( ebrw_readstr.int_u32() )
		if ebrw_readstr.remaining(): cls.unknowns.append( ebrw_readstr.float() )
		if ebrw_readstr.remaining(): cls.unknowns.append( ebrw_readstr.float() )
		if ebrw_readstr.remaining(): cls.vol = ebrw_readstr.int_s32()/32767
		if ebrw_readstr.remaining(): cls.unknowns.append( ebrw_readstr.flags_i32() )
		if ebrw_readstr.remaining(): cls.name = ebrw_readstr.string(48)
		if ebrw_readstr.remaining(): cls.aux1 = ebrw_readstr.int_u32()/65535
		if ebrw_readstr.remaining(): cls.aux2 = ebrw_readstr.int_u32()/65535
		if ebrw_readstr.remaining(): cls.pan = ebrw_readstr.float()/32767
		if ebrw_readstr.remaining(): cls.data = ebrw_readstr.rest()
		return cls

class item_cntr:
	def __init__(self):
		self.data = None
		self.unknowns = []

	@classmethod
	def from_ebrw_readstr(cls, ebrw_readstr):
		cls = cls()
		if ebrw_readstr.remaining(): cls.unknowns.append( ebrw_readstr.int_u32() )
		if ebrw_readstr.remaining(): cls.unknowns.append( ebrw_readstr.int_u32() )
		if ebrw_readstr.remaining(): cls.unknowns.append( ebrw_readstr.int_u32() )
		if ebrw_readstr.remaining(): cls.unknowns.append( ebrw_readstr.int_u32() )
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
	def from_ebrw_readstr(cls, ebrw_readstr):
		cls = cls()
		cls.fileid = ebrw_readstr.int_u32()
		cls.unknowns.append( ebrw_readstr.int_u32() )
		cls.offset = ebrw_readstr.int_u32()
		cls.size = ebrw_readstr.int_u32()
		cls.start = ebrw_readstr.int_u64()
		cls.end = ebrw_readstr.int_u64()
		cls.unknowns.append( ebrw_readstr.int_u8() )
		cls.unknowns.append( ebrw_readstr.int_u8() )
		cls.unknowns.append( ebrw_readstr.int_u8() )
		cls.unknowns.append( ebrw_readstr.int_u8() )
		cls.unknowns.append( ebrw_readstr.int_u32() )
		cls.unknowns.append( ebrw_readstr.int_u32() )
		cls.unknowns.append( ebrw_readstr.int_u32() )
		cls.unk_color = ebrw_readstr.list_int_u8(4)
		cls.fg_color = ebrw_readstr.list_int_u8(4)
		cls.bg_color = ebrw_readstr.list_int_u8(4)
		cls.group = ebrw_readstr.int_u32()
		cls.unknowns.append( ebrw_readstr.int_u32() )
		cls.unknowns.append( ebrw_readstr.int_u32() )
		cls.fade_in = ebrw_readstr.int_u64()
		cls.fade_out = ebrw_readstr.int_u64()
		cls.vol = ebrw_readstr.int_u32()
		cls.unknowns.append( ebrw_readstr.int_u32() )
		cls.unknowns.append( ebrw_readstr.int_u32() )
		cls.loop_end = ebrw_readstr.int_u32()
		cls.unknowns.append( ebrw_readstr.int_u32() )
		cls.unknowns.append( ebrw_readstr.int_u32() )
		cls.unknowns.append( ebrw_readstr.int_u32() )
		cls.unknowns.append( ebrw_readstr.int_u32() )
		cls.name = ebrw_readstr.string(32, errors="ignore")
		cls.unknowns.append( ebrw_readstr.int_u32() )
		cls.unknowns.append( ebrw_readstr.int_u32() )
		cls.unknowns.append( ebrw_readstr.int_u32() )
		cls.unknowns.append( ebrw_readstr.int_u32() )
		cls.unknowns.append( ebrw_readstr.int_u32() )
		cls.unknowns.append( ebrw_readstr.int_u32() )
		cls.unknowns.append( ebrw_readstr.int_s32() )
		cls.unknowns.append( ebrw_readstr.int_u32() )
		if ebrw_readstr.remaining(): cls.unknowns.append( ebrw_readstr.int_s32() )
		if ebrw_readstr.remaining(): cls.speed = ebrw_readstr.float()
		if ebrw_readstr.remaining(): cls.unknowns.append( ebrw_readstr.int_s32() )
		if ebrw_readstr.remaining(): cls.unknowns.append( ebrw_readstr.int_s32() )
		if ebrw_readstr.remaining(): cls.pitch = ebrw_readstr.float()
		return cls

class item_oeff:
	def __init__(self):
		self.data = None

	@classmethod
	def from_ebrw_readstr(cls, ebrw_readstr):
		cls = cls()
		cls.data = ebrw_readstr.rest()
		return cls

class item_otrn:
	def __init__(self):
		self.rest = None
		self.tempo = 120
		self.unknowns = []

	@classmethod
	def from_ebrw_readstr(cls, ebrw_readstr):
		cls = cls()
		cls.tempo = ebrw_readstr.float()
		cls.unknowns.append( ebrw_readstr.int_u32() )
		cls.rest = ebrw_readstr.rest()
		return cls

class item_omid:
	def __init__(self):
		self.data = None

	@classmethod
	def from_ebrw_readstr(cls, ebrw_readstr):
		cls = cls()
		cls.data = ebrw_readstr.rest()
		return cls

class item_usgr:
	def __init__(self):
		self.data = None

	@classmethod
	def from_ebrw_readstr(cls, ebrw_readstr):
		cls = cls()
		cls.data = ebrw_readstr.rest()
		return cls

class item_rubb:
	def __init__(self):
		self.pos = 0
		self.val = 0
		self.param = 0
		self.data = None
		self.unknowns = []

	@classmethod
	def from_ebrw_readstr(cls, ebrw_readstr):
		cls = cls()
		cls.pos = ebrw_readstr.int_u32()
		cls.unknowns.append( ebrw_readstr.int_u32() )
		cls.val = ebrw_readstr.int_s32()
		cls.unknowns.append( ebrw_readstr.int_u32() )
		cls.param = ebrw_readstr.int_u32()
		cls.data = ebrw_readstr.rest()
		return cls

class item_crsr:
	def __init__(self):
		self.data = None

	@classmethod
	def from_ebrw_readstr(cls, ebrw_readstr):
		cls = cls()
		cls.data = ebrw_readstr.rest()
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
	def from_ebrw_readstr(cls, ebrw_readstr):
		cls = cls()
		#cls.data = ebrw_readstr.rest()
		cls.unknowns.append( ebrw_readstr.int_u32() )
		cls.unknowns.append( ebrw_readstr.int_u32() )
		cls.unknowns.append( ebrw_readstr.int_u32() )
		cls.unknowns.append( ebrw_readstr.int_u32() )
		cls.unknowns.append( ebrw_readstr.int_u32() )
		cls.sample_rate = ebrw_readstr.int_u32()
		cls.timeisg_num = ebrw_readstr.int_u32()
		cls.timeisg_denom = ebrw_readstr.int_u32()
		cls.tempo = ebrw_readstr.float()
		return cls

class item_teq:
	def __init__(self):
		self.data = None

	@classmethod
	def from_ebrw_readstr(cls, ebrw_readstr):
		cls = cls()
		cls.data = ebrw_readstr.rest()
		return cls

class item_tpq:
	def __init__(self):
		self.data = None

	@classmethod
	def from_ebrw_readstr(cls, ebrw_readstr):
		cls = cls()
		cls.data = ebrw_readstr.rest()
		return cls

class item_comp:
	def __init__(self):
		self.data = None

	@classmethod
	def from_ebrw_readstr(cls, ebrw_readstr):
		cls = cls()
		cls.data = ebrw_readstr.rest()
		return cls

class item_tdrx:
	def __init__(self):
		self.data = None
		self.unknowns = []

	@classmethod
	def from_ebrw_readstr(cls, ebrw_readstr):
		cls = cls()
		cls.data = ebrw_readstr.rest()
		return cls

class item_vsti:
	def __init__(self):
		self.data = None
		self.filename = ''
		self.name = ''
		self.unknowns = []

	@classmethod
	def from_ebrw_readstr(cls, ebrw_readstr):
		cls = cls()
		cls.filename = ebrw_readstr.string(256)
		cls.name = ebrw_readstr.string(64)
		cls.data = ebrw_readstr.rest()
		return cls

# ---------------------- FX ----------------------

class item_FXHD:
	def __init__(self):
		self.data = None
		self.unknowns = []
		self.numparams = 0
		self.fxtype = 0
		self.flags = []

	@classmethod
	def from_ebrw_readstr(cls, ebrw_readstr):
		cls = cls()
		cls.unknowns.append( ebrw_readstr.int_u8() )
		cls.unknowns.append( ebrw_readstr.int_u8() )
		cls.unknowns.append( ebrw_readstr.int_u8() )
		cls.unknowns.append( ebrw_readstr.int_u8() )
		cls.unknowns.append( ebrw_readstr.int_u32() )
		cls.numparams = ebrw_readstr.int_u32()
		cls.fxtype = ebrw_readstr.int_u32()
		cls.flags = ebrw_readstr.flags_i32()
		cls.unknowns.append( ebrw_readstr.int_u32() )
		return cls

class item_AFXP:
	def __init__(self):
		self.data = None

	@classmethod
	def from_ebrw_readstr(cls, ebrw_readstr):
		cls = cls()
		cls.paramnum = ebrw_readstr.int_u32()
		cls.name = ebrw_readstr.string(20)
		cls.val_min = ebrw_readstr.float()
		cls.val_max = ebrw_readstr.float()
		cls.val_def = ebrw_readstr.float()
		cls.val_current = ebrw_readstr.float()
		cls.data = ebrw_readstr.rest()
		return cls

class group_AFXD:
	def __init__(self):
		self.data_AFXE = []
		self.params = []

	@classmethod
	def from_riffchunks(cls, riffchunks, ebrw_readstr, tabnum):
		cls = cls()
		for x in riffchunks.iter_reader(ebrw_readstr):
			if x.id == b'AFXE':
				printtxt(tabnum, x, 0)
				if check_isgroup(x): cls.data_AFXE.append(group_AFXE.from_riffchunks(x, ebrw_readstr, tabnum+1))
			elif x.id == b'AFXP':
				printtxt(tabnum, x, 0)
				if check_isitem(x): cls.params.append(item_AFXP.from_ebrw_readstr(ebrw_readstr))
			elif VERBOSE: printtxt(tabnum, x, 0) # print('unknown chunk in trks: '+str(x.id))
		return cls

class group_AFXE:
	def __init__(self):
		self.data_FXHD = None
		self.data_AFXD = None

	@classmethod
	def from_riffchunks(cls, riffchunks, ebrw_readstr, tabnum):
		cls = cls()
		for x in riffchunks.iter_reader(ebrw_readstr):
			if x.id == b'AFXD':
				printtxt(tabnum, x, 0)
				if check_isgroup(x): cls.data_AFXD = group_AFXD.from_riffchunks(x, ebrw_readstr, tabnum+1)
			elif x.id == b'FXHD':
				printtxt(tabnum, x, 0)
				if check_isitem(x): cls.data_FXHD = item_FXHD.from_ebrw_readstr(ebrw_readstr)
				#print((tabnum*'   ')+str(cls.data_FXHD.unknowns))
			elif VERBOSE: printtxt(tabnum, x, 0) # print('unknown chunk in trks: '+str(x.id))
		return cls

class group_AUFX:
	def __init__(self):
		self.data_AFXE = []

	@classmethod
	def from_riffchunks(cls, riffchunks, ebrw_readstr, tabnum):
		cls = cls()
		for x in riffchunks.iter_reader(ebrw_readstr):
			if x.id == b'AFXE':
				printtxt(tabnum, x, 0)
				if check_isgroup(x): cls.data_AFXE.append(group_AFXE.from_riffchunks(x, ebrw_readstr, tabnum+1))
			elif VERBOSE: printtxt(tabnum, x, 0) # print('unknown chunk in trks: '+str(x.id))
		return cls

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
		self.data_vsti = None
		self.data_AUFX = None

	def load_from_file(self, input_file):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_file(input_file)
		riffchunks = riff_chunks.riff_chunk()
		riffchunks.read(ebrw_readstr, 0)

		for x in riffchunks.iter_reader(ebrw_readstr):
			if x.id == b'SVIP':
				printtxt(0, x, 1)
				if check_isitem(x): self.data_svip = item_svip.from_ebrw_readstr(ebrw_readstr)
			elif x.id == b'phys':
				printtxt(0, x, 1)
				if check_isgroup(x): self.data_phys = group_phys.from_riffchunks(x, ebrw_readstr, 1)
			elif x.id == b'trks':
				printtxt(0, x, 1)
				if check_isgroup(x): self.data_trks = group_trks.from_riffchunks(x, ebrw_readstr, 1)
			elif x.id == b'rngs':
				printtxt(0, x, 1)
				if check_isgroup(x): self.data_rngs = group_rngs.from_riffchunks(x, ebrw_readstr, 1)
			elif x.id == b'crss':
				printtxt(0, x, 1)
				if check_isgroup(x): self.data_crss = group_crss.from_riffchunks(x, ebrw_readstr, 1)
			elif x.id == b'AUFX':
				printtxt(0, x, 0)
				if check_isgroup(x): self.data_AUFX = group_AUFX.from_riffchunks(x, ebrw_readstr, 1)
			elif x.id == b'PROI':
				printtxt(0, x, 1)
				if check_isitem(x): self.data_proi = item_proi.from_ebrw_readstr(ebrw_readstr)
			elif x.id == b'teq1':
				printtxt(0, x, 0)
				if check_isitem(x): self.data_teq[1] = item_teq.from_ebrw_readstr(ebrw_readstr)
			elif x.id == b'teq2':
				printtxt(0, x, 0)
				if check_isitem(x): self.data_teq[2] = item_teq.from_ebrw_readstr(ebrw_readstr)
			elif x.id == b'teq3':
				printtxt(0, x, 0)
				if check_isitem(x): self.data_teq[3] = item_teq.from_ebrw_readstr(ebrw_readstr)
			elif x.id == b'teq4':
				printtxt(0, x, 0)
				if check_isitem(x): self.data_teq[4] = item_teq.from_ebrw_readstr(ebrw_readstr)
			elif x.id == b'teq5':
				printtxt(0, x, 0)
				if check_isitem(x): self.data_teq[5] = item_teq.from_ebrw_readstr(ebrw_readstr)
			elif x.id == b'tpq1':
				printtxt(0, x, 0)
				if check_isitem(x): self.data_tpq[1] = item_tpq.from_ebrw_readstr(ebrw_readstr)
			elif x.id == b'tpq2':
				printtxt(0, x, 0)
				if check_isitem(x): self.data_tpq[2] = item_tpq.from_ebrw_readstr(ebrw_readstr)
			elif x.id == b'tpq3':
				printtxt(0, x, 0)
				if check_isitem(x): self.data_tpq[3] = item_tpq.from_ebrw_readstr(ebrw_readstr)
			elif x.id == b'tpq4':
				printtxt(0, x, 0)
				if check_isitem(x): self.data_tpq[4] = item_tpq.from_ebrw_readstr(ebrw_readstr)
			elif x.id == b'tpq5':
				printtxt(0, x, 0)
				if check_isitem(x): self.data_tpq[5] = item_tpq.from_ebrw_readstr(ebrw_readstr)
			elif x.id == b'vsti':
				printtxt(0, x, 0)
				if check_isitem(x): self.data_vsti = item_vsti.from_ebrw_readstr(ebrw_readstr)
			elif x.id == b'comp':
				printtxt(0, x, 0)
				if check_isitem(x): self.data_comp = item_comp.from_ebrw_readstr(ebrw_readstr)
			elif VERBOSE: printtxt(0, x, 0) # print('unknown chunk in root: '+str(x.id))
		return True

# ---------------------- GROUP ----------------------
class group_phys:
	def __init__(self):
		self.files = []

	@classmethod
	def from_riffchunks(cls, riffchunks, ebrw_readstr, tabnum):
		cls = cls()
		for x in riffchunks.iter_reader(ebrw_readstr):
			if x.id == b'file':
				printtxt(tabnum, x, 1)
				if check_isitem(x): cls.files.append(item_file.from_ebrw_readstr(ebrw_readstr))
			elif VERBOSE: printtxt(tabnum, x, 0) # print('unknown chunk in phys: '+str(x.id))
		return cls



class group_trks:
	def __init__(self):
		self.data_trck = []

	@classmethod
	def from_riffchunks(cls, riffchunks, ebrw_readstr, tabnum):
		cls = cls()
		for x in riffchunks.iter_reader(ebrw_readstr):
			if x.id == b'trck':
				printtxt(tabnum, x, 1)
				if check_isgroup(x): cls.data_trck.append(group_trck.from_riffchunks(x, ebrw_readstr, tabnum+1))
			elif VERBOSE: printtxt(tabnum, x, 0) # print('unknown chunk in trks: '+str(x.id))
		return cls


class group_trck:
	def __init__(self):
		self.data_trci = None
		self.data_cntr = []
		self.data_objs = []
		self.data_rubb = []
		self.data_tdrx = None
		self.data_viif = None

	@classmethod
	def from_riffchunks(cls, riffchunks, ebrw_readstr, tabnum):
		cls = cls()
		for x in riffchunks.iter_reader(ebrw_readstr):
			if x.id == b'trci':
				printtxt(tabnum, x, 1)
				if check_isitem(x): cls.data_trci = item_trci.from_ebrw_readstr(ebrw_readstr)
			elif x.id == b'tdrx':
				printtxt(tabnum, x, 1)
				if check_isitem(x): cls.data_tdrx = item_tdrx.from_ebrw_readstr(ebrw_readstr)
			elif x.id == b'cntr':
				printtxt(tabnum, x, 1)
				if check_isitem(x): cls.data_cntr.append(item_cntr.from_ebrw_readstr(ebrw_readstr))
			elif x.id == b'objs':
				printtxt(tabnum, x, 1)
				if check_isgroup(x): cls.data_objs.append(group_objs.from_riffchunks(x, ebrw_readstr, tabnum+1))
			elif x.id == b'rubb':
				printtxt(tabnum, x, 0)
				if check_isitem(x): cls.data_rubb.append(item_rubb.from_ebrw_readstr(ebrw_readstr))
			elif x.id == b'viif':
				printtxt(tabnum, x, 1)
				if check_isgroup(x): cls.data_viif = group_viif.from_riffchunks(x, ebrw_readstr, tabnum+1)
			elif VERBOSE: printtxt(tabnum, x, 0) # print('unknown chunk in trck: '+str(x.id))
		return cls

class item_3dau:
	def __init__(self):
		self.data = None
		self.unknowns = []

	@classmethod
	def from_ebrw_readstr(cls, ebrw_readstr):
		cls = cls()
		cls.unknowns.append( ebrw_readstr.int_u32() )
		cls.unknowns.append( ebrw_readstr.float() )
		cls.unknowns.append( ebrw_readstr.int_u32() )
		return cls

class item_orup:
	def __init__(self):
		self.data = None
		self.unknowns = []

	@classmethod
	def from_ebrw_readstr(cls, ebrw_readstr):
		cls = cls()
		cls.unknowns.append( ebrw_readstr.int_u32() )
		ebrw_readstr.skip(4)
		cls.unknowns.append( ebrw_readstr.int_s32() )
		ebrw_readstr.skip(4)
		cls.unknowns.append( ebrw_readstr.int_u32() )
		ebrw_readstr.skip(4)
		cls.unknowns.append( ebrw_readstr.double() )
		return cls

class item_sfnm:
	def __init__(self):
		self.data = None

	@classmethod
	def from_ebrw_readstr(cls, ebrw_readstr):
		cls = cls()
		cls.data = ebrw_readstr.rest()
		return cls

class item_vils:
	def __init__(self):
		self.data = None

	@classmethod
	def from_ebrw_readstr(cls, ebrw_readstr):
		cls = cls()
		cls.data = ebrw_readstr.rest()
		return cls



class group_objs:
	def __init__(self):
		self.data_objc = None
		self.data_oeff = None
		self.data_otrn = None
		self.data_3dau = None
		self.synth_data = None
		self.synth_filename = None
		self.data_orup = []
		self.data_AUFX = None
		self.data_omid = None
		self.data_usgr = None

	@classmethod
	def from_riffchunks(cls, riffchunks, ebrw_readstr, tabnum):
		cls = cls()
		for x in riffchunks.iter_reader(ebrw_readstr):
			if x.id == b'objc':
				printtxt(tabnum, x, 1)
				if check_isitem(x): cls.data_objc = item_objc.from_ebrw_readstr(ebrw_readstr)
			elif x.id == b'oeff':
				printtxt(tabnum, x, 0)
				if check_isitem(x): cls.data_oeff = item_oeff.from_ebrw_readstr(ebrw_readstr)
			elif x.id == b'otrn':
				printtxt(tabnum, x, 1)
				if check_isitem(x): cls.data_otrn = item_otrn.from_ebrw_readstr(ebrw_readstr)
			elif x.id == b'3dau':
				printtxt(tabnum, x, 1)
				if check_isitem(x): cls.data_3dau = item_3dau.from_ebrw_readstr(ebrw_readstr)
			elif x.id == b'orup':
				printtxt(tabnum, x, 1)
				if check_isitem(x): cls.data_orup.append(item_orup.from_ebrw_readstr(ebrw_readstr))
			elif x.id == b'sfnm':
				printtxt(tabnum, x, 1)
				if check_isitem(x): cls.synth_filename = ebrw_readstr.rest()
			elif x.id == b'synt':
				printtxt(tabnum, x, 1)
				if check_isitem(x): cls.synth_data = ebrw_readstr.rest()
			elif x.id == b'omid':
				printtxt(tabnum, x, 1)
				if check_isitem(x): cls.data_omid = item_omid.from_ebrw_readstr(ebrw_readstr)
			elif x.id == b'usgr':
				printtxt(tabnum, x, 1)
				if check_isitem(x): cls.data_usgr = item_usgr.from_ebrw_readstr(ebrw_readstr)
			elif x.id == b'AUFX':
				printtxt(tabnum, x, 1)
				if check_isgroup(x): cls.data_AUFX = group_AUFX.from_riffchunks(x, ebrw_readstr, tabnum+1)
			elif VERBOSE: printtxt(tabnum, x, 0) # print('unknown chunk in objs: '+str(x.id))
		return cls


class group_crss:
	def __init__(self):
		self.data_crsr = []

	@classmethod
	def from_riffchunks(cls, riffchunks, ebrw_readstr, tabnum):
		cls = cls()
		for x in riffchunks.iter_reader(ebrw_readstr):
			if x.id == b'crsr':
				printtxt(tabnum, x, 0)
				if check_isitem(x): cls.data_crsr.append(item_crsr.from_ebrw_readstr(ebrw_readstr))
			elif VERBOSE: printtxt(tabnum, x, 0) # print('unknown chunk in crss: '+str(x.id))
		return cls


class group_viif:
	def __init__(self):
		self.data_vils = []

	@classmethod
	def from_riffchunks(cls, riffchunks, ebrw_readstr, tabnum):
		cls = cls()
		for x in riffchunks.iter_reader(ebrw_readstr):
			if x.id == b'vils':
				printtxt(tabnum, x, 1)
				if check_isitem(x): cls.data_vils.append(item_vils.from_ebrw_readstr(ebrw_readstr))
			elif VERBOSE: printtxt(tabnum, x, 0) # print('unknown chunk in crss: '+str(x.id))
		return cls


class group_rngs:
	def __init__(self):
		self.data = []

	@classmethod
	def from_riffchunks(cls, riffchunks, ebrw_readstr, tabnum):
		cls = cls()
		cls.data = [x for x in riffchunks.iter_reader(ebrw_readstr)]
		return cls