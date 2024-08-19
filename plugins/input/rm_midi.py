# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
from objects.songinput import midi_in

import logging
logger_input = logging.getLogger('input')

class reader_midifile_class():
	def do_song(self, input_file):
		from objects_midi.parser import MidiFile
		midifile = MidiFile.fromFile(input_file)
		ppq = midifile.ppqn
		song_obj = midi_in.midi_song(16, ppq, 120, [4,4])
		for n, miditrack in enumerate(midifile.tracks):
			logger_input.info('Track '+str(n+1)+' of '+str(len(midifile.tracks)))
			track_obj = song_obj.create_track(len(miditrack.events))
			self.do_track(miditrack.events, track_obj, song_obj)
		return 16, ppq, song_obj

	def do_track(self, eventlist, track_obj, song_obj):
		from objects_midi import events as MidiEvents
		curpos = 0
		for msg in eventlist:
			curpos += msg.deltaTime
			if type(msg) == MidiEvents.NoteOnEvent:
				if msg.velocity != 0: track_obj.note_on(curpos, msg.channel, msg.note, msg.velocity)
				else: track_obj.note_off(curpos, msg.channel, msg.note)
			elif type(msg) == MidiEvents.NoteOffEvent:       track_obj.note_off(curpos, msg.channel, msg.note)
			elif type(msg) == MidiEvents.TrackNameEvent:     track_obj.track_name = msg.name
			elif type(msg) == MidiEvents.PitchBendEvent:     track_obj.pitchwheel(curpos, msg.channel, msg.pitch)
			elif type(msg) == MidiEvents.ControllerEvent:    track_obj.control_change(curpos, msg.channel, msg.controller, msg.value)
			elif type(msg) == MidiEvents.ProgramEvent:       track_obj.program_change(curpos, msg.channel, msg.program)
			elif type(msg) == MidiEvents.TempoEvent:         track_obj.set_tempo(curpos, 60000000/msg.tempo)
			elif type(msg) == MidiEvents.TimeSignatureEvent: track_obj.time_signature(curpos, msg.numerator, msg.denominator)
			elif type(msg) == MidiEvents.TextEvent:          track_obj.text(curpos, msg.text)
			elif type(msg) == MidiEvents.MarkerEvent:        track_obj.marker(curpos, msg.marker)
			elif type(msg) == MidiEvents.SequencerEvent:     track_obj.sequencer_specific(msg.data)
			elif type(msg) == MidiEvents.SysExEvent:         track_obj.sysex(curpos, msg.data)
			elif type(msg) == MidiEvents.CopyrightEvent:     track_obj.copyright(msg.copyright)
			elif type(msg) == MidiEvents.LyricEvent:         track_obj.lyric(curpos, msg.lyric)
			elif type(msg) == MidiEvents.KeySignatureEvent:  pass
			elif type(msg) == MidiEvents.EndOfTrackEvent:    break

class input_midi(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def getshortname(self): return 'midi'
	def gettype(self): return 'rm'
	def getdawinfo(self, dawinfo_obj): 
		dawinfo_obj.name = 'MIDI'
		dawinfo_obj.file_ext = 'mid'
		dawinfo_obj.fxtype = 'rack'
		dawinfo_obj.fxrack_params = ['vol','pan','pitch']
		dawinfo_obj.auto_types = ['nopl_ticks']
		dawinfo_obj.track_nopl = True
		dawinfo_obj.plugin_included = ['midi']
	def supported_autodetect(self): return True
	def detect(self, input_file):
		bytestream = open(input_file, 'rb')
		bytestream.seek(0)
		bytesdata = bytestream.read(4)
		if bytesdata == b'MThd': return True
		else: return False
	def parse(self, convproj_obj, input_file, dv_config):
		convproj_obj.type = 'rm'

		midiread_obj = reader_midifile_class()

		numchans, ppq, song_obj = midiread_obj.do_song(input_file)
		logger_input.info('PPQ: ' + str(ppq))
		convproj_obj.set_timings(ppq, False)

		logger_input.info('Auto Pitch: '+str(song_obj.auto_pitch.num_parts))
		#logger_input.info('Auto Ctrls: '+str(song_obj.old_auto_chan.num_parts))
		logger_input.info('Auto Inst: '+str(song_obj.insts.num_parts))
		logger_input.info('Auto TimeSig: '+str(song_obj.auto_timesig.num_parts))
		logger_input.info('Auto BPM: '+str(song_obj.auto_bpm.num_parts))

		song_obj.postprocess()
		song_obj.to_cvpj(convproj_obj)

		convproj_obj.do_actions.append('do_addloop')
		convproj_obj.do_actions.append('do_singlenotelistcut')
		#convproj_obj.do_actions.append('do_sorttracks')

