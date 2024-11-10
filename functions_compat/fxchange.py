# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_values
from functions_compat import trackfx_to_numdata
import copy

import logging
logger_compat = logging.getLogger('compat')

def move_fx0_to_mastertrack(convproj_obj):
	if 0 in convproj_obj.fxrack:
		fxchannel_obj = convproj_obj.fxrack[0]
		convproj_obj.automation.move(['fxmixer','0','vol'], ['master', 'vol'])
		convproj_obj.automation.move(['fxmixer','0','pan'], ['master', 'pan'])
		fxchannel_obj.params.move(convproj_obj.track_master.params, 'vol')
		fxchannel_obj.params.move(convproj_obj.track_master.params, 'pan')
		convproj_obj.track_master.fxslots_audio = fxchannel_obj.fxslots_audio.copy()
		convproj_obj.track_master.fxslots_mixer = fxchannel_obj.fxslots_mixer.copy()
		fxchannel_obj.fxslots_audio = []
		fxchannel_obj.fxslots_mixer = []
		del convproj_obj.fxrack[0]

def track2fxrack(convproj_obj, data_obj, fxnum, defualtname, starttext, doboth, autoloc):
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

	if doboth == True: 
		pan = data_obj.params.get('pan', 0).value
		data_obj.params.remove('pan')
		fxchannel_obj.params.add('pan', pan, 'float')
		convproj_obj.automation.move(autoloc+['pan'], ['fxmixer',str(fxnum),'pan'])

		enabled = data_obj.params.get('enabled', True).value
		data_obj.params.remove('enabled')
		fxchannel_obj.params.add('enabled', enabled, 'float')
		convproj_obj.automation.move(autoloc+['enabled'], ['fxmixer',str(fxnum),'enabled'])

	return fxchannel_obj

def process(convproj_obj, in_dawinfo, out_dawinfo, out_type):
	in_fxtype = convproj_obj.fxtype
	out_fxtype = out_dawinfo.fxtype
	#print('fxchange: '+in_fxtype+' > '+out_fxtype+' - Proj Type: '+convproj_obj.type)
	logger_compat.info('fxchange: '+in_fxtype+' > '+out_fxtype+' - Proj Type: '+convproj_obj.type)

	paramchange = in_dawinfo.fxrack_params.copy()
	for x in out_dawinfo.fxrack_params:
		if x in paramchange: paramchange.remove(x)

	if in_fxtype == 'rack' and out_fxtype == 'rack' and convproj_obj.type in ['r', 'ri']:
		for trackid, track_obj in convproj_obj.track__iter():
			if track_obj.fxrack_channel > 0:
				fxrack_obj = convproj_obj.fxrack[track_obj.fxrack_channel]
				for paramid in paramchange:
					convproj_obj.automation.copy(['fxmixer',str(track_obj.fxrack_channel),paramid], ['track',trackid,paramid])
					fxrack_obj.params.copy(track_obj.params, paramid)

	if out_fxtype == 'none':
		convproj_obj.fx__chan__clear()
		convproj_obj.fx__group__clear()
		convproj_obj.fx__route__clear()
		convproj_obj.fx__return__clear()
		for trackid, track_obj in convproj_obj.track__iter():
			track_obj.fxrack_channel = 0
			track_obj.group = None

	elif in_fxtype in ['groupreturn', 'none'] and out_fxtype == 'rack' and convproj_obj.type in ['m', 'mi']:
		logger_compat.info('fxchange: Master to FX 0')
		fxchannel_obj = convproj_obj.fx__chan__add(0)
		fxchannel_obj.visual = copy.deepcopy(convproj_obj.track_master.visual)
		fxchannel_obj.params = copy.deepcopy(convproj_obj.track_master.params)
		fxchannel_obj.fxslots_audio = convproj_obj.track_master.fxslots_audio.copy()
		fxchannel_obj.fxslots_mixer = convproj_obj.track_master.fxslots_mixer.copy()
		convproj_obj.track_master.fxslots_audio = []
		convproj_obj.track_master.fxslots_mixer = []
		convproj_obj.automation.move(['master','vol'], ['fxmixer','0','vol'])
		convproj_obj.automation.move(['master','pan'], ['fxmixer','0','pan'])
		for count, iterval in enumerate(convproj_obj.instrument__iter()):
			fxnum = count+1
			inst_id, inst_obj = iterval
			fxchannel_obj = convproj_obj.fx__chan__add(fxnum)
			fxchannel_obj.visual = copy.deepcopy(inst_obj.visual)
			fxchannel_obj.params = copy.deepcopy(inst_obj.params)
			fxchannel_obj.fxslots_audio = inst_obj.fxslots_audio.copy()
			fxchannel_obj.fxslots_mixer = inst_obj.fxslots_mixer.copy()
			inst_obj.fxslots_audio = []
			inst_obj.fxslots_mixer = []
			inst_obj.fxrack_channel = fxnum
			fxchannel_obj.visual = inst_obj.visual.copy()
			convproj_obj.automation.move(['track',inst_id,'vol'], ['fxmixer',str(fxnum),'vol'])
			inst_obj.params.move(fxchannel_obj.params, 'vol')
			logger_compat.info('fxchange: Instrument to FX '+str(fxnum)+(' ('+fxchannel_obj.visual.name+')' if fxchannel_obj.visual.name else ''))
		return True

	elif in_fxtype == 'none' and out_fxtype == 'rack' and convproj_obj.type in ['r', 'ri', 'rm', 'ms', 'rs']:
		tracknum = 1
		for trackid, track_obj in convproj_obj.track__iter():
			fxchannel_obj = track2fxrack(convproj_obj, track_obj, tracknum, '', '', True, ['track',trackid])
			track_obj.fxrack_channel = tracknum
			tracknum += 1

	elif in_fxtype == 'groupreturn' and out_fxtype == 'rack' and convproj_obj.type in ['r', 'ri', 'rm', 'ms', 'rs']:
		t2m = trackfx_to_numdata.to_numdata()
		output_ids = t2m.trackfx_to_numdata(convproj_obj, 1)
		dict_returns = {}
		for returnid, return_obj in convproj_obj.track_master.returns.items(): dict_returns[returnid] = return_obj

		track2fxrack(convproj_obj, convproj_obj.track_master, 0, 'Master', '', True, ['master'])

		for output_id in output_ids:
			
			if output_id[1] == 'return':
				fxchannel_obj = track2fxrack(convproj_obj, dict_returns[output_id[2]], output_id[0]+1, 'Return', '[R] ', True, ['return',output_id[2]])
				fxchannel_obj.visual_ui.other['docked'] = 1

			if output_id[1] == 'group':
				fxchannel_obj = track2fxrack(convproj_obj, convproj_obj.groups[output_id[2]], output_id[0]+1, 'Group', '[G] ', True, ['group',output_id[2]])
				fxchannel_obj.visual_ui.other['docked'] = -1

			if output_id[1] == 'track':
				fxnum = output_id[0]+1
				track_obj = convproj_obj.track_data[output_id[2]]
				fxchannel_obj = track2fxrack(convproj_obj, track_obj, fxnum, '', '', True, ['track',output_id[2]])
				track_obj.fxrack_channel = output_id[0]+1
				track_obj.placements.add_fxrack_channel(fxnum)
				for _, scene_obj in track_obj.scenes.items():
					for _, lane_obj in scene_obj.items():
						lane_obj.add_fxrack_channel(fxnum)
				if track_obj.group: fxchannel_obj.sends.to_master_active = False

			fxchannel_obj.sends.add(output_id[3][0]+1, output_id[3][2], output_id[3][1])

			for senddata in output_id[4]: 
				fxchannel_obj.sends.add(senddata[0]+1, senddata[2], senddata[1])
				#fxchannel_obj.sends[5].to_master_active = False

		return True

	elif in_fxtype == 'rack' and out_fxtype == 'groupreturn' and convproj_obj.type in ['r', 'ri']:
		move_fx0_to_mastertrack(convproj_obj)

		fx_trackids = {}
		for trackid, track_obj in convproj_obj.track__iter():
			if track_obj.fxrack_channel > 0:
				if track_obj.fxrack_channel not in fx_trackids: fx_trackids[track_obj.fxrack_channel] = []
				fx_trackids[track_obj.fxrack_channel].append(trackid)
				track_obj.group = 'fxrack_'+str(track_obj.fxrack_channel)
				track_obj.fxrack_channel = -1

		routedatas = {}
		for fx_from, d in convproj_obj.fxrack.items():
			s = d.sends
			if not s.to_master_active:
				if len(s.data) == 1:
					fx_to = list(s.data)[0]
					if fx_to in convproj_obj.fxrack:
						targ_data = convproj_obj.fxrack[fx_to].sends.to_master_active
						if targ_data:
							routedatas[fx_from] = fx_to

		for x, y in routedatas.items():
			if y not in fx_trackids: fx_trackids[y] = []
			if x not in fx_trackids: fx_trackids[x] = []

		for fx_num in fx_trackids:

			if fx_num in convproj_obj.fxrack:
				fxchannel_obj = convproj_obj.fxrack[fx_num]
				fxchannel_obj.sends = {}
				groupid = 'fxrack_'+str(fx_num)
				group_obj = convproj_obj.fx__group__add(groupid)

				if fx_num in routedatas:
					group_obj.group = 'fxrack_'+str(routedatas[fx_num])

				cvpjtrackdata = convproj_obj.track_data
				colors = []
				for x in fx_trackids[fx_num]:
					track_obj = cvpjtrackdata[x]
					if track_obj.is_laned:
						for _, x in track_obj.lanes.items():
							if x.visual.color:
								colors.append(x.visual.color)
					if not colors:
						if track_obj.visual.color: colors.append(track_obj.visual.color)

				allcolor = colors[0] if (all(x == colors[0] for x in colors) and colors) else None

				convproj_obj.automation.move(['fxmixer',str(fx_num),'pan'], ['group',groupid,'pan'])
				convproj_obj.automation.move(['fxmixer',str(fx_num),'vol'], ['group',groupid,'vol'])
				fxchannel_obj.params.move(group_obj.params, 'vol')
				fxchannel_obj.params.move(group_obj.params, 'pan')
				group_obj.fxslots_audio = fxchannel_obj.fxslots_audio.copy()
				group_obj.fxslots_mixer = fxchannel_obj.fxslots_mixer.copy()
				fxchannel_obj.fxslots_audio = []
				fxtracks = fx_trackids[fx_num]
				if fxchannel_obj.visual.name: group_obj.visual.name = fxchannel_obj.visual.name
				elif len(fxtracks) == 1: 
					track_obj = convproj_obj.track_data[fxtracks[0]]
					if track_obj.visual.name: group_obj.visual.name = track_obj.visual.name+' [FX '+str(fx_num)+']'
					else: group_obj.visual.name = 'FX '+str(fx_num)
				else: 
					allnames = [(convproj_obj.track_data[x].visual.name.split(' #')[0] if convproj_obj.track_data[x].visual.name else '') for x in fxtracks]
					if all(x == allnames[0] for x in allnames) and allnames: 
						group_obj.visual.name = allnames[0]+' [FX '+str(fx_num)+']' if allnames[0] else 'FX '+str(fx_num)
					else: group_obj.visual.name = 'FX '+str(fx_num)
				group_obj.visual.color = fxchannel_obj.visual.color
				if allcolor: group_obj.visual.color.merge(allcolor)

				for x in fxtracks:
					track_obj = cvpjtrackdata[x]
					track_obj.visual.color.merge(group_obj.visual.color)

			logger_compat.info('fxchange: FX to Tracks '+ ', '.join(fx_trackids[fx_num]))
		convproj_obj.fxrack = {}
		return True

	elif in_fxtype == 'rack' and out_fxtype == 'route' and convproj_obj.type in ['r', 'ri']:
		convproj_obj.fx__chan__remove_unused()

		for trackid in convproj_obj.track_order: convproj_obj.fx__route__add(trackid)

		move_fx0_to_mastertrack(convproj_obj)

		used_fxchans = []

		fx_trackids = {}
		nofx_trackids = []

		for trackid, track_obj in convproj_obj.track__iter():
			if track_obj.fxrack_channel > 0:
				if track_obj.fxrack_channel not in used_fxchans: used_fxchans.append(track_obj.fxrack_channel)
				if track_obj.fxrack_channel not in fx_trackids: fx_trackids[track_obj.fxrack_channel] = []
				fx_trackids[track_obj.fxrack_channel].append(trackid)
				convproj_obj.trackroute[trackid].add('fxrack_'+str(track_obj.fxrack_channel), None, 1)
				convproj_obj.trackroute[trackid].to_master_active = False
			else:
				nofx_trackids.append(trackid)

			track_obj.fxrack_channel = -1

		for fxnum, fxdata in convproj_obj.fxrack.items():
			if fxnum > 0:
				is_fx_used = False
				if fxdata.visual.name != None: is_fx_used = True
				if fxdata.visual.color != None: is_fx_used = True
				if fxdata.fxslots_audio != []: is_fx_used = True
				if is_fx_used and (fxnum not in used_fxchans): used_fxchans.append(fxnum)

				for target in fxdata.sends.data:
					if target not in used_fxchans and target>0: 
						used_fxchans.append(target)
				track_obj.fxrack_channel = -1

		used_fxchans = sorted(used_fxchans)

		for n, fxnum in enumerate(used_fxchans):
			fx_obj = convproj_obj.fxrack[fxnum]
			track_id = 'fxrack_'+str(fxnum)
			convproj_obj.fx__route__add(track_id)
			track_obj = convproj_obj.track__add(track_id, 'fx', 1, 0)

			convproj_obj.automation.move(['fxmixer',str(fxnum),'vol'], ['track',track_id,'vol'])
			convproj_obj.automation.move(['fxmixer',str(fxnum),'pan'], ['track',track_id,'pan'])
			fx_obj.params.move(track_obj.params, 'vol')
			fx_obj.params.move(track_obj.params, 'pan')
			track_obj.visual = fx_obj.visual
			track_obj.visual.name = '[FX '+str(fxnum)+'] '+(track_obj.visual.name if track_obj.visual.name else '')
			track_obj.fxslots_audio = fx_obj.fxslots_audio.copy()
			fx_obj.fxslots_audio = []

			convproj_obj.trackroute['fxrack_'+str(fxnum)].to_master_active = fx_obj.sends.to_master_active

			for n, d in fx_obj.sends.data.items(): convproj_obj.trackroute['fxrack_'+str(fxnum)].data['fxrack_'+str(n)] = d

		convproj_obj.track_order = []
		for fxnum, ids in fx_trackids.items():
			convproj_obj.track_order.append('fxrack_'+str(fxnum))
			for sid in ids: convproj_obj.track_order.append(sid)
			used_fxchans.remove(fxnum)

		for sid in nofx_trackids: convproj_obj.track_order.append(sid)

		for fxnum in used_fxchans: convproj_obj.track_order.append('fxrack_'+str(fxnum))
		return True

	elif in_fxtype == 'route' and out_fxtype == 'rack' and convproj_obj.type in ['r', 'ri']:
		tracknums = {}

		#track2fxrack(convproj_obj, convproj_obj.track_master, 0, 'Master', '', True, ['master'])
		if not convproj_obj.trackroute:
			for t in convproj_obj.track_order:
				convproj_obj.fx__route__add(t)

		for num, trackid in enumerate(convproj_obj.track_order): 
			track_obj = convproj_obj.track_data[trackid]
			tracknums[trackid] = num+1

		for trackid, track_obj in convproj_obj.track__iter():
			fxnum = tracknums[trackid]
			#convproj_obj, data_obj, fxnum, defualtname, starttext, doboth, autoloc
			fxchannel_obj = track2fxrack(convproj_obj, track_obj, fxnum, '', '', False, ['track',trackid])
			track_obj.fxrack_channel = fxnum

			oldmasteractive = convproj_obj.trackroute[trackid].to_master_active
			oldroute = convproj_obj.trackroute[trackid].data
			convproj_obj.trackroute[trackid].data = {}
			for t, r in oldroute.items(): fxchannel_obj.sends.data[tracknums[t]] = r
			fxchannel_obj.sends.to_master_active = oldmasteractive
			track_obj.placements.add_fxrack_channel(fxnum)

		return True

	elif in_fxtype == 'groupreturn' and out_fxtype == 'route' and convproj_obj.type in ['r', 'ri', 'rm', 'ms', 'rs']:

		convproj_obj.fx__route__clear()
		strgrptrk = convproj_obj.group__iter_stream_inside()

		newtrackids = [t+'_'+i for t, i, g in strgrptrk]

		old_track_data = convproj_obj.track_data

		convproj_obj.track_data = {}
		convproj_obj.track_order = []

		num = 0
		for t, i, g in strgrptrk:
			oi = newtrackids[num]

			if g:
				trackr = convproj_obj.fx__route__add(oi)
				trackr.add('GROUP_'+g, None, 1)
				trackr.to_master_active = False

			if t == 'GROUP':
				group_obj = convproj_obj.fx__group__get(i)
				track_obj = convproj_obj.track__add(oi, 'fx', 1, 0)
				track_obj.visual = group_obj.visual.copy()
				if track_obj.visual.name: track_obj.visual.name = '[Group] '+track_obj.visual.name
				else: track_obj.visual.name = '[Group]'

			if t == 'TRACK':
				track_obj = old_track_data[i]
				senddat = track_obj.sends.data
				trackr = convproj_obj.fx__route__add(oi)
				for i, x in track_obj.sends.iter():
					trackr.add('RETURN_'+i, None, x.params.get('amount', 0).value)
				convproj_obj.track_data[oi] = track_obj
				convproj_obj.track_order.append(oi)
			num += 1

		for returnid, return_obj in convproj_obj.track_master.returns.items(): 
			track_obj = convproj_obj.track__add('RETURN_'+returnid, 'fx', 1, 0)
			track_obj.visual = return_obj.visual.copy()
			if track_obj.visual.name: track_obj.visual.name = '[Return] '+track_obj.visual.name
			else: track_obj.visual.name = '[Return]'

		convproj_obj.fx__group__clear()
		return True
		
	else: return False
