# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import base64
import json
import math
import plugin_input
import os
import struct
import zlib
import sys
import xml.etree.ElementTree as ET
from functions import note_mod
from functions import note_data
from functions import notelist_data
from functions import data_dataset
from functions import colors
from functions import auto
from functions import plugins
from functions import song
from functions_tracks import auto_id
from functions_tracks import auto_nopl
from functions_tracks import fxrack
from functions_tracks import fxslot
from functions_tracks import tracks_r

lfoshape = ['sine', 'tri', 'saw', 'square', 'custom', 'random']
arpdirection = ['up', 'down', 'updown', 'downup', 'random']

filtertype = [
['lowpass', None], ['highpass', None], ['bandpass','csg'], 
['bandpass','czpg'], ['notch', None], ['allpass', None], 
['moog', None], ['lowpass','double'], ['lowpass','rc12'], 
['bandpass','rc12'], ['highpass','rc12'], ['lowpass','rc24'], 
['bandpass','rc24'], ['highpass','rc24'], ['formant', None], 
['moog','double'], ['lowpass','sv'], ['bandpass','sv'], 
['highpass','sv'], ['notch','sv'], ['formant','fast'], ['tripole', None]
]

opl2opvarnames = [
['_a', '_env_attack'],
['_d', '_env_decay'],
['_r', '_env_release'],
['_s', '_env_sustain'],
['_mul', '_freqmul'],
['_ksr', '_ksr'],
['_lvl', '_level'],
['_perc', '_sustained'],
['_scale', '_scale'],
['_trem', '_tremolo'],
['_vib', '_vibrato'],
['_waveform', '_waveform']
]

opl2varnames = [
['feedback', 'feedback'],
['fm', 'fm'],
['tremolo_depth', 'tremolo_depth'],
['vibrato_depth', 'vibrato_depth']
]

sid_att = [2, 8, 16, 24, 38, 56, 68, 80, 100, 250, 500, 800, 1000, 3000, 5000, 8000]
sid_decrel = [6, 24, 48, 72, 114, 168, 204, 240, 300, 750, 1500, 2400, 3000, 9000, 15000, 24000]
sid_wave = ['square', 'triangle', 'saw', 'noise_4bit']




chord = [[0], [0, 4, 7], [0, 4, 6], [0, 3, 7], [0, 3, 6], [0, 2, 7], [0, 5, 7], [0, 4, 8], [0, 5, 8], [0, 3, 6, 9], [0, 4, 7, 9], [0, 5, 7, 9], [0, 4, 7, 9, 14], [0, 3, 7, 9], [0, 3, 7, 9, 14], [0, 4, 7, 10], [0, 5, 7, 10], [0, 4, 8, 10], [0, 4, 6, 10], [0, 4, 7, 10, 15], [0, 4, 7, 10, 13], [0, 4, 8, 10, 15], [0, 4, 8, 10, 13], [0, 4, 6, 10, 13], [0, 4, 7, 10, 17], [0, 4, 7, 10, 21], [0, 4, 7, 10, 18], [0, 4, 7, 11], [0, 4, 6, 11], [0, 4, 8, 11], [0, 4, 7, 11, 18], [0, 4, 7, 11, 21], [0, 3, 7, 10], [0, 3, 6, 10], [0, 3, 7, 10, 13], [0, 3, 7, 10, 17], [0, 3, 7, 10, 21], [0, 3, 7, 11], [0, 3, 7, 11, 17], [0, 3, 7, 11, 21], [0, 4, 7, 10, 14], [0, 5, 7, 10, 14], [0, 4, 7, 14], [0, 4, 8, 10, 14], [0, 4, 6, 10, 14], [0, 4, 7, 10, 14, 18], [0, 4, 7, 10, 14, 20], [0, 4, 7, 11, 14], [0, 5, 7, 11, 15], [0, 4, 8, 11, 14], [0, 4, 7, 11, 14, 18], [0, 3, 7, 10, 14], [0, 3, 7, 14], [0, 3, 6, 10, 14], [0, 3, 7, 11, 14], [0, 4, 7, 10, 14, 17], [0, 4, 7, 10, 13, 17], [0, 4, 7, 11, 14, 17], [0, 3, 7, 10, 14, 17], [0, 3, 7, 11, 14, 17], [0, 4, 7, 10, 14, 21], [0, 4, 7, 10, 15, 21], [0, 4, 7, 10, 13, 21], [0, 4, 6, 10, 13, 21], [0, 4, 7, 11, 14, 21], [0, 3, 7, 10, 14, 21], [0, 3, 7, 11, 14, 21], [0, 2, 4, 5, 7, 9, 11], [0, 2, 3, 5, 7, 8, 11], [0, 2, 3, 5, 7, 9, 11], [0, 2, 4, 6, 8, 10], [0, 2, 3, 5, 6, 8, 9, 11], [0, 2, 4, 7, 9], [0, 3, 5, 7, 10], [0, 1, 5, 7, 10], [0, 2, 4, 5, 7, 8, 9, 11], [0, 2, 4, 5, 7, 9, 10, 11], [0, 3, 5, 6, 7, 10], [0, 1, 4, 5, 7, 8, 11], [0, 1, 4, 6, 8, 10, 11], [0, 1, 3, 5, 7, 9, 11], [0, 1, 3, 5, 7, 8, 11], [0, 2, 3, 6, 7, 8, 11], [0, 2, 3, 5, 7, 9, 10], [0, 1, 3, 5, 7, 8, 10], [0, 2, 4, 6, 7, 9, 11], [0, 2, 4, 5, 7, 9, 10], [0, 2, 3, 5, 7, 8, 10], [0, 1, 3, 5, 6, 8, 10], [0, 2, 3, 5, 7, 8, 10], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], [0, 1, 3, 4, 6, 7, 9, 10], [0, 7], [0, 1, 4, 5, 7, 8, 10], [0, 1, 4, 5, 6, 8, 11]]
fxlist = {}
fxlist['amplifier'] = 'AmplifierControls'
fxlist['bassbooster'] = 'bassboostercontrols'
fxlist['bitcrush'] = 'bitcrushcontrols'
fxlist['crossovereq'] = 'crossoevereqcontrols'
fxlist['delay'] = 'Delay'
fxlist['dualfilter'] = 'DualFilterControls'
fxlist['dynamicsprocessor'] = 'dynamicsprocessor_controls'
fxlist['eq'] = 'Eq'
fxlist['flanger'] = 'Flanger'
fxlist['multitapecho'] = 'multitapechocontrols'
fxlist['peakcontrollereffect'] = 'peakcontrollereffectcontrols'
fxlist['reverbsc'] = 'ReverbSCControls'
fxlist['spectrumanalyzer'] = 'spectrumanaylzercontrols'
fxlist['stereoenhancer'] = 'stereoenhancercontrols'
fxlist['stereomatrix'] = 'stereomatrixcontrols'
fxlist['waveshaper'] = 'waveshapercontrols'
fxlist['vsteffect'] = 'vsteffectcontrols'

# ------- functions -------


send_auto_id = 1000
def get_send_auto_id():
    global send_auto_id
    send_auto_id += 1
    return 'send'+str(send_auto_id)

def add_window_data(xmltag, cvpj_l, w_group, w_name):
    window_x = xmltag.get('x')
    window_y = xmltag.get('y')
    window_visible = xmltag.get('visible')
    window_width = xmltag.get('width')
    window_height = xmltag.get('height')
    window_maximized = xmltag.get('maximized')

    w_pos = None
    w_size = None
    w_open = None
    w_max = None

    if window_x != None and window_y != None: w_pos = [int(window_x), int(window_y)]
    if window_width != None and window_height != None: w_size = [int(window_width), int(window_height)]
    if window_visible != None: w_open = bool(int(window_visible))
    if window_maximized != None: w_max = bool(int(window_maximized))

    song.add_visual_window(cvpj_l, w_group, w_name, w_pos, w_size, w_open, w_max)



def getvstparams(cvpj_plugindata, pluginid, xmldata):
    if os.path.exists( xmldata.get('plugin')):
        cvpj_plugindata.dataval_add('path', xmldata.get('plugin'))
    else:
        cvpj_plugindata.dataval_add('path', lmms_vstpath+xmldata.get('plugin'))
    vst_data = xmldata.get('chunk')
    vst_numparams = xmldata.get('numparams')
    vst_program = xmldata.get('program')

    w_open = xmldata.get('guivisible')
    if w_open == None: w_open = False
    song.add_visual_window(cvpj_l, 'plugin', pluginid, None, None, bool(int(w_open)), None)

    if vst_program != None: 
        cvpj_plugindata.dataval_add('current_program', int(vst_program))
    if vst_data != None:
        cvpj_plugindata.dataval_add('datatype', 'chunk')
        cvpj_plugindata.dataval_add('chunk', vst_data)
    elif vst_numparams != None:
        cvpj_plugindata.dataval_add('datatype', 'param')
        cvpj_plugindata.dataval_add('numparams', int(vst_numparams))
        for param in range(int(vst_numparams)):
            paramdata = xmldata.get('param'+str(param)).split(':')
            paramnum = 'vst_param_'+str(param)
            cvpj_plugindata.param_add(paramnum, float(paramdata[-1]), 'float', paramdata[1])
    for node in xmldata.iter():
        notetagtxt = node.tag
        if notetagtxt.startswith('param'):
            value = node.get('value')
            if value != None:
                auto_id.in_define(str(node.get('id')), ['plugin', pluginid, 'vst_param_'+notetagtxt[5:]], 'float', None)

def hundredto1(lmms_input): return float(lmms_input) * 0.01

def lmms_auto_getvalue(x_tag, x_name, i_fbv, i_type, i_addmul, i_loc):
    outval = i_fbv

    xmlval = None
    if x_tag.get(x_name) != None:
        xmlval = x_tag.get(x_name)
    elif x_tag.findall(x_name) != []: 
        realvaluetag = x_tag.findall(x_name)[0]
        xmlval = realvaluetag.get('value')
        if xmlval != None: auto_id.in_define(str(realvaluetag.get('id')), i_loc, i_type, i_addmul)
    
    if xmlval != None: outval = (float(xmlval)+i_addmul[0])*i_addmul[1] if i_addmul != None else float(xmlval)
    if i_type == 'float': outval = outval
    if i_type == 'int': outval = int(outval)
    if i_type == 'bool': outval = bool(int(outval))

    return outval

def lmms_getvalue(xmltag, xmlname, fallbackval): 
    xmlval = xmltag.get(xmlname)
    if xmlval == None: xmlval = fallbackval
    return xmlval

def dset_plugparams(pluginname, pluginid, xml_data, cvpj_plugindata):
    paramlist = dataset.params_list('plugin', pluginname)
    if paramlist != None:
        for paramname in paramlist:
            paramlist = dataset.params_i_get('plugin', pluginname, paramname)
            pv_noauto,pv_type,pv_def,pv_min,pv_max,pv_name = paramlist
            if pv_noauto == False:
                plugval = lmms_auto_getvalue(xml_data, paramname, 0, pv_type, None, ['plugin', pluginid, paramname])
                cvpj_plugindata.param_add(paramname, plugval, pv_type, pv_name)
            else:
                xml_pluginparam = xml_data.get(paramname)
                if xml_pluginparam: cvpj_plugindata.dataval_add(paramname, xml_pluginparam)



# ------- Instruments and Plugins -------

def exp2sec(value): return (value*value)*5

def asdflfo_get(trkX_insttr, inst_plugindata):
    elcX = trkX_insttr.findall('eldata')
    if len(elcX) != 0:
        eldataX = elcX[0]
        if eldataX.findall('elvol'): asdflfo(inst_plugindata, eldataX.findall('elvol')[0], 'vol')
        if eldataX.findall('elcut'): asdflfo(inst_plugindata, eldataX.findall('elcut')[0], 'cutoff')
        if eldataX.findall('elres'): asdflfo(inst_plugindata, eldataX.findall('elres')[0], 'reso')

        if eldataX.get('ftype') != None: 
            filter_cutoff = float(lmms_getvalue(eldataX, 'fcut', 0))
            filter_reso = float(lmms_getvalue(eldataX, 'fres', 0))
            filter_enabled = float(lmms_getvalue(eldataX, 'fwet', 0))
            filter_type, filter_subtype = filtertype[int(eldataX.get('ftype'))]
            inst_plugindata.filter_add(filter_enabled, filter_cutoff, filter_reso, filter_type, filter_subtype)

def asdflfo(inst_plugindata, xmlO, asdrtype):
    envelopeparams = {}

    asdr_predelay = exp2sec(float(lmms_getvalue(xmlO, 'pdel', 0)))
    asdr_attack = exp2sec(float(lmms_getvalue(xmlO, 'att', 0)))
    asdr_hold = exp2sec(float(lmms_getvalue(xmlO, 'hold', 0)))
    asdr_decay = exp2sec(float(lmms_getvalue(xmlO, 'dec', 0)))
    asdr_sustain = float(lmms_getvalue(xmlO, 'sustain', 1))
    asdr_release = exp2sec(float(lmms_getvalue(xmlO, 'rel', 0)))
    asdr_amount = float(lmms_getvalue(xmlO, 'amt', 0))
    if asdrtype == 'cutoff': asdr_amount *= 6000

    inst_plugindata.asdr_env_add(asdrtype, asdr_predelay, asdr_attack, asdr_hold, asdr_decay, asdr_sustain, asdr_release, asdr_amount)

    lfoparams = {}

    speedx100 = xmlO.get('x100')
    speedx100 = int(speedx100) if speedx100 != None else 0

    lfo_predelay = float(lmms_getvalue(xmlO, 'pdel', 0))
    lfo_attack = exp2sec(float(lmms_getvalue(xmlO, 'latt', 0)))
    lfo_amount = float(lmms_getvalue(xmlO, 'lamt', 0))
    lfo_shape = lfoshape[int(lmms_getvalue(xmlO, 'lshape', 0))]
    if asdrtype == 'cutoff': lfo_amount *= 6000

    lfo_speed = 0
    if xmlO.get('lspd') != None: lfo_speed = (float(xmlO.get('lspd'))*0.2) if speedx100 == 1 else (float(xmlO.get('lspd'))*20)
    inst_plugindata.lfo_add(asdrtype, lfo_shape, 'seconds', lfo_speed, lfo_predelay, lfo_attack, lfo_amount)

def lmms_decodeplugin(trkX_insttr):
    trkX_instrument = trkX_insttr.findall('instrument')[0]
    pluginname = trkX_instrument.get('name')

    out_color = None

    pluginid = plugins.get_id()

    xml_a_plugin = trkX_instrument.findall(pluginname)
    if len(xml_a_plugin) != 0: 
        xml_plugin = xml_a_plugin[0]

        if pluginname == "sf2player":
            inst_plugindata = plugins.cvpj_plugin('deftype', 'soundfont2', None)
            inst_plugindata.dataval_add('bank', int(xml_plugin.get('bank')))
            inst_plugindata.dataval_add('patch', int(xml_plugin.get('patch')))
            inst_plugindata.dataval_add('file', xml_plugin.get('src'))
            inst_plugindata.param_add('gain', float(xml_plugin.get('gain')), 'float', 'Gain')
            for cvpj_name, lmmsname in [['chorus_depth','chorusDepth'],['chorus_level','chorusLevel'],['chorus_lines','chorusNum'],['chorus_speed','chorusSpeed'],['reverb_damping','reverbDamping'],['reverb_level','reverbLevel'],['reverb_roomsize','reverbRoomSize'],['reverb_width','reverbWidth']]:
                inst_plugindata.param_add(cvpj_name, float(xml_plugin.get(lmmsname)), 'float', lmmsname)
            inst_plugindata.param_add('chorus_enabled', float(xml_plugin.get('chorusOn')), 'bool', 'chorusOn')
            inst_plugindata.param_add('reverb_enabled', float(xml_plugin.get('reverbOn')), 'bool', 'reverbOn')

        elif pluginname == "audiofileprocessor":
            inst_plugindata = plugins.cvpj_plugin('sampler', lmms_getvalue(xml_plugin, 'src', ''), None)
            inst_plugindata.dataval_add('reverse', bool(int(lmms_getvalue(xml_plugin, 'reversed', 0))))
            inst_plugindata.dataval_add('amp', float(lmms_getvalue(xml_plugin, 'amp', 1))/100)
            inst_plugindata.dataval_add('continueacrossnotes', bool(int(lmms_getvalue(xml_plugin, 'stutter', 0))))
            inst_plugindata.dataval_add('trigger', 'normal')
            inst_plugindata.dataval_add('point_value_type', "percent")

            cvpj_loop = {}
            looped = int(xml_plugin.get('looped'))
            if looped == 0: cvpj_loop = {'enabled': 0}
            if looped == 1: cvpj_loop = {'enabled': 1, 'mode': "normal"}
            if looped == 2: cvpj_loop = {'enabled': 1, 'mode': "pingpong"}

            looppoint = xml_plugin.get('lframe')
            startpoint = xml_plugin.get('eframe')

            cvpj_loop['points'] = [
                float(looppoint) if looppoint != None else 0, 
                float(startpoint) if startpoint != None else 0]
            inst_plugindata.dataval_add('loop', cvpj_loop)
            inst_plugindata.dataval_add('end', float(lmms_getvalue(xml_plugin, 'eframe', 1)))
            inst_plugindata.dataval_add('start', float(lmms_getvalue(xml_plugin, 'sframe', 0)))
            inst_plugindata.dataval_add('point_value_type', "percent")

            lmms_interpolation = int(xml_plugin.get('interp'))
            if lmms_interpolation == 0: cvpj_interpolation = "none"
            if lmms_interpolation == 1: cvpj_interpolation = "linear"
            if lmms_interpolation == 2: cvpj_interpolation = "sinc"
            inst_plugindata.dataval_add('interpolation', cvpj_interpolation)

            asdflfo_get(trkX_insttr, inst_plugindata)


        elif pluginname == "OPL2" or pluginname == "opulenz":
            inst_plugindata = plugins.cvpj_plugin('deftype', 'fm', 'opl2')
            for lmms_opname, cvpj_opname in [['op1', 'mod'],['op2', 'car']]:
                for varname in opl2opvarnames:
                    plugval = lmms_auto_getvalue(xml_plugin, lmms_opname+varname[0], 0, 'int', None, ['plugin', pluginid, cvpj_opname+varname[1]])
                    inst_plugindata.param_add(cvpj_opname+varname[1], plugval, 'int', lmms_opname+varname[1])
                
            for varname in opl2varnames:
                plugval = lmms_auto_getvalue(xml_plugin, varname[0], 0, 'int', None,  ['plugin', pluginid, varname[1]])
                inst_plugindata.param_add(varname[1], plugval, 'int', varname[1])

        elif pluginname == "vestige":
            inst_plugindata = plugins.cvpj_plugin('deftype', 'vst2', 'win')
            getvstparams(inst_plugindata, pluginid, xml_plugin)

        else:
            inst_plugindata = plugins.cvpj_plugin('deftype', 'native-lmms', pluginname)
            dset_plugparams(pluginname, pluginid, xml_plugin, inst_plugindata)

            asdflfo_get(trkX_insttr, inst_plugindata)

            if pluginname == "bitinvader":
                sampleshape = xml_plugin.get('sampleShape')
                sampleshape = base64.b64decode(sampleshape.encode('ascii'))
                sampleshape_size = len(sampleshape)//4
                wave_data = struct.unpack('f'*sampleshape_size, sampleshape)
                inst_plugindata.wave_add('main', wave_data, -1, 1)
                inst_plugindata.osc_num_oscs(1)
                inst_plugindata.osc_opparam_set(0, 'wave_name', 'main')

            if pluginname == "sid":
                inst_plugindata.osc_num_oscs(3)
                inst_plugindata.oscdata_add('traits', ['coarse', 'pulse_width'])
                for num in range(3):
                    sid_waveform = inst_plugindata.param_get('waveform'+str(num), 0)[0]
                    sid_pulsewidth = inst_plugindata.param_get('pulsewidth'+str(num), 0)[0]
                    sid_coarse = inst_plugindata.param_get('coarse'+str(num), 0)[0]
                    sid_attack = inst_plugindata.param_get('attack'+str(num), 0)[0]
                    sid_decay = inst_plugindata.param_get('decay'+str(num), 0)[0]
                    sid_sustain = inst_plugindata.param_get('sustain'+str(num), 0)[0]
                    sid_release = inst_plugindata.param_get('release'+str(num), 0)[0]
                    sid_attack = sid_att[int(sid_attack)]/1000
                    sid_decay = sid_decrel[int(sid_decay)]/1000
                    sid_sustain = sid_sustain/15
                    sid_release = sid_decrel[int(sid_release)]/1000
                    asdr_name = 'osc'+str(num)
                    inst_plugindata.asdr_env_add(asdr_name, 0, sid_attack, 0, sid_decay, sid_sustain, sid_release, 1)
                    inst_plugindata.osc_opparam_set(num, 'shape', sid_wave[int(sid_waveform)])
                    inst_plugindata.osc_opparam_set(num, 'env_adsr', {'vol': asdr_name})
                    inst_plugindata.osc_opparam_set(num, 'pulse_width', int(sid_pulsewidth)/4095)
                    inst_plugindata.osc_opparam_set(num, 'coarse', int(sid_coarse))
                    inst_plugindata.osc_opparam_set(num, 'vol', 1)
                sid_voice3Off = inst_plugindata.param_get('voice3Off', 0)[0]
                inst_plugindata.osc_opparam_set(2, 'vol', int(not int(sid_voice3Off)))

            if pluginname == "zynaddsubfx":
                zdata = xml_plugin.findall('ZynAddSubFX-data')
                if zdata: 
                    xsdata = ET.tostring(zdata[0], encoding='utf-8')
                    inst_plugindata.dataval_add('data', base64.b64encode(xsdata).decode('ascii'))

            if pluginname == "tripleoscillator":
                threeosc_userwavefile0 = xml_plugin.get('userwavefile0')
                threeosc_userwavefile1 = xml_plugin.get('userwavefile1')
                threeosc_userwavefile2 = xml_plugin.get('userwavefile2')
                inst_plugindata.fileref_add('osc_1', threeosc_userwavefile0)
                inst_plugindata.fileref_add('osc_2', threeosc_userwavefile1)
                inst_plugindata.fileref_add('osc_3', threeosc_userwavefile2)

            print(pluginname)

        inst_plugindata.to_cvpj(cvpj_l, pluginid)
    
    _, plugincolor = dataset.object_get_name_color('plugin', pluginname)

    return plugincolor, pluginname, pluginid

# ------- Notelist -------

def lmms_decode_nlpattern(notesX):
    notelist = []
    printcountpat = 0
    for noteX in notesX:
        noteJ = note_data.rx_makenote(float(noteX.get('pos'))/12, float(noteX.get('len'))/12, int(noteX.get('key'))-60, hundredto1(noteX.get('vol')), hundredto1(noteX.get('pan')))
        noteX_auto = noteX.findall('automationpattern')
        if len(noteX_auto) != 0: 
            noteJ['notemod'] = {}
            noteJ['notemod']['auto'] = {}
            noteJ['notemod']['auto']['pitch'] = []
            noteX_auto = noteX.findall('automationpattern')[0]
            if len(noteX_auto.findall('detuning')) != 0: 
                noteX_detuning = noteX_auto.findall('detuning')[0]
                if len(noteX_detuning.findall('time')) != 0: 
                    prognum = int(noteX_detuning.get('prog'))
                    for pointX in noteX_detuning.findall('time'):
                        pointJ = {}
                        pointJ['position'] = float(pointX.get('pos')) / 12
                        pointJ['value'] = float(pointX.get('value'))
                        pointJ['type'] = 'instant' if prognum == 0 else 'normal'
                        noteJ['notemod']['auto']['pitch'].append(pointJ)
        printcountpat += 1
        notelist.append(noteJ)
    print('['+str(printcountpat), end='] ')
    return notelist
def lmms_decode_nlplacements(trkX):
    nlplacements = []
    patsX = trkX.findall('pattern')
    printcountplace = 0
    print('[input-lmms]       Placements: ', end='')
    for patX in patsX:
        printcountplace += 1
        placeJ = {}
        placeJ["position"] = float(patX.get('pos')) / 12
        placeJ["name"] = patX.get('name')
        placeJ["muted"] = bool(int(patX.get('muted')))
        notesX = patX.findall('note')
        notesJ = lmms_decode_nlpattern(notesX)
        placeJ["notelist"] = notesJ
        out_duration = notelist_data.getduration(notesJ)
        if out_duration == 0: out_duration = 16
        placeJ["duration"] = math.ceil(out_duration/16)*16
        nlplacements.append(placeJ)
    print('['+str(printcountplace), end='] ')
    print(' ')
    return nlplacements

# ------- Track: Inst -------

def lmms_decode_inst_track(trkX, trackid):
    cvpj_name = trkX.get('name')
    print('[input-lmms] Instrument Track')
    print('[input-lmms]       Name: ' + cvpj_name)

    cvpj_enabled = int(lmms_auto_getvalue(trkX, 'muted', 1, 'bool', [-1, -1], ['track', trackid, 'enabled']))
    cvpj_solo = int(lmms_auto_getvalue(trkX, 'solo', 1, 'bool', None, ['track', trackid, 'solo']))

    #trkX_insttr
    trkX_insttr = trkX.findall('instrumenttrack')[0]
    track_color, pluginname, instpluginid = lmms_decodeplugin(trkX_insttr)
    add_window_data(trkX, cvpj_l, 'plugin', instpluginid)
    cvpj_pan = float(lmms_auto_getvalue(trkX_insttr, 'pan', 0, 'float', [0, 0.01], ['track', trackid, 'pan']))
    cvpj_vol = float(lmms_auto_getvalue(trkX_insttr, 'vol', 100, 'float', [0, 0.01], ['track', trackid, 'vol']))
    
    tracks_r.track_create(cvpj_l, trackid, 'instrument')
    tracks_r.track_visual(cvpj_l, trackid, name=cvpj_name, color=track_color)
    tracks_r.track_inst_pluginid(cvpj_l, trackid, instpluginid)
    tracks_r.track_param_add(cvpj_l, trackid, 'vol', cvpj_vol, 'float')
    tracks_r.track_param_add(cvpj_l, trackid, 'pan', cvpj_pan, 'float')
    tracks_r.track_param_add(cvpj_l, trackid, 'enabled', cvpj_enabled, 'bool')
    tracks_r.track_param_add(cvpj_l, trackid, 'solo', cvpj_solo, 'bool')

    #midi
    xml_a_midiport = trkX_insttr.findall('midiport')
    if len(xml_a_midiport) != 0:

        midi_inJ = {}
        midiportX = trkX_insttr.findall('midiport')[0]
        midi_inJ['enabled'] = int(midiportX.get('readable'))
        if midiportX.get('inputchannel') != '0' and midiportX.get('inputchannel') != None: 
            midi_inJ['channel'] = int(midiportX.get('inputchannel'))
        if midiportX.get('fixedinputvelocity') != '-1' and midiportX.get('fixedinputvelocity') != None: 
            midi_inJ['fixedvelocity'] = int(midiportX.get('fixedinputvelocity'))+1
        tracks_r.track_dataval_add(cvpj_l, trackid, 'midi', 'input', midi_inJ)

        midi_outJ = {}
        midi_outJ['enabled'] = int(midiportX.get('writable'))
        midi_outJ['channel'] = int(midiportX.get('outputchannel'))
        if midiportX.get('outputprogram') != None: 
            midi_outJ['program'] = int(midiportX.get('outputprogram'))
        if midiportX.get('fixedoutputvelocity') != '-1' and midiportX.get('fixedoutputvelocity') != None: 
            midi_outJ['fixedvelocity'] = int(midiportX.get('fixedoutputvelocity'))+1
        if midiportX.get('fixedoutputnote') != '-1' and midiportX.get('fixedoutputnote') != None: 
            midi_outJ['fixednote'] = int(midiportX.get('fixedoutputnote'))+1
        tracks_r.track_dataval_add(cvpj_l, trackid, 'midi', 'output', midi_outJ)

        tracks_r.track_dataval_add(cvpj_l, trackid, 'midi', 'basevelocity', int(midiportX.get('basevelocity')))

    xml_a_fxchain = trkX_insttr.findall('fxchain')
    if len(xml_a_fxchain) != 0: fxslot.insert(cvpj_l, ['track', trackid], 'audio', lmms_decode_fxchain(xml_a_fxchain[0]))


    xml_fxch = trkX_insttr.get('fxch')
    if xml_fxch != None: tracks_r.track_fxrackchan_add(cvpj_l, trackid, int(xml_fxch))
        
    tracks_r.track_param_add(cvpj_l, trackid, 'usemasterpitch', trkX_insttr.get('usemasterpitch'), 'bool')
    tracks_r.track_param_add(cvpj_l, trackid, 'pitch', float(lmms_auto_getvalue(trkX_insttr, 'pitch', 0, 'float', [0, 0.01], ['track', trackid, 'pitch'])), 'float')

    if 'basenote' in trkX_insttr.attrib:
        basenote = int(trkX_insttr.get('basenote'))-57
        noteoffset = 0
        if pluginname == 'audiofileprocessor': noteoffset = 3
        if pluginname == 'sf2player': noteoffset = 0
        if pluginname == 'OPL2': noteoffset = 24
        middlenote = basenote - noteoffset
        tracks_r.track_dataval_add(cvpj_l, trackid, 'instdata', 'middlenote', middlenote)

    xml_a_arpeggiator = trkX_insttr.findall('arpeggiator')
    if len(xml_a_arpeggiator) != 0:
        trkX_arpeggiator = xml_a_arpeggiator[0]
        pluginid = plugins.get_id()

        cvpj_l_arpeggiator_enabled = lmms_auto_getvalue(trkX_arpeggiator, 'arp-enabled', 0, 'bool', None, ['slot', pluginid, 'enabled'])
        notefx_plugindata = plugins.cvpj_plugin('deftype', 'native-lmms', 'arpeggiator')
        notefx_plugindata.fxdata_add(cvpj_l_arpeggiator_enabled, None)
        dset_plugparams('arpeggiator', pluginid, trkX_arpeggiator, notefx_plugindata)
        notefx_plugindata.to_cvpj(cvpj_l, pluginid)
        fxslot.insert(cvpj_l, ['track', trackid], 'notes', pluginid)


    xml_a_chordcreator = trkX_insttr.findall('chordcreator')
    if len(xml_a_chordcreator) != 0:
        trkX_chordcreator = xml_a_chordcreator[0]
        pluginid = plugins.get_id()

        cvpj_l_chordcreator_enabled = lmms_auto_getvalue(trkX_chordcreator, 'chord-enabled', 0, 'bool', None, ['slot', pluginid, 'enabled'])
        notefx_plugindata = plugins.cvpj_plugin('deftype', 'native-lmms', 'chordcreator')
        notefx_plugindata.fxdata_add(cvpj_l_chordcreator_enabled, None)
        dset_plugparams('chordcreator', pluginid, trkX_chordcreator, notefx_plugindata)
        notefx_plugindata.to_cvpj(cvpj_l, pluginid)
        fxslot.insert(cvpj_l, ['track', trackid], 'notes', pluginid)


    tracks_r.add_pl(cvpj_l, trackid, 'notes', lmms_decode_nlplacements(trkX))

    print('[input-lmms]')

# ------- Audio Placements -------

def lmms_decode_audioplacements(trkX):
    audioplacements = []
    sampletcoX = trkX.findall('sampletco')
    printcountplace = 0
    print('[input-lmms]       Placements: ', end='')
    for samplecX in sampletcoX:
        printcountplace += 1
        placeJ = {}
        placeJ["position"] = float(samplecX.get('pos')) / 12
        placeJ["file"] = samplecX.get('src')
        placeJ["duration"] = float(samplecX.get('len')) / 12
        placeJ['enabled'] = int(not int(samplecX.get('muted')))
        placeJ['sample_rate'] = int(samplecX.get('sample_rate'))
        if samplecX.get('off') != None:
            cut_start = (float(samplecX.get('off'))/12)*-1
            if cut_start != 0: placeJ['cut'] = {'type': 'cut', 'start': cut_start, 'end': cut_start+placeJ["duration"]}
        audioplacements.append(placeJ)
    print('['+str(printcountplace)+'] ')
    return audioplacements

# ------- Track: audio -------

def lmms_decode_audio_track(trkX, trackid):
    cvpj_name = trkX.get('name')
    trkX_audiotr = trkX.findall('sampletrack')[0]

    cvpj_pan = float(lmms_auto_getvalue(trkX_audiotr, 'pan', 0, 'float', [0, 0.01], ['track', trackid, 'pan']))
    cvpj_vol = float(lmms_auto_getvalue(trkX_audiotr, 'vol', 100, 'float', [0, 0.01], ['track', trackid, 'vol']))
    cvpj_enabled = int(lmms_auto_getvalue(trkX, 'muted', 1, 'bool', [-1, -1] ,['track', trackid, 'enabled']))
    cvpj_solo = int(trkX.get('solo'))

    tracks_r.track_create(cvpj_l, trackid, 'audio')
    tracks_r.track_visual(cvpj_l, trackid, name=cvpj_name)

    tracks_r.track_param_add(cvpj_l, trackid, 'vol', cvpj_vol, 'float')
    tracks_r.track_param_add(cvpj_l, trackid, 'pan', cvpj_pan, 'float')
    tracks_r.track_param_add(cvpj_l, trackid, 'enabled', cvpj_enabled, 'bool')
    tracks_r.track_param_add(cvpj_l, trackid, 'solo', cvpj_solo, 'bool')

    print('[input-lmms] Audio Track')
    print('[input-lmms]       Name: ' + cvpj_name)

    xml_fxch = trkX_audiotr.get('fxch')
    if xml_fxch != None: tracks_r.track_fxrackchan_add(cvpj_l, trackid, int(xml_fxch))
    xml_a_fxchain = trkX_audiotr.findall('fxchain')
    if len(xml_a_fxchain) != 0: 
        fxslot.insert(cvpj_l, ['track', trackid], 'audio', lmms_decode_fxchain(xml_a_fxchain[0]))
    print('[input-lmms]')
    tracks_r.add_pl(cvpj_l, trackid, 'audio', lmms_decode_audioplacements(trkX))

# ------- Track: Automation -------

def lmms_decode_autopattern(pointsX):
    autopoints = []
    printcountpat = 0
    for pointX in pointsX:
        pointJ = {}
        pointJ["position"] = float(pointX.get('pos')) / 12
        pointJ["value"] = float(pointX.get('value'))
        printcountpat += 1
        autopoints.append(pointJ)
    print('['+str(printcountpat), end='] ')
    return autopoints

def lmms_decode_autoplacements(trkX):
    autoplacements = []
    autopatsX = trkX.findall('automationpattern')
    printcountplace = 0
    print('[input-lmms]       Auto Placements: ', end='')
    for autopatX in autopatsX:
        placeJ = {}
        placeJ["position"] = float(autopatX.get('pos')) / 12
        placeJ["duration"] = float(autopatX.get('len')) / 12
        pointsX = autopatX.findall('time')
        pointsJ = lmms_decode_autopattern(pointsX)
        placeJ["points"] = pointsJ
        autoobjectX = autopatX.findall('object')
        if len(autoobjectX) != 0:
            internal_id = autoobjectX[0].get('id')
            auto_id.in_add_pl(str(autoobjectX[0].get('id')), placeJ)
    print(' ')

def lmms_decode_auto_track(trkX):
    lmms_decode_autoplacements(trkX)

# ------- Effects -------

def get_ladspa_path(ladname):
    if lmms_ladspapath != None: temppath = lmms_ladspapath+ladname
    else: temppath = ladname

    if sys.platform == 'win32': 
        unixsys = False
        temppath += '.dll'
    else: 
        unixsys = True
        temppath += '.so'

    if os.path.exists(temppath) == True:
        return temppath
    elif unixsys == True:
        pathlist = []
        pathlist.append('/usr/lib/ladspa/'+ladname+'.so')
        pathlist.append('/usr/lib/x86_64-linux-gnu/lmms/ladspa/'+ladname+'.so')
        for path in pathlist:
            if os.path.exists(path) == True:
                return path
    elif unixsys == False:
        pathlist = []
        pathlist.append('C:\\Program Files\\LMMS\\plugins\\ladspa\\'+ladname+'.dll')
        for path in pathlist:
            if os.path.exists(path) == True:
                return path
    else:
        return ladname

def lmms_decode_effectslot(fxslotX):
    fxpluginname = fxslotX.get('name')

    pluginid = plugins.get_id()

    if fxpluginname == 'eq':
        fxxml_plugin = fxslotX.findall('Eq')[0]

        fx_plugindata = plugins.cvpj_plugin('deftype', 'universal', 'eq-bands')

        Outputgain = lmms_auto_getvalue(fxxml_plugin, 'Outputgain', 0, 'float', None, ['slot', pluginid, 'gain_out'])
        Inputgain = lmms_auto_getvalue(fxxml_plugin, 'Inputgain', 0, 'float', None, ['slot', pluginid, 'gain_in'])

        fx_plugindata.param_add('gain_out', Outputgain, 'float', 'Out Gain')
        fx_plugindata.param_add('gain_in', Inputgain, 'float', 'In Gain')

        LPactive = lmms_auto_getvalue(fxxml_plugin, 'LPactive', 0, 'int', None, ['slot', pluginid, 'peak_1_on'])
        LPfreq   = lmms_auto_getvalue(fxxml_plugin, 'LPfreq', 0, 'float', None,   ['slot', pluginid, 'peak_1_freq'])
        LPres    = lmms_auto_getvalue(fxxml_plugin, 'LPres', 0, 'float', None,    ['slot', pluginid, 'peak_1_val'])
        fx_plugindata.eqband_add(LPactive, LPfreq, 0, 'low_pass', LPres, None)

        Lowshelfactive = lmms_auto_getvalue(fxxml_plugin, 'Lowshelfactive', 0, 'int', None, ['slot', pluginid, 'peak_2_on'])
        LowShelffreq   = lmms_auto_getvalue(fxxml_plugin, 'LowShelffreq', 0, 'float', None,   ['slot', pluginid, 'peak_2_freq'])
        Lowshelfgain   = lmms_auto_getvalue(fxxml_plugin, 'Lowshelfgain', 0, 'float', None,   ['slot', pluginid, 'peak_2_gain'])
        LowShelfres    = lmms_auto_getvalue(fxxml_plugin, 'LowShelfres', 0, 'float', None,    ['slot', pluginid, 'peak_2_val'])
        fx_plugindata.eqband_add(Lowshelfactive, LowShelffreq, Lowshelfgain, 'low_shelf', LowShelfres, None)

        Peak1active = lmms_auto_getvalue(fxxml_plugin, 'Peak1active', 0, 'int', None, ['slot', pluginid, 'peak_3_on'])
        Peak1bw     = lmms_auto_getvalue(fxxml_plugin, 'Peak1bw', 0, 'float', None,     ['slot', pluginid, 'peak_3_val'])
        Peak1freq   = lmms_auto_getvalue(fxxml_plugin, 'Peak1freq', 0, 'float', None,   ['slot', pluginid, 'peak_3_freq'])
        Peak1gain   = lmms_auto_getvalue(fxxml_plugin, 'Peak1gain', 0, 'float', None,   ['slot', pluginid, 'peak_3_gain'])
        fx_plugindata.eqband_add(Peak1active, Peak1freq, Peak1gain, 'peak', Peak1bw, None)

        Peak2active = lmms_auto_getvalue(fxxml_plugin, 'Peak2active', 0, 'int', None, ['slot', pluginid, 'peak_4_on'])
        Peak2bw     = lmms_auto_getvalue(fxxml_plugin, 'Peak2bw', 0, 'float', None,     ['slot', pluginid, 'peak_4_val'])
        Peak2freq   = lmms_auto_getvalue(fxxml_plugin, 'Peak2freq', 0, 'float', None,   ['slot', pluginid, 'peak_4_freq'])
        Peak2gain   = lmms_auto_getvalue(fxxml_plugin, 'Peak2gain', 0, 'float', None,   ['slot', pluginid, 'peak_4_gain'])
        fx_plugindata.eqband_add(Peak2active, Peak2freq, Peak2gain, 'peak', Peak2bw, None)

        Peak3active = lmms_auto_getvalue(fxxml_plugin, 'Peak3active', 0, 'int', None, ['slot', pluginid, 'peak_5_on'])
        Peak3bw     = lmms_auto_getvalue(fxxml_plugin, 'Peak3bw', 0, 'float', None,     ['slot', pluginid, 'peak_5_val'])
        Peak3freq   = lmms_auto_getvalue(fxxml_plugin, 'Peak3freq', 0, 'float', None,   ['slot', pluginid, 'peak_5_freq'])
        Peak3gain   = lmms_auto_getvalue(fxxml_plugin, 'Peak3gain', 0, 'float', None,   ['slot', pluginid, 'peak_5_gain'])
        fx_plugindata.eqband_add(Peak3active, Peak3freq, Peak3gain, 'peak', Peak3bw, None)

        Peak4active = lmms_auto_getvalue(fxxml_plugin, 'Peak4active', 0, 'int', None, ['slot', pluginid, 'peak_6_on'])
        Peak4bw     = lmms_auto_getvalue(fxxml_plugin, 'Peak4bw', 0, 'float', None,     ['slot', pluginid, 'peak_6_val'])
        Peak4freq   = lmms_auto_getvalue(fxxml_plugin, 'Peak4freq', 0, 'float', None,   ['slot', pluginid, 'peak_6_freq'])
        Peak4gain   = lmms_auto_getvalue(fxxml_plugin, 'Peak4gain', 0, 'float', None,   ['slot', pluginid, 'peak_6_gain'])
        fx_plugindata.eqband_add(Peak4active, Peak4freq, Peak4gain, 'peak', Peak4bw, None)

        Highshelfactive = lmms_auto_getvalue(fxxml_plugin, 'Highshelfactive', 0, 'int', None, ['slot', pluginid, 'peak_7_on'])
        Highshelffreq   = lmms_auto_getvalue(fxxml_plugin, 'Highshelffreq', 0, 'float', None,   ['slot', pluginid, 'peak_7_freq'])
        HighShelfgain   = lmms_auto_getvalue(fxxml_plugin, 'HighShelfgain', 0, 'float', None,   ['slot', pluginid, 'peak_7_gain'])
        HighShelfres    = lmms_auto_getvalue(fxxml_plugin, 'HighShelfres', 0, 'float', None,    ['slot', pluginid, 'peak_7_val'])
        fx_plugindata.eqband_add(Highshelfactive, Highshelffreq, HighShelfgain, 'high_shelf', HighShelfres, None)

        HPactive = lmms_auto_getvalue(fxxml_plugin, 'HPactive', 0, 'int', None, ['slot', pluginid, 'peak_8_on'])
        HPfreq   = lmms_auto_getvalue(fxxml_plugin, 'HPfreq', 0, 'float', None,   ['slot', pluginid, 'peak_8_freq'])
        HPres    = lmms_auto_getvalue(fxxml_plugin, 'HPres', 0, 'float', None,    ['slot', pluginid, 'peak_8_val'])
        fx_plugindata.eqband_add(HPactive, HPfreq, 0, 'high_pass', HPres, None)

    elif fxpluginname == 'vsteffect':
        fxxml_plugin = fxslotX.findall(fxlist[fxpluginname])[0]
        print('[vst2-dll',end='] ')
        fx_plugindata = plugins.cvpj_plugin('deftype', 'vst2', 'win')
        getvstparams(fx_plugindata, pluginid, fxxml_plugin)

    elif fxpluginname == 'ladspaeffect':
        fxxml_plugin = fxslotX.findall('ladspacontrols')[0]
        print('[ladspa',end='] ')
        fxxml_plugin_key = fxslotX.findall('key')[0]
        fxxml_plugin_ladspacontrols = fxslotX.findall('ladspacontrols')[0]

        fx_plugindata = plugins.cvpj_plugin('deftype', 'ladspa', None)

        for attribute in fxxml_plugin_key.findall('attribute'):
            attval = attribute.get('value')
            attname = attribute.get('name')
            if attname == 'file':
                if os.path.exists(attval): 
                    fx_plugindata.dataval_add('name', attval)
                    fx_plugindata.dataval_add('path', attval)
                else: 
                    fx_plugindata.dataval_add('name', attval)
                    fx_plugindata.dataval_add('path', get_ladspa_path(attval))
            if attname == 'plugin': 
                fx_plugindata.dataval_add('plugin', attval)

        ladspa_ports = int(fxxml_plugin_ladspacontrols.get('ports'))
        ladspa_linked = fxxml_plugin_ladspacontrols.get('link')
        seperated_channels = False

        if ladspa_linked != None: 
            ladspa_ports //= 2
            if ladspa_linked == "0": seperated_channels = True

        fx_plugindata.dataval_add('numparams', ladspa_ports)

        for node in fxxml_plugin_ladspacontrols.iter():
            notetagtxt = node.tag
            if notetagtxt.startswith('port'):
                l_ch = notetagtxt[4]
                l_val = notetagtxt[5:]
                t_data = node.get('data')
                paramid = 'ladspa_param_'+l_val if l_ch == '0' else 'ladspa_param_'+l_val+'_'+l_ch
                paramval = float(lmms_auto_getvalue(node, 'data', '0', 'float', None, ['plugin', pluginid, paramid]))
                fx_plugindata.param_add(paramid, paramval, 'float', paramid)
        fx_plugindata.dataval_add('seperated_channels', seperated_channels)
        
    else:
        fxxml_plugin = fxslotX.findall(fxlist[fxpluginname])[0]
        print('['+fxpluginname,end='] ')
        fx_plugindata = plugins.cvpj_plugin('deftype', 'native-lmms', fxpluginname)
        dset_plugparams(fxpluginname, pluginid, fxxml_plugin, fx_plugindata)

    fxenabled = lmms_auto_getvalue(fxslotX, 'on', 1, 'bool', None, ['slot', pluginid, 'enabled'])
    fxwet = lmms_auto_getvalue(fxslotX, 'wet', 1, 'float', None, ['slot', pluginid, 'wet'])

    fx_plugindata.fxdata_add(fxenabled, fxwet)
    fx_plugindata.to_cvpj(cvpj_l, pluginid)

    return pluginid

def lmms_decode_fxchain(fxchainX):
    print('[input-lmms]       Audio FX Chain: ',end='')
    fxchain = []
    fxslotsX = fxchainX.findall('effect')
    for fxslotX in fxslotsX:
        fxslotJ = lmms_decode_effectslot(fxslotX)
        if fxslotJ != None: fxchain.append(fxslotJ)
    print('')
    return fxchain

def lmms_decode_fxmixer(cvpj_l, fxX):
    fxlist = {}
    for fxcX in fxX:
        fx_name = fxcX.get('name')
        fx_num = fxcX.get('num')
        print('[input-lmms] FX ' + fx_num)
        print('[input-lmms]       Name: ' + fx_name)
        fxc_vol = float(lmms_auto_getvalue(fxcX, 'volume', 1, 'float', None, ['fxmixer', fx_num, 'vol']))
        fxrack.add(cvpj_l, fx_num, fxc_vol, 0, name=fx_name)

        fxc_enabled = True
        if fxcX.get('muted') != None: fxc_enabled = not int(fxcX.get('muted'))
        fxrack.param_add(cvpj_l, fx_num, 'enabled', fxc_enabled, 'bool')

        fxchainX = fxcX.find('fxchain')
        if fxchainX != None:
            fxrack.param_add(cvpj_l, fx_num, 'fx_enabled', bool(int(fxchainX.get('enabled'))), 'bool')
            fxslotids = lmms_decode_fxchain(fxchainX)
            for fxslotid in fxslotids:
                fxslot.insert(cvpj_l, ['fxrack', fx_num], 'audio', fxslotid)

        sendsxml = fxcX.findall('send')
        for sendxml in sendsxml:
            send_id = get_send_auto_id()
            fx_to_num = int(sendxml.get('channel'))
            fx_amount = lmms_auto_getvalue(sendxml, 'amount', 1, 'float', None, ['send', send_id, 'amount'])
            fxrack.addsend(cvpj_l, fx_num, fx_to_num, fx_amount, send_id)
        print('[input-lmms]')

    return fxlist

# ------- Main -------

def lmms_decode_tracks(trksX):
    idtracknum = 0
    for trkX in trksX:
        idtracknum += 1
        tracktype = trkX.get('type')
        if tracktype == "0": lmms_decode_inst_track(trkX, 'LMMS_Inst_'+str(idtracknum))
        if tracktype == "2": lmms_decode_audio_track(trkX, 'LMMS_Audio_'+str(idtracknum))
        if tracktype == "5": lmms_decode_auto_track(trkX)

class input_lmms(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'lmms'
    def getname(self): return 'LMMS'
    def gettype(self): return 'r'
    def getdawcapabilities(self): 
        return {
        'fxrack': True,
        'fxrack_params': ['enabled','vol']
        }
    def supported_autodetect(self): return True
    def detect(self, input_file):
        try:
            root = get_xml_tree(input_file)
            if root.tag == "lmms-project": output = True
            else: output = False
        except ET.ParseError: output = False
        return output
    def parse(self, input_file, extra_param):
        print('[input-lmms] Input Start')
        global lmms_vstpath
        global lmms_ladspapath
        global dataset
        global cvpj_l

        cvpj_l = {}
        homepath = os.path.expanduser('~')
        lmmsconfigpath_win = homepath+'\\.lmmsrc.xml'
        lmmsconfigpath_unx = homepath+'/.lmmsrc.xml'
        lmmsconfigpath_found = False

        if os.path.exists(lmmsconfigpath_win):
            lmmsconfigpath = lmmsconfigpath_win
            lmmsconfigpath_found = True
        if os.path.exists(lmmsconfigpath_unx):
            lmmsconfigpath = lmmsconfigpath_unx
            lmmsconfigpath_found = True

        try:
            if lmmsconfigpath_found == True:
                lmmsconfX = ET.parse(lmmsconfigpath).getroot()
                lmmsconf_pathsX = lmmsconfX.findall('paths')[0]
                lmms_vstpath = lmmsconf_pathsX.get('vstdir')
                lmms_ladspapath = lmmsconf_pathsX.get('ladspadir')
            else: 
                lmms_vstpath = ''
                lmms_ladspapath = ''
        except: 
            lmms_vstpath = ''
            lmms_ladspapath = ''


        dataset = data_dataset.dataset('./data_dset/lmms.dset')

        tree = get_xml_tree(input_file)
        headX = tree.findall('head')[0]
        songX = tree.findall('song')[0]
        trkscX = songX.findall('trackcontainer')
        if len(trkscX): add_window_data(trkscX[0], cvpj_l, 'main', 'tracklist')
        trksX = trkscX[0].findall('track')
        fxmixerX = songX.findall('fxmixer')
        if len(fxmixerX): add_window_data(fxmixerX[0], cvpj_l, 'main', 'fxmixer')
        fxX = fxmixerX[0].findall('fxchannel')

        tlX = songX.find('timeline')

        cvpj_bpm = float(lmms_auto_getvalue(headX, 'bpm', 140, 'float', None, ['main', 'bpm']))
        cvpj_vol = float(lmms_auto_getvalue(headX, 'mastervol', 100, 'float', [0, 0.01], ['main', 'vol']))
        cvpj_pitch = float(lmms_auto_getvalue(headX, 'masterpitch', 0, 'float', None, ['main', 'pitch']))
        timesig_numerator = lmms_auto_getvalue(headX, 'timesig_numerator', 4, 'int', None, None)
        timesig_denominator = lmms_auto_getvalue(headX, 'timesig_denominator', 4, 'int', None, None)

        song.add_timesig(cvpj_l, timesig_numerator, timesig_denominator)

        song.add_param(cvpj_l, 'bpm', cvpj_bpm)
        song.add_param(cvpj_l, 'vol', cvpj_vol)
        song.add_param(cvpj_l, 'pitch', cvpj_pitch)

        projnotesX = songX.findall('projectnotes')

        lmms_decode_tracks(trksX)
        lmms_decode_fxmixer(cvpj_l, fxX)

        trackdata = cvpj_l['track_data'] if 'track_data' in cvpj_l else {}

        auto_id.in_output(cvpj_l)

        X_controllerrackview = songX.findall('ControllerRackView')
        if len(X_controllerrackview): add_window_data(X_controllerrackview[0], cvpj_l, 'main', 'controller_rack_view')

        X_pianoroll = songX.findall('pianoroll')
        if len(X_pianoroll): add_window_data(X_pianoroll[0], cvpj_l, 'main', 'piano_roll')

        X_automationeditor = songX.findall('automationeditor')
        if len(X_automationeditor): add_window_data(X_automationeditor[0], cvpj_l, 'main', 'automation_editor')

        if len(projnotesX): 
            song.add_info_msg(cvpj_l, 'html', projnotesX[0].text)
            add_window_data(projnotesX[0], cvpj_l, 'main', 'project_notes')

        return json.dumps(cvpj_l, indent=2)
        
def get_xml_tree(path):
    with open(path, 'rb') as file:
        try:
            file.seek(4)
            data = zlib.decompress(file.read())
            return ET.fromstring(data)

        except zlib.error:
            return ET.parse(path).getroot()