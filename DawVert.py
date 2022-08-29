# SPDX-FileCopyrightText: 2022 Colby Ray
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import math
import json
import argparse
from termcolor import colored
from plugin_input import base as base_input
from plugin_output import base as base_output
from functions import cvpjconv

def textprint(text):
	print('DawVert | '+text)

def textprint_extra(textcat,text):
	textprint(textcat+' | '+text)

parser = argparse.ArgumentParser()
parser.add_argument("input")
parser.add_argument("out_type")
parser.add_argument("output")
args = parser.parse_args()

convproj_json = {}

# Detect Input

detected_input_plugin = None

for inputplugin in base_input.plugins:
	inputpluginclass = inputplugin()
	formatname = inputpluginclass.getname()
	textprint_extra('Identifier-Input', '? ' + formatname)
	detected_format = inputpluginclass.detect(args.input)
	if detected_format == True:
		textprint_extra('Identifier-Input', formatname + ' Detected')
		detected_input_plugin = inputpluginclass
		break

if detected_input_plugin != None:
	convproj_json = detected_input_plugin.parse(args.input)
else:
	textprint_extra('Main', 'No Input Format Detected.')
	exit()

if convproj_json == {} or convproj_json == None:
	textprint_extra('Main', 'Plugin outputted no json')
	exit()

convproj_json_list = json.loads(convproj_json)

if convproj_json_list['convprojtype'] == 'single':
	print('DawVert | ConvProj Type: Single')
elif convproj_json_list['convprojtype'] == 'multiple':
	convproj_json = cvpjconv.convert_multiple_single(convproj_json)
else:
	print('DawVert | ConvProj Type Unsupported')
	exit()

for outputplugin in base_output.plugins:
	outputpluginclass = outputplugin()
	shortname = outputpluginclass.getshortname()
	if shortname == args.out_type:
		outputpluginclass.parse(convproj_json, args.output)
