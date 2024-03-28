# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

def cutloopdata(start, loopstart, loopend):
    cut_data = {}
    if start == 0 and loopstart == 0:
        cut_type = 'loop'
        cut_data['loopend'] = loopend
    elif loopstart == 0:
        cut_type = 'loop_off'
        cut_data['start'] = start
        cut_data['loopend'] = loopend
    else:
        cut_type = 'loop_adv'
        cut_data['start'] = start
        cut_data['loopstart'] = loopstart
        cut_data['loopend'] = loopend
    return cut_type, cut_data