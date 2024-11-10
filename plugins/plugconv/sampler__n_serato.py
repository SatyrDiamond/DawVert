# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import os
import json
from functions import extpluglog

class plugconv(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'plugconv'
	def get_priority(self): return -100
	def get_prop(self, in_dict): 
		in_dict['in_plugins'] = [['native', 'serato-inst', 'instrument']]
		in_dict['in_daws'] = ['serato']
		in_dict['out_plugins'] = [['universal', 'sampler', None]]
		in_dict['out_daws'] = []
	def convert(self, convproj_obj, plugin_obj, pluginid, dv_config):
		
		if plugin_obj.type.check_wildmatch('native', 'serato-inst', 'instrument'):
			isfound, fileref = plugin_obj.fileref__get('instrument', convproj_obj)
			if isfound:
				filepath = fileref.get_path(None, False)
				if os.path.exists(filepath):
					f = open(filepath)
					try:
						instdata = json.load(f)
						extpluglog.convinternal('Serato Studio', 'Instrument', 'Sampler', 'MultiSampler')
						plugin_obj.replace('universal', 'sampler', 'multi')
						if 'samples' in instdata:
							samples = instdata['samples']
							for sample in samples:
								sample_fileref = fileref.copy()
								sample_file = sample['file'] if "file" in sample else ''
								sample_fileref.file.set(sample_file)
								fullpath = sample_fileref.get_path(None, False)
	
								nominal_note = sample['nominal_note'] if "nominal_note" in sample else 60
								nominal_amplitude = sample['nominal_amplitude'] if "nominal_amplitude" in sample else 1
								trigger_note_min = sample['trigger_note_min'] if "trigger_note_min" in sample else 0
								trigger_note_max = sample['trigger_note_max'] if "trigger_note_max" in sample else 127
								#trigger_velocity_min = sample['trigger_velocity_min'] if "trigger_velocity_min" in sample else 1
								#trigger_velocity_max = sample['trigger_velocity_max'] if "trigger_velocity_max" in sample else 127
	
								sampleref_obj = convproj_obj.sampleref__add(fullpath, fullpath, None)
								sp_obj = plugin_obj.sampleregion_add(trigger_note_min-60, trigger_note_max-60, nominal_note-60, None)
								sp_obj.from_sampleref_obj(sampleref_obj)
								sp_obj.sampleref = fullpath
								sp_obj.vol = nominal_amplitude
						return 1
					except:
						pass
		return 2

