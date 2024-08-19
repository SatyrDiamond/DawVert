# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions_plugin_cvpj import params_fm
from functions import data_bytes
from functions import data_values
from objects import globalstore
from objects.file_proj import proj_adlib_rol
from objects.file import adlib_bnk

import plugins
import json

class input_adlib_rol(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def getshortname(self): return 'adlib_rol'
	def gettype(self): return 'rm'
	def getdawinfo(self, dawinfo_obj): 
		dawinfo_obj.name = 'AdLib Visual Composer'
		dawinfo_obj.file_ext = 'rol'
		dawinfo_obj.auto_types = ['nopl_ticks']
		dawinfo_obj.track_nopl = True
		dawinfo_obj.plugin_included = ['fm:opl2']
	def supported_autodetect(self): return True
	def detect(self, input_file):
		bytestream = open(input_file, 'rb')
		bytestream.seek(4)
		bytesdata = bytestream.read(40)
		if bytesdata == b'\\roll\\default\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00': return True
		else: return False
	def parse(self, convproj_obj, input_file, dv_config):
		convproj_obj.type = 'rm'

		project_obj = proj_adlib_rol.adlib_rol_project()
		project_obj.load_from_file(input_file)

		globalstore.dataset.load('adlib_rol', './data_main/dataset/adlib_rol.dset')

		if dv_config.path_extrafile:
			adlibbnk_obj = adlib_bnk.bnk_file()
			adlibbnk_obj.read_file(dv_config.path_extrafile)
			for instnum, used in enumerate(adlibbnk_obj.used):

				if used:
					instname = adlibbnk_obj.names[instnum].replace(" ", "")
					instname_upper = instname.upper()

					inst_obj = convproj_obj.add_instrument(instname_upper)
					midifound = inst_obj.from_dataset('adlib_rol', 'inst', instname_upper, True)
					if midifound: inst_obj.to_midi_noplug()

					inst_obj.pluginid = instname_upper
					opli = adlibbnk_obj.get_inst_index(instnum)
					opli.to_cvpj(convproj_obj, inst_obj.pluginid)

		else:
			instlist = globalstore.dataset.get_cat('adlib_rol', 'inst')

			if instlist:
				for instid in instlist.objects.list():
					instname_upper = instid.upper()
					inst_obj = convproj_obj.add_instrument(instname_upper)
					midifound = inst_obj.from_dataset('adlib_rol', 'inst', instname_upper, True)
					if midifound: inst_obj.to_midi(convproj_obj, instname_upper, True)

		convproj_obj.set_timings(project_obj.tickBeat, False)

		bpm = project_obj.track_tempo.tempo
		convproj_obj.params.add('bpm', bpm, 'float')
		for pos, bpmmod in project_obj.track_tempo.events: 
			convproj_obj.automation.add_autotick(['main', 'bpm'], 'float', pos, bpmmod*bpm)

		for tracknum, rol_track in enumerate(project_obj.tracks):
			cvpj_trackid = 'track'+str(tracknum+1)
			track_obj = convproj_obj.add_track(cvpj_trackid, 'instruments', 0, False)
			track_obj.visual.name = rol_track.voice.name

			curtrackpos = 0
			for note, pos in rol_track.voice.events:
				if note >= 12: track_obj.placements.notelist.add_m(None, curtrackpos, pos, note-48-12, 1, {})
				curtrackpos += pos

			upper_timbre = [[i, p.upper()] for i, p in rol_track.timbre.events.copy()]
			track_obj.placements.notelist.add_instpos(upper_timbre)
			for pos, val in rol_track.volume.events: convproj_obj.automation.add_autotick(['track', cvpj_trackid, 'vol'], 'float', pos, val)
			for pos, val in rol_track.pitch.events: convproj_obj.automation.add_autotick(['track', cvpj_trackid, 'pitch'], 'float', pos, val)

		convproj_obj.do_actions.append('do_addloop')
		convproj_obj.do_actions.append('do_singlenotelistcut')
		convproj_obj.timesig = [project_obj.beatMeasure, 4]
