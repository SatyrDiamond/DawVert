# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects import globalstore
from io import BytesIO
import json
import plugins
import struct
from objects.exceptions import ProjectFileParserException

def getval(i_val):
	if i_val == 91: i_val = 11
	elif i_val == 11: i_val = 91
	elif i_val == -3: i_val = 92
	elif i_val == -2: i_val = 93
	return i_val

midi_inst = {
	'paint': [5,0,3,4,9,14,11,13,1,12]
}

class input_petaporon(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def get_shortname(self): return 'petaporon'
	def get_name(self): return 'Petaporon'
	def get_priority(self): return 0
	def supported_autodetect(self): return False
	def get_prop(self, in_dict): 
		in_dict['file_ext'] = ['json']
		in_dict['file_ext_detect'] = False
		in_dict['track_nopl'] = True
		in_dict['plugin_included'] = ['universal:synth-osc']
	def parse(self, convproj_obj, input_file, dv_config):
		from objects import colors
		bytestream = open(input_file, 'r')
		
		try:
			petapo_data = json.load(bytestream)
		except UnicodeDecodeError:
			raise ProjectFileParserException('petaporon: File is not text')
		except json.decoder.JSONDecodeError as t:
			raise ProjectFileParserException('petaporon: JSON parsing error: '+str(t))

		convproj_obj.type = 'r'
		convproj_obj.set_timings(4, True)

		peta_notedata = petapo_data['n'].encode('ascii')
		peta_noteints = struct.unpack("B"*len(peta_notedata), peta_notedata)
		peta_instset = petapo_data['i']
		bio_peta_notebytes = BytesIO(bytes(peta_noteints))

		peta_notelists = [[] for _ in range(10)]

		globalstore.dataset.load('petaporon', './data_main/dataset/petaporon.dset')
		colordata = colors.colorset.from_dataset('petaporon', 'inst', 'main')

		for _ in range(len(peta_noteints)//5):
			partdata = bio_peta_notebytes.read(5)
			peta_note = getval(partdata[0]-35)
			peta_inst = getval(partdata[1]-35)
			peta_len = getval(partdata[2]-35)
			peta_poshigh = getval(partdata[3]-35)
			peta_poslow = getval(partdata[4]-35)
			peta_pos = peta_poslow+(peta_poshigh*94)
			peta_notelists[peta_inst].append([peta_pos, peta_len, peta_note-12])

		for instnum in range(10):
			instid = 'petaporon'+str(instnum)

			track_obj = convproj_obj.track__add(instid, 'instrument', 0, False)
			track_obj.visual.name = 'Inst #'+str(instnum+1)
			track_obj.visual.color.set_float(colordata.getcolornum(instnum))
			plugin_obj, pluginid = convproj_obj.plugin__add__genid('universal', 'synth-osc', None)
			plugin_obj.role = 'synth'
			track_obj.inst_pluginid = pluginid

			osc_data = plugin_obj.osc_add()
			
			if instnum in [0,1,2,3,4,7]: osc_data.prop.shape = 'square'
			if instnum in [5,6]: osc_data.prop.shape = 'triangle'
			if instnum in [8]: osc_data.prop.shape = 'noise'
			if instnum in [0,1]: osc_data.prop.pulse_width = 1/8
			if instnum in [2,7]: osc_data.prop.pulse_width = 1/4
			if instnum in [3,4,5,6]: osc_data.prop.pulse_width = 1/2

			if instnum == 0: plugin_obj.env_asdr_add('vol', 0, 0, 0, 0.1, 0, 0, 1)
			if instnum == 1: plugin_obj.env_asdr_add('vol', 0, 0, 0, 0.1, 0.7, 0, 1)
			if instnum == 2: plugin_obj.env_asdr_add('vol', 0, 0, 0, 0.25, 0, 0, 1)
			if instnum == 3: plugin_obj.env_asdr_add('vol', 0, 0, 0, 0.2, 0, 0, 1)
			if instnum == 4: plugin_obj.env_asdr_add('vol', 0, 0, 0, 0, 1, 0, 1)
			if instnum == 5: plugin_obj.env_asdr_add('vol', 0, 0, 0, 0, 1, 0, 1)
			if instnum == 6: plugin_obj.env_asdr_add('vol', 0, 0, 0, 0.2, 0, 0, 1)
			if instnum == 7: plugin_obj.env_asdr_add('vol', 0, 0.3, 0, 0.3, 0.2, 0.3, 1)
			if instnum == 8: plugin_obj.env_asdr_add('vol', 0, 0, 0, 0.4, 0, 0, 1)

			for n in peta_notelists[instnum]: track_obj.placements.notelist.add_r(n[0], n[1], n[2], 1, {})

		convproj_obj.do_actions.append('do_singlenotelistcut')
		convproj_obj.params.add('bpm', petapo_data['t'], 'float')
		convproj_obj.timesig[0] = petapo_data['c']