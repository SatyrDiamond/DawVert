# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import song
from functions import notelist_data
from functions import data_values
from functions import xtramath
from functions import tracks
from functions import placement_data
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

        if 'sends_audio' in track_master_data:
            for send in track_master_data['sends_audio']:
                send_data = track_master_data['sends_audio'][send]
                list2fxrack(cvpj_l, send_data, fxnum, send, '[S] ')
                fxdata[fxnum] = [['return',send],['master',None]]
                returnids[send] = fxnum
                fxnum += 1
            del track_master_data['sends_audio']
            
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


def r_removeloops_placements(cvpj_placements, tempo):
    new_placements = []
    for cvpj_placement in cvpj_placements:
        audiorate = 1
        if 'audiomod' in cvpj_placement:
            if 'stretch' in cvpj_placement['audiomod']:
                stretchdata = cvpj_placement['audiomod']['stretch']
                if 'enabled' in stretchdata:
                    if stretchdata['enabled'] == True:
                        if 'time' in stretchdata:
                            if 'data' in stretchdata['time']:
                                if 'rate' in stretchdata['time']['data']:
                                    audiorate = stretchdata['time']['data']['rate']

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
                    placement_data.time_from_steps(cvpj_placement_cutted['cut'], 'start', True, cutpoint[2], tempo, audiorate)
                    placement_data.time_from_steps(cvpj_placement_cutted['cut'], 'end', True, cutpoint[3], tempo, audiorate)

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
                            track_placements_data['notes'] = r_removeloops_placements(tj_lanedata['notes'], tempo)

            if not_laned == True:
                print('[compat] RemoveLoops: non-laned: '+track_placements_id)
                if 'notes' in track_placements_data:
                    track_placements_data['notes'] = r_removeloops_placements(track_placements_data['notes'], tempo)
                if 'audio' in track_placements_data:
                    track_placements_data['audio'] = r_removeloops_placements(track_placements_data['audio'], tempo)

def m_removeloops(projJ):
    tempo = projJ['bpm']
    for playlist_id in projJ['playlist']:
        playlist_id_data = projJ['playlist'][playlist_id]
        if 'placements_notes' in playlist_id_data:
            playlist_id_data['placements_notes'] = r_removeloops_placements(playlist_id_data['placements_notes'], tempo)

# -------------------------------------------- r_track_lanes --------------------------------------------

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

# -------------------------------------------- no_placements --------------------------------------------

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

# -------------------------------------------- no_pl_auto --------------------------------------------


def remove_auto_placements_single(autodata):
    new_points = []
    for autopart in autodata:
        #print(autopart)
        base_pos = autopart['position']
        for oldpoint in autopart['points']:
            oldpoint['position'] += base_pos
            new_points.append(oldpoint)
    if len(new_points) != 0: return [{'position': 0, 'points': new_points, 'duration': new_points[-1]['position']+8}]
    else: return []

def remove_auto_placements(cvpj_l):
    if 'automation' in cvpj_l:
        cvpj_auto = cvpj_l['automation']
        for autotype in cvpj_auto:
            #print('CAT', autotype)
            if autotype in ['main']:
                for autoid in cvpj_auto[autotype]:
                    #print('PARAM', autoid)
                    cvpj_auto[autotype][autoid] = remove_auto_placements_single(cvpj_auto[autotype][autoid])
            else:
                for packid in cvpj_auto[autotype]:
                    #print('PACK', packid)
                    for autoid in cvpj_auto[autotype][packid]:
                        #print('PARAM', autoid)
                        cvpj_auto[autotype][packid][autoid] = remove_auto_placements_single(cvpj_auto[autotype][packid][autoid])
                    

# -------------------------------------------- Main --------------------------------------------

def makecompat_any(cvpj_l, cvpj_type, in_dawcapabilities, out_dawcapabilities):
    cvpj_proj = json.loads(cvpj_l)

    in__fxrack = False
    out__fxrack = False
    if 'fxrack' in in_dawcapabilities: in__fxrack = in_dawcapabilities['fxrack']
    if 'fxrack' in out_dawcapabilities: out__fxrack = out_dawcapabilities['fxrack']

    in__no_pl_auto = False
    out__no_pl_auto = False
    if 'no_pl_auto' in in_dawcapabilities: in__no_pl_auto = in_dawcapabilities['no_pl_auto']
    if 'no_pl_auto' in out_dawcapabilities: out__no_pl_auto = out_dawcapabilities['no_pl_auto']

    print('[compat] ----------------+-------+-------+')
    print('[compat] Name            | In    | Out   |')
    print('[compat] ----------------+-------+-------+')
    print('[compat] fxrack          | '+str(in__fxrack).ljust(5)+' | '+str(out__fxrack).ljust(5)+' |')
    print('[compat] no_pl_auto      | '+str(in__no_pl_auto).ljust(5)+' | '+str(out__no_pl_auto).ljust(5)+' |')
    print('[compat] ----------------+-------+-------+')

    if in__fxrack == False and out__fxrack == True: trackfx2fxrack(cvpj_proj, cvpj_type)
    if in__no_pl_auto == False and out__no_pl_auto == True: remove_auto_placements(cvpj_proj)
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

    in__r_track_lanes = False
    in__placement_cut = False
    in__placement_loop = False
    in__no_placements = False
    in__audio_events = False

    out__r_track_lanes = False
    out__placement_cut = False
    out__placement_loop = False
    out__no_placements = False
    out__audio_events = False

    if 'r_track_lanes' in in_dawcapabilities: in__r_track_lanes = in_dawcapabilities['r_track_lanes']
    if 'placement_cut' in in_dawcapabilities: in__placement_cut = in_dawcapabilities['placement_cut']
    if 'placement_loop' in in_dawcapabilities: in__placement_loop = in_dawcapabilities['placement_loop']
    if 'no_placements' in in_dawcapabilities: in__no_placements = in_dawcapabilities['no_placements']
    if 'audio_events' in in_dawcapabilities: in__audio_events = in_dawcapabilities['audio_events']

    if 'r_track_lanes' in out_dawcapabilities: out__r_track_lanes = out_dawcapabilities['r_track_lanes']
    if 'placement_cut' in out_dawcapabilities: out__placement_cut = out_dawcapabilities['placement_cut']
    if 'placement_loop' in out_dawcapabilities: out__placement_loop = out_dawcapabilities['placement_loop']
    if 'no_placements' in out_dawcapabilities: out__no_placements = out_dawcapabilities['no_placements']
    if 'audio_events' in out_dawcapabilities: out__audio_events = out_dawcapabilities['audio_events']

    if isprinted == False:
        print('[compat] ----------------+-------+-------+')
        print('[compat] Name            | In    | Out   |')
        print('[compat] ----------------+-------+-------+')
        print('[compat] r_track_lanes   | '+str(in__r_track_lanes).ljust(5)+' | '+str(out__r_track_lanes).ljust(5)+' |')
        print('[compat] placement_cut   | '+str(in__placement_cut).ljust(5)+' | '+str(out__placement_cut).ljust(5)+' |')
        print('[compat] placement_loop  | '+str(in__placement_loop).ljust(5)+' | '+str(out__placement_loop).ljust(5)+' |')
        print('[compat] no_placements   | '+str(in__no_placements).ljust(5)+' | '+str(out__no_placements).ljust(5)+' |')
        print('[compat] pl_audio_events | '+str(in__audio_events).ljust(5)+' | '+str(out__audio_events).ljust(5)+' |')
        print('[compat] ----------------+-------+-------+')
    isprinted = True

    if cvpj_type == 'm' and m_processed == False:
        if in__placement_loop == True and out__placement_loop == False: m_removeloops(cvpj_proj)
        m_processed = True

    if cvpj_type == 'mi' and mi_processed == False:
        if in__placement_loop == True and out__placement_loop == False: m_removeloops(cvpj_proj)
        mi_processed = True

    if cvpj_type == 'r' and r_processed == False:
        if in__no_placements == True and out__no_placements == False: r_split_single_notelist(cvpj_proj)
        if in__r_track_lanes == True and out__r_track_lanes == False: r_removelanes(cvpj_proj)
        if in__placement_loop == True and out__placement_loop == False: r_removeloops(cvpj_proj)
        if in__placement_cut == True and out__placement_cut == False: r_removecut(cvpj_proj)
        if in__placement_loop == False and out__placement_loop == True: r_addloops(cvpj_proj)
        r_processed = True

    if cvpj_type == 'ri' and ri_processed == False:
        if in__placement_loop == True and out__placement_loop == False: r_removeloops(cvpj_proj)
        ri_processed = True

    return json.dumps(cvpj_proj)

