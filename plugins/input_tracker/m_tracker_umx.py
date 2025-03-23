# SPDX-FileCopyrightText: 2024 SatyrDiamond and B0ney
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import os
import numpy as np
import math

from objects import format_detect

from plugins.input_tracker.ts_tracker_s3m import input_s3m as s3m
from plugins.input_tracker.ts_tracker_mod import input_mod as mod
from plugins.input_tracker.ts_tracker_it import input_it as it
from plugins.input_tracker.ts_tracker_xm import input_xm as xm

import logging
logger_input = logging.getLogger('input')

FORMATS = ["it", "xm", "s3m", "mod"]

TRACKER_FORMATS = {
	"mod": mod(),
	"s3m": s3m(),
	"it": it(),
	"xm": xm()
}

IGNORE_ERRORS = False

class input_mod(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'

	def get_shortname(self):
		return 'umx'

	def get_name(self):
		return 'Unreal Package Container'

	def get_priority(self):
		return 0

	def get_prop(self, in_dict):
		in_dict['file_ext'] = ['umx']
		in_dict['track_lanes'] = True
		in_dict['audio_filetypes'] = ['wav']
		in_dict['plugin_included'] = ['universal:sampler:single', 'universal:sampler:multi']
		in_dict['projtype'] = 'ts'

	def get_detect_info(self, detectdef_obj):
		detectdef_obj.headers.append([0, b'\xc1\x83\x2a\x9e'])

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj_tracker import umx as proj_umx

		filedetector_obj = format_detect.file_detector()
		filedetector_obj.load_def('data_main/autodetect.xml')

		project_obj = proj_umx.umx_file()
		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		isdetected = None
		if "Music" not in project_obj.nametable:
			logger_input.error("Unreal Package does not contain music")
			exit()
		elif project_obj.nametable:
			firstname = project_obj.nametable[0]

			#outdetected = filedetector_obj.detect_file(dawvert_intent.input_file)
			dawvert_intent_copy = dawvert_intent.copy()
			dawvert_intent_copy.input_mode = 'bytes'
			dawvert_intent_copy.input_data = project_obj.outdata

			if firstname in TRACKER_FORMATS:
				tracker = TRACKER_FORMATS[firstname]
				logger_input.info(f"Detected inner UMX format: { tracker.get_name() }")
				tracker.parse(convproj_obj, dawvert_intent_copy)
			else:
				logger_input.error(firstname+" is not supported")
				exit()