# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_values
from functions_tracks import tracks_r
from functions_tracks import auto_data
from functions_tracks import trackfx

def process_r(cvpj_l):
    if 'fxrack' in cvpj_l:
        cvpj_fxrack = cvpj_l['fxrack']
        if '0' in cvpj_fxrack:
            print('[compat] fxrack2trackfx: FX 0 to Master')
            cvpj_l['track_master'] = cvpj_fxrack['0']

        auto_data.move(cvpj_l, ['fxmixer','0','vol'], ['master','vol'])
        auto_data.move(cvpj_l, ['fxmixer','0','pan'], ['master','pan'])
        fx_trackids = {}
        for cvpj_trackid, s_trackdata, track_placements in tracks_r.iter(cvpj_l):
            cvpj_track_fxnum = tracks_r.track_fxrackchan_get(cvpj_l, cvpj_trackid)

            if cvpj_track_fxnum not in fx_trackids: fx_trackids[cvpj_track_fxnum] = []
            fx_trackids[cvpj_track_fxnum].append(cvpj_trackid)
            if 'fxrack_channel' in s_trackdata: del s_trackdata['fxrack_channel']
            if cvpj_track_fxnum != 0: s_trackdata['group'] = 'fxrack_'+str(cvpj_track_fxnum)

        if 0 in fx_trackids: del fx_trackids[0]

        for fx_trackid in fx_trackids:
            cvpj_fxdata = cvpj_fxrack[str(fx_trackid)] if str(fx_trackid) in cvpj_fxrack else {}
            if 'sends' in cvpj_fxdata: del cvpj_fxdata['sends']
            groupid = 'fxrack_'+str(fx_trackid)
            trackfx.group_add(cvpj_l, groupid, None)
            cvpj_l['groups'][groupid] |= cvpj_fxdata
            print('[compat] fxrack2trackfx: FX to Tracks '+ ', '.join(fx_trackids[fx_trackid]))
    return True

def process(cvpj_l, cvpj_type, in_compat, out_compat):
    if in_compat == True and out_compat == False:
        if cvpj_type in ['r', 'ri', 'rm']: return process_r(cvpj_l)
        else: return False
    else: return False