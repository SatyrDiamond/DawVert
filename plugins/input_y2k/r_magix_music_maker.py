# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
from objects import globalstore
import os

class input_old_magix_maker(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'magix_old'
	
	def get_name(self):
		return 'Magix Music Maker'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['file_ext'] = ['mmm']
		in_dict['projtype'] = 'r'
		in_dict['placement_loop'] = ['loop', 'loop_off']
		in_dict['audio_stretch'] = ['rate']
		in_dict['track_hybrid'] = True

	def parse(self, convproj_obj, dawvert_intent):
		from objects import colors
		from objects.file_proj_past import magix_music_maker

		convproj_obj.type = 'r'

		project_obj = magix_music_maker.root_group()
		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		sample_time = 44100//2
		sample_rate = 44100

		tempomul = 1

		tempo = 120
		data_proi = project_obj.data_proi
		if data_proi is not None:
			tempo = data_proi.tempo
			convproj_obj.params.add('bpm', tempo, 'float')
			convproj_obj.timesig = [data_proi.timeisg_num, data_proi.timeisg_denom]
			#sample_time = data_proi.sample_rate
			sample_rate = data_proi.sample_rate
			tempomul = 120/data_proi.tempo

		convproj_obj.set_timings(sample_time*tempomul, True)

		sampleref_objs = {}
		videoref_objs = {}
		data_phys = project_obj.data_phys
		if data_phys is not None:
			for n, x in enumerate(data_phys.files):
				sampleid = 'sample_'+str(n)
				joinedpath = '\\'.join([x.file, x.file2])

				if '.' in x.file2:
					fileext = x.file2.rsplit('.', 1)[1].lower()
					if fileext == 'wav':
						sampleref_obj = convproj_obj.sampleref__add(sampleid, joinedpath, 'win')
						sampleref_obj.search_local(dawvert_intent.input_folder)
						sampleref_obj.set_fileformat(fileext)
						sampleref_objs[n] = sampleref_obj
					if fileext == 'avi':
						videoref_obj = convproj_obj.videoref__add(sampleid, joinedpath, 'win')
						videoref_obj.search_local(dawvert_intent.input_folder)
						videoref_objs[n] = videoref_obj
				elif '.' in x.video:
					fileext = x.video.rsplit('.', 1)[1].lower()
					joinedpath = '\\'.join([x.folder, x.video])
					if fileext == 'avi':
						videoref_obj = convproj_obj.videoref__add(sampleid, joinedpath, 'win')
						videoref_obj.search_local(dawvert_intent.input_folder)
						videoref_objs[n] = videoref_obj


		data_trks = project_obj.data_trks
		if data_trks is not None:
			for tracknum, mmm_track in enumerate(data_trks.data_trck):
				trackid = str(tracknum)
				track_obj = convproj_obj.track__add(trackid, 'hybrid', 1, False)

				data_trci = mmm_track.data_trci
				if data_trci is not None:
					track_obj.visual.name = data_trci.name
					track_obj.params.add('pan', data_trci.pan, 'float')
					track_obj.params.add('vol', max(0, data_trci.vol), 'float')
				
				totalcolors = []
				uniquecolors = {}

				for obj in mmm_track.data_objs:
					data_objc = obj.data_objc
					if data_objc is not None:

						if data_objc.fileid in sampleref_objs:
							placement_obj = track_obj.placements.add_audio()
							color = list(data_objc.bg_color[0:3])
							placement_obj.visual.name = data_objc.name
							placement_obj.visual.color.set_int(color)
							placement_obj.time.set_startend(data_objc.start, data_objc.end)
							placement_obj.fade_in.set_dur((data_objc.fade_in/sample_time), 'beats')
							placement_obj.fade_out.set_dur((data_objc.fade_out/sample_time), 'beats')
							placement_obj.group = str(data_objc.group) if data_objc.group else None
	
							if color not in totalcolors: 
								uniquecolors[len(totalcolors)] = 0
								totalcolors.append(color)
							uniquecolors[totalcolors.index(color)] += 1
	
							if data_objc.loop_end: 
								placement_obj.time.set_loop_data(data_objc.offset, 0, data_objc.loop_end)

							sampleref_obj = sampleref_objs[data_objc.fileid]
	
							samp_hz = sampleref_obj.get_hz()
							hzspeed = samp_hz/sample_rate if samp_hz else 1
	
							sample_obj = placement_obj.sample
							sample_obj.sampleref = 'sample_'+str(data_objc.fileid)
							sample_obj.vol = data_objc.vol/65535
							sample_obj.pitch = data_objc.pitch
							if data_objc.speed:
								sample_obj.stretch.set_rate_speed(tempo, data_objc.speed/hzspeed, False)
								sample_obj.stretch.uses_tempo = True
								sample_obj.stretch.algorithm = 'stretch'
								sample_obj.stretch.preserve_pitch = True

						if data_objc.fileid in videoref_objs:
							placement_obj = track_obj.placements.add_video()
							color = list(data_objc.bg_color[0:3])
							placement_obj.visual.name = data_objc.name
							placement_obj.visual.color.set_int(color)
							placement_obj.time.set_startend(data_objc.start, data_objc.end)
							placement_obj.fade_in.set_dur((data_objc.fade_in/sample_time), 'beats')
							placement_obj.fade_out.set_dur((data_objc.fade_out/sample_time), 'beats')
							placement_obj.videoref = 'sample_'+str(data_objc.fileid)

							if color not in totalcolors: 
								uniquecolors[len(totalcolors)] = 0
								totalcolors.append(color)
							uniquecolors[totalcolors.index(color)] += 1
	
						#print(color)

				if uniquecolors:
					trackcolor = totalcolors[max(uniquecolors, key=lambda k: uniquecolors.get(k))]
					track_obj.visual.color.set_int(trackcolor)

				track_obj.placements.pl_audio.sort()
				track_obj.placements.pl_audio.remove_overlaps()
		#self.loop_end = 0