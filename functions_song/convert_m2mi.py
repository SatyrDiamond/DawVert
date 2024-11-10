# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import logging
logger_project = logging.getLogger('project')

def convert(convproj_obj):
    logger_project.info('ProjType Convert: Multiple > MultipleIndexed')

    existingpatterns = []
    pn = 1
    for pl_id, playlist_obj in convproj_obj.playlist__iter():
        x, pn = playlist_obj.placements.to_indexed_notes(existingpatterns, pn)

        for patid, nle_data in x:
            nle_obj = convproj_obj.notelistindex__add(patid)
            nle_obj.notelist = nle_data[0]
            nle_obj.visual.name = nle_data[1]
            nle_obj.visual.color = nle_data[2]

    existingsamples = []
    pn = 1
    for pl_id, playlist_obj in convproj_obj.playlist__iter():
        x, pn = playlist_obj.placements.to_indexed_audio(existingsamples, pn)
        for patid, sle_data in x: 
            convproj_obj.sample_index[patid] = sle_data

    convproj_obj.type = 'mi'