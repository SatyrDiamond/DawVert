# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.data_bytes import dynbytearr
import numpy as np

dtype_ccinfo = np.dtype([
	('name', np.str_, 64),
	('def', np.int8),
	('math_add', np.int32),
	('math_div', np.int32)
	])

cc_data = np.zeros(128, dtype=dtype_ccinfo)
cc_data['math_add'][:] = 0
cc_data['math_div'][:] = 127

cc_data['math_add'][10] = -64
cc_data['math_div'][10] = 64

cc_defualtvals = cc_data['def']
cc_defualtvals[:] = 0
cc_defualtvals[7] = 100
cc_defualtvals[10] = 64
cc_defualtvals[11] = 100
cc_data['def'] = cc_defualtvals

cc_defualtnames = cc_data['name']
cc_defualtnames = np.zeros(128, (np.str_, 64))
for n in range(128): cc_defualtnames[n] = 'midi_cc_'+str(n)
cc_defualtnames[1] = 'modulation'
cc_defualtnames[2] = 'breath'
cc_defualtnames[7] = 'vol'
cc_defualtnames[10] = 'pan'
cc_defualtnames[11] = 'expression'
cc_defualtnames[64] = 'sustain'
cc_defualtnames[65] = 'portamento'
cc_defualtnames[66] = 'sostenuto'
cc_defualtnames[67] = 'soft_pedal'
cc_defualtnames[68] = 'legato'
cc_data['name'] = cc_defualtnames

ctrl_auto_premake = dynbytearr.dynbytearr_premake([
	('pos', np.uint32),
	('chanport', np.uint16),
	('ctrl', np.uint8),
	('val', np.int32),
	('before_note', np.int8),
	])

def calcval(val, cc):
	d = cc_data[cc]
	return (val+d['math_add'])/d['math_div']

class ctrl_data:
	__slots__ = ['all_ctrl','cur_ctrl','num_channels','num_ports']
	def __init__(self, num_ports, num_channels):
		self.all_ctrl = ctrl_auto_premake.create()
		self.cur_ctrl = self.all_ctrl.create_cursor()
		self.num_channels = num_channels
		self.num_ports = num_ports

	def __iter__(self):
		for x in self.all_ctrl.data:
			yield x

	def alloc(self, allocsize):
		self.all_ctrl.alloc(allocsize)

	def sort(self):
		self.all_ctrl.sort(['pos'])

	def add_point(self, pos, chanport, ctrl, val):
		self.cur_ctrl.add()
		self.cur_ctrl['pos'] = pos
		self.cur_ctrl['chanport'] = chanport
		self.cur_ctrl['ctrl'] = ctrl
		self.cur_ctrl['val'] = val

	def add_startpos(self, pos, chanport):
		ctrldata = self.all_ctrl.data
		n_data = ctrldata['chanport']==chanport
		if pos > -1:
			where_bef = np.where(np.logical_and(ctrldata['pos']<pos, n_data))
			where_eq = np.where(np.logical_and(ctrldata['pos']==pos, n_data))
			self.all_ctrl.data['before_note'][where_bef] = 2
			self.all_ctrl.data['before_note'][where_eq] = 1
		else:
			self.all_ctrl.data['before_note'][n_data] = 2

	def filter_chanport(self, chan, port):
		ctrldata = self.all_ctrl.data
		return ctrldata[np.where(ctrldata['chanport']==calc_channum(chan, port, self.num_channels))]

	def get_cc_used_fx(self, chanport):
		ctrldata = self.all_ctrl.data
		n_data = ctrldata[ctrldata['chanport']==chanport]

		fx_reverb = n_data[n_data['ctrl']==91]['val']
		fx_tremolo = n_data[n_data['ctrl']==92]['val']
		fx_chorus = n_data[n_data['ctrl']==93]['val']
		fx_detune = n_data[n_data['ctrl']==94]['val']
		fx_phaser = n_data[n_data['ctrl']==95]['val']
		fx_filter = n_data[n_data['ctrl']==74]['val']

		out = []
		if len(fx_reverb): out.append('reverb')
		if len(fx_tremolo): out.append('tremolo')
		if len(fx_chorus): out.append('chorus')
		if len(fx_detune): out.append('detune')
		if len(fx_phaser): out.append('phaser')
		if len(fx_filter): out.append('filter')
		return out

	def add_loops(self, transport_obj):
		ctrldata = self.all_ctrl.data
		rpgm_start = ctrldata[ctrldata['ctrl']==111]['pos']

		if len(rpgm_start):
			transport_obj.loop_active = True
			transport_obj.loop_start = rpgm_start[0]

		xmi_start = ctrldata[ctrldata['ctrl']==116]['pos']
		if len(xmi_start):
			transport_obj.loop_active = True
			transport_obj.loop_start = xmi_start[0]

		xmi_end = ctrldata[ctrldata['ctrl']==117]['pos']
		if len(xmi_end):
			transport_obj.loop_end = xmi_end[0]

	def get_init_vals(self, chanport):
		ctrldata = self.all_ctrl.get_used()
		wherebool = np.logical_and(ctrldata['before_note']!=0, ctrldata['chanport']==chanport)
		ctrldata = ctrldata[wherebool][['ctrl','val']]
		return np.unique(ctrldata, axis=0)

	def get_auto(self, chanport):
		ctrldata = self.all_ctrl.get_used()
		ctrldata = ctrldata[ctrldata['chanport']==chanport]
		for ccnum in np.unique(ctrldata['ctrl']):
			ccdata = ctrldata[ctrldata['ctrl']==ccnum]
			yield ccnum, ccdata[['pos','val']], int(np.count_nonzero(ccdata['before_note']==0))