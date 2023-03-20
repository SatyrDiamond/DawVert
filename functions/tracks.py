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

