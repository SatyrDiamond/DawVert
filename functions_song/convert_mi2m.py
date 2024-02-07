# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json

def convert(convproj_obj, extra_json):
    nle_list = [x for x in convproj_obj.notelist_index]
    unused_nle = []

    for pl_id, playlist_obj in convproj_obj.iter_playlist():
        unused_nle += [x.fromindex for x in playlist_obj.placements.data_notes]
        playlist_obj.placements.unindex_notes(convproj_obj.notelist_index)
        playlist_obj.placements.unindex_audio(convproj_obj.sample_index)

    unused_nle = list(set(unused_nle))

    #mi2m-output-unused-nle 
    for x in nle_list:
        if x in unused_nle: unused_nle.remove(x)

    convproj_obj.notelist_index = {}
    convproj_obj.sample_index = {}

    convproj_obj.type = 'm'