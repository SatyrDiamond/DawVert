# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later


def do_placements(placementsdata):
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
                                new_placements[-1]['cut']['loopend'] = p_dur
                                new_placements[-1]['duration'] += p_dur
                            else:
                                new_placements[-1]['duration'] += p_dur
        if ipnl == False:
            new_placements.append(placement)
        prevpp = [p_pos, p_dur, p_nl]
    return new_placements

def process_r(projJ):
    do_addloop = True
    if 'do_addloop' in projJ: do_addloop = projJ['do_addloop']
    if do_addloop == True: 
        track_placements = projJ['track_placements']
        for track_placement in track_placements:
            if 'notes' in track_placements[track_placement]:
                plcount_before = len(track_placements[track_placement]['notes'])
                print('[compat] AddLoops: '+ track_placement +': ', end='')
                track_placement_s = track_placements[track_placement]
                track_placements[track_placement]['notes'] = do_placements(track_placement_s['notes'])
                plcount_after = len(track_placements[track_placement]['notes'])
                if plcount_before != plcount_after: print(str(plcount_before-plcount_after)+' loops found')
                else: print('unchanged')
    return True

def process(projJ, cvpj_type, in__placement_loop, out__placement_loop):
    if in__placement_loop == [] and 'loop' in out__placement_loop:
        if cvpj_type == 'r': return process_r(projJ)
        else: return False
    else: return False