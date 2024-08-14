# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import argparse
import os
import logging
from objects import core
from functions import plug_conv

from objects.convproj import fileref
cvpj_fileref = fileref.cvpj_fileref

scriptfiledir = os.path.dirname(os.path.realpath(__file__))

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
parser.add_argument("--old-plugins", action='store_true')
parser.add_argument("--splitter-mode")
parser.add_argument("--splitter-detect-start")
parser.add_argument("-y", action='store_true')
parser.add_argument("-q", action='store_true')
args = parser.parse_args()

in_file = args.i
out_file = args.o
in_format = args.it
out_format = args.ot

if not in_file:
	print('[error] Input File Not Specified.')
	exit()
elif not os.path.exists(in_file):
	print('[error] Input File Not Found.')
	exit()

if args.q == True: 
	logging.disable(logging.INFO)

pluginset = 'main'
dawvert_core = core.core()

dawvert_core.config.load('./__config/config.ini')

if args.y == True: core.config_data.flags_core.append('overwrite')
if args.soundfont != None: core.config_data.path_soundfont = args.soundfont
if args.songnum != None: core.config_data.songnum = int(args.songnum)
if args.extrafile != None: core.config_data.path_extrafile = args.extrafile
if args.mi2m__output_unused_nle == True: core.config_data.flags_convproj.append('mi2m-output-unused-nle')
if args.use_experiments_input == True: pluginset = 'experiments'
if args.nonfree_plugins == True: core.config_data.extplug_cat.append('nonfree')
if args.shareware_plugins == True: core.config_data.extplug_cat.append('shareware')
if args.old_plugins == True: core.config_data.extplug_cat.append('old')
if args.splitter_mode != None: core.config_data.splitter_mode = int(args.splitter_mode)
if args.splitter_detect_start != None: core.config_data.splitter_detect_start = bool(int(args.splitter_detect_start))

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

cvpj_fileref.add_searchpath_abs('projectfile', out_file_path)
cvpj_fileref.add_searchpath_file('projectfile', out_file_path)

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

os.makedirs(dawvert_core.config.path_samples_extracted, exist_ok=True)
os.makedirs(dawvert_core.config.path_samples_downloaded, exist_ok=True)
os.makedirs(dawvert_core.config.path_samples_generated, exist_ok=True)
os.makedirs(dawvert_core.config.path_samples_converted, exist_ok=True)

cvpj_fileref.add_searchpath_file('extracted', dawvert_core.config.path_samples_extracted)
cvpj_fileref.add_searchpath_file('downloaded', dawvert_core.config.path_samples_downloaded)
cvpj_fileref.add_searchpath_file('generated', dawvert_core.config.path_samples_generated)
cvpj_fileref.add_searchpath_file('converted', dawvert_core.config.path_samples_converted)
cvpj_fileref.add_searchpath_abs('external_data', os.path.join(scriptfiledir, '__external_data'))
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