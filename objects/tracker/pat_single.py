# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.tracker import notestream
from objects.tracker import pat_data

class single_patsong:
	def __init__(self, num_channels, text_inst_start, maincolor):
		self.num_chans = num_channels
		self.channels = [pat_data.tracker_channel() for _ in range(self.num_chans)]
		self.patdata = {}
		self.text_inst_start = text_inst_start
		self.maincolor = maincolor
		self.orders = []

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

	def to_cvpj(self, convproj_obj, text_inst_start, s_bpm, s_speed, use_starttempo, maincolor):
		convproj_obj.type = 'm'
		convproj_obj.set_timings(4, True)

		playstr = pat_data.playstream()
		playstr.init_tempo(s_bpm, s_speed)
		for _ in range(self.num_chans): playstr.add_channel(text_inst_start)

		for n in self.orders:
			if n in self.patdata:
				singlepat_obj = self.patdata[n]
				playstr.init_patinfo(singlepat_obj.num_rows, n)
				playstr.columns = singlepat_obj.data
				while playstr.next_row(): pass

		if use_starttempo and playstr.first_speed: 
			convproj_obj.params.add('bpm', playstr.first_speed, 'float')
		playstr.auto_tempo.to_cvpj(convproj_obj, ['main','bpm'])
		playstr.auto_mastervol.to_cvpj(convproj_obj, ['main','vol'])

		for chns in playstr.notestreams: chns.add_pl(-1)

		used_inst = []

		for ch_num, chan_obj in enumerate(self.channels):
			playlist_obj = convproj_obj.playlist__add(ch_num, True, False)
			playlist_obj.visual.name = chan_obj.name
			playlist_obj.visual.color = chan_obj.color

			cur_pl_pos = 0
			for tpl in playstr.notestreams[ch_num].placements:
				if tpl[0]:
					for ui in tpl[3]:
						if ui not in used_inst: used_inst.append(ui)

					if tpl[1].notesfound():
						tpl[1].notemod_conv()
						placement_obj = playlist_obj.placements.add_notes()
						placement_obj.time.set_posdur(cur_pl_pos, tpl[0])
						placement_obj.notelist = tpl[1]
						placement_obj.visual.name = self.patdata[tpl[2]].name
				cur_pl_pos += tpl[0]

		patlentable = [x[0] for x in playstr.notestreams[0].placements]
		convproj_obj.timemarker__from_patlenlist(patlentable[:-1], -1)

		return used_inst


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