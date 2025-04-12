# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import json
from functions import xtramath

class output_midi(plugins.base):
	def is_dawvert_plugin(self):
		return 'output'
	
	def get_name(self):
		return 'MIDI'
	
	def get_shortname(self):
		return 'midi'
	
	def gettype(self):
		return 'cm'
	
	def get_prop(self, in_dict): 
		in_dict['file_ext'] = 'mid'
		in_dict['fxtype'] = 'rack'
		in_dict['fxrack_params'] = ['vol','pan','pitch']
		in_dict['auto_types'] = ['nopl_ticks']
		in_dict['track_nopl'] = True
		in_dict['plugin_included'] = ['universal:midi']
		in_dict['projtype'] = 'cm'
	
	def parse(self, convproj_obj, dawvert_intent):
		import mido

		metamsg = mido.MetaMessage
		rmsg = mido.Message

		midiobj = mido.MidiFile()
		midiobj.ticks_per_beat = convproj_obj.time_ppq

		autotrack = mido.MidiTrack()
		midi_numerator, midi_denominator = convproj_obj.timesig


		headcmd = []
		if 'bpm' in convproj_obj.params.list():
			midi_tempo = mido.bpm2tempo(convproj_obj.params.get('bpm', 120).value)
			autotrack.append(metamsg('set_tempo', tempo=midi_tempo, time=0))
		aid_found, aid_data = convproj_obj.automation.get_autoticks(['main', 'bpm'])
		if aid_found:
			for pos, val in aid_data: headcmd.append([pos, 'tempo', val])

		if convproj_obj.transport.loop_active:
			headcmd.append([int(convproj_obj.transport.loop_start), 'loop_start'])
			if convproj_obj.transport.loop_end:
				headcmd.append([int(convproj_obj.transport.loop_end), 'loop_end'])

		headcmd = sorted(headcmd)
		prevpos = 0
		for hcmd in headcmd:
			posdif = hcmd[0]-prevpos
			if hcmd[1] == 'tempo': 
				midi_tempo = mido.bpm2tempo(hcmd[2])
				autotrack.append(metamsg('set_tempo', tempo=midi_tempo, time=posdif))
			if hcmd[1] == 'loop_start': 
				autotrack.append(rmsg('control_change', channel=0, control=111, value=0, time=posdif))
				autotrack.append(rmsg('control_change', channel=0, control=116, value=0, time=posdif))
			if hcmd[1] == 'loop_end': 
				autotrack.append(rmsg('control_change', channel=0, control=117, value=0, time=posdif))
			prevpos = hcmd[0]

		if len(autotrack):
			autotrack.insert(0, metamsg('track_name', name='Auto Track', time=0))
			midiobj.tracks.append(autotrack)

		for trackid, track_obj in convproj_obj.track__iter():
			miditrack = mido.MidiTrack()
			midi_trackname = track_obj.visual.name if track_obj.visual.name else ''
			midi_trackcolor = track_obj.visual.color

			middlenote = track_obj.datavals.get('middlenote', 0)

			if midi_trackname != '': 
				miditrack.append(metamsg('track_name', name=midi_trackname, time=0))
			if midi_trackcolor: 
				midi_trackcolor = midi_trackcolor.get_int()
				miditrack.append(metamsg('sequencer_specific', data=(83, 105, 103, 110, 1, 255, midi_trackcolor[2], midi_trackcolor[1], midi_trackcolor[0]))) #from Signal MIDI Editor
				miditrack.append(metamsg('sequencer_specific', data=(80, 114, 101, 83, 1, 255, midi_trackcolor[2], midi_trackcolor[1], midi_trackcolor[0]))) #from Studio One
				red_p1 = midi_trackcolor[0] >> 2
				red_p2 = (midi_trackcolor[0] << 5) & 0x7f
				green_p1 = midi_trackcolor[1] >> 3
				green_p2 = (midi_trackcolor[1] << 4) & 0x7f
				blue_p1 = midi_trackcolor[2] >> 4
				blue_p2 = midi_trackcolor[2] & 0x0f
				anvilcolor = [blue_p2,green_p2+blue_p1,red_p2+green_p1,red_p1]
				miditrack.append(metamsg('sequencer_specific', data=(5, 15, 52, anvilcolor[0], anvilcolor[1], anvilcolor[2], anvilcolor[3], 0))) #from Anvil Studio

			midievents_obj = track_obj.placements.midievents
			midievents_obj.sort()
			midievents_obj.del_note_durs()
			midievents_obj.sort()

			for x in midievents_obj.iter_events():
				etype = x[1]
				etime = int(x['pos_dif'])

				if etype == 'NOTE_OFF':
					outnote = int(x[3])-middlenote
					if 127>outnote>=0:
						miditrack.append(rmsg('note_off', channel=int(x[2]), note=outnote, time=etime))

				elif etype == 'NOTE_ON':
					outnote = int(x[3])-middlenote
					if 127>outnote>=0:
						miditrack.append(rmsg('note_on', channel=int(x[2]), note=outnote, velocity=int(x[4]), time=etime))

				elif etype == 'PROGRAM':
					miditrack.append(rmsg('program_change', channel=int(x[2]), program=int(x[3]), time=etime))

				elif etype == 'CONTROL':
					miditrack.append(rmsg('control_change', channel=int(x[2]), control=int(x[3]), value=int(x[4]), time=etime))

				elif etype == 'TEMPO':
					miditrack.append(metamsg('set_tempo', tempo=mido.bpm2tempo(x[6]), time=etime))

				elif etype == 'PITCH':
					miditrack.append(rmsg('pitchwheel', pitch=int(x[3]/4096), time=etime))

				elif etype == 'TIMESIG':
					miditrack.append(metamsg('time_signature', numerator=4, denominator=4, time=etime))

				elif etype == 'SYSEX':
					sysexdata = bytearray(midievents_obj.sysex[int(x[3])])
					miditrack.append(rmsg('sysex', data=sysexdata, time=etime))

				elif etype == 'TEXT':
					miditrack.append(metamsg('text', text=midievents_obj.texts[int(x[3])], time=etime))

				elif etype == 'SEQSPEC':
					sysexdata = bytearray(midievents_obj.seq_spec[int(x[3])])
					miditrack.append(metamsg('sequencer_specific', data=sysexdata, time=etime))

			midiobj.tracks.append(miditrack)

		if dawvert_intent.output_mode == 'file':
			midiobj.save(dawvert_intent.output_file)