# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.convproj import autopoints
from functions import xtramath

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
			notelist_obj.last_add_auto('pitch', spoint[0], spoint[1])

class notelist_note_auto:
	def __init__(self, time_ppq):
		self.time_ppq = time_ppq

		self.u_notemod = False
		self.mod_pitch = 0
		self.mod_pan = 0

		self.u_slide = False
		self.slide = []

		self.u_auto = False
		self.auto = {}

	def change_timings(self, time_ppq):
		for sn in self.slide:
			sn[0] = xtramath.change_timing(self.time_ppq, time_ppq, sn[0])
			sn[1] = xtramath.change_timing(self.time_ppq, time_ppq, sn[1])

		for t in self.auto: 
			self.auto[t].change_timings(time_ppq)

		self.time_ppq = time_ppq

# ------------------------------------------ Points ------------------------------------------

	def auto__remove(self):
		self.u_auto = False
		self.auto = {}

	def auto__add_point(self, mpetype, pos, val):
		autodata = self.auto
		if mpetype not in autodata: autodata[mpetype] = autopoints.cvpj_autopoints(self.time_ppq, 'float')
		autodata[mpetype].points__add_normal(pos, val, 0, None)
		self.u_auto = True

	def auto__add_point_instant(self, mpetype, pos, val):
		autodata = self.auto
		if mpetype not in autodata: autodata[mpetype] = autopoints.cvpj_autopoints(self.time_ppq, 'float')
		autodata[mpetype].points__add_instant(pos, val)
		self.u_auto = True

# ------------------------------------------ Slide ------------------------------------------

	def slide__remove(self):
		self.u_slide = False
		self.slide = []

	def slide__add_point(self, t_pos, t_dur, t_key, t_vol, t_extra):
		self.slide.append([t_pos, t_dur, t_key, t_vol, t_extra])
		self.u_slide = True

# ------------------------------------------ NoteMod ------------------------------------------

	def notemod__add_finepitch(self, mod_pitch):
		self.u_notemod = True
		self.mod_pitch = mod_pitch

	def notemod__add_pan(self, mod_pan):
		self.u_notemod = True
		self.mod_pan = mod_pan

# ------------------------------------------ Conversion ------------------------------------------

	def convert_to(self, outtype, multikeys, vol):
		if outtype == 'auto':
			self.auto__from_slide(False, multikeys[0])
			self.auto__from_notemod(False)
		if outtype == 'slide':
			self.slide__from_auto(False, multikeys, vol)

	def auto__from_notemod(self, overwrite):
		if self.u_notemod:
			if 'pitch' not in self.auto:
				self.auto['pitch'] = autopoints.cvpj_autopoints(self.time_ppq, 'float')
				self.auto['pitch'].points__add_normal(0, self.mod_pitch/100, 0, None)
			if 'pan' not in self.auto:
				self.auto['pan'] = autopoints.cvpj_autopoints(self.time_ppq, 'float')
				self.auto['pan'].points__add_normal(0, self.mod_pan, 0, None)
			self.u_auto = True
			return True
		return False

	def auto__from_slide(self, overwrite, key):
		if self.u_slide and not self.u_auto:
			pointsdata = pitchmod(key)
			for slidenote in self.slide: pointsdata.slide_note(slidenote[0], slidenote[2], slidenote[1])
			nmp = pointsdata.to_pointdata()
			self.auto['pitch'] = autopoints.cvpj_autopoints(self.time_ppq, 'float')
			for nmps in nmp:
				self.auto['pitch'].points__add_normal(nmps[0], nmps[1], 0, None)
			self.u_auto = True
			return True
		return False

	def slide__from_auto(self, overwrite, multikey, vol):
		if self.u_auto and not self.slide:
			if 'pitch' in self.auto:
				pitchauto = self.auto['pitch'].copy()
				pitchauto.remove_instant()
				pitchregions = pitchauto.to_regions()
				maxnote = max(multikey)
				for n, r in enumerate(pitchregions):
					pos_start = float(r['pos_start'])
					dur = float(r['dur'])
					diff = float(r['diff'])

					if n == 0:
						self.slide.append([
							pos_start,
							dur, 
							int(r['value_end'])+maxnote, 
							vol, 
							{}
						])

					else:
						if diff:
							self.slide.append([
								pos_start,
								dur, 
								int(r['value_end'])+maxnote, 
								vol, 
								{}
							])
				self.u_slide = True
			return True
		return False