# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_values
from plugins import base as dv_plugins
from objects.plugin_manu import plugin_conv
import base64
import json
import logging
import math
import os
import struct

logger_plugconv = logging.getLogger('plugconv')

______debugtxt______ = False

def load_plugins():
	dv_plugins.load_plugindir('plugconv', '')
	dv_plugins.load_plugindir('plugconv_ext', '')
	dv_plugins.load_plugindir('extplug', '')

# -------------------- convproj --------------------

#def commalist2plugtypes(inputdata):
#	sep_supp_plugs = []
#	for inputpart in inputdata:
#		splitdata = inputpart.split(':')
#		if len(splitdata) == 3: outputpart = splitdata
#		elif len(splitdata) == 2: outputpart = [splitdata[0], splitdata[1], None]
#		else: outputpart = [splitdata[0], None, None]
#		sep_supp_plugs.append(outputpart)
#	return sep_supp_plugs

plugconv_int_selector = dv_plugins.create_selector('plugconv')

def convproj(convproj_obj, in_dawinfo, out_dawinfo, out_dawname, in_dawname, dawvert_intent):

	plugin_conv_obj = plugin_conv.convproj_plug_conv()
	plugin_conv_obj.storage_pstr(os.path.join('data_main','plugstatets_index.json'))
	plugin_conv_obj.current_daw_in = in_dawname
	plugin_conv_obj.current_daw_out = out_dawname
	for pi in in_dawinfo.plugin_included: plugin_conv_obj.add_supported_plugin_in(pi)
	for pi in out_dawinfo.plugin_included: plugin_conv_obj.add_supported_plugin_out(pi)
	plugin_conv_obj.set_active()

	#norepeat = []

	for pluginid, plugin_obj in convproj_obj.plugins.items():

		is_external = plugin_obj.check_wildmatch('external', None, None)
#
	#	if is_external:
	#		plugin_obj.external_make_compat(convproj_obj, out_dawinfo.plugin_ext)

		if not is_external:
			#print(plugin_obj.type)
			plugin_conv_obj.convert_plugin(convproj_obj, plugin_obj, pluginid)
			#plugin_obj.params.debugtxt()
