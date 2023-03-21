# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

# ------------------------ Regular ------------------------

def r_addtrack_inst(cvpj_l, idval, instdata):
    if 'track_data' not in cvpj_l: cvpj_l['track_data'] = {}
    if 'track_order' not in cvpj_l: cvpj_l['track_order'] = []
    cvpj_inst = {}
    cvpj_inst['type'] = 'instrument'
    cvpj_inst['instdata'] = instdata
    cvpj_l['track_data'][idval] = cvpj_inst
    cvpj_l['track_order'].append(idval)

def r_addtrackpl(cvpj_l, idval, placements_data):
    if 'track_placements' not in cvpj_l: cvpj_l['track_placements'] = {}
    cvpj_l['track_placements'][idval] = {}
    cvpj_l['track_placements'][idval]['notes'] = placements_data

def r_addtrack_data(cvpj_l, idval, trk_name, trk_color, trk_vol, trk_pan):
    if 'track_data' in cvpj_l:
        if idval in cvpj_l['track_data']:
            cvpj_inst = cvpj_l['track_data'][idval]
            cvpj_inst['name'] = trk_name
            if trk_color != None: cvpj_inst['color'] = trk_color
            if trk_vol != None: cvpj_inst['vol'] = trk_vol
            if trk_pan != None: cvpj_inst['pan'] = trk_pan

# ------------------------ RegularIndexed ------------------------

def ri_addtrack_inst(cvpj_l, idval, notelistindex, instdata):
    if 'track_data' not in cvpj_l: cvpj_l['track_data'] = {}
    if 'track_order' not in cvpj_l: cvpj_l['track_order'] = []
    cvpj_inst = {}
    cvpj_inst['type'] = 'instrument'
    cvpj_inst['instdata'] = instdata
    cvpj_inst['notelistindex'] = notelistindex
    cvpj_l['track_data'][idval] = cvpj_inst
    cvpj_l['track_order'].append(idval)

# ------------------------ Multiple ------------------------

def m_addinst(cvpj_l, idval, instdata):
    if 'instruments_data' not in cvpj_l: cvpj_l['instruments_data'] = {}
    if 'instruments_order' not in cvpj_l: cvpj_l['instruments_order'] = []
    cvpj_inst = {}
    cvpj_inst['instdata'] = instdata
    cvpj_l['instruments_data'][idval] = cvpj_inst
    cvpj_l['instruments_order'].append(idval)

def m_addinst_data(cvpj_l, idval, trk_name, trk_color, trk_vol, trk_pan):
    if 'instruments_data' in cvpj_l:
        if idval in cvpj_l['instruments_data']:
            cvpj_inst = cvpj_l['instruments_data'][idval]
            cvpj_inst['name'] = trk_name
            if trk_color != None: cvpj_inst['color'] = trk_color
            if trk_vol != None: cvpj_inst['vol'] = trk_vol
            if trk_pan != None: cvpj_inst['pan'] = trk_pan

def m_addinst_param(cvpj_l, idval, v_name, v_value):
    if 'instruments_data' in cvpj_l:
        if idval in cvpj_l['instruments_data']:
            cvpj_inst = cvpj_l['instruments_data'][idval]
            cvpj_inst[v_name] = v_value

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