# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_values
from functions import xtramath

import json

def convert(convproj_obj):
    print('[song-convert] Converting from RegularMultiple > Regular')

    useable_plugins = convproj_obj.plugins
    convproj_obj.plugins = {}

    used_plugins = []

    convproj_obj.instruments_order = []

    old_track_order = convproj_obj.track_order.copy()

    splitted_trks = {}
    for trackid, track_obj in convproj_obj.iter_track():
        used_insts = track_obj.placements.used_notes()
        splitted_pl = track_obj.placements.inst_split()
        for inst_id, placements in splitted_pl.items():
            if inst_id not in splitted_trks: splitted_trks[inst_id] = []
            if inst_id in convproj_obj.instruments:
                inst_obj = convproj_obj.instruments[inst_id]
                new_track_obj = track_obj.make_base_inst(inst_obj)
                used_plugins.append(new_track_obj.inst_pluginid)

                if new_track_obj.fxrack_channel == -1: 
                    new_track_obj.fxrack_channel = track_obj.fxrack_channel

                if new_track_obj.visual.name and inst_obj.visual.name: new_track_obj.visual.name = inst_obj.visual.name+' ('+new_track_obj.visual.name+')'
                else: new_track_obj.visual.name = inst_obj.visual.name
                if not new_track_obj.visual.color: new_track_obj.visual.color = inst_obj.visual.color
            else:
                new_track_obj = track_obj.make_base()
                new_track_obj.visual.name = inst_id+' ('+new_track_obj.visual.name+')'
            splitted_trks[inst_id].append([trackid, new_track_obj, placements])

    for x in old_track_order:
        convproj_obj.track_order.remove(x)
        del convproj_obj.track_data[x]

    for xc, trackdata in splitted_trks.items():
        for oldtrackid, track_obj, track_pls in trackdata:
            cvpj_trackid = 'rm2r_'+xc+'_'+oldtrackid
            track_obj.type = 'instrument'
            track_obj.placements.data_notes = track_pls
            convproj_obj.track_data[cvpj_trackid] = track_obj
            convproj_obj.track_order.append(cvpj_trackid)

    for num, fxchannel_obj in convproj_obj.fxrack.items():
        used_plugins += fxchannel_obj.fxslots_audio

    used_plugins = set(used_plugins)
    if '' in used_plugins: used_plugins.remove('')

    for plugid in set(used_plugins):
        convproj_obj.plugins[plugid] = useable_plugins[plugid]

    convproj_obj.instruments = {}
    convproj_obj.type = 'r'
