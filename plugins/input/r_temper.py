# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import note_data
import xml.etree.ElementTree as ET
from objects.file_proj import proj_temper
import plugins
import json

class input_cvpj_f(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def getshortname(self): return 'temper'
	def gettype(self): return 'r'
	def getdawinfo(self, dawinfo_obj): 
		dawinfo_obj.name = 'Temper'
		dawinfo_obj.file_ext = ''
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
		convproj_obj.type = 'r'
		convproj_obj.set_timings(6716, False)

		project_obj = proj_temper.temper_song()
		project_obj.load_from_file(input_file)

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
				track_obj = convproj_obj.add_track(str(tracknum), 'instrument', 1, False)
				if tmp_track.customname: track_obj.visual.name = tmp_track.customname
				else: track_obj.visual.name = tmp_track.name
				track_obj.visual.color.set_float([0.66, 0.66, 0.73])
				curpos = 0
				for phrase in tmp_track.phrases:
					curpos += phrase.td
					placement_obj = track_obj.placements.add_notes()
					placement_obj.position = curpos
					placement_obj.duration = phrase.d
					ncurpos = 0
					for event in phrase.events:
						ncurpos += event.td
						if isinstance(event, proj_temper.event_note):
							placement_obj.notelist.add_r(ncurpos, event.d, note_data.text_to_note(event.p), event.v/127, {})

			elif tmp_track.audios:
				track_obj = convproj_obj.add_track(str(tracknum), 'audio', 1, False)
				if tmp_track.customname: track_obj.visual.name = tmp_track.customname
				else: track_obj.visual.name = tmp_track.name
				track_obj.visual.color.set_float([0.66, 0.73, 0.66])
				curpos = 0
				for audio in tmp_track.audios:
					curpos += audio.td
					placement_obj = track_obj.placements.add_audio()
					placement_obj.position = curpos
					placement_obj.duration = audio.end
					convproj_obj.add_sampleref(audio.file, audio.file)
					sp_obj = placement_obj.sample
					sp_obj.sampleref = audio.file



