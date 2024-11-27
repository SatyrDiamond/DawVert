# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

def process(convproj_obj, in_compat, out_compat, out_type, dawvert_intent):

    convproj_obj.automation.convert(
        'pl_points' in out_compat, 
        'nopl_points' in out_compat, 
        'pl_ticks' in out_compat, 
        'nopl_ticks' in out_compat
        )
    return True