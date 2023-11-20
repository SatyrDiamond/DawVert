# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from plugin_plugconv import base as base_plugconv

import json
import os
import struct
import math
import base64
from functions import data_values
from functions import plugin_vst2
from functions import plugins

from functions_plugparams import data_vc2xml
from functions_plugparams import params_various_fx
from functions_plugparams import params_vital


______debugtxt______ = False


pl_pc_in = []
pl_pc_in_always = []
pl_pc_out = []

def getvisualname(plugidinput):
	if plugidinput[1] == None: return plugidinput[0]+':*'
	else: return plugidinput[0]+':'+plugidinput[1]

def load_plugins():
	global pl_pc_in
	global pl_pc_in_always
	global pl_pc_out
	pluglist_plugconv = {}

	dv_pluginclasses = base_plugconv

	for plugconvplugin in dv_pluginclasses.plugins:
		plco_class_list = plugconvplugin()
		try:
			plugtype = plco_class_list.is_dawvert_plugin()
			if plugtype == 'plugconv': 
				pcp_i_data, pcp_o_data, pcp_isoutput, pcp_i_always = plco_class_list.getplugconvinfo()
				if not pcp_isoutput: 
					if pcp_i_always: pl_pc_in_always.append([plco_class_list, pcp_i_data, pcp_o_data])
					else: pl_pc_in.append([plco_class_list, pcp_i_data, pcp_o_data])
				else: pl_pc_out.append([plco_class_list, pcp_i_data, pcp_o_data])
		except: pass

	for vispluginlistdata in [[pl_pc_in_always, 'A-Input'], [pl_pc_in, 'Input'], [pl_pc_out, 'Output']]:
		print('[plug_conv] Plugins ('+vispluginlistdata[1]+'): ')
		for pl_pc_in_p in vispluginlistdata[0]:
			visualplugname_in = getvisualname(pl_pc_in_p[1])
			visualplugname_out = getvisualname(pl_pc_in_p[2])
			print('    ['+visualplugname_in+' > '+visualplugname_out+'] ')
		print('')




# -------------------- convproj --------------------



def plugtype_match(first, second):
	if ______debugtxt______: print(first, second, first[0] == second[0], first[1] == second[1], second[1] == None)
	outval = False
	if first == second: outval = True
	if first[0] == second[0] and second[1] == None: outval = True

	if first[0] == first[1]: outval = False

	return outval

def commalist2plugtypes(inputdata):
	sep_supp_plugs = []
	for inputpart in inputdata:
		splitdata = inputpart.split(':')
		if len(splitdata) == 2: outputpart = splitdata
		else: outputpart = [splitdata[0], None]
		sep_supp_plugs.append(outputpart)
	return sep_supp_plugs

def convertpluginconvproj(cvpj_l, pluginid, pci_in, cvpj_plugindata, extra_json):
	is_converted = False 
	plugintype = cvpj_plugindata.type_get()

	for plugclassinfo in pci_in:
		ismatched = plugtype_match(plugintype, plugclassinfo[1][0:2])
		#if ______debugtxt______: 
		#	visualplugname_in = getvisualname(plugclassinfo[1])
		#	visualplugname_out = getvisualname(plugclassinfo[2])
		#	print('convertpluginconvproj -------------', ismatched, plugintype, 
		#	'    ['+visualplugname_in+' > '+visualplugname_out+'] ')

		if ismatched == True:
			#visualplugname_in = getvisualname(plugclassinfo[1])
			#visualplugname_out = getvisualname(plugclassinfo[2])
			#print('convertpluginconvproj -------------', ismatched, plugintype, 
			#'    ['+visualplugname_in+' > '+visualplugname_out+'] ')

			is_converted = plugclassinfo[0].convert(cvpj_l, pluginid, cvpj_plugindata, extra_json)
			if is_converted == True: break

	return is_converted

def convproj(cvpjdata, platform_id, in_type, out_type, in_daw, out_daw, 
	out_supportedplugins, out_getsupportedplugformats, extra_json):

	global pl_pc_in
	global pl_pc_in_always
	global pl_pc_out

	out_supportedplugins = commalist2plugtypes(out_supportedplugins)

	#out_daw = 'lmms'

	sep_pl_pc_out__native = []
	sep_pl_pc_out__plugins = {}

	for cpv in pl_pc_out:
		if cpv[2][2] == out_daw: sep_pl_pc_out__native.append(cpv)
		else: 
			supplugtype = cpv[2][0]
			if supplugtype not in sep_pl_pc_out__plugins: sep_pl_pc_out__plugins[supplugtype] = []
			sep_pl_pc_out__plugins[supplugtype].append(cpv)

	cvpj_l = json.loads(cvpjdata)
	if out_type != 'debug':
		if 'plugins' in cvpj_l:

			plugindataclasses = {}
			for pluginid in cvpj_l['plugins']:
				plugindataclasses[pluginid] = plugins.cvpj_plugin('cvpj', cvpj_l, pluginid)

			for pluginid in plugindataclasses:
				cvpj_plugindata = plugindataclasses[pluginid]
				plugintype_plug = cvpj_plugindata.type_get()

				if plugintype_plug[0] not in out_getsupportedplugformats:

					if ______debugtxt______: print('-------')
	
					if ______debugtxt______: print('- input always')
					is_converted = convertpluginconvproj(cvpj_l, pluginid, pl_pc_in_always, cvpj_plugindata, extra_json)


					if ______debugtxt______: print('- input')
					is_converted = convertpluginconvproj(cvpj_l, pluginid, pl_pc_in, cvpj_plugindata, extra_json)

					if ______debugtxt______: print('- output')
					is_converted = convertpluginconvproj(cvpj_l, pluginid, sep_pl_pc_out__native, cvpj_plugindata, extra_json)

					if is_converted != True:
						is_plugin_unsupported = cvpj_plugindata.type_get() not in out_supportedplugins
					#	if ______debugtxt______: print('---pluugin not supported:', is_plugin_unsupported)

						if is_plugin_unsupported:
							for out_getsupportedplugformat in out_getsupportedplugformats:
								if out_getsupportedplugformat in sep_pl_pc_out__plugins:
									is_converted = convertpluginconvproj(cvpj_l, pluginid, sep_pl_pc_out__plugins[out_getsupportedplugformat], cvpj_plugindata, extra_json)

					cvpj_plugindata.to_cvpj(cvpj_l, pluginid)

		return json.dumps(cvpj_l, indent=2)
