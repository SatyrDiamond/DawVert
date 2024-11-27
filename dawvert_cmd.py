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

dawvert_core = core.core()
if args.pq == True: dawvert_core.logger_only_plugconv()
if args.q == True: logging.disable(logging.INFO)

if not args.i:
	logger_core.error('Input File Not Specified.')
	exit()
elif not os.path.exists(args.i):
	logger_core.error('Input File Not Found.')
	exit()

if not args.o:
	logger_core.error('Output File Not Specified.')
	exit()

dawvert_intent = core.dawvert_intent()
dawvert_intent.config_load('./__config/config.ini')
dawvert_intent.plugin_set = True
dawvert_intent.input_file = args.i
dawvert_intent.output_file = args.o
dawvert_intent.plugin_input = args.it
dawvert_intent.plugin_output = args.ot
dawvert_intent.plugset_input = args.ips
dawvert_intent.plugset_output = args.ops

if args.y == True: dawvert_intent.flag_overwrite = True
if args.soundfont != None: dawvert_intent.path_soundfonts['global'] = args.soundfont
if args.songnum != None: dawvert_intent.songnum = int(args.songnum)-1
if args.extrafile != None: dawvert_intent.input_params['extra_file'] = args.extrafile
if args.mi2m__output_unused_nle == True: dawvert_intent.flags_compat.append('mi2m-output-unused-nle')
if args.splitter_mode != None: dawvert_intent.splitter_mode = int(args.splitter_mode)
if args.splitter_detect_start != None: dawvert_intent.splitter_detect_start = bool(int(args.splitter_detect_start))

plug_conv.load_plugins()

if not dawvert_core.intent_setplugins(dawvert_intent): exit()

# -------------------------------------------------------------- Output Format --------------------------------------------------------------

dawvert_intent.input_visname = os.path.splitext(os.path.basename(dawvert_intent.input_file))[0]
out_in_file_pathext = os.path.splitext(os.path.basename(dawvert_intent.output_file))
out_file_path = os.path.dirname(dawvert_intent.output_file)
dawvert_intent.set_projname_path()

out_plug_ext = dawvert_core.output_get_extension()
if out_in_file_pathext[1] == '': dawvert_intent.output_file = os.path.join(out_file_path, out_in_file_pathext[0]+'.'+out_plug_ext)

dawvert_intent.create_folder_paths()

filesearcher.add_basepath('projectfile', os.path.dirname(dawvert_intent.input_file))
filesearcher.add_basepath('dawvert', scriptfiledir)

filesearcher.add_searchpath_partial('projectfile', '.', 'projectfile')
filesearcher.add_searchpath_full_append('projectfile', os.path.dirname(dawvert_intent.input_file), None)

filesearcher.add_searchpath_full_filereplace('extracted', dawvert_intent.path_samples['extracted'], None)
filesearcher.add_searchpath_full_filereplace('downloaded', dawvert_intent.path_samples['downloaded'], None)
filesearcher.add_searchpath_full_filereplace('generated', dawvert_intent.path_samples['generated'], None)
filesearcher.add_searchpath_full_filereplace('converted', dawvert_intent.path_samples['converted'], None)
filesearcher.add_searchpath_full_filereplace('external_data', os.path.join(scriptfiledir, '__external_data'), None)

if os.path.isfile(dawvert_intent.output_file) and not dawvert_intent.flag_overwrite:
	user_input = input("File '"+dawvert_intent.output_file+"' already exists. Overwrite? [y/n]")
	if user_input.lower() == 'y': pass
	elif user_input.lower() == 'n': exit()
	else: 
		logger_core.error('Not overwriting - exiting')
		exit()

try: dawvert_core.parse_input(dawvert_intent)
except ProjectFileParserException: exit()

dawvert_core.convert_type_output(dawvert_intent)
dawvert_core.convert_plugins(dawvert_intent)
dawvert_core.parse_output(dawvert_intent)