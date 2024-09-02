# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.file_proj import proj_deflemask
from objects.tracker import pat_multi
from objects import globalstore
from objects import audio_data
import plugins

class input_deflemask(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def getshortname(self): return 'deflemask'
	def gettype(self): return 'm'
	def supported_autodetect(self): return False
	def getdawinfo(self, dawinfo_obj): 
		dawinfo_obj.name = 'Deflemask'
		dawinfo_obj.file_ext = 'dmf'
		dawinfo_obj.track_lanes = True
		dawinfo_obj.track_nopl = True
		dawinfo_obj.fxtype = 'rack'
	def parse(self, convproj_obj, input_file, dv_config):
		project_obj = proj_deflemask.deflemask_project()
		project_obj.load_from_file(input_file)

		globalstore.dataset.load('furnace', './data_main/dataset/furnace.dset')

		patterndata_obj = pat_multi.multi_patsong()
		patterndata_obj.num_rows = project_obj.total_rows_per_pattern
		patterndata_obj.dataset_name = 'furnace'
		patterndata_obj.dataset_cat = 'chip'

		if project_obj.song_name: convproj_obj.metadata.name = project_obj.song_name
		if project_obj.song_author: convproj_obj.metadata.author = project_obj.song_author

		for num, name in enumerate(project_obj.chantype):
			chan_obj = patterndata_obj.add_channel(name)
			chan_obj.name = project_obj.channames[num]

		for channum, dmf_chan in enumerate(project_obj.channels):
			patterndata_obj.orders[channum] = list(dmf_chan.orders)
			chantype = project_obj.chantype[channum]
			for patnum, patdata in dmf_chan.patterns.items():
				pat_obj = patterndata_obj.pattern_add(channum, patnum)

				for r_row, r_dat in enumerate(patdata):
					r_note, r_oct, r_vol, r_inst, r_fx = r_dat

					output_note = None
					output_inst = None

					if r_note == 0 and r_oct == 0: output_note = None
					elif r_note == 100: output_note = 'off'
					else: output_note = (r_note + r_oct*12)-60

					if output_note != None and output_note != 'off':
						if chantype == 'square': output_note += 36
						if chantype == 'opn2': output_note += 12

					if r_inst != -1 and output_note != None: output_inst = r_inst

					pat_obj.cell_note(r_row, output_note, output_inst)

					if r_vol != -1:
						vol_data = r_vol/16 if chantype != 'opn2' else r_vol/127
						pat_obj.cell_param(r_row, 'vol', vol_data)

					#if not all([x == [-1, -1] for x in r_fx]):
					#	for x in r_fx:
					#		if x != [-1, -1]:
					#			print(x)

		used_insts = patterndata_obj.to_cvpj(convproj_obj, 150, project_obj.ticktime2)

		for instname, instnums in used_insts.items():
			for chinst in instnums:
				instnum, channum = chinst
				instid = instname+'_'+str(channum)+'_'+str(instnum)

				inst_obj = convproj_obj.add_instrument(instid)
				inst_obj.fxrack_channel = channum+1

				insttype = patterndata_obj.get_channel_insttype(channum)
				inst_obj.visual.from_dset('furnace', 'chip', insttype, False)

				dmf_inst = project_obj.insts[instnum]

				inst_obj.visual.name = dmf_inst.name

				#print(dmf_inst.mode, insttype, instnum, channum)

				if dmf_inst.mode == 1 and insttype == 'opn2':
					plugin_obj, inst_obj.pluginid = dmf_inst.fm_data.to_cvpj_genid(convproj_obj)

				if dmf_inst.mode == 0:
					plugin_obj, inst_obj.pluginid = convproj_obj.add_plugin_genid('universal', 'synth-osc')
					plugin_obj.role = 'synth'
					osc_data = plugin_obj.osc_add()
					if insttype == 'square': osc_data.prop.shape = 'square'
					if insttype == 'triangle': osc_data.prop.shape = 'triangle'
					if insttype == 'noise': osc_data.prop.shape = 'random'

					volenv = dmf_inst.env_volume.values
					if len(volenv) == 1: inst_obj.params.add('vol', volenv[0]/15, 'float')
					if len(volenv) > 1: plugin_obj.env_blocks_add('vol', volenv, 0.05, 15, dmf_inst.env_volume.looppos, -1)