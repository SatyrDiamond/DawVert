# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects import globalstore
from objects.convproj import sample_entry
from objects.convproj import fileref
from objects.convproj import params
from objects.convproj import tracks
from objects.convproj import visual
from objects.convproj import sends
from objects.convproj import notelist
from objects.convproj import stretch
from objects.convproj import placements
from objects.convproj import placements_notes
from objects.convproj import placements_audio
from objects.convproj import placements_index
from objects.convproj import midi_inst
from objects.convproj import autoticks
from objects.convproj import timemarker

import copy

class lanefit:
	def __init__(self):
		self.mergeddata_notes = []
		self.mergeddata_audio = []

	def add_pl(self, pl_data, is_audio):
		nummlane = 1
		isplaced = False
		while not isplaced:
			if len(self.mergeddata_notes) < nummlane: 
				self.mergeddata_notes.append(placements_notes.cvpj_placements_notes())
				self.mergeddata_audio.append(placements_audio.cvpj_placements_audio())

			if not is_audio:
				overlapped = self.mergeddata_notes[-1].check_overlap(pl_data.time.position, pl_data.time.duration)
				if not overlapped: 
					self.mergeddata_notes[-1].append(pl_data)
					isplaced = True
				else: nummlane += 1
			else:
				overlapped = self.mergeddata_audio[-1].check_overlap(pl_data.time.position, pl_data.time.duration)
				if not overlapped: 
					self.mergeddata_audio[-1].append(pl_data)
					isplaced = True
				else: nummlane += 1


class cvpj_nle:
	__slots__ = ['visual','notelist','timesig_auto','timemarkers']
	def __init__(self, time_ppq, time_float):
		self.visual = visual.cvpj_visual()
		self.notelist = notelist.cvpj_notelist(time_ppq, time_float)
		self.timesig_auto = autoticks.cvpj_autoticks(time_ppq, time_float, 'timesig')
		self.timemarkers = timemarker.cvpj_timemarkers(time_ppq, time_float)

cvpj_visual = visual.cvpj_visual
cvpj_stretch = stretch.cvpj_stretch

class cvpj_midiport:
	def __init__(self):
		self.in_enabled = False
		self.in_chan = -1
		self.in_fixedvelocity = -1

		self.out_enabled = False
		self.out_fixedvelocity = -1
		self.out_chan = -1
		self.out_inst = midi_inst.cvpj_midi_inst()

		self.basevelocity = 63

class cvpj_instrument:
	__slots__ = ['visual','params','datavals','midi','fxrack_channel','fxslots_notes','fxslots_audio','pluginid','is_drum']
	def __init__(self):
		self.visual = visual.cvpj_visual()
		self.params = params.cvpj_paramset()
		self.datavals = params.cvpj_datavals()
		self.midi = cvpj_midiport()
		self.is_drum = False
		self.fxrack_channel = -1
		self.fxslots_notes = []
		self.fxslots_audio = []
		self.pluginid = ''

	def from_dataset(self, ds_id, ds_cat, ds_obj, ow_vis):
		self.visual.from_dset(ds_id, ds_cat, ds_obj, ow_vis)
		dso_obj = globalstore.dataset.get_obj(ds_id, ds_cat, ds_obj)
		dso_midi = dso_obj.midi if dso_obj else None

		midifound = False
		if dso_midi:
			if dso_midi.used != False:
				midifound = True
				midi_obj = self.midi.out_inst
				midi_obj.bank = dso_midi.bank
				midi_obj.patch = dso_midi.patch
				midi_obj.drum = dso_midi.is_drum
				self.is_drum = dso_midi.is_drum

		return midifound

	def to_midi_noplug(self):
		midi_obj = self.midi.out_inst
		m_bank_hi = midi_obj.bank_hi
		m_bank = midi_obj.bank
		m_inst = midi_obj.patch
		m_drum = midi_obj.drum
		m_dev = midi_obj.device
		self.params.add('usemasterpitch', not m_drum, 'bool')
		self.visual.from_dset_midi(m_bank_hi, m_bank, m_inst, m_drum, m_dev, False)

	def to_midi(self, convproj_obj, plug_id, use_visual):
		midi_obj = self.midi.out_inst
		m_bank_hi = midi_obj.bank_hi
		m_bank = midi_obj.bank
		m_inst = midi_obj.patch
		m_drum = midi_obj.drum
		m_dev = midi_obj.device
		plugin_obj = convproj_obj.plugin__addspec__midi(plug_id, m_bank_hi, m_bank, m_inst, m_drum, m_dev)
		plugin_obj.role = 'synth'
		self.pluginid = plug_id
		self.params.add('usemasterpitch', not m_drum, 'bool')
		if use_visual: self.visual.from_dset_midi(m_bank_hi, m_bank, m_inst, m_drum, m_dev, False)
		return plugin_obj


class cvpj_return_track:
	__slots__ = ['visual','visual_ui','params','datavals','fxslots_notes','fxslots_audio','fxslots_mixer','sends']
	def __init__(self):
		self.visual = visual.cvpj_visual()
		self.visual_ui = visual.cvpj_visual_ui()
		self.params = params.cvpj_paramset()
		self.datavals = params.cvpj_datavals()
		self.fxslots_notes = []
		self.fxslots_audio = []
		self.fxslots_mixer = []
		self.sends = sends.cvpj_sends()

	def plugin_autoplace(self, plugin_obj, pluginid):
		if plugin_obj.role == 'fx': self.fxslots_audio.append(pluginid)
		elif plugin_obj.role == 'notefx': self.fxslots_notes.append(pluginid)

class cvpj_lane:
	def __init__(self, track_type, time_ppq, time_float, uses_placements, is_indexed):
		self.visual = visual.cvpj_visual()
		self.visual_ui = visual.cvpj_visual_ui()
		self.params = params.cvpj_paramset()
		self.datavals = params.cvpj_datavals()
		self.placements = placements.cvpj_placements(time_ppq, time_float, uses_placements, is_indexed)

class cvpj_armstate:
	def __init__(self):
		self.on = False
		self.in_keys = False
		self.in_audio = False

class cvpj_track:
	__slots__ = ['time_ppq','time_float','uses_placements','lanes','is_indexed','type','is_laned','inst_pluginid','datavals','visual','visual_ui','params','midi','fxrack_channel','fxslots_notes','fxslots_audio','fxslots_mixer','placements','sends','group','returns','notelist_index','scenes','audio_channels','is_drum','timemarkers','armed']
	def __init__(self, track_type, time_ppq, time_float, uses_placements, is_indexed):
		self.time_ppq = time_ppq
		self.time_float = time_float
		self.uses_placements = uses_placements
		self.is_indexed = is_indexed
		self.type = track_type
		self.is_laned = False
		self.lanes = {}
		self.inst_pluginid = ''
		self.visual = visual.cvpj_visual()
		self.visual_ui = visual.cvpj_visual_ui()
		self.params = params.cvpj_paramset()
		self.datavals = params.cvpj_datavals()
		self.midi = cvpj_midiport()
		self.fxrack_channel = -1
		self.fxslots_notes = []
		self.fxslots_audio = []
		self.fxslots_mixer = []
		self.sends = sends.cvpj_sends()
		self.placements = placements.cvpj_placements(self.time_ppq, self.time_float, self.uses_placements, self.is_indexed)
		self.group = None
		self.returns = {}
		self.notelist_index = {}
		self.scenes = {}
		self.audio_channels = 2
		self.is_drum = False
		self.timemarkers = timemarker.cvpj_timemarkers(time_ppq, time_float)
		self.armed = cvpj_armstate()

	def from_dataset(self, ds_id, ds_cat, ds_obj, ow_vis):
		self.visual.from_dset(ds_id, ds_cat, ds_obj, ow_vis)
		dso_obj = globalstore.dataset.get_obj(ds_id, ds_cat, ds_obj)
		dso_midi = dso_obj.midi if dso_obj else None

		midifound = False
		if dso_midi:
			if dso_midi.used != False:
				midifound = True
				midi_obj = self.midi.out_inst
				midi_obj.bank = dso_midi.bank
				midi_obj.patch = dso_midi.patch
				midi_obj.drum = dso_midi.is_drum

		return midifound

	def to_midi(self, convproj_obj, plug_id, use_visual):
		midi_obj = self.midi.out_inst
		m_bank_hi = midi_obj.bank_hi
		m_bank = midi_obj.bank
		m_inst = midi_obj.patch
		m_drum = midi_obj.drum
		m_dev = midi_obj.device
		plugin_obj = convproj_obj.plugin__addspec__midi(plug_id, m_bank_hi, m_bank, m_inst, m_drum, m_dev)
		plugin_obj.role = 'synth'
		self.inst_pluginid = plug_id
		self.params.add('usemasterpitch', not m_drum, 'bool')
		if use_visual: self.visual.from_dset_midi(m_bank_hi, m_bank, m_inst, m_drum, m_dev, False)
		return plugin_obj

	def used_insts(self):
		used_insts = self.placements.used_insts()
		for _, lane in self.lanes.items(): used_insts += lane.placements.used_insts()
		return list(set(used_insts))

	def scene__add(self, i_id, i_lane):
		if i_id not in self.scenes: self.scenes[i_id] = {}
		if i_lane not in self.scenes[i_id]: self.scenes[i_id][i_lane] = placements.cvpj_placements(self.time_ppq, self.time_float, self.uses_placements, self.is_indexed)
		return self.scenes[i_id][i_lane]

	def get_midi(self, convproj_obj):
		plugin_found, plugin_obj = convproj_obj.plugin__get(self.inst_pluginid)
		return plugin_found, plugin_obj.midi if plugin_found else midi_inst.cvpj_midi_inst()

	def fx__return__add(self, returnid):
		self.returns[returnid] = cvpj_track('return', self.time_ppq, self.time_float, False, False)
		return self.returns[returnid]

	def make_base(self):
		c_obj = cvpj_track(self.type,self.time_ppq,self.time_float,self.uses_placements,self.is_indexed)
		c_obj.time_ppq = self.time_ppq
		c_obj.time_float = self.time_float
		c_obj.uses_placements = self.uses_placements
		c_obj.is_indexed = self.is_indexed
		c_obj.type = self.type
		c_obj.is_laned = False
		c_obj.lanes = {}
		c_obj.inst_pluginid = self.inst_pluginid
		c_obj.visual = copy.deepcopy(self.visual)
		c_obj.visual_ui = copy.deepcopy(self.visual_ui)
		c_obj.params = copy.deepcopy(self.params)
		c_obj.datavals = copy.deepcopy(self.datavals)
		c_obj.midi = copy.deepcopy(self.midi)
		c_obj.fxrack_channel = self.fxrack_channel
		c_obj.fxslots_notes = self.fxslots_notes
		c_obj.fxslots_audio = self.fxslots_audio
		c_obj.fxslots_mixer = self.fxslots_mixer
		c_obj.sends = copy.deepcopy(self.sends)
		c_obj.placements = placements.cvpj_placements(self.time_ppq, self.time_float, self.uses_placements, self.is_indexed)
		c_obj.group = self.group
		c_obj.returns = self.returns
		c_obj.notelist_index = self.notelist_index
		c_obj.armed = copy.deepcopy(self.armed)
		return c_obj

	def make_base_inst(self, inst_obj):
		track_obj = self.make_base()
		track_obj.inst_pluginid = inst_obj.pluginid
		#track_obj.visual = copy.deepcopy(inst_obj.visual)
		track_obj.params = copy.deepcopy(inst_obj.params)
		track_obj.datavals = copy.deepcopy(inst_obj.datavals)
		track_obj.midi = copy.deepcopy(inst_obj.midi)
		track_obj.fxrack_channel = inst_obj.fxrack_channel
		track_obj.fxslots_notes = inst_obj.fxslots_notes
		track_obj.fxslots_audio = inst_obj.fxslots_audio
		return track_obj

	def notelistindex__add(self, i_id):
		self.notelist_index[i_id] = cvpj_nle(self.time_ppq, self.time_float)
		return self.notelist_index[i_id]

	def add_lane(self, laneid):
		self.is_laned = True
		if laneid not in self.lanes: 
			self.lanes[laneid] = cvpj_lane(self.type, self.time_ppq, self.time_float, self.uses_placements, self.is_indexed)
		return self.lanes[laneid]

	def lanefit(self):
		old_lanes = self.lanes

		lanefit_obj = lanefit()

		colors = []

		for l_name, l_data in old_lanes.items():
			if l_data.visual.color: colors.append(l_data.visual.color)
			for npl in l_data.placements.pl_notes: lanefit_obj.add_pl(npl, False)
			for apl in l_data.placements.pl_audio: lanefit_obj.add_pl(apl, True)

		allcolor = colors[0] if (all(x == colors[0] for x in colors) and colors) else None

		if len(old_lanes) >= len(lanefit_obj.mergeddata_notes):
			self.lanes = {}
			for lanenum in range(len(lanefit_obj.mergeddata_notes)):
				laneid = 'lanefit_'+str(lanenum)
				lane_obj = cvpj_lane(self.type, self.time_ppq, self.time_float, self.uses_placements, self.is_indexed)
				lane_obj.placements.pl_notes = lanefit_obj.mergeddata_notes[lanenum]
				lane_obj.placements.pl_audio = lanefit_obj.mergeddata_audio[lanenum]
				if allcolor: lane_obj.visual.color = copy.deepcopy(allcolor)
				self.lanes[laneid] = lane_obj

	def change_timings(self, time_ppq, time_float):
		self.placements.change_timings(time_ppq, time_float)
		for laneid, lane_obj in self.lanes.items():
			lane_obj.placements.change_timings(time_ppq, time_float)
		self.time_float = time_float
		self.time_ppq = time_ppq
		self.timemarkers.change_timings(time_ppq, time_float)

	def fx__return__add(self, returnid):
		return_obj = cvpj_return_track()
		self.returns[returnid] = return_obj
		return return_obj

	def iter_return(self):
		for returnid, return_obj in self.returns.items():
			yield returnid, return_obj

	def timemarker__add(self):
		return self.timemarkers.add()

	def plugin_autoplace(self, plugin_obj, pluginid):
		if plugin_obj.role == 'fx': self.fxslots_audio.append(pluginid)
		elif plugin_obj.role == 'notefx': self.fxslots_notes.append(pluginid)
		elif plugin_obj.role == 'synth': self.inst_pluginid = pluginid
