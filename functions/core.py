# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from plugin_input import base as base_input
from plugin_output import base as base_output
from functions import song_convert
from functions import song_compat
from functions import plug_conv
import platform
import os

typelist = {}
typelist['r'] = 'Regular'
typelist['ri'] = 'RegularIndexed'
typelist['m'] = 'Multiple'
typelist['mi'] = 'MultipleIndexed'
typelist['debug'] = 'debug'

# ------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------- OS Detect ----------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------

platform_architecture = platform.architecture()
if platform_architecture[1] == 'WindowsPE': platform_id = 'win'
else: platform_id = 'lin'

# ------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------- Input Plugins -------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------

pluglist_input = {}
pluglist_input_auto = {}
currentplug_input = [None, None]

def input_load_plugins():
	print('[core] Plugins (Input): ',end='')
	for inputplugin in base_input.plugins:
		in_class_list = inputplugin()
		in_validplugin = False
		try:
			plugtype = in_class_list.is_dawvert_plugin()
			if plugtype == 'input':
				in_validplugin = True
		except: pass
		if in_validplugin == True:
			shortname = in_class_list.getshortname()
			pluglist_input[shortname] = in_class_list
			if in_class_list.supported_autodetect() == True:
				pluglist_input_auto[shortname] = in_class_list
				print(shortname,end='[a] ')
			else:
				print(shortname,end=' ')
	print('')

def input_get_plugins(): 
	return pluglist_input

def input_get_plugins_auto(): 
	return pluglist_input_auto

def input_get_current(): 
	return currentplug_input[1]

def input_set(pluginname): 
	global currentplug_input
	if pluginname in pluglist_input:
		currentplug_input = [
			pluglist_input[pluginname], 
			pluginname, 
			pluglist_input[pluginname].getname(),
			pluglist_input[pluginname].gettype(),
			pluglist_input[pluginname].getdawcapabilities(),
			]
		print('[core] Set input format:',currentplug_input[2],'('+ currentplug_input[1]+')')
		print('[core] Input Format:',currentplug_input[1])
		print('[core] Input DataType:',typelist[currentplug_input[3]])
		return pluginname
	else: return None

def input_autoset(in_file):
	global currentplug_input
	outputname = None
	for autoplugin in pluglist_input_auto:
		temp_in_class = pluglist_input_auto[autoplugin]
		detected_format = temp_in_class.detect(in_file)
		if detected_format == True:
			outputname = temp_in_class.getshortname()
			full_name = temp_in_class.getname()
			input_set(outputname)
			break
	return outputname

# ------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------- Output Plugins -------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------

pluglist_output = {}
currentplug_output = [None, None]

def output_load_plugins():
	print('[core] Plugins (Output): ',end='')
	for outputplugin in base_output.plugins:
		out_class_list = outputplugin()
		out_validplugin = False
		try:
			plugtype = out_class_list.is_dawvert_plugin()
			if plugtype == 'output':
				out_validplugin = True
		except: pass
		if out_validplugin == True:
			shortname = out_class_list.getshortname()
			pluglist_output[shortname] = out_class_list
			print(shortname,end=' ')
	print('')

def output_get_plugins(): 
	return pluglist_output

def output_get_current(): 
	return currentplug_output[1]

def output_set(pluginname): 
	global currentplug_output
	if pluginname in pluglist_output:
		currentplug_output = [
			pluglist_output[pluginname], 
			pluginname, 
			pluglist_output[pluginname].getname(),
			pluglist_output[pluginname].gettype(),
			pluglist_output[pluginname].getdawcapabilities(),
			]
		print('[core] Output Format:',currentplug_output[1])
		print('[core] Output DataType:',typelist[currentplug_output[3]])
		return pluginname
	else: return None

# ------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------- Convert -----------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------


def get_cvpj(extra_json): return convproj_j

def parse_input(in_file, extra_json): 
	global convproj_j
	convproj_j = [currentplug_input[0].parse(in_file, extra_json), currentplug_input[3], currentplug_input[4]]
	if convproj_j == '{}' or convproj_j == None:
		print('[error] Input Plugin outputted no json')
		exit()

def convert_plugins(extra_json): 
	global platform_id
	global convproj_j
	CVPJ_C = plug_conv.convproj(convproj_j[0], platform_id, convproj_j[1], currentplug_output[3], convproj_j[2], currentplug_output[0], extra_json)
	if CVPJ_C != None: convproj_j[0] = CVPJ_C

def convert_type_output(extra_json): 
	in_type = currentplug_input[3]
	out_type = currentplug_output[3]
	in_dawcapabilities = currentplug_input[4]
	out_dawcapabilities = currentplug_output[4]

	print('[core] ' + typelist[in_type] + ' > ' + typelist[out_type])

	if out_type != 'debug':
		convproj_j[0] = song_compat.makecompat(convproj_j[0], in_type, in_dawcapabilities, out_dawcapabilities)

	if in_type == 'ri' and out_type == 'mi': convproj_j[0] = song_convert.ri2mi(convproj_j[0])
	if in_type == 'ri' and out_type == 'r': convproj_j[0] = song_convert.ri2r(convproj_j[0])

	if in_type == 'm' and out_type == 'mi': convproj_j[0] = song_convert.m2mi(convproj_j[0])
	if in_type == 'm' and out_type == 'r': convproj_j[0] = song_convert.m2r(convproj_j[0])

	if in_type == 'r' and out_type == 'm': convproj_j[0] = song_convert.r2m(convproj_j[0])
	if in_type == 'r' and out_type == 'mi': 
		convproj_j[0] = song_convert.r2m(convproj_j[0])
		convproj_j[0] = song_convert.m2mi(convproj_j[0])

	if in_type == 'mi' and out_type == 'm':  convproj_j[0] = song_convert.mi2m(convproj_j[0], extra_json)
	if in_type == 'mi' and out_type == 'r': 
		convproj_j[0] = song_convert.mi2m(convproj_j[0], extra_json)
		convproj_j[0] = song_convert.m2r(convproj_j[0])

	if out_type != 'debug':
		convproj_j[0] = song_compat.makecompat(convproj_j[0], out_type, in_dawcapabilities, out_dawcapabilities)

	convproj_j[0] = song_compat.makecompat_any(convproj_j[0], out_type, in_dawcapabilities, out_dawcapabilities)
	convproj_j[1] = currentplug_output[3]
	convproj_j[2] = currentplug_output[4]

def parse_output(out_file): 
	global convproj_j
	currentplug_output[0].parse(convproj_j[0], out_file)