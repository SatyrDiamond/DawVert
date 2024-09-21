# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_values
from functions import extpluglog
from objects import plugts
from plugins import base as dv_plugins
import base64
import json
import logging
import math
import os
import struct

logger_plugconv = logging.getLogger('plugconv')
#from functions import data_values
#from functions_plugin_ext import plugin_vst2
#from functions import plugins

______debugtxt______ = False

plugtransform = plugts.storedtransform()

def load_plugins():
	dv_plugins.load_plugindir('plugconv')
	dv_plugins.load_plugindir('plugconv_ext')
	dv_plugins.load_plugindir('extplug')

# -------------------- convproj --------------------


def commalist2plugtypes(inputdata):
	sep_supp_plugs = []
	for inputpart in inputdata:
		splitdata = inputpart.split(':')
		if len(splitdata) == 2: outputpart = splitdata
		else: outputpart = [splitdata[0], None]
		sep_supp_plugs.append(outputpart)
	return sep_supp_plugs

plugconv_int_selector = dv_plugins.create_selector('plugconv')
plugconv_ext_selector = dv_plugins.create_selector('plugconv_ext')

def convproj(convproj_obj, in_dawinfo, out_dawinfo, out_dawname, dv_config):
	plugqueue = []

	for shortname, dvplugin in plugconv_int_selector.iter_dvp():
		if shortname in dvplugin.prop_obj.in_daws: dvplugin.priority = -1000

	#indaw_plugs = commalist2plugtypes(in_dawinfo.plugin_included)
	outdaw_plugs = commalist2plugtypes(out_dawinfo.plugin_included)

	norepeat = []

	for pluginid, plugin_obj in convproj_obj.plugins.items():
		converted_val = 2

		for shortname, dvplug_obj, prop_obj in plugconv_int_selector.iter():
			ismatch = True in [plugin_obj.check_wildmatch(x[0], x[1]) for x in prop_obj.in_plugins]
			correctdaw = (out_dawname in prop_obj.out_daws) if prop_obj.out_daws else True
			if ismatch and correctdaw:
				converted_val_p = dvplug_obj.convert(convproj_obj, plugin_obj, pluginid, dv_config)
				if converted_val_p < converted_val: converted_val = converted_val_p
				if converted_val == 0: break

		ext_conv_val = False
		notsupported = not (True in [plugin_obj.check_wildmatch(x[0], x[1]) for x in outdaw_plugs])

		if converted_val:
			if notsupported:
				extpluglog.extpluglist.clear()
				for shortname, dvplug_obj, prop_obj in plugconv_ext_selector.iter():
					ismatch = plugin_obj.check_wildmatch(prop_obj.in_plugin[0], prop_obj.in_plugin[1])
					extmatch = True in [(x in out_dawinfo.plugin_ext) for x in prop_obj.ext_formats]
					catmatch = data_values.list__only_values(prop_obj.plugincat, dv_config.extplug_cat)

					if ismatch and extmatch and catmatch:
						ext_conv_val = dvplug_obj.convert(convproj_obj, plugin_obj, pluginid, dv_config, out_dawinfo.plugin_ext)
						if ext_conv_val: break

		if converted_val==2 and not ext_conv_val and notsupported and str(plugin_obj.type) not in norepeat:
			logger_plugconv.warning('No equivalent to "'+str(plugin_obj.type)+'" found or not supported')
			norepeat.append(str(plugin_obj.type))