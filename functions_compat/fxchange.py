# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_values
from functions_compat import trackfx_to_numdata
import copy

def list2fxrack(convproj_obj, data_obj, fxnum, defualtname, starttext, removeboth, autoloc):
    fx_name = starttext+data_obj.visual.name if data_obj.visual.name else starttext+defualtname
    fx_color = data_obj.visual.color if data_obj.visual.color else None

    fxchannel_obj = convproj_obj.add_fxchan(fxnum)
    fxchannel_obj.visual.name = fx_name
    fxchannel_obj.visual.color = fx_color
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

def process(convproj_obj, in_fxtype, out_fxtype):
    print('[fxchange] '+in_fxtype+' > '+out_fxtype)
    if in_fxtype == 'groupreturn' and out_fxtype == 'rack' and convproj_obj.type in ['m', 'mi']:
        print('[fxchange] Master to FX 0')
        fxchannel_obj = convproj_obj.add_fxchan(0)
        fxchannel_obj.visual = copy.deepcopy(convproj_obj.track_master.visual)
        fxchannel_obj.params = copy.deepcopy(convproj_obj.track_master.params)
        fxchannel_obj.fxslots_audio = convproj_obj.track_master.fxslots_audio.copy()
        fxchannel_obj.fxslots_mixer = convproj_obj.track_master.fxslots_mixer.copy()
        convproj_obj.track_master.fxslots_audio = []
        convproj_obj.track_master.fxslots_mixer = []
        convproj_obj.automation.move(['master','vol'], ['fxmixer','0','vol'])
        convproj_obj.automation.move(['master','pan'], ['fxmixer','0','pan'])
        for count, iterval in enumerate(convproj_obj.iter_instrument()):
            fxnum = count+1
            inst_id, inst_obj = iterval
            fxchannel_obj = convproj_obj.add_fxchan(fxnum)
            fxchannel_obj.visual = copy.deepcopy(inst_obj.visual)
            fxchannel_obj.params = copy.deepcopy(inst_obj.params)
            fxchannel_obj.fxslots_audio = inst_obj.fxslots_audio.copy()
            inst_obj.fxslots_audio = []
            inst_obj.fxrack_channel = fxnum
            fxchannel_obj.visual.name = inst_obj.visual.name
            fxchannel_obj.visual.color = inst_obj.visual.color
            convproj_obj.automation.move(['track',inst_id,'vol'], ['fxmixer',str(fxnum),'vol'])
            inst_obj.params.move(fxchannel_obj.params, 'vol')
            print('[fxchange] Instrument to FX '+str(fxnum)+(' ('+fxchannel_obj.visual.name+')' if fxchannel_obj.visual.name else ''))
        return True

    elif in_fxtype == 'groupreturn' and out_fxtype == 'rack' and convproj_obj.type in ['r', 'ri', 'rm']:
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

    elif in_fxtype == 'rack' and out_fxtype == 'groupreturn' and convproj_obj.type in ['r', 'ri']:
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

        fx_trackids = {}
        for trackid, track_obj in convproj_obj.iter_track():
            if track_obj.fxrack_channel > 0:
                if track_obj.fxrack_channel not in fx_trackids: fx_trackids[track_obj.fxrack_channel] = []
                fx_trackids[track_obj.fxrack_channel].append(trackid)
                track_obj.group = 'fxrack_'+str(track_obj.fxrack_channel)
                track_obj.fxrack_channel = -1

        #for fxnum, fxchannel_obj in convproj_obj.fxrack.items()
        for fx_num in fx_trackids:

            if fx_num in convproj_obj.fxrack:
                fxchannel_obj = convproj_obj.fxrack[fx_num]
                fxchannel_obj.sends = {}
                groupid = 'fxrack_'+str(fx_num)
                group_obj = convproj_obj.add_group(groupid)

                convproj_obj.automation.move(['fxmixer',str(fx_num),'pan'], ['group',groupid,'pan'])
                convproj_obj.automation.move(['fxmixer',str(fx_num),'vol'], ['group',groupid,'vol'])
                fxchannel_obj.params.move(group_obj.params, 'vol')
                fxchannel_obj.params.move(group_obj.params, 'pan')
                group_obj.fxslots_audio = fxchannel_obj.fxslots_audio.copy()
                group_obj.fxslots_mixer = fxchannel_obj.fxslots_mixer.copy()
                fxchannel_obj.fxslots_audio = []
                group_obj.visual = fxchannel_obj.visual

            print('[compat] fxchange: FX to Tracks '+ ', '.join(fx_trackids[fx_num]))
        convproj_obj.fxrack = {}
        return True

    elif in_fxtype == 'rack' and out_fxtype == 'track' and convproj_obj.type in ['r', 'ri']:
        for trackid in convproj_obj.track_order: convproj_obj.add_trackroute(trackid)

        used_fxchans = []

        fx_trackids = {}
        nofx_trackids = []

        for trackid, track_obj in convproj_obj.iter_track():
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
                    if target not in used_fxchans: used_fxchans.append(target)
                track_obj.fxrack_channel = -1

        used_fxchans = sorted(used_fxchans)

        for n, fxnum in enumerate(used_fxchans):
            fx_obj = convproj_obj.fxrack[fxnum]
            track_id = 'fxrack_'+str(fxnum)
            convproj_obj.add_trackroute(track_id)
            track_obj = convproj_obj.add_track(track_id, 'fx', 1, 0)

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

    else: return False