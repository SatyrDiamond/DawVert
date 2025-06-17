# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import math
import os
import numpy as np

def get_timebase(i_val):
	if i_val == 2: return 0.004
	if i_val == 3: return 0.005
	if i_val == 16: return 0.010
	if i_val == 17: return 0.020
	if i_val == 18: return 0.040
	if i_val == 19: return 0.050
	
class input_mmf(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'mmf'
	
	def get_name(self):
		return 'Mobile Music File'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['plugin_included'] = ['universal:midi']
		in_dict['projtype'] = 'cm'

	def parse(self, convproj_obj, dawvert_intent):
		from objects import audio_data
		from objects.file_proj_past import mmf as proj_mmf

		convproj_obj.fxtype = 'rack'
		convproj_obj.type = 'cm'

		traits_obj = convproj_obj.traits
		traits_obj.fxrack_params = ['vol','pan','pitch']
		traits_obj.auto_types = ['nopl_ticks']
		traits_obj.track_nopl = True
		traits_obj.audio_filetypes = ['wav']

		project_obj = proj_mmf.smaf_song()

		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		convproj_obj.params.add('bpm', 120, 'float')

		samplefolder = dawvert_intent.path_samples['extracted']

		firstma2 = False
		#if True in [isinstance(x, proj_mmf.smaf_track_ma2) for x in project_obj.tracks2]:

			#for grpnum, track in enumerate(project_obj.tracks2):
			#	if track:
			#		timebase = get_timebase(track.timebase_dur)
			#		realtime = int(timebase*(math.pi*10000))
			#		if not firstma2: 
			#			song_obj = midi_in.midi_song(16, realtime, 120, [4,4])
			#			track_obj = song_obj.create_track(len(track.sequence))
			#			firstma2 = True
			#		
			#			track_obj.track_name = 'MA2 #'+str(grpnum)
#
			#		curpos = 0
			#		for msg in track.sequence:
			#			curpos += msg.resttime
#
			#			channel = msg.channel+(grpnum*4)
#
			#			if msg.event_type == 'note':
			#				track_obj.note_dur(curpos, channel, msg.note_key+36+(msg.note_oct*12), 100, msg.duration)
#
			#			elif msg.event_type == 'program':
			#				track_obj.program_change(curpos, channel, msg.value)
#
			#			elif msg.event_type == 'bank':
			#				track_obj.control_change(curpos, channel, 0, msg.value)
#
			#			elif msg.event_type == 'volume':
			#				track_obj.control_change(curpos, channel, 7, msg.value)
#
			#			elif msg.event_type == 'pan':
			#				track_obj.control_change(curpos, channel, 10, msg.value)
#
			#			elif msg.event_type == 'expression':
			#				track_obj.control_change(curpos, channel, 11, msg.value)
#
			#			else:
			#				print(msg.event_type)
#
			#song_obj.postprocess()
			#song_obj.to_cvpj(convproj_obj)

		for n, track in enumerate(project_obj.tracks3):
			if track is not None:
				timebase = get_timebase(track.timebase_dur)
				realtime = int(timebase*(math.pi*10000))

				midippq = 960
				convproj_obj.set_timings(int(midippq*realtime))
				track_obj = convproj_obj.track__add(str(n), 'midi', 1, False)

				curpos = 0
				if track.sequence is not None:
					events_obj = track_obj.placements.midievents
					events_obj.has_duration = True

					for event in track.sequence:
						curpos += event[0]*midippq
	
						if event[1] == 8:
							events_obj.add_note_dur(curpos, event[2], event[3], 127, event[4]*midippq)
						elif event[1] == 9:
							events_obj.add_note_dur(curpos, event[2], event[3], event[4], event[5]*midippq)
						elif event[1] == 11:
							events_obj.add_control(curpos, event[2], event[3], event[4])
						elif event[1] == 12:
							events_obj.add_program(curpos, event[2], event[3])
						elif event[1] == 14:
							events_obj.add_pitch(curpos, event[2], event[3])

					used_notes = events_obj.get_used_notes()
					used_drums = used_notes[used_notes['chan']==9]
					used_drums = used_drums[used_drums['value']<16]
					
					used_drumnums = np.unique(used_drums['value'])
					for used_drumnum in used_drumnums:
						drumnotes = used_drums[used_drums['value']==used_drumnum]

						drumtrackid = '%i_drum_%i' % (n, used_drumnum)
						track_obj = convproj_obj.track__add(drumtrackid, 'audio', 1, False)
						track_obj.visual.name = 'Track #%i MA-3 Stream #%i' % (n+1, used_drumnum)
						track_obj.visual.color.set_int([30,30,30])
	
						sampleid = 'snd_%i_%i' % (n, used_drumnum+1)
	
						for start, end, _, _, vol in drumnotes:
							placement_obj = track_obj.placements.add_audio()
							placement_obj.sample.sampleref = sampleid
							placement_obj.sample.vol = int(vol)/127
							placement_obj.visual.name = 'Stream #%i' % (used_drumnum)
							time_obj = placement_obj.time
							time_obj.set_posdur(int(start), int(end))
							sp_obj = placement_obj.sample
							sp_obj.stretch.timing.set__speed(1)
							sp_obj.stretch.preserve_pitch = True
							sp_obj.interpolation = "none"

				for soundnum, hzsnd in track.audio.items():
					hz, sounddata = hzsnd

					wav_path = samplefolder + 'snd_%i_%i.wav' % (n, soundnum)
					sampleid = 'snd_%i_%i' % (n, soundnum)
					audio_obj = audio_data.audio_obj()
					audio_obj.decode_from_codec('yamaha_aica', sounddata)
					audio_obj.rate = hz
					audio_obj.to_file_wav(wav_path)

					sampleref_obj = convproj_obj.sampleref__add(sampleid, wav_path, None)
					sampleref_obj.set_fileformat('wav')
					audio_obj.to_sampleref_obj(sampleref_obj)

		custinst_obj = convproj_obj.main__add_midi_custom_inst()
		custinst_obj.bank = 124
		custinst_obj.visual.name = 'MA-3 Voice $patch$'
		custinst_obj.visual.color.set_int([0,170,255])
		custinst_obj.pluginid = 'voice_$patch$'

		custinst_obj = convproj_obj.main__add_midi_custom_inst()
		custinst_obj.bank = 125
		custinst_obj.visual.name = 'MA-3 Drum/Stream $patch$'
		custinst_obj.visual.color.set_int([0,255,170])
		custinst_obj.pluginid = 'drum_$patch$'

		convproj_obj.params.add('bpm', 120, 'float')
