# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import xtramath
from objects.convproj import autopoints
from functions import data_values
import numpy as np
import copy
import hashlib

class pitchmod:
	def __init__(self, c_note):
		self.current_pitch = 0
		self.start_note = c_note
		self.porta_target = c_note
		self.pitch_change = 1
		self.slide_data = {}

	def slide_tracker_porta_targ(self, note):
		self.porta_target = note

	def slide_porta(self, pos, pitch):
		if pitch != 0: self.pitch_change = pitch*1.5
		self.slide_data[pos] = [1.0, 'porta', self.pitch_change, self.porta_target]

	def slide_up(self, pos, pitch):
		if pitch != 0: self.pitch_change = pitch
		self.slide_data[pos] = [1.0, 'slide_c', self.pitch_change, self.porta_target]

	def slide_down(self, pos, pitch):
		if pitch != 0: self.pitch_change = pitch
		self.slide_data[pos] = [1.0, 'slide_c', -self.pitch_change, self.porta_target]

	def slide_note(self, pos, pitch, dur):
		self.slide_data[pos] = [dur, 'slide_n', dur, pitch]

	def to_pointdata(self):
		outslide = []

		prevpos = -10000
		slide_list = []
		for slidepart in self.slide_data:
			slide_list.append([slidepart]+self.slide_data[slidepart])

		for index, slidepart in enumerate(slide_list):
			if index != 0:
				slidepart_prev = slide_list[index-1]
				minval = min(slidepart[0]-slidepart_prev[0], slidepart_prev[1])
				mulval = minval/slidepart_prev[1] if slidepart_prev[1] != 0 else 1
				slidepart_prev[1] = minval
				if slidepart_prev[2] != 'slide_n': 
					slidepart_prev[3] = slidepart_prev[3]*mulval

		out_blocks = []

		cur_pitch = self.start_note

		for slidepart in slide_list:

			output_blk = False

			if slidepart[2] == 'slide_c': 
				cur_pitch += slidepart[3]
				output_blk = True

			if slidepart[2] == 'slide_n': 
				partslide = slidepart[1]/slidepart[3] if slidepart[3] != 0 else 1
				cur_pitch += (slidepart[4]-cur_pitch)*partslide
				output_blk = True
				
			if slidepart[2] == 'porta': 
				max_dur = min(abs(cur_pitch-slidepart[4]), slidepart[3])
				if cur_pitch > slidepart[4]: 
					cur_pitch -= max_dur
					output_blk = True
				if cur_pitch < slidepart[4]: 
					cur_pitch += max_dur
					output_blk = True
				slidepart[1] *= max_dur/slidepart[3]

			if output_blk: out_blocks.append([slidepart[0], slidepart[1], cur_pitch-self.start_note])

		islinked = False
		prevpos = -10000
		prevval = 0

		out_pointdata = []

		for slidepart in out_blocks:
			islinked = slidepart[0]-prevpos == slidepart[1]
			if not islinked: out_pointdata.append([slidepart[0], prevval])
			out_pointdata.append([slidepart[0]+slidepart[1], slidepart[2]])
			prevval = slidepart[2]
			prevpos = slidepart[0]

		return out_pointdata

	def to_points(self, notelist_obj):
		pointdata = self.to_pointdata()
		for spoint in pointdata:
			autopoints_obj = notelist_obj.last_add_auto('pitch')
			autopoints_obj.pos = spoint[0]
			autopoints_obj.value = spoint[1]









class notelist_data:
	dt = np.dtype([
		('used', np.int8), 
		('pos', np.float64), 
		('dur', np.float64), 
		('vol', np.float16),
		('key', np.int16),
		('is_inst', np.int8), 
		('is_extra', np.int8), 
		('is_auto', np.int8), 
		('is_slide', np.int8), 
		('is_multikey', np.int8), 
		('assoc_inst', np.uint16), 
		('assoc_extra', np.int32), 
		('assoc_auto', np.int32), 
		('assoc_slide', np.int32), 
		('assoc_multikey', np.int32), 
		]) 

	def __init__(self):
		self.init_nl()
		self.v_assoc_inst = []
		self.v_assoc_extra = []
		self.v_assoc_auto = []
		self.v_assoc_slide = []
		self.v_assoc_multikey = []
		self.cursor = 0
		self.num_notes = 0
		self.alloc_size = 16
		self.lastnote = 0

	def __copy__(self):
		new_obj = notelist_data()
		new_obj.v_assoc_inst = copy.deepcopy(self.v_assoc_inst)
		new_obj.v_assoc_extra = copy.deepcopy(self.v_assoc_extra)
		new_obj.v_assoc_auto = copy.deepcopy(self.v_assoc_auto)
		new_obj.v_assoc_slide = copy.deepcopy(self.v_assoc_slide)
		new_obj.v_assoc_multikey = copy.deepcopy(self.v_assoc_multikey)
		new_obj.cursor = self.cursor
		new_obj.num_notes = self.num_notes
		new_obj.alloc_size = self.alloc_size
		new_obj.lastnote = self.lastnote
		new_obj.nl = self.nl.copy()
		return new_obj

	def __eq__(self, nlo):
		nl_same = np.all(self.nl == nlo.nl) if len(self.nl)==len(nlo.nl) else False
		same_v_assoc_inst = self.v_assoc_inst == nlo.v_assoc_inst
		same_v_assoc_extra = self.v_assoc_extra == nlo.v_assoc_extra
		same_v_assoc_auto = self.v_assoc_auto == nlo.v_assoc_auto
		same_v_assoc_slide = self.v_assoc_slide == nlo.v_assoc_slide
		same_v_assoc_multikey = self.v_assoc_multikey == nlo.v_assoc_multikey

		all_issame = nl_same and same_v_assoc_inst and same_v_assoc_extra and same_v_assoc_auto and same_v_assoc_slide and same_v_assoc_multikey
		return all_issame

	def init_nl(self):
		self.nl = np.array([], dtype=notelist_data.dt)

	def __iter__(self):
		prev_cur = self.cursor
		for n, d in enumerate(self.nl):
			self.cursor = n
			yield d
		self.cursor = prev_cur

	def alloc_auto(self, num):
		newsize = self.num_notes+num
		if len(self.nl) < newsize: self.extend(self.alloc_size)

	def alloc(self, num):
		self.nl = np.zeros(num, dtype=notelist_data.dt)

	def extend(self, num):
		zeros = np.zeros(num, dtype=notelist_data.dt)
		self.nl = np.hstack((self.nl,zeros))

	def add(self):
		self.alloc_auto(1)
		num = self.num_notes
		note = self.nl[num]
		note['used'] = 1
		self.num_notes += 1
		self.lastnote = self.num_notes-1
		self.cursor = self.num_notes-1
		return note

	def getcur(self):
		return self.nl[self.cursor]

	def assoc_multikey_add(self, m_keys):
		if m_keys != None:
			note = self.nl[self.cursor]
			if len(m_keys) != 1:
				note['is_multikey'] = 1
				note['assoc_multikey'] = len(self.v_assoc_multikey)
				self.v_assoc_multikey.append(m_keys)
			else: note['key'] = m_keys[0]

	def assoc_multikey_get(self):
		note = self.nl[self.cursor]
		return self.v_assoc_multikey[note['assoc_multikey']] if note['is_multikey'] else [note['key']]

	def assoc_extra_add(self, t_extra):
		if t_extra:
			note = self.nl[self.cursor]
			note['is_extra'] = 1
			note['assoc_extra'] = len(self.v_assoc_extra)
			self.v_assoc_extra.append(t_extra)

	def assoc_extra_set(self, name, val):
		if not note['is_extra']: self.assoc_extra_add({name: val})
		else: self.v_assoc_extra[note['assoc_extra']][name] = val

	def assoc_extra_get(self):
		note = self.nl[self.cursor]
		return self.v_assoc_extra[note['assoc_extra']] if note['is_extra'] else None

	def assoc_auto_set(self):
		note = self.nl[self.cursor]
		if not note['is_auto']:
			note['is_auto'] = 1
			note['assoc_auto'] = len(self.v_assoc_auto)
			self.v_assoc_auto.append({})
		return self.v_assoc_auto[note['assoc_auto']]

	def assoc_auto_get(self):
		note = self.nl[self.cursor]
		return self.v_assoc_auto[note['assoc_auto']] if note['is_auto'] else None

	def assoc_slide_append(self, slide):
		note = self.nl[self.cursor]
		if not note['is_slide']:
			note['is_slide'] = 1
			note['assoc_slide'] = len(self.v_assoc_slide)
			self.v_assoc_slide.append([])
		self.v_assoc_slide[note['assoc_slide']].append(slide)

	def assoc_slide_get(self):
		note = self.nl[self.cursor]
		return self.v_assoc_slide[note['assoc_slide']] if note['is_slide'] else None

	def add_inst(self, t_inst):
		if t_inst not in self.v_assoc_inst: self.v_assoc_inst.append(t_inst)
		return self.v_assoc_inst.index(t_inst)

	def assoc_inst_add(self, t_inst):
		if t_inst:
			note = self.nl[self.cursor]
			note['is_inst'] = 1
			note['assoc_inst'] = self.add_inst(t_inst)

	def assoc_inst_get(self):
		note = self.nl[self.cursor]
		return self.v_assoc_inst[note['assoc_inst']] if note['is_inst'] else None

	def assoc_multikey_append(self, key):
		note = self.nl[self.cursor]
		if not note['is_multikey'] and key != note['key']: 
			self.assoc_multikey_add([note['key'], key])
		else: 
			mkeys = self.v_assoc_multikey[note['assoc_multikey']]
			if key not in mkeys: mkeys.append(key)

	def sort(self):
		nums = self.nl.argsort(order=['used', 'pos'])
		nonzero = np.count_nonzero(self.nl['used'])
		self.nl = np.roll(self.nl[nums], nonzero)
		self.num_notes = nonzero
		self.cursor = nonzero-1

	def extra_to_noteenv(self, nl_obj):
		extra_d = self.assoc_extra_get()
		auto_d = self.assoc_auto_get()
		if extra_d != None and auto_d == None:
			auto_d = self.assoc_auto_set()
			auto_d['pitch'] = autopoints.cvpj_autopoints(nl_obj.time_ppq, nl_obj.time_float, 'float')
			if 'finepitch' in extra_d:
				autopoint = auto_d['pitch'].add_point()
				autopoint.pos = 0
				autopoint.value = extra_d['finepitch']/100

	def notemod_conv(self, nl_obj):
		note = self.nl[self.cursor]
		if note['is_auto'] or note['is_slide']:
			auto_d = self.assoc_auto_get()
			slide_d = self.assoc_slide_get()

			if slide_d != None and auto_d == None:
				pointsdata = pitchmod(note['key'])
				for slidenote in slide_d:
					pointsdata.slide_note(slidenote[0], slidenote[2], slidenote[1])
				nmp = pointsdata.to_pointdata()
				auto_d = self.assoc_auto_set()
				auto_d['pitch'] = autopoints.cvpj_autopoints(nl_obj.time_ppq, nl_obj.time_float, 'float')
				for nmps in nmp:
					autopoint = auto_d['pitch'].add_point()
					autopoint.pos = nmps[0]
					autopoint.value = nmps[1]

			if slide_d == None and auto_d != None:
				if 'pitch' in auto_d:
					pitchauto = auto_d['pitch']
					pitchauto.remove_instant()
					pitchblocks = pitchauto.blocks()
					maxnote = max(self.assoc_multikey_get())
					for pb in pitchblocks:
						self.assoc_slide_append([pb[0], pb[1], pb[2]+maxnote, note[3], {}])

	def merge(self, targ, offset):
		copy_nl = targ.nl.copy()
		copy_nl['pos'] += offset
		self.v_assoc_inst, remap_inst = data_values.assoc_remap(self.v_assoc_inst, targ.v_assoc_inst)
		copy_nl['assoc_extra'] += len(self.v_assoc_extra)
		copy_nl['assoc_auto'] += len(self.v_assoc_auto)
		copy_nl['assoc_slide'] += len(self.v_assoc_slide)
		copy_nl['assoc_multikey'] += len(self.v_assoc_multikey)

		copy_nl['assoc_extra'] *= copy_nl['is_extra']
		copy_nl['assoc_auto'] *= copy_nl['is_auto']
		copy_nl['assoc_slide'] *= copy_nl['is_slide']
		copy_nl['assoc_multikey'] *= copy_nl['is_multikey']

		self.v_assoc_extra += targ.v_assoc_extra
		self.v_assoc_auto += targ.v_assoc_auto
		self.v_assoc_slide += targ.v_assoc_slide
		self.v_assoc_multikey += targ.v_assoc_multikey
		if remap_inst:
			for n, x in enumerate(copy_nl['assoc_inst']):
				copy_nl['assoc_inst'][n] = remap_inst[x]
		self.nl = np.concatenate([self.nl, copy_nl])
		
		self.sort()


verbose = False

class cvpj_notelist:
	def __init__(self, time_ppq, time_float):
		self.nld = notelist_data()
		self.time_ppq = time_ppq
		self.time_float = time_float

	def __copy__(self):
		new_obj = cvpj_notelist(self.time_ppq, self.time_float)
		new_obj.nld = self.nld.__copy__()
		return new_obj

	def __eq__(self, nlo):
		nl_same = self.nld == nlo.nld
		time_ppq_same = self.time_ppq == nlo.time_ppq
		time_float_same = self.time_float == nlo.time_float
		return nl_same and time_ppq_same and time_float_same

	def __getitem__(self, name):
		return self.nld[name]

	def inst_split(self):
		if verbose: print('[notelist] inst_split')
		nldata = self.nld.nl
		out_nl = {}
		w_used = np.where(nldata['used'] == 1)
		for num, inst in enumerate(self.nld.v_assoc_inst):
			w_inst = np.where(nldata['assoc_inst'] == num)
			splitnl = cvpj_notelist(self.time_ppq, self.time_float)
			splitnld = splitnl.nld
			splitnld.nl = nldata[np.intersect1d(w_used, w_inst)]
			if len(splitnld.nl):
				splitnld.nl['assoc_inst'] = 0
				splitnld.v_assoc_inst = [inst]
				splitnld.v_assoc_extra = self.nld.v_assoc_extra.copy()
				splitnld.v_assoc_auto = self.nld.v_assoc_auto.copy()
				splitnld.v_assoc_slide = copy.deepcopy(self.nld.v_assoc_slide)
				splitnld.v_assoc_multikey = self.nld.v_assoc_multikey.copy()
				splitnld.num_notes = len(splitnld.nl)
				out_nl[inst] = splitnl
		return out_nl

	def inst_all(self, instid):
		if verbose: print('[notelist] inst_all')
		self.nld.v_assoc_inst = [instid]
		self.nld.nl['is_inst'] = 1
		self.nld.nl['assoc_inst'] = 0

	def stretch(self, time_ppq, time_float):
		if verbose: print('[notelist] stretch |', len(self.nld.nl), end=' | ')
		for note in self.nld:
			note['pos'] = xtramath.change_timing(self.time_ppq, time_ppq, time_float, note['pos'])
			note['dur'] = xtramath.change_timing(self.time_ppq, time_ppq, time_float, note['dur'])

		for slides in self.nld.v_assoc_slide:
			for sn in slides:
				sn[0] = xtramath.change_timing(self.time_ppq, time_ppq, time_float, sn[0])
				sn[1] = xtramath.change_timing(self.time_ppq, time_ppq, time_float, sn[1])

		for autos in self.nld.v_assoc_auto:
			for t in autos: autos[t].change_timings(time_ppq, time_float)

		if verbose: print(len(self.nld.nl))

	def change_timings(self, time_ppq, time_float):
		self.stretch(time_ppq, time_float)

		self.time_ppq = time_ppq
		self.time_float = time_float

	def add_r(self, t_pos, t_dur, t_key, t_vol, t_extra):
		#if verbose: print('[notelist] add_r')
		note = self.nld.add()
		note['pos'] = t_pos
		note['dur'] = t_dur
		note['vol'] = t_vol
		note['key'] = t_key
		self.nld.assoc_extra_add(t_extra)

	def add_r_multi(self, t_pos, t_dur, m_keys, t_vol, t_extra):
		#if verbose: print('[notelist] add_r_multi')
		note = self.nld.add()
		note['pos'] = t_pos
		note['dur'] = t_dur
		note['vol'] = t_vol
		self.nld.assoc_extra_add(t_extra)
		self.nld.assoc_multikey_add(m_keys)

	def add_m(self, t_inst, t_pos, t_dur, t_key, t_vol, t_extra):
		#if verbose: print('[notelist] add_m')
		note = self.nld.add()
		note['pos'] = t_pos
		note['dur'] = t_dur
		note['vol'] = t_vol
		note['key'] = t_key
		self.nld.assoc_inst_add(t_inst)
		self.nld.assoc_extra_add(t_extra)

	def add_m_multi(self, t_inst, t_pos, t_dur, m_keys, t_vol, t_extra):
		#if verbose: print('[notelist] add_m_multi')
		note = self.nld.add()
		note['pos'] = t_pos
		note['dur'] = t_dur
		note['vol'] = t_vol
		self.nld.assoc_inst_add(t_inst)
		self.nld.assoc_extra_add(t_extra)
		self.nld.assoc_multikey_add(m_keys)

	def last_add_auto(self, a_type):
		if verbose: print('[notelist] last_add_auto')
		autodata = self.nld.assoc_auto_set()
		if a_type not in autodata: 
			autodata[a_type] = autopoints.cvpj_autopoints(self.time_ppq, self.time_float, 'float')
		return autodata[a_type].add_point()

	def last_add_slide(self, t_pos, t_dur, t_key, t_vol, t_extra):
		if verbose: print('[notelist] last_add_slide')
		slidedata = self.nld.assoc_slide_append([t_pos, t_dur, t_key, t_vol, t_extra])

	def last_add_vol(self, i_val):
		if verbose: print('[notelist] last_add_vol')
		note = self.nld.getcur()
		note['vol'] = i_val

	def last_add_extra(self, i_name, i_val):
		if verbose: print('[notelist] last_add_extra')
		note = self.nld.assoc_extra_set(i_name, i_val)

	def last_extend_pos(self, endpos):
		if verbose: print('[notelist] last_extend_pos')
		if np.count_nonzero(self.nld.nl['used']):
			note = self.nld.getcur()
			note['dur'] = endpos-note['pos']

	def last_extend(self, dur):
		if verbose: print('[notelist] last_extend')
		if np.count_nonzero(self.nld.nl['used']):
			note = self.nld.getcur()
			note['dur'] += dur

	def auto_add_slide(self, t_inst, t_pos, t_dur, t_key, t_vol, t_extra):
		if verbose: print('[notelist] auto_add_slide')
		for note in self.nld:
			n_inst = note['assoc_inst'] if note['is_inst'] else None
			s_inst = self.nld.v_assoc_inst.index(t_inst) if t_inst in self.nld.v_assoc_inst else None

			match_pos = (note['pos'] <= t_pos < note['pos']+note['dur'])
			match_inst = n_inst == s_inst

			if note['used'] and match_pos and match_inst:
				sn_pos = t_pos - note['pos'] 
				sn_key = t_key
				slidedata = self.nld.assoc_slide_append([sn_pos, t_dur, sn_key, t_vol, t_extra])

	def notesfound(self):
		return self.nld.nl.size != 0

	def get_dur(self):
		if verbose: print('[notelist] get_dur')
		tab = self.nld.nl['pos']+self.nld.nl['dur']
		#print(self.nld.nl)
		return max(tab) if tab.any() else 0

	def get_start(self):
		if verbose: print('[notelist] get_start')
		tab = self.nld.nl['pos']
		return min(tab) if tab.any() else 0

	def get_start_end(self):
		if verbose: print('[notelist] get_start_end')
		ma = self.nld.nl['pos']+self.nld.nl['dur']
		return min(ma) if ma.any() else 0, max(ma) if ma.any() else 0

	def edit_move(self, pos):
		if verbose: print('[notelist] edit_move |', len(self.nld.nl), end=' | ')
		self.nld.nl['pos'] += pos
		used = [n for n, x in enumerate(self.nld.nl['pos']) if x>=0]
		self.nld.nl = self.nld.nl[used]
		if verbose: print(len(self.nld.nl))

	def edit_move_minus(self, pos):
		if verbose: print('[notelist] edit_move_minus |', len(self.nld.nl), end=' | ')
		self.nld.nl['pos'] += pos
		if verbose: print(len(self.nld.nl))

	def edit_trim(self, pos):
		if verbose: print('[notelist] edit_trim |', len(self.nld.nl), end=' | ')
		self.nld.nl['pos'] += pos
		used = [n for n, x in enumerate(self.nld.nl['pos']) if x>=pos]
		self.nld.nl = self.nld.nl[used]
		if verbose: print(len(self.nld.nl))

	def edit_trim_limit(self, pos):
		if verbose: print('[notelist] edit_trim_limit |', len(self.nld.nl), end=' | ')
		self.nld.nl['pos'] += pos
		used = [n for n, x in enumerate(self.nld.nl['pos']) if x>=pos]
		self.nld.nl = self.nld.nl[used]
		if verbose: print(len(self.nld.nl))
		self.clean()

	def edit_trimmove(self, startat, endat):
		if verbose: print('[notelist] edit_trimmove |', len(self.nld.nl), end=' | ')
		used = [n for n, x in enumerate(self.nld.nl['pos']) if endat>x>=startat]
		self.nld.nl['pos'] += -startat
		self.nld.nl = self.nld.nl[used]
		if verbose: print(len(self.nld.nl))

	def new_nl_start_end(self, startat, endat):
		if verbose: print('[notelist] new_nl_start_end |', startat, endat, end=' | ')
		used = [n for n, x in enumerate(self.nld.nl['pos']) if endat>x>=startat]

		new_nl = cvpj_notelist(self.time_ppq, self.time_float)
		new_nl.nld.nl = self.nld.nl[used].copy()
		new_nl.nld.v_assoc_inst = copy.deepcopy(self.nld.v_assoc_inst)
		new_nl.nld.v_assoc_extra = copy.deepcopy(self.nld.v_assoc_extra)
		new_nl.nld.v_assoc_auto = copy.deepcopy(self.nld.v_assoc_auto)
		new_nl.nld.v_assoc_slide = copy.deepcopy(self.nld.v_assoc_slide)
		new_nl.nld.v_assoc_multikey = copy.deepcopy(self.nld.v_assoc_multikey)
		new_nl.nld.nl['pos'] += -startat
		new_nl.sort()
		new_nl.clean()
		return new_nl

	def mod_scale(self, i_size):
		if verbose: print('[notelist] mod_scale')
		self.nld.nl['pos'] *= i_size
		self.nld.nl['dur'] *= i_size

	def mod_transpose(self, i_key):
		if verbose: print('[notelist] mod_transpose')
		self.nld.nl['key'] += i_key
		self.nld.v_assoc_multikey = [[x+i_key for x in n] for n in self.nld.v_assoc_multikey]

	def mod_weird(self, i_key):
		if verbose: print('[notelist] mod_weird')
		self.nld.nl['key'] *= i_key
		self.nld.v_assoc_multikey = [[x*i_key for x in n] for n in self.nld.v_assoc_multikey]

	def clean(self):
		if verbose: print('[notelist] clean')
		self.nld.nl = self.nld.nl[np.nonzero(self.nld.nl['used'])]

	def sort(self):
		if verbose: print('[notelist] sort |', len(self.nld.nl), end=' | ')
		self.nld.sort()
		if verbose: print(len(self.nld.nl))

	def clear(self):
		if verbose: print('[notelist] clear')
		nld = self.nld
		nld.init_nl()
		nld.v_assoc_inst = []
		nld.v_assoc_extra = []
		nld.v_assoc_auto = []
		nld.v_assoc_slide = []
		nld.v_assoc_multikey = []
		nld.cursor = 0
		nld.num_notes = 0
		nld.lastnote = 0

	def clear_size(self, i_size):
		if verbose: print('[notelist] clear_size')
		self.nld.alloc(i_size)
		self.nld.v_assoc_inst = []
		self.nld.v_assoc_extra = []
		self.nld.v_assoc_auto = []
		self.nld.v_assoc_slide = []
		self.nld.v_assoc_multikey = []
		self.nld.cursor = 0
		self.nld.num_notes = 0
		self.nld.lastnote = 0

	def last_arpeggio(self, notes):
		if verbose: print('[notelist] last_arpeggio')
		note = self.nld.getcur()
		counts = np.unique(notes, return_counts=True)
		isduped = True in (counts[1]>2)
		if not isduped: 
			self.nld.assoc_multikey_add([note['key']+x for x in notes])

	def add_instpos(self, instlocs):
		if verbose: print('[notelist] add_instpos')
		nld = self.nld

		if len(self.nld.nl):
			if len(instlocs)==1:
				self.inst_all(instlocs[0][1])
	
			if len(instlocs)>1:
				inst_data = np.zeros(len(instlocs), dtype=np.dtype([('start', np.float64), ('end', np.float64), ('inst', np.int16), ('name', np.str_, 256)]))
	
				maxval = np.max(self.nld.nl['pos']+self.nld.nl['dur'])
	
				inst_data['start'] = [x[0] for x in instlocs]
				inst_data['end'] = [x[0] for x in instlocs[1:]]+[maxval]
				inst_data['inst'] = [nld.add_inst(x[1]) for x in instlocs]
				inst_data['name'] = [x[1] for x in instlocs]
	
				uniqueinsts = np.unique(inst_data)
	
				poses = self.nld.nl['pos']
				usedd = self.nld.nl['used']
				for n in inst_data:
					findex = np.where(np.logical_and(n['start']<=poses, poses<n['end'], usedd==1))
					self.nld.nl['is_inst'][findex] = 1
					self.nld.nl['assoc_inst'][findex] = n['inst']
	
				self.v_assoc_inst = uniqueinsts['name']

	def get_used_inst(self):
		return self.nld.v_assoc_inst

	def iter(self):
		for note in self.nld:
			if note['used']:
				t_pos = note['pos']
				t_dur = note['dur']
				t_keys = self.nld.assoc_multikey_get()
				t_vol = note['vol']
				t_inst = self.nld.assoc_inst_get()
				t_extra = self.nld.assoc_extra_get()
				t_auto = self.nld.assoc_auto_get()
				t_slide = self.nld.assoc_slide_get()
				yield t_pos, t_dur, t_keys, t_vol, t_inst, t_extra, t_auto, t_slide

	def debugtxt(self):
		print(len(self.nld.nl), 'notes')
		for note in self.nld:
			if note['used']:
				t_pos = note['pos']
				t_dur = note['dur']
				t_keys = self.nld.assoc_multikey_get()
				t_vol = note['vol']
				t_inst = self.nld.assoc_inst_get()
				t_extra = self.nld.assoc_extra_get()
				t_auto = self.nld.assoc_auto_get()
				t_slide = self.nld.assoc_slide_get()
				print(t_pos, t_dur, t_keys, t_vol, t_inst, t_extra, t_auto!=None, t_slide!=None)

	def notemod_conv(self):
		if verbose: print('[notelist] notemod_conv')
		for note in self.nld: self.nld.notemod_conv(self)

	def extra_to_noteenv(self):
		if verbose: print('[notelist] extra_to_noteenv')
		for note in self.nld: self.nld.extra_to_noteenv(self)

	def merge(self, i_nl, offset):
		if verbose: print('[notelist] merge')
		self.nld.merge(i_nl.nld, offset)

	def usedrange(self, start, end):
		if verbose: print('[notelist] usedrange')
		poses = self.nld.nl['pos']
		usedd = self.nld.nl['used']
		return len(self.nld.nl[np.where(np.logical_and(start<=poses, poses<end, usedd==1))]) != 0

	def usedoverflow(self, start, end):
		if verbose: print('[notelist] usedoverflow')
		poses = self.nld.nl['pos']
		usedd = self.nld.nl['used']
		usedposes = np.logical_and(start<=poses, poses<end)
		usedvals = np.where(np.logical_and(usedposes, usedd==1))
		filternl = self.nld.nl[usedvals]
		if len(filternl): return True, max(np.max(filternl['pos']+filternl['dur'])-end, 0) 
		else: return False, 0

	def appendtxt_inst(self, start, end):
		self.nld.v_assoc_inst = [start+x+end for x in self.nld.v_assoc_inst]

	def multikey_comb(self):
		prev_note = None
		for n, x in enumerate(self.nld.nl):
			if x['used'] == 1 and x['is_extra'] == x['is_auto'] == x['is_slide'] == x['is_multikey'] == 0:
				iffound_1 = np.logical_and(
					self.nld.nl['vol']==x['vol'],
					self.nld.nl['pos']==x['pos'],
				)
				iffound_2 = np.logical_and(
					self.nld.nl['dur']==x['dur'],
					self.nld.nl['is_inst']==x['is_inst'],
				)
				iffound_3 = np.logical_and(
					self.nld.nl['assoc_inst']==x['assoc_inst'],
					self.nld.nl['is_extra']==0,
				)
				iffound_4 = np.logical_and(
					self.nld.nl['is_auto']==0,
					self.nld.nl['is_slide']==0,
					self.nld.nl['is_multikey']==0,
				)
				iffound_5 = np.logical_and(iffound_1,iffound_2)
				iffound_6 = np.logical_and(iffound_3,iffound_4)

				iffound = np.logical_and(iffound_5,iffound_6,self.nld.nl['used']==1)

				foundvals = np.where(iffound)[0]
				if len(foundvals) > 1:
					multikeys = list(self.nld.nl['key'][foundvals])
					self.nld.nl['is_multikey'][foundvals[0]] = 1
					self.nld.nl['assoc_multikey'][foundvals[0]] = len(self.nld.v_assoc_multikey)
					self.nld.v_assoc_multikey.append(multikeys)

					for kn in foundvals[1:]: self.nld.nl['used'][kn] = 0

		self.clean()

	def get_hash(self):
		m = hashlib.md5()
		notebytes = self.nld.nl.tobytes()
		m.update(notebytes)
		return m.hexdigest() if len(notebytes) else None

	def get_hash_range(self, startat, endat):
		new_nl = self.new_nl_start_end(startat, endat)
		return new_nl.get_hash()

	def get_hash_split(self, splitdur, endat):
		return [self.get_hash_range(x, x+splitdur) for x in range(0, endat, splitdur)]