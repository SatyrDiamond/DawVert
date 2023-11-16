# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import params
from functions import data_values
from functions_tracks import tracks_r
from functions_tracks import auto_data
from functions_tracks import fxrack
from functions_tracks import fxslot
from functions_compat import trackfx_to_numdata

def list2fxrack(cvpj_l, input_list, fxnum, defualtname, starttext, removeboth):
    fx_name = starttext+input_list['name'] if 'name' in input_list else starttext+defualtname
    fx_color = input_list['color'] if 'color' in input_list else None

    vol = params.get(input_list, [], 'vol', 1)[0]
    pan = params.get(input_list, [], 'pan', 0)[0]

    params.remove(input_list, 'vol')
    if removeboth == True:
        params.remove(input_list, 'pan')

    fxrack.add(cvpj_l, fxnum, vol, pan, name=fx_name, color=fx_color)
    if 'chain_fx_audio' in input_list: 
        for plugid in input_list['chain_fx_audio']:
            fxslot.insert(cvpj_l, ['fxrack', fxnum], 'audio', plugid)
        del input_list['chain_fx_audio']

def process_r(cvpj_l):
    if 'fxrack' not in cvpj_l:
        cvpj_l['fxrack'] = {}

        output_ids = trackfx_to_numdata.trackfx_to_numdata(cvpj_l, 1)

        dict_returns = {}

        auto_data.move(cvpj_l, ['master','vol'], ['fxmixer','0','vol'])
        auto_data.move(cvpj_l, ['master','pan'], ['fxmixer','0','pan'])

        if 'track_master' in cvpj_l:
            track_master_data = cvpj_l['track_master']
            list2fxrack(cvpj_l, track_master_data, 0, 'Master', '', True)
            if 'returns' in track_master_data:
                for returnid in track_master_data['returns']:
                    return_data = track_master_data['returns'][returnid]
                    dict_returns[returnid] = return_data
            del cvpj_l['track_master']


        if 'track_placements' in cvpj_l:
            for output_id in output_ids:
                if output_id[2] in cvpj_l['track_placements']:
                    track_placements = cvpj_l['track_placements'][output_id[2]]
                    if 'audio_nested' in track_placements:
                        for spld in track_placements['audio_nested']: spld['fxrack_channel'] = output_id[0]+1
                    if 'audio' in track_placements:
                        for spld in track_placements['audio']: spld['fxrack_channel'] = output_id[0]+1

        for output_id in output_ids:
            
            if output_id[1] == 'return':
                return_data = dict_returns[output_id[2]]
                auto_data.move(cvpj_l, ['return',output_id[2],'vol'], ['fxmixer',str(output_id[0]+1),'vol'])
                auto_data.move(cvpj_l, ['return',output_id[2],'pan'], ['fxmixer',str(output_id[0]+1),'pan'])
                list2fxrack(cvpj_l, return_data, output_id[0]+1, 'Return', '[R] ', True)

            if output_id[1] == 'group':
                group_data = cvpj_l['groups'][output_id[2]]
                auto_data.move(cvpj_l, ['group',output_id[2],'vol'], ['fxmixer',str(output_id[0]+1),'vol'])
                auto_data.move(cvpj_l, ['group',output_id[2],'pan'], ['fxmixer',str(output_id[0]+1),'pan'])
                list2fxrack(cvpj_l, group_data, output_id[0]+1, 'Group', '[G] ', True)

            if output_id[1] == 'track':
                track_data = cvpj_l['track_data'][output_id[2]]
                auto_data.move(cvpj_l, ['track',output_id[2],'vol'], ['fxmixer',str(output_id[0]+1),'vol'])
                auto_data.move(cvpj_l, ['track',output_id[2],'pan'], ['fxmixer',str(output_id[0]+1),'pan'])
                list2fxrack(cvpj_l, track_data, output_id[0]+1, '', '', False)
                track_data['fxrack_channel'] = output_id[0]+1

            fxrack.addsend(cvpj_l, output_id[0]+1, output_id[3][0]+1, output_id[3][1], output_id[3][2])

            for senddata in output_id[4]:
                fxrack.addsend(cvpj_l, output_id[0]+1, senddata[0]+1, senddata[1], senddata[2])

        return True

    else: return False

def process_m(cvpj_l):
    if 'fxrack' not in cvpj_l:
        fxnum = 1
        cvpj_l['fxrack'] = {}

        c_orderingdata = cvpj_l['instruments_order']
        c_trackdata = cvpj_l['instruments_data']

        if 'track_master' in cvpj_l:
            print('[trackfx2fxrack] Master to FX 0')
            cvpj_l['fxrack']['0'] = cvpj_l['track_master']
            auto_data.move(cvpj_l, ['master','vol'], ['fxmixer','0','vol'])

        for trackid in c_orderingdata:
            trackdata = c_trackdata[trackid]
            trackdata['fxrack_channel'] = fxnum
            fxtrack = {}
            if 'name' in trackdata: 
                fxtrack['name'] = trackdata['name']
                print('[trackfx2fxrack] Track to FX '+str(fxnum)+' ('+str(trackdata['name'])+')')
            else:
                print('[trackfx2fxrack] Track to FX '+str(fxnum))

            if 'color' in trackdata: fxtrack['color'] = trackdata['color']
            if 'chain_fx_audio' in trackdata: 
                fxtrack['chain_fx_audio'] = trackdata['chain_fx_audio']
                del trackdata['chain_fx_audio']
            cvpj_l['fxrack'][str(fxnum)] = fxtrack

            fxnum += 1
        return True
    else: return False

def process(cvpj_l, cvpj_type, in_compat, out_compat):
    if in_compat == False and out_compat == True:
        if cvpj_type in ['r', 'ri', 'rm']: return process_r(cvpj_l)
        elif cvpj_type in ['m', 'mi']: return process_m(cvpj_l)
        else: return False
    else: return False