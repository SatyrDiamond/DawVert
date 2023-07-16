# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_values
from functions import plugins

def create_blank_prog():
    progout = ''
    progtext = '0 0 0 0.001000 0.001000 1.000000 0.001000 '
    progout += '1 '
    for _ in range(128): progout += progtext
    return progout

def initparams():
    global data_progs
    global data_main
    data_main = {}
    data_progs = {}

    data_main['number_of_slices'] = '0.000000'
    data_main['sliceSensitivity'] = '0.500000'
    data_main['attack'] = '0.001000'
    data_main['decay'] = '0.001000'
    data_main['sustain'] = '1.000000'
    data_main['release'] = '0.001000'
    data_main['load'] = '0.000000'
    data_main['slicemode'] = '1.000000'
    data_main['programGrid'] = '1.000000'
    data_main['playmode'] = '0.000000'
    data_main['pitchbendDepth'] = '12.000000'
    data_main['OneShotForward'] = '1.000000'
    data_main['OneShotReverse'] = '0.000000'
    data_main['LoopForward'] = '0.000000'
    data_main['LoopReverse'] = '0.000000'

    data_progs['slices'] = 'empty'
    data_progs['filepathFromUI'] = ''
    data_progs['program00'] = create_blank_prog()
    data_progs['program01'] = create_blank_prog()
    data_progs['program02'] = create_blank_prog()
    data_progs['program03'] = create_blank_prog()
    data_progs['program04'] = create_blank_prog()
    data_progs['program05'] = create_blank_prog()
    data_progs['program06'] = create_blank_prog()
    data_progs['program07'] = create_blank_prog()
    data_progs['program08'] = create_blank_prog()
    data_progs['program09'] = create_blank_prog()
    data_progs['program10'] = create_blank_prog()
    data_progs['program11'] = create_blank_prog()
    data_progs['program12'] = create_blank_prog()
    data_progs['program13'] = create_blank_prog()
    data_progs['program14'] = create_blank_prog()
    data_progs['program15'] = create_blank_prog()

def slicerdata(cvpj_l, pluginid):
    global data_progs
    global data_main

    filepath = plugins.get_plug_dataval(cvpj_l, pluginid, 'file', '')
    slices = plugins.get_plug_dataval(cvpj_l, pluginid, 'slices', [])
    trigger = plugins.get_plug_dataval(cvpj_l, pluginid, 'trigger', 'normal')

    if trigger == 'normal': releasevalue = '0.001000'
    if trigger == 'oneshot': releasevalue = '1.000000'

    progtable = []
    for _ in range(127): progtable.append('0 0 0 0.001000 0.001000 1.000000 '+releasevalue+' ')
    data_main['release'] = releasevalue
    progout = ''
    progout += str(len(slices))+' 128 '
    data_main['number_of_slices'] = str(len(slices))

    for slicenum in range(len(slices)):
        slicedata = slices[slicenum]
        s_reverse = data_values.get_value(slicedata, 'reverse', False)
        s_looped = data_values.get_value(slicedata, 'looped', False)
        loopout = 0
        if s_reverse == True: loopout += 1
        if s_looped == True: loopout += 2
        progtable[slicenum] = str(slicedata['pos']*2)+' '+str(slicedata['end']*2)+' '+str(loopout)+' 0.001000 0.001000 1.000000 '+releasevalue

    data_progs['filepathFromUI'] = filepath

    for prognums in progtable: progout += prognums+' '
    data_progs['program00'] = progout

def getparams():
    global data_progs
    global data_main
    return [data_progs, data_main]
