from functions_tracks import tracks_r

def trackfx_to_numdata_track(trackid, ingroupnum): 
    global tracknum
    global output_ids
    global idnum_tracks
    global idnum_return
    global idnum_group

    if ingroupnum == None: output_ids.append([tracknum, 'track', trackid, [-1, 1, None], []  ])
    else: output_ids.append([tracknum, 'track', trackid, [ingroupnum, 1, None], []  ])
    idnum_tracks[trackid] = tracknum

    cvpj_track_data = cvpj_l['track_data'][trackid]
    tracknum = idnum_tracks[trackid]
    if 'sends_audio' in cvpj_track_data:
        for senddata in cvpj_track_data['sends_audio']:
            returnnum = idnum_return[senddata['sendid']]
            sendautoid = senddata['sendautoid'] if 'sendautoid' in senddata else None
            output_ids[tracknum][4].append([returnnum, senddata['amount'], sendautoid])
    tracknum += 1

def trackfx_to_numdata(cvpj_l_in, order_mode): 
    global tracknum
    global output_ids
    global idnum_tracks
    global idnum_return
    global idnum_group
    global cvpj_l

    cvpj_l = cvpj_l_in

    group_trk = {}
    nogroup_trk = []

    for cvpj_trackid, s_trackdata, track_placements in tracks_r.iter(cvpj_l):
        inside_group = s_trackdata['group'] if 'group' in s_trackdata else None
        if inside_group != None:
            if inside_group not in group_trk: group_trk[inside_group] = []
            group_trk[inside_group].append(cvpj_trackid)
        else:
            nogroup_trk.append(cvpj_trackid)

    output_ids = []
    idnum_group = {}
    groups_inside = {}
    idnum_return = {}
    idnum_tracks = {}

    tracknum = 0
    if 'track_master' in cvpj_l:
        track_master = cvpj_l['track_master']
        if 'returns' in track_master:
            for returnid in track_master['returns']:
                idnum_return[returnid] = tracknum
                output_ids.append([tracknum, 'return', returnid, [-1, 1, None], []])
                tracknum += 1

    for groupid in group_trk:
        cvpj_group_data = cvpj_l['groups'][groupid]
        parent_group = cvpj_group_data['parent_group'] if 'parent_group' in cvpj_group_data else None
        if parent_group != None: groups_inside[tracknum] = parent_group
        idnum_group[groupid] = tracknum
        output_ids.append([tracknum, 'group', groupid, [-1, 1, None], []  ])
        tracknum += 1
        if order_mode == 0:
            for trackid in group_trk[groupid]:
                trackfx_to_numdata_track(trackid, idnum_group[groupid])

    if order_mode == 1:
        for groupid in group_trk:
            for trackid in group_trk[groupid]:
                trackfx_to_numdata_track(trackid, idnum_group[groupid])


    for groupidnum in groups_inside:
        output_ids[groupidnum][3] = [idnum_group[groups_inside[groupidnum]], 1, None]

    for trackid in nogroup_trk:
        trackfx_to_numdata_track(trackid, None)

    for groupid in group_trk:
        if 'sends_audio' in cvpj_group_data:
            for senddata in cvpj_group_data['sends_audio']:
                groupidnum = idnum_group[groupid]
                returnnum = idnum_return[senddata['sendid']]
                sendautoid = senddata['sendautoid'] if 'sendautoid' in senddata else None
                output_ids[groupidnum][4].append([returnnum, senddata['amount'], sendautoid])

    return output_ids

