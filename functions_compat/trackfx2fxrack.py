# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_values
from functions_compat import trackfx_to_numdata
import copy

import logging
logger_compat = logging.getLogger('compat')

def list2fxrack(convproj_obj, data_obj, fxnum, defualtname, starttext, removeboth, autoloc):
	fx_name = starttext+data_obj.visual.name if data_obj.visual.name else starttext+defualtname

	fxchannel_obj = convproj_obj.fx__chan__add(fxnum)
	fxchannel_obj.visual.name = fx_name
	if data_obj.visual.color: fxchannel_obj.visual.color = data_obj.visual.color.copy()
	fxchannel_obj.fxslots_audio = data_obj.fxslots_audio.copy()
	fxchannel_obj.fxslots_mixer = data_obj.fxslots_mixer.copy()
	data_obj.fxslots_audio = []
	data_obj.fxslots_mixer = []

	vol = data_obj.params.get('vol', 1).value
	data_obj.params.remove('vol')
	fxchannel_obj.params.add('vol', vol, 'float')
	convproj_obj.automation.move(autoloc+['vol'], ['fxmixer',str(fxnum),'vol'])

	if removeboth == True: 
		pan = data_obj.params.get('pan', 0).value
		data_obj.params.remove('pan')
		fxchannel_obj.params.add('pan', pan, 'float')
		convproj_obj.automation.move(autoloc+['pan'], ['fxmixer',str(fxnum),'pan'])

	return fxchannel_obj

def process_r(convproj_obj):
	if not convproj_obj.fxrack:
		t2m = trackfx_to_numdata.to_numdata()
		output_ids = t2m.trackfx_to_numdata(convproj_obj, 1)
		dict_returns = {}
		for returnid, return_obj in convproj_obj.track_master.returns.items(): dict_returns[returnid] = return_obj

		list2fxrack(convproj_obj, convproj_obj.track_master, 0, 'Master', '', True, ['master'])

		for output_id in output_ids:
			
			if output_id[1] == 'return':
				fxchannel_obj = list2fxrack(convproj_obj, dict_returns[output_id[2]], output_id[0]+1, 'Return', '[R] ', True, ['return',output_id[2]])
				fxchannel_obj.visual_ui.other['docked'] = 1

			if output_id[1] == 'group':
				fxchannel_obj = list2fxrack(convproj_obj, convproj_obj.groups[output_id[2]], output_id[0]+1, 'Group', '[G] ', True, ['group',output_id[2]])
				fxchannel_obj.visual_ui.other['docked'] = -1

			if output_id[1] == 'track':
				fxnum = output_id[0]+1
				track_obj = convproj_obj.track_data[output_id[2]]
				fxchannel_obj = list2fxrack(convproj_obj, track_obj, fxnum, '', '', False, ['track',output_id[2]])
				track_obj.fxrack_channel = output_id[0]+1
				if not track_obj.placements.is_indexed:
					for pl_obj in track_obj.placements.pl_audio:
						if pl_obj.fxrack_channel == -1: pl_obj.fxrack_channel = fxnum
					for nestedpl_obj in track_obj.placements.pl_audio_nested:
						for e in nestedpl_obj.events:
							e.fxrack_channel = fxnum

			fxchannel_obj.sends.add(output_id[3][0]+1, output_id[3][2], output_id[3][1])

			for senddata in output_id[4]: fxchannel_obj.sends.add(senddata[0]+1, senddata[2], senddata[1])
		return True
	else: return False

def process_m(convproj_obj):
	if not convproj_obj.fxrack:
		logger_compat.info('trackfx2fxrack: Master to FX 0')
		fxchannel_obj = convproj_obj.fx__chan__add(0)
		fxchannel_obj.visual = copy.deepcopy(convproj_obj.track_master.visual)
		fxchannel_obj.params = copy.deepcopy(convproj_obj.track_master.params)
		fxchannel_obj.fxslots_audio = convproj_obj.track_master.fxslots_audio.copy()
		fxchannel_obj.fxslots_mixer = convproj_obj.track_master.fxslots_mixer.copy()
		convproj_obj.track_master.fxslots_audio = []
		convproj_obj.track_master.fxslots_mixer = []

		convproj_obj.automation.move(['master','vol'], ['fxmixer','0','vol'])
		convproj_obj.automation.move(['master','pan'], ['fxmixer','0','pan'])

		fxnum = 1
		for inst_id, inst_obj in convproj_obj.instrument__iter():
			fxchannel_obj = convproj_obj.fx__chan__add(fxnum)
			fxchannel_obj.visual = copy.deepcopy(inst_obj.visual)
			fxchannel_obj.params = copy.deepcopy(inst_obj.params)
			fxchannel_obj.fxslots_audio = inst_obj.fxslots_audio.copy()
			inst_obj.fxslots_audio = []
			inst_obj.fxrack_channel = fxnum
			fxchannel_obj.visual.name = inst_obj.visual.name
			fxchannel_obj.visual.color = inst_obj.visual.color

			convproj_obj.automation.move(['track',inst_id,'vol'], ['fxmixer',str(fxnum),'vol'])
			inst_obj.params.move(fxchannel_obj.params, 'vol')

			logger_compat.info('trackfx2fxrack: Instrument to FX '+str(fxnum)+(' ('+fxchannel_obj.visual.name+')' if fxchannel_obj.visual.name else ''))
			fxnum += 1

		return True
	else: return False

def process(convproj_obj, in_compat, out_compat, out_type):
	if in_compat == False and out_compat == True:
		if convproj_obj.type in ['r', 'ri', 'rm']: return process_r(convproj_obj)
		elif convproj_obj.type in ['m', 'mi']: return process_m(convproj_obj)
		else: return False
	else: return False