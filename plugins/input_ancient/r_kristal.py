# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import xml.etree.ElementTree as ET
import plugins
from objects import globalstore
from objects import colors

class input_kristal(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'kristal'
	
	def get_name(self):
		return 'KRISTAL Audio Engine'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['file_ext'] = ['kristal']
		in_dict['audio_filetypes'] = ['wav']
		in_dict['projtype'] = 'r'
		in_dict['audio_nested'] = True

	def get_detect_info(self, detectdef_obj):
		detectdef_obj.headers.append([0, b'Crys'])

	def do_audiopart(self, convproj_obj, placement_obj, part, minpos):
		placement_obj.time.set_posdur(part.position-minpos, part.duration)
		placement_obj.time.set_offset(part.offset)
		placement_obj.visual.name = part.name
		placement_obj.visual.color.set_int(part.color[0:3])
		placement_obj.fade_in.set_dur(part.fade_in/44100, 'seconds')
		placement_obj.fade_out.set_dur(part.fade_out/44100, 'seconds')

		sp_obj = placement_obj.sample
		sp_obj.vol = part.volume
		sp_obj.stretch.set_rate_tempo(120, 1, False)
		sp_obj.stretch.preserve_pitch = True
		sp_obj.stretch.algorithm = 'stretch'
		if part.path:
			if part.path[0] == 'CPath':
				filepath = part.path[1].path
				sampleref_obj = convproj_obj.sampleref__add(filepath, filepath, 'win')
				sp_obj.sampleref = filepath

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj import kristal as proj_kristal
		from objects import audio_data

		convproj_obj.type = 'r'
		convproj_obj.set_timings(44100/2, True)

		project_obj = proj_kristal.kristal_song()
		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		tracknum = 0
		tracknums = {}

		if project_obj.audio_input:
			inum, indata = project_obj.audio_input
			for inp in indata:
				if inp.type == b'Plug' and inp.name == 'Waver.cin':
					if inp.chunkdata:
						if inp.chunkdata[0] == 'CCrystalInput':
							for ch_track, ch_data in inp.chunkdata[1].tracks:
								if ch_track=='CAudioTrack':
									cvpj_trackid = 'track_'+str(tracknum)
									track_obj = convproj_obj.track__add(cvpj_trackid, 'audio', 1, False)
									tracknums[tracknum] = track_obj
									track_obj.visual.name = ch_data.name
									for cid, part in ch_data.parts:
										if cid == 'CAudioPart': 
											placement_obj = track_obj.placements.add_nested_audio()
											placement_obj.time.set_posdur(part.position, part.duration)
											placement_obj.visual.name = part.name
											placement_obj.visual.color.set_int(part.color[0:3])
											placement_obj = placement_obj.add()
											self.do_audiopart(convproj_obj, placement_obj, part, part.position)
										if cid == 'CFolderPart': 
											placement_obj = track_obj.placements.add_nested_audio()
											placement_obj.time.set_posdur(part.position, part.duration)
											placement_obj.time.set_offset(part.offset)
											placement_obj.visual.name = part.name
											placement_obj.visual.color.set_int(part.color[0:3])
											for icid, inpart in part.parts:
												if icid == 'CAudioPart': 
													npa_obj = placement_obj.add()
													self.do_audiopart(convproj_obj, npa_obj, inpart, part.position)

									tracknum += 1

		channum = 0
		if project_obj.globalinserts:
			for icid, inpart in project_obj.globalinserts:
				if icid == 'CMixerChannel':
					if channum in tracknums:
						track_obj = tracknums[channum]
						track_obj.params.add('enabled', not bool(inpart.muted), 'bool')
						track_obj.params.add('solo', bool(inpart.solo), 'bool')
						track_obj.params.add('vol', inpart.vol, 'float')
						track_obj.params.add('pan', (inpart.pan-0.5)*2, 'float')
					channum += 1