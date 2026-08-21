# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
from objects import globalstore
from functions import xtramath
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
		in_dict['projtype'] = 'r'

	def parse(self, convproj_obj, dawvert_intent):
		from objects import colors
		from objects.file_proj_past import magix_music_maker

		convproj_obj.type = 'r'
		convproj_obj.fxtype = 'groupreturn'

		traits_obj = convproj_obj.traits
		traits_obj.placement_loop = ['loop', 'loop_off']
		traits_obj.audio_stretch = ['rate']
		traits_obj.audio_filetypes = ['wav']
		traits_obj.track_hybrid = True

		project_obj = magix_music_maker.root_group()
		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		sample_time = 44100//2
		sample_rate = 44100

		tempomul = 1.0

		tempo = 120
		data_proi = project_obj.data_proi
		if data_proi is not None:
			tempo = data_proi.tempo
			convproj_obj.params.add('bpm', tempo, 'float')
			convproj_obj.timesig = [data_proi.timeisg_num, data_proi.timeisg_denom]
			#sample_time = data_proi.sample_rate
			sample_rate = data_proi.sample_rate
			tempomul = 120/data_proi.tempo

		convproj_obj.set_timings(sample_time*tempomul)

		sampleref_objs = {}
		videoref_objs = {}
		data_phys = project_obj.data_phys
		if data_phys is not None:
			for n, x in enumerate(data_phys.files):
				sampleid = 'sample_'+str(n)
				joinedpath = '\\'.join([x.file, x.file2])

				if '.' in x.file2:
					fileext = x.file2.rsplit('.', 1)[1].lower()
					if fileext.lower() in ['wav', 'ogg']:
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

		return_obj = convproj_obj.track_master.fx__return__add('aux1')
		return_obj.visual.name = 'FX '+str(1)

		return_obj = convproj_obj.track_master.fx__return__add('aux2')
		return_obj.visual.name = 'FX '+str(2)

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
					track_obj.params.add('enabled', 1 not in data_trci.flags, 'float')
					track_obj.sends.add('aux1', 'send_%i_aux1' % (tracknum), data_trci.aux1)
					track_obj.sends.add('aux2', 'send_%i_aux2' % (tracknum), data_trci.aux2)

				#totalcolors = []
				#uniquecolors = {}

				for obj in mmm_track.data_objs:
					data_objc = obj.data_objc
					data_AUFX = obj.data_AUFX

					if data_objc is not None:
						if data_objc.fileid in sampleref_objs:
							placement_obj = track_obj.placements.add_audio()
							time_obj = placement_obj.time

							placement_obj.visual.name = data_objc.name
							placement_obj.fade_in.set_dur((data_objc.fade_in/sample_time), 'beats')
							placement_obj.fade_out.set_dur((data_objc.fade_out/sample_time), 'beats')
							placement_obj.group = str(data_objc.group) if data_objc.group else None

							bg_color = list(data_objc.bg_color[0:3])
							placement_obj.visual.color.set_int(bg_color)
							fg_color = list(data_objc.fg_color[0:3])
							placement_obj.visual.altcolor_add('fg').set_int(fg_color)

							time_obj.set_startend(data_objc.start, data_objc.end)
							if data_objc.loop_end: time_obj.set_loop_data(data_objc.offset, 0, data_objc.loop_end)

							#if color not in totalcolors: 
							#	uniquecolors[len(totalcolors)] = 0
							#	totalcolors.append(color)
							#uniquecolors[totalcolors.index(color)] += 1
	
							sampleref_obj = sampleref_objs[data_objc.fileid]

							sample_obj = placement_obj.sample
							sample_obj.sampleref = 'sample_'+str(data_objc.fileid)
							sample_obj.vol = data_objc.vol/65535


							class sample_speedtemp:
								def __init__(self):
									self.sample_speed = 1
									self.sample_pitch = 0
									self.resample = False
									self.fx_found = False

							sample_stretch = sample_speedtemp()

							def do_fx(data_AFXE, sample_stretch):
								for x in data_AFXE:
									data_FXHD = x.data_FXHD
									if x.data_AFXD and data_FXHD:
										data_AFXD = x.data_AFXD

										if 1 not in data_FXHD.flags:
											if data_FXHD.fxtype in [148, 536871060]:
												sample_stretch.fx_found = True
												for param in data_AFXD.params:
													if param.paramnum==0:
														sample_stretch.sample_speed = param.val_current
													elif param.paramnum==1:
														sample_stretch.sample_pitch = param.val_current
											elif data_FXHD.fxtype in [149, 536871061]:
												for param in data_AFXD.params:
													if param.paramnum==0:
														sample_stretch.resample = True
														sample_stretch.sample_speed = param.val_current
											#else:
											#	print(data_FXHD.fxtype, [x.name for x in data_AFXD.params])

										if data_AFXD.data_AFXE:
											do_fx(data_AFXD.data_AFXE, sample_stretch)

							if data_AUFX:
								do_fx(data_AUFX.data_AFXE, sample_stretch)

							#print(sampleref_obj.fileref.get_path(None, False))

							if not sample_stretch.fx_found:
								samp_hz = sampleref_obj.get_hz()
								hzspeed = samp_hz/sample_rate if samp_hz else 1

								if data_objc.speed:
									sample_stretch.sample_speed = data_objc.speed/hzspeed
									sample_stretch.sample_pitch = data_objc.pitch

							sample_obj.pitch = sample_stretch.sample_pitch
							stretch_obj = sample_obj.stretch
							stretch_obj.timing.set__real_rate(tempo, sample_stretch.sample_speed)
							stretch_obj.preserve_pitch = not sample_stretch.resample

						if data_objc.fileid in videoref_objs:
							placement_obj = track_obj.placements.add_video()
							time_obj = placement_obj.time
							
							placement_obj.visual.name = data_objc.name

							bg_color = list(data_objc.bg_color[0:3])
							placement_obj.visual.color.set_int(bg_color)
							fg_color = list(data_objc.fg_color[0:3])
							placement_obj.visual.altcolor_add('fg').set_int(fg_color)

							time_obj.set_startend(data_objc.start, data_objc.end)
							if data_objc.loop_end: time_obj.set_loop_data(data_objc.offset, 0, data_objc.loop_end)

							placement_obj.fade_in.set_dur((data_objc.fade_in/sample_time), 'beats')
							placement_obj.fade_out.set_dur((data_objc.fade_out/sample_time), 'beats')
							placement_obj.videoref = 'sample_'+str(data_objc.fileid)

							#if color not in totalcolors: 
							#	uniquecolors[len(totalcolors)] = 0
							#	totalcolors.append(color)
							#uniquecolors[totalcolors.index(color)] += 1
	
						#print(color)

				autodata = {}
				for rubb in mmm_track.data_rubb:
					if rubb.param not in autodata: autodata[rubb.param] = {}
					autodata[rubb.param][rubb.pos] = rubb.val

				for paramnum, paramdata in autodata.items():
					autoloc = None
					v_min = 0
					v_max = 1
					if paramnum == 0: autoloc = ['track', trackid, 'vol']
					if paramnum == 30: 
						autoloc = ['track', trackid, 'pan']
						v_min = 1
						v_max = -1
					if paramnum == 4: autoloc = ['send', 'send_%i_aux1' % (tracknum), 'amount']
					if paramnum == 5: autoloc = ['send', 'send_%i_aux2' % (tracknum), 'amount']
					if autoloc:
						auto_obj = convproj_obj.automation.create(autoloc, 'float', True)
						for pos, val in paramdata.items():
							val = xtramath.between_from_one(v_min, v_max, (val+32768)/65535)
							auto_obj.add_autopoint(pos, val, None)

				#if uniquecolors:
				#	trackcolor = totalcolors[max(uniquecolors, key=lambda k: uniquecolors.get(k))]
				#	track_obj.visual.color.set_int(trackcolor)

				track_obj.placements.pl_audio.sort()
				track_obj.placements.pl_audio.remove_overlaps()
		#self.loop_end = 0