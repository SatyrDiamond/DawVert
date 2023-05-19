# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_values
from functions import auto

# ------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------- Regular -----------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------

def r_create_copy(cvpj_l, trackid, trackdata):
    cvpj_l['track_data'][trackid] = trackdata
    cvpj_l['track_order'].append(trackid)

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
    data_values.nested_dict_add_value(cvpj_l, ['track_data', trackid, 'notelistindex', patid], {})
    cvpj_inst_nle = cvpj_l['track_data'][trackid]['notelistindex'][patid]
    if nle_name != None: cvpj_inst_nle['name'] = nle_name
    cvpj_inst_nle['notelist'] = nle_notelist

# ------------------------ Regular******** ------------------------

def r_pl_notes(cvpj_l, trackid, placements_data):
    data_values.nested_dict_add_to_list(cvpj_l, ['track_placements', trackid, 'notes'], placements_data)

def r_pl_audio(cvpj_l, trackid, placements_data):
    data_values.nested_dict_add_to_list(cvpj_l, ['track_placements', trackid, 'audio'], placements_data)

def r_pl_notes_laned(cvpj_l, trackid, lanename, placements_data):
    data_values.nested_dict_add_value(cvpj_l, ['track_placements', trackid, 'laned'], 1)
    data_values.nested_dict_add_to_list(cvpj_l, ['track_placements', trackid, 'lanedata', lanename, 'notes'], placements_data)
    data_values.nested_dict_add_to_list(cvpj_l, ['track_placements', trackid, 'laneorder'], lanename)

def r_pl_audio_laned(cvpj_l, trackid, lanename, placements_data):
    data_values.nested_dict_add_value(cvpj_l, ['track_placements', trackid, 'laned'], 1)
    data_values.nested_dict_add_to_list(cvpj_l, ['track_placements', trackid, 'lanedata', lanename, 'audio'], placements_data)
    data_values.nested_dict_add_to_list(cvpj_l, ['track_placements', trackid, 'laneorder'], lanename)

def r_pl_laned(cvpj_l, trackid, laneddata):
    if 'track_placements' not in cvpj_l: cvpj_l['track_placements'] = {}
    cvpj_l['track_placements'][trackid] = {}
    if laneddata != None: cvpj_l['track_placements'][trackid] = laneddata



# ------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------- Multiple -----------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------

def m_create_inst(cvpj_l, trackid, instdata):
    if 'instruments_data' not in cvpj_l: cvpj_l['instruments_data'] = {}
    if 'instruments_order' not in cvpj_l: cvpj_l['instruments_order'] = []
    cvpj_inst = {}
    cvpj_inst['instdata'] = instdata
    cvpj_l['instruments_data'][trackid] = cvpj_inst
    if trackid not in cvpj_l['instruments_order']: cvpj_l['instruments_order'].append(trackid)

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

def m_param_instdata(cvpj_l, trackid, v_name, v_value):
    if 'instruments_data' in cvpj_l:
        if trackid in cvpj_l['instruments_data']:
            if 'instdata' not in cvpj_l['instruments_data'][trackid]: cvpj_l['instruments_data'][trackid]['instdata'] = {}
            cvpj_inst = cvpj_l['instruments_data'][trackid]['instdata']
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
    data_values.nested_dict_add_to_list(cvpj_l, ['playlist', str(idnum), 'placements_notes'], placement_data)

def m_add_nle(cvpj_l, patid, nle_notelist):
    if 'notelistindex' not in cvpj_l: cvpj_l['notelistindex'] = {}
    cvpj_l['notelistindex'][patid] = {}
    cvpj_l['notelistindex'][patid]['notelist'] = nle_notelist
    
def m_add_nle_info(cvpj_l, patid, nle_name, nle_color):
    if nle_name != None: cvpj_l['notelistindex'][patid]['name'] = nle_name
    if nle_color != None: cvpj_l['notelistindex'][patid]['color'] = nle_color

# ------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------ All -------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------

def a_addtrack_master(cvpj_l, i_name, i_vol, i_color):
    if 'track_master' not in cvpj_l: cvpj_l['track_master'] = {}
    if i_name != None: cvpj_l['track_master']['name'] = i_name
    if i_vol != None: cvpj_l['track_master']['vol'] = i_vol
    if i_color != None: cvpj_l['track_master']['color'] = i_color

def a_addtrack_master_param(cvpj_l, v_name, v_value):
    cvpj_l['track_master'][v_name] = v_value

# ------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------- FXRack -----------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------

def fxrack_add(cvpj_l, fx_num, fx_name, fx_color, fx_vol, fx_pan):
    data_values.nested_dict_add_value(cvpj_l, ['fxrack', str(fx_num)], {})
    fxdata = cvpj_l['fxrack'][str(fx_num)]
    if fx_color != None: fxdata['color'] = fx_color
    if fx_name != None: fxdata['name'] = fx_name

def fxrack_param(cvpj_l, fx_num, v_name, v_value):
    data_values.nested_dict_add_value(cvpj_l, ['fxrack', str(fx_num)], {})
    cvpj_l['fxrack'][str(fx_num)][v_name] = v_value

def fxrack_addsend(cvpj_l, fx_num, fx_to_num, fx_amount, fx_sendautoid):
    senddata = {"amount": fx_amount, "channel": fx_to_num}
    if fx_sendautoid != None: senddata['sendautoid'] = fx_sendautoid
    data_values.nested_dict_add_to_list(cvpj_l, ['fxrack', str(fx_num), 'sends'], senddata)

# ------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------- Groups --------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------

def group_add(cvpj_l, i_id, i_inside_group):
    data_values.nested_dict_add_value(cvpj_l, ['groups', i_id], {})
    if i_inside_group != None: 
        data_values.nested_dict_add_value(cvpj_l, ['groups', i_id, 'parent_group'], i_inside_group)
        data_values.nested_dict_add_value(cvpj_l, ['groups', i_id, 'audio_destination'], {'type': 'group', 'id': i_inside_group})
    else:
        data_values.nested_dict_add_value(cvpj_l, ['groups', i_id, 'audio_destination'], {'type': 'master'})

def group_basicdata(cvpj_l, i_id, i_name, i_vol, i_color):
    if i_name != None: data_values.nested_dict_add_value(cvpj_l, ['groups', i_id, 'name'], i_name)
    if i_vol != None: data_values.nested_dict_add_value(cvpj_l, ['groups', i_id, 'vol'], i_vol)
    if i_color != None: data_values.nested_dict_add_value(cvpj_l, ['groups', i_id, 'color'], i_color)

# ------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------- Sends --------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------

def get_sendcvpjlocation(sendloc):
    out_location = None
    if sendloc[0] == 'master': out_location = ['track_master', 'sends_audio']
    if sendloc[0] == 'group': out_location = ['groups', sendloc[1], 'sends_audio']
    return out_location

def r_add_return(cvpj_l, i_location, i_sendname):
    out_location = get_sendcvpjlocation(i_location)
    data_values.nested_dict_add_value(cvpj_l, out_location+[i_sendname], {})

def r_add_return_basicdata(cvpj_l, i_location, i_sendname, trk_name, trk_color, trk_vol, trk_pan):
    out_location = get_sendcvpjlocation(i_location)
    if trk_name != None: data_values.nested_dict_add_value(cvpj_l, out_location+[i_sendname, 'name'], trk_name)
    if trk_color != None: data_values.nested_dict_add_value(cvpj_l, out_location+[i_sendname, 'color'], trk_color)
    if trk_vol != None: data_values.nested_dict_add_value(cvpj_l, out_location+[i_sendname, 'vol'], trk_vol)
    if trk_pan != None: data_values.nested_dict_add_value(cvpj_l, out_location+[i_sendname, 'pan'], trk_pan)

def r_add_send(cvpj_l, i_trackid, i_sendname, i_amount, i_sendautoid):
    send_data = {'amount': i_amount, 'sendid': i_sendname}
    if i_sendautoid != None: send_data['sendautoid'] = i_sendautoid
    data_values.nested_dict_add_to_list(cvpj_l, ['track_data', i_trackid, 'sends_audio'], send_data)

# ------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------ FX ------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------

def get_fxcvpjlocation(fxloc):
    out_location = None
    if fxloc[0] == 'track': out_location = ['track_data', fxloc[1]]
    if fxloc[0] == 'instrument': out_location = ['instruments_data', fxloc[1]]
    if fxloc[0] == 'master': out_location = ['track_master']
    if fxloc[0] == 'fxrack': out_location = ['fxrack', str(fxloc[1])]
    if fxloc[0] == 'group': out_location = ['groups', fxloc[1]]
    if fxloc[0] == 'send': 
        if fxloc[1] == None: out_location = ['track_master', 'sends_audio', fxloc[2]]
        else: out_location = ['groups', fxloc[1], 'sends_audio', fxloc[2]]
    return out_location

def add_fxslot(cvpj_l, fxloc, fxtype, chain_fx_data):
    out_location = get_fxcvpjlocation(fxloc)
    if fxtype == 'audio': data_values.nested_dict_add_to_list(cvpj_l, out_location+['chain_fx_audio'], chain_fx_data)
    if fxtype == 'notes': data_values.nested_dict_add_to_list(cvpj_l, out_location+['chain_fx_notes'], chain_fx_data)

def add_fxslot_basic(cvpj_l, fxloc, fxtype, enabled, wet, auto_plug, auto_slot, pluginname, plugindata):
    fxslot_data = {"plugin": pluginname, "plugindata": plugindata}
    if auto_plug != None: fxslot_data['pluginautoid'] = auto_plug
    if auto_slot != None: fxslot_data['slotautoid'] = auto_slot
    if enabled != None: fxslot_data['enabled'] = enabled
    if wet != None: fxslot_data['wet'] = wet
    add_fxslot(cvpj_l, fxloc, fxtype, fxslot_data)

def add_fxslot_native(cvpj_l, fxtype, nativedawname, fxloc, enabled, wet, auto_id, fx_name, fx_data):
    plugindata = {}
    plugindata['name'] = fx_name
    plugindata['data'] = fx_data
    add_fxslot_basic(cvpj_l, fxloc, fxtype, enabled, wet, auto_id, auto_id, 'native-'+nativedawname, plugindata)

# ------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------ Auto ------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------



# ------------------------ Auto ------------------------

def a_add_auto_pl(cvpj_l, autolocation, in_autopoints):
    data_values.nested_dict_add_to_list(cvpj_l, ['automation']+autolocation, in_autopoints)

# ------------------------ NoPl Auto ------------------------

nopl_autopoints = {}

def a_auto_nopl_addpoint(in_type, in_id, in_name, point_pos, point_val, point_type):
    global nopl_autopoints
    pointdata = {"position": point_pos, "value": point_val, "type": point_type}
    if in_type in ['track', 'plugin', 'fxmixer', 'slot', 'send']:
        data_values.nested_dict_add_to_list(nopl_autopoints, [in_type, in_id, in_name], pointdata)
    else: 
        data_values.nested_dict_add_to_list(nopl_autopoints, [in_type, in_name], pointdata)

def a_auto_nopl_twopoints(in_type, in_id, in_name, twopoints, notelen, pointtype):
    cvpj_points = []
    for twopoint in twopoints:
        a_auto_nopl_addpoint(in_type, in_id, in_name, twopoint[0]*notelen, twopoint[1], pointtype)

def a_auto_nopl_to_pl(pointsdata):
    autopl = {}
    durpos = auto.getdurpos(pointsdata, 0)
    autopl['position'] = durpos[0]
    autopl['duration'] = durpos[1]-durpos[0]+4
    autopl['points'] = auto.trimmove(pointsdata, durpos[0], durpos[0]+durpos[1])
    return autopl

def a_auto_nopl_to_cvpj(cvpj_l):
    global nopl_autopoints
    for in_type in nopl_autopoints:
        if in_type in ['track', 'plugin', 'fxmixer', 'slot', 'send']:
            for in_id in nopl_autopoints[in_type]:
                for in_name in nopl_autopoints[in_type][in_id]:
                    #print(in_type, in_id, in_name, nopl_autopoints[in_type][in_id][in_name])
                    data_values.nested_dict_add_to_list(cvpj_l, ['automation', in_type, in_id, in_name], a_auto_nopl_to_pl(nopl_autopoints[in_type][in_id][in_name]))
        else:
            for in_name in nopl_autopoints[in_type]:
                #print(in_type, in_name, nopl_autopoints[in_type][in_name])
                data_values.nested_dict_add_to_list(cvpj_l, ['automation', in_type, in_name], a_auto_nopl_to_pl(nopl_autopoints[in_type][in_name]))