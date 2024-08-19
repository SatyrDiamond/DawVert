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

def convproj(convproj_obj, in_dawinfo, out_dawinfo, dv_config):
	plugqueue = []

	for plugin in dv_plugins.plugins_plugconv:
		if in_dawinfo.shortname in plugin.in_daws: plugin.priority = 1

	#indaw_plugs = commalist2plugtypes(in_dawinfo.plugin_included)
	outdaw_plugs = commalist2plugtypes(out_dawinfo.plugin_included)

	norepeat = []

	for pluginid, plugin_obj in convproj_obj.plugins.items():
		converted_val = 2

		for convplug_obj in dv_plugins.iter_plugconv():
			ismatch = True in [plugin_obj.check_wildmatch(x[0], x[1]) for x in convplug_obj.in_plugins]
			correctdaw = (out_dawinfo.shortname in convplug_obj.out_daws) if convplug_obj.out_daws else True
			if ismatch and correctdaw:
				converted_val_p = convplug_obj.object.convert(convproj_obj, plugin_obj, pluginid, dv_config)
				if converted_val_p < converted_val: converted_val = converted_val_p
				if converted_val == 0: break

		ext_conv_val = False
		notsupported = not (True in [plugin_obj.check_wildmatch(x[0], x[1]) for x in outdaw_plugs])

		if converted_val:
			if notsupported:
				extpluglog.extpluglist.clear()
				for pluginfo in dv_plugins.iter_plugconv_ext():
					convplug_obj = pluginfo.object
					ismatch = plugin_obj.check_wildmatch(pluginfo.in_plugin[0], pluginfo.in_plugin[1])
					extmatch = True in [(x in out_dawinfo.plugin_ext) for x in pluginfo.ext_formats]
					catmatch = data_values.list__only_values(pluginfo.plugincat, dv_config.extplug_cat)

					if ismatch and extmatch and catmatch:
						ext_conv_val = convplug_obj.convert(convproj_obj, plugin_obj, pluginid, dv_config, out_dawinfo.plugin_ext)
						if ext_conv_val: break

		if converted_val==2 and not ext_conv_val and notsupported and str(plugin_obj.type) not in norepeat:
			logger_plugconv.warning('No equivalent to "'+str(plugin_obj.type)+'" found or not supported')
			norepeat.append(str(plugin_obj.type))