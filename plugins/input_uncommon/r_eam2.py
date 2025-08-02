# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import struct
from functions import xtramath

def conv_color(b_color):
	color = b_color.to_bytes(4, "little")
	return [color[0],color[1],color[2]]

class input_eam2(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'eam2'
	
	def get_name(self):
		return 'easy audio mixer 2'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['projtype'] = 'r'

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj_uncommon import easy_audio_mixer as proj_easy_audio_mixer
		from objects import colors
		from objects.convproj import fileref

		convproj_obj.type = 'r'
		convproj_obj.fxtype = 'none'
		convproj_obj.set_timings(48)

		traits_obj = convproj_obj.traits
		traits_obj.auto_types = ['nopl_points']
		traits_obj.time_seconds = True

		project_obj = proj_easy_audio_mixer.easyamixr_proj()
		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()
		
		if project_obj.Format == 'EAMFormat01':
			eamproj = project_obj.EAMFormat1

			convproj_obj.params.add('bpm', eamproj.BPM, 'float')
			tempomul = 120/eamproj.BPM

			for track in eamproj.AudioChannelsList:
				cvpj_trackid = str(track.ID)

				if track.Type != 'Main':
					autoloc_s = ['track', cvpj_trackid]
					track_obj = convproj_obj.track__add(cvpj_trackid, 'audio', 1, False)
				else:
					autoloc_s = ['master']
					track_obj = convproj_obj.track_master

				color = conv_color(struct.unpack('I', struct.pack('i', track.EventsColorRGB))[0])
				track_obj.visual.name = track.Name
				track_obj.visual.color.set_int(color)

				track_obj.params.add('vol', xtramath.from_db(track.Volume), 'float')
				track_obj.params.add('pan', track.Pan, 'float')
				track_obj.params.add('enabled', not track.Muted, 'bool')
				track_obj.params.add('solo', track.Solo, 'bool')

				for autop in track.AutomationList:
					autoloc_e = None
					if autop.AutomationType == 'Pan':
						autoloc = autoloc_s+['pan']
						auto_obj = convproj_obj.automation.create(autoloc, 'float', True)
						auto_obj.is_seconds = True
						for p in autop.Points:
							if p.BeatN>=0: auto_obj.add_autopoint(p.BeatN, (p.Value-0.5)*2, None)

					if autop.AutomationType == 'Volume':
						autoloc = autoloc_s+['vol']
						auto_obj = convproj_obj.automation.create(autoloc, 'float', True)
						auto_obj.is_seconds = True
						for p in autop.Points:
							if p.BeatN>=0: auto_obj.add_autopoint(p.BeatN, p.Value, None)

				for event in track.EventsList:
					startsample_sec = (event.StartSampleMS)/1000
					endsample_sec = (event.EndSampleMS)/1000
					pos_sec = event.BeatPos
					filepath = event.FilePath

					placement_obj = track_obj.placements.add_audio()
					placement_obj.fade_in.set_dur(event.FadeIN_LengthBeats, 'seconds')
					placement_obj.fade_out.set_dur(event.FadeOUT_LengthBeats, 'seconds')
					placement_obj.muted = event.Muted
					placement_obj.sample.vol = xtramath.from_db(event.Gain)
					if event.Title: placement_obj.visual.name = event.Title

					time_obj = placement_obj.time
					time_obj.set_posdur_real(pos_sec, endsample_sec-startsample_sec)
					time_obj.set_offset_real(startsample_sec)

					sp_obj = placement_obj.sample
					sampleref_obj = convproj_obj.sampleref__add(filepath, filepath, None)
					sampleref_obj.search_local(dawvert_intent.input_folder)
					sp_obj.sampleref = filepath
