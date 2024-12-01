# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_values
from functions import xtramath

#from functions_compat import fxrack2trackfx
#from functions_compat import trackfx2fxrack

from functions_compat import fxchange

from functions_compat import autopl_addrem
from functions_compat import changestretch
from functions_compat import fxrack_moveparams
from functions_compat import loops_add
from functions_compat import loops_remove
from functions_compat import removecut
from functions_compat import removelanes
from functions_compat import time_seconds
from functions_compat import timesigblocks
from functions_compat import nopl_track
from functions_compat import unhybrid
from functions_compat import sep_nest_audio

import json
import math

import logging
logger_compat = logging.getLogger('compat')


class song_compat:
	def __init__(self):
		self.finished_processes = []
		self.currenttime = None
		self.current_dawcap = []

	def process_part(self, process_name, classname, convproj_obj, cvpj_type, in_compat, out_compat, out_type, dawvert_intent):
		if process_name not in self.finished_processes:
			if classname.process(convproj_obj, in_compat, out_compat, out_type, dawvert_intent):
				logger_compat.info(process_name+' Done.')
				self.finished_processes.append(process_name)

	def makecompat(self, convproj_obj, cvpj_type, in_dawinfo, out_dawinfo, out_type, dawvert_intent):
		if self.currenttime == None: self.currenttime = in_dawinfo.time_seconds
		if 'time_seconds' in self.finished_processes: self.currenttime = out_dawinfo.time_seconds

		self.process_part('fxchange', fxchange,						convproj_obj, cvpj_type, in_dawinfo, out_dawinfo, out_type, dawvert_intent)

		self.process_part('unhybrid', unhybrid,					   convproj_obj, cvpj_type, in_dawinfo.track_hybrid, out_dawinfo.track_hybrid, out_type, dawvert_intent)
		self.process_part('removelanes', removelanes,				 convproj_obj, cvpj_type, in_dawinfo.track_lanes, out_dawinfo, out_type, dawvert_intent)

		if self.currenttime == False:
			self.process_part('autopl_addrem', autopl_addrem,		 convproj_obj, cvpj_type, in_dawinfo.auto_types, out_dawinfo.auto_types, out_type, dawvert_intent)
			self.process_part('loops_remove', loops_remove,		   convproj_obj, cvpj_type, in_dawinfo.placement_loop, out_dawinfo.placement_loop, out_type, dawvert_intent)
			self.process_part('sep_nest_audio', sep_nest_audio,	   convproj_obj, cvpj_type, in_dawinfo.audio_nested, out_dawinfo.audio_nested, out_type, dawvert_intent)
			self.process_part('changestretch', changestretch,		 convproj_obj, cvpj_type, in_dawinfo.audio_stretch, out_dawinfo.audio_stretch, out_type, dawvert_intent)
			self.process_part('removecut', removecut,				 convproj_obj, cvpj_type, in_dawinfo.placement_cut, out_dawinfo.placement_cut, out_type, dawvert_intent)
			self.process_part('loops_add', loops_add,				 convproj_obj, cvpj_type, in_dawinfo.placement_loop, out_dawinfo.placement_loop, out_type, dawvert_intent)
			self.process_part('nopl_track', nopl_track,			   convproj_obj, cvpj_type, in_dawinfo.track_nopl, out_dawinfo.track_nopl, out_type, dawvert_intent)

		if cvpj_type in ['r']:
			self.process_part('time_seconds', time_seconds,			   convproj_obj, cvpj_type, in_dawinfo.time_seconds, out_dawinfo.time_seconds, out_type, dawvert_intent)