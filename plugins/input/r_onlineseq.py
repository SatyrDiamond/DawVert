# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.convproj import project as convproj
from objects.file_proj import proj_onlineseq
from objects.inst_params import fx_delay
from objects import globalstore
import plugins
import struct

def int2float(value): return struct.unpack("<f", struct.pack("<I", value))[0]

class input_onlinesequencer(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def getshortname(self): return 'onlineseq'
	def gettype(self): return 'r'
	def getdawinfo(self, dawinfo_obj): 
		dawinfo_obj.name = 'Online Sequencer'
		dawinfo_obj.file_ext = 'sequence'
		dawinfo_obj.auto_types = ['nopl_points']
		dawinfo_obj.track_nopl = True
		dawinfo_obj.plugin_included = ['midi','native-onlineseq','universal:synth-osc']
	def supported_autodetect(self): return False
	def parse(self, convproj_obj, input_file, dv_config):
		global onlseq_notelist
		global onlseq_customnames

		convproj_obj.type = 'r'
		convproj_obj.set_timings(4, True)

		globalstore.dataset.load('onlineseq', './data_main/dataset/onlineseq.dset')

		project_obj = proj_onlineseq.onlineseq_project()
		if not project_obj.load_from_file(input_file): exit()

		used_fx = {}
		for instid, instparam in project_obj.params.items(): used_fx[instid] = instparam.used_fx
		for target, params in project_obj.seperate_markers().items(): 
			if target != -1:
				if ((3 in params) or (4 in params) or (5 in params)) and 'eq' not in used_fx[target]: used_fx[instid].append('eq')
				if (6 in params) and 'delay' not in used_fx[target]: used_fx[instid].append('delay')
				if ((7 in params) or (12 in params)) and 'reverb' not in used_fx[target]: used_fx[instid].append('reverb')
				if ((13 in params) or (14 in params)) and 'distort' not in used_fx[target]: used_fx[instid].append('distort')
				if ((18 in params) or (19 in params) or (20 in params)) and 'bitcrush' not in used_fx[target]: used_fx[instid].append('bitcrush')

			for paramid, markers in params.items(): 
				autoloc = None
				div = 1
				if target == 0:
					if paramid == 0: autoloc = ['main', 'bpm']
					if paramid == 8: autoloc = ['master', 'vol']
				else:
					trackid = 'os_'+str(target)
					if paramid == 1: autoloc = ['track', trackid, 'vol']
					if paramid == 2: autoloc = ['track', trackid, 'pan']
					if paramid == 11: 
						autoloc = ['track', trackid, 'pitch']
						div = 100
					if paramid == 3: autoloc = ['plugin', trackid+'_eq', 'eq_high']
					if paramid == 4: autoloc = ['plugin', trackid+'_eq', 'eq_mid']
					if paramid == 5: autoloc = ['plugin', trackid+'_eq', 'eq_low']

					if paramid == 6: autoloc = ['slot', trackid+'_delay', 'enabled']

					if paramid == 7: autoloc = ['plugin', trackid+'_reverb', 'reverb_type']
					if paramid == 12: autoloc = ['slot', trackid+'_reverb', 'wet']

					if paramid == 13: autoloc = ['plugin', trackid+'_distort', 'distort_type']
					if paramid == 14: autoloc = ['slot', trackid+'_distort', 'wet']

					if paramid == 26: autoloc = ['plugin', trackid+'_bitcrush', 'bits']

				if autoloc:
					for marker in markers: convproj_obj.automation.add_autopoint(autoloc, 'float', marker.pos, marker.value/div, 'normal' if marker.type else 'instant')

		sep_notes = project_obj.seperate_notes(False)
		for instid, notes in sep_notes.items():
			s_used_fx = used_fx[instid] if instid in used_fx else []
			trackid = 'os_'+str(instid)
			trueinstid = instid%10000
			track_obj = convproj_obj.add_track(trackid, 'instrument', 0, False)
			midifound = track_obj.from_dataset('onlineseq', 'inst', str(trueinstid), True)
			if midifound: 
				track_obj.to_midi(convproj_obj, trackid, True)
			else:
				if instid in [13,14,15,16]: 
					plugin_obj = convproj_obj.add_plugin(trackid, 'universal', 'synth-osc')
					plugin_obj.role = 'synth'
					track_obj.inst_pluginid = trackid
					osc_data = plugin_obj.osc_add()
					if instid == 13: osc_data.prop.shape = 'sine'
					if instid == 14: osc_data.prop.shape = 'square'
					if instid == 15: osc_data.prop.shape = 'saw'
					if instid == 16: osc_data.prop.shape = 'triangle'

			if instid in project_obj.params:
				i_params = project_obj.params[instid]
				if i_params.name: track_obj.visual.name = i_params.name
				track_obj.params.add('vol', i_params.vol, 'float')
				track_obj.params.add('pan', i_params.pan, 'float')
	
				if 'bitcrush' in s_used_fx:
					pluginid = trackid+'_bitcrush'
					plugin_obj = convproj_obj.add_plugin(pluginid, 'universal', 'bitcrush')
					plugin_obj.role = 'effect'
					plugin_obj.params.add('bits', i_params.bitcrush_depth, 'float')
					track_obj.fxslots_audio.append(pluginid)

				if 'delay' in s_used_fx:
					pluginid = trackid+'_delay'
					delay_obj = fx_delay.fx_delay()
					delay_obj.feedback[0] = 0.25
					timing_obj = delay_obj.timing_add(0)
					timing_obj.set_steps(2, convproj_obj)
					plugin_obj, pluginid = delay_obj.to_cvpj(convproj_obj, pluginid)
					plugin_obj.fxdata_add(bool(i_params.delay_on), 0.5)
					plugin_obj.visual.name = 'Delay'
	
				if 'distort' in s_used_fx:
					pluginid = trackid+'_distort'
					plugin_obj = convproj_obj.add_plugin(pluginid, 'native-onlineseq', 'distort')
					plugin_obj.role = 'effect'
					plugin_obj.fxdata_add(True, i_params.distort_wet)
					plugin_obj.params.add('distort_type', i_params.distort_type, 'int')
					plugin_obj.visual.name = 'Distortion'
					track_obj.fxslots_audio.append(pluginid)
	
				if 'reverb' in s_used_fx:
					pluginid = trackid+'_reverb'
					plugin_obj = convproj_obj.add_plugin(pluginid, 'native-onlineseq', 'reverb')
					plugin_obj.role = 'effect'
					plugin_obj.fxdata_add(bool(i_params.reverb_on), i_params.reverb_wet)
					plugin_obj.params.add('reverb_type', i_params.reverb_type, 'int')
					plugin_obj.visual.name = 'Reverb'
					track_obj.fxslots_audio.append(pluginid)
	
				if 'eq' in s_used_fx:
					pluginid = trackid+'_eq'
					plugin_obj = convproj_obj.add_plugin(pluginid, 'native-onlineseq', 'eq')
					plugin_obj.role = 'effect'
					plugin_obj.fxdata_add(bool(i_params.enable_eq), 1)
					plugin_obj.params.add('eq_high', i_params.eq_high, 'float')
					plugin_obj.params.add('eq_mid', i_params.eq_mid, 'float')
					plugin_obj.params.add('eq_low', i_params.eq_low, 'float')
					plugin_obj.visual.name = 'EQ'
					track_obj.fxslots_audio.append(pluginid)

			track_obj.placements.notelist.clear_size(len(notes))

			for key, pos, dur, inst, vol in notes: 
				track_obj.placements.notelist.add_r(pos, dur, key-60, vol, {})

		convproj_obj.timesig = [project_obj.numerator, 4]
		convproj_obj.do_actions.append('do_addloop')
		convproj_obj.do_actions.append('do_singlenotelistcut')
		convproj_obj.params.add('bpm', project_obj.bpm, 'float')
