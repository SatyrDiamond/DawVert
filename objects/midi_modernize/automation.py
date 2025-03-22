# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import numpy as np
from objects.data_bytes import dynbytearr

# -----------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------
# --------------------------------------- AUTOLOC -----------------------------------------
# -----------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------

dtype_autoloc = np.dtype([
	('autoloc', (np.str_, 64), 4),
	('math_add', np.int32),
	('math_div', np.int32)
])

def gen_cc_names(p, c):
	ccdata = np.empty(128, dtype_autoloc)
	ccdata['autoloc'][:,0] = 'midi_cc'
	ccdata['autoloc'][:,1] = p
	ccdata['autoloc'][:,2] = c
	ccdata['autoloc'][:,3] = range(128)
	return ccdata

class autoloc_store:
	def __init__(self, num_ports, num_channels):
		self.num_channels = num_channels
		self.num_ports = num_ports
		self.data = np.empty([self.num_ports, self.num_channels, 128], dtype_autoloc)
		self.data_pitch = np.empty([self.num_ports, self.num_channels], dtype_autoloc)
		#self.init_names()

	def init_names(self):
		aloc = self.data
		for p in range(self.num_ports):
			for c in range(self.num_channels):
				ccdata = np.empty(128, dtype_autoloc)
				ccdata['autoloc'][:,0] = 'midi_cc'
				ccdata['autoloc'][:,1] = p
				ccdata['autoloc'][:,2] = c
				ccdata['autoloc'][:,3] = range(128)
				aloc[p,c] = ccdata

	def add_fxchan(self, p, curd_port, c, curd_channel):
		import objects.midi_modernize.ctrls as ctrls
		idstor = curd_channel['idstor']
		if idstor['used']:
			ccdata = np.empty(128, dtype_autoloc)
			ccdata['autoloc'][:,0] = 'fxmixer'
			ccdata['autoloc'][:,1] = idstor['chanid']
			ccdata['autoloc'][:,2] = ctrls.cc_defualtnames
			ccdata['autoloc'][:,3] = ''

			ccdata['math_add'][:] = ctrls.cc_data['math_add']
			ccdata['math_div'][:] = ctrls.cc_data['math_div']

			ccdata['autoloc'][93,0] = 'plugin'
			ccdata['autoloc'][93,1] = '_'.join([str(p), str(c), 'chorus'])
			ccdata['autoloc'][93,2] = 'amount'

			ccdata['autoloc'][91,0] = 'send'
			ccdata['autoloc'][91,1] = '_'.join([str(p), str(c), 'reverb'])
			ccdata['autoloc'][91,2] = 'amount'

			self.data[p,c] = ccdata

			self.data_pitch['autoloc'][p,c,0] = 'fxmixer'
			self.data_pitch['autoloc'][p,c,1] = idstor['chanid']
			self.data_pitch['autoloc'][p,c,2] = 'pitch'
			self.data_pitch['autoloc'][p,c,3] = ''

	def get_autoloc(self, po, ch, cc):
		return [str(i) for i in self.data[po,ch,cc]['autoloc'] if i != '']

	def get_autoloc_pitch(self, po, ch):
		return [str(i) for i in self.data_pitch[po,ch]['autoloc'] if i != '']

	def get_math(self, po, ch, cc):
		sdata = self.data[po,ch,cc]
		return int(sdata['math_add']), int(sdata['math_div'])

# -----------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------
# -------------------------------------- AUTOMATION ---------------------------------------
# -----------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------

auto_cc_channel = np.dtype([
	('cc_inital', np.int64, 130),
	('cc_dict_ids', np.uintp, 130),
	('cc_after_notes', np.int8, 130),
	])

class ctrl_auto:
	def __init__(self, num_ports, num_channels):
		import objects.midi_modernize.ctrls as ctrls
		self.num_channels = num_channels
		self.num_ports = num_ports
		self.diff = ctrl_auto_diff(self.num_ports, self.num_channels)
		self.data = np.zeros((self.num_ports, self.num_channels), dtype=auto_cc_channel)
		self.data_startvals = self.data['cc_inital']
		self.data_dictids = self.data['cc_dict_ids']
		self.data_after_notes = self.data['cc_after_notes']
		self.data_startvals[:] = cc_defualtvals[:]
		self.auto = {}

# -----------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------
# ---------------------------------------- TEMPO ------------------------------------------
# -----------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------

tempo_premake = dynbytearr.dynbytearr_premake([
	('pos', np.uint64),
	('value', np.float64)
	])

class tempo_data:
	def __init__(self):
		self.data = tempo_premake.create()
		self.cur = self.data.create_cursor()

	def alloc(self, allocsize):
		self.data.alloc(allocsize)

	def add(self, pos, val):
		cur = self.cur
		cur.add()
		cur['pos'] = pos
		cur['value'] = val

	def sort(self):
		self.data.sort(['pos'])

	def get_inital(self, pos):
		useddata = self.data.get_used()
		befvals = useddata[useddata['pos']<=pos]
		if len(befvals):
			ov = befvals[-1]
			return float(ov['value'])
		else:
			return 0

	def get_points(self):
		useddata = self.data.get_used()
		return useddata[['pos', 'value']]

# -----------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------
# --------------------------------------- TIMESIG -----------------------------------------
# -----------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------

timesig_premake = dynbytearr.dynbytearr_premake([
	('pos', np.uint64),
	('num', np.uint8),
	('denom', np.uint8)
	])

class timesig_data:
	def __init__(self):
		self.data = timesig_premake.create()
		self.cur = self.data.create_cursor()

	def alloc(self, allocsize):
		self.data.alloc(allocsize)

	def add(self, pos, num, denom):
		cur = self.cur
		cur.add()
		cur['pos'] = pos
		cur['num'] = num
		cur['denom'] = denom

	def sort(self):
		self.data.sort(['pos'])

	def get_inital(self, pos):
		useddata = self.data.get_used()
		befvals = useddata[useddata['pos']<=pos]
		if len(befvals):
			ov = befvals[-1]
			return [int(ov['num']), int(ov['denom'])]
		else:
			return None

	def get_points(self):
		useddata = self.data.get_used()
		return useddata[['pos', 'num', 'denom']]