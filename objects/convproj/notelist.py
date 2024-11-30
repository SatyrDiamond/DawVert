# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import xtramath
from objects.convproj import autopoints
from functions import data_values
import numpy as np
import copy
import hashlib
import os

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

class notelist_cursor:
	def __init__(self, base_nl):
		self.base_nl = base_nl
		self.pos = -1
		self.enable_go_last = True
		self.goto_last()

	def __iter__(self):
		oldpos = self.pos
		self.enable_go_last = False
		for pos, data in enumerate(self.base_nl):
			self.pos = pos
			yield data
		self.pos = oldpos
		self.enable_go_last = True

	def goto_last(self):
		ones = np.where(self.base_nl['used']==1)
		self.pos = ones[0][-1] if len(ones[0]) else -1

	def getcur(self):
		if self.base_nl.go_last and self.enable_go_last:
			self.goto_last()
			self.base_nl.go_last = False
		return self.base_nl[self.pos]

	def add(self):
		if self.base_nl.go_last:
			self.goto_last()
			self.base_nl.go_last = False
		self.pos += 1
		self.base_nl.alloc_auto(self.pos+1)
		cur_obj = self.getcur()
		cur_obj['used'] = 1
		return cur_obj

	def add_r(self, t_pos, t_dur, t_key, t_vol, t_extra):
		note = self.add()
		note['pos'] = t_pos
		note['dur'] = t_dur
		note['vol'] = t_vol
		note['key'] = t_key
		self.assoc_extra_add(t_extra)

	def add_r_multi(self, t_pos, t_dur, m_keys, t_vol, t_extra):
		note = self.add()
		note['pos'] = t_pos
		note['dur'] = t_dur
		note['vol'] = t_vol
		self.assoc_extra_add(t_extra)
		self.assoc_multikey_add(m_keys)

	def add_m(self, t_inst, t_pos, t_dur, t_key, t_vol, t_extra):
		note = self.add()
		note['pos'] = t_pos
		note['dur'] = t_dur
		note['vol'] = t_vol
		note['key'] = t_key
		self.assoc_inst_add(t_inst)
		self.assoc_extra_add(t_extra)

	def add_m_multi(self, t_inst, t_pos, t_dur, m_keys, t_vol, t_extra):
		note = self.add()
		note['pos'] = t_pos
		note['dur'] = t_dur
		note['vol'] = t_vol
		self.assoc_inst_add(t_inst)
		self.assoc_extra_add(t_extra)
		self.assoc_multikey_add(m_keys)

	def assoc_multikey_add(self, m_keys):
		if m_keys != None:
			note = self.getcur()
			if len(m_keys) != 1:
				v_assoc_multikey = self.base_nl.v_assoc_multikey
				note['is_multikey'] = 1
				note['assoc_multikey'] = len(v_assoc_multikey)
				v_assoc_multikey.append(m_keys)
			else: note['key'] = m_keys[0]

	def assoc_multikey_get(self):
		v_assoc_multikey = self.base_nl.v_assoc_multikey
		note = self.getcur()
		return v_assoc_multikey[note['assoc_multikey']] if note['is_multikey'] else [note['key']]

	def assoc_multikey_append(self, key):
		v_assoc_multikey = self.base_nl.v_assoc_multikey
		note = self.getcur()
		if not note['is_multikey'] and key != note['key']: 
			self.assoc_multikey_add([note['key'], key])
		else: 
			mkeys = v_assoc_multikey[note['assoc_multikey']]
			if key not in mkeys: mkeys.append(key)

	def assoc_extra_add(self, t_extra):
		if t_extra:
			v_assoc_extra = self.base_nl.v_assoc_extra
			note = self.getcur()
			note['is_extra'] = 1
			note['assoc_extra'] = len(v_assoc_extra)
			v_assoc_extra.append(t_extra)

	def assoc_extra_set(self, name, val):
		v_assoc_extra = self.base_nl.v_assoc_extra
		note = self.getcur()
		if not note['is_extra']: self.assoc_extra_add({name: val})
		else: v_assoc_extra[note['assoc_extra']][name] = val

	def assoc_extra_get(self):
		v_assoc_extra = self.base_nl.v_assoc_extra
		note = self.getcur()
		return v_assoc_extra[note['assoc_extra']] if note['is_extra'] else None

	def assoc_auto_set(self):
		v_assoc_auto = self.base_nl.v_assoc_auto
		note = self.getcur()
		if not note['is_auto']:
			note['is_auto'] = 1
			note['assoc_auto'] = len(v_assoc_auto)
			v_assoc_auto.append({})
		return v_assoc_auto[note['assoc_auto']]

	def assoc_auto_get(self):
		v_assoc_auto = self.base_nl.v_assoc_auto
		note = self.getcur()
		return v_assoc_auto[note['assoc_auto']] if note['is_auto'] else None

	def assoc_slide_append(self, slide):
		v_assoc_slide = self.base_nl.v_assoc_slide
		note = self.getcur()
		if not note['is_slide']:
			note['is_slide'] = 1
			note['assoc_slide'] = len(v_assoc_slide)
			v_assoc_slide.append([])
		v_assoc_slide[note['assoc_slide']].append(slide)

	def assoc_slide_get(self):
		v_assoc_slide = self.base_nl.v_assoc_slide
		note = self.getcur()
		return v_assoc_slide[note['assoc_slide']] if note['is_slide'] else None

	def assoc_inst_add(self, t_inst):
		if t_inst:
			note = self.getcur()
			note['is_inst'] = 1
			note['assoc_inst'] = self.base_nl.add_inst(t_inst)

	def assoc_inst_get(self):
		note = self.getcur()
		return self.base_nl.v_assoc_inst[note['assoc_inst']] if note['is_inst'] else None

	def extra_to_noteenv(self, time_ppq, time_float):
		nl_obj = self.base_nl
		extra_d = self.assoc_extra_get()
		auto_d = self.assoc_auto_get()
		if extra_d != None and auto_d == None:
			auto_d = self.assoc_auto_set()
			if 'pitch' not in auto_d:
				auto_d['pitch'] = autopoints.cvpj_autopoints(time_ppq, time_float, 'float')
				if 'finepitch' in extra_d:
					autopoint = auto_d['pitch'].add_point()
					autopoint.pos = 0
					autopoint.value = extra_d['finepitch']/100

	def notemod_conv(self, time_ppq, time_float):
		nl_obj = self.base_nl
		note = self.getcur()
		if note['is_auto'] or note['is_slide']:
			auto_d = self.assoc_auto_get()
			slide_d = self.assoc_slide_get()

			if slide_d != None and auto_d == None:
				pointsdata = pitchmod(note['key'])
				for slidenote in slide_d: pointsdata.slide_note(slidenote[0], slidenote[2], slidenote[1])
				nmp = pointsdata.to_pointdata()
				auto_d = self.assoc_auto_set()
				auto_d['pitch'] = autopoints.cvpj_autopoints(time_ppq, time_float, 'float')
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

verbose_copy = False

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

	__slots__ = [
		'v_assoc_inst', 'v_assoc_extra', 'v_assoc_auto', 
		'v_assoc_slide', 'v_assoc_multikey', 'alloc_size', 
		'num_notes', 'nl', 'go_last'
		]

	def __init__(self):
		self.init_nl()
		self.v_assoc_inst = []
		self.v_assoc_extra = []
		self.v_assoc_auto = []
		self.v_assoc_slide = []
		self.v_assoc_multikey = []
		self.alloc_size = 16
		self.num_notes = 0

	def init_nl(self):
		self.nl = np.array([], dtype=notelist_data.dt)
		self.go_last = True

	def clean(self):
		self.nl = self.nl[np.nonzero(self.nl['used'])]
		self.go_last = True

	def after_proc(self):
		self.num_notes = self.count()
		self.sort()
		self.clean()

	def __copy__(self):
		if verbose_copy: print(len(self.nl),'notelist_data, verbose_copy')
		new_obj = notelist_data()
		new_obj.v_assoc_inst = copy.deepcopy(self.v_assoc_inst)
		new_obj.v_assoc_extra = copy.deepcopy(self.v_assoc_extra)
		new_obj.v_assoc_auto = copy.deepcopy(self.v_assoc_auto)
		new_obj.v_assoc_slide = copy.deepcopy(self.v_assoc_slide)
		new_obj.v_assoc_multikey = copy.deepcopy(self.v_assoc_multikey)
		new_obj.alloc_size = self.alloc_size
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

	def __len__(self):
		return self.nl.__len__()

	def __iter__(self):
		return self.nl.__iter__()

	def __getitem__(self, a):
		return self.nl.__getitem__(a)

	def __setitem__(self, a, b):
		return self.nl.__setitem__(a, b)

	def count(self):
		return np.count_nonzero(self.nl['used'])

	def alloc_auto(self, pos):
		newsize = self.num_notes+pos
		if len(self.nl) < newsize: 
			self.extend(self.alloc_size)

	def alloc(self, num):
		self.nl = np.zeros(num, dtype=notelist_data.dt)

	def extend(self, num):
		zeros = np.zeros(num, dtype=notelist_data.dt)
		self.nl = np.hstack((self.nl,zeros))

	def add_inst(self, t_inst):
		if t_inst not in self.v_assoc_inst: self.v_assoc_inst.append(t_inst)
		return self.v_assoc_inst.index(t_inst)

	def inst_all(self, instid):
		self.v_assoc_inst = [instid]
		self.nl['is_inst'] = 1
		self.nl['assoc_inst'] = 0

	def sort(self):
		nums = self.nl.argsort(order=['used', 'pos'])
		nonzero = np.count_nonzero(self.nl['used'])
		self.nl = np.roll(self.nl[nums], nonzero)
		self.go_last = True

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
		self.go_last = True
		if remap_inst:
			for n, x in enumerate(copy_nl['assoc_inst']):
				copy_nl['assoc_inst'][n] = remap_inst[x]
		self.nl = np.concatenate([self.nl, copy_nl])
		self.after_proc()

	def appendtxt_inst(self, start, end):
		self.v_assoc_inst = [start+x+end for x in self.v_assoc_inst]

verbose = False

class cvpj_notelist:

	__slots__ = ['data', 'cursor', 'time_ppq', 'time_float']

	def __init__(self, time_ppq, time_float):
		self.data = notelist_data()
		self.cursor = notelist_cursor(self.data)
		self.time_ppq = time_ppq
		self.time_float = time_float

	def create_cursor(self):
		cursor_obj = notelist_cursor(self.data)
		cursor_obj.go_last = True
		return cursor_obj

	def __copy__(self):
		if verbose_copy: print(len(self.data),'cvpj_notelist, verbose_copy')
		new_obj = cvpj_notelist(self.time_ppq, self.time_float)
		new_obj.data = self.data.__copy__()
		new_obj.cursor = notelist_cursor(new_obj.data)
		new_obj.cursor.goto_last()
		return new_obj

	def __eq__(self, nlo):
		nl_same = self.data == nlo.data
		time_ppq_same = self.time_ppq == nlo.time_ppq
		time_float_same = self.time_float == nlo.time_float
		return nl_same and time_ppq_same and time_float_same

	def __len__(self):
		return self.data.count()

	def __bool__(self):
		return bool(self.data.count())

	def inst_split(self):
		if verbose: print(len(self.data),'inst_split')
		nldata = self.data.nl
		out_nl = {}
		w_used = np.where(nldata['used'] == 1)
		for num, inst in enumerate(self.data.v_assoc_inst):
			w_inst = np.where(nldata['assoc_inst'] == num)
			splitnl = cvpj_notelist(self.time_ppq, self.time_float)
			splitnld = splitnl.data
			splitnld.nl = nldata[np.intersect1d(w_used, w_inst)]
			if len(splitnld.nl):
				splitnld.nl['assoc_inst'] = 0
				splitnld.v_assoc_inst = [inst]
				splitnld.v_assoc_extra = self.data.v_assoc_extra.copy()
				splitnld.v_assoc_auto = self.data.v_assoc_auto.copy()
				splitnld.v_assoc_slide = copy.deepcopy(self.data.v_assoc_slide)
				splitnld.v_assoc_multikey = self.data.v_assoc_multikey.copy()
				splitnld.num_notes = len(splitnld.nl)
				out_nl[inst] = splitnl
		return out_nl

	def inst_all(self, instid):
		if verbose: print(len(self.data),'inst_all', instid)
		self.data.inst_all(instid)

	def stretch(self, time_ppq, time_float):
		if verbose: print(len(self.data),'stretch', time_ppq, time_float)
		for note in self.data:
			note['pos'] = xtramath.change_timing(self.time_ppq, time_ppq, time_float, note['pos'])
			note['dur'] = xtramath.change_timing(self.time_ppq, time_ppq, time_float, note['dur'])

		for slides in self.data.v_assoc_slide:
			for sn in slides:
				sn[0] = xtramath.change_timing(self.time_ppq, time_ppq, time_float, sn[0])
				sn[1] = xtramath.change_timing(self.time_ppq, time_ppq, time_float, sn[1])

		for autos in self.data.v_assoc_auto:
			for t in autos: autos[t].change_timings(time_ppq, time_float)

	def change_timings(self, time_ppq, time_float):
		if verbose: print(len(self.data),'change_timings', time_ppq, time_float)
		self.stretch(time_ppq, time_float)

		self.time_ppq = time_ppq
		self.time_float = time_float

	def add_r(self, t_pos, t_dur, t_key, t_vol, t_extra):
		self.cursor.add_r(t_pos, t_dur, t_key, t_vol, t_extra)

	def add_r_multi(self, t_pos, t_dur, m_keys, t_vol, t_extra):
		self.cursor.add_r_multi(t_pos, t_dur, m_keys, t_vol, t_extra)

	def add_m(self, t_inst, t_pos, t_dur, t_key, t_vol, t_extra):
		self.cursor.add_m(t_inst, t_pos, t_dur, t_key, t_vol, t_extra)

	def add_m_multi(self, t_inst, t_pos, t_dur, m_keys, t_vol, t_extra):
		self.cursor.add_m_multi(t_inst, t_pos, t_dur, m_keys, t_vol, t_extra)

	def last_add_auto(self, a_type):
		if self.__len__():
			autodata = self.cursor.assoc_auto_set()
			if a_type not in autodata: 
				autodata[a_type] = autopoints.cvpj_autopoints(self.time_ppq, self.time_float, 'float')
			return autodata[a_type].add_point()
		else:
			dummyp = autopoints.cvpj_autopoints(self.time_ppq, self.time_float, 'float')
			return dummyp.add_point()

	def last_add_slide(self, t_pos, t_dur, t_key, t_vol, t_extra):
		slidedata = self.cursor.assoc_slide_append([t_pos, t_dur, t_key, t_vol, t_extra])

	def last_add_vol(self, i_val):
		note = self.cursor.getcur()
		note['vol'] = i_val

	def last_add_extra(self, i_name, i_val):
		note = self.cursor.assoc_extra_set(i_name, i_val)

	def last_extend_pos(self, endpos):
		if self.count():
			note = self.cursor.getcur()
			note['dur'] = endpos-note['pos']

	def last_extend(self, dur):
		if self.count():
			note = self.cursor.getcur()
			note['dur'] += dur

	def auto_add_slide(self, t_inst, t_pos, t_dur, t_key, t_vol, t_extra):
		for note in self.cursor:
			n_inst = note['assoc_inst'] if note['is_inst'] else None
			s_inst = self.data.v_assoc_inst.index(t_inst) if t_inst in self.data.v_assoc_inst else None

			match_pos = (note['pos'] <= t_pos < note['pos']+note['dur'])
			match_inst = n_inst == s_inst
			
			if note['used'] and match_pos and match_inst:
				sn_pos = t_pos - note['pos']
				sn_key = t_key
				slidedata = self.cursor.assoc_slide_append([sn_pos, t_dur, sn_key, t_vol, t_extra])

	def notesfound(self):
		return self.count() != 0

	def get_dur(self):
		tab = self.data.nl['pos']+self.data.nl['dur']
		return max(tab) if tab.any() else 0

	def get_start(self):
		tab = self.data.nl['pos']
		return min(tab) if tab.any() else 0

	def get_start_end(self):
		ma = self.data.nl['pos']+self.data.nl['dur']
		return min(ma) if ma.any() else 0, max(ma) if ma.any() else 0

	def edit_move(self, pos):
		if verbose: print(len(self.data),'edit_move', pos)
		self.data.nl['pos'] += pos
		used = [n for n, x in enumerate(self.data.nl['pos']) if x>=0]
		self.data.nl = self.data.nl[used]
		self.data.go_last = True
		self.data.after_proc()

	def edit_move_minus(self, pos):
		if verbose: print(len(self.data),'edit_move_minus', pos)
		self.data.nl['pos'] += pos

	def edit_trim(self, pos):
		if verbose: print(len(self.data),'edit_trim', pos)
		self.data.nl['pos'] += pos
		used = [n for n, x in enumerate(self.data.nl['pos']) if x>=pos]
		self.data.nl = self.data.nl[used]
		self.data.after_proc()

	def edit_trim_limit(self, pos):
		if verbose: print(len(self.data),'edit_trim_limit', pos)
		self.data.nl['pos'] += pos
		used = [n for n, x in enumerate(self.data.nl['pos']) if x>=pos]
		self.data.nl = self.data.nl[used]
		self.data.after_proc()

	def edit_trimmove(self, startat, endat):
		if verbose: print(len(self.data),'edit_trimmove', startat, endat)
		used = [n for n, x in enumerate(self.data.nl['pos']) if endat>x>=startat]
		self.data.nl['pos'] += -startat
		self.data.nl = self.data.nl[used]
		self.data.go_last = True
		self.data.after_proc()

	def new_nl_start_end(self, startat, endat):
		if verbose_copy: print(len(self.data),'new_nl_start_end', startat, endat)
		used = [n for n, x in enumerate(self.data.nl['pos']) if endat>x>=startat]

		new_nl = cvpj_notelist(self.time_ppq, self.time_float)
		new_data = new_nl.data
		new_data.v_assoc_inst = copy.deepcopy(self.data.v_assoc_inst)
		new_data.v_assoc_extra = copy.deepcopy(self.data.v_assoc_extra)
		new_data.v_assoc_auto = copy.deepcopy(self.data.v_assoc_auto)
		new_data.v_assoc_slide = copy.deepcopy(self.data.v_assoc_slide)
		new_data.v_assoc_multikey = copy.deepcopy(self.data.v_assoc_multikey)
		new_data.nl = self.data.nl[used].copy()
		new_data.nl['pos'] += -startat
		new_data.after_proc()

		return new_nl

	def mod_scale(self, i_size):
		self.data.nl['pos'] *= i_size
		self.data.nl['dur'] *= i_size

	def mod_transpose(self, i_key):
		self.data.nl['key'] += i_key
		self.data.v_assoc_multikey = [[x+i_key for x in n] for n in self.data.v_assoc_multikey]

	def mod_weird(self, i_key):
		self.data.nl['key'] *= i_key
		self.data.v_assoc_multikey = [[x*i_key for x in n] for n in self.data.v_assoc_multikey]

	def mod_limit(self, imin, imax):
		if verbose: print(len(self.data),'mod_limit', imin, imax)
		self.clean()
		keyval = self.data.nl['key']
		findex = np.where(np.logical_and(imin<=keyval, keyval<=imax))
		self.data.nl['used'] = 0
		self.data.nl['used'][findex] = 1
		self.data.after_proc()

	def mod_filter_inst(self, instname):
		if verbose: print(len(self.data),'mod_filter_inst', instname)
		self.clean()
		self.data.nl['used'] = 0
		if instname in self.data.v_assoc_inst:
			aid = self.data.v_assoc_inst.index(instname)
			self.data.nl['used'][np.where(aid==self.data.nl['assoc_inst'])] = 1
		self.data.after_proc()

	def remove_overlap(self):
		if verbose: print(len(self.data),'remove_overlap')
		self.sort()
		self.clean()
		endnotes = np.zeros(129, dtype=np.dtype([('pos', np.int32), ('endpos', np.float64)]))
		endnotes[:] = -1

		for i, n in enumerate(self.data):
			keynum = n['key']+60

			if n['dur']:
				endpos = n['pos']+n['dur']
				if endnotes[keynum][0] != -1:
					previ, preve = endnotes[keynum]
					subv = -min(n['pos']-preve, 0)
					self.data.nl[previ]['dur'] -= subv
					if self.data.nl[previ]['dur'] == 0: self.data.nl[previ]['used'] = 0

				endnotes[keynum]['pos'] = i
				endnotes[keynum]['endpos'] = endpos
		self.data.after_proc()

	def sort(self):
		self.data.sort()

	def clear(self):
		nld = self.data
		nld.init_nl()
		nld.v_assoc_inst = []
		nld.v_assoc_extra = []
		nld.v_assoc_auto = []
		nld.v_assoc_slide = []
		nld.v_assoc_multikey = []

	def clear_size(self, i_size):
		nld = self.data
		nld.init_nl()
		nld.v_assoc_inst = []
		nld.v_assoc_extra = []
		nld.v_assoc_auto = []
		nld.v_assoc_slide = []
		nld.v_assoc_multikey = []
		nld.alloc(i_size)

	def clean(self):
		return self.data.clean()

	def last_arpeggio(self, notes):
		if verbose: print(len(self.data),'last_arpeggio')
		note = self.cursor.getcur()
		counts = np.unique(notes, return_counts=True)
		isduped = True in (counts[1]>2)
		if not isduped: 
			self.cursor.assoc_multikey_add([note['key']+x for x in notes])

	def add_instpos(self, instlocs):
		if verbose: print(len(self.data),'add_instpos')

		if len(self.data):

			if len(instlocs)==1:
				self.inst_all(instlocs[0][1])
	
			if len(instlocs)>1:
				inst_data = np.zeros(len(instlocs), dtype=np.dtype([('start', np.float64), ('end', np.float64), ('inst', np.int16), ('name', np.str_, 256)]))
	
				maxval = np.max(self.data.nl['pos']+self.data.nl['dur'])
	
				inst_data['start'] = [x[0] for x in instlocs]
				inst_data['end'] = [x[0] for x in instlocs[1:]]+[maxval]
				inst_data['inst'] = [self.data.add_inst(x[1]) for x in instlocs]
				inst_data['name'] = [x[1] for x in instlocs]
	
				uniqueinsts = np.unique(inst_data)
	
				poses = self.data.nl['pos']
				usedd = self.data.nl['used']
				for n in inst_data:
					findex = np.where(np.logical_and(n['start']<=poses, poses<n['end'], usedd==1))
					self.data.nl['is_inst'][findex] = 1
					self.data.nl['assoc_inst'][findex] = n['inst']
	
				self.data.v_assoc_inst = uniqueinsts['name']

	def get_used_inst(self):
		return self.data.v_assoc_inst

	def count(self):
		return self.data.count()

	def iter(self):
		cursor_obj = self.create_cursor()

		for note in cursor_obj:
			if note['used']:
				t_pos = note['pos']
				t_dur = note['dur']
				t_keys = cursor_obj.assoc_multikey_get()
				t_vol = note['vol']
				t_inst = cursor_obj.assoc_inst_get()
				t_extra = cursor_obj.assoc_extra_get()
				t_auto = cursor_obj.assoc_auto_get()
				t_slide = cursor_obj.assoc_slide_get()
				yield t_pos, t_dur, t_keys, t_vol, t_inst, t_extra, t_auto, t_slide

	def notemod_conv(self):
		cursor_obj = self.create_cursor()
		for note in cursor_obj:
			if note['used']:
				cursor_obj.notemod_conv(self.time_ppq, self.time_float)

	def extra_to_noteenv(self):
		cursor_obj = self.create_cursor()
		for note in cursor_obj:
			if note['used']:
				cursor_obj.extra_to_noteenv(self.time_ppq, self.time_float)

	def merge(self, i_nl, offset):
		if verbose: print(len(self.data),'merge')
		self.data.merge(i_nl.data, offset)

	def usedrange(self, start, end):
		if verbose: print(len(self.data),'usedrange')
		poses = self.data.nl['pos']
		usedd = self.data.nl['used']
		return len(self.data.nl[np.where(np.logical_and(start<=poses, poses<end, usedd==1))]) != 0

	def usedoverflow(self, start, end):
		if verbose: print(len(self.data),'usedoverflow')
		poses = self.data.nl['pos']
		usedd = self.data.nl['used']
		usedposes = np.logical_and(start<=poses, poses<end)
		usedvals = np.where(np.logical_and(usedposes, usedd==1))
		filternl = self.data.nl[usedvals]
		if len(filternl): return True, max(np.max(filternl['pos']+filternl['dur'])-end, 0) 
		else: return False, 0

	def appendtxt_inst(self, start, end):
		self.data.appendtxt_inst(start, end)

	def midi_from(self, input_file):
		from objects.songinput import midi_in
		from objects_midi.parser import MidiFile
		from objects.songinput._midi_multi import notes
		from objects_midi import events as MidiEvents
		

		if os.path.exists(input_file):
			midifile = MidiFile.fromFile(input_file)
			self.time_ppq = midifile.ppqn
			self.time_float = False
			if midifile.tracks:
				events = midifile.tracks[0].events
				numevents = len(events)
				notes_obj = notes.midi_notes_multi(numevents)

				curpos = 0
				for msg in midifile.tracks[0].events:
					curpos += msg.deltaTime
					if type(msg) == MidiEvents.NoteOnEvent:
						if msg.velocity != 0: notes_obj.note_on(curpos, msg.channel, msg.note, msg.velocity)
						else: notes_obj.note_off(curpos, msg.channel, msg.note)
					elif type(msg) == MidiEvents.NoteOffEvent:
						notes_obj.note_off(curpos, msg.channel, msg.note)

				self.clear_size(numevents)

				for n in notes_obj.data.data:
					if n['complete']:
						self.add_r(int(n['start']), int(n['end']-n['start']), int(n['key'])-60, float(n['vol'])/127, None)


	#def multikey_comb(self):
	#	prev_note = None
	#	for n, x in enumerate(self.data):
	#		if x['used'] == 1 and x['is_extra'] == x['is_auto'] == x['is_slide'] == x['is_multikey'] == 0:
	#			iffound_1 = np.logical_and(
	#				self.data.nl['vol']==x['vol'],
	#				self.data.nl['pos']==x['pos'],
	#			)
	#			iffound_2 = np.logical_and(
	#				self.data.nl['dur']==x['dur'],
	#				self.data.nl['is_inst']==x['is_inst'],
	#			)
	#			iffound_3 = np.logical_and(
	#				self.data.nl['assoc_inst']==x['assoc_inst'],
	#				self.data.nl['is_extra']==0,
	#			)
	#			iffound_4 = np.logical_and(
	#				self.data.nl['is_auto']==0,
	#				self.data.nl['is_slide']==0,
	#				self.data.nl['is_multikey']==0,
	#			)
	#			iffound_5 = np.logical_and(iffound_1,iffound_2)
	#			iffound_6 = np.logical_and(iffound_3,iffound_4)
#
	#			iffound = np.logical_and(iffound_5,iffound_6,self.data.nl['used']==1)
#
	#			foundvals = np.where(iffound)[0]
	#			if len(foundvals) > 1:
	#				multikeys = list(self.data.nl['key'][foundvals])
	#				self.data.nl['is_multikey'][foundvals[0]] = 1
	#				self.data.nl['assoc_multikey'][foundvals[0]] = len(self.data.v_assoc_multikey)
	#				self.data.v_assoc_multikey.append(multikeys)
#
	#				for kn in foundvals[1:]: self.data.nl['used'][kn] = 0
#
	#	self.clean()
#
	#def get_hash(self):
	#	m = hashlib.md5()
	#	notebytes = self.data.tobytes()
	#	m.update(notebytes)
	#	return m.hexdigest() if len(notebytes) else None
#
	#def get_hash_range(self, startat, endat):
	#	new_nl = self.new_nl_start_end(startat, endat)
	#	return new_nl.get_hash()
#
	#def get_hash_split(self, splitdur, endat):
	#	return [self.get_hash_range(x, x+splitdur) for x in range(0, endat, splitdur)]