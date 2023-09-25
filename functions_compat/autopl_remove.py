# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

def do_placements(i_autodata):
    new_points = []
    autotype = i_autodata['type']
    autodata = i_autodata['placements']
    for autopart in autodata:
        base_pos = autopart['position']
        if len(autopart['points']) != 0: autopart['points'][0]['type'] = 'instant'
        for oldpoint in autopart['points']:
            oldpoint['position'] += base_pos
            new_points.append(oldpoint)
    if len(new_points) != 0: 
        o_autodata = {}
        o_autodata['type'] = autotype
        o_autodata['placements'] = [{'position': 0, 'points': new_points, 'duration': new_points[-1]['position']+8}]
        return o_autodata
    else: 
        o_autodata = {}
        o_autodata['type'] = autotype
        o_autodata['placements'] = []
        return o_autodata

def process(cvpj_l, cvpj_type, in_compat, out_compat):
    if in_compat == False and out_compat == True:
        if 'automation' in cvpj_l:
            cvpj_auto = cvpj_l['automation']
            for autotype in cvpj_auto:
                if autotype in ['main', 'master']:
                    for autoid in cvpj_auto[autotype]:
                        cvpj_auto[autotype][autoid] = do_placements(cvpj_auto[autotype][autoid])
                else:
                    for packid in cvpj_auto[autotype]:
                        for autoid in cvpj_auto[autotype][packid]:
                            cvpj_auto[autotype][packid][autoid] = do_placements(cvpj_auto[autotype][packid][autoid])
        return True
    else: return False