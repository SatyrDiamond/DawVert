# SPDX-FileCopyrightText: 2022 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import math
import json
import argparse
from plugin_input import base as base_input
from plugin_output import base as base_output
from functions import cvpjconv

parser = argparse.ArgumentParser()
parser.add_argument("input")
parser.add_argument("out_type")
parser.add_argument("output")
parser.add_argument("--extrapath", default=None)
parser.add_argument("--samplefolder", default=None)
args = parser.parse_args()

extra_json = {}

if args.samplefolder != None:
	extra_json['samplefolder'] = args.samplefolder

if args.extrapath != None:
	extra_json['extrapath'] = args.extrapath

cjpjJ = {}

# --------- Input Plugin

chosen_input_plugin = None

for inputplugin in base_input.plugins:
	inputpluginclass = inputplugin()
	formatname = inputpluginclass.getname()
	print('[main] ? ' + formatname)
	detected_format = inputpluginclass.detect(args.input)
	if detected_format == True:
		print('[main] ' + formatname + ' Detected')
		chosen_input_plugin = inputpluginclass
		break

# --------- Output Plugin

chosen_output_plugin = None

for outputplugin in base_output.plugins:
	inputpluginclass = outputplugin()
	shortname = inputpluginclass.getshortname()
	if shortname == args.out_type:
		chosen_output_plugin = inputpluginclass

# --------- Convert

if chosen_input_plugin == None:
	print('[error] No Input Format Detected.')
	exit()
if chosen_output_plugin == None:
	print('[error] Output Type not Found.')
	exit()
else:
	outputcvpjtype = chosen_output_plugin.getcvpjtype()

cjpjJ = chosen_input_plugin.parse(args.input, extra_json)
if cjpjJ == {} or cjpjJ == None:
	print('[error] Input Plugin outputted no json')
	exit()

cjpjJ_l = json.loads(cjpjJ)

with open('debug_plugin_out.cvpj', 'w') as f:
	json.dump(cjpjJ_l, f, indent=2)

inputcvpjtype = cjpjJ_l['cvpjtype']

if inputcvpjtype == 'single':
	print('[main] ConvProj Type: Single')
if inputcvpjtype == 'multiple':
	print('[main] ConvProj Type: Multiple')
if inputcvpjtype == 'multiple_indexed':
	print('[main] ConvProj Type: Multiple, Indexed')
if inputcvpjtype == 'trackany':
	print('[main] ConvProj Type: TrackAny')

if inputcvpjtype == 'single' and outputcvpjtype == 'single':
	cjpjS_forout = cjpjJ
elif inputcvpjtype == 'multiple' and outputcvpjtype == 'single':
	cjpjS_multiple = cjpjJ
	cjpjS_forout = cvpjconv.convert_multiple_single(cjpjJ)
elif inputcvpjtype == 'multiple_indexed' and outputcvpjtype == 'single':
	cjpjS_multiple_indexed = cjpjJ
	cjpjS_multiple = cvpjconv.convert_multipleindexed_multiple(cjpjS_multiple_indexed)
	cjpjS_forout = cvpjconv.convert_multiple_single(cjpjS_multiple)
elif inputcvpjtype == 'trackany' and outputcvpjtype == 'single':
	cjpjS_trackany = cjpjJ
	cjpjS_forout = cvpjconv.convert_trackany_single(cjpjS_trackany)
else:
	print('[error] ConvProj Conversion from '+inputcvpjtype+' to '+outputcvpjtype+' Unsupported')
	exit()

chosen_output_plugin.parse(cjpjS_forout, args.output)