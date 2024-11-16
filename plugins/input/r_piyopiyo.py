# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import json
import struct
import os.path
from objects import globalstore

def parse_notes(convproj_obj, trackid, notes_data, track_obj, keyoffset):
	for pos, nd in enumerate(notes_data):
		notes, pan = nd
		track_obj.placements.notelist.add_r_multi(pos, 1, [(x+keyoffset)-12 for x in notes], 1, {})
		if pan != 0:
			convproj_obj.automation.add_autotick(['track', trackid, 'pan'], 'float', pos, (pan-4)/3)

class input_piyopiyo(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def get_shortname(self): return 'piyopiyo'
	def get_name(self): return 'PiyoPiyo'
	def get_priority(self): return 0
	def get_prop(self, in_dict): 
		in_dict['file_ext'] = ['pmd']
		in_dict['plugin_included'] = ['universal:synth-osc','universal:sampler:multi']
		in_dict['auto_types'] = ['nopl_ticks']
		in_dict['track_nopl'] = True
		in_dict['projtype'] = 'r'
	def supported_autodetect(self): return True
	def detect(self, input_file):
		bytestream = open(input_file, 'rb')
		bytestream.seek(0)
		bytesdata = bytestream.read(3)
		if bytesdata == b'PMD': return True
		else: return False

	def parse(self, convproj_obj, input_file, dv_config):
		from objects import colors
		from objects.file_proj import proj_piyopiyo

		convproj_obj.type = 'r'
		convproj_obj.set_timings(4, True)

		project_obj = proj_piyopiyo.piyopiyo_song()
		if not project_obj.load_from_file(input_file): exit()

		extpath_path = os.path.join(dv_config.path_external_data, 'piyopiyo')

		globalstore.dataset.load('piyopiyo', './data_main/dataset/piyopiyo.dset')
		colordata = colors.colorset.from_dataset('piyopiyo', 'inst', 'main')

		for tracknum in range(3):
			pmdtrack_obj = project_obj.tracks[tracknum]
			keyoffset = (pmdtrack_obj.octave-2)*12

			idval = str(tracknum)
			track_obj = convproj_obj.track__add(idval, 'instrument', 0, False)
			track_obj.visual.name = 'Inst #'+str(tracknum+1)
			track_obj.visual.color.set_float(colordata.getcolornum(tracknum))
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
		track_obj.visual.color.set_float(colordata.getcolornum(3))
		track_obj.params.add('vol', (project_obj.perc_volume/250)/3, 'float')
		plugin_obj, pluginid = convproj_obj.plugin__add__genid('universal', 'sampler', 'multi')
		plugin_obj.role = 'synth'
		plugin_obj.env_asdr_add('vol', 0, 0, 0, 0, 1, 10, 1)
		track_obj.is_drum = True
		track_obj.plugslots.set_synth(pluginid)

		sampleref_obj = convproj_obj.sampleref__add('PIYOPIYO_BASS1', os.path.join(extpath_path,'BASS1.wav'), None)
		sampleref_obj.find_relative('external_data')
		sampleref_obj = convproj_obj.sampleref__add('PIYOPIYO_BASS2', os.path.join(extpath_path,'BASS2.wav'), None)
		sampleref_obj.find_relative('external_data')
		sampleref_obj = convproj_obj.sampleref__add('PIYOPIYO_SNARE1', os.path.join(extpath_path,'SNARE1.wav'), None)
		sampleref_obj.find_relative('external_data')
		sampleref_obj = convproj_obj.sampleref__add('PIYOPIYO_HAT1', os.path.join(extpath_path,'HAT1.wav'), None)
		sampleref_obj.find_relative('external_data')
		sampleref_obj = convproj_obj.sampleref__add('PIYOPIYO_HAT2', os.path.join(extpath_path,'HAT2.wav'), None)
		sampleref_obj.find_relative('external_data')
		sampleref_obj = convproj_obj.sampleref__add('PIYOPIYO_SYMBAL1', os.path.join(extpath_path,'SYMBAL1.wav'), None)
		sampleref_obj.find_relative('external_data')

		sp_obj = plugin_obj.sampleregion_add(-12, -12, -12, None)
		sp_obj.sampleref = 'PIYOPIYO_BASS1'
		sp_obj = plugin_obj.sampleregion_add(-11, -11, -11, None)
		sp_obj.sampleref = 'PIYOPIYO_BASS1'

		sp_obj = plugin_obj.sampleregion_add(-10, -10, -10, None)
		sp_obj.sampleref = 'PIYOPIYO_BASS2'
		sp_obj = plugin_obj.sampleregion_add(-9, -9, -9, None)
		sp_obj.sampleref = 'PIYOPIYO_BASS2'

		sp_obj = plugin_obj.sampleregion_add(-8, -8, -8, None)
		sp_obj.sampleref = 'PIYOPIYO_SNARE1'
		sp_obj = plugin_obj.sampleregion_add(-7, -7, -7, None)
		sp_obj.sampleref = 'PIYOPIYO_SNARE1'

		sp_obj = plugin_obj.sampleregion_add(-4, -4, -4, None)
		sp_obj.sampleref = 'PIYOPIYO_HAT1'
		sp_obj = plugin_obj.sampleregion_add(-3, -3, -3, None)
		sp_obj.sampleref = 'PIYOPIYO_HAT1'

		sp_obj = plugin_obj.sampleregion_add(-2, -2, -2, None)
		sp_obj.sampleref = 'PIYOPIYO_HAT2'
		sp_obj = plugin_obj.sampleregion_add(-1, -1, -1, None)
		sp_obj.sampleref = 'PIYOPIYO_HAT2'

		sp_obj = plugin_obj.sampleregion_add(0, 0, 0, None)
		sp_obj.sampleref = 'PIYOPIYO_SYMBAL1'
		sp_obj = plugin_obj.sampleregion_add(1, 1, 1, None)
		sp_obj.sampleref = 'PIYOPIYO_SYMBAL1'

		parse_notes(convproj_obj, '3', project_obj.notes_data[3], track_obj, 0)

		convproj_obj.do_actions.append('do_addloop')
		convproj_obj.do_actions.append('do_singlenotelistcut')
		convproj_obj.params.add('bpm', (120/project_obj.musicwait)*120, 'float')

		convproj_obj.loop_active = True
		convproj_obj.loop_start = project_obj.loopstart
		convproj_obj.loop_end = project_obj.loopend