# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import logging
from functions import data_bytes

logger_plugconv = logging.getLogger('plugconv')

class plugconv(plugins.base):
	def is_dawvert_plugin(self):
		return 'plugconv'
	
	def get_priority(self):
		return -90
	
	def get_prop(self, in_dict): 
		in_dict['in_plugin'] = 'universal:midi'
		in_dict['in_daws'] = []
		in_dict['out_plugins'] = ['universal:soundfont2']
		in_dict['out_daws'] = []

	def convert(self, convproj_obj, plugin_obj, pluginid, dawvert_intent):

		if convproj_obj.type not in ['cm', 'cs']:
			sf2_loc = None
			if 'global' in dawvert_intent.path_soundfonts:
				sf2_loc = dawvert_intent.path_soundfonts['global']
	
			if sf2_loc == None: 
				mididevice = plugin_obj.datavals.get('device', 'gm')
				if mididevice in dawvert_intent.path_soundfonts:
					if dawvert_intent.path_soundfonts[mididevice]:
						#logger_plugconv.info('Using '+mididevice.upper()+' SF2.')
						sf2_loc = dawvert_intent.path_soundfonts[mididevice]
	
			if sf2_loc:
				midi_obj = plugin_obj.midi
				plugin_obj.replace('universal', 'soundfont2', None)
				plugin_obj.midi = midi_obj
				convproj_obj.fileref__add(sf2_loc, sf2_loc, None)
				plugin_obj.state.filerefs['file'] = sf2_loc
				return True