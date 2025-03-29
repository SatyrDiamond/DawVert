# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.convproj.tracker import notestream
from objects.convproj.tracker import pat_data
from objects.convproj import visual

class single_pattern:
	def __init__(self, num_channels, num_rows):
		self.name = None
		self.num_rows = num_rows
		self.data = [pat_data.tracker_column() for x in range(num_channels)]
		self.notekeys = {}

	def cell_note(self, chan, row_num, note, inst):
		if len(self.data)>chan:
			self.data[chan].cell_note(row_num, note, inst)
			if note not in ['off', 'cut', None]:
				if inst not in self.notekeys: self.notekeys[inst] = {}
				if note not in self.notekeys[inst]: self.notekeys[inst][note] = 0
				self.notekeys[inst][note] += 1

	def cell_param(self, chan, row_num, p_name, p_val):
		if len(self.data)>chan:
			self.data[chan].cell_param(row_num, p_name, p_val)

	def cell_g_param(self, chan, row_num, p_name, p_val):
		if len(self.data)>chan:
			self.data[chan].cell_g_param(row_num, p_name, p_val)

	def cell_fx_mod(self, chan, row_num, fx_type, fx_value):
		if len(self.data)>chan:
			self.data[chan].cell_fx_mod(row_num, fx_type, fx_value)

	def cell_fx_s3m(self, chan, row_num, fx_type, fx_value):
		if len(self.data)>chan:
			self.data[chan].cell_fx_s3m(row_num, fx_type, fx_value)

class convproj_tracker_patsong:
	def __init__(self):
		self.num_chans = 0
		self.channels = [pat_data.tracker_channel() for _ in range(self.num_chans)]
		self.patdata = {}
		self.assoc_instid = {}
		self.mainvisual = visual.cvpj_visual()
		self.orders = []
		self.timepoints = []
		self.tempo = 120
		self.speed = 6
		self.use_starttempo = False

	def add_inst(self, convproj_obj, instnum, instid):
		instid = instid if instid else 'inst_'+str(instnum)
		inst_obj = convproj_obj.instrument__add(instid)
		inst_obj.visual.color = self.mainvisual.color.copy()
		self.assoc_instid[instnum+1] = instid
		return inst_obj

	def set_num_chans(self, num_chans):
		self.num_chans = num_chans
		self.channels = [pat_data.tracker_channel() for _ in range(num_chans)]

	def pattern_add(self, pat_num, num_rows):
		pat_obj = single_pattern(self.num_chans, num_rows)
		self.patdata[pat_num] = pat_obj
		return pat_obj

	def get_drum_notes(self):
		notekeys = {}
		for num, pd in self.patdata.items():
			for i_n, i_d in pd.notekeys.items():
				if i_n not in notekeys: notekeys[i_n] = {}
				for k_n, k_d in pd.notekeys[i_n].items():
					if k_n not in notekeys[i_n]: notekeys[i_n][k_n] = 0
					notekeys[i_n][k_n] += k_d

		return notekeys
