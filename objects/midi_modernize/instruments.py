# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.data_bytes import dynbytearr
import numpy as np
import objects.midi_modernize.devices_types as devices_types

# ------------------------------------------- inst -------------------------------------------

midi_instrument = np.dtype([
	('track', np.uint32),
	('chanport', np.uint8),
	('chan', np.uint8),
	('port', np.uint8),
	('drum', np.uint8),
	('bank_hi', np.uint8),
	('bank', np.uint8),
	('patch', np.uint8),
	('device', np.uint8),
	])

# ------------------------------------------- instchange -------------------------------------------

CHANGE__INST = 1
CHANGE__BANK = 2
CHANGE__HIBANK = 3
CHANGE__DRUM = 4
CHANGE__DEVICE = 5

instchange_premake = dynbytearr.dynbytearr_premake([
	('pos', np.uint64),
	('chanport', np.int32),
	('type', np.uint8),
	('val', np.uint8),
	])

class instchange:
	def __init__(self, num_ports, num_channels):
		self.num_channels = num_channels
		self.num_ports = num_ports
		self.data = instchange_premake.create()
		self.cur = self.data.create_cursor()

	def __iter__(self):
		return self.data.__iter__()

	def add_program(self, pos, chanport, val):
		self.cur.add()
		self.cur['type'] = CHANGE__INST
		self.cur['pos'] = pos
		self.cur['chanport'] = chanport
		self.cur['val'] = val

	def add_bank(self, pos, chanport, val):
		self.cur.add()
		self.cur['type'] = CHANGE__BANK
		self.cur['pos'] = pos
		self.cur['chanport'] = chanport
		self.cur['val'] = val

	def add_hibank(self, pos, chanport, val):
		self.cur.add()
		self.cur['type'] = CHANGE__HIBANK
		self.cur['pos'] = pos
		self.cur['chanport'] = chanport
		self.cur['val'] = val

	def add_drum(self, pos, chanport, val):
		self.cur.add()
		self.cur['type'] = CHANGE__DRUM
		self.cur['pos'] = pos
		self.cur['chanport'] = chanport
		self.cur['val'] = val

	def add_device(self, pos, val):
		self.cur.add()
		self.cur['type'] = CHANGE__DEVICE
		self.cur['pos'] = pos
		self.cur['val'] = val
		self.cur['chanport'] = -1

	def sort(self):
		self.data.sort(['pos'])

	def clean(self):
		self.data.clean()

def get_inst_id(indata):
	instnames = ['track','chanport','drum','bank_hi','bank','patch','device']
	return '_'.join([str(x) for x in indata[instnames]])

def cvpj_create_instrument(convproj_obj, inst):
	cvpj_instid = get_inst_id(inst)
	inst_obj = convproj_obj.instrument__add(cvpj_instid)
	midi_obj = inst_obj.midi.out_inst
	midi_obj.bank_hi = inst['bank_hi']
	midi_obj.bank = inst['bank']
	midi_obj.patch = inst['patch']
	midi_obj.drum = bool(inst['drum'])
	midi_obj.device = devices_types.get_devname(inst['device'])
	inst_obj.to_midi(convproj_obj, cvpj_instid, True)
	return inst_obj