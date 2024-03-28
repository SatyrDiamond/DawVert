# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import argparse
import os
from functions import core
from functions import plug_conv

print('DawVert: Daw Conversion Tool')

parser = argparse.ArgumentParser()
parser.add_argument("-i", default=None)
parser.add_argument("-it", default=None)
parser.add_argument("-o", default=None)
parser.add_argument("-ot", default=None)
parser.add_argument("--sample-out-path", default=None)
parser.add_argument("--soundfont", default=None)
parser.add_argument("--songnum", default=1)
parser.add_argument("--extrafile", default=None)
parser.add_argument("--use-experiments-input", action='store_true')
parser.add_argument("--mi2m--output-unused-nle", action='store_true')
parser.add_argument("--nonfree-plugins", action='store_true')
parser.add_argument("--shareware-plugins", action='store_true')
parser.add_argument("-y", action='store_true')
args = parser.parse_args()

in_file = args.i
out_file = args.o
in_format = args.it
out_format = args.ot

if not os.path.exists(in_file):
	print('[error] Input File Not Found.')
	exit()


pluginset = 'main'
dawvert_core = core.core()

if args.y == True: dawvert_core.config.flags_core.append('overwrite')
if args.soundfont != None: dawvert_core.config.path_soundfont_gm = args.soundfont
if args.songnum != None: dawvert_core.config.songnum = int(args.songnum)
if args.extrafile != None: dawvert_core.config.path_extrafile = args.extrafile
if args.mi2m__output_unused_nle == True: dawvert_core.config.flags_convproj.append('mi2m-output-unused-nle')
if args.use_experiments_input == True: pluginset = 'experiments'
if args.nonfree_plugins == True: dawvert_core.config.flags_plugins.append('nonfree')
if args.shareware_plugins == True: dawvert_core.config.flags_plugins.append('shareware')


# -------------------------------------------------------------- Input Plugin List--------------------------------------------------------------
dawvert_core.input_load_plugins(pluginset)
plug_conv.load_plugins()

# -------------------------------------------------------------- Output Plugin List -------------------------------------------------------------

dawvert_core.output_load_plugins()

# -------------------------------------------------------------- Input Format--------------------------------------------------------------

if in_format == None:
	detect_plugin_found = dawvert_core.input_autoset(in_file)
	if detect_plugin_found == None:
		print('[error] could not identify the input format')
		exit()
else:
	if in_format in dawvert_core.input_get_plugins():
		in_class = dawvert_core.input_set(in_format)
	else:
		print('[error] input format plugin not found')
		exit()

# -------------------------------------------------------------- Output Format --------------------------------------------------------------

out_file_nameext = os.path.splitext(os.path.basename(out_file))
out_file_path = os.path.dirname(out_file)

if out_format in dawvert_core.output_get_plugins():
	out_class = dawvert_core.output_set(out_format)
else:
	print('[error] output format plugin not found')
	exit()

out_plug_ext = dawvert_core.output_get_extension()
if out_file_nameext[1] == '': out_file = os.path.join(out_file_path, out_file_nameext[0]+'.'+out_plug_ext)

# -------------------------------------------------------------- convert --------------------------------------------------------------

file_name = os.path.splitext(os.path.basename(in_file))[0]
if args.sample_out_path != None: 
	dawvert_core.config.path_samples_extracted = args.sample_out_path
	dawvert_core.config.path_samples_downloaded = args.sample_out_path
	dawvert_core.config.path_samples_generated = args.sample_out_path
	dawvert_core.config.path_samples_converted = args.sample_out_path
else: 
	dawvert_core.config.path_samples_extracted += file_name + '/'
	dawvert_core.config.path_samples_downloaded += file_name + '/'
	dawvert_core.config.path_samples_generated += file_name + '/'
	dawvert_core.config.path_samples_converted += file_name + '/'

# -------------------------------------------------------------- convert --------------------------------------------------------------

if os.path.isfile(out_file) and 'overwrite' not in dawvert_core.config.flags_core:
	user_input = input("File '"+out_file+"' already exists. Overwrite? [y/n]")
	if user_input.lower() == 'y': pass
	elif user_input.lower() == 'n': exit()
	else: 
		print('Not overwriting - exiting')
		exit()

dawvert_core.parse_input(in_file, dawvert_core.config)
dawvert_core.convert_type_output(dawvert_core.config)
dawvert_core.convert_plugins(dawvert_core.config)
dawvert_core.parse_output(out_file)