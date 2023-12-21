# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from plugin_plugconv import base as base_plugconv
from plugin_plugconv_extern import base as base_plugconv_extern

import json
import os
import struct
import math
import base64
from functions import data_values
from functions import plugin_vst2
from functions import plugins

______debugtxt______ = False

pl_pc_in = []
pl_pc_in_always = []
pl_pc_out = []
pl_pc_ext = []

def getvisualname(plugidinput):
	if plugidinput[1] == None: return plugidinput[0]+':*'
	else: return plugidinput[0]+':'+plugidinput[1]

def load_plugins():
	global pl_pc_in
	global pl_pc_in_always
	global pl_pc_out
	global pl_pc_ext

	pluglist_plugconv = {}

	dv_pluginclasses = base_plugconv
	dv_pluginclasses_ext = base_plugconv_extern

	for plugconvplugin in dv_pluginclasses.plugins:
		plco_class_data = plugconvplugin()
		try:
			plugtype = plco_class_data.is_dawvert_plugin()
			if plugtype == 'plugconv': 
				pcp_i_data, pcp_o_data, pcp_isoutput, pcp_i_always = plco_class_data.getplugconvinfo()
				if not pcp_isoutput: 
					if pcp_i_always: pl_pc_in_always.append([plco_class_data, pcp_i_data, pcp_o_data])
					else: pl_pc_in.append([plco_class_data, pcp_i_data, pcp_o_data])
				else: pl_pc_out.append([plco_class_data, pcp_i_data, pcp_o_data])
		except: pass


	for plugconvplugin in dv_pluginclasses_ext.plugins:
		plco_class_data = plugconvplugin()
		try:
			plugtype = plco_class_data.is_dawvert_plugin()
			if plugtype == 'plugconv_ext': 
				plugtype, supportedplugs, nativedaw = plco_class_data.getplugconvinfo()
				pl_pc_ext.append([plco_class_data, plugtype, supportedplugs, nativedaw])
		except: pass


	for vispluginlistdata in [[pl_pc_in_always, 'A-Input'], [pl_pc_in, 'Input'], [pl_pc_out, 'Output']]:
		print('[plug_conv] Plugins ('+vispluginlistdata[1]+'): ')
		for pl_pc_in_p in vispluginlistdata[0]:
			visualplugname_in = getvisualname(pl_pc_in_p[1])
			visualplugname_out = getvisualname(pl_pc_in_p[2])
			print('    ['+visualplugname_in+' > '+visualplugname_out+'] ')
		print('')


	print('[plug_conv] Plugins (External): ')
	for pl_pc_ext_p in pl_pc_ext:
		visualplugname = getvisualname(pl_pc_ext_p[1])
		print('    ['+visualplugname+' > '+','.join(pl_pc_ext_p[2])+'] ')
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

def convertpluginconvproj(converted_val, cvpj_l, pluginid, pci_in, cvpj_plugindata, extra_json):
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

			converted_val_p = plugclassinfo[0].convert(cvpj_l, pluginid, cvpj_plugindata, extra_json)

			if converted_val_p < converted_val: converted_val = converted_val_p

			if converted_val == 0: break

	return converted_val

def convproj(cvpjdata, platform_id, in_type, out_type, in_daw, out_daw, 
	out_supportedplugins, out_supportedplugformats, extra_json):

	global pl_pc_in
	global pl_pc_in_always
	global pl_pc_out
	global pl_pc_ext

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

			ext_plug_needed = {}

			for pluginid in plugindataclasses:
				cvpj_plugindata = plugindataclasses[pluginid]
				plugintype_plug = cvpj_plugindata.type_get()

				converted_val = 2

				if plugintype_plug[0] not in out_supportedplugins:

					if ______debugtxt______: print('-------')
	
					if ______debugtxt______: print('- input always')
					converted_val = convertpluginconvproj(converted_val, cvpj_l, pluginid, pl_pc_in_always, cvpj_plugindata, extra_json)

					if ______debugtxt______: print('- input')
					converted_val = convertpluginconvproj(converted_val, cvpj_l, pluginid, pl_pc_in, cvpj_plugindata, extra_json)

					if ______debugtxt______: print('- output')
					converted_val = convertpluginconvproj(converted_val, cvpj_l, pluginid, sep_pl_pc_out__native, cvpj_plugindata, extra_json)

					#print(converted_val)

					if converted_val != 0:
						ext_plug_needed[pluginid] = cvpj_plugindata

					cvpj_plugindata.to_cvpj(cvpj_l, pluginid)

			for pluginid in ext_plug_needed:
				cvpj_plugindata = ext_plug_needed[pluginid]
				plugintype_plug = cvpj_plugindata.type_get()

				ext_conv_val = False

				if not (True in [plugtype_match(plugintype_plug, x) for x in out_supportedplugins]):
					for p_pl_pc_ext in pl_pc_ext:
						ismatched = plugtype_match(plugintype_plug, p_pl_pc_ext[1])
						if ismatched and p_pl_pc_ext[3] != out_daw:
							for plugformat in out_supportedplugformats:
								ext_conv_val = p_pl_pc_ext[0].convert(cvpj_l, pluginid, cvpj_plugindata, extra_json, plugformat)
								if ext_conv_val: break
						if ext_conv_val: break


		return json.dumps(cvpj_l, indent=2)
