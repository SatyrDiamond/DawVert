# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import xml.etree.ElementTree as ET
import plugins
from objects import globalstore
from objects import colors

class input_nanostudio_v1(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'nanostudio_v1'
	
	def get_name(self):
		return 'NanoStudio 1'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['file_ext'] = ['prj']
		in_dict['audio_filetypes'] = ['wav']
		in_dict['auto_types'] = ['pl_ticks']
		in_dict['placement_loop'] = ['loop']
		in_dict['track_lanes'] = True
		in_dict['projtype'] = 'r'

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj import nanostudio as proj_nanostudio
		from objects import audio_data

		samplefolder = dawvert_intent.path_samples['extracted']

		globalstore.dataset.load('nanostudio_v1', './data_main/dataset/nanostudio_v1.dset')
		colordata = colors.colorset.from_dataset('nanostudio_v1', 'clips', 'main')

		convproj_obj.type = 'r'
		convproj_obj.set_timings(256, True)

		project_obj = proj_nanostudio.nanostudio_song()
		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_folder(dawvert_intent.input_file): exit()

		convproj_obj.params.add('bpm', project_obj.tempo, 'float')

		track_data = {}

		for instnum, ns_inst in project_obj.instruments.items():
			cvpj_trackid = 'track_'+str(instnum)

			if ns_inst.type != 'Mixer':
				track_obj = convproj_obj.track__add(cvpj_trackid, 'instrument', 1, False)
				track_data[instnum] = track_obj
				track_obj.visual.name = ns_inst.name

				plugin_obj = convproj_obj.plugin__add(cvpj_trackid, 'native', 'nanostudio_v1', ns_inst.type)
				plugin_obj.role = 'synth'
				track_obj.plugin_autoplace(plugin_obj, cvpj_trackid)

				if ns_inst.mixerchannels:
					channel = ns_inst.mixerchannels[list(ns_inst.mixerchannels)[0]]
					track_obj.params.add('vol', channel.vol, 'float')
					track_obj.params.add('pan', (channel.pan-0.5)*2, 'float')

					infx = channel.insertfx
					for n, fx in enumerate([infx.node_slot1, infx.node_slot2, infx.node_slot3, infx.node_slot4]):
						if fx.type:
							fxid = cvpj_trackid+'_fx_'+str(n)
							plugin_obj = convproj_obj.plugin__add(fxid, 'native', 'nanostudio_v1', fx.type)
							plugin_obj.role = 'fx'
							if 'Enable' in fx.patch: 
								plugin_obj.fxdata_add(fx.patch['Enable']=='1', None)
								del fx.patch['Enable']
							for key, val in fx.patch.items():
								if val.replace('.', '').isnumeric(): plugin_obj.params.add(key, float(val), 'float')
								else: plugin_obj.datavals.add(key, val)
							track_obj.plugin_autoplace(plugin_obj, fxid)

		repeatnum = {}
		for tracknum, clips in project_obj.clips:
			if tracknum not in repeatnum: repeatnum[tracknum] = 0
			repeatnum[tracknum] += 1
			if tracknum in track_data:
				track_obj = track_data[tracknum]
				lane_pl = track_obj.add_lane(str(repeatnum[tracknum]))
				if clips is not None:
					for clip in clips:
						clipsize, events = project_obj.patterns[clip['event_assoc']]
						placement_obj = lane_pl.placements.add_notes()
						if clip['event_assoc']<100: 
							placement_obj.visual.name = 'Pattern #'+str(clip['event_assoc'])
							colorfloat = colordata.getcolornum(clip['event_assoc']-1)
							placement_obj.visual.color.set_float(colorfloat)
						else:
							placement_obj.visual.color.set_float([0.25, 0.59, 0.73])

						placement_obj.time.set_posdur(clip['position']*256, clip['duration']*256)
						if clip['duration']>clipsize: placement_obj.time.set_loop_data(0, 0, clipsize*256)

						for event in events:
							if event['type'] == 0:
								placement_obj.notelist.add_r(event['position'], event['duration'], event['key']-60, event['vol_val']/127, None)
