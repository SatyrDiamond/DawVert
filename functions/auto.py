# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import xtramath

def move(points, pos):
    newautopoints = []
    for point in points:
        newpoint = point.copy()
        newpoint['position'] = newpoint['position'] + pos
        if newpoint['position'] >= 0: newautopoints.append(newpoint)
    return newautopoints

def trim(points, pos):
    newautopoints = []
    for point in points:
        if point['position'] < pos: newautopoints.append(point)
    return newautopoints

def trimmove(points, startat, endat):
    newpoints = points
    if endat != None: newpoints = trim(points, endat)
    if startat != None: newpoints = move(points, -startat)
    return newpoints

def getduration(listdata):
    duration_final = 0
    for listpoint in listdata:
        endpos = listpoint['position']
        if duration_final < endpos: duration_final = endpos
    return duration_final

def getdurpos(listdata, startpos):
    duration_final = 0
    pos_final = 100000000
    for listpoint in listdata:
        pointpos = listpoint['position']
        if duration_final < pointpos: duration_final = pointpos
        if pos_final > pointpos: pos_final = pointpos
    return pos_final, duration_final

def makepl(t_pos, t_dur, t_points):
    pl_data = {}
    pl_data['position'] = t_pos
    pl_data['duration'] = t_dur
    pl_data['points'] = t_points
    return pl_data

def multiply_nopl(auto_data, addval, mulval):
    for point in auto_data:
        if 'value' in point:
            point['value'] = (point['value']+addval)*mulval
    return auto_data

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

def remove_instant_note(cvpj_points):
    cvpj_output = []
    startpoint = True
    prevvalue = 0

    zerofound = False
    for cvpj_auto_poi in cvpj_points:
        if cvpj_auto_poi['position'] == 0: zerofound = True

    if zerofound == False: cvpj_output.append({'position': 0, 'value': 0})

    for cvpj_auto_poi in cvpj_points:
        pointtype = cvpj_auto_poi['type'] if 'type' in cvpj_auto_poi else 'normal'
        instanttype = True if pointtype == 'instant' else False
        if instanttype == True:
            cvpj_output.append({'position': cvpj_auto_poi['position'], 'value': prevvalue})

        cvpj_output.append({'position': cvpj_auto_poi['position'], 'value': cvpj_auto_poi['value']})
        prevvalue = cvpj_auto_poi['value']
        startpoint = False

    return cvpj_output


def remove_instant(cvpj_points, startposition, isnote):
    cvpj_output = []
    startpoint = True
    prevvalue = None
    if len(cvpj_points) != 0:
        cvpj_output.append({'position': 0, 'value': cvpj_points[0]['value']})

    for cvpj_auto_poi in cvpj_points:
        cvpj_auto_poi['position'] += startposition
        instanttype = False
        if 'type' in cvpj_auto_poi:
            if cvpj_auto_poi['type'] == 'instant':
                instanttype = True
        if (instanttype == True and prevvalue != None) or (startpoint == True and prevvalue != None):
            cvpj_output.append({'position': cvpj_auto_poi['position']-0.000001, 'value': prevvalue})
        if isnote == True:
            if (instanttype == True and prevvalue == None) or (startpoint == True and prevvalue == None):
                cvpj_output.append({'position': cvpj_auto_poi['position'], 'value': 0})
        cvpj_output.append({'position': cvpj_auto_poi['position'], 'value': cvpj_auto_poi['value']})
        prevvalue = cvpj_auto_poi['value']
        startpoint = False
    return cvpj_output

def points2blocks(cvpj_points):
    t_posval = []
    prevvalue = 0
    outblocks = []

    for part in cvpj_points:
        isinstant = False
        if 'type' in part:
            if part['type'] == 'instant': isinstant = True
        if isinstant == True: t_posval.append([part['position'], prevvalue])
        t_posval.append([part['position'], part['value']])
        prevvalue = part['value']

    for pinu in range(len(t_posval)-1):
        slide_dur = t_posval[pinu+1][0] - t_posval[pinu][0]
        if t_posval[pinu+1][1] != t_posval[pinu][1]:
            outblocks.append( [t_posval[pinu][0], slide_dur, t_posval[pinu+1][1]] )
    return outblocks

def blocks2points(auto_pl_blocks):
    outplacements = []
    if auto_pl_blocks != []:
        basepos = auto_pl_blocks[0][0]
        basedur = auto_pl_blocks[-1][0]
        autopl = {}
        autopl['position'] = basepos
        autopl['duration'] = (basedur+4)-basepos
        autopl['points'] = []
        for point in auto_pl_blocks:
            #print(basepos, basedur, point)
            if point[1] == 0: outtype = 'instant'
            else: outtype = 'normal'
            autopl['points'].append( {"position": point[0]-basepos, "value": point[2], "type": outtype} )
    return autopl

def values2points(i_values, i_minmax):
    curpos = 1
    points = []
    if i_minmax == None:
        for i_value in i_values:
            points.append( {"position": curpos, "value": i_value} )
            curpos += 1
    else:
        for i_value in i_values:
            normval = xtramath.between_to_one(i_minmax[0], i_minmax[1], i_value)
            points.append( {"position": curpos, "value": normval} )
            curpos += 1
    return points

def twopoints_addmul(twopoints, addval, mulval):
    for twopoint in twopoints:
        twopoint[1] = (twopoint[1]+addval)*mulval
    return twopoints
