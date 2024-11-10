# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import os.path

endtxt = ['', '4OP', '2OP']
panvals = [1, 0, -1]
maincolor = [0.39, 0.16, 0.78]

class input_sop(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def get_shortname(self): return 'adlib_sop'
	def get_name(self): return 'Note Sequencer'
	def get_priority(self): return 0
	def get_prop(self, in_dict): 
		in_dict['file_ext'] = ['sop']
		in_dict['auto_types'] = ['nopl_ticks']
		in_dict['track_nopl'] = True
		in_dict['plugin_included'] = ['chip:fm:opl2','chip:fm:opl3']
		in_dict['projtype'] = 'rm'
	def supported_autodetect(self): return True
	def detect(self, input_file):
		bytestream = open(input_file, 'rb')
		bytestream.seek(0)
		bytesdata = bytestream.read(7)
		if bytesdata == b'sopepos': return True
		else: return False
	def parse(self, convproj_obj, input_file, dv_config):
		from objects.file_proj import proj_adlib_sop

		song_file = open(input_file, 'rb')

		convproj_obj.type = 'rm'
		
		project_obj = proj_adlib_sop.adlib_sop_project()
		if not project_obj.load_from_file(input_file): exit()

		convproj_obj.set_timings(project_obj.tickBeat, False)
		convproj_obj.metadata.name = project_obj.title
		convproj_obj.metadata.comment_text = project_obj.comment
		convproj_obj.params.add('bpm', project_obj.basicTempo, 'float')

		# Instruments
		sop_data_inst = []
		for instnum, opli in enumerate(project_obj.insts):
			cvpj_instname = str(instnum)
			inst_obj = convproj_obj.instrument__add(cvpj_instname)
			inst_obj.pluginid = cvpj_instname
			inst_obj.visual.name = opli.name_long if not opli.name_long else opli.name
			inst_obj.visual.color.set_float(maincolor)
			inst_obj.is_drum = opli.perc_type!=0
			opli.to_cvpj(convproj_obj, cvpj_instname)

		for tracknum, soptrack in enumerate(project_obj.tracks):
			trackname_endtext = endtxt[soptrack.chanmode]

			cvpj_trackid = str(tracknum)
			track_obj = convproj_obj.track__add(cvpj_trackid, 'instruments', 0, False)
			track_obj.visual.name = '#'+str(cvpj_trackid)+' '+str()+trackname_endtext
			track_obj.visual.color.set_float(maincolor)
			
			curtick = 0
			instpos = []
			for event in soptrack.events:
				curtick += event[0]
				if event[1] == 'VOL': 
					convproj_obj.automation.add_autotick(['track', cvpj_trackid, 'vol'], 'float', curtick, event[2]/127)

				if event[1] == 'PAN': 
					convproj_obj.automation.add_autotick(['track', cvpj_trackid, 'pan'], 'float', curtick, panvals[event[2]])

				if event[1] == 'INST': 
					instpos.append([curtick, str(event[2])])

				if event[1] == 'NOTE': 
					track_obj.placements.notelist.add_m(None, curtick, event[3], event[2]-60, 1, {})

			track_obj.placements.notelist.add_instpos(instpos)

		for event in project_obj.controltrack:
			curtick += event[0]
			if event[1] == 'TEMPO': 
				convproj_obj.automation.add_autotick(['main', 'bpm'], 'float', curtick, event[2])
			if event[1] == 'GVOL': 
				convproj_obj.automation.add_autotick(['master', 'vol'], 'float', curtick, event[2]/127)

		convproj_obj.timesig = [project_obj.beatMeasure, 4]
		convproj_obj.do_actions.append('do_addloop')
		convproj_obj.do_actions.append('do_singlenotelistcut')