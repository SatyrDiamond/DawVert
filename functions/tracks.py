# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_values
from functions import auto
from functions import params

# ------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------- Regular -----------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------

def r_create_track(cvpj_l, tracktype, trackid, **kwargs):
    if 'track_data' not in cvpj_l: cvpj_l['track_data'] = {}
    if 'track_order' not in cvpj_l: cvpj_l['track_order'] = []
    cvpj_track = {}
    cvpj_track['type'] = tracktype
    if 'name' in kwargs: 
        if kwargs['name'] != None: cvpj_track['name'] = kwargs['name']
    if 'color' in kwargs: 
        if kwargs['color'] != None: cvpj_track['color'] = kwargs['color']
    cvpj_l['track_data'][trackid] = cvpj_track
    cvpj_l['track_order'].append(trackid)

def r_track_pluginid(cvpj_l, trackid, pluginid):
    data_values.nested_dict_add_value(cvpj_l, ['track_data', trackid, 'instdata', 'pluginid'], pluginid)

def r_add_param(cvpj_l, trackid, p_id, p_value, p_type, **kwargs):
    if p_value != None: params.add(cvpj_l, ['track_data', trackid], p_id, p_value, p_type, **kwargs)

def r_get_param(cvpj_l, trackid, paramname, fallbackval):
    return params.get(cvpj_l, ['track_data', trackid], paramname, fallbackval)

def r_add_dataval(cvpj_l, trackid, datagroup, i_name, i_value):
    if datagroup != None:
        data_values.nested_dict_add_value(cvpj_l, ['track_data', trackid, datagroup, i_name], i_value)
    else:
        data_values.nested_dict_add_value(cvpj_l, ['track_data', trackid, i_name], i_value)

# ------------------------ RegularIndexed ------------------------

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

def r_track_iter(cvpj_l):
    cvpj_track_placements = cvpj_l['track_placements'] if 'track_placements' in cvpj_l else {}
    cvpj_track_order = cvpj_l['track_order'] if 'track_order' in cvpj_l else []
    cvpj_track_data = cvpj_l['track_data'] if 'track_data' in cvpj_l else {}
    for trackid in cvpj_track_order:
        track_placements = cvpj_track_placements[trackid] if trackid in cvpj_track_placements else {}
        track_data = cvpj_track_data[trackid] if trackid in cvpj_track_data else {}
        yield trackid, track_data, track_placements

# ------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------- Multiple -----------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------


def m_inst_create(cvpj_l, trackid, **kwargs):
    if 'instruments_data' not in cvpj_l: cvpj_l['instruments_data'] = {}
    if 'instruments_order' not in cvpj_l: cvpj_l['instruments_order'] = []
    cvpj_inst = {}
    if 'name' in kwargs: 
        if kwargs['name'] != None: cvpj_inst['name'] = kwargs['name']
    if 'color' in kwargs: 
        if kwargs['color'] != None: cvpj_inst['color'] = kwargs['color']
    cvpj_l['instruments_data'][trackid] = cvpj_inst
    if trackid not in cvpj_l['instruments_order']: cvpj_l['instruments_order'].append(trackid)

def m_inst_pluginid(cvpj_l, trackid, pluginid):
    data_values.nested_dict_add_value(cvpj_l, ['instruments_data', trackid, 'instdata', 'pluginid'], pluginid)

def m_inst_add_param(cvpj_l, trackid, p_id, p_value, p_type, **kwargs):
    params.add(cvpj_l, ['instruments_data', trackid], p_id, p_value, p_type, **kwargs)

def m_inst_get_param(cvpj_l, trackid, paramname, fallbackval):
    return params.get(cvpj_l, ['instruments_data', trackid], paramname, fallbackval)

def m_inst_add_dataval(cvpj_l, trackid, datagroup, i_name, i_value):
    if datagroup != None:
        data_values.nested_dict_add_value(cvpj_l, ['instruments_data', trackid, datagroup, i_name], i_value)
    else:
        data_values.nested_dict_add_value(cvpj_l, ['instruments_data', trackid, i_name], i_value)

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
# ---------------------------------------------------------------- Cloned ------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------

def c_inst_create(cvpj_l, trackid, **kwargs):
    if 'instruments_data' not in cvpj_l: cvpj_l['instruments_data'] = {}
    cvpj_inst = {}
    if 'name' in kwargs: 
        if kwargs['name'] != None: cvpj_inst['name'] = kwargs['name']
    if 'color' in kwargs: 
        if kwargs['color'] != None: cvpj_inst['color'] = kwargs['color']
    cvpj_l['instruments_data'][trackid] = cvpj_inst

def c_create_track(cvpj_l, tracktype, trackid, **kwargs):
    if 'track_data' not in cvpj_l: cvpj_l['track_data'] = {}
    if 'track_order' not in cvpj_l: cvpj_l['track_order'] = []
    cvpj_track = {}
    cvpj_track['type'] = tracktype
    if 'name' in kwargs: 
        if kwargs['name'] != None: cvpj_track['name'] = kwargs['name']
    if 'color' in kwargs: 
        if kwargs['color'] != None: cvpj_track['color'] = kwargs['color']
    cvpj_l['track_data'][trackid] = cvpj_track
    cvpj_l['track_order'].append(trackid)

def c_add_dataval(cvpj_l, trackid, datagroup, i_name, i_value):
    if datagroup != None:
        data_values.nested_dict_add_value(cvpj_l, ['track_data', trackid, datagroup, i_name], i_value)
    else:
        data_values.nested_dict_add_value(cvpj_l, ['track_data', trackid, i_name], i_value)

def c_inst_pluginid(cvpj_l, trackid, pluginid):
    data_values.nested_dict_add_value(cvpj_l, ['instruments_data', trackid, 'instdata', 'pluginid'], pluginid)

def c_inst_add_param(cvpj_l, trackid, p_id, p_value, p_type, **kwargs):
    params.add(cvpj_l, ['instruments_data', trackid], p_id, p_value, p_type, **kwargs)

def c_inst_get_param(cvpj_l, trackid, paramname, fallbackval):
    return params.get(cvpj_l, ['instruments_data', trackid], paramname, fallbackval)

def c_inst_add_dataval(cvpj_l, trackid, datagroup, i_name, i_value):
    if datagroup != None:
        data_values.nested_dict_add_value(cvpj_l, ['instruments_data', trackid, datagroup, i_name], i_value)
    else:
        data_values.nested_dict_add_value(cvpj_l, ['instruments_data', trackid, i_name], i_value)

def c_pl_notes(cvpj_l, trackid, placements_data):
    data_values.nested_dict_add_to_list(cvpj_l, ['track_placements', trackid, 'notes'], placements_data)

def c_pl_audio(cvpj_l, trackid, placements_data):
    data_values.nested_dict_add_to_list(cvpj_l, ['track_placements', trackid, 'audio'], placements_data)

# ------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------ All -------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------

def a_addtrack_master(cvpj_l, i_name, i_vol, i_color):
    if 'track_master' not in cvpj_l: cvpj_l['track_master'] = {}
    cvpj_master = cvpj_l['track_master']
    if i_name != None: cvpj_master['name'] = i_name
    if i_vol != None: params.add(cvpj_l, ['track_master'], 'vol', i_vol, 'float')
    if i_color != None: cvpj_master['color'] = i_color

def a_addtrack_master_param(cvpj_l, p_id, p_value, p_type):
    params.add(cvpj_l, ['track_master'], p_id, p_value, p_type)

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
    if fx_vol != None: params.add(fxdata, [], 'vol', fx_vol, 'float')
    if fx_pan != None: params.add(fxdata, [], 'pan', fx_pan, 'float')

def fxrack_param(cvpj_l, fx_num, v_name, v_value, v_type):
    data_values.nested_dict_add_value(cvpj_l, ['fxrack', str(fx_num)], {})
    params.add(cvpj_l, ['fxrack',str(fx_num)], v_name, v_value, v_type)

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
        print('[tracks] Adding Group: "'+i_id+'" inside "'+i_inside_group+'"')
        data_values.nested_dict_add_value(cvpj_l, ['groups', i_id, 'parent_group'], i_inside_group)
        data_values.nested_dict_add_value(cvpj_l, ['groups', i_id, 'audio_destination'], {'type': 'group', 'id': i_inside_group})
    else:
        print('[tracks] Adding Group: "'+i_id+'"')
        data_values.nested_dict_add_value(cvpj_l, ['groups', i_id, 'audio_destination'], {'type': 'master'})

def group_basicdata(cvpj_l, i_id, i_name, i_color, i_vol, i_pan):
    if i_name != None: data_values.nested_dict_add_value(cvpj_l, ['groups', i_id, 'name'], i_name)
    if i_color != None: data_values.nested_dict_add_value(cvpj_l, ['groups', i_id, 'color'], i_color)
    if i_vol != None: params.add(cvpj_l, ['groups', i_id], 'vol', i_vol, 'float')
    if i_pan != None: params.add(cvpj_l, ['groups', i_id], 'pan', i_pan, 'float')

# ------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------- Sends --------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------

def get_sendcvpjlocation(sendloc):
    out_location = None
    if sendloc[0] == 'master': out_location = ['track_master', 'returns']
    if sendloc[0] == 'group': out_location = ['groups', sendloc[1], 'returns']
    return out_location

def r_add_return(cvpj_l, i_location, i_returnname):
    out_location = get_sendcvpjlocation(i_location)
    print('[tracks] Adding Return: "'+i_returnname+'" in '+'/'.join(out_location))
    data_values.nested_dict_add_value(cvpj_l, out_location+[i_returnname], {})

def r_add_return_basicdata(cvpj_l, i_location, i_sendname, trk_name, trk_color, trk_vol, trk_pan):
    out_location = get_sendcvpjlocation(i_location)
    if trk_name != None: data_values.nested_dict_add_value(cvpj_l, out_location+[i_sendname, 'name'], trk_name)
    if trk_color != None: data_values.nested_dict_add_value(cvpj_l, out_location+[i_sendname, 'color'], trk_color)
    if trk_vol != None: params.add(cvpj_l, out_location+[i_sendname], 'vol', trk_vol, 'float')
    if trk_pan != None: params.add(cvpj_l, out_location+[i_sendname], 'pan', trk_pan, 'float')

def r_add_send(cvpj_l, i_trackid, i_sendname, i_amount, i_sendautoid):
    send_data = {'amount': i_amount, 'sendid': i_sendname}
    if i_sendautoid != None: send_data['sendautoid'] = i_sendautoid
    print('[tracks] Adding Send: "'+i_sendname+'"')
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
    if fxloc[0] == 'return': 
        if fxloc[1] == None: out_location = ['track_master', 'returns', fxloc[2]]
        else: out_location = ['groups', fxloc[1], 'returns', fxloc[2]]
    return out_location

def insert_fxslot(cvpj_l, fxloc, fxtype, pluginid):
    out_location = get_fxcvpjlocation(fxloc)
    if fxtype == 'audio': 
        data_values.nested_dict_add_to_list(cvpj_l, out_location+['chain_fx_audio'], pluginid)
    if fxtype == 'notes': 
        data_values.nested_dict_add_to_list(cvpj_l, out_location+['chain_fx_notes'], pluginid)

#def add_fxslot(cvpj_l, fxloc, fxtype, chain_fx_data):
#    out_location = get_fxcvpjlocation(fxloc)
#    if fxtype == 'audio': data_values.nested_dict_add_to_list(cvpj_l, out_location+['chain_fx_audio'], chain_fx_data)
#    if fxtype == 'notes': data_values.nested_dict_add_to_list(cvpj_l, out_location+['chain_fx_notes'], chain_fx_data)

#def add_fxslot_basic(cvpj_l, fxloc, fxtype, enabled, wet, auto_plug, auto_slot, pluginname, plugindata):
#    fxslot_data = {"plugin": pluginname, "plugindata": plugindata}
#    if auto_plug != None: fxslot_data['pluginautoid'] = auto_plug
#    if auto_slot != None: fxslot_data['slotautoid'] = auto_slot
#    if enabled != None: fxslot_data['enabled'] = enabled
#    if wet != None: fxslot_data['wet'] = wet
#    add_fxslot(cvpj_l, fxloc, fxtype, fxslot_data)

#def add_fxslot_native(cvpj_l, fxtype, nativedawname, fxloc, enabled, wet, auto_id, fx_name, fx_data):
#    plugindata = {}
#    plugindata['name'] = fx_name
#    plugindata['data'] = fx_data
#    add_fxslot_basic(cvpj_l, fxloc, fxtype, enabled, wet, auto_id, auto_id, 'native-'+nativedawname, plugindata)

# ------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------ Auto ------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------



# ------------------------ Auto ------------------------

def a_add_auto_pl(cvpj_l, val_type, autolocation, in_autopoints):
    if autolocation != None:
        data_values.nested_dict_add_value(cvpj_l, ['automation']+autolocation+['type'], val_type)
        data_values.nested_dict_add_to_list(cvpj_l, ['automation']+autolocation+['placements'], in_autopoints)

def a_auto_iter(cvpj_l):
    outdata = []
    if 'automation' in cvpj_l:
        cvpj_auto = cvpj_l['automation']
        for autotype in cvpj_auto:
            if autotype in ['main', 'master']:
                for autovarname in cvpj_auto[autotype]:
                    outdata.append([False, [autotype, autovarname], cvpj_auto[autotype][autovarname]])
            else:
                for autonameid in cvpj_auto[autotype]:
                    for autovarname in cvpj_auto[autotype][autonameid]:
                        outdata.append([True, [autotype, autonameid, autovarname], cvpj_auto[autotype][autonameid][autovarname]])
    return outdata

def a_move_auto(cvpj_l, old_autolocation, new_autolocation):
    print('[tracks] Moving Automation:','/'.join(old_autolocation),'to','/'.join(new_autolocation))
    dictvals = data_values.nested_dict_get_value(cvpj_l, ['automation']+old_autolocation)
    if dictvals != None:
        data_values.nested_dict_add_value(cvpj_l, ['automation']+new_autolocation, dictvals)
        if old_autolocation[0] in ['main', 'master']:
            del cvpj_l['automation'][old_autolocation[0]][old_autolocation[1]]
        else:
            del cvpj_l['automation'][old_autolocation[0]][old_autolocation[1]][old_autolocation[2]]

def a_del_auto_plugin(cvpj_l, pluginid):
    print('[tracks] Removing Plugin Automation:',pluginid)
    dictvals = data_values.nested_dict_get_value(cvpj_l, ['automation', 'plugin', pluginid])
    if dictvals != None: del cvpj_l['automation', 'plugin', pluginid]

# ------------------------ NoPl Auto ------------------------

nopl_autopoints = {}

def a_auto_nopl_addpoint(in_autoloc, val_type, point_pos, point_val, point_type):
    global nopl_autopoints
    pointdata = {"position": point_pos, "value": point_val, "type": point_type}
    data_values.nested_dict_add_value(nopl_autopoints, in_autoloc+['type'], val_type)
    data_values.nested_dict_add_to_list(nopl_autopoints, in_autoloc+['points'], pointdata)

def a_auto_nopl_twopoints(in_autoloc, val_type, twopoints, notelen, point_type):
    cvpj_points = []
    for twopoint in twopoints:
        a_auto_nopl_addpoint(in_autoloc, val_type, twopoint[0]*notelen, twopoint[1], point_type)

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
                    s_autodata = nopl_autopoints[in_type][in_id][in_name]
                    data_values.nested_dict_add_value(cvpj_l, ['automation', in_type, in_id, in_name, 'type'], s_autodata['type'])
                    data_values.nested_dict_add_to_list(cvpj_l, ['automation', in_type, in_id, in_name, 'placements'], a_auto_nopl_to_pl(s_autodata['points']))
        else:
            for in_name in nopl_autopoints[in_type]:
                s_autodata = nopl_autopoints[in_type][in_name]
                data_values.nested_dict_add_value(cvpj_l, ['automation', in_type, in_name, 'type'], s_autodata['type'])
                data_values.nested_dict_add_to_list(cvpj_l, ['automation', in_type, in_name, 'placements'], a_auto_nopl_to_pl(s_autodata['points']))

def a_auto_nopl_getpoints(cvpj_l, in_autoloc):
    out = None
    autopoints = data_values.nested_dict_get_value(cvpj_l, ['automation']+in_autoloc)
    if autopoints != None:
        if 'placements' in autopoints:
            spldat = autopoints['placements']
            if len(spldat) != 0:
                out = spldat[0]['points']
    return out



# ------------------------ autoid to cvpjauto ------------------------

autoid_in_data = {}

def autoid_in_define(i_id, i_loc, i_type, i_addmul):
    #print('autoid_in_define', i_id, i_loc, i_type, i_addmul)
    if i_id not in autoid_in_data: 
        autoid_in_data[i_id] = [i_loc, i_type, i_addmul, []]
    else:
        autoid_in_data[i_id][0] = i_loc
        autoid_in_data[i_id][1] = i_type
        autoid_in_data[i_id][2] = i_addmul

def autoid_in_add_pl(i_id, i_autopl):
    #print('autoid_in_add_pl', i_id, len(i_autopl))
    if i_id not in autoid_in_data: autoid_in_data[i_id] = [None, None, None, []]
    autoid_in_data[i_id][3].append(i_autopl)

def autoid_in_output(cvpj_l):
    for i_id in autoid_in_data:
        out_auto_loc = autoid_in_data[i_id][0]
        out_auto_type = autoid_in_data[i_id][1]
        out_auto_addmul = autoid_in_data[i_id][2]
        out_auto_data = autoid_in_data[i_id][3]
        #print(i_id, autoid_in_data[i_id][0:3], out_auto_data)
        if autoid_in_data[i_id][0:4] != [None, None, None] and out_auto_data != []:
            if out_auto_addmul != None: out_auto_data = auto.multiply(out_auto_data, out_auto_addmul[0], out_auto_addmul[1])
            a_add_auto_pl(cvpj_l, out_auto_type, out_auto_loc, out_auto_data)

# ------------------------ cvpjauto to autoid ------------------------

autoid_out_num = 340000
autoid_out_ids = {}
autoid_out_data = {}

def autoid_out_getlist(i_id):
    global autoid_out_num
    global autoid_out_data
    dictvals = data_values.nested_dict_get_value(autoid_out_ids, i_id)
    return dictvals

def autoid_out_get(i_id):
    global autoid_out_num
    global autoid_out_data
    idvalue = data_values.nested_dict_get_value(autoid_out_ids, i_id)

    if idvalue != None and idvalue in autoid_out_data: 
        output = idvalue, autoid_out_data[idvalue]
        del autoid_out_data[idvalue]
        return output
    else: return None, None

def autoid_out_load(cvpj_l):
    global autoid_out_num
    global autoid_out_data

    for autopart in a_auto_iter(cvpj_l):
        data_values.nested_dict_add_value(autoid_out_ids, autopart[1], autoid_out_num)
        autoid_out_data[autoid_out_num] = autopart[2]
        autoid_out_num += 1