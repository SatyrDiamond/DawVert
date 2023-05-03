# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import argparse
import os
from functions import core

print('DawVert: Daw Conversion Tool')

parser = argparse.ArgumentParser()
parser.add_argument("-i", default=None)
parser.add_argument("-it", default=None)
parser.add_argument("-o", default=None)
parser.add_argument("-ot", default=None)
parser.add_argument("--samplefolder", default=None)
parser.add_argument("--soundfont", default=None)
parser.add_argument("--songnum", default=1)
parser.add_argument("--extrafile", default=None)
parser.add_argument("--use-experiments-input", action='store_true')
parser.add_argument("--mi2m--output-unused-nle", action='store_true')
parser.add_argument("-y", action='store_true')
args = parser.parse_args()

in_file = args.i
out_file = args.o
in_format = args.it
out_format = args.ot

extra_json = {}

do_overwrite = False

if args.y == True: do_overwrite = True
if args.soundfont != None: extra_json['soundfont'] = args.soundfont
if args.samplefolder != None: extra_json['samplefolder'] = args.samplefolder
if args.songnum != None: extra_json['songnum'] = args.songnum
if args.extrafile != None: extra_json['extrafile'] = args.extrafile
if args.mi2m__output_unused_nle == True: extra_json['mi2m-output-unused-nle'] = True

# -------------------------------------------------------------- Input Plugin List--------------------------------------------------------------

core.input_load_plugins()

# -------------------------------------------------------------- Output Plugin List -------------------------------------------------------------

core.output_load_plugins()

# -------------------------------------------------------------- Input Format--------------------------------------------------------------

if in_format == None:
	detect_plugin_found = core.input_autoset(in_file)
	if detect_plugin_found == None:
		print('[error] could not identify the input format')
		exit()
else:
	if in_format in core.input_get_plugins():
		in_class = core.input_set(in_format)
	else:
		print('[error] input format plugin not found')
		exit()

# -------------------------------------------------------------- Output Format --------------------------------------------------------------

if out_format in core.output_get_plugins():
	out_class = core.output_set(out_format)
else:
	print('[error] output format plugin not found')
	exit()

# -------------------------------------------------------------- convert --------------------------------------------------------------

if os.path.isfile(out_file) and do_overwrite == False:
	user_input = input("File '"+out_file+"' already exists. Overwrite? [y/n]")
	if user_input.lower() == 'y': pass
	elif user_input.lower() == 'n': exit()
	else: 
		print('Not overwriting - exiting')
		exit()

core.parse_input(in_file, extra_json)
core.convert_plugins(extra_json)
core.convert_type_output(extra_json)
core.parse_output(out_file)