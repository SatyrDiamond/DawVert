# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import json
from objects.songinput import midi_in
from objects_midi.parser import MidiFile
from objects_midi import events

import logging
logger_input = logging.getLogger('input')

def do_track(miditrack, track_obj, song_obj):
	curpos = 0
	for msg in miditrack:
		curpos += msg.deltaTime
		if type(msg) == events.NoteOnEvent:
			if msg.velocity != 0: track_obj.note_on(curpos, msg.channel, msg.note, msg.velocity)
			else: track_obj.note_off(curpos, msg.channel, msg.note)

		elif type(msg) == events.NoteOffEvent: 
			track_obj.note_off(curpos, msg.channel, msg.note)

		elif type(msg) == events.TrackNameEvent: 
			track_obj.track_name = msg.name

		#elif type(msg) == events.MidiPortEvent: 
		#	track_obj.portnum(msg.port)

		elif type(msg) == events.PitchBendEvent:
			track_obj.pitchwheel(curpos, msg.channel, msg.pitch)

		elif type(msg) == events.ControllerEvent:
			track_obj.control_change(curpos, msg.channel, msg.controller, msg.value)

		elif type(msg) == events.ProgramEvent:
			track_obj.program_change(curpos, msg.channel, msg.program)

		elif type(msg) == events.TempoEvent:
			track_obj.set_tempo(curpos, 60000000/msg.tempo)

		elif type(msg) == events.TimeSignatureEvent:
			track_obj.time_signature(curpos, msg.numerator, msg.denominator)

		elif type(msg) == events.TextEvent:
			track_obj.text(curpos, msg.text)

		elif type(msg) == events.MarkerEvent:
			track_obj.marker(curpos, msg.marker)

		elif type(msg) == events.SequencerEvent:
			track_obj.sequencer_specific(msg.data)

		elif type(msg) == events.SysExEvent:
			track_obj.sysex(curpos, msg.data)

		elif type(msg) == events.CopyrightEvent:
			track_obj.copyright(msg.copyright)

		elif type(msg) == events.LyricEvent:
			track_obj.lyric(curpos, msg.lyric)

		elif type(msg) == events.KeySignatureEvent:
			pass

		elif type(msg) == events.EndOfTrackEvent: 
			break

		#else:
		#	print(msg)

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
		midifile = MidiFile.fromFile(input_file)

		ppq = midifile.ppqn
		logger_input.info('PPQ: ' + str(ppq))
		convproj_obj.type = 'rm'
		convproj_obj.set_timings(ppq, False)

		song_obj = midi_in.midi_song(16, ppq, 120, [4,4])

		for n, miditrack in enumerate(midifile.tracks):
			logger_input.info('Track '+str(n+1)+' of '+str(len(midifile.tracks)))
			track_obj = song_obj.create_track(len(miditrack.events))
			do_track(miditrack.events, track_obj, song_obj)

		logger_input.info('Auto Pitch: '+str(song_obj.auto_pitch.num_parts))
		logger_input.info('Auto Ctrls: '+str(song_obj.auto_chan.num_parts))
		logger_input.info('Auto Inst: '+str(song_obj.insts.num_parts))
		logger_input.info('Auto TimeSig: '+str(song_obj.auto_timesig.num_parts))
		logger_input.info('Auto BPM: '+str(song_obj.auto_bpm.num_parts))

		song_obj.postprocess()
		song_obj.to_cvpj(convproj_obj)

		convproj_obj.do_actions.append('do_addloop')
		convproj_obj.do_actions.append('do_singlenotelistcut')
		#convproj_obj.do_actions.append('do_sorttracks')

