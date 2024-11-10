# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import json
import struct
from objects import globalstore
from functions import data_values

def create_auto(project_obj, convproj_obj, os_target, os_param, autoloc, mul):
	from objects.file_proj import proj_onlineseq
	auto_found, auto_points = convproj_obj.automation.get_autopoints(autoloc)

	if auto_found:
		for auto_point in auto_points:
			os_marker = proj_onlineseq.onlineseq_marker(None)
			os_marker.pos = auto_point.pos
			os_marker.value = auto_point.value*mul
			os_marker.type = 0 if auto_point.type == 'instant' else 1
			os_marker.id = os_target
			os_marker.param = os_param
			project_obj.markers.append(os_marker)

class output_onlineseq(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'output'
	def get_shortname(self): return 'onlineseq'
	def get_name(self): return 'Online Sequencer'
	def gettype(self): return 'r'
	def get_prop(self, in_dict): 
		in_dict['file_ext'] = 'sequence'
		in_dict['auto_types'] = ['nopl_points']
		in_dict['track_nopl'] = True
		in_dict['plugin_included'] = ['universal:midi','native:onlineseq','universal:synth-osc']
		in_dict['projtype'] = 'r'
	def parse(self, convproj_obj, output_file):
		from objects.file_proj import proj_onlineseq

		convproj_obj.change_timings(4, True)

		project_obj = proj_onlineseq.onlineseq_project()
		project_obj.bpm = int(convproj_obj.params.get('bpm', 120).value)

		globalstore.idvals.load('midi_map', './data_main/dataset/onlineseq_map_midi.csv')
		idvals_onlineseq_inst = globalstore.idvals.get('midi_map')

		repeatedolinst = {}

		for trackid, track_obj in convproj_obj.track__iter():
			onlineseqinst = 43
			midiinst = None

			middlenote = track_obj.datavals.get('middlenote', 0)

			plugin_found, plugin_obj = convproj_obj.plugin__get(track_obj.inst_pluginid)

			midi_found, midi_inst = track_obj.get_midi(convproj_obj)
			
			if not midi_inst.drum: midiinst = midi_inst.patch

			if plugin_found: 
				if plugin_obj.check_wildmatch('universal', 'synth-osc', None):
					if len(plugin_obj.oscs) == 1:
						s_osc = plugin_obj.oscs[0]
						if s_osc.prop.shape == 'sine': onlineseqinst = 13
						if s_osc.prop.shape == 'square': onlineseqinst = 14
						if s_osc.prop.shape == 'triangle': onlineseqinst = 16
						if s_osc.prop.shape == 'saw': onlineseqinst = 15
				
				if idvals_onlineseq_inst: t_instid = idvals_onlineseq_inst.get_idval(str(midiinst), 'outid')
				else: t_instid = None
				if t_instid not in ['null', None]: onlineseqinst = int(t_instid)

			if onlineseqinst not in repeatedolinst: repeatedolinst[onlineseqinst] = 0
			else: repeatedolinst[onlineseqinst] += 1 
			onlineseqnum = int(onlineseqinst + repeatedolinst[onlineseqinst]*10000)

			iparams = proj_onlineseq.onlineseq_inst_param(None)
			iparams.vol = track_obj.params.get('vol', 1).value
			iparams.pan = track_obj.params.get('pan', 0).value

			if track_obj.visual.name: iparams.name = track_obj.visual.name

			for t_pos, t_dur, t_keys, t_vol, t_inst, t_extra, t_auto, t_slide in track_obj.placements.notelist.iter():
				for t_key in t_keys:
					onlineseq_note = [int(t_key+60-middlenote),t_pos,t_dur,onlineseqnum,t_vol]
					project_obj.notes.append(onlineseq_note)

			project_obj.params[onlineseqnum] = iparams

			create_auto(project_obj, convproj_obj, onlineseqnum, 1, ['track', trackid, 'vol'], 1)
			create_auto(project_obj, convproj_obj, onlineseqnum, 2, ['track', trackid, 'pan'], 1)
			create_auto(project_obj, convproj_obj, onlineseqnum, 11, ['track', trackid, 'pitch'], 100)

		create_auto(project_obj, convproj_obj, 0, 0, ['main', 'bpm'], 1)
		create_auto(project_obj, convproj_obj, 0, 8, ['master', 'vol'], 1)

		project_obj.save_to_file(output_file)