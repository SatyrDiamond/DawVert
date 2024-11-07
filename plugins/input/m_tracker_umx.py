# SPDX-FileCopyrightText: 2024 SatyrDiamond and B0ney
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import os
import numpy as np
import math

from plugins.input.m_tracker_s3m import input_s3m as s3m
from plugins.input.m_tracker_mod import input_mod as mod
from plugins.input.m_tracker_it import input_it as it
from plugins.input.m_tracker_xm import input_xm as xm

import logging
logger_input = logging.getLogger('input')

FORMATS = ["it", "xm", "s3m", "mod"]

TRACKER_FORMATS = {
	"s3m": s3m(),
	"it": it(),
	"xm": xm()
}

IGNORE_ERRORS = False

class input_mod(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def get_shortname(self): return 'umx'
	def get_name(self): return 'Unreal Package Container'
	def get_priority(self): return 0
	def get_prop(self, in_dict):
		in_dict['file_ext'] = ['umx']
		in_dict['track_lanes'] = True
		in_dict['audio_filetypes'] = ['wav']
		in_dict['plugin_included'] = ['universal:sampler:single', 'universal:sampler:multi']
		in_dict['projtype'] = 'm'
	def supported_autodetect(self): return True
	def detect(self, input_file):
		bytestream = open(input_file, 'rb')
		bytesdata = bytestream.read(4)
		if bytesdata == b'\xc1\x83\x2a\x9e': return True
		else: return False

	def parse(self, convproj_obj, input_file, dv_config):
		from objects.file_proj import proj_umx
		project_obj = proj_umx.umx_file()
		if not project_obj.load_from_file(input_file): exit()

		isdetected = None
		if "Music" not in project_obj.nametable:
			logger_input.error("Unreal Package does not contain music")
			exit()
		elif project_obj.nametable:
			firstname = project_obj.nametable[0]
			for (extension, tracker) in TRACKER_FORMATS.items():
				if tracker.detect_bytes(project_obj.outdata):
					isdetected = extension
					logger_input.info(f"Detected inner UMX format: { tracker.get_name() }")
					tracker.parse_bytes(convproj_obj, project_obj.outdata, dv_config, input_file)
			if not isdetected:
				if firstname in FORMATS:
					modo = mod()
					modo.parse_bytes(convproj_obj, project_obj.outdata, dv_config, input_file)
				else:
					logger_input.error(firstname+" is not supported")
					exit()