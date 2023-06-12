# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import song
from functions import notelist_data
from functions import data_values
from functions import xtramath
from functions import tracks
from functions import data_values
from functions import audio
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
        tracks.add_fxslot(cvpj_l, ['fxrack', fxnum], 'audio', input_list['chain_fx_audio'])
        del input_list['chain_fx_audio']


def trackfx2fxrack(cvpj_l, cvpjtype):
    if cvpjtype == 'r' or cvpjtype == 'ri':
        r_trackfx2fxrack(cvpj_l, cvpjtype)
    else:
        o_trackfx2fxrack(cvpj_l, cvpjtype)

def r_trackfx2fxrack(cvpj_l, cvpjtype):
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
        s_trkdata['fxrack_channel'] = fxnum

        fxnum += 1

    #print(outfxnum)

    print('[r_trackfx2fxrack] Num ', 'type'.ljust(8), 'id'.ljust(12), 'dest'.ljust(8), 'dest_id'.ljust(12))
    for fxslot in fxdata:
        slotdata = fxdata[fxslot]

        out_fx_send = [0, 1.0]

        if slotdata[1][0] == 'group':
            if 'group' in outfxnum:
                if slotdata[1][1] in outfxnum['group']:
                    out_fx_send = outfxnum['group'][slotdata[1][1]]

        tracks.fxrack_addsend(cvpj_l, fxslot, out_fx_send[0], out_fx_send[1], None)

        print('[r_trackfx2fxrack] '+str(fxslot).rjust(4), 
              str(slotdata[0][0]).ljust(8), 
              str(slotdata[0][1]).ljust(12), 
              str(slotdata[1][0]).ljust(8),
              str(slotdata[1][1]).ljust(12),
              out_fx_send)

def o_trackfx2fxrack(cvpj_l, cvpjtype):
    cvpj_l['fxrack'] = {}
    fxnum = 1
    if cvpjtype == 'r' or cvpjtype == 'ri':
        c_orderingdata = cvpj_l['track_order']
        c_trackdata = cvpj_l['track_data']
    if cvpjtype == 'm' or cvpjtype == 'mi':
        c_orderingdata = cvpj_l['instruments_order']
        c_trackdata = cvpj_l['instruments_data']

    if 'track_master' in cvpj_l:
        print('[compat] trackfx2fxrack: Master to FX 0')
        cvpj_l['fxrack']['0'] = cvpj_l['track_master']

    for trackid in c_orderingdata:
        trackdata = c_trackdata[trackid]
        trackdata['fxrack_channel'] = fxnum
        fxtrack = {}
        if 'name' in trackdata: 
            fxtrack['name'] = trackdata['name']
            print('[compat] trackfx2fxrack: Track to FX '+str(fxnum)+' ('+str(trackdata['name'])+')')
        else:
            print('[compat] trackfx2fxrack: Track to FX '+str(fxnum))

        if 'color' in trackdata: fxtrack['color'] = trackdata['color']
        if 'fxchain_audio' in trackdata: 
            fxtrack['fxchain_audio'] = trackdata['fxchain_audio']
            del trackdata['fxchain_audio']
        cvpj_l['fxrack'][str(fxnum)] = fxtrack
        fxnum += 1

# -------------------------------------------- placement_cut --------------------------------------------

def r_removecut_placements(note_placements):
    for note_placement in note_placements:
        if 'cut' in note_placement: 
            if note_placement['cut']['type'] == 'cut': 
                if 'start' in note_placement['cut']: cut_start = note_placement['cut']['start']
                if 'end' in note_placement['cut']: cut_end = note_placement['cut']['end']
                note_placement['notelist'] = notelist_data.trimmove(note_placement['notelist'], cut_start, cut_end)
                del note_placement['cut']

def r_removecut(projJ):
    if 'track_placements' in projJ:
        for track_placements_id in projJ['track_placements']:
            track_placements_data = projJ['track_placements'][track_placements_id]

            not_laned = True

            if 'laned' in track_placements_data:
                print('[compat] RemoveCut: laned: '+track_placements_id)
                if s_pldata['laned'] == 1:
                    not_laned = False
                    s_lanedata = s_pldata['lanedata']
                    s_laneordering = s_pldata['laneorder']
                    for t_lanedata in s_lanedata:
                        tj_lanedata = s_lanedata[t_lanedata]
                        if 'notes' in tj_lanedata:
                            r_removecut_placements(tj_lanedata['notes'])

            if not_laned == True:
                if 'notes' in track_placements_data:
                    print('[compat] RemoveCut: non-laned: '+track_placements_id)
                    r_removecut_placements(track_placements_data['notes'])


# -------------------------------------------- placement_loop --------------------------------------------

def addloops_pl(placementsdata):
    prevpp = None
    new_placements = []
    for placement in placementsdata:
        p_pos = placement['position']
        p_dur = placement['duration']
        if 'notelist' in placement: p_nl = placement['notelist']
        else: p_nl = []
        ipnl = False
        if prevpp != None:
            isfromprevpos = prevpp[0]==p_pos-p_dur
            isdursame = prevpp[1]==p_dur
            issamenotelist = prevpp[2]==p_nl
            isplacecut = 'cut' in placement
            prevpp[0]==p_pos-p_dur
            if isfromprevpos == True:
                if issamenotelist == True:
                    if isdursame == True:
                        if isplacecut == False:
                            ipnl = True
                            if 'cut' not in new_placements[-1]:
                                new_placements[-1]['cut'] = {}
                                new_placements[-1]['cut']['type'] = 'loop'
                                new_placements[-1]['cut']['start'] = 0
                                new_placements[-1]['cut']['loopstart'] = 0
                                new_placements[-1]['cut']['loopend'] = p_dur
                                new_placements[-1]['duration'] += p_dur
                            else:
                                new_placements[-1]['duration'] += p_dur
        if ipnl == False:
            new_placements.append(placement)
        prevpp = [p_pos, p_dur, p_nl]
    return new_placements

def r_addloops(projJ):
    do_addloop = True
    if 'do_addloop' in projJ: do_addloop = projJ['do_addloop']
    if do_addloop == True: 
        track_placements = projJ['track_placements']
        for track_placement in track_placements:
            if 'notes' in track_placements[track_placement]:
                plcount_before = len(track_placements[track_placement]['notes'])
                print('[compat] AddLoops: '+ track_placement +': ', end='')
                track_placement_s = track_placements[track_placement]
                track_placements[track_placement]['notes'] = addloops_pl(track_placement_s['notes'])
                plcount_after = len(track_placements[track_placement]['notes'])
                if plcount_before != plcount_after: print(str(plcount_before-plcount_after)+' loops found')
                else: print('unchanged')


def r_removeloops_cutpoint(pl_pos, pl_dur, cut_start, cut_end):
    return [pl_pos, pl_dur, cut_start, cut_end]

def r_removeloops_before_loop(bl_p_pos, bl_p_dur, bl_p_start, bl_l_start, bl_l_end):
    #print('BEFORE')
    cutpoints = []
    temppos = min(bl_l_end, bl_p_dur)
    cutpoints.append( r_removeloops_cutpoint((bl_p_pos+bl_p_start)-bl_p_start, temppos-bl_p_start, bl_p_start, min(bl_l_end, bl_p_dur)) )
    bl_p_dur += bl_p_start
    placement_loop_size = bl_l_end-bl_l_start
    if bl_l_end < bl_p_dur and bl_l_end > bl_l_start:
        remainingcuts = (bl_p_dur-bl_l_end)/placement_loop_size
        while remainingcuts > 0:
            outdur = min(remainingcuts, 1)
            cutpoints.append( r_removeloops_cutpoint((bl_p_pos+temppos)-bl_p_start, placement_loop_size*outdur, bl_l_start, bl_l_end*outdur) )
            temppos += placement_loop_size
            remainingcuts -= 1
    return cutpoints

def r_removeloops_after_loop(bl_p_pos, bl_p_dur, bl_p_start, bl_l_start, bl_l_end):
    #print('AFTER')
    cutpoints = []
    placement_loop_size = bl_l_end-bl_l_start
    #print(bl_p_pos, bl_p_dur, '|', bl_p_start, '|', bl_l_start, bl_l_end, '|', placement_loop_size)
    bl_p_dur_mo = bl_p_dur-bl_l_start
    bl_p_start_mo = bl_p_start-bl_l_start
    bl_l_start_mo = bl_l_start-bl_l_start
    bl_l_end_mo = bl_l_end-bl_l_start
    remainingcuts = (bl_p_dur_mo+bl_p_start_mo)/placement_loop_size
    #print(bl_p_pos, bl_p_dur, '|', bl_p_start_mo, '|', bl_l_start_mo, bl_l_end_mo, '|', placement_loop_size)
    temppos = bl_p_pos
    temppos -= bl_p_start_mo
    flag_first_pl = True
    while remainingcuts > 0:
        outdur = min(remainingcuts, 1)
        if flag_first_pl == True:
            cutpoints.append( r_removeloops_cutpoint(temppos+bl_p_start_mo, (outdur*placement_loop_size)-bl_p_start_mo, bl_l_start+bl_p_start_mo, outdur*bl_l_end) )
        if flag_first_pl == False:
            cutpoints.append( r_removeloops_cutpoint(temppos, outdur*placement_loop_size, bl_l_start, outdur*bl_l_end) )
        temppos += placement_loop_size
        remainingcuts -= 1
        flag_first_pl = False
    return cutpoints


def r_removeloops_placements(cvpj_placements, tempo, isaudio):
    tempomul = data_values.tempo_to_rate(tempo, False)

    new_placements = []
    for cvpj_placement in cvpj_placements:

        if 'cut' in cvpj_placement: 
            if cvpj_placement['cut']['type'] == 'loop': 
                cvpj_placement_base = cvpj_placement.copy()
                del cvpj_placement_base['cut']
                del cvpj_placement_base['position']
                del cvpj_placement_base['duration']
                loop_base_position = cvpj_placement['position']
                loop_base_duration = cvpj_placement['duration']
                loop_start = cvpj_placement['cut']['start']
                loop_loopstart = cvpj_placement['cut']['loopstart']
                loop_loopend = cvpj_placement['cut']['loopend']

                if loop_loopstart > loop_start: cutpoints = r_removeloops_before_loop(loop_base_position, loop_base_duration, loop_start, loop_loopstart, loop_loopend)
                else: cutpoints = r_removeloops_after_loop(loop_base_position, loop_base_duration, loop_start, loop_loopstart, loop_loopend)

                #print(cutpoints)
                for cutpoint in cutpoints:
                    cvpj_placement_cutted = cvpj_placement_base.copy()
                    cvpj_placement_cutted['position'] = cutpoint[0]
                    cvpj_placement_cutted['duration'] = cutpoint[1]
                    cvpj_placement_cutted['cut'] = {}
                    cvpj_placement_cutted['cut']['type'] = 'cut'

                    if isaudio == False:
                        cvpj_placement_cutted['cut']['start'] = cutpoint[2]
                        cvpj_placement_cutted['cut']['end'] = cutpoint[3]
                    else:
                        cvpj_placement_cutted['cut']['start'] = cutpoint[2]
                        cvpj_placement_cutted['cut']['end'] = cutpoint[3]

                    new_placements.append(cvpj_placement_cutted)
            else: new_placements.append(cvpj_placement)
        else: new_placements.append(cvpj_placement)
    return new_placements

def r_removeloops(projJ):
    tempo = projJ['bpm']
    if 'track_placements' in projJ:
        for track_placements_id in projJ['track_placements']:
            track_placements_data = projJ['track_placements'][track_placements_id]

            not_laned = True

            if 'laned' in track_placements_data:
                print('[compat] RemoveLoops: laned: '+track_placements_id)
                if s_pldata['laned'] == 1:
                    not_laned = False
                    s_lanedata = s_pldata['lanedata']
                    s_laneordering = s_pldata['laneorder']
                    for t_lanedata in s_lanedata:
                        tj_lanedata = s_lanedata[t_lanedata]
                        if 'notes' in tj_lanedata:
                            track_placements_data['notes'] = r_removeloops_placements(tj_lanedata['notes'], tempo, False)
                        if 'audio' in tj_lanedata:
                            track_placements_data['audio'] = r_removeloops_placements(tj_lanedata['audio'], tempo, True)

            if not_laned == True:
                print('[compat] RemoveLoops: non-laned: '+track_placements_id)
                if 'notes' in track_placements_data:
                    track_placements_data['notes'] = r_removeloops_placements(track_placements_data['notes'], tempo, False)
                if 'audio' in track_placements_data:
                    track_placements_data['audio'] = r_removeloops_placements(track_placements_data['audio'], tempo, True)

def m_removeloops(projJ):
    tempo = projJ['bpm']
    for playlist_id in projJ['playlist']:
        playlist_id_data = projJ['playlist'][playlist_id]
        if 'placements_notes' in playlist_id_data:
            playlist_id_data['placements_notes'] = r_removeloops_placements(playlist_id_data['placements_notes'], tempo, False)

# -------------------------------------------- placement_audio_stretch --------------------------------------------


def warp2rate(cvpj_placements, tempo):
    new_placements = []
    tempomul = (120/tempo)
    for cvpj_placement in cvpj_placements:
        audiorate = 1
        minus_offset = 0
        plus_offset = 0
        if 'audiomod' in cvpj_placement:
            old_audiomod = cvpj_placement['audiomod']
            new_audiomod = {}
            new_audiomod['stretch_data'] = {}
            new_audiomod['stretch_method'] = None
            new_audiomod['stretch_algorithm'] = 'stretch'
            if 'pitch' in old_audiomod: new_audiomod['pitch'] = old_audiomod['pitch']

            if 'stretch_method' in old_audiomod: 
                if old_audiomod['stretch_method'] == 'warp':
                    t_warpmarkers = old_audiomod['stretch_data']

                    if t_warpmarkers[0]['pos'] != 0: 
                        minuswarppos = t_warpmarkers[0]['pos']
                        if t_warpmarkers[0]['pos'] < 0: minus_offset -= minuswarppos
                        if t_warpmarkers[0]['pos'] > 0: plus_offset += minuswarppos
                        for t_warpmarker in t_warpmarkers:
                            t_warpmarker['pos'] -= minuswarppos

                    #print(minus_offset, plus_offset)

                    audio_info = audio.get_audiofile_info(cvpj_placement['file'])
                    audio_dur_sec_steps = audio_info['dur_sec']*8

                    if 'stretch_algorithm' in old_audiomod: new_audiomod['stretch_algorithm'] = old_audiomod['stretch_algorithm']

                    if len(t_warpmarkers) >= 2:
                        t_warpmarker_last = t_warpmarkers[-1]
                        new_audiomod['stretch_method'] = 'rate_tempo'
                        audiorate = (1/((t_warpmarker_last['pos']/8)/t_warpmarkers[-1]['pos_real']))
                        new_audiomod['stretch_data']['rate'] = audiorate

            cvpj_placement['audiomod'] = new_audiomod

        if 'cut' in cvpj_placement:
            cutdata = cvpj_placement['cut']

            if audiorate != 1:
                if cutdata['type'] == 'loop':
                    data_values.time_from_steps(cutdata, 'start', True, cutdata['start']+minus_offset, audiorate)
                    data_values.time_from_steps(cutdata, 'loopstart', True, cutdata['loopstart']+minus_offset, audiorate)
                    data_values.time_from_steps(cutdata, 'loopend', True, cutdata['loopend']+minus_offset, audiorate )
                    cvpj_placement['position'] += plus_offset
                    cvpj_placement['duration'] -= plus_offset
                    cvpj_placement['duration'] += minus_offset

                if cutdata['type'] == 'cut':
                    data_values.time_from_steps(cutdata, 'start', True, cutdata['start']+minus_offset, (1/audiorate)*tempomul )
                    data_values.time_from_steps(cutdata, 'end', True, cutdata['end']+minus_offset-plus_offset, (1/audiorate)*tempomul )

    return cvpj_placements

def rate2warp(cvpj_placements, tempo):
    new_placements = []
    tempomul = (120/tempo)

    for cvpj_placement in cvpj_placements:
        audiorate = 1
        ratetempo = 1

        if 'audiomod' in cvpj_placement:
            old_audiomod = cvpj_placement['audiomod']
            new_audiomod = {}

            if 'stretch_method' in old_audiomod: 
                if old_audiomod['stretch_method'] in ['rate_tempo', 'rate_speed', 'rate_ignoretempo']:
                    audio_info = audio.get_audiofile_info(cvpj_placement['file'])
                    audio_dur_sec = audio_info['dur_sec']

                    t_stretch_data = old_audiomod['stretch_data']

                    new_audiomod = {}
                    new_audiomod['stretch_method'] = 'warp'
                    new_audiomod['stretch_algorithm'] = 'stretch'
                    if 'stretch_algorithm' in old_audiomod: new_audiomod['stretch_algorithm'] = old_audiomod['stretch_algorithm']
                    if 'pitch' in old_audiomod: new_audiomod['pitch'] = old_audiomod['pitch']

                    audiorate = t_stretch_data['rate']
                    ratetempo = 1/(audiorate/tempomul)

                    if old_audiomod['stretch_method'] == 'rate_ignoretempo':
                        new_audiomod['stretch_data'] = [
                            {'pos': 0.0, 'pos_real': 0.0}, 
                            {'pos': audio_dur_sec*8, 'pos_real': (audio_dur_sec*audiorate)/tempomul}
                        ]

                    if old_audiomod['stretch_method'] == 'rate_tempo':
                        new_audiomod['stretch_data'] = [
                            {'pos': 0.0, 'pos_real': 0.0}, 
                            {'pos': audio_dur_sec*8, 'pos_real': (audio_dur_sec*audiorate)}
                        ]

                    if old_audiomod['stretch_method'] == 'rate_speed':
                        new_audiomod['stretch_data'] = [
                            {'pos': 0.0, 'pos_real': 0.0}, 
                            {'pos': audio_dur_sec*8, 'pos_real': (audio_dur_sec*audiorate)*tempomul}
                        ]

                    cvpj_placement['audiomod'] = new_audiomod


        #if 'cut' in cvpj_placement:
        #    cutdata = cvpj_placement['cut']
        #
        #    if cutdata['type'] == 'cut':
        #        if 'start' not in cutdata: data_values.time_from_steps(cutdata, 'start', True, 0, audiorate)
        #        data_values.time_from_seconds(cutdata, 'start', False, cutdata['start'], 1)
        #        if 'end' in cutdata:
        #            data_values.time_from_seconds(cutdata, 'end', False, cutdata['end'], 1)

    return cvpj_placements

def r_changestretch(projJ, stretchtype):
    tempo = projJ['bpm']
    if 'track_placements' in projJ:
        for track_placements_id in projJ['track_placements']:
            track_placements_data = projJ['track_placements'][track_placements_id]
            not_laned = True
            if 'laned' in track_placements_data:
                print('[compat] warp2rate: laned: '+track_placements_id)
                if s_pldata['laned'] == 1:
                    not_laned = False
                    s_lanedata = s_pldata['lanedata']
                    s_laneordering = s_pldata['laneorder']
                    for t_lanedata in s_lanedata:
                        tj_lanedata = s_lanedata[t_lanedata]
                        if 'audio' in tj_lanedata:
                            if stretchtype == 'rate': 
                                print('[compat] warp2rate: laned: '+track_placements_id)
                                tj_lanedata['audio'] = warp2rate(tj_lanedata['audio'], tempo)
                            if stretchtype == 'warp': 
                                print('[compat] rate2warp: laned: '+track_placements_id)
                                tj_lanedata['audio'] = rate2warp(tj_lanedata['audio'], tempo)

            if not_laned == True:
                if 'audio' in track_placements_data:
                    if stretchtype == 'rate': 
                        print('[compat] warp2rate: non-laned: '+track_placements_id)
                        track_placements_data['audio'] = warp2rate(track_placements_data['audio'], tempo)
                    if stretchtype == 'warp': 
                        print('[compat] rate2warp: non-laned: '+track_placements_id)
                        track_placements_data['audio'] = rate2warp(track_placements_data['audio'], tempo)


def m_changestretch(projJ, stretchtype):
    tempo = projJ['bpm']
    for playlist_id in projJ['playlist']:
        playlist_id_data = projJ['playlist'][playlist_id]
        if 'placements_audio' in playlist_id_data:
            if stretchtype == 'rate': playlist_id_data['placements_audio'] = warp2rate(playlist_id_data['placements_audio'], tempo)
            if stretchtype == 'warp': playlist_id_data['placements_audio'] = rate2warp(playlist_id_data['placements_audio'], tempo)

# -------------------------------------------- track_lanes --------------------------------------------

def tracklanename(trackname, lanename, fallback):
    if trackname != None:
        if lanename != None: ntp_name = trackname+' ['+lanename+']'
        if lanename == None: ntp_name = trackname
    if trackname == None:
        if lanename != None: ntp_name = 'none'+' ['+lanename+']'
        if lanename == None: ntp_name = 'none'
    return ntp_name

def r_removelanes(projJ):
    old_trackdata = projJ['track_data']
    old_trackordering = projJ['track_order']
    old_trackplacements = projJ['track_placements']
    new_trackdata = {}
    new_trackordering = []
    new_trackplacements = {}

    for trackid in old_trackordering:
        if trackid in old_trackdata:
            print('[compat] RemoveLanes: '+ trackid)
            if trackid in old_trackplacements:

                s_trackdata = old_trackdata[trackid]
                s_pldata = old_trackplacements[trackid]

                if 'name' in s_trackdata: s_trackname = s_trackdata['name']
                else: s_trackname = None

                not_laned = True

                if 'laned' in s_pldata:
                    if s_pldata['laned'] == 1:
                        not_laned = False

                        s_lanedata = s_pldata['lanedata']
                        s_laneordering = s_pldata['laneorder']

                        if len(s_laneordering) == 0:
                            new_trackdata[trackid] = s_trackdata
                            new_trackplacements[trackid] = {}
                            new_trackplacements[trackid]['notes'] = []
                            new_trackordering.append(trackid)

                        if len(s_laneordering) == 1:
                            new_trackdata[trackid] = s_trackdata
                            new_trackplacements[trackid] = {}
                            new_trackplacements[trackid]['notes'] = s_lanedata[s_laneordering[0]]['notes']
                            new_trackordering.append(trackid)

                        if len(s_laneordering) > 1:
                            for laneid in s_laneordering:

                                splitnameid = trackid+'_Lane'+laneid

                                s_d_lanedata = s_lanedata[laneid]
                                if 'name' in s_d_lanedata: s_lanename = s_d_lanedata['name']
                                else: s_lanename = None

                                septrackname = tracklanename(s_trackname, s_lanename, 'noname')

                                new_trackdata[splitnameid] = s_trackdata.copy()
                                new_trackdata[splitnameid]['name'] = septrackname
                                new_trackplacements[splitnameid] = {}
                                new_trackplacements[splitnameid]['notes'] = s_lanedata[laneid]['notes']
                                new_trackordering.append(splitnameid)

                if not_laned == True:
                    new_trackdata[trackid] = s_trackdata
                    new_trackplacements[trackid] = s_pldata
                    new_trackordering.append(trackid)

    projJ['track_data'] = new_trackdata
    projJ['track_order'] = new_trackordering
    projJ['track_placements'] = new_trackplacements

# -------------------------------------------- track_nopl --------------------------------------------

points_items = None

def single_notelists2placements(placementsdata):
    global points_items
    timepoints = []
    numarea = len(points_items)-1

    nlname = None
    if 'name' in placementsdata[0]: nlname = placementsdata[0]['name']

    if numarea >= 1:
        for num in range(numarea):
            timepoints_part = xtramath.gen_float_range(points_items[num][0],points_items[num+1][0],points_items[num][1]*4)
            for timepoints_pp in timepoints_part:
                if timepoints_pp < points_items[num+1][0]:
                    timepoints.append([timepoints_pp, timepoints_pp+points_items[num][1]*4, False, False])
    if 'notelist' in placementsdata[0]:
        notelist = placementsdata[0]['notelist']
        for note in notelist:
            note_start = note['position']
            note_end = note['duration'] + note_start
            for timepoint in timepoints:
                position = timepoint[0]
                position_end = timepoint[1]
                note_overlap = bool(xtramath.overlap(position, position_end, note_start, note_end))
                if timepoint[2] == False: timepoint[2] = note_overlap
                if timepoint[3] == False: timepoint[3] = note_overlap and position_end<note_end
        cutranges = []
        appendnext = False
        for timepoint in timepoints:
            #print(timepoint)
            if timepoint[2] == True:
                if appendnext == False: cutranges.append([timepoint[0], timepoint[1]])
                else: cutranges[-1][1] = timepoint[1]
            appendnext = timepoint[3]
        new_placements = []
        for cutrange in cutranges:
            new_placement = {}
            new_placement['notelist'] = notelist_data.trimmove(notelist, cutrange[0], cutrange[1])
            if nlname != None: new_placement['name'] = nlname
            new_placement['position'] = cutrange[0]
            new_placement['duration'] = cutrange[1]-cutrange[0]
            new_placements.append(new_placement)
    return new_placements

def create_points_cut(projJ):
    global points_items
    if points_items == None:
        songduration = song.r_getduration(projJ)
        if 'timesig_numerator' in projJ:
            timesig_numerator = projJ['timesig_numerator']
        else: timesig_numerator = 4
        points = {}
        points[0] = timesig_numerator
        if 'timemarkers' in projJ:
            for timemarker in projJ['timemarkers']:
                if 'type' in timemarker:
                    if timemarker['type'] == 'timesig':
                        points[timemarker['position']] = timemarker['numerator']
        points[songduration] = 4
        points = dict(sorted(points.items(), key=lambda item: item[0]))
        points_items = [(k,v) for k,v in points.items()]

def r_split_single_notelist(projJ):
    global points_items
    create_points_cut(projJ)
    if 'do_singlenotelistcut' in projJ:
        if projJ['do_singlenotelistcut'] == True:
            track_placements = projJ['track_placements']
            for trackid in track_placements:
                islaned = False
                if 'laned' in track_placements[trackid]:
                    if track_placements[trackid]['laned'] == 1:
                        islaned = True
                if islaned == False:
                    if 'notes' in track_placements[trackid]:
                        placementdata = track_placements[trackid]['notes']
                        if len(placementdata) == 1:
                            track_placements[trackid]['notes'] = single_notelists2placements(placementdata)
                            print('[compat] singlenotelist2placements: non-laned: splitted "'+trackid+'" to '+str(len(track_placements[trackid]['notes'])) + ' placements.')
                else:
                    for s_lanedata in track_placements[trackid]['lanedata']:
                        placementdata = track_placements[trackid]['lanedata'][s_lanedata]['notes']
                        if len(placementdata) == 1:
                            track_placements[trackid]['lanedata'][s_lanedata]['notes'] = single_notelists2placements(placementdata)
                            print('[compat] singlenotelist2placements: laned: splitted "'+trackid+'" from lane "'+str(s_lanedata)+'" to '+str(len(track_placements[trackid]['lanedata'][s_lanedata]['notes'])) + ' placements.')
    projJ['do_singlenotelistcut'] = False

# -------------------------------------------- auto_nopl --------------------------------------------

def remove_auto_placements_single(i_autodata):
    new_points = []
    autotype = i_autodata['type']
    autodata = i_autodata['placements']
    for autopart in autodata:
        base_pos = autopart['position']
        if len(autopart['points']) != 0: autopart['points'][0]['type'] = 'instant'
        for oldpoint in autopart['points']:
            oldpoint['position'] += base_pos
            new_points.append(oldpoint)
    if len(new_points) != 0: 
        o_autodata = {}
        o_autodata['type'] = autotype
        o_autodata['placements'] = [{'position': 0, 'points': new_points, 'duration': new_points[-1]['position']+8}]
        return o_autodata
    else: 
        o_autodata = {}
        o_autodata['type'] = autotype
        o_autodata['placements'] = []
        return o_autodata

def remove_auto_placements(cvpj_l):
    if 'automation' in cvpj_l:
        cvpj_auto = cvpj_l['automation']
        for autotype in cvpj_auto:
            #print('CAT', autotype)
            if autotype == 'main':
                for autoid in cvpj_auto[autotype]:
                    #print('PARAM', autoid)
                    cvpj_auto[autotype][autoid] = remove_auto_placements_single(cvpj_auto[autotype][autoid])
            else:
                for packid in cvpj_auto[autotype]:
                    #print('PACK', packid)
                    for autoid in cvpj_auto[autotype][packid]:
                        #print('PARAM', autoid)
                        cvpj_auto[autotype][packid][autoid] = remove_auto_placements_single(cvpj_auto[autotype][packid][autoid])
                    
# -------------------------------------------- time_seconds --------------------------------------------

def step2sec(i_value, i_bpm): return (i_value/8)*(120/i_bpm)

def beats_to_seconds_dopls(cvpj_placements, i_bpm):
    for cvpj_placement in cvpj_placements:
        if 'position' in cvpj_placement: cvpj_placement['position'] = step2sec(cvpj_placement['position'], i_bpm)
        if 'duration' in cvpj_placement: cvpj_placement['duration'] = step2sec(cvpj_placement['duration'], i_bpm)

def beats_to_seconds_all(s_track_pl, i_bpm):
    if 'notes' in s_track_pl: beats_to_seconds_dopls(s_track_pl['notes'], i_bpm)
    if 'audio' in s_track_pl: beats_to_seconds_dopls(s_track_pl['audio'], i_bpm)
    if 'placements_notes' in s_track_pl: beats_to_seconds_dopls(s_track_pl['placements_notes'], i_bpm)
    if 'placements_audio' in s_track_pl: beats_to_seconds_dopls(s_track_pl['placements_audio'], i_bpm)

def beats_to_seconds(cvpj_l, cvpj_type):
    bpm = 120
    if 'bpm' in cvpj_l: bpm = cvpj_l['bpm']
    print('[compat] Beats2Seconds: BPM:', bpm)

    if cvpj_type in ['r', 'ri']:
        if 'track_placements' in cvpj_l:
            for id_track_pl in cvpj_l['track_placements']:
                s_track_pl = cvpj_l['track_placements'][id_track_pl]
                beats_to_seconds_all(s_track_pl, bpm)
    if cvpj_type in ['m', 'mi']:
        for playlist_id in cvpj_l['playlist']:
            playlist_id_data = cvpj_l['playlist'][playlist_id]
            beats_to_seconds_all(playlist_id_data, bpm)

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
            if cvpj_type == 'm': m_changestretch(cvpj_proj, 'rate')
            if cvpj_type == 'r': r_changestretch(cvpj_proj, 'rate')
            audiostretch_processed = True

        if 'rate' in in__placement_audio_stretch and 'warp' in out__placement_audio_stretch:
            if cvpj_type == 'm': m_changestretch(cvpj_proj, 'warp')
            if cvpj_type == 'r': r_changestretch(cvpj_proj, 'warp')
            audiostretch_processed = True
    return json.dumps(cvpj_proj)

def makecompat_any(cvpj_l, cvpj_type, in_dawcapabilities, out_dawcapabilities):
    cvpj_proj = json.loads(cvpj_l)

    in__fxrack = False
    out__fxrack = False
    if 'fxrack' in in_dawcapabilities: in__fxrack = in_dawcapabilities['fxrack']
    if 'fxrack' in out_dawcapabilities: out__fxrack = out_dawcapabilities['fxrack']

    in__auto_nopl = False
    out__auto_nopl = False
    if 'auto_nopl' in in_dawcapabilities: in__auto_nopl = in_dawcapabilities['auto_nopl']
    if 'auto_nopl' in out_dawcapabilities: out__auto_nopl = out_dawcapabilities['auto_nopl']

    in__time_seconds = False
    out__time_seconds = False
    if 'time_seconds' in in_dawcapabilities: in__time_seconds = in_dawcapabilities['time_seconds']
    if 'time_seconds' in out_dawcapabilities: out__time_seconds = out_dawcapabilities['time_seconds']

    print('[compat] '+str(in__auto_nopl).ljust(5)+' | '+str(out__auto_nopl).ljust(5)+' | auto_nopl')
    print('[compat] '+str(in__fxrack).ljust(5)+' | '+str(out__fxrack).ljust(5)+' | fxrack')
    print('[compat] '+str(in__time_seconds).ljust(5)+' | '+str(out__time_seconds).ljust(5)+' | time_seconds')

    if in__fxrack == False and out__fxrack == True: trackfx2fxrack(cvpj_proj, cvpj_type)
    if in__auto_nopl == False and out__auto_nopl == True: remove_auto_placements(cvpj_proj)
    if in__time_seconds == False and out__time_seconds == True: beats_to_seconds(cvpj_proj, cvpj_type)

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

    in__track_lanes = False
    in__placement_cut = False
    in__placement_loop = False
    in__track_nopl = False
    in__placement_audio_events = False

    out__track_lanes = False
    out__placement_cut = False
    out__placement_loop = False
    out__track_nopl = False
    out__placement_audio_events = False

    if 'track_lanes' in in_dawcapabilities: in__track_lanes = in_dawcapabilities['track_lanes']
    if 'track_nopl' in in_dawcapabilities: in__track_nopl = in_dawcapabilities['track_nopl']
    if 'placement_cut' in in_dawcapabilities: in__placement_cut = in_dawcapabilities['placement_cut']
    if 'placement_loop' in in_dawcapabilities: in__placement_loop = in_dawcapabilities['placement_loop']
    if 'placement_audio_events' in in_dawcapabilities: in__placement_audio_events = in_dawcapabilities['placement_audio_events']

    if 'track_lanes' in out_dawcapabilities: out__track_lanes = out_dawcapabilities['track_lanes']
    if 'track_nopl' in out_dawcapabilities: out__track_nopl = out_dawcapabilities['track_nopl']
    if 'placement_cut' in out_dawcapabilities: out__placement_cut = out_dawcapabilities['placement_cut']
    if 'placement_loop' in out_dawcapabilities: out__placement_loop = out_dawcapabilities['placement_loop']
    if 'placement_audio_events' in out_dawcapabilities: out__placement_audio_events = out_dawcapabilities['placement_audio_events']

    if isprinted == False:
        print('[compat] '+str(in__placement_audio_events).ljust(5)+' | '+str(out__placement_audio_events).ljust(5)+' | placement_audio_events')
        print('[compat] '+str(in__placement_cut).ljust(5)+' | '+str(out__placement_cut).ljust(5)+' | placement_cut')
        print('[compat] '+str(in__placement_loop).ljust(5)+' | '+str(out__placement_loop).ljust(5)+' | placement_loop')
        print('[compat] '+str(in__track_lanes).ljust(5)+' | '+str(out__track_lanes).ljust(5)+' | track_lanes')
        print('[compat] '+str(in__track_nopl).ljust(5)+' | '+str(out__track_nopl).ljust(5)+' | track_nopl')
    isprinted = True

    #if cvpj_type == 'm' and m_processed == False:
    #    if in__placement_loop == False and out__placement_loop == True: r_addloops(cvpj_proj)
    #    m_processed = True

    if cvpj_type == 'mi' and mi_processed == False:
        if in__placement_loop == True and out__placement_loop == False: m_removeloops(cvpj_proj)
        mi_processed = True

    if cvpj_type == 'r' and r_processed == False:
        if in__track_nopl == True and out__track_nopl == False: r_split_single_notelist(cvpj_proj)
        if in__track_lanes == True and out__track_lanes == False: r_removelanes(cvpj_proj)
        if in__placement_loop == True and out__placement_loop == False: r_removeloops(cvpj_proj)
        if in__placement_cut == True and out__placement_cut == False: r_removecut(cvpj_proj)
        if in__placement_loop == False and out__placement_loop == True: r_addloops(cvpj_proj)
        r_processed = True

    if cvpj_type == 'ri' and ri_processed == False:
        if in__placement_loop == True and out__placement_loop == False: r_removeloops(cvpj_proj)
        ri_processed = True

    return json.dumps(cvpj_proj)

