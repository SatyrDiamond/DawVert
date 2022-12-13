# SPDX-FileCopyrightText: 2022 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import argparse

from plugin_input import base as base_input
from plugin_output import base as base_output
from functions import song_convert
from functions import plug_conv

print('DawVert: Daw Conversion Tool')

parser = argparse.ArgumentParser()
parser.add_argument("-i", default=None)
parser.add_argument("-it", default=None)
parser.add_argument("-o", default=None)
parser.add_argument("-ot", default=None)
#parser.add_argument("--samplefolder", default=None)
parser.add_argument("--soundfont", default=None)
args = parser.parse_args()

in_file = args.i
out_file = args.o
in_format = args.it
out_format = args.ot

extra_json = {}

if args.soundfont != None: extra_json['soundfont'] = args.soundfont
#if args.samplefolder != None: extra_json['samplefolder'] = args.samplefolder

typelist = {}
typelist['r'] = 'Regular'
typelist['ri'] = 'RegularIndexed'
typelist['s'] = 'Seperate'
typelist['m'] = 'Multiple'
typelist['mi'] = 'MultipleIndexed'
typelist['debug'] = 'debug'

# --------- Input Plugin: Get List
pluglist_input = {}
pluglist_input_auto = {}
print('[info] Plugins (Input): ',end='')
for inputplugin in base_input.plugins:
	in_class_list = inputplugin()
	shortname = in_class_list.getshortname()
	pluglist_input[shortname] = in_class_list
	if in_class_list.supported_autodetect() == True:
		pluglist_input_auto[shortname] = in_class_list
		print(shortname,end='[a] ')
	else:
		print(shortname,end=' ')
print('')

# --------- Output Plugin: Get List
pluglist_output = {}
print('[info] Plugins (Output): ',end='')
for outputplugin in base_output.plugins:
	out_class_list = outputplugin()
	shortname = out_class_list.getshortname()
	pluglist_output[shortname] = out_class_list
	print(shortname,end=' ')
print('')

if in_file == None: print('[error] An input file must be specified'); exit()
if out_file == None: print('[error] An output file must be specified'); exit()
if out_format == None: print('[error] An output format must be specified'); exit()

detected_format = False
detect_done = False

# --------- Input Format
if in_format == None:
	for autoplugin in pluglist_input_auto:
		temp_in_class = pluglist_input_auto[autoplugin]
		detected_format = temp_in_class.detect(in_file)
		if detected_format == True:
			in_class = temp_in_class
			in_name = in_class.getname()
			in_shortname = in_class.getshortname()
			in_format = in_shortname
			print('[info] Detected input format:',in_name,'('+ str(in_shortname)+')')
			break
	detect_done = True

if in_format == None:
	if detect_done == True:
		print('[error] could not identify the input format')
		exit()
else:
	if in_format in pluglist_input:
		in_class = pluglist_input[in_format]
	else:
		print('[error] input format plugin not found')
		exit()

# --------- Output Format
if out_format in pluglist_output:
	out_class = pluglist_output[out_format]
else:
	print('[error] output format plugin not found')
	exit()

# --------- Parse to List
in_type = in_class.gettype()
out_type = out_class.gettype()

# --------- Info
print('[info] Input Format:',in_format)
print('[info] Input DataType:',typelist[in_type])
print('[info] Output Format:',out_format)
print('[info] Output DataType:',typelist[out_type])
typeconvsupported = False

if in_type == out_type: typeconvsupported = True
if out_type == 'debug': typeconvsupported = True

if in_type == 's' and out_type == 'r': typeconvsupported = True

if in_type == 'm' and out_type == 'mi': typeconvsupported = True
if in_type == 'm' and out_type == 'r': typeconvsupported = True
if in_type == 'm' and out_type == 's': typeconvsupported = True

if in_type == 'r' and out_type == 's': typeconvsupported = True
if in_type == 'r' and out_type == 'm': typeconvsupported = True
if in_type == 'r' and out_type == 'mi': typeconvsupported = True

if in_type == 'mi' and out_type == 'm': typeconvsupported = True
if in_type == 'mi' and out_type == 'r': typeconvsupported = True
if in_type == 'mi' and out_type == 's': typeconvsupported = True

if typeconvsupported == False:
	print('[info] type Conversion from ' + typelist[in_type] + ' to ' + typelist[out_type] + ' not supported.')
	exit()

# --------- Parse to List
CVPJ_j = in_class.parse(in_file, extra_json)
if CVPJ_j == '{}' or CVPJ_j == None:
	print('[error] Input Plugin outputted no json')
	exit()

# --------- Plugins

CVPJ_C = plug_conv.convproj(CVPJ_j, in_type, out_type, out_format, extra_json)
if CVPJ_C != None: CVPJ_j = CVPJ_C

# --------- Convert Type -- mi <> m <> r

print('[info] ' + typelist[in_type] + ' > ' + typelist[out_type])

if in_type == 's' and out_type == 'r': 
	CVPJ_j = song_convert.a2r(CVPJ_j)

if in_type == 'm' and out_type == 'mi': 
	CVPJ_j = song_convert.m2mi(CVPJ_j)
if in_type == 'm' and out_type == 'r': 
	CVPJ_j = song_convert.m2r(CVPJ_j)
if in_type == 'm' and out_type == 's': 
	CVPJ_j = song_convert.m2r(CVPJ_j)
	CVPJ_j = song_convert.r2a(CVPJ_j)

if in_type == 'r' and out_type == 'm': 
	CVPJ_j = song_convert.r2m(CVPJ_j)
if in_type == 'r' and out_type == 'mi': 
	CVPJ_j = song_convert.r2m(CVPJ_j)
	CVPJ_j = song_convert.m2mi(CVPJ_j)
if in_type == 'r' and out_type == 's': 
	CVPJ_j = song_convert.r2a(CVPJ_j)

if in_type == 'mi' and out_type == 'm': 
	CVPJ_j = song_convert.mi2m(CVPJ_j)
if in_type == 'mi' and out_type == 'r': 
	CVPJ_j = song_convert.mi2m(CVPJ_j)
	CVPJ_j = song_convert.m2r(CVPJ_j)
if in_type == 'mi' and out_type == 's': 
	CVPJ_j = song_convert.mi2m(CVPJ_j)
	CVPJ_j = song_convert.m2r(CVPJ_j)
	CVPJ_j = song_convert.r2a(CVPJ_j)

# --------- Output

out_class.parse(CVPJ_j, out_file)
