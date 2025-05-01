# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import os.path
import bisect
from objects import globalstore
from objects.convproj import fileref

class input_acid_3(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'sf_acid_3'
	
	def get_name(self):
		return 'Sonic Foundry ACID 3.0'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['projtype'] = 'r'
		in_dict['audio_filetypes'] = ['wav']
		in_dict['placement_loop'] = ['loop', 'loop_off', 'loop_adv', 'loop_adv_off']
		in_dict['fxtype'] = 'groupreturn'
		in_dict['audio_stretch'] = ['rate']
		in_dict['auto_types'] = ['pl_points','nopl_ticks']
		in_dict['notes_midi'] = True

	def parse(self, convproj_obj, dawvert_intent):
		from objects import colors
		from objects.file_proj_past import new_acid

		convproj_obj.type = 'r'
		convproj_obj.fxtype = 'groupreturn'

		project_obj = new_acid.sony_acid_song()
		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		globalstore.dataset.load('sony_acid', './data_main/dataset/sony_acid.dset')
		colordata = colors.colorset.from_dataset('sony_acid', 'track', 'acid_4')
		
		tempo = 120

		files = {}
		filecount = 0
		tracknum = -1

		for root_chunk, root_name in project_obj.root.iter_wtypes():
			if root_name == 'MainData':
				def_data = root_chunk.def_data
				tempo = def_data.tempo
				convproj_obj.params.add('bpm', tempo, 'float')
				convproj_obj.timesig = [def_data.timesig_num, def_data.timesig_denom]

				ppq = def_data.ppq
				convproj_obj.set_timings(ppq, False)

			elif root_name == 'Group:RegionDatas':
				for regs_chunk, regs_name in root_chunk.iter_wtypes():
					if regs_name == 'RegionData':
						def_data = regs_chunk.def_data
						files[filecount] = def_data.filename
						filecount += 1

			elif root_name == 'Group:TrackList':
				for trks_chunk, trks_name in root_chunk.iter_wtypes():

					if trks_name == 'Group:Track':
						tracknum += 1

						track_header = None
						track_audioinfo = None
						track_audiostretch = None
						track_regions = []

						for track_chunk, track_name in trks_chunk.iter_wtypes():

							if track_chunk.is_list:
								if track_name == 'Group:AudioInfo': 
									for trackg_chunk, trackg_name in track_chunk.iter_wtypes():
										if trackg_name == 'TrackAudioInfo':
											track_audioinfo = trackg_chunk.def_data

								if track_name == 'Group:AudioStretch': 
									for trackg_chunk, trackg_name in track_chunk.iter_wtypes():
										if trackg_name == 'Group:AudioStretch':
											track_audiostretch = trackg_chunk.def_data

								if track_name == 'TrackData': 
									for trackg_chunk, trackg_name in track_chunk.iter_wtypes():
										if trackg_name == 'Group:Regions':
											for reg_chunk, reg_name in trackg_chunk.iter_wtypes():
												if reg_name == 'TrackRegion':
													track_regions.append(reg_chunk.def_data)

							else:
								if track_name == 'TrackData':
									track_header = track_chunk.def_data

						if track_header:
							if track_header.type == 2:
								cvpj_trackid = 'track_'+str(track_header.id)
								track_obj = convproj_obj.track__add(cvpj_trackid, 'audio', 1, False)
								color = colordata.getcolornum(track_header.color)
								track_obj.visual.name = track_header.name
								track_obj.visual.color.set_int(color)
								if track_audioinfo:
									track_obj.params.add('vol', track_audioinfo.vol, 'float')
									track_obj.params.add('pan', track_audioinfo.pan, 'float')

								if track_regions and track_audiostretch:
									stretch_type = track_header.stretchtype
									track_root_note = track_audiostretch.root_note
									filename = track_header.filename
									num_beats = track_audiostretch.downbeat_offset
									seconds = track_header.seconds
	
									mul1 = track_audiostretch.tempo/120 if track_audiostretch.tempo else 1
									mul2 = num_beats/(seconds*2)
	
									samplemul = mul2
	
									sample_beats = num_beats
	
									sampleref_obj = convproj_obj.sampleref__add(filename, filename, 'win')
									sampleref_obj.search_local(dawvert_intent.input_folder)
	
									for region in track_regions:
	
										#offset = (int(region.offset/mul2)/5000000)*ppq
	
										outsize = region.size
	
										placement_obj = track_obj.placements.add_audio()

										if stretch_type == 0:
											time_obj = placement_obj.time
											time_obj.set_posdur(region.pos, outsize)
											time_obj.set_loop_data(0, 0, sample_beats*ppq)
											sp_obj = placement_obj.sample 
											sp_obj.sampleref = filename
											sp_obj.stretch.set_rate_tempo(tempo, samplemul, True)
											sp_obj.stretch.preserve_pitch = True
											sp_obj.pitch = region.pitch

										if stretch_type == 1:
											ssize = (int(region.size)/5000000)*ppq
											time_obj = placement_obj.time
											time_obj.set_posdur(region.pos, ssize)
											sp_obj = placement_obj.sample 
											sp_obj.sampleref = filename

										if stretch_type == 2:
											time_obj = placement_obj.time
											time_obj.set_posdur(region.pos, outsize)
											sp_obj = placement_obj.sample 
											sp_obj.sampleref = filename
											sp_obj.stretch.set_rate_tempo(tempo, mul1, True)
											sp_obj.pitch = region.pitch

							if track_header.type == 4:
								cvpj_trackid = 'track_'+str(track_header.id)
								track_obj = convproj_obj.track__add(cvpj_trackid, 'instruments', 1, False)
								color = colordata.getcolornum(track_header.color)
								track_obj.visual.name = track_header.name
								track_obj.visual.color.set_int(color)

								if track_regions:
									filename_obj = fileref.cvpj_fileref()
									filename_obj.set_path('win', track_header.filename, True)
									filename_obj.search_local(dawvert_intent.input_folder)
									filename = filename_obj.get_path('win', False)

									for region in track_regions:
	
										outsize = region.size
	
										placement_obj = track_obj.placements.add_midi()

										time_obj = placement_obj.time
										time_obj.set_posdur(region.pos, outsize)

										placement_obj.midi_from(filename)

										midievents_obj = placement_obj.midievents
										midievents_obj.sort()

										maxdur = (midievents_obj.get_dur()/midievents_obj.ppq)*ppq

										if maxdur>0:
											time_obj.set_loop_data(region.offset, 0, maxdur)

