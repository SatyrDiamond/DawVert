# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins

from functions_plugin_ext import plugin_vst2
from functions import extpluglog
from functions import xtramath

class plugconv(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'plugconv_ext'
	def get_prop(self, in_dict): 
		in_dict['in_plugin'] = ['universal', None, None]
		in_dict['ext_formats'] = ['vst2']
		in_dict['plugincat'] = ['nonfree']
	def convert(self, convproj_obj, plugin_obj, pluginid, dawvert_intent, extplugtype):
		if plugin_obj.type.check_wildmatch('universal', 'autotune', None):
			if 'vst2' in extplugtype:
				extpluglog.extpluglist.add('Nonfree', 'VST2', 'GSnap', 'GVST')
				if plugin_vst2.check_exists('id', 1735999862):
					extpluglog.extpluglist.success('Universal', 'AutoTune')
					keysdata = []
					for x in range(12):
						realkey = (x+9)%12
						keysdata.append( int(plugin_obj.params.get('key_on_'+str(realkey), 1).value) )
					speed = plugin_obj.params.get('speed', 1).value
					calibrate = plugin_obj.params.get('calibrate', 440).value
					amount = plugin_obj.params.get('amount', 1).value
					attack = plugin_obj.params.get('attack', 0.001).value
					release = plugin_obj.params.get('release', 0.001).value

					plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'any', 1735999862, 'param', None, 25)
					plugin_obj.params.add_named('ext_param_0', 0, 'float', "MinFreq")
					plugin_obj.params.add_named('ext_param_1', 1, 'float', "MaxFreq")
					plugin_obj.params.add_named('ext_param_2', 0, 'float', "Gate")
					plugin_obj.params.add_named('ext_param_3', 1-speed, 'float', "Speed")
					plugin_obj.params.add_named('ext_param_4', 1, 'float', "CorThrsh")
					plugin_obj.params.add_named('ext_param_5', amount, 'float', "CorAmt")
					plugin_obj.params.add_named('ext_param_6', xtramath.between_to_one(0.001, 0.3, attack), 'float', "CorAtk")
					plugin_obj.params.add_named('ext_param_7', xtramath.between_to_one(0.001, 0.3, release), 'float', "CorRel")
					plugin_obj.params.add_named('ext_param_8', keysdata[0], 'float', "Note00")
					plugin_obj.params.add_named('ext_param_9', keysdata[1], 'float', "Note01")
					plugin_obj.params.add_named('ext_param_10', keysdata[2], 'float', "Note02")
					plugin_obj.params.add_named('ext_param_11', keysdata[3], 'float', "Note03")
					plugin_obj.params.add_named('ext_param_12', keysdata[4], 'float', "Note04")
					plugin_obj.params.add_named('ext_param_13', keysdata[5], 'float', "Note05")
					plugin_obj.params.add_named('ext_param_14', keysdata[6], 'float', "Note06")
					plugin_obj.params.add_named('ext_param_15', keysdata[7], 'float', "Note07")
					plugin_obj.params.add_named('ext_param_16', keysdata[8], 'float', "Note08")
					plugin_obj.params.add_named('ext_param_17', keysdata[9], 'float', "Note09")
					plugin_obj.params.add_named('ext_param_18', keysdata[10], 'float', "Note10")
					plugin_obj.params.add_named('ext_param_19', keysdata[11], 'float', "Note11")
					plugin_obj.params.add_named('ext_param_20', 0, 'float', "MidiMode")
					plugin_obj.params.add_named('ext_param_21', 0, 'float', "BendAmt")
					plugin_obj.params.add_named('ext_param_22', 0, 'float', "VibAmt")
					plugin_obj.params.add_named('ext_param_23', 0.090909, 'float', "VibSpeed")
					plugin_obj.params.add_named('ext_param_24', xtramath.between_to_one(430, 450, calibrate), 'float', "Calib")
					return True
