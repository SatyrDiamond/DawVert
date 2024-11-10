# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import note_data
from functions import value_midi
import xml.etree.ElementTree as ET
import plugins
import json

class input_cvpj_f(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def get_shortname(self): return 'temper'
	def get_name(self): return 'Temper'
	def get_priority(self): return 0
	def get_prop(self, in_dict): 
		in_dict['audio_filetypes'] = ['wav']
		in_dict['auto_types'] = ['pl_points']
		in_dict['projtype'] = 'r'
	def supported_autodetect(self): return True
	def detect(self, input_file):
		output = False
		try:
			tree = ET.parse(input_file)
			root = tree.getroot()
			if root.tag == "music-sequence": output = True
		except ET.ParseError: output = False
		return output
	def parse(self, convproj_obj, input_file, dv_config):
		from objects.file_proj import proj_temper

		convproj_obj.type = 'r'
		convproj_obj.set_timings(6716, False)

		project_obj = proj_temper.temper_song()
		if not project_obj.load_from_file(input_file): exit()

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
			if tmp_track.phrases:
				track_obj = convproj_obj.track__add(cvpj_trackid, 'instrument', 1, False)
				track_obj.params.add('vol', 1, 'float')
				track_obj.params.add('pan', 0, 'float')
				if tmp_track.customname: track_obj.visual.name = tmp_track.customname
				else: track_obj.visual.name = tmp_track.name
				track_obj.visual.color.set_float([0.66, 0.66, 0.73])
				curpos = 0
				for phrase in tmp_track.phrases:
					curpos += phrase.td
					phraseauto = {}
					placement_obj = track_obj.placements.add_notes()
					placement_obj.time.set_posdur(curpos, phrase.d)
					ncurpos = 0
					for event in phrase.events:
						ncurpos += event.td
						if isinstance(event, proj_temper.event_note):
							placement_obj.notelist.add_r(ncurpos, event.d, note_data.text_to_note(event.p)+24, event.v/127, {})
						if isinstance(event, proj_temper.event_control):
							if event.n not in phraseauto: phraseauto[event.n] = []
							phraseauto[event.n].append([ncurpos, event])

					for pa_c, pc_d in phraseauto.items():
						midiautoinfo = value_midi.get_cc_info(pa_c)
						autoloc = midiautoinfo.get_autoloc_track(cvpj_trackid)

						if autoloc:
							autopl_obj = convproj_obj.automation.add_pl_points(autoloc, 'float')
							autopl_obj.time.set_posdur(curpos, phrase.d)
							prev_i = 1
							for p_pos, p_val in pc_d:
								autopoint_obj = autopl_obj.data.add_point()
								autopoint_obj.pos = p_pos
								autopoint_obj.value = ((p_val.v/127)+midiautoinfo.math_add)*midiautoinfo.math_mul
								autopoint_obj.type = 'instant' if prev_i else 'normal'
								prev_i = p_val.ct



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
