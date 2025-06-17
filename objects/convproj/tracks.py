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
				self.mergeddata_notes.append(placements_notes.cvpj_placements_notes(pl_data.time_ppq))
				self.mergeddata_audio.append(placements_audio.cvpj_placements_audio(pl_data.time_ppq))

			if not is_audio:
				overlapped = self.mergeddata_notes[-1].check_overlap_timeobj(pl_data.time)
				if not overlapped: 
					self.mergeddata_notes[-1].append(pl_data)
					isplaced = True
				else: nummlane += 1
			else:
				overlapped = self.mergeddata_audio[-1].check_overlap_timeobj(pl_data.time)
				if not overlapped: 
					self.mergeddata_audio[-1].append(pl_data)
					isplaced = True
				else: nummlane += 1


class cvpj_nle:
	__slots__ = ['visual','notelist','timesig_auto','timemarkers']
	def __init__(self, time_ppq):
		self.visual = visual.cvpj_visual()
		self.notelist = notelist.cvpj_notelist(time_ppq)
		self.timesig_auto = autoticks.cvpj_autoticks(time_ppq, 'timesig')
		self.timemarkers = timemarker.cvpj_timemarkers(time_ppq)

	def json__make(self):
		outjson = {}
		outjson['visual'] = self.visual.json__make()
		outjson['notelist'] = self.notelist.json__make()
		outjson['timesig_auto'] = self.timesig_auto.json__make()
		outjson['timemarkers'] = self.timemarkers.json__make()
		return outjson

	@classmethod
	def json__parse(cls, injson):
		cls = cls()
		if 'visual' in injson: 
			cls.visual = visual.cvpj_visual.json__parse(injson['visual'])
		if 'notelist' in injson: 
			cls.notelist = notelist.cvpj_notelist.json__parse(injson['notelist'])
		if 'timesig_auto' in injson: 
			cls.timesig_auto = autoticks.cvpj_autoticks.json__parse(injson['timesig_auto'])
		if 'timemarkers' in injson: 
			cls.timemarkers = timemarker.cvpj_timemarkers.json__parse(injson['timemarkers'])
		return cls

cvpj_visual = visual.cvpj_visual
cvpj_stretch = stretch.cvpj_stretch

class cvpj_chanport:
	def __init__(self):
		self.chan = False
		self.port = -1
		self.port_name = ''

	def json__make(self):
		outjson = {}
		outjson['chan'] = self.chan
		outjson['port'] = self.port
		outjson['port_name'] = self.port_name
		return outjson

	@classmethod
	def json__parse(cls, injson):
		cls = cls()
		if 'chan' in injson: cls.chan = injson['chan']
		if 'port' in injson: cls.port = injson['port']
		if 'port_name' in injson: cls.port_name = injson['port_name']
		return cls

class cvpj_midiport:
	def __init__(self):
		self.in_enabled = False
		self.in_chanport = cvpj_chanport()
		self.in_fixedvelocity = -1

		self.out_enabled = False
		self.out_chanport = cvpj_chanport()
		self.out_fixedvelocity = -1
		self.out_inst = midi_inst.cvpj_midi_inst()

		self.basevelocity = 63

	def json__make(self):
		outjson = {}
		outjson['basevelocity'] = self.basevelocity
		outjson['in_chanport'] = self.in_chanport.json__make()
		outjson['in_enabled'] = self.in_enabled
		outjson['in_fixedvelocity'] = self.in_fixedvelocity
		outjson['out_chanport'] = self.out_chanport.json__make()
		outjson['out_enabled'] = self.out_enabled
		outjson['out_fixedvelocity'] = self.out_fixedvelocity
		outjson['out_inst'] = self.out_inst.json__make()
		return outjson

	@classmethod
	def json__parse(cls, injson):
		cls = cls()
		if 'in_enabled' in injson: cls.in_enabled = injson['in_enabled']
		if 'out_enabled' in injson: cls.out_enabled = injson['out_enabled']
		if 'in_fixedvelocity' in injson: cls.in_fixedvelocity = injson['in_fixedvelocity']
		if 'out_fixedvelocity' in injson: cls.out_fixedvelocity = injson['out_fixedvelocity']
		if 'basevelocity' in injson: cls.basevelocity = injson['basevelocity']
		if 'in_chanport' in injson: cls.in_chanport = cvpj_chanport.json__parse(injson['in_chanport'])
		if 'out_chanport' in injson: cls.out_chanport = cvpj_chanport.json__parse(injson['out_chanport'])
		if 'out_inst' in injson: cls.out_inst = midi_inst.cvpj_midi_inst.json__parse(injson['out_inst'])
		return cls

class cvpj_plugslots:
	__slots__ = ['slots_notes','slots_audio','slots_mixer','slots_synths','synth','slots_audio_enabled']
	def __init__(self):
		self.slots_synths = []
		self.slots_notes = []
		self.slots_audio = []
		self.slots_audio_enabled = True
		self.slots_mixer = []
		self.synth = ''

	def json__make(self):
		outjson = {}
		outjson['slots_synths'] = self.slots_synths
		outjson['slots_notes'] = self.slots_notes
		outjson['slots_audio'] = self.slots_audio
		outjson['slots_audio_enabled'] = self.slots_audio_enabled
		outjson['slots_mixer'] = self.slots_mixer
		outjson['synth'] = self.synth
		return outjson

	@classmethod
	def json__parse(cls, injson):
		cls = cls()
		if 'slots_synths' in injson: cls.slots_synths = injson['slots_synths']
		if 'slots_notes' in injson: cls.slots_notes = injson['slots_notes']
		if 'slots_audio' in injson: cls.slots_audio = injson['slots_audio']
		if 'slots_audio_enabled' in injson: cls.slots_audio_enabled = injson['slots_audio_enabled']
		if 'slots_mixer' in injson: cls.slots_mixer = injson['slots_mixer']
		if 'synth' in injson: cls.synth = injson['synth']
		return cls

	def set_synth(self, pluginid):
		self.slots_synths = [pluginid]
		self.synth = pluginid

	def plugin_autoplace(self, plugin_obj, pluginid):
		if plugin_obj is not None:
			if plugin_obj.role == 'fx': self.slots_audio.append(pluginid)
			elif plugin_obj.role == 'notefx': self.slots_notes.append(pluginid)
			elif plugin_obj.role == 'synth': 
				if not self.synth: self.synth = pluginid
				self.slots_synths.append(pluginid)

	def copy(self):
		return copy.deepcopy(self)

	def __iter__(self):
		for x in self.slots_notes: yield 'notes', x
		for x in self.slots_synths: yield 'synth', x
		for x in self.slots_audio: yield 'audio', x

class cvpj_instrument:
	__slots__ = ['visual','params','datavals','midi','fxrack_channel','pluginid','is_drum','plugslots','group','latency_offset','visual_keynotes']
	def __init__(self):
		self.visual = visual.cvpj_visual()
		self.params = params.cvpj_paramset()
		self.datavals = params.cvpj_datavals()
		self.midi = cvpj_midiport()
		self.is_drum = False
		self.fxrack_channel = -1
		self.plugslots = cvpj_plugslots()
		self.latency_offset = 0
		self.group = None
		self.visual_keynotes = visual.cvpj_visual_keynote()

	def json__make(self):
		outjson = {}
		outjson['visual'] = self.visual.json__make()
		outjson['params'] = self.params.json__make()
		outjson['datavals'] = self.datavals.json__make()
		outjson['midi'] = self.midi.json__make()
		outjson['plugslots'] = self.plugslots.json__make()
		outjson['visual_keynotes'] = self.visual_keynotes.json__make()
		outjson['is_drum'] = self.is_drum
		outjson['fxrack_channel'] = self.fxrack_channel
		outjson['latency_offset'] = self.latency_offset
		outjson['group'] = self.group
		return outjson

	@classmethod
	def json__parse(cls, injson):
		cls = cls()
		if 'visual' in injson: cls.visual = visual.cvpj_visual.json__parse(injson['visual'])
		if 'params' in injson: cls.params = params.cvpj_paramset.json__parse(injson['params'])
		if 'datavals' in injson: cls.datavals = params.cvpj_datavals.json__parse(injson['datavals'])
		if 'midi' in injson: cls.midi = cvpj_midiport.json__parse(injson['midi'])
		if 'plugslots' in injson: cls.plugslots = cvpj_plugslots.json__parse(injson['plugslots'])
		if 'visual_keynotes' in injson: cls.visual_keynotes = visual.cvpj_visual_keynote.json__parse(injson['visual_keynotes'])
		if 'is_drum' in injson: cls.is_drum = injson['is_drum']
		if 'fxrack_channel' in injson: cls.fxrack_channel = injson['fxrack_channel']
		if 'latency_offset' in injson: cls.latency_offset = injson['latency_offset']
		if 'group' in injson: cls.group = injson['group']
		return cls

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
		indict = {}
		indict['bank_hi'] = midi_obj.bank_hi
		indict['bank'] = midi_obj.bank
		indict['patch'] = midi_obj.patch
		indict['drum'] = midi_obj.drum
		indict['device'] = midi_obj.device

		plugin_obj = convproj_obj.plugin__addspec__midi(plug_id, indict)
		plugin_obj.role = 'synth'
		self.plugslots.synth = plug_id
		self.params.add('usemasterpitch', not m_drum, 'bool')
		if use_visual: self.visual.from_dset_midi(m_bank_hi, m_bank, m_inst, m_drum, m_dev, False)
		return plugin_obj

class cvpj_return_track:
	__slots__ = ['visual','visual_ui','params','datavals','sends','plugslots','latency_offset']
	def __init__(self):
		self.visual = visual.cvpj_visual()
		self.visual_ui = visual.cvpj_visual_ui()
		self.params = params.cvpj_paramset()
		self.datavals = params.cvpj_datavals()
		self.plugslots = cvpj_plugslots()
		self.sends = sends.cvpj_sends()
		self.latency_offset = 0

	def json__make(self):
		outjson = {}
		outjson['visual'] = self.visual.json__make()
		outjson['visual_ui'] = self.visual_ui.json__make()
		outjson['params'] = self.params.json__make()
		outjson['datavals'] = self.datavals.json__make()
		outjson['plugslots'] = self.plugslots.json__make()
		outjson['sends'] = self.sends.json__make()
		outjson['latency_offset'] = self.latency_offset
		return outjson

	@classmethod
	def json__parse(cls, injson):
		cls = cls()
		if 'visual' in injson: cls.visual = visual.cvpj_visual.json__parse(injson['visual'])
		if 'visual_ui' in injson: cls.visual_ui = visual.cvpj_visual_ui.json__parse(injson['visual_ui'])
		if 'params' in injson: cls.params = params.cvpj_paramset.json__parse(injson['params'])
		if 'datavals' in injson: cls.datavals = params.cvpj_datavals.json__parse(injson['datavals'])
		if 'plugslots' in injson: cls.plugslots = cvpj_plugslots.json__parse(injson['plugslots'])
		if 'sends' in injson: cls.sends = sends.cvpj_sends.json__parse(injson['sends'])
		if 'latency_offset' in injson: cls.latency_offset = injson['latency_offset']
		return cls

	def plugin_autoplace(self, plugin_obj, pluginid):
		self.plugslots.plugin_autoplace(plugin_obj, pluginid)

class cvpj_lane:
	def __init__(self, track_type, time_ppq, uses_placements, is_indexed):
		self.visual = visual.cvpj_visual()
		self.visual_ui = visual.cvpj_visual_ui()
		self.params = params.cvpj_paramset()
		self.datavals = params.cvpj_datavals()
		self.placements = placements.cvpj_placements(time_ppq, uses_placements, is_indexed)

	def json__make(self):
		outjson = {}
		outjson['visual'] = self.visual.json__make()
		outjson['visual_ui'] = self.visual_ui.json__make()
		outjson['params'] = self.params.json__make()
		outjson['datavals'] = self.datavals.json__make()
		outjson['placements'] = self.placements.json__make()
		return outjson

	@classmethod
	def json__parse(cls, injson):
		cls = cls()
		if 'visual' in injson: cls.visual = visual.cvpj_visual.json__parse(injson['visual'])
		if 'visual_ui' in injson: cls.visual_ui = visual.cvpj_visual_ui.json__parse(injson['visual_ui'])
		if 'params' in injson: cls.params = params.cvpj_paramset.json__parse(injson['params'])
		if 'datavals' in injson: cls.datavals = params.cvpj_datavals.json__parse(injson['datavals'])
		if 'placements' in injson: cls.placements = placements.cvpj_placements.json__parse(injson['placements'])
		return cls

class cvpj_armstate:
	def __init__(self):
		self.on = False
		self.in_keys = False
		self.in_audio = False

	def json__make(self):
		outjson = {}
		outjson['on'] = self.on
		if self.in_keys: outjson['in_keys'] = self.in_keys
		if self.in_audio: outjson['in_audio'] = self.in_audio
		return outjson

	@classmethod
	def json__parse(cls, injson):
		cls = cls()
		if 'on' in injson: cls.on = injson['on']
		if 'in_keys' in injson: cls.in_keys = injson['in_keys']
		if 'in_audio' in injson: cls.in_audio = injson['in_audio']
		return cls

class cvpj_track:
	__slots__ = ['time_ppq','uses_placements','lanes','is_indexed','type','is_laned','datavals','visual','visual_ui','visual_inst','params','midi','fxrack_channel','placements','sends','group','returns','notelist_index','scenes','audio_channels','is_drum','timemarkers','armed','plugslots','latency_offset','visual_keynotes']
	def __init__(self, track_type, time_ppq, uses_placements, is_indexed):
		self.time_ppq = time_ppq
		self.uses_placements = uses_placements
		self.is_indexed = is_indexed
		self.type = track_type
		self.is_laned = False
		self.lanes = {}
		self.visual = visual.cvpj_visual()
		self.visual_ui = visual.cvpj_visual_ui()
		self.visual_inst = visual.cvpj_visual()
		self.params = params.cvpj_paramset()
		self.datavals = params.cvpj_datavals()
		self.midi = cvpj_midiport()
		self.plugslots = cvpj_plugslots()
		self.fxrack_channel = -1
		self.sends = sends.cvpj_sends()
		self.placements = placements.cvpj_placements(self.time_ppq, self.uses_placements, self.is_indexed)
		self.group = None
		self.returns = {}
		self.notelist_index = {}
		self.scenes = {}
		self.audio_channels = 2
		self.is_drum = False
		self.timemarkers = timemarker.cvpj_timemarkers(time_ppq)
		self.armed = cvpj_armstate()
		self.latency_offset = 0
		self.visual_keynotes = visual.cvpj_visual_keynote()

	def json__make(self):
		outjson = {}
		outjson['time_ppq'] = self.time_ppq
		outjson['uses_placements'] = self.uses_placements
		outjson['is_indexed'] = self.is_indexed
		outjson['type'] = self.type
		outjson['is_laned'] = self.is_laned
		outjson['lanes'] = dict([(k, v.json__make()) for k, v in self.lanes])
		outjson['visual'] = self.visual.json__make() 
		outjson['visual_ui'] = self.visual_ui.json__make() 
		outjson['visual_inst'] = self.visual_inst.json__make() 
		outjson['params'] = self.params.json__make() 
		outjson['datavals'] = self.datavals.json__make() 
		outjson['midi'] = self.midi.json__make() 
		outjson['plugslots'] = self.plugslots.json__make() 
		outjson['fxrack_channel'] = self.fxrack_channel
		outjson['sends'] = self.sends.json__make() 
		outjson['placements'] = self.placements.json__make()
		outjson['group'] = self.group = None
		outjson['returns'] = dict([(k, v.json__make()) for k, v in self.returns])
		outjson['notelist_index'] = dict([(k, v.json__make()) for k, v in self.notelist_index])
		#outjson['scenes'] = dict([(k, v.json__make()) for k, v in self.scenes]) JSON__WIP
		outjson['audio_channels'] = self.audio_channels
		outjson['is_drum'] = self.is_drum
		outjson['timemarkers'] = self.timemarkers.json__make() 
		outjson['armed'] = self.armed.json__make() 
		outjson['latency_offset'] = self.latency_offset
		outjson['visual_keynotes'] = self.visual_keynotes.json__make() 
		return outjson

	@classmethod
	def json__parse(cls, injson):
		cls = cls()
		if 'time_ppq' in injson: cls.time_ppq = injson['time_ppq']
		if 'uses_placements' in injson: cls.uses_placements = injson['uses_placements']
		if 'is_indexed' in injson: cls.is_indexed = injson['is_indexed']
		if 'type' in injson: cls.type = injson['type']
		if 'is_laned' in injson: cls.is_laned = injson['is_laned']
		if 'lanes' in injson: cls.lanes = dict([(k, cvpj_lane.json__parse(v)) for k, v in injson['lanes']])
		if 'visual' in injson: cls.visual = visual.cvpj_visual.json__parse(injson['visual'])
		if 'visual_ui' in injson: cls.visual_ui = visual.cvpj_visual_ui.json__parse(injson['visual_ui'])
		if 'visual_inst' in injson: cls.visual_inst = visual.cvpj_visual.json__parse(injson['visual_inst'])
		if 'params' in injson: cls.params = params.cvpj_paramset.json__parse(injson['params'])
		if 'datavals' in injson: cls.datavals = params.cvpj_datavals.json__parse(injson['datavals'])
		if 'midi' in injson: cls.midi = cvpj_midiport.json__parse(injson['midi'])
		if 'plugslots' in injson: cls.plugslots = cvpj_plugslots.json__parse(injson['plugslots'])
		if 'fxrack_channel' in injson: cls.fxrack_channel = injson['fxrack_channel']
		if 'sends' in injson: cls.sends = sends.cvpj_sends.json__parse(injson['sends'])
		if 'placements' in injson: cls.placements = placements.cvpj_placements.json__parse(injson['placements'])
		if 'group' in injson: cls.group = injson['group']
		if 'returns' in injson: cls.returns = dict([(k, cvpj_track.json__parse(v)) for k, v in injson['lanes']])
		if 'notelist_index' in injson: cls.notelist_index = dict([(k, cvpj_nle.json__parse(v)) for k, v in injson['lanes']])
		#if 'scenes' in injson: cls.scenes = dict([(k, cvpj_nle.json__parse(v)) for k, v in injson['lanes']]) JSON__WIP
		if 'audio_channels' in injson: cls.audio_channels = injson['audio_channels']
		if 'is_drum' in injson: cls.is_drum = injson['is_drum']
		if 'timemarkers' in injson: cls.timemarkers = timemarker.cvpj_timemarkers.json__parse(injson['timemarkers'])
		if 'armed' in injson: cls.armed = cvpj_armstate.json__parse(injson['armed'])
		if 'latency_offset' in injson: cls.latency_offset = injson['latency_offset']
		if 'visual_keynotes' in injson: cls.visual_keynotes = visual.cvpj_visual_keynote.json__parse(injson['visual_keynotes'])
		return cls

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
		indict = {}
		indict['bank_hi'] = midi_obj.bank_hi
		indict['bank'] = midi_obj.bank
		indict['patch'] = midi_obj.patch
		indict['drum'] = midi_obj.drum
		indict['device'] = midi_obj.device
		plugin_obj = convproj_obj.plugin__addspec__midi(plug_id, indict)
		plugin_obj.role = 'synth'
		self.plugslots.synth = plug_id
		self.params.add('usemasterpitch', not m_drum, 'bool')
		if use_visual: self.visual.from_dset_midi(m_bank_hi, m_bank, m_inst, m_drum, m_dev, False)
		self.visual_inst.from_dset_midi(m_bank_hi, m_bank, m_inst, m_drum, m_dev, False)
		return plugin_obj

	def used_insts(self):
		used_insts = self.placements.used_insts()
		for _, lane in self.lanes.items(): used_insts += lane.placements.used_insts()
		return list(set(used_insts))

	def scene__add(self, i_id, i_lane):
		if i_id not in self.scenes: self.scenes[i_id] = {}
		if i_lane not in self.scenes[i_id]: self.scenes[i_id][i_lane] = placements.cvpj_placements(self.time_ppq, self.uses_placements, self.is_indexed)
		return self.scenes[i_id][i_lane]

	def get_midi(self, convproj_obj):
		plugin_found, plugin_obj = convproj_obj.plugin__get(self.plugslots.synth)
		if plugin_found:
			if plugin_obj.midi_incompat_synth_on: return plugin_obj.midi_incompat_synth
			else: return plugin_obj.midi
		else:
			return self.midi.out_inst if self.midi.out_enabled else None

	def fx__return__add(self, returnid):
		self.returns[returnid] = cvpj_track('return', self.time_ppq, False, False)
		return self.returns[returnid]

	def make_base(self):
		c_obj = cvpj_track(self.type,self.time_ppq,self.uses_placements,self.is_indexed)
		c_obj.time_ppq = self.time_ppq
		c_obj.uses_placements = self.uses_placements
		c_obj.is_indexed = self.is_indexed
		c_obj.type = self.type
		c_obj.is_laned = False
		c_obj.lanes = {}
		c_obj.visual = copy.deepcopy(self.visual)
		c_obj.visual_ui = copy.deepcopy(self.visual_ui)
		c_obj.params = copy.deepcopy(self.params)
		c_obj.datavals = copy.deepcopy(self.datavals)
		c_obj.midi = copy.deepcopy(self.midi)
		c_obj.fxrack_channel = self.fxrack_channel
		c_obj.plugslots = copy.deepcopy(self.plugslots)
		c_obj.sends = copy.deepcopy(self.sends)
		c_obj.placements = placements.cvpj_placements(self.time_ppq, self.uses_placements, self.is_indexed)
		c_obj.group = self.group
		c_obj.returns = self.returns
		c_obj.notelist_index = self.notelist_index
		c_obj.armed = copy.deepcopy(self.armed)
		c_obj.latency_offset = self.latency_offset
		c_obj.visual_keynotes = copy.deepcopy(self.visual_keynotes)
		return c_obj

	def make_base_inst(self, inst_obj):
		track_obj = self.make_base()
		#track_obj.visual = copy.deepcopy(inst_obj.visual)
		track_obj.params = copy.deepcopy(inst_obj.params)
		track_obj.datavals = copy.deepcopy(inst_obj.datavals)
		track_obj.midi = copy.deepcopy(inst_obj.midi)
		track_obj.fxrack_channel = inst_obj.fxrack_channel
		track_obj.plugslots = copy.deepcopy(inst_obj.plugslots)
		track_obj.latency_offset = inst_obj.latency_offset
		track_obj.visual_keynotes = copy.deepcopy(inst_obj.visual_keynotes)
		return track_obj

	def notelistindex__add(self, i_id):
		self.notelist_index[i_id] = cvpj_nle(self.time_ppq)
		return self.notelist_index[i_id]

	def add_lane(self, laneid):
		self.is_laned = True
		if laneid not in self.lanes: 
			self.lanes[laneid] = cvpj_lane(self.type, self.time_ppq, self.uses_placements, self.is_indexed)
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
				lane_obj = cvpj_lane(self.type, self.time_ppq, self.uses_placements, self.is_indexed)
				lane_obj.placements.pl_notes = lanefit_obj.mergeddata_notes[lanenum]
				lane_obj.placements.pl_audio = lanefit_obj.mergeddata_audio[lanenum]
				if allcolor: lane_obj.visual.color = copy.deepcopy(allcolor)
				self.lanes[laneid] = lane_obj

	def change_timings(self, time_ppq):
		self.placements.change_timings(time_ppq)
		for laneid, lane_obj in self.lanes.items():
			lane_obj.placements.change_timings(time_ppq)
		self.time_ppq = time_ppq
		self.timemarkers.change_timings(time_ppq)

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
		self.plugslots.plugin_autoplace(plugin_obj, pluginid)
