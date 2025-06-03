# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import json
import struct
import os.path
from objects import globalstore

def parse_notes(convproj_obj, trackid, notes_data, track_obj, keyoffset):
	cvpj_notelist = track_obj.placements.notelist
	for pos, nd in enumerate(notes_data):
		notes, pan = nd
		cvpj_notelist.add_r_multi(pos, 1, [(x+keyoffset)-12 for x in notes], 1, None)
		if pan != 0: convproj_obj.automation.add_autotick(['track', trackid, 'pan'], 'float', pos, (pan-4)/3)
	cvpj_notelist.sort()

class input_piyopiyo(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'piyopiyo'
	
	def get_name(self):
		return 'PiyoPiyo'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['plugin_included'] = ['universal:synth-osc','universal:sampler:multi']
		in_dict['projtype'] = 'r'

	def parse(self, convproj_obj, dawvert_intent):
		from objects import colors
		from objects.file_proj_past import piyopiyo as proj_piyopiyo

		convproj_obj.type = 'r'
		convproj_obj.set_timings(4, True)

		traits_obj = convproj_obj.traits
		traits_obj.auto_types = ['nopl_ticks']
		traits_obj.track_nopl = True

		project_obj = proj_piyopiyo.piyopiyo_song()
		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		extpath_path = os.path.join(dawvert_intent.path_external_data, 'piyopiyo')

		globalstore.dataset.load('piyopiyo', './data_main/dataset/piyopiyo.dset')
		colordata = colors.colorset.from_dataset('piyopiyo', 'inst', 'main')

		for tracknum in range(3):
			pmdtrack_obj = project_obj.tracks[tracknum]
			keyoffset = (pmdtrack_obj.octave-2)*12

			idval = str(tracknum)
			track_obj = convproj_obj.track__add(idval, 'instrument', 0, False)
			track_obj.visual.name = 'Inst #'+str(tracknum+1)
			track_obj.visual.color.set_int(colordata.getcolornum(tracknum))
			track_obj.params.add('vol', pmdtrack_obj.volume/250, 'float')

			plugin_obj, pluginid = convproj_obj.plugin__add__genid('universal', 'synth-osc', None)
			plugin_obj.role = 'synth'
			osc_data = plugin_obj.osc_add()
			osc_data.prop.type = 'wave'
			osc_data.prop.nameid = 'main'
			wave_obj = plugin_obj.wave_add('main')
			wave_obj.set_all_range(pmdtrack_obj.waveform, -128, 128)
			plugin_obj.env_blocks_add('vol', pmdtrack_obj.envelope, 1/64, 128, None, None)
			plugin_obj.env_points_from_blocks('vol')
			track_obj.plugslots.set_synth(pluginid)
			parse_notes(convproj_obj, idval, project_obj.notes_data[tracknum], track_obj, keyoffset)

		track_obj = convproj_obj.track__add("3", 'instrument', False, False)
		track_obj.visual.name = 'Drums'
		track_obj.visual.color.set_int(colordata.getcolornum(3))
		track_obj.params.add('vol', (project_obj.perc_volume/250)/3, 'float')
		plugin_obj, pluginid = convproj_obj.plugin__add__genid('universal', 'sampler', 'drums')
		plugin_obj.role = 'synth'
		track_obj.is_drum = True
		track_obj.plugslots.set_synth(pluginid)

		for sampname in ['BASS1', 'BASS2', 'SNARE1', 'HAT1', 'HAT2', 'SYMBAL1']:
			sampid = 'PIYOPIYO_%s' % sampname
			sampleref_obj = convproj_obj.sampleref__add(sampname, os.path.join(extpath_path,sampname+'.wav'), None)
			sampleref_obj.find_relative('external_data')
			sp_obj = plugin_obj.samplepart_add(sampid)
			sp_obj.sampleref = sampname

		drumpad_obj, layer_obj = plugin_obj.drumpad_add_singlelayer()
		drumpad_obj.key = -12
		drumpad_obj.visual.name = 'Bass 1'
		layer_obj.samplepartid = 'PIYOPIYO_BASS1'

		drumpad_obj, layer_obj = plugin_obj.drumpad_add_singlelayer()
		drumpad_obj.key = -11
		drumpad_obj.vol = 0.6
		drumpad_obj.visual.name = 'Bass 1'
		layer_obj.samplepartid = 'PIYOPIYO_BASS1'

		drumpad_obj, layer_obj = plugin_obj.drumpad_add_singlelayer()
		drumpad_obj.key = -10
		drumpad_obj.visual.name = 'Bass 2'
		layer_obj.samplepartid = 'PIYOPIYO_BASS2'

		drumpad_obj, layer_obj = plugin_obj.drumpad_add_singlelayer()
		drumpad_obj.key = -9
		drumpad_obj.vol = 0.6
		drumpad_obj.visual.name = 'Bass 2'
		layer_obj.samplepartid = 'PIYOPIYO_BASS2'

		drumpad_obj, layer_obj = plugin_obj.drumpad_add_singlelayer()
		drumpad_obj.key = -8
		drumpad_obj.visual.name = 'Snare'
		layer_obj.samplepartid = 'PIYOPIYO_SNARE1'

		drumpad_obj, layer_obj = plugin_obj.drumpad_add_singlelayer()
		drumpad_obj.key = -7
		drumpad_obj.vol = 0.6
		drumpad_obj.visual.name = 'Snare'
		layer_obj.samplepartid = 'PIYOPIYO_SNARE1'

		drumpad_obj, layer_obj = plugin_obj.drumpad_add_singlelayer()
		drumpad_obj.key = -4
		drumpad_obj.visual.name = 'Hat 1'
		layer_obj.samplepartid = 'PIYOPIYO_HAT1'

		drumpad_obj, layer_obj = plugin_obj.drumpad_add_singlelayer()
		drumpad_obj.key = -3
		drumpad_obj.vol = 0.6
		drumpad_obj.visual.name = 'Hat 1'
		layer_obj.samplepartid = 'PIYOPIYO_HAT1'

		drumpad_obj, layer_obj = plugin_obj.drumpad_add_singlelayer()
		drumpad_obj.key = -2
		drumpad_obj.visual.name = 'Hat 2'
		layer_obj.samplepartid = 'PIYOPIYO_HAT2'

		drumpad_obj, layer_obj = plugin_obj.drumpad_add_singlelayer()
		drumpad_obj.key = -1
		drumpad_obj.vol = 0.6
		drumpad_obj.visual.name = 'Hat 2'
		layer_obj.samplepartid = 'PIYOPIYO_HAT2'

		drumpad_obj, layer_obj = plugin_obj.drumpad_add_singlelayer()
		drumpad_obj.key = 0
		drumpad_obj.visual.name = 'Symbal'
		layer_obj.samplepartid = 'PIYOPIYO_SYMBAL1'

		drumpad_obj, layer_obj = plugin_obj.drumpad_add_singlelayer()
		drumpad_obj.key = 1
		drumpad_obj.vol = 0.6
		drumpad_obj.visual.name = 'Symbal'
		layer_obj.samplepartid = 'PIYOPIYO_SYMBAL1'

		parse_notes(convproj_obj, '3', project_obj.notes_data[3], track_obj, 0)

		convproj_obj.do_actions.append('do_addloop')
		convproj_obj.do_actions.append('do_singlenotelistcut')
		convproj_obj.params.add('bpm', (120/project_obj.musicwait)*120, 'float')

		convproj_obj.transport.loop_active = True
		convproj_obj.transport.loop_start = project_obj.loopstart
		convproj_obj.transport.loop_end = project_obj.loopend