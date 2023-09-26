# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import params
from functions import tracks
from functions import data_values

def list2fxrack(cvpj_l, input_list, fxnum, defualtname, starttext, dontremoveboth):
    fx_name = starttext+input_list['name'] if 'name' in input_list else starttext+defualtname
    fx_color = input_list['color'] if 'color' in input_list else None

    vol = params.get(input_list, [], 'vol', 1)[0]
    pan = params.get(input_list, [], 'pan', 0)[0]

    params.remove(input_list, 'vol')
    if dontremoveboth == True:
        params.remove(input_list, 'pan')

    tracks.fxrack_add(cvpj_l, fxnum, fx_name, fx_color, vol, pan)
    if 'chain_fx_audio' in input_list: 
        for plugid in input_list['chain_fx_audio']:
            tracks.insert_fxslot(cvpj_l, ['fxrack', fxnum], 'audio', plugid)
        del input_list['chain_fx_audio']

def process_r(cvpj_l):
    if 'fxrack' not in cvpj_l:
        cvpj_l['fxrack'] = {}
        fxnum = 1

        fxdata = {}
        fxdata[0] = [['master',None],[None,None]]

        outfxnum = {}
        returnids = {}

        if 'track_master' in cvpj_l:
            track_master_data = cvpj_l['track_master']

            list2fxrack(cvpj_l, track_master_data, 0, 'Master', '', True)

            if 'returns' in track_master_data:
                for send in track_master_data['returns']:
                    send_data = track_master_data['returns'][send]
                    list2fxrack(cvpj_l, send_data, fxnum, send, '[S] ', True)
                    fxdata[fxnum] = [['return',send],['master',None]]
                    returnids[send] = fxnum
                    fxnum += 1
                del track_master_data['returns']
                
            del cvpj_l['track_master']

        if 'groups' in cvpj_l:
            for groupid in cvpj_l['groups']:
                group_data = cvpj_l['groups'][groupid]
                group_audio_destination = group_data['audio_destination']
                group_dest_type = None
                group_dest_id = None
                if 'type' in group_audio_destination: group_dest_type = group_audio_destination['type']
                if 'id' in group_audio_destination: group_dest_id = group_audio_destination['id']
                fxdata[fxnum] = [['group',groupid],[group_dest_type,group_dest_id]]
                data_values.nested_dict_add_value(outfxnum, ['group', groupid], [fxnum, 1.0])
                list2fxrack(cvpj_l, group_data, fxnum, 'FX '+str(fxnum), '[G] ', True)
                fxnum += 1

                if 'sends_audio' in group_data:
                    for send in group_data['sends_audio']:
                        send_data = group_data['sends_audio'][send]
                        list2fxrack(cvpj_l, send_data, fxnum, send, '[S] ', True)
                        fxdata[fxnum] = [['return',send],['group',groupid]]
                        returnids[send] = fxnum
                        fxnum += 1

            del cvpj_l['groups']

        c_orderingdata = cvpj_l['track_order']
        c_trackdata = cvpj_l['track_data']

        for trackid in c_orderingdata:
            s_trkdata = c_trackdata[trackid]

            if 'sends_audio' in s_trkdata:
                for send_data in s_trkdata['sends_audio']:
                    if send_data['sendid'] in returnids:
                        sendautoid = None
                        if 'sendautoid' in send_data: sendautoid = send_data['sendautoid']
                        tracks.fxrack_addsend(cvpj_l, fxnum, returnids[send_data['sendid']], send_data['amount'], sendautoid)
                del s_trkdata['sends_audio']

            track_dest_type = None
            track_dest_id = None
            if 'group' in s_trkdata:
                track_dest_type = 'group'
                track_dest_id = s_trkdata['group']
            else:
                track_dest_type = 'master'
            fxdata[fxnum] = [['track',trackid],[track_dest_type,track_dest_id]]
            data_values.nested_dict_add_value(outfxnum, ['track', trackid], [fxnum, 1.0])

            list2fxrack(cvpj_l, s_trkdata, fxnum, trackid, '', False)
            tracks.r_add_dataval(cvpj_l, trackid, None, 'fxrack_channel', int(fxnum))

            fxnum += 1

        print('[trackfx2fxrack] Num ', 'type'.ljust(8), 'id'.ljust(12), 'dest'.ljust(8), 'dest_id'.ljust(12))
        for fxslot in fxdata:
            slotdata = fxdata[fxslot]

            out_fx_send = [0, 1.0]

            if slotdata[1][0] == 'group':
                if 'group' in outfxnum:
                    if slotdata[1][1] in outfxnum['group']:
                        out_fx_send = outfxnum['group'][slotdata[1][1]]

            tracks.fxrack_addsend(cvpj_l, fxslot, out_fx_send[0], out_fx_send[1], None)

            print('[trackfx2fxrack] '+str(fxslot).rjust(4), 
                  str(slotdata[0][0]).ljust(8), 
                  str(slotdata[0][1]).ljust(12), 
                  str(slotdata[1][0]).ljust(8),
                  str(slotdata[1][1]).ljust(12),
                  out_fx_send)

            if slotdata[0][0] == 'master': 
                tracks.a_move_auto(cvpj_l, ['master','vol'], ['fxmixer',str(fxslot),'vol'])
            if slotdata[0][0] == 'group': 
                tracks.a_move_auto(cvpj_l, ['group',slotdata[0][1],'vol'], ['fxmixer',str(fxslot),'vol'])
                tracks.a_move_auto(cvpj_l, ['group',slotdata[0][1],'pan'], ['fxmixer',str(fxslot),'pan'])
            if slotdata[0][0] == 'return': 
                tracks.a_move_auto(cvpj_l, ['return',slotdata[0][1],'vol'], ['fxmixer',str(fxslot),'vol'])
                tracks.a_move_auto(cvpj_l, ['return',slotdata[0][1],'pan'], ['fxmixer',str(fxslot),'pan'])
            if slotdata[0][0] == 'track': 
                tracks.a_move_auto(cvpj_l, ['track',slotdata[0][1],'vol'], ['fxmixer',str(fxslot),'vol'])
                tracks.a_move_auto(cvpj_l, ['track',slotdata[0][1],'pan'], ['fxmixer',str(fxslot),'pan'])

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
            tracks.a_move_auto(cvpj_l, ['master','vol'], ['fxmixer','0','vol'])

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