# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import logging
import numpy as np
import struct

logger_project = logging.getLogger('project')

def convert(convproj_obj):
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
	from objects.convproj import midievents

	logger_project.info('ProjType Convert: ClassicalMultiple > RegularMultiple')

	# -----------------------------------------------------------------------------------------
	# -----------------------------------------------------------------------------------------
	# -------------------------------------- INIT VALUES --------------------------------------
	# -----------------------------------------------------------------------------------------
	# -----------------------------------------------------------------------------------------

	total_notes = 0
	total_control = 0
	total_tempo = 0
	total_pitch = 0
	total_timesig = 0

	num_ports = 0

	for trackid, track_obj in convproj_obj.track__iter():
		midievents_obj = track_obj.placements.midievents
		midievents_obj.sort()
		midievents_obj.clean()
		num_ports = max(midievents_obj.port, num_ports)

		total_notes += midievents_obj.count_part('type', midievents.EVENTID__NOTE_ON)
		total_control += midievents_obj.count_part('type', midievents.EVENTID__CONTROL)
		total_pitch += midievents_obj.count_part('type', midievents.EVENTID__PITCH)
		total_tempo += midievents_obj.count_part('type', midievents.EVENTID__TEMPO)
		total_timesig += midievents_obj.count_part('type', midievents.EVENTID__TIMESIG)

	num_channels = convproj_obj.midi.num_channels
	num_ports += 1

	notes_data = midinotes.notes_data(num_ports, num_channels)
	notes_data.alloc(total_notes)

	ctrl_data = ctrls.ctrl_data(num_ports, num_channels)
	ctrl_data.alloc(total_control)

	tempo_data = automation.tempo_data()
	tempo_data.alloc(total_tempo)

	timesig_data = automation.timesig_data()
	timesig_data.alloc(total_timesig)

	pitch_data = pitch.pitch_data(num_ports, num_channels)
	pitch_data.alloc(total_pitch)

	sysex_data = sysex.sysex_data()
	seqspec_data = sysex.seqspec_data()
	instchange_data = instruments.instchange(num_ports, num_channels)

	# -----------------------------------------------------------------------------------------
	# -----------------------------------------------------------------------------------------
	# -------------------------------------- TRACK INPUT --------------------------------------
	# -----------------------------------------------------------------------------------------
	# -----------------------------------------------------------------------------------------

	visstore_data = visstore.visstore_data(num_ports, num_channels)

	visstore_data.setlen_track(convproj_obj.track__count())

	for n, d in enumerate(convproj_obj.track__iter()):
		trackid, track_obj = d
		midievents_obj = track_obj.placements.midievents
		for data in midievents_obj.seq_spec:
			seqspec_data.add(n, data)

	othertracks = []
	trackdata = []
	for n, d in enumerate(convproj_obj.track__iter()):
		trackid, track_obj = d

		if track_obj.type == 'midi':
			logger_project.debug('cm2rm: Track '+trackid)
			midievents_obj = track_obj.placements.midievents
			midievents_obj.add_note_durs()
	
			trackdata.append([trackid, track_obj])
	
			if track_obj.visual.name:
				visstore_data.vis_track_set_name(n, track_obj.visual.name)
			if track_obj.visual.color:
				visstore_data.vis_track_set_color_force(n, track_obj.visual.color.get_int())
	
			for seqspec_obj in seqspec_data.get(n):
				if seqspec_obj.sequencer == 'signal_midi' and seqspec_obj.param == 'color':
					visstore_data.vis_track_set_color_force(n, seqspec_obj.value)
				if seqspec_obj.sequencer == 'anvil_studio' and seqspec_obj.param == 'color':
					visstore_data.vis_track_set_color_force(n, seqspec_obj.value)
				if seqspec_obj.sequencer == 'studio_one' and seqspec_obj.param == 'color':
					visstore_data.vis_track_set_color_force(n, seqspec_obj.value)
	
			portnum = midievents_obj.port
	
			usedchans = midievents_obj.get_channums()
			if len(usedchans)==1:
				visstore_data.set_track_chan(n, portnum, usedchans[0])
	
			for x in midievents_obj:
				if x['type'] == midievents.EVENTID__NOTE_DUR:
					notes_data.add_note_dur(n, x['pos'], x['chan'], portnum, x['value'], x['value2'], x['uhival'])
	
				if x['type'] == midievents.EVENTID__NOTE_ON:
					notes_data.add_note_on(n, x['pos'], x['chan'], portnum, x['value'], x['value2'])
	
				if x['type'] == midievents.EVENTID__NOTE_OFF:
					notes_data.add_note_off(x['chan'], portnum, x['value'], x['pos'])
	
				if x['type'] == midievents.EVENTID__CONTROL:
					chanport = gfunc.calc_channum(x['chan'], portnum, num_channels)
					if x['value'] == 0:
						instchange_data.add_bank(x['pos'], chanport, x['uhival'])
					elif x['value'] == 32:
						instchange_data.add_hibank(x['pos'], chanport, x['uhival'])
					else:
						ctrl_data.add_point(x['pos'], chanport, x['value'], x['uhival'])
	
				if x['type'] == midievents.EVENTID__PITCH:
					pitch_data.add(x['pos'], gfunc.calc_channum(x['chan'], portnum, num_channels), x['shival'])
	
				if x['type'] == midievents.EVENTID__PROGRAM:
					instchange_data.add_program(x['pos'], gfunc.calc_channum(x['chan'], portnum, num_channels), x['value'])
	
				if x['type'] == midievents.EVENTID__SYSEX:
					sysex_data.add(x['pos'], midievents_obj.sysex[x['uhival']])
	
				if x['type'] == midievents.EVENTID__TEMPO:
					tempo_data.add(x['pos'], struct.unpack('f', struct.pack('I', x['uhival']))[0])
	
				if x['type'] == midievents.EVENTID__TIMESIG:
					timesig_data.add(x['pos'], x['value'], x['value2'])
	
				if x['type'] == midievents.EVENTID__TEXT:
					marker_data = midievents_obj.texts[x['uhival']]
					if marker_data == 'loopStart':
						convproj_obj.transport.loop_active = True
						convproj_obj.transport.loop_start = x['pos']
	
					if marker_data == 'loopEnd':
						convproj_obj.transport.loop_end = x['pos']
	
					if marker_data == 'Start':
						convproj_obj.transport.start_pos = x['pos']
	
				if x['type'] == midievents.EVENTID__MARKER:
					marker_data = midievents_obj.markers[x['uhival']]
					timemarker_obj = convproj_obj.timemarker__add()
					timemarker_obj.position = x['pos']
					if marker_data: timemarker_obj.visual.name = marker_data

	logger_project.debug('cm2rm: SysEX')

	#sc55_display = []

	for p, sysex_obj in sysex_data:

		if sysex_obj.vendor == '#43':
			if (sysex_obj.param, sysex_obj.value) == ('reset', 'all_params'):
				instchange_data.add_device(p, devices_types.DEVICETYPE_XG)

		if sysex_obj.vendor == '#41':

			if sysex_obj.param == 'gs_reset': 
				instchange_data.add_device(p, devices_types.DEVICETYPE_GS)

			if sysex_obj.model_id == 22: 
				instchange_data.add_device(p, devices_types.DEVICETYPE_MT32)

			if sysex_obj.model_id == 66: 
				if (sysex_obj.category, sysex_obj.group, sysex_obj.param) == ('patch_a', 'block', 'use_rhythm'):
					instchange_data.add_drum(p, sysex_obj.num if sysex_obj.num else 9, sysex_obj.value)

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

	notes_data.sort()
	ctrl_data.sort()
	tempo_data.sort()
	timesig_data.sort()

	logger_project.debug('cm2rm: Instruments')
	instchange_data.sort()
	instchange_data.clean()
	notes_data.proc_instchan()
	notes_data.add_instchange(instchange_data)
	notes_data.get_note_starts()

	autoloc_store = automation.autoloc_store(num_ports, num_channels)
	fxmaker = fxchans.fxchans_maker(num_ports, num_channels)

	logger_project.debug('cm2rm: Controls and FX')
	for pnum in range(num_ports):
		for enum in range(num_channels):
			chanport = gfunc.calc_channum(enum, pnum, num_channels)
			fxmaker.add_fx(pnum, enum, ctrl_data.get_cc_used_fx(chanport))
			startpos = notes_data.get_startpos(chanport)
			ctrl_data.add_startpos(startpos, chanport)
			for c, v in ctrl_data.get_init_vals(chanport):
				fxmaker.add_cc_vals(pnum, enum, c, v)

	fxmaker.generate(convproj_obj)
	fxmaker.make_autoloc(convproj_obj, autoloc_store)

	ctrl_data.add_loops(convproj_obj.transport)

	logger_project.debug('cm2rm: Automation')
	for pnum in range(num_ports):
		for enum in range(num_channels):
			chanport = gfunc.calc_channum(enum, pnum, num_channels)
			for ccnum, data, afterstart in ctrl_data.get_auto(chanport):
				autoloc = autoloc_store.get_autoloc(pnum, enum, ccnum)
				math_add, math_div = autoloc_store.get_math(pnum, enum, ccnum)
				if afterstart:
					for pos, val in data:
						val = (float(val)+math_add)/math_div
						convproj_obj.automation.add_autotick(autoloc, 'float', int(pos), val)

	start_pos = notes_data.get_global_startpos()
	logger_project.debug('cm2rm: Pitch Automation')
	for pnum in range(num_ports):
		for enum in range(num_channels):
			chanport = gfunc.calc_channum(enum, pnum, num_channels)
			autoloc = autoloc_store.get_autoloc_pitch(pnum, enum)
			if autoloc:
				for pos, val in pitch_data.get_auto(chanport):
					convproj_obj.automation.add_autotick(autoloc, 'float', int(pos), val)

	logger_project.debug('cm2rm: Tempo')
	inittempo = tempo_data.get_inital(start_pos)
	if inittempo: convproj_obj.params.add('bpm', inittempo, 'float')
	for pos, val in tempo_data.get_points():
		convproj_obj.automation.add_autotick(['main', 'bpm'], 'float', int(pos), float(val))

	logger_project.debug('cm2rm: TimeSig')
	inittimesig = timesig_data.get_inital(start_pos)
	if inittimesig is not None: convproj_obj.timesig = inittimesig
	for pos, num, denom in timesig_data.get_points():
		convproj_obj.timesig_auto.add_point(pos, [num, denom])

	# -----------------------------------------------------------------------------------------
	# -----------------------------------------------------------------------------------------
	# -------------------------------------- INSTRUMENTS --------------------------------------
	# -----------------------------------------------------------------------------------------
	# -----------------------------------------------------------------------------------------

	used_inst = notes_data.get_used_inst()
	visstore_data.set_used_inst(used_inst)
	visstore_data.set_cust_inst(convproj_obj.midi_cust_inst)

	if len(trackdata)==1:
		visstore_data.proc__inst_to_fx()

	if len(trackdata)>1:
		visstore_data.proc__track_to_fx__track()
		visstore_data.proc__track_to_fx__inst()
		visstore_data.proc__track_to_inst()
		visstore_data.proc__inst_to_fx()
		visstore_data.proc__fx_to_track()
		visstore_data.proc__inst_to_track()

	logger_project.debug('cm2rm: Instruments')
	for n, inst in enumerate(used_inst):
		inst_obj = instruments.cvpj_create_instrument(convproj_obj, inst)
		inst_obj.fxrack_channel = fxmaker.get_fxid(inst['port'], inst['chan'])
		visstore_data.vis_inst[n].to_cvpj_visual(inst_obj.visual)
		for x in convproj_obj.midi_cust_inst:
			if instruments.match_custom(inst, x):
				pluginid = instruments.replacetxt(inst, x.pluginid)
				inst_obj.plugslots.set_synth(pluginid)

	for po in range(num_ports):
		for ch in range(num_channels):
			fxchannel_obj = fxmaker.get_fxobj(po, ch)
			if fxchannel_obj:
				fxn = fxmaker.get_fxid(po, ch)
				visstore_data.vis_fxchan[po][ch].to_cvpj_visual(fxchannel_obj.visual)

	# -----------------------------------------------------------------------------------------
	# -----------------------------------------------------------------------------------------
	# ----------------------------------------- TRACKS ----------------------------------------
	# -----------------------------------------------------------------------------------------
	# -----------------------------------------------------------------------------------------

	miditracks = [x for x in trackdata if x[1].type == 'midi']

	if trackdata:
		logger_project.debug('cm2rm: Out Tracks')

		firsttrack_id, firsttrack_obj = trackdata[0]

		if len(miditracks)==1:
			convproj_obj.track__del(firsttrack_id)
			chanportlist = np.unique(used_inst['chanport'])
			for chanport in chanportlist:
				track_obj = convproj_obj.track__add('cm2rm_'+str(chanport), 'instruments', firsttrack_obj.uses_placements, firsttrack_obj.is_indexed)
				tracknotes = notes_data.filter_chanport(chanport)
				portnum, channum = gfunc.split_channum(chanport, num_channels)
				visstore_data.vis_fxchan[portnum][channum].to_cvpj_visual(track_obj.visual)

				cvpj_notelist = track_obj.placements.notelist

				if len(tracknotes):
					compused = np.nonzero(np.logical_and(tracknotes['complete'], tracknotes['used']))[0]
					cvpj_notelist.clear_size(len(compused))
					for n in tracknotes:
						if n['complete']:
							cvpj_notelist.add_m(instruments.get_inst_id(n['inst']), 
								int(n['start']), 
								int(n['end']-n['start']), 
								int(n['key'])-60, 
								float(n['vol'])/127, 
								None)
		
		else:
			for n, track_obj in enumerate(trackdata):
				visstore_data.vis_track[n].to_cvpj_visual(track_obj.visual)
				midievents_obj = track_obj.placements.midievents
				midievents = midievents_obj.data
	
				cvpj_notelist = track_obj.placements.notelist
				tracknotes = notes_data.filter_track(n)

				if len(tracknotes):
					compused = np.nonzero(np.logical_and(tracknotes['complete'], tracknotes['used']))[0]

					cvpj_notelist.clear_size(len(compused))
					for n in tracknotes:
						if n['complete']:
							cvpj_notelist.add_m(instruments.get_inst_id(n['inst']), 
								int(n['start']), 
								int(n['end']-n['start']), 
								int(n['key'])-60, 
								float(n['vol'])/127, 
								None)
		
				track_obj.type = 'instruments'
				midievents.clear()
	

	if convproj_obj.transport.loop_start and not convproj_obj.transport.loop_end:
		convproj_obj.transport.loop_end = convproj_obj.get_dur()

	convproj_obj.type = 'rm'
