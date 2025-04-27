# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import logging

logger_project = logging.getLogger('project')

def convert(convproj_obj):
    logger_project.info('ProjType Convert: RegularIndexed > Regular')

    for trackid, track_obj in convproj_obj.track__iter():
        if not track_obj.is_laned: 
            track_obj.placements.unindex_notes(track_obj.notelist_index)
        else:
            for lane_id, lane_obj in track_obj.lanes.items():
                lane_obj.placements.unindex_notes(track_obj.notelist_index)
                
    convproj_obj.type = 'r'