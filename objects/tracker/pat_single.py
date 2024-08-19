# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.tracker import notestream
from objects.tracker import pat_data

class cur_speed:
	def __init__(self, s_bpm, s_speed):
		self.tempo = s_bpm
		self.speed = s_speed
		self.changed = False

	def get_speed(self):
		return self.tempo*(6/(self.speed if self.speed else 1))

	def proc_data(self, idata):
		if 'speed' in idata: 
			self.speed = idata['speed']
			self.bpm_changed = True
		if 'tempo' in idata: 
			self.tempo = idata['tempo']
			self.bpm_changed = True

	def get_change(self):
		outval = (self.get_speed() if self.bpm_changed else None)
		self.bpm_changed = False
		return outval

class single_playstream:
	def __init__(self, patdata_obj):
		self.row_num = 0
		self.patdata_obj = patdata_obj
		self.num_chans = len(self.patdata_obj.channels)

	def stream_rows(self, p_num, cur_speed_obj):
		firstrow = True
		while self.row_num < self.cpat.num_rows:
			rowdata = [(x.data[self.row_num] if self.row_num in x.data else None) for x in self.cpat.data]
			g_data = {}
			for x in rowdata:
				if x: 
					if x.g_fx: g_data |= x.g_fx

			cur_speed_obj.proc_data(g_data)

			yield firstrow, g_data, self.row_num, rowdata, cur_speed_obj.get_change()

			if 'pattern_jump' in g_data: break
			if 'break_to_row' in g_data: break
			firstrow = False
			self.row_num += 1
		self.row_num = 0

	def stream_song(self, s_bpm, s_speed):
		cur_speed_obj = cur_speed(s_bpm, s_speed)

		cur_speed_obj.bpm_changed = True
		self.cpat_num = 0

		for i_num, p_num in enumerate(self.patdata_obj.orders):
			if p_num in self.patdata_obj.patdata:
				self.cpat = self.patdata_obj.patdata[p_num]
				self.cpat_num = p_num
				yield self.stream_rows(p_num, cur_speed_obj)


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

		notepl = [notestream.notestream(text_inst_start) for _ in range(self.num_chans)]
		autopl_tempo = notestream.autostream()

		playstream_obj = single_playstream(self)

		#notekeys = self.get_drum_notes()

		first_speed = None

		for pat_gen in playstream_obj.stream_song(s_bpm, s_speed):
			for firstrow, g_data, row_num, rowdata, speed_ch in pat_gen:
				if first_speed == None: speed_ch

				if firstrow: autopl_tempo.add_pl()

				if speed_ch: autopl_tempo.do_point(speed_ch)

				for c_num, x in enumerate(rowdata):
					nsc = notepl[c_num]
					if firstrow: nsc.add_pl(playstream_obj.cpat_num)
					nsc.do_cell_obj(x,s_speed)

				autopl_tempo.next()
				#print(firstrow, g_data, playstream_obj.cpat_num, row_num, speed_ch, [([x.note,x.inst,x.fx,x.g_fx] if x!=None else '') for x in rowdata])

		if use_starttempo and first_speed: convproj_obj.params.add('bpm', first_speed, 'float')
		autopl_tempo.to_cvpj(convproj_obj, ['main','bpm'])

		for ch_num in range(self.num_chans):
			notepl[ch_num].add_pl(-1)

		used_inst = []

		for ch_num, chan_obj in enumerate(self.channels):
			playlist_obj = convproj_obj.add_playlist(ch_num, True, False)
			playlist_obj.visual.name = chan_obj.name
			playlist_obj.visual.color = chan_obj.color

			cur_pl_pos = 0
			for tpl in notepl[ch_num].placements:
				if tpl[0]:
					for ui in tpl[3]:
						if ui not in used_inst: used_inst.append(ui)

					if tpl[1].notesfound():
						tpl[1].notemod_conv()
						placement_obj = playlist_obj.placements.add_notes()
						placement_obj.position = cur_pl_pos
						placement_obj.duration = tpl[0]
						placement_obj.notelist = tpl[1]
						placement_obj.visual.name = self.patdata[tpl[2]].name
				cur_pl_pos += tpl[0]

		patlentable = [x[0] for x in notepl[0].placements]
		convproj_obj.patlenlist_to_timemarker(patlentable[:-1], -1)

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