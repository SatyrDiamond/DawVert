# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins

import logging
logger_input = logging.getLogger('input')

class reader_midifile_class():
	def do_song(self, input_file, convproj_obj):
		from objects_midi.parser import MidiFile
		midifile = MidiFile.fromFile(input_file)
		ppq = midifile.ppqn
		convproj_obj.set_timings(ppq, False)
		for n, miditrack in enumerate(midifile.tracks):
			track_obj = convproj_obj.track__add(str(n), 'midi', 1, False)
			logger_input.info('Track '+str(n+1)+' of '+str(len(midifile.tracks)))
			self.do_track(miditrack.events, track_obj)
		return ppq

	def do_track(self, eventlist, track_obj):
		from objects_midi import events as MidiEvents
		events_obj = track_obj.placements.midievents
		events_obj.data.alloc(len(eventlist))

		curpos = 0
		for msg in eventlist:
			curpos += msg.deltaTime
			if type(msg) == MidiEvents.NoteOnEvent: events_obj.add_note_on(curpos, msg.channel, msg.note, msg.velocity)
			elif type(msg) == MidiEvents.NoteOffEvent: events_obj.add_note_off(curpos, msg.channel, msg.note, 0)
			elif type(msg) == MidiEvents.TrackNameEvent: track_obj.visual.name = msg.name
			elif type(msg) == MidiEvents.CopyrightEvent: events_obj.add_copyright(msg.copyright)
			elif type(msg) == MidiEvents.PitchBendEvent: events_obj.add_pitch(curpos, msg.channel, msg.pitch)
			elif type(msg) == MidiEvents.ControllerEvent: events_obj.add_control(curpos, msg.channel, msg.controller, msg.value)
			elif type(msg) == MidiEvents.ProgramEvent: events_obj.add_program(curpos, msg.channel, msg.program)
			elif type(msg) == MidiEvents.TempoEvent: events_obj.add_tempo(curpos, 60000000/msg.tempo)
			elif type(msg) == MidiEvents.TimeSignatureEvent: events_obj.add_timesig(curpos, msg.numerator, msg.denominator**2)
			elif type(msg) == MidiEvents.TextEvent: events_obj.add_text(curpos, msg.text)
			elif type(msg) == MidiEvents.SysExEvent: events_obj.add_sysex(curpos, msg.data)
			elif type(msg) == MidiEvents.MarkerEvent: events_obj.add_marker(curpos, msg.marker)
			elif type(msg) == MidiEvents.LyricEvent: events_obj.add_lyric(curpos, msg.lyric)
			elif type(msg) == MidiEvents.SequencerEvent: events_obj.add_seq_spec(msg.data)
			elif type(msg) == MidiEvents.MidiPortEvent: events_obj.add_port(msg.port)
			elif type(msg) == MidiEvents.EndOfTrackEvent: break

class input_midi(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'midi'
	
	def get_name(self):
		return 'MIDI'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['file_ext'] = ['mid']
		in_dict['fxrack_params'] = ['vol','pan','pitch']
		in_dict['auto_types'] = ['nopl_ticks']
		in_dict['track_nopl'] = True
		in_dict['plugin_included'] = ['universal:midi']
		in_dict['fxtype'] = 'rack'
		in_dict['projtype'] = 'cm'

	def parse(self, convproj_obj, dawvert_intent):
		convproj_obj.fxtype = 'rack'
		convproj_obj.type = 'cm'

		midiread_obj = reader_midifile_class()

		if dawvert_intent.input_mode == 'file':
			midiread_obj.do_song(dawvert_intent.input_file, convproj_obj)

		convproj_obj.do_actions.append('do_addloop')
		convproj_obj.do_actions.append('do_singlenotelistcut')