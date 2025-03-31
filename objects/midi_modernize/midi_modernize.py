# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import objects.midi_modernize.fxchans as fxchans
import objects.midi_modernize.instruments as instruments
import objects.midi_modernize.notes as midinotes
import objects.midi_modernize.pitch as pitch
import objects.midi_modernize.sysex as sysex
import objects.midi_modernize.ctrls as ctrls
import objects.midi_modernize.automation as automation
import objects.midi_modernize.devices_types as devices_types
import objects.midi_modernize.visstore as visstore
import objects.midi_modernize.gfunc as gfunc
import numpy as np
import struct
from objects.convproj import midievents

class midi_modernize:
	def __init__(self, num_channels):
		self.total_notes = 0
		self.total_control = 0
		self.total_tempo = 0
		self.total_pitch = 0
		self.total_timesig = 0

		self.num_channels = num_channels
		self.num_ports = 1
		self.num_tracks = 0
		self.num_miditracks = 0

		self.tempo_data = automation.tempo_data()
		self.timesig_data = automation.timesig_data()
		self.sysex_data = sysex.sysex_data()
		self.seqspec_data = sysex.seqspec_data()
		self.notes_data = midinotes.notes_data(1, self.num_channels)
		self.ctrl_data = ctrls.ctrl_data(1, self.num_channels)
		self.pitch_data = pitch.pitch_data(1, self.num_channels)
		self.instchange_data = instruments.instchange(1, self.num_channels)
		self.visstore_data = visstore.visstore_data(1, self.num_channels)
		self.autoloc_store = automation.autoloc_store(1, self.num_channels)
		self.fxmaker = fxchans.fxchans_maker(1, self.num_channels)
		self.cvpj_tracks = []
		self.cvpj_tracks_midi = []

		self.sc55_display = []

	def memory__add_count(self, midievents_obj):
		midievents_obj.sort()
		midievents_obj.clean()
		self.num_ports = max(midievents_obj.port+1, self.num_ports)

		self.total_notes += midievents_obj.count_part('type', midievents.EVENTID__NOTE_ON)
		self.total_control += midievents_obj.count_part('type', midievents.EVENTID__CONTROL)
		self.total_pitch += midievents_obj.count_part('type', midievents.EVENTID__PITCH)
		self.total_tempo += midievents_obj.count_part('type', midievents.EVENTID__TEMPO)
		self.total_timesig += midievents_obj.count_part('type', midievents.EVENTID__TIMESIG)

	def memory__set_chanport(self):
		self.notes_data = midinotes.notes_data(self.num_ports, self.num_channels)
		self.ctrl_data = ctrls.ctrl_data(self.num_ports, self.num_channels)
		self.pitch_data = pitch.pitch_data(self.num_ports, self.num_channels)
		self.instchange_data = instruments.instchange(self.num_ports, self.num_channels)
		self.visstore_data = visstore.visstore_data(self.num_ports, self.num_channels)
		self.autoloc_store = automation.autoloc_store(self.num_ports, self.num_channels)
		self.fxmaker = fxchans.fxchans_maker(self.num_ports, self.num_channels)

	def memory__alloc(self):
		self.memory__set_chanport()
		self.notes_data.alloc(self.total_notes)
		self.ctrl_data.alloc(self.total_control)
		self.pitch_data.alloc(self.total_pitch)
		self.tempo_data.alloc(self.total_tempo)
		self.timesig_data.alloc(self.total_timesig)
		self.start_pos = None





	def from_cvpj__add_tracks(self, convproj_obj):
		self.cvpj_tracks = [x for x in convproj_obj.track__iter_num()]
		self.cvpj_tracks_midi = [x for x in self.cvpj_tracks if x[2].type == 'midi']
		self.num_tracks = len(self.cvpj_tracks)
		self.num_miditracks = len(self.cvpj_tracks_midi)
		self.visstore_data.setlen_track(len(self.cvpj_tracks))




	def add_events_seq_spec(self, tracknum, midievents_obj):
		for data in midievents_obj.seq_spec:
			self.seqspec_data.add(tracknum, data)

	def add_track_visual(self, tracknum, visual_obj):
		if visual_obj.name: self.visstore_data.vis_track_set_name(tracknum, visual_obj.name)
		if visual_obj.color: self.visstore_data.vis_track_set_color_force(tracknum, visual_obj.color.get_int())
	
		for seqspec_obj in self.seqspec_data.get(tracknum):
			if seqspec_obj.sequencer == 'signal_midi' and seqspec_obj.param == 'color':
				self.visstore_data.vis_track_set_color_force(tracknum, seqspec_obj.value)
			if seqspec_obj.sequencer == 'anvil_studio' and seqspec_obj.param == 'color':
				self.visstore_data.vis_track_set_color_force(tracknum, seqspec_obj.value)
			if seqspec_obj.sequencer == 'studio_one' and seqspec_obj.param == 'color':
				self.visstore_data.vis_track_set_color_force(tracknum, seqspec_obj.value)
	
	def visual_chan(self, tracknum, portnum, usedchans):
		if len(usedchans)==1:
			self.visstore_data.set_track_chan(tracknum, portnum, usedchans[0])

	def do_notes(self, convproj_obj, midievents_obj, inpos, dur, offset, in_section, portnum, tracknum):
		for x in midievents_obj:
			pos = (x['pos']-offset)+inpos
			condpos = (dur+inpos)>(pos)>=0 if dur>=0 else True

			if condpos:
				if x['type'] == midievents.EVENTID__NOTE_DUR:
					cur_notes = self.notes_data.add_note_dur(tracknum, pos, x['chan'], portnum, x['value'], x['value2'], x['uhival'])
					cur_notes['section'] = in_section

				elif x['type'] == midievents.EVENTID__NOTE_ON:
					cur_notes = self.notes_data.add_note_on(tracknum, pos, x['chan'], portnum, x['value'], x['value2'])
					cur_notes['section'] = in_section

				elif x['type'] == midievents.EVENTID__NOTE_OFF:
					self.notes_data.add_note_off(x['chan'], portnum, x['value'], pos)
	
				elif x['type'] == midievents.EVENTID__CONTROL:
					chanport = gfunc.calc_channum(x['chan'], portnum, self.num_channels)
					if x['value'] == 0:
						self.instchange_data.add_bank(pos, chanport, x['uhival'])
					elif x['value'] == 32:
						self.instchange_data.add_hibank(pos, chanport, x['uhival'])
					else:
						self.ctrl_data.add_point(pos, chanport, x['value'], x['uhival'])
	
				elif x['type'] == midievents.EVENTID__PITCH:
					self.pitch_data.add(pos, gfunc.calc_channum(x['chan'], portnum, self.num_channels), x['shival'])
	
				elif x['type'] == midievents.EVENTID__PROGRAM:
					self.instchange_data.add_program(pos, gfunc.calc_channum(x['chan'], portnum, self.num_channels), x['value'])
	
				elif x['type'] == midievents.EVENTID__SYSEX:
					self.sysex_data.add(pos, midievents_obj.sysex[x['uhival']])
	
				elif x['type'] == midievents.EVENTID__TEMPO:
					self.tempo_data.add(pos, struct.unpack('f', struct.pack('I', x['uhival']))[0])
	
				elif x['type'] == midievents.EVENTID__TIMESIG:
					self.timesig_data.add(pos, x['value'], x['value2'])
	
				elif x['type'] == midievents.EVENTID__TEXT:
					marker_data = midievents_obj.texts[x['uhival']]
					if marker_data == 'loopStart':
						convproj_obj.transport.loop_active = True
						convproj_obj.transport.loop_start = pos
	
					if marker_data == 'loopEnd':
						convproj_obj.transport.loop_end = pos
	
					if marker_data == 'Start':
						convproj_obj.transport.start_pos = pos
	
				elif x['type'] == midievents.EVENTID__MARKER:
					marker_data = midievents_obj.markers[x['uhival']]
					timemarker_obj = convproj_obj.timemarker__add()
					timemarker_obj.position = pos
					if marker_data: timemarker_obj.visual.name = marker_data

		self.start_pos = self.notes_data.get_global_startpos()

	def instchange_from_sysex(self):
		for p, sysex_obj in self.sysex_data:
	
			if sysex_obj.vendor == '#43':
				if (sysex_obj.param, sysex_obj.value) == ('reset', 'all_params'):
					self.instchange_data.add_device(p, devices_types.DEVICETYPE_XG)
	
			if sysex_obj.vendor == '#41':
	
				if sysex_obj.param == 'gs_reset': 
					self.instchange_data.add_device(p, devices_types.DEVICETYPE_GS)
	
				if sysex_obj.model_id == 22: 
					self.instchange_data.add_device(p, devices_types.DEVICETYPE_MT32)
	
				if sysex_obj.model_id == 66: 
					if (sysex_obj.category, sysex_obj.group, sysex_obj.param) == ('patch_a', 'block', 'use_rhythm'):
						self.instchange_data.add_drum(p, sysex_obj.num if sysex_obj.num else 9, sysex_obj.value)

			#if sysex_obj.model_id == 69: 
			#	if sysex_obj.group == 'bitmap': 
			#		if len(sysex_obj.value) == 66:
			#			pagedata = np.frombuffer(sysex_obj.value[0:-2], dtype=np.uint8).reshape((4, 16))
			#			scdisplay = np.zeros((16, 20), dtype=np.bool_)
			#			for part1num, part1 in enumerate(pagedata):
			#				for part2num, part2 in enumerate(part1):
			#					startd = (part1num*5)
			#					scdisplay[part2num][startd:startd+5] = [bool((1 << i) & part2) for i in range(4, -1, -1)]
			#		sc55_display[p] = scdisplay

	def sort(self):
		self.notes_data.sort()
		self.ctrl_data.sort()
		self.tempo_data.sort()
		self.timesig_data.sort()

	def do_instruments(self):
		self.instchange_data.sort()
		self.instchange_data.clean()
		self.notes_data.proc_instchan()
		self.notes_data.add_instchange(self.instchange_data)
		self.notes_data.get_note_starts()

	def do_fx_ctrls(self, convproj_obj):
		for pnum in range(self.num_ports):
			for enum in range(self.num_channels):
				chanport = gfunc.calc_channum(enum, pnum, self.num_channels)
				self.fxmaker.add_fx(pnum, enum, self.ctrl_data.get_cc_used_fx(chanport))
				startpos = self.notes_data.get_startpos(chanport)
				self.ctrl_data.add_startpos(startpos, chanport)
				for c, v in self.ctrl_data.get_init_vals(chanport):
					self.fxmaker.add_cc_vals(pnum, enum, c, v)
		self.fxmaker.generate(convproj_obj)
		self.fxmaker.make_autoloc(convproj_obj, self.autoloc_store)
		self.ctrl_data.add_loops(convproj_obj.transport)

	def do_automation(self, convproj_obj):
		for pnum in range(self.num_ports):
			for enum in range(self.num_channels):
				chanport = gfunc.calc_channum(enum, pnum, self.num_channels)
				for ccnum, data, afterstart in self.ctrl_data.get_auto(chanport):
					autoloc = self.autoloc_store.get_autoloc(pnum, enum, ccnum)
					math_add, math_div = self.autoloc_store.get_math(pnum, enum, ccnum)
					if afterstart:
						for pos, val in data:
							val = (float(val)+math_add)/math_div
							convproj_obj.automation.add_autotick(autoloc, 'float', int(pos), val)

	def do_pitch_automation(self, convproj_obj):
		for pnum in range(self.num_ports):
			for enum in range(self.num_channels):
				chanport = gfunc.calc_channum(enum, pnum, self.num_channels)
				autoloc = self.autoloc_store.get_autoloc_pitch(pnum, enum)
				if autoloc:
					for pos, val in self.pitch_data.get_auto(chanport):
						convproj_obj.automation.add_autotick(autoloc, 'float', int(pos), val)

	def do_tempo(self, convproj_obj):
		inittempo = self.tempo_data.get_inital(self.start_pos)
		if inittempo: convproj_obj.params.add('bpm', inittempo, 'float')
		for pos, val in self.tempo_data.get_points():
			convproj_obj.automation.add_autotick(['main', 'bpm'], 'float', int(pos), float(val))

	def do_timesig(self, convproj_obj):
		inittimesig = self.timesig_data.get_inital(self.start_pos)
		if inittimesig is not None: convproj_obj.timesig = inittimesig
		for pos, num, denom in self.timesig_data.get_points():
			convproj_obj.timesig_auto.add_point(pos, [num, denom])

	def to_cvpj_inst_visual(self, convproj_obj):
		self.used_inst = self.notes_data.get_used_inst()
		self.visstore_data.set_used_inst(self.used_inst)
		self.visstore_data.set_cust_inst(convproj_obj.midi_cust_inst)
	
		if self.num_miditracks==1:
			self.visstore_data.proc__inst_to_fx()
	
		if self.num_miditracks>1:
			self.visstore_data.proc__track_to_fx__track()
			self.visstore_data.proc__track_to_fx__inst()
			#self.visstore_data.proc__track_to_inst()
			self.visstore_data.proc__inst_to_fx()
			self.visstore_data.proc__fx_to_track()
			self.visstore_data.proc__inst_to_track()
	
		for n, inst in enumerate(self.used_inst):
			inst_obj = instruments.cvpj_create_instrument(convproj_obj, inst)
			inst_obj.fxrack_channel = self.fxmaker.get_fxid(inst['port'], inst['chan'])
			self.visstore_data.vis_inst[n].to_cvpj_visual(inst_obj.visual)
			for x in convproj_obj.midi_cust_inst:
				if instruments.match_custom(inst, x):
					pluginid = instruments.replacetxt(inst, x.pluginid)
					inst_obj.plugslots.set_synth(pluginid)
	
		for po in range(self.num_ports):
			for ch in range(self.num_channels):
				fxchannel_obj =  self.fxmaker.get_fxobj(po, ch)
				if fxchannel_obj:
					fxn =  self.fxmaker.get_fxid(po, ch)
					self.visstore_data.vis_fxchan[po][ch].to_cvpj_visual(fxchannel_obj.visual)

	def midinotes_to_cvpjnotes(self, tracknotes, cvpj_notelist, offset):
		if len(tracknotes):
			compused = np.nonzero(np.logical_and(tracknotes['complete'], tracknotes['used']))[0]
			cvpj_notelist.clear_size(len(compused))
			for n in tracknotes:
				if n['complete']:
					cvpj_notelist.add_m(instruments.get_inst_id(n['inst']), 
						int(n['start']-offset), 
						int(n['end']-n['start']), 
						int(n['key'])-60, 
						float(n['vol'])/127, 
						None)

	def output_tracks(self, convproj_obj):
		if self.cvpj_tracks:
			first_track = self.cvpj_tracks[0]
	
			if len(self.cvpj_tracks)==1:
				firsttrack_obj = first_track[2]
				convproj_obj.track__del(first_track[1])
				chanportlist = np.unique(self.used_inst['chanport'])
				for chanport in chanportlist:
					track_obj = convproj_obj.track__add('cm2rm_'+str(chanport), 'instruments', firsttrack_obj.uses_placements, firsttrack_obj.is_indexed)
					tracknotes = self.notes_data.filter_chanport(chanport)
					portnum, channum = gfunc.split_channum(chanport, self.num_channels)
					self.visstore_data.vis_fxchan[portnum][channum].to_cvpj_visual(track_obj.visual)
					self.midinotes_to_cvpjnotes(tracknotes, track_obj.placements.notelist, 0)
			else:
				for n, strackdata in enumerate(self.cvpj_tracks):
					track_obj = strackdata[2]
					self.visstore_data.vis_track[n].to_cvpj_visual(track_obj.visual)
					midievents_obj = track_obj.placements.midievents
					midievents = midievents_obj.data

					cvpj_notelist = track_obj.placements.notelist

					for plnum, pl_midi in enumerate(track_obj.placements.pl_midi):
						pl_notes = track_obj.placements.pl_notes.make_base_from_midi(pl_midi)
						pl_tracknotes = self.notes_data.filter_track_section(n, plnum+1)
						self.midinotes_to_cvpjnotes(pl_tracknotes, pl_notes.notelist, pl_notes.time.position, 0)
						
					tracknotes = self.notes_data.filter_track_section(n, 0)
	
					self.midinotes_to_cvpjnotes(tracknotes, track_obj.placements.notelist, 0)

					track_obj.type = 'instruments'
					midievents.clear()