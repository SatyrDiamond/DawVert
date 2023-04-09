# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

# ------------------------ Regular ------------------------

def r_create_inst(cvpj_l, trackid, instdata):
    if 'track_data' not in cvpj_l: cvpj_l['track_data'] = {}
    if 'track_order' not in cvpj_l: cvpj_l['track_order'] = []
    cvpj_inst = {}
    cvpj_inst['type'] = 'instrument'
    cvpj_inst['instdata'] = instdata
    cvpj_l['track_data'][trackid] = cvpj_inst
    cvpj_l['track_order'].append(trackid)

def r_create_audio(cvpj_l, trackid, audiodata):
    if 'track_data' not in cvpj_l: cvpj_l['track_data'] = {}
    if 'track_order' not in cvpj_l: cvpj_l['track_order'] = []
    cvpj_inst = {}
    cvpj_inst['type'] = 'audio'
    cvpj_inst['audiodata'] = audiodata
    cvpj_l['track_data'][trackid] = cvpj_inst
    cvpj_l['track_order'].append(trackid)

def r_basicdata(cvpj_l, trackid, trk_name, trk_color, trk_vol, trk_pan):
    if 'track_data' in cvpj_l:
        if trackid in cvpj_l['track_data']:
            cvpj_inst = cvpj_l['track_data'][trackid]
            if trk_name != None: cvpj_inst['name'] = trk_name
            if trk_color != None: cvpj_inst['color'] = trk_color
            if trk_vol != None: cvpj_inst['vol'] = trk_vol
            if trk_pan != None: cvpj_inst['pan'] = trk_pan

def r_param_inst(cvpj_l, trackid, v_name, v_value):
    if 'track_data' in cvpj_l:
        if trackid in cvpj_l['track_data']:
            if 'instdata' not in cvpj_l['track_data'][trackid]: cvpj_l['track_data'][trackid]['instdata'] = {}
            cvpj_inst = cvpj_l['track_data'][trackid]['instdata']
            cvpj_inst[v_name] = v_value

def r_param(cvpj_l, trackid, v_name, v_value):
    if 'track_data' in cvpj_l:
        if trackid in cvpj_l['track_data']:
            cvpj_inst = cvpj_l['track_data'][trackid]
            cvpj_inst[v_name] = v_value

# ------------------------ RegularIndexed ------------------------

def ri_create_inst(cvpj_l, trackid, notelistindex, instdata):
    if 'track_data' not in cvpj_l: cvpj_l['track_data'] = {}
    if 'track_order' not in cvpj_l: cvpj_l['track_order'] = []
    cvpj_inst = {}
    cvpj_inst['type'] = 'instrument'
    cvpj_inst['instdata'] = instdata
    if notelistindex != None: cvpj_inst['notelistindex'] = notelistindex
    else: cvpj_inst['notelistindex'] = {}
    cvpj_l['track_data'][trackid] = cvpj_inst
    cvpj_l['track_order'].append(trackid)

def ri_nle_add(cvpj_l, trackid, patid, nle_notelist, nle_name):
    if 'track_data' in cvpj_l:
        if trackid in cvpj_l['track_data']:
            if 'notelistindex' not in cvpj_l['track_data'][trackid]: cvpj_l['track_data'][trackid]['notelistindex'] = {}
            cvpj_l['track_data'][trackid]['notelistindex'][patid] = {}
            cvpj_inst_nle = cvpj_l['track_data'][trackid]['notelistindex'][patid]
            if nle_name != None: cvpj_inst_nle['name'] = nle_name
            cvpj_inst_nle['notelist'] = nle_notelist

# ------------------------ Regular******** ------------------------

def r_pl_notes(cvpj_l, trackid, placements_data):
    if 'track_placements' not in cvpj_l: cvpj_l['track_placements'] = {}
    cvpj_l['track_placements'][trackid] = {}
    if placements_data != None: cvpj_l['track_placements'][trackid]['notes'] = placements_data

def r_pl_audio(cvpj_l, trackid, placements_data):
    if 'track_placements' not in cvpj_l: cvpj_l['track_placements'] = {}
    cvpj_l['track_placements'][trackid] = {}
    if placements_data != None: cvpj_l['track_placements'][trackid]['audio'] = placements_data

def r_pl_laned(cvpj_l, trackid, laneddata):
    if 'track_placements' not in cvpj_l: cvpj_l['track_placements'] = {}
    cvpj_l['track_placements'][trackid] = {}
    if laneddata != None: cvpj_l['track_placements'][trackid] = laneddata

def r_fx_audio(cvpj_l, trackid, chain_fx_audio):
    if chain_fx_audio != None: cvpj_l['track_data'][trackid]['chain_fx_audio'] = chain_fx_audio

def r_fx_notes(cvpj_l, trackid, chain_fx_note):
    if chain_fx_note != None: cvpj_l['track_data'][trackid]['instdata']['chain_fx_notes'] = chain_fx_note

def r_fx_notes_append(cvpj_l, trackid, enabled, pluginname, plugindata):
    if 'chain_fx_note' not in cvpj_l['track_data'][trackid]['instdata']: cvpj_l['track_data'][trackid]['instdata']['chain_fx_notes'] = []
    cvpj_l['track_data'][trackid]['instdata']['chain_fx_notes'].append(
            {"enabled": enabled, "plugin": pluginname, "plugindata": plugindata}
            )















# ------------------------ Multiple ------------------------

def m_create_inst(cvpj_l, trackid, instdata):
    if 'instruments_data' not in cvpj_l: cvpj_l['instruments_data'] = {}
    if 'instruments_order' not in cvpj_l: cvpj_l['instruments_order'] = []
    cvpj_inst = {}
    cvpj_inst['instdata'] = instdata
    cvpj_l['instruments_data'][trackid] = cvpj_inst
    cvpj_l['instruments_order'].append(trackid)

def m_basicdata_inst(cvpj_l, trackid, trk_name, trk_color, trk_vol, trk_pan):
    if 'instruments_data' in cvpj_l:
        if trackid in cvpj_l['instruments_data']:
            cvpj_inst = cvpj_l['instruments_data'][trackid]
            cvpj_inst['name'] = trk_name
            if trk_color != None: cvpj_inst['color'] = trk_color
            if trk_vol != None: cvpj_inst['vol'] = trk_vol
            if trk_pan != None: cvpj_inst['pan'] = trk_pan

def m_param_inst(cvpj_l, trackid, v_name, v_value):
    if 'instruments_data' in cvpj_l:
        if trackid in cvpj_l['instruments_data']:
            cvpj_inst = cvpj_l['instruments_data'][trackid]
            cvpj_inst[v_name] = v_value

# ------------------------ Multiple******** ------------------------

def m_playlist_pl(cvpj_l, idnum, trk_name, trk_color, placements_notes):
    if 'playlist' not in cvpj_l: cvpj_l['playlist'] = {}
    if str(idnum) not in cvpj_l: cvpj_l['playlist'][str(idnum)] = {}
    if placements_notes != None: cvpj_l['playlist'][str(idnum)]['placements_notes'] = placements_notes
    else: cvpj_l['playlist'][str(idnum)]['placements_notes'] = []
    if trk_name != None: cvpj_l['playlist'][str(idnum)]['name'] = trk_name
    if trk_color != None: cvpj_l['playlist'][str(idnum)]['color'] = trk_color

def m_playlist_pl_add(cvpj_l, idnum, placement_data):
    if 'playlist' in cvpj_l:
        if str(idnum) in cvpj_l['playlist']:
            cvpj_l['playlist'][str(idnum)]['placements_notes'].append(placement_data)

def m_add_nle(cvpj_l, patid, nle_notelist, nle_name):
    if 'notelistindex' not in cvpj_l: cvpj_l['notelistindex'] = {}
    cvpj_l['notelistindex'][patid] = {}
    if nle_name != None: cvpj_l['notelistindex'][patid]['name'] = nle_name
    cvpj_l['notelistindex'][patid]['notelist'] = nle_notelist
    
# ------------------------ All ------------------------

def a_addtrack_master(cvpj_l, i_name, i_vol, i_color):
    if 'track_master' not in cvpj_l: cvpj_l['track_master'] = {}
    if i_name != None: cvpj_l['track_master']['name'] = i_name
    if i_vol != None: cvpj_l['track_master']['vol'] = i_vol
    if i_color != None: cvpj_l['track_master']['color'] = i_color

def a_addtrack_master_param(cvpj_l, v_name, v_value):
    cvpj_l['track_master'][v_name] = v_value
