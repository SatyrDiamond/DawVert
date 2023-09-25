# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import song
from functions import notelist_data
from functions import data_values
from functions import xtramath
from functions import params
from functions import tracks
from functions import audio

from functions_compat import changestretch
from functions_compat import autopl_remove
from functions_compat import loops_add
from functions_compat import loops_remove
from functions_compat import removecut
from functions_compat import removelanes
from functions_compat import time_seconds
from functions_compat import unhybrid
from functions_compat import timesigblocks
from functions_compat import trackpl_add

import json
import math

# -------------------------------------------- fxrack --------------------------------------------

def list2fxrack(cvpj_l, input_list, fxnum, defualtname, starttext):
    if 'name' in input_list: fx_name = starttext+input_list['name']
    else: fx_name = starttext+defualtname
    if 'color' in input_list: fx_color = input_list['color']
    else: fx_color = None
    tracks.fxrack_add(cvpj_l, fxnum, fx_name, fx_color, None, None)
    if 'chain_fx_audio' in input_list: 
        for plugid in input_list['chain_fx_audio']:
            tracks.insert_fxslot(cvpj_l, ['fxrack', fxnum], 'audio', plugid)
        del input_list['chain_fx_audio']


def trackfx2fxrack(cvpj_l, cvpjtype):

    tracks.a_move_auto(cvpj_l, ['master','vol'], ['fxmixer','0','vol'])
    
    if cvpjtype in ['r', 'ri']:
        trackfx2fxrack_adv(cvpj_l, cvpjtype)
    else:
        trackfx2fxrack_simple(cvpj_l, cvpjtype)

def trackfx2fxrack_adv(cvpj_l, cvpjtype):
    cvpj_l['fxrack'] = {}
    fxnum = 1

    fxdata = {}
    fxdata[0] = [['master',None],[None,None]]

    outfxnum = {}
    returnids = {}

    if 'track_master' in cvpj_l:
        track_master_data = cvpj_l['track_master']

        list2fxrack(cvpj_l, track_master_data, 0, 'Master', '')

        if 'returns' in track_master_data:
            for send in track_master_data['returns']:
                send_data = track_master_data['returns'][send]
                list2fxrack(cvpj_l, send_data, fxnum, send, '[S] ')
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
            list2fxrack(cvpj_l, group_data, fxnum, 'FX '+str(fxnum), '[G] ')
            fxnum += 1

            if 'sends_audio' in group_data:
                for send in group_data['sends_audio']:
                    send_data = group_data['sends_audio'][send]
                    list2fxrack(cvpj_l, send_data, fxnum, send, '[S] ')
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

        list2fxrack(cvpj_l, s_trkdata, fxnum, trackid, '')
        tracks.r_add_dataval(cvpj_l, trackid, None, 'fxrack_channel', int(fxnum))

        fxnum += 1

    #print(outfxnum)

    print('[trackfx2fxrack_adv] Num ', 'type'.ljust(8), 'id'.ljust(12), 'dest'.ljust(8), 'dest_id'.ljust(12))
    for fxslot in fxdata:
        slotdata = fxdata[fxslot]

        out_fx_send = [0, 1.0]

        if slotdata[1][0] == 'group':
            if 'group' in outfxnum:
                if slotdata[1][1] in outfxnum['group']:
                    out_fx_send = outfxnum['group'][slotdata[1][1]]

        tracks.fxrack_addsend(cvpj_l, fxslot, out_fx_send[0], out_fx_send[1], None)

        print('[trackfx2fxrack_adv] '+str(fxslot).rjust(4), 
              str(slotdata[0][0]).ljust(8), 
              str(slotdata[0][1]).ljust(12), 
              str(slotdata[1][0]).ljust(8),
              str(slotdata[1][1]).ljust(12),
              out_fx_send)



def trackfx2fxrack_simple(cvpj_l, cvpjtype):
    cvpj_l['fxrack'] = {}
    fxnum = 1
    if cvpjtype in ['r', 'ri', 'c']:
        c_orderingdata = cvpj_l['track_order']
        c_trackdata = cvpj_l['track_data']
    if cvpjtype in ['m', 'mi']:
        c_orderingdata = cvpj_l['instruments_order']
        c_trackdata = cvpj_l['instruments_data']

    if 'track_master' in cvpj_l:
        print('[compat] trackfx2fxrack: Master to FX 0')
        cvpj_l['fxrack']['0'] = cvpj_l['track_master']
        tracks.a_move_auto(cvpj_l, ['master','vol'], ['fxmixer','0','vol'])

    for trackid in c_orderingdata:
        trackdata = c_trackdata[trackid]
        trackdata['fxrack_channel'] = fxnum
        fxtrack = {}
        if 'name' in trackdata: 
            fxtrack['name'] = trackdata['name']
            print('[trackfx2fxrack_simple] Track to FX '+str(fxnum)+' ('+str(trackdata['name'])+')')
        else:
            print('[trackfx2fxrack_simple] Track to FX '+str(fxnum))

        if 'color' in trackdata: fxtrack['color'] = trackdata['color']
        if 'chain_fx_audio' in trackdata: 
            fxtrack['chain_fx_audio'] = trackdata['chain_fx_audio']
            del trackdata['chain_fx_audio']
        cvpj_l['fxrack'][str(fxnum)] = fxtrack

        if cvpjtype == 'c':
            tracks.a_move_auto(cvpj_l, ['track',trackid,'vol'], ['fxmixer',str(fxnum),'vol'])

        fxnum += 1

def fxrack2trackfx(cvpj_l, cvpjtype):
    if 'fxrack' in cvpj_l:
        cvpj_fxrack = cvpj_l['fxrack']
        if '0' in cvpj_fxrack:
            print('[compat] trackfx2fxrack: FX 0 to Master')
            cvpj_l['track_master'] = cvpj_fxrack['0']

        tracks.a_move_auto(cvpj_l, ['fxmixer','0','vol'], ['master','vol'])
        tracks.a_move_auto(cvpj_l, ['fxmixer','0','pan'], ['master','pan'])
        fx_trackids = {}
        for cvpj_trackid, s_trackdata, track_placements in tracks.r_track_iter(cvpj_l):
            cvpj_track_fxnum = s_trackdata['fxrack_channel'] if 'fxrack_channel' in s_trackdata else None
            if cvpj_track_fxnum != None: 
                if cvpj_track_fxnum not in fx_trackids: fx_trackids[cvpj_track_fxnum] = []
                fx_trackids[cvpj_track_fxnum].append(cvpj_trackid)
                if 'fxrack_channel' in s_trackdata: del s_trackdata['fxrack_channel']
                if cvpj_track_fxnum != 0:
                    s_trackdata['group'] = 'fxrack_'+str(cvpj_track_fxnum)

        if 0 in fx_trackids: del fx_trackids[0]

        for fx_trackid in fx_trackids:
            cvpj_fxdata = cvpj_fxrack[str(fx_trackid)] if str(fx_trackid) in cvpj_fxrack else {}
            if 'sends' in cvpj_fxdata: del cvpj_fxdata['sends']
            groupid = 'fxrack_'+str(fx_trackid)
            tracks.group_add(cvpj_l, groupid, None)
            cvpj_l['groups'][groupid] |= cvpj_fxdata
            print('[compat] trackfx2fxrack: FX to Tracks '+ ', '.join(fx_trackids[fx_trackid]))

# -------------------------------------------- Main --------------------------------------------

audiostretch_processed = False

def makecompat_audiostretch(cvpj_l, cvpj_type, in_dawcapabilities, out_dawcapabilities):
    cvpj_proj = json.loads(cvpj_l)
    global audiostretch_processed
    if audiostretch_processed == False and cvpj_type in ['r', 'm']:
        in__placement_audio_stretch = []
        out__placement_audio_stretch = []
        if 'placement_audio_stretch' in in_dawcapabilities: in__placement_audio_stretch = in_dawcapabilities['placement_audio_stretch']
        if 'placement_audio_stretch' in out_dawcapabilities: out__placement_audio_stretch = out_dawcapabilities['placement_audio_stretch']
        if 'warp' in in__placement_audio_stretch and 'warp' not in out__placement_audio_stretch:
            if cvpj_type == 'm': changestretch.process_m(cvpj_proj, 'rate')
            if cvpj_type == 'r': changestretch.process_r(cvpj_proj, 'rate')
            audiostretch_processed = True

        if 'rate' in in__placement_audio_stretch and 'rate' not in out__placement_audio_stretch:
            if cvpj_type == 'm': changestretch.process_m(cvpj_proj, 'warp')
            if cvpj_type == 'r': changestretch.process_r(cvpj_proj, 'warp')
            audiostretch_processed = True
    return json.dumps(cvpj_proj)

def makecompat_any(cvpj_l, cvpj_type, in_dawcapabilities, out_dawcapabilities):
    cvpj_proj = json.loads(cvpj_l)

    in__fxrack = in_dawcapabilities['fxrack'] if 'fxrack' in in_dawcapabilities else False
    out__fxrack = out_dawcapabilities['fxrack'] if 'fxrack' in out_dawcapabilities else False

    in__auto_nopl = in_dawcapabilities['auto_nopl'] if 'auto_nopl' in in_dawcapabilities else False
    out__auto_nopl = out_dawcapabilities['auto_nopl'] if 'auto_nopl' in out_dawcapabilities else False

    print('[compat] '+str(in__auto_nopl).ljust(5)+' | '+str(out__auto_nopl).ljust(5)+' | auto_nopl')
    print('[compat] '+str(in__fxrack).ljust(5)+' | '+str(out__fxrack).ljust(5)+' | fxrack')

    if in__fxrack == False and out__fxrack == True: trackfx2fxrack(cvpj_proj, cvpj_type)
    if in__fxrack == True and out__fxrack == False: fxrack2trackfx(cvpj_proj, cvpj_type)
    if in__auto_nopl == False and out__auto_nopl == True: autopl_remove.process(cvpj_proj)

    return json.dumps(cvpj_proj)

def makecompat_time(cvpj_l, cvpj_type, in_dawcapabilities, out_dawcapabilities):
    cvpj_proj = json.loads(cvpj_l)

    in__time_seconds = False
    out__time_seconds = False
    if 'time_seconds' in in_dawcapabilities: in__time_seconds = in_dawcapabilities['time_seconds']
    if 'time_seconds' in out_dawcapabilities: out__time_seconds = out_dawcapabilities['time_seconds']

    print('[compat] '+str(in__time_seconds).ljust(5)+' | '+str(out__time_seconds).ljust(5)+' | time_seconds')

    if in__time_seconds == False and out__time_seconds == True: time_seconds.process(cvpj_proj, cvpj_type, True)
    if in__time_seconds == True and out__time_seconds == False: time_seconds.process(cvpj_proj, cvpj_type, False)

    return json.dumps(cvpj_proj)

r_processed = False
ri_processed = False
m_processed = False
mi_processed = False

isprinted = False

def makecompat(cvpj_l, cvpj_type, in_dawcapabilities, out_dawcapabilities):
    global r_processed
    global ri_processed
    global m_processed
    global mi_processed
    global isprinted

    cvpj_proj = json.loads(cvpj_l)

    in__track_lanes = in_dawcapabilities['track_lanes'] if 'track_lanes' in in_dawcapabilities else False
    in__track_nopl = in_dawcapabilities['track_nopl'] if 'track_nopl' in in_dawcapabilities else False
    in__track_hybrid = in_dawcapabilities['track_hybrid'] if 'track_hybrid' in in_dawcapabilities else False
    in__placement_cut = in_dawcapabilities['placement_cut'] if 'placement_cut' in in_dawcapabilities else False
    in__placement_loop = in_dawcapabilities['placement_loop'] if 'placement_loop' in in_dawcapabilities else []
    in__placement_audio_events = in_dawcapabilities['placement_audio_events'] if 'placement_audio_events' in in_dawcapabilities else False

    out__track_lanes = out_dawcapabilities['track_lanes'] if 'track_lanes' in out_dawcapabilities else False
    out__track_nopl = out_dawcapabilities['track_nopl'] if 'track_nopl' in out_dawcapabilities else False
    out__track_hybrid = out_dawcapabilities['track_hybrid'] if 'track_hybrid' in out_dawcapabilities else False
    out__placement_cut = out_dawcapabilities['placement_cut'] if 'placement_cut' in out_dawcapabilities else False
    out__placement_loop = out_dawcapabilities['placement_loop'] if 'placement_loop' in out_dawcapabilities else []
    out__placement_audio_events = out_dawcapabilities['placement_audio_events'] if 'placement_audio_events' in out_dawcapabilities else False

    if isprinted == False:
        print('[compat] '+str(in__placement_audio_events).ljust(5)+' | '+str(out__placement_audio_events).ljust(5)+' | placement_audio_events')
        print('[compat] '+str(in__placement_cut).ljust(5)+' | '+str(out__placement_cut).ljust(5)+' | placement_cut')
        print('[compat] '+str(in__placement_loop).ljust(5)+' | '+str(out__placement_loop).ljust(5)+' | placement_loop')
        print('[compat] '+str(in__track_hybrid).ljust(5)+' | '+str(out__track_hybrid).ljust(5)+' | track_hybrid')
        print('[compat] '+str(in__track_lanes).ljust(5)+' | '+str(out__track_lanes).ljust(5)+' | track_lanes')
        print('[compat] '+str(in__track_nopl).ljust(5)+' | '+str(out__track_nopl).ljust(5)+' | track_nopl')
    isprinted = True

    remainingplloop = [e for e in in__placement_loop if e not in out__placement_loop]

    if cvpj_type == 'mi' and mi_processed == False:
        if in__placement_loop != [] and remainingplloop != []: loops_remove.process_m(cvpj_proj, out__placement_loop)
        mi_processed = True

    if cvpj_type == 'r' and r_processed == False:
        if in__track_hybrid == True and out__track_hybrid == False: unhybrid.process_r(cvpj_proj)
        if in__track_nopl == True and out__track_nopl == False: trackpl_add.process_r(cvpj_proj)
        if in__track_lanes == True and out__track_lanes == False: removelanes.process_r(cvpj_proj)
        if in__placement_loop != [] and remainingplloop != []: loops_remove.process_r(cvpj_proj, out__placement_loop)
        if in__placement_cut == True and out__placement_cut == False: removecut.process_r(cvpj_proj)
        if in__placement_loop == [] and 'loop' in out__placement_loop: loops_add.process_r(cvpj_proj)
        r_processed = True

    if cvpj_type == 'ri' and ri_processed == False:
        if in__placement_loop != [] and remainingplloop != []: loops_remove.process_r(cvpj_proj, out__placement_loop)
        ri_processed = True

    return json.dumps(cvpj_proj)

