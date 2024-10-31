#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import argparse
import os
import logging
from objects import core
from functions import plug_conv
from objects.exceptions import ProjectFileParserException

from objects.convproj import fileref
filesearcher = fileref.filesearcher

logger_core = logging.getLogger('core')

scriptfiledir = os.path.dirname(os.path.realpath(__file__))

print('DawVert: Daw Conversion Tool')

parser = argparse.ArgumentParser()
parser.add_argument("-i", default=None)
parser.add_argument("-it", default=None)
parser.add_argument("-ips", default='main')
parser.add_argument("-o", default=None)
parser.add_argument("-ot", default=None)
parser.add_argument("-ops", default='main')
parser.add_argument("--soundfont", default=None)
parser.add_argument("--songnum", default=1)
parser.add_argument("--extrafile", default=None)
parser.add_argument("--mi2m--output-unused-nle", action='store_true')
parser.add_argument("--nonfree-plugins", action='store_true')
parser.add_argument("--shareware-plugins", action='store_true')
parser.add_argument("--old-plugins", action='store_true')
parser.add_argument("--splitter-mode")
parser.add_argument("--splitter-detect-start")
parser.add_argument("-y", action='store_true')
parser.add_argument("-q", action='store_true')
parser.add_argument("-pq", action='store_true')
args = parser.parse_args()

in_file = args.i
out_file = args.o
in_format = args.it
out_format = args.ot

if not in_file:
	logger_core.error('Input File Not Specified.')
	exit()
elif not os.path.exists(in_file):
	logger_core.error('Input File Not Found.')
	exit()

pluginset = 'main'
opluginset = 'main'
dawvert_core = core.core()

if args.pq == True: 
	dawvert_core.logger_only_plugconv()

if args.q == True: 
	logging.disable(logging.INFO)

dawvert_core.config.load('./__config/config.ini')

if args.y == True: core.config_data.flags_core.append('overwrite')
if args.soundfont != None: core.config_data.path_soundfont = args.soundfont
if args.songnum != None: core.config_data.songnum = int(args.songnum)
if args.extrafile != None: core.config_data.path_extrafile = args.extrafile
if args.mi2m__output_unused_nle == True: core.config_data.flags_convproj.append('mi2m-output-unused-nle')
if args.ips: pluginset = args.ips
if args.ips: opluginset = args.ops
if args.splitter_mode != None: core.config_data.splitter_mode = int(args.splitter_mode)
if args.splitter_detect_start != None: core.config_data.splitter_detect_start = bool(int(args.splitter_detect_start))

# -------------------------------------------------------------- Input Plugin List--------------------------------------------------------------
dawvert_core.input_load_plugins(pluginset)
plug_conv.load_plugins()

# -------------------------------------------------------------- Output Plugin List -------------------------------------------------------------

dawvert_core.output_load_plugins(opluginset)

# -------------------------------------------------------------- Input Format--------------------------------------------------------------

if in_format == None:
	detect_plugin_found = dawvert_core.input_autoset(in_file)
	if detect_plugin_found == None:
		detect_plugin_found = dawvert_core.input_autoset_fileext(in_file)
		if detect_plugin_found == None:
			logger_core.error('Could not identify the input format')
			exit()

else:
	if in_format in dawvert_core.input_get_plugins():
		in_class = dawvert_core.input_set(in_format)
	else:
		logger_core.error('Input format plugin not found')
		exit()

# -------------------------------------------------------------- Output Format --------------------------------------------------------------

if out_format in dawvert_core.output_get_plugins():
	out_class = dawvert_core.output_set(out_format)
else:
	logger_core.error('Output format plugin not found')
	exit()

out_file_nameext = os.path.splitext(os.path.basename(out_file))
out_file_path = os.path.dirname(out_file)

out_plug_ext = dawvert_core.output_get_extension()
if out_file_nameext[1] == '': out_file = os.path.join(out_file_path, out_file_nameext[0]+'.'+out_plug_ext)

# -------------------------------------------------------------- convert --------------------------------------------------------------

file_name = os.path.splitext(os.path.basename(in_file))[0]

dawvert_core.config.set_projname_path(file_name)

os.makedirs(dawvert_core.config.path_samples_extracted, exist_ok=True)
os.makedirs(dawvert_core.config.path_samples_downloaded, exist_ok=True)
os.makedirs(dawvert_core.config.path_samples_generated, exist_ok=True)
os.makedirs(dawvert_core.config.path_samples_converted, exist_ok=True)

filesearcher.add_basepath('projectfile', os.path.dirname(in_file))
filesearcher.add_basepath('dawvert', scriptfiledir)

filesearcher.add_searchpath_partial('projectfile', '.', 'projectfile')
filesearcher.add_searchpath_full_append('projectfile', os.path.dirname(in_file), None)

filesearcher.add_searchpath_full_filereplace('extracted', dawvert_core.config.path_samples_extracted, None)
filesearcher.add_searchpath_full_filereplace('downloaded', dawvert_core.config.path_samples_downloaded, None)
filesearcher.add_searchpath_full_filereplace('generated', dawvert_core.config.path_samples_generated, None)
filesearcher.add_searchpath_full_filereplace('converted', dawvert_core.config.path_samples_converted, None)
filesearcher.add_searchpath_full_filereplace('external_data', os.path.join(scriptfiledir, '__external_data'), None)

# -------------------------------------------------------------- convert --------------------------------------------------------------

if os.path.isfile(out_file) and 'overwrite' not in dawvert_core.config.flags_core:
	user_input = input("File '"+out_file+"' already exists. Overwrite? [y/n]")
	if user_input.lower() == 'y': pass
	elif user_input.lower() == 'n': exit()
	else: 
		logger_core.error('Not overwriting - exiting')
		exit()

try:
	dawvert_core.parse_input(in_file, dawvert_core.config)
except ProjectFileParserException:
	exit()

dawvert_core.convert_type_output(dawvert_core.config)
dawvert_core.convert_plugins(dawvert_core.config)
dawvert_core.parse_output(out_file)