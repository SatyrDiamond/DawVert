# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import os
import math
import zipfile

from objects import globalstore

from objects.convproj import fileref
from objects.file import audio_wav

class input_fl_mobile(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'

	def get_shortname(self):
		return 'fl_mobile'

	def get_name(self):
		return 'FL Studio Mobile'

	def get_priority(self):
		return 0

	def get_prop(self, in_dict): 
		in_dict['file_ext'] = ['flm']
		in_dict['auto_types'] = ['pl_points']
		in_dict['placement_loop'] = ['loop', 'loop_off', 'loop_adv', 'loop_adv_off']
		in_dict['projtype'] = 'r'
		in_dict['fxtype'] = 'route'
		in_dict['track_lanes'] = True
		in_dict['audio_filetypes'] = ['wav','mp3']
		in_dict['audio_stretch'] = ['rate']

	def get_detect_info(self, detectdef_obj):
		detectdef_obj.headers.append([0, b'10LF'])
		detectdef_obj.containers.append(['zip', '*.flm'])

	def parse(self, convproj_obj, dawvert_intent):
		global samplefolder

		from objects.file_proj import proj_fl_mobile
		from objects.file import adlib_bnk

		convproj_obj.type = 'r'
		convproj_obj.fxtype = 'route'
		convproj_obj.set_timings(1, False)

		fileref.filesearcher.add_searchpath_full_append('factorysamples', "C:\\Program Files (x86)\\Image-Line\\FL Studio 20\\Plugins\\Fruity\\Generators\\FL Studio Mobile\\Installed", 'win')
		fileref.filesearcher.add_searchpath_full_append('factorysamples', "C:\\Program Files\\Image-Line\\FL Studio 20\\Plugins\\Fruity\\Generators\\FL Studio Mobile\\Installed", 'win')
		fileref.filesearcher.add_searchpath_full_append('factorysamples', "C:\\Program Files (x86)\\Image-Line\\FL Studio 21\\Plugins\\Fruity\\Generators\\FL Studio Mobile\\Installed", 'win')
		fileref.filesearcher.add_searchpath_full_append('factorysamples', "C:\\Program Files\\Image-Line\\FL Studio 21\\Plugins\\Fruity\\Generators\\FL Studio Mobile\\Installed", 'win')
		fileref.filesearcher.add_searchpath_full_append('factorysamples', "C:\\Program Files\\Image-Line\\FL Studio 2024\\Plugins\\Fruity\\Generators\\FL Studio Mobile\\Installed", 'win')

		samplefolder = dawvert_intent.path_samples['extracted']

		project_obj = proj_fl_mobile.flm_project()
		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		globalstore.dataset.load('fl_mobile', './data_main/dataset/fl_mobile.dset')

		tempomul = 120/project_obj.tempo

		sorttracks = {}

		tracks = [(project_obj.racks[n], x) for n, x in enumerate(project_obj.channels)]
		for n, d in enumerate(tracks):
			flm_rack, flm_channel = d

			startloc = []

			if flm_channel.unk1 == 0: 
				tracktype = 'master'
			elif flm_channel.unk1 == 128: 
				tracktype = 'fx'
			else: 
				if flm_rack.devices_sampler:
					tracktype = 'instrument'
				else:
					tracktype = 'audio'

			devices_order = {}
			for x in flm_rack.devices:
				devices_order[x.order] = x

			if tracktype == 'master':
				trackid = 'master'
				add_visual(convproj_obj.track_master.visual, flm_channel)
				add_params(convproj_obj.track_master.params, flm_rack)

				do_devices(devices_order, convproj_obj, flm_rack.devices, convproj_obj.track_master.plugslots, dawvert_intent.input_file, project_obj.zipfile, trackid)

			if tracktype == 'fx':
				trackid = 'flm_fx_'+str(flm_rack.fx_id)
				sorttracks[flm_channel.unk5] = trackid
				track_obj = convproj_obj.track__add(trackid, 'fx', 1, False)
				add_visual(track_obj.visual, flm_channel)
				add_params(track_obj.params, flm_rack)

				do_devices(devices_order, convproj_obj, flm_rack.devices, track_obj.plugslots, dawvert_intent.input_file, project_obj.zipfile, trackid)

				sends_obj = convproj_obj.fx__route__add(trackid)
				sends_obj.to_master_active = flm_rack.target == -1
				if flm_rack.target != -1:
					send_target = 'flm_fx_'+str(flm_rack.target)
					sends_obj.to_master_active = False
					send_obj = sends_obj.add(send_target, None, 1)
	
			if tracktype == 'instrument':
				trackid = 'flm_inst_'+str(n)
				sorttracks[flm_channel.unk5] = trackid
				track_obj = convproj_obj.track__add(trackid, 'instrument', 1, False)
				add_visual(track_obj.visual, flm_channel)
				add_params(track_obj.params, flm_rack)
				pluginid, plugin_obj = do_device(convproj_obj, flm_rack.devices_sampler, dawvert_intent.input_file, project_obj.zipfile, trackid, 2)
				track_obj.plugslots.plugin_autoplace(plugin_obj, pluginid)

				do_devices(devices_order, convproj_obj, flm_rack.devices, track_obj.plugslots, dawvert_intent.input_file, project_obj.zipfile, trackid)

				sends_obj = convproj_obj.fx__route__add(trackid)
				sends_obj.to_master_active = flm_rack.target == -1
				if flm_rack.target != -1:
					send_target = 'flm_fx_'+str(flm_rack.target)
					sends_obj.to_master_active = False
					send_obj = sends_obj.add(send_target, None, 1)

			if tracktype == 'audio':
				trackid = 'flm_inst_'+str(n)
				sorttracks[flm_channel.unk5] = trackid
				track_obj = convproj_obj.track__add(trackid, 'audio', 1, False)
				add_visual(track_obj.visual, flm_channel)
				add_params(track_obj.params, flm_rack)

				do_devices(devices_order, convproj_obj, flm_rack.devices, track_obj.plugslots, dawvert_intent.input_file, project_obj.zipfile, trackid)

				sends_obj = convproj_obj.fx__route__add(trackid)
				sends_obj.to_master_active = flm_rack.target == -1
				if flm_rack.target != -1:
					send_target = 'flm_fx_'+str(flm_rack.target)
					sends_obj.to_master_active = False
					send_obj = sends_obj.add(send_target, None, 1)

			if trackid:
				for lanenum, lanedata in enumerate(flm_channel.tracks):

					if lanedata.auto_on == 0:
						lane_obj = track_obj.add_lane(str(lanenum))
						if tracktype == 'instrument':
							for flm_clip in lanedata.clips:
								pos = flm_clip.position/128
								placement_obj = lane_obj.placements.add_notes()
								placement_obj.time.set_posdur(pos, flm_clip.duration)
								placement_obj.time.set_loop_data(flm_clip.cut_start%flm_clip.loop_end, 0, flm_clip.loop_end)

								if not flm_clip.duration: 
									placement_obj.auto_dur(1, flm_clip.loop_end)

								if flm_clip.evn2:
									slidenotes = []
									for event in flm_clip.evn2.events:
										if len(event) > 7:
											if event[7]: 
												slidenotes.append([event[0]/128, event[1], event[2]-60, event[4]/127, None])
											else: 
												placement_obj.notelist.add_r(event[0]/128, event[1], event[2]-60, event[4]/127, None)
										else:
											placement_obj.notelist.add_r(event[0]/128, event[1], event[2]-60, event[4]/127, None)

									for sn in slidenotes: 
										placement_obj.notelist.auto_add_slide(None, sn[0], sn[1], sn[2], sn[3], sn[4])

					if lanedata.auto_on == 3:
						lane_obj = track_obj.add_lane(str(lanenum))
						if tracktype == 'instrument':
							for flm_clip in lanedata.clips:
								pos = flm_clip.position/128
								placement_obj = lane_obj.placements.add_notes()
								placement_obj.time.set_posdur(pos, flm_clip.duration)
								placement_obj.time.set_loop_data(flm_clip.cut_start%flm_clip.loop_end, 0, flm_clip.loop_end)
								if not flm_clip.duration: 
									placement_obj.auto_dur(1, flm_clip.loop_end)

								if flm_clip.evn2:
									for event in flm_clip.evn2.events:
										placement_obj.notelist.add_r(event[0]/128, event[1], event[2], event[4]/127, None)

					if lanedata.auto_on == 2:
						lane_obj = track_obj.add_lane(str(lanenum))
						if tracktype == 'audio':
							for flm_clip in lanedata.clips:
								pos = flm_clip.position/128
								placement_obj = lane_obj.placements.add_audio()
								placement_obj.time.set_posdur(pos, flm_clip.duration)
								placement_obj.time.set_loop_data(flm_clip.cut_start%flm_clip.loop_end, 0, flm_clip.loop_end)

								if flm_clip.sample:
									flm_sample = flm_clip.sample
									sample_path = get_path(flm_sample.sample_path)

									sampleref_obj = do_sample(convproj_obj, sample_path, project_obj.zipfile, dawvert_intent.input_file)

									if sampleref_obj:
										if not placement_obj.time.duration:
											placement_obj.time.duration = ((sampleref_obj.dur_sec*2)*tempomul)

									placement_obj.visual.name = flm_clip.sample.sample_name

									sp_obj = placement_obj.sample
									sp_obj.sampleref = sample_path

									sp_obj.stretch.set_rate_speed(project_obj.tempo, flm_sample.stretch_size, True)
									sp_obj.stretch.preserve_pitch = True
									sp_obj.pitch = math.log2(1/flm_sample.pitch)*-12

									sp_obj.reverse = bool(flm_sample.main_unk_4)
									if flm_sample.prms:
										sp_obj.reverse = bool(flm_sample.main_unk_4)
										sp_obj.vol = flm_sample.prms[0]
										sp_obj.pan = (flm_sample.prms[1]-0.5)*2
										

					if lanedata.auto_on == 1:
						v_add = 0
						v_mul = 1
						v_bool = False

						if lanedata.auto_device == 0:
							if tracktype == 'master': autoloc = ['master']
							if tracktype == 'fx': autoloc = ['return', trackid]
							if tracktype == 'instrument': autoloc = ['track', trackid]
							if tracktype == 'audio': autoloc = ['track', trackid]

							if lanedata.auto_param == 0: autoloc += ['vol']
							if lanedata.auto_param == 1: 
								autoloc += ['pan']
								v_add = -0.5
								v_mul = 2
							if lanedata.auto_param == 2: 
								autoloc += ['mute']
								v_bool = True

						else:
							autoloc = ['plugin', trackid+'_'+str(lanedata.auto_device), 'param_'+str(lanedata.auto_param)]

						for flm_clip in lanedata.clips:
							startpos = flm_clip.position/128
							if flm_clip.evn2: 
								autopl_obj = convproj_obj.automation.add_pl_points(autoloc, 'float')
								duration = do_auto(flm_clip.evn2.events, autopl_obj.data, startpos, v_add, v_mul, v_bool)
								autopl_obj.time.set_posdur(startpos, duration)

		convproj_obj.track_order = [sorttracks[x] for x in sorted(list(sorttracks))]

		convproj_obj.params.add('bpm', project_obj.tempo, 'float')

def extract_audio(audioname, zip_data):
	audio_filename = None
	for s_file in zip_data.namelist():
		if audioname in s_file:
			audio_filename = samplefolder+s_file
			if os.path.exists(samplefolder+s_file) == False:
				zip_data.extract(s_file, path=samplefolder, pwd=None)
				break
	return audio_filename

def do_sample(convproj_obj, sample_path, zipfile, projfile):
	if sample_path:
		fromzip = False
		o_sample_path = sample_path
		if zipfile:
			t_sample_path = sample_path.replace('\\', '/')
			if t_sample_path in zipfile.namelist():
				o_sample_path = extract_audio(t_sample_path, zipfile)
				fromzip = True

		sampleref_obj = convproj_obj.sampleref__add(sample_path, o_sample_path, None)
		if not fromzip:
			sampleref_obj.find_relative('factorysamples')
			sampleref_obj.search_local(os.path.dirname(projfile))

		return sampleref_obj

def do_devices(devices_order, convproj_obj, devices, plugslots, projfilepath, zipfile, trackid):
	sortlist = sorted(list(devices_order))

	for i in sortlist: 
		x = devices_order[i]
		pluginid, plugin_obj = do_device(convproj_obj, x, projfilepath, zipfile, trackid, x.order)
		plugslots.plugin_autoplace(plugin_obj, pluginid)

def do_device(convproj_obj, device_obj, projfilepath, zipfile, pluginid, numberid):

	pluginid = pluginid+'_'+str(device_obj.order)

	plugin_obj = None

	if device_obj.type == 1397567537:
		if device_obj.drumsamples:
			plugin_obj = convproj_obj.plugin__add(pluginid, 'universal', 'sampler', 'multi')
			plugin_obj.env_asdr_add('vol', 0, 0, 0, 0, 1, 10, 1)
			plugin_obj.role = 'synth'

			for n, flm_sample in enumerate(device_obj.drumsamples):
				keynum = n
				sample_path = get_path(flm_sample.sample_path)
				sampleref_obj = do_sample(convproj_obj, sample_path, zipfile, projfilepath)
				sp_obj = plugin_obj.sampleregion_add(keynum, keynum, keynum, None)
				sp_obj.sampleref = sample_path
				sp_obj.pitch = math.log2(1/flm_sample.pitch)*-12
				sp_obj.reverse = bool(flm_sample.main_unk_4)
				sp_obj.trigger = 'oneshot'
				if flm_sample.prms:
					sp_obj.reverse = bool(flm_sample.main_unk_4)
					sp_obj.vol = flm_sample.prms[0]
					sp_obj.pan = (flm_sample.prms[1]-0.5)*2

	elif device_obj.type == 1:
		if device_obj.cstm:
			cstm = device_obj.cstm
			zones = cstm.zones
			if zones:
				plugin_obj = convproj_obj.plugin__add(pluginid, 'universal', 'sampler', 'multi')
				plugin_obj.role = 'synth'
				for x in zones:
					sample_path = get_path(x.name)
					sampleref_obj = do_sample(convproj_obj, sample_path, zipfile, projfilepath)
	
					middlenote = int((device_obj.prms[3]-0.5)*48) if device_obj.prms else 0

					if sampleref_obj.fileref.file.extension == 'wav':
						filepath = sampleref_obj.fileref.get_path(None, False)
						try:
							wav_obj = audio_wav.wav_main()
							wav_obj.readinfo(filepath)
							wav_inst = wav_obj.inst
							sp_obj = plugin_obj.sampleregion_add(wav_inst.note_low-60, wav_inst.note_high-60, (wav_inst.rootnote-60)-middlenote, None)
							sp_obj.vel_min = wav_inst.vel_low/127
							sp_obj.vel_max = wav_inst.vel_high/127
							sp_obj.sampleref = sample_path
							sp_obj.from_sampleref_obj(sampleref_obj)
						except:
							pass

	else:
		plugin_obj = convproj_obj.plugin__add(pluginid, 'native', 'fl_mobile', str(device_obj.type))

		fldso = globalstore.dataset.get_obj('fl_mobile', 'plugin', str(device_obj.type))
		if fldso:
			plugin_obj.visual.name = fldso.visual.name

		if device_obj.prms:
			if fldso:
				for n, v in enumerate(device_obj.prms):
					dset_param = fldso.params.get('param_'+str(n))
					if dset_param: plugin_obj.dset_param__add('param_'+str(n), v, dset_param)
			else:
				for num, val in enumerate(device_obj.prms):
					plugin_obj.params.add('param_'+str(num), val, 'float')

	return pluginid, plugin_obj

def get_path(sample_path):
	out = sample_path
	if sample_path[0:4] == b'@L@\x00':
		out = sample_path[4:].split(b'\0')[0].decode()
	elif sample_path[0:4] == b'@R@\x00':
		out = sample_path[4:].split(b'\0')[0].decode()
	elif sample_path[0:3] == b'@R@':
		out = sample_path[3:].split(b'\0')[0].decode()
	else:
		out = sample_path.split(b'\0')[0].decode()
	if out:
		return out

def add_params(params_obj, flm_rack):
	params_obj.add('vol', flm_rack.volume, 'float')
	params_obj.add('pan', (flm_rack.pan-0.5)*2, 'float')
	params_obj.add('enabled', not flm_rack.mute, 'float')
	params_obj.add('solo', flm_rack.solo, 'float')

def do_auto(evn2_events, autopoints, startpos, v_add, v_mul, v_bool):
	duration = 0
	for event in evn2_events:
		if event[2] != -1:
			autopoint_obj = autopoints.add_point()
			duration = autopoint_obj.pos = event[0]/128
			autopoint_obj.value = ((event[5]/65534)+v_add)*v_mul if not v_bool else int((event[5]>32767))
	return duration

def add_visual(visual_obj, flm_channel):
	visual_obj.name = flm_channel.name
	visual_obj.color.set_hsv((flm_channel.color*0.8)-0.21, 0.8, 1)