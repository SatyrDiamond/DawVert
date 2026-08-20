# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from external.easybinrw import easybinrw
from objects.data_bytes import dynbytearr
from objects.exceptions import ProjectFileParserException
import numpy as np
import struct
import logging

VERBOSE = False
DEBUG_IN_OUT = False

logger_projparse = logging.getLogger('projparse')

class ptcop_delay:
	def __init__(self):
		self.unk1 = 0
		self.unk2 = 0
		self.unit = 0
		self.group = 0
		self.rate = 16000
		self.freq = 1.0

	def read(self, ebrw_readstr):
		self.unk1 = ebrw_readstr.int_u8()
		self.unk2 = ebrw_readstr.int_u8()
		self.unit = ebrw_readstr.int_u16()
		self.group = ebrw_readstr.int_u16()
		self.rate = ebrw_readstr.int_u16()
		self.freq = ebrw_readstr.float()

	def dump(self):
		ebrw_writestr = easybinrw.binwrite()
		ebrw_writestr.int_u8(self.unk1)
		ebrw_writestr.int_u8(self.unk2)
		ebrw_writestr.int_u16(self.unit)
		ebrw_writestr.int_u16(self.group)
		ebrw_writestr.int_u16(self.rate)
		ebrw_writestr.float(self.freq)
		return ebrw_writestr.getvalue()

class ptcop_overdrive:
	def __init__(self):
		self.xxx = 0
		self.group = 1
		self.cut = 50.0
		self.amp = 2.0
		self.yyy = 0.0

	def read(self, ebrw_readstr):
		self.xxx = ebrw_readstr.int_u16()
		self.group = ebrw_readstr.int_u16()
		self.cut = ebrw_readstr.float()
		self.amp = ebrw_readstr.float()
		self.yyy = ebrw_readstr.float()

	def dump(self):
		ebrw_writestr = easybinrw.binwrite()
		ebrw_writestr.int_u16(self.xxx)
		ebrw_writestr.int_u16(self.group)
		ebrw_writestr.float(self.cut)
		ebrw_writestr.float(self.amp)
		ebrw_writestr.float(self.yyy)
		return ebrw_writestr.getvalue()

class ptcop_master:
	def __init__(self):
		self.unk1 = 0
		self.beat = 0
		self.unk2 = 0
		self.beattempo = 0
		self.repeat = 0
		self.last = 0

	def read(self, ebrw_readstr):
		self.unk1 = ebrw_readstr.int_u16()
		self.beat = ebrw_readstr.int_u8()
		self.unk2 = ebrw_readstr.int_u16()
		self.beattempo = ebrw_readstr.int_u16_b()
		self.beattempo = struct.unpack(">f", struct.pack("I", self.beattempo))[0]
		self.repeat = ebrw_readstr.int_u32()
		self.last = ebrw_readstr.int_u32()

	def dump(self):
		ebrw_writestr = easybinrw.binwrite()
		ebrw_writestr.int_u16(self.unk1)
		ebrw_writestr.int_u8(self.beat)
		ebrw_writestr.int_u16(self.unk2)
		ebrw_writestr.int_u16_b(struct.unpack("I", struct.pack(">f", self.beattempo))[0])
		ebrw_writestr.int_u32(self.repeat)
		ebrw_writestr.int_u32(self.last)
		return ebrw_writestr.getvalue()

class ptcop_voice_mateOGGV:
	def __init__(self):
		self.basic_key_field = 69
		self.sps2 = [1]
		self.key_correct = 1.0
		self.channels = 2
		self.hz = 44100
		self.samples = 0
		self.data = b''

	def read(self, ebrw_readstr):
		ebrw_readstr.skip(3)
		self.basic_key_field = ebrw_readstr.int_u8()
		self.sps2 = ebrw_readstr.flags_i32()
		self.key_correct = ebrw_readstr.float()
		self.channels = ebrw_readstr.int_u32()
		self.hz = ebrw_readstr.int_u32()
		self.samples = ebrw_readstr.int_u32()
		self.data = ebrw_readstr.raw(ebrw_readstr.int_u32())

	def dump(self):
		ebrw_writestr = easybinrw.binwrite()
		ebrw_writestr.raw(b'\x00\x00\x00')
		ebrw_writestr.int_u8(self.basic_key_field)
		ebrw_writestr.flags_i32(self.sps2)
		ebrw_writestr.float(self.key_correct)
		ebrw_writestr.int_u32(self.channels)
		ebrw_writestr.int_u32(self.hz)
		ebrw_writestr.int_u32(self.samples)
		ebrw_writestr.raw_i32(self.data)
		return ebrw_writestr.getvalue()

class ptcop_voice_matePCM:
	def __init__(self):
		self.basic_key_field = 69
		self.sps2 = [0, 1]
		self.ch = 1
		self.bits = 8
		self.hz = 44100
		self.key_correct = 1.0
		self.samples = 0
		self.data = b''

	def read(self, ebrw_readstr):
		ebrw_readstr.skip(3)
		self.basic_key_field = ebrw_readstr.int_u8()
		self.sps2 = ebrw_readstr.flags_i32()
		self.ch = ebrw_readstr.int_u16()
		self.bits = ebrw_readstr.int_u16()
		self.hz = ebrw_readstr.int_u32()
		self.key_correct = ebrw_readstr.float()
		numbytes = self.bits//8
		self.samples = ebrw_readstr.int_u32()//numbytes
		self.data = ebrw_readstr.raw(numbytes * self.samples)

	def dump(self):
		ebrw_writestr = easybinrw.binwrite()
		ebrw_writestr.raw(b'\x00\x00\x00')
		ebrw_writestr.int_u8(self.basic_key_field)
		ebrw_writestr.flags_i32(self.sps2)
		ebrw_writestr.int_u16(self.ch)
		ebrw_writestr.int_u16(self.bits)
		ebrw_writestr.int_u32(self.hz)
		ebrw_writestr.float(self.key_correct)
		ebrw_writestr.raw_i32(self.data)
		return ebrw_writestr.getvalue()

class ptcop_voice_matePTV:
	def __init__(self):
		self.key_correct = 0.0
		self.data = b''

	def read(self, ebrw_readstr):
		ebrw_readstr.skip(4)
		self.key_correct = ebrw_readstr.float()
		datasize = ebrw_readstr.int_u32()
		self.data = ebrw_readstr.raw(datasize)

	def dump(self):
		ebrw_writestr = easybinrw.binwrite()
		ebrw_writestr.raw(b'\x00\x00\x00\x00')
		ebrw_writestr.float(self.key_correct)
		ebrw_writestr.raw_i32(self.data)
		return ebrw_writestr.getvalue()

class ptcop_voice_matePTN:
	def __init__(self):
		self.key_correct = 0
		self.basic_key_field = 69
		self.unk1 = 2
		self.unk2 = 1
		self.data = b''

	def read(self, ebrw_readstr):
		ebrw_readstr.skip(3)
		self.basic_key_field = ebrw_readstr.int_u8()
		self.unk1 = ebrw_readstr.int_u32()
		self.key_correct = ebrw_readstr.float()
		self.unk2 = ebrw_readstr.int_u32()
		self.data = ebrw_readstr.rest()

	def dump(self):
		ebrw_writestr = easybinrw.binwrite()
		ebrw_writestr.raw(b'\x00\x00\x00')
		ebrw_writestr.int_u8(self.basic_key_field)
		ebrw_writestr.int_u32(self.unk1)
		ebrw_writestr.float(self.key_correct)
		ebrw_writestr.int_u32(self.unk2)
		ebrw_writestr.raw(self.data)
		return ebrw_writestr.getvalue()

class ptcop_unit:
	def __init__(self):
		self.name = None

event_premake = dynbytearr.dynbytearr_premake([
	('position', np.uint32),
	('unitnum', np.uint8),
	('eventnum', np.uint8),
	('value', np.uint32),
	('d_position', np.uint32),
	])

def make_chunk(ebrw_writestr, header, data):
	ebrw_writestr.raw(header)
	ebrw_writestr.raw_i32(data)

class ptcop_song:
	def __init__(self):
		self.master = ptcop_master()
		self.comment = ''
		self.title = ''
		self.events = event_premake.create()
		self.units = []
		self.voices = {}
		self.delays = []
		self.overdrives = []
		self.header = b'PTCOLLAGE-071119'
		self.unk1 = 5

	def load_from_raw(self, input_data):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_data(input_data)
		return self.load(ebrw_readstr)

	def load_from_file(self, input_file):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_file(input_file)
		return self.load(ebrw_readstr)

	def load(self, ebrw_readstr):
		self.header = ebrw_readstr.raw(16)
		self.unk1 = ebrw_readstr.int_u32()

		voicenum = 0

		while ebrw_readstr.remaining():
			chunk_id = ebrw_readstr.raw(8)
			chunk_size = ebrw_readstr.int_u32()

			if chunk_id == b'Event V5':
				ev_cur = self.events.create_cursor()
				numevents = ebrw_readstr.int_u32()
				for _ in range(numevents):
					ev_cur.add()
					ev_cur['position'] = ebrw_readstr.varint()
					ev_cur['unitnum'] = ebrw_readstr.int_u8()
					ev_cur['eventnum'] = ebrw_readstr.int_u8()
					ev_cur['value'] = ebrw_readstr.varint()

			else:
				ebrw_readstr.isolate_size(chunk_size)

				if chunk_id == b'MasterV5':
					self.master.read(ebrw_readstr)

				elif chunk_id == b'effeDELA':
					delay_obj = ptcop_delay()
					delay_obj.read(ebrw_readstr)
					self.delays.append(delay_obj)
					if VERBOSE: print('effeDELA:', delay_obj.unit, delay_obj.group)

				elif chunk_id == b'effeOVER':
					overdrive_obj = ptcop_overdrive()
					overdrive_obj.read(ebrw_readstr)
					self.overdrives.append(overdrive_obj)
					if VERBOSE: print('effeOVER:', overdrive_obj.group)

				elif chunk_id == b'mateOGGV':
					voice_obj = ptcop_voice_mateOGGV()
					voice_obj.read(ebrw_readstr)
					self.voices[voicenum] = voice_obj
					if VERBOSE: print('mateOGGV:', voicenum)
					voicenum += 1

				elif chunk_id == b'matePCM ':
					voice_obj = ptcop_voice_matePCM()
					voice_obj.read(ebrw_readstr)
					self.voices[voicenum] = voice_obj
					if VERBOSE: print('mate PCM:', voicenum)
					voicenum += 1

				elif chunk_id == b'matePTV ':
					voice_obj = ptcop_voice_matePTV()
					voice_obj.read(ebrw_readstr)
					self.voices[voicenum] = voice_obj
					if VERBOSE: print('mate PTV:', voicenum)
					voicenum += 1

				elif chunk_id == b'matePTN ':
					voice_obj = ptcop_voice_matePTN()
					voice_obj.read(ebrw_readstr)
					self.voices[voicenum] = voice_obj
					if VERBOSE: print('mate PTN:', voicenum)
					voicenum += 1

				elif chunk_id == b'assiWOIC':
					voice_num = ebrw_readstr.int_u32()
					self.voices[voice_num].name = ebrw_readstr.string(chunk_size-4, encoding="shift-jis")
					if VERBOSE: print('assiWOIC:', voice_num, self.voices[voice_num].name)

				elif chunk_id == b'assiUNIT':
					unit_num = ebrw_readstr.int_u32()
					self.units[unit_num].name = ebrw_readstr.string(chunk_size-4, encoding="shift-jis")
					if VERBOSE: print('assiUNIT:', unit_num, self.units[unit_num].name)

				elif chunk_id == b'num UNIT':
					self.units = [ptcop_unit() for _ in range(ebrw_readstr.int_u32())]
					if VERBOSE: print('num UNIT:', self.voices[voice_num].name)

				elif chunk_id == b'textCOMM':
					self.comment = ebrw_readstr.string(chunk_size, encoding="shift-jis")
					if VERBOSE: print('textCOMM:', self.comment)

				elif chunk_id == b'textNAME':
					self.title = ebrw_readstr.string(chunk_size, encoding="shift-jis")
					if VERBOSE: print('textNAME:', self.title)

				elif chunk_id == b'pxtoneND':
					break

				else: raise ProjectFileParserException('pxtone: unknown chunk: '+str(chunk_id))

				ebrw_readstr.isolate_end()

		self.events.clean()
		self.postprocess()
		return True

	def postprocess(self):
		curpos = 0
		for x in self.events:
			curpos += x['position']
			x['d_position'] = curpos

	def write(self, ebrw_writestr):
		ebrw_writestr.raw(self.header)
		ebrw_writestr.int_u32(self.unk1)
		make_chunk(ebrw_writestr, b'MasterV5', self.master.dump())

		ebrw_writestr.raw(b'Event V5')
		ebrw_writestr.int_u32(len(self.events)*7)
		ebrw_writestr.int_u32(len(self.events))
		for x in self.events:
			ebrw_writestr.varint(x['position'])
			ebrw_writestr.int_u8(x['unitnum'])
			ebrw_writestr.int_u8(x['eventnum'])
			ebrw_writestr.varint(x['value'])

		if self.title: make_chunk(ebrw_writestr, b'textNAME', self.title.encode('shift-jis'))
		if self.comment: make_chunk(ebrw_writestr, b'textCOMM', self.comment.encode('shift-jis'))

		for delay_obj in self.delays:
			make_chunk(ebrw_writestr, b'effeDELA', delay_obj.dump())
		for overdrive_obj in self.overdrives:
			make_chunk(ebrw_writestr, b'effeOVER', overdrive_obj.dump())

		for voicenum in sorted(self.voices):
			voice_obj = self.voices[voicenum]
			if isinstance(voice_obj, ptcop_voice_mateOGGV): make_chunk(ebrw_writestr, b'mateOGGV', voice_obj.dump())
			if isinstance(voice_obj, ptcop_voice_matePCM): make_chunk(ebrw_writestr, b'matePCM ', voice_obj.dump())
			if isinstance(voice_obj, ptcop_voice_matePTV): make_chunk(ebrw_writestr, b'matePTV ', voice_obj.dump())
			if isinstance(voice_obj, ptcop_voice_matePTN): make_chunk(ebrw_writestr, b'matePTN ', voice_obj.dump())

			assiWOIC_ebrw_writestr = easybinrw.binwrite()
			assiWOIC_ebrw_writestr.int_u32(voicenum)
			assiWOIC_ebrw_writestr.string(voice_obj.name, 16, encoding='shift-jis')
			make_chunk(ebrw_writestr, b'assiWOIC', assiWOIC_ebrw_writestr.getvalue())
			
		numUNIT_ebrw_writestr = easybinrw.binwrite()
		numUNIT_ebrw_writestr.int_u32(len(self.units))
		make_chunk(ebrw_writestr, b'num UNIT', numUNIT_ebrw_writestr.getvalue())
	
		for num, unit in enumerate(self.units):
			assiUNIT_ebrw_writestr = easybinrw.binwrite()
			assiUNIT_ebrw_writestr.int_u32(num)
			assiUNIT_ebrw_writestr.string(unit.name, 16, encoding='shift-jis')
			make_chunk(ebrw_writestr, b'assiUNIT', assiUNIT_ebrw_writestr.getvalue())

		make_chunk(ebrw_writestr, b'pxtoneND', b'')

	def save_to_file(self, output_file):
		ebrw_writestr = easybinrw.binwrite()
		self.write(ebrw_writestr)
		f = open(output_file, 'wb')
		f.write(ebrw_writestr.getvalue())