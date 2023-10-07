# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_values
from functions import params
from functions import auto

nopl_autopoints = {}

def addpoint(in_autoloc, val_type, point_pos, point_val, point_type):
    global nopl_autopoints
    pointdata = {"position": point_pos, "value": point_val, "type": point_type}
    data_values.nested_dict_add_value(nopl_autopoints, in_autoloc+['type'], val_type)
    data_values.nested_dict_add_to_list(nopl_autopoints, in_autoloc+['points'], pointdata)

def twopoints(in_autoloc, val_type, twopoints, notelen, point_type):
    cvpj_points = []
    for twopoint in twopoints:
        addpoint(in_autoloc, val_type, twopoint[0]*notelen, twopoint[1], point_type)

def paramauto(in_autoloc, val_type, input_points, ticks, before_note, fallback, divi, add):
    out_param, out_twopoints = auto.points2paramauto(input_points, ticks, before_note, fallback, divi, add)
    if out_twopoints != []: twopoints(in_autoloc, val_type, out_twopoints, 1, 'instant')
    return out_param

def to_pl(pointsdata):
    autopl = {}
    durpos = auto.getdurpos(pointsdata, 0)
    autopl['position'] = durpos[0]
    autopl['duration'] = durpos[1]-durpos[0]+4
    autopl['points'] = auto.trimmove(pointsdata, durpos[0], durpos[0]+durpos[1])
    return autopl

def to_cvpj(cvpj_l):
    global nopl_autopoints
    for in_type in nopl_autopoints:
        if in_type in ['track', 'plugin', 'fxmixer', 'slot', 'send']:
            for in_id in nopl_autopoints[in_type]:
                for in_name in nopl_autopoints[in_type][in_id]:
                    s_autodata = nopl_autopoints[in_type][in_id][in_name]
                    data_values.nested_dict_add_value(cvpj_l, ['automation', in_type, in_id, in_name, 'type'], s_autodata['type'])
                    data_values.nested_dict_add_to_list(cvpj_l, ['automation', in_type, in_id, in_name, 'placements'], to_pl(s_autodata['points']))
        else:
            for in_name in nopl_autopoints[in_type]:
                s_autodata = nopl_autopoints[in_type][in_name]
                data_values.nested_dict_add_value(cvpj_l, ['automation', in_type, in_name, 'type'], s_autodata['type'])
                data_values.nested_dict_add_to_list(cvpj_l, ['automation', in_type, in_name, 'placements'], to_pl(s_autodata['points']))

def getpoints(cvpj_l, in_autoloc):
    out = None
    autopoints = data_values.nested_dict_get_value(cvpj_l, ['automation']+in_autoloc)
    if autopoints != None:
        if 'placements' in autopoints:
            spldat = autopoints['placements']
            if len(spldat) != 0:
                out = spldat[0]['points']
    return out
