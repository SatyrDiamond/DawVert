# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import xtramath
from objects import globalstore
import json
import plugins
import struct
import zlib

class input_notessimo_v2(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'notessimo_v2'
	
	def get_name(self):
		return 'Notessimo V2'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['plugin_included'] = ['universal:midi']
		in_dict['projtype'] = 'ms'

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj_uncommon import notessimo_v2 as proj_notessimo_v2

		global used_insts
		used_insts = []

		# ---------- CVPJ Start ----------
		convproj_obj.fxtype = 'rack'
		convproj_obj.type = 'ms'

		traits_obj = convproj_obj.traits
		traits_obj.auto_types = ['pl_points']
		traits_obj.track_lanes = True

		convproj_obj.set_timings(4, True)

		globalstore.dataset.load('notessimo_v2', './data_main/dataset/notessimo_v2.dset')
		
		# ---------- File ----------
		project_obj = proj_notessimo_v2.notev2_song()
		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		convproj_obj.metadata.name = project_obj.name
		convproj_obj.metadata.author = project_obj.author

		try:
			t_date, t_time = project_obj.date1.split(', ')
			t_month, t_day, t_year = t_date.split('/')
			t_hours, t_min = t_time.split(':')
			convproj_obj.metadata.t_hours = int(t_hours)
			convproj_obj.metadata.t_minutes = int(t_min)
			convproj_obj.metadata.t_day = int(t_day)
			convproj_obj.metadata.t_month = int(t_month)
			convproj_obj.metadata.t_year = int(t_year)
		except: pass

		cvpj_tracks = []
		for layernum in range(9):
			track_obj = convproj_obj.track__add(str(layernum+1), 'instruments', 1, False) 
			track_obj.visual.name = 'Layer #'+str(layernum+1)

		tempo_len = []
		used_insts = []
		for pat_num, x in enumerate(project_obj.patterns):
			mss_tempo, notelen = xtramath.get_lower_tempo(x.tempo, 4, 170)
			notelen = notelen/4
			tempo_len.append([mss_tempo, notelen])
			if x.notes:
				sceneid = str(pat_num)
				scene_obj = convproj_obj.scene__add(sceneid)
				scene_obj.visual.name = 'Pat #'+str(pat_num+1)
				layers = [[] for x in range(9)]
				for note in x.notes: 
					layers[note.layer].append(note)
					if note.inst not in used_insts: used_insts.append(note.inst)
				for l_num, layer in enumerate(layers):
					if layer:
						trscene_obj = convproj_obj.track__add_scene(str(l_num+1), sceneid, 'main')

						placement_obj = trscene_obj.add_notes()
						placement_obj.visual.name = 'Pat #'+str(pat_num+1)+', Layer #'+str(l_num+1)
						time_obj = placement_obj.time
						time_obj.set_posdur(0, x.size)
						cvpj_notelist = placement_obj.notelist
						for nnn in layer: cvpj_notelist.add_m(str(nnn.inst), (nnn.pos)*notelen, (nnn.dur/4)*notelen, nnn.get_note(), nnn.vol, None)

		fxchan_data = convproj_obj.fx__chan__add(1)
		fxchan_data.visual.name = 'Drums'

		fxnum = 2
		for used_inst in used_insts:
			cvpj_instid = str(used_inst)
			inst_obj = convproj_obj.instrument__add(cvpj_instid)
			inst_obj.visual.from_dset('notessimo_v2', 'inst', cvpj_instid, True)
			midifound = inst_obj.midi.out_inst.from_dataset('notessimo_v2', 'inst', cvpj_instid)
			inst_obj.fxrack_channel = 1 if inst_obj.midi.out_inst.drum else fxnum
			if midifound:
				fxchan_data = convproj_obj.fx__chan__add(fxnum)
				fxchan_data.visual.name = inst_obj.visual.name
				fxchan_data.visual.color = inst_obj.visual.color.copy()
				fxnum += 1

		curpos = 0
		for pat_num in project_obj.order:
			tempo, notelen = tempo_len[pat_num]
			size = ((project_obj.patterns[pat_num].size)-32)*notelen
			scenepl_obj = convproj_obj.scene__add_pl()
			scenepl_obj.position = curpos
			scenepl_obj.duration = size
			scenepl_obj.id = str(pat_num)

			autopl_obj = convproj_obj.automation.add_pl_points(['main','bpm'], 'float')
			autopl_obj.time.set_posdur(curpos, size)

			autopoints_obj = autopl_obj.data
			autopoints_obj.points__add_normal(0, tempo_len[pat_num][0], 0, None)

			curpos += size

		convproj_obj.do_actions.append('do_lanefit')