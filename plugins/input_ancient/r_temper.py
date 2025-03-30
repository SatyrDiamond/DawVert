# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import note_data
from functions import value_midi
import xml.etree.ElementTree as ET
import plugins
import json

class input_cvpj_f(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'temper'
	
	def get_name(self):
		return 'Temper'
	
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
		from objects.file_proj_past import temper as proj_temper
		convproj_obj.fxtype = 'rack'
		convproj_obj.type = 'cm'

		convproj_obj.set_timings(6716, False)

		project_obj = proj_temper.temper_song()
		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		curpos = 0
		for metaevent in project_obj.meta_track:
			curpos += metaevent.td

			if isinstance(metaevent, proj_temper.metaevent_bpm):
				if not curpos: convproj_obj.params.add('bpm', metaevent.bpm, 'float')
				convproj_obj.automation.add_autopoint(['main', 'bpm'], 'float', curpos, metaevent.bpm, 'normal')

			if isinstance(metaevent, proj_temper.metaevent_meter):
				if not curpos: convproj_obj.timesig = [metaevent.beats, metaevent.beat_value]
				convproj_obj.timesig_auto.add_point(curpos, [metaevent.beats, metaevent.beat_value])

		for tracknum, tmp_track in enumerate(project_obj.track):
			cvpj_trackid = 'track_'+str(tracknum)
			track_obj = convproj_obj.track__add(cvpj_trackid, 'midi', 1, False)

			if tmp_track.customname: track_obj.visual.name = tmp_track.customname
			else: track_obj.visual.name = tmp_track.name

			track_obj.visual.color.set_float([0.66, 0.66, 0.73])

			if tmp_track.phrases:
				channel = tmp_track.channel

				print(channel)

				curpos = 0
				for phrase in tmp_track.phrases:
					curpos += phrase.td
					phraseauto = {}
					placement_obj = track_obj.placements.add_midi()
					placement_obj.time.set_posdur(curpos, phrase.d)

					midievents_obj = placement_obj.midievents

					ncurpos = 0
					for event in phrase.events:
						ncurpos += event.td
						if isinstance(event, proj_temper.event_note):
							note = note_data.text_to_note(event.p)+24
							midievents_obj.add_note_dur(ncurpos, channel, note+60, event.v, event.d)
						elif isinstance(event, proj_temper.event_control):
							midievents_obj.add_control(ncurpos, channel, event.n, int(event.v))
						elif isinstance(event, proj_temper.event_patch):
							midievents_obj.add_program(ncurpos, channel, event.v)
						#else:
						#	print(event)

			elif tmp_track.audios:
				track_obj = convproj_obj.track__add(str(tracknum), 'audio', 1, False)
				if tmp_track.customname: track_obj.visual.name = tmp_track.customname
				else: track_obj.visual.name = tmp_track.name
				track_obj.visual.color.set_float([0.66, 0.73, 0.66])
				curpos = 0
				for audio in tmp_track.audios:
					curpos += audio.td
					placement_obj = track_obj.placements.add_audio()
					placement_obj.time.set_posdur(curpos, audio.end)
					convproj_obj.sampleref__add(audio.file, audio.file)
					sp_obj = placement_obj.sample
					sp_obj.sampleref = audio.file
