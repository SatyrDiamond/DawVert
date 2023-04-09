# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

def multiply(auto_data, addval, mulval):
    for autopl in auto_data:
        if 'points' in autopl:
            for point in autopl['points']:
                if 'value' in point:
                    point['value'] = (point['value']+addval)*mulval
    return auto_data


def resize(autopl):
    in_points = autopl['points']

    firstpos = None
    for note in in_points:
        pointpos = note['position']
        if firstpos != None: 
            if firstpos > pointpos: firstpos = pointpos
        else: firstpos = pointpos

    if firstpos != None:
        for in_point in in_points:
            in_point['position'] -= firstpos
        autopl['duration'] -= firstpos
        autopl['position'] += firstpos

def twopoints2cvpjpoints(twopoints, notelen, pointtype, endlen):
    cvpj_points = []
    for twopoint in twopoints:
        cvpj_points.append({"type": pointtype, "position": twopoint[0]*notelen, "value": twopoint[1]})
    return [{'position': 0, 'duration': (twopoints[-1][0]*notelen)+endlen, 'points': cvpj_points}]
