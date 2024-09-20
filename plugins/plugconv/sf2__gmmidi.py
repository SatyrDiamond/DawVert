# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import logging
from functions import data_bytes
from functions import extpluglog

logger_plugconv = logging.getLogger('plugconv')

class plugconv(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'plugconv'
	def getplugconvinfo(self, plugconv_obj): 
		plugconv_obj.priority = 200
		plugconv_obj.in_plugins = [['midi', None]]
		plugconv_obj.in_daws = []
		plugconv_obj.out_plugins = [['soundfont2', None]]
		plugconv_obj.out_daws = []
	def convert(self, convproj_obj, plugin_obj, pluginid, dv_config):

		sf2_loc = None
		if dv_config.path_soundfont: sf2_loc = dv_config.path_soundfont

		if sf2_loc == None: 
			mididevice = plugin_obj.datavals.get('device', 'gm')
			if mididevice in dv_config.paths_soundfonts:
				if dv_config.paths_soundfonts[mididevice]:
					logger_plugconv.info('Using '+mididevice.upper()+' SF2.')
					sf2_loc = dv_config.paths_soundfonts[mididevice]

		if sf2_loc != None:
			extpluglog.convinternal('MIDI', 'MIDI', 'SoundFont2', 'SoundFont2')
			plugin_obj.replace('soundfont2', None)
			convproj_obj.add_fileref(sf2_loc, sf2_loc, None)
			plugin_obj.filerefs['file'] = sf2_loc
			return 1

		#if sf2_loc == None: print('[plug-conv] No Soundfont Argument or Configured:',pluginid)
		return 2