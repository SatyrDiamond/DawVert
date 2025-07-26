# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_values
from functions import xtramath

#from functions.convproj_compat import fxrack2trackfx
#from functions.convproj_compat import trackfx2fxrack

from functions.convproj_compat import fxchange
from functions.convproj_compat import autopl_addrem
from functions.convproj_compat import changestretch
from functions.convproj_compat import fxrack_moveparams
from functions.convproj_compat import loops_add
from functions.convproj_compat import loops_remove
from functions.convproj_compat import removecut
from functions.convproj_compat import removelanes
from functions.convproj_compat import time_seconds
from functions.convproj_compat import timesigblocks
from functions.convproj_compat import track_pl_add
from functions.convproj_compat import track_pl_del
from functions.convproj_compat import unhybrid
from functions.convproj_compat import sep_nest_audio
from functions.convproj_compat import midi_notes
from functions.convproj_compat import setup_tempocalc

import json
import math

import logging
logger_compat = logging.getLogger('compat')

class song_compat:
	def __init__(self):
		self.finished_processes = []
		self.currenttime = None
		self.current_dawcap = []
		self.tempostore = None

	def process_part(self, process_name, classname, convproj_obj, cvpj_type, in_compat, out_compat, out_type, dawvert_intent):
		if process_name not in self.finished_processes:
			if classname.process(convproj_obj, in_compat, out_compat, out_type, dawvert_intent):
				logger_compat.info(process_name+' Done.')
				self.finished_processes.append(process_name)

	def makecompat(self, convproj_obj, cvpj_type, in_dawinfo, out_dawinfo, out_type, dawvert_intent):
		traits_obj = convproj_obj.traits

		if self.currenttime == None: self.currenttime = traits_obj.time_seconds
		if 'time_seconds' in self.finished_processes: self.currenttime = out_dawinfo.time_seconds

		self.process_part('setup_tempocalc', setup_tempocalc,		convproj_obj, cvpj_type, traits_obj, out_dawinfo, out_type, dawvert_intent)
		self.process_part('fxchange', fxchange,						convproj_obj, cvpj_type, traits_obj, out_dawinfo, out_type, dawvert_intent)

		self.process_part('unhybrid', unhybrid,					   convproj_obj, cvpj_type, traits_obj.track_hybrid, out_dawinfo.track_hybrid, out_type, dawvert_intent)
		self.process_part('removelanes', removelanes,				 convproj_obj, cvpj_type, traits_obj.track_lanes, out_dawinfo, out_type, dawvert_intent)

		if self.currenttime == False:
			self.process_part('autopl_addrem', autopl_addrem,		 convproj_obj, cvpj_type, traits_obj.auto_types, out_dawinfo.auto_types, out_type, dawvert_intent)
			self.process_part('loops_remove', loops_remove,		   convproj_obj, cvpj_type, traits_obj.placement_loop, out_dawinfo.placement_loop, out_type, dawvert_intent)
			self.process_part('sep_nest_audio', sep_nest_audio,	   convproj_obj, cvpj_type, traits_obj.audio_nested, out_dawinfo.audio_nested, out_type, dawvert_intent)
			self.process_part('changestretch', changestretch,		 convproj_obj, cvpj_type, traits_obj.audio_stretch, out_dawinfo.audio_stretch, out_type, dawvert_intent)
			self.process_part('removecut', removecut,				 convproj_obj, cvpj_type, traits_obj.placement_cut, out_dawinfo.placement_cut, out_type, dawvert_intent)
			self.process_part('track_pl_add', track_pl_add,			   convproj_obj, cvpj_type, traits_obj.track_nopl, out_dawinfo.track_nopl, out_type, dawvert_intent)
			self.process_part('loops_add', loops_add,				 convproj_obj, cvpj_type, traits_obj.placement_loop, out_dawinfo.placement_loop, out_type, dawvert_intent)

		self.process_part('midi_notes', midi_notes,				convproj_obj, cvpj_type, traits_obj.notes_midi, out_dawinfo.notes_midi, out_type, dawvert_intent)

		if self.currenttime == False:
			self.process_part('track_pl_del', track_pl_del,			   convproj_obj, cvpj_type, traits_obj.track_nopl, out_dawinfo.track_nopl, out_type, dawvert_intent)

		if cvpj_type in ['r']:
			self.process_part('time_seconds', time_seconds,			   convproj_obj, cvpj_type, traits_obj.time_seconds, out_dawinfo.time_seconds, out_type, dawvert_intent)
