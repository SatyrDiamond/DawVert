# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import base64
import json
import math
import plugin_input
import os
import zlib
import sys
import xml.etree.ElementTree as ET
from functions_plugin import lmms_auto
from functions import note_mod
from functions import note_data
from functions import notelist_data
from functions import colors
from functions import auto
from functions import plugins
from functions import song
from functions import tracks

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
['_perc', '_perc_env'],
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

plugincolors = {}
plugincolors['audiofileprocessor'] = [0.28, 0.28, 0.28]
plugincolors['bitinvader'] = [0.86, 0.86, 0.86]
plugincolors['papu'] = [0.60, 0.80, 0.14]
plugincolors['gigplayer'] = [0.55, 0.00, 0.00]
plugincolors['kicker'] = [0.51, 0.58, 0.58]
plugincolors['lb302'] = [0.81, 0.65, 0.72]
plugincolors['malletsstk'] = [0.55, 0.13, 0.07]
plugincolors['monstro'] = [0.65, 0.68, 0.70]
plugincolors['nes'] = [0.90, 0.13, 0.09]
plugincolors['OPL2'] = [0.03, 0.33, 0.53]
plugincolors['organic'] = [0.24, 0.76, 0.13]
plugincolors['patman'] = [0.97, 1.00, 0.33]
plugincolors['sf2player'] = [0.60, 0.61, 0.62]
plugincolors['sfxr'] = [1.00, 0.70, 0.00]
plugincolors['sid'] = [0.73, 0.69, 0.63]
plugincolors['tripleoscillator'] = [1.00, 0.34, 0.13]
plugincolors['vestige'] = [0.06, 0.60, 0.21]
plugincolors['vibedstrings'] = [0.39, 0.47, 0.53]
plugincolors['watsyn'] = [0.81, 0.87, 0.87]
plugincolors['zynaddsubfx'] = [0.75, 0.75, 0.75]

# ------- functions -------


send_auto_id = 1000
def get_send_auto_id():
    global send_auto_id
    send_auto_id += 1
    return 'send'+str(send_auto_id)



def getvstparams(pluginid, xmldata):
    if os.path.exists( xmldata.get('plugin')):
        plugins.add_plug_data(cvpj_l, pluginid, 'path', xmldata.get('plugin'))
    else:
        plugins.add_plug_data(cvpj_l, pluginid, 'path', lmms_vstpath+xmldata.get('plugin'))
    vst_data = xmldata.get('chunk')
    vst_numparams = xmldata.get('numparams')
    vst_program = xmldata.get('program')
    if vst_program != None: 
        plugins.add_plug_data(cvpj_l, pluginid, 'current_program', int(vst_program))
    if vst_data != None:
        plugins.add_plug_data(cvpj_l, pluginid, 'datatype', 'chunk')
        plugins.add_plug_data(cvpj_l, pluginid, 'chunk', vst_data)
    elif vst_numparams != None:
        plugins.add_plug_data(cvpj_l, pluginid, 'datatype', 'param')
        plugins.add_plug_data(cvpj_l, pluginid, 'numparams', int(vst_numparams))
        for param in range(int(vst_numparams)):
            paramdata = xmldata.get('param'+str(param)).split(':')
            paramnum = 'vst_param_'+str(param)
            plugins.add_plug_param(cvpj_l, pluginid, paramnum, float(paramdata[-1]), 'float', paramdata[1])
    for node in xmldata.iter():
        notetagtxt = node.tag
        if notetagtxt.startswith('param'):
            value = node.get('value')
            if value != None:
                tracks.autoid_in_define(str(node.get('id')), ['plugin', pluginid, 'vst_param_'+notetagtxt[5:]], 'float', None)

def hundredto1(lmms_input): return float(lmms_input) * 0.01

def lmms_auto_getvalue(x_tag, x_name, i_fbv, i_type, i_addmul, i_loc):
    if x_tag.get(x_name) != None: 
        if i_type == 'float': return float(x_tag.get(x_name))
        if i_type == 'int': return int(x_tag.get(x_name))
        if i_type == 'bool': return int(bool(x_tag.get(x_name)))
    elif x_tag.findall(x_name) != []: 
        realvaluetag = x_tag.findall(x_name)[0]
        value = realvaluetag.get('value')
        if value != None:
            tracks.autoid_in_define(str(realvaluetag.get('id')), i_loc, i_type, i_addmul)
            if i_type == 'float': return float(realvaluetag.get('value'))
            if i_type == 'int': return int(realvaluetag.get('value'))
            if i_type == 'bool': return int(bool(realvaluetag.get('value')))
    else: 
        return i_fbv

def lmms_getvalue_int(json_name, xml_in): 
    if xml_in != None: json_in[json_name] = int(xml_in)
def lmms_getvalue_float(json_name, xml_in): 
    if xml_in != None: json_in[json_name] = float(xml_in)
def lmms_getvalue_100(json_name, xml_in): 
    if xml_in != None: json_in[json_name] = hundredto1(float(xml_in))
def lmms_getvalue_exp(json_name, xml_in): 
    if xml_in != None: json_in[json_name] = exp2sec(float(xml_in))


def lmms_getvalue(xmltag, xmlname, fallbackval): 
    xmlval = xmltag.get(xmlname)
    if xmlval != None: return xmlval
    else: return fallbackval

# ------- Instruments and Plugins -------

def exp2sec(value): return (value*value)*5

def asdflfo_get(trkX_insttr, pluginid):
    elcX = trkX_insttr.findall('eldata')
    if len(elcX) != 0:
        eldataX = elcX[0]
        if eldataX.findall('elvol'): asdflfo(pluginid, eldataX.findall('elvol')[0], 'vol')
        if eldataX.findall('elcut'): asdflfo(pluginid, eldataX.findall('elcut')[0], 'cutoff')
        if eldataX.findall('elres'): asdflfo(pluginid, eldataX.findall('elres')[0], 'reso')

        if eldataX.get('ftype') != None: 
            filter_cutoff = float(lmms_getvalue(eldataX, 'fcut', 0))
            filter_reso = float(lmms_getvalue(eldataX, 'fres', 0))
            filter_enabled = float(lmms_getvalue(eldataX, 'fwet', 0))
            filter_type, filter_subtype = filtertype[int(eldataX.get('ftype'))]
            plugins.add_filter(cvpj_l, pluginid, 
                filter_enabled, filter_cutoff, filter_reso, 
                filter_type, filter_subtype)

def asdflfo(pluginid, xmlO, asdrtype):
    envelopeparams = {}

    asdr_predelay = exp2sec(float(lmms_getvalue(xmlO, 'pdel', 0)))
    asdr_attack = exp2sec(float(lmms_getvalue(xmlO, 'att', 0)))
    asdr_hold = exp2sec(float(lmms_getvalue(xmlO, 'hold', 0)))
    asdr_decay = exp2sec(float(lmms_getvalue(xmlO, 'dec', 0)))
    asdr_sustain = float(lmms_getvalue(xmlO, 'sustain', 1))
    asdr_release = exp2sec(float(lmms_getvalue(xmlO, 'rel', 0)))
    asdr_amount = float(lmms_getvalue(xmlO, 'amt', 0))
    if asdrtype == 'cutoff': asdr_amount *= 6000

    plugins.add_asdr_env(cvpj_l, pluginid, asdrtype, 
        asdr_predelay, asdr_attack, asdr_hold, asdr_decay, asdr_sustain, asdr_release, asdr_amount)

    lfoparams = {}

    speedx100 = xmlO.get('x100')
    if speedx100 != None: speedx100 = int(speedx100)
    else: speedx100 = 0

    lfo_predelay = float(lmms_getvalue(xmlO, 'pdel', 0))
    lfo_attack = exp2sec(float(lmms_getvalue(xmlO, 'latt', 0)))
    lfo_amount = float(lmms_getvalue(xmlO, 'lamt', 0))
    lfo_shape = lfoshape[int(lmms_getvalue(xmlO, 'lamt', 0))]
    if asdrtype == 'cutoff': lfo_amount *= 6000

    lfo_speed = 0
    if xmlO.get('lspd') != None: 
        if speedx100 == 1: lfo_speed = float(xmlO.get('lspd')) * 0.2
        else: lfo_speed = float(xmlO.get('lspd')) * 20

    plugins.add_lfo(cvpj_l, pluginid, asdrtype, 
        lfo_shape, 'seconds', lfo_speed, lfo_predelay, lfo_attack, lfo_amount)

def lmms_decodeplugin(trkX_insttr, cvpj_l_inst):
    trkX_instrument = trkX_insttr.findall('instrument')[0]
    pluginname = trkX_instrument.get('name')

    out_color = None

    xml_a_plugin = trkX_instrument.findall(pluginname)
    if len(xml_a_plugin) != 0: 
        xml_plugin = xml_a_plugin[0]

        pluginid = plugins.get_id()
        cvpj_l_inst['pluginid'] = pluginid

        if pluginname == "sf2player":
            plugins.add_plug(cvpj_l, pluginid, 'soundfont2', None)
            plugins.add_plug_data(cvpj_l, pluginid, 'bank', int(xml_plugin.get('bank')))
            plugins.add_plug_data(cvpj_l, pluginid, 'patch', int(xml_plugin.get('patch')))
            plugins.add_plug_data(cvpj_l, pluginid, 'file', xml_plugin.get('src'))
            plugins.add_plug_param(cvpj_l, pluginid, 'gain', float(xml_plugin.get('gain')), 'float', 'Gain')
            plugins.add_plug_param(cvpj_l, pluginid, 'chorus_depth', float(xml_plugin.get('chorusDepth')), 'float', 'chorusDepth')
            plugins.add_plug_param(cvpj_l, pluginid, 'chorus_level', float(xml_plugin.get('chorusLevel')), 'float', 'chorusLevel')
            plugins.add_plug_param(cvpj_l, pluginid, 'chorus_lines', float(xml_plugin.get('chorusNum')), 'float', 'chorusNum')
            plugins.add_plug_param(cvpj_l, pluginid, 'chorus_enabled', float(xml_plugin.get('chorusOn')), 'bool', 'chorusOn')
            plugins.add_plug_param(cvpj_l, pluginid, 'chorus_speed', float(xml_plugin.get('chorusSpeed')), 'float', 'chorusSpeed')
            plugins.add_plug_param(cvpj_l, pluginid, 'reverb_damping', float(xml_plugin.get('reverbDamping')), 'float', 'reverbDamping')
            plugins.add_plug_param(cvpj_l, pluginid, 'reverb_level', float(xml_plugin.get('reverbLevel')), 'float', 'reverbLevel')
            plugins.add_plug_param(cvpj_l, pluginid, 'reverb_enabled', float(xml_plugin.get('reverbOn')), 'bool', 'reverbOn')
            plugins.add_plug_param(cvpj_l, pluginid, 'reverb_roomsize', float(xml_plugin.get('reverbRoomSize')), 'float', 'reverbRoomSize')
            plugins.add_plug_param(cvpj_l, pluginid, 'reverb_width', float(xml_plugin.get('reverbWidth')), 'float', 'reverbWidth')

        elif pluginname == "audiofileprocessor":
            plugins.add_plug_sampler_singlefile(cvpj_l, pluginid, lmms_getvalue(xml_plugin, 'src', ''))
            plugins.add_plug_data(cvpj_l, pluginid, 'reverse', bool(int(lmms_getvalue(xml_plugin, 'reversed', 0))))
            plugins.add_plug_data(cvpj_l, pluginid, 'amp', float(lmms_getvalue(xml_plugin, 'amp', 1))/100)
            plugins.add_plug_data(cvpj_l, pluginid, 'continueacrossnotes', bool(int(lmms_getvalue(xml_plugin, 'stutter', 0))))
            plugins.add_plug_data(cvpj_l, pluginid, 'trigger', 'normal')
            plugins.add_plug_data(cvpj_l, pluginid, 'point_value_type', "percent")

            cvpj_loop = {}
            looped = int(xml_plugin.get('looped'))
            if looped == 0: cvpj_loop = {'enabled': 0}
            if looped == 1: cvpj_loop = {'enabled': 1, 'mode': "normal"}
            if looped == 2: cvpj_loop = {'enabled': 1, 'mode': "pingpong"}
            cvpj_loop['points'] = [float(xml_plugin.get('lframe')), float(xml_plugin.get('eframe'))]
            plugins.add_plug_data(cvpj_l, pluginid, 'loop', cvpj_loop)
            plugins.add_plug_data(cvpj_l, pluginid, 'end', float(lmms_getvalue(xml_plugin, 'eframe', 1)))
            plugins.add_plug_data(cvpj_l, pluginid, 'start', float(lmms_getvalue(xml_plugin, 'sframe', 0)))
            plugins.add_plug_data(cvpj_l, pluginid, 'point_value_type', "percent")

            lmms_interpolation = int(xml_plugin.get('interp'))
            if lmms_interpolation == 0: cvpj_interpolation = "none"
            if lmms_interpolation == 1: cvpj_interpolation = "linear"
            if lmms_interpolation == 2: cvpj_interpolation = "sinc"
            plugins.add_plug_data(cvpj_l, pluginid, 'interpolation', cvpj_interpolation)

            asdflfo_get(trkX_insttr, pluginid)


        elif pluginname == "OPL2" or pluginname == "opulenz":
            plugins.add_plug(cvpj_l, pluginid, 'fm', 'opl2')
            for opnum in range(2):
                opl2_optxt = 'op'+str(opnum+1)
                for varname in opl2opvarnames:
                    plugins.add_plug_param(cvpj_l, pluginid, opl2_optxt+varname[1], 
                    lmms_auto_getvalue(xml_plugin, opl2_optxt+varname[0], 0, 'int', None, 
                        ['plugin', pluginid, opl2_optxt+varname[1]]), 
                    'int', opl2_optxt+varname[1])
                
            for varname in opl2varnames:
                plugins.add_plug_param(cvpj_l, pluginid, varname[1], 
                lmms_auto_getvalue(xml_plugin, varname[0], 0, 'int', None, 
                    ['plugin', pluginid, varname[1]]), 
                'int', varname[1])

        elif pluginname == "vestige":
            plugins.add_plug(cvpj_l, pluginid, 'vst2', 'win')
            getvstparams(pluginid, xml_plugin)

        else:
            plugins.add_plug(cvpj_l, pluginid, 'native-lmms', pluginname)
            lmms_autovals = lmms_auto.get_params_inst(pluginname)
            for pluginparam in lmms_autovals[0]:
                plugins.add_plug_param(cvpj_l, pluginid, pluginparam, 
                lmms_auto_getvalue(xml_plugin, pluginparam, 0, 'float', None, 
                    ['plugin', pluginid, pluginparam]), 
                'float', pluginparam)
            for pluginparam in lmms_autovals[1]:
                xml_pluginparam = xml_plugin.get(pluginparam)
                if xml_pluginparam: 
                    plugins.add_plug_data(cvpj_l, pluginid, pluginparam, xml_pluginparam)
            asdflfo_get(trkX_insttr, pluginid)
            if pluginname == "zynaddsubfx":
                zdata = xml_plugin.findall('ZynAddSubFX-data')[0]
                plugins.add_plug_data(cvpj_l, pluginid, 'data', 
                    base64.b64encode(ET.tostring(zdata, encoding='utf-8')).decode('ascii')
                    )

    if pluginname in plugincolors: plugincolor = plugincolors[pluginname]
    else: plugincolor = None
    return plugincolor, pluginname

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
                        if prognum == 0: pointJ['type'] = 'instant'
                        else: pointJ['type'] = 'normal'
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
    cvpj_l_track_inst = {}

    cvpj_name = trkX.get('name')
    print('[input-lmms] Instrument Track')
    print('[input-lmms]       Name: ' + cvpj_name)

    tracks.r_create_inst(cvpj_l, trackid, cvpj_l_track_inst)

    tracks.r_param(cvpj_l, trackid, 'enabled', int( lmms_auto_getvalue(trkX, 'muted', 1, 'bool', [-1, -1] ,['track', trackid, 'enabled']) ))
    tracks.r_param(cvpj_l, trackid, 'solo', int(trkX.get('solo')))

    #trkX_insttr
    trkX_insttr = trkX.findall('instrumenttrack')[0]
    cvpj_pan = hundredto1(float(lmms_auto_getvalue(trkX_insttr, 'pan', 0, 'float', [0, 0.01], ['track', trackid, 'pan'])))
    cvpj_vol = hundredto1(float(lmms_auto_getvalue(trkX_insttr, 'vol', 1, 'float', [0, 0.01], ['track', trackid, 'vol'])))
    
    #midi
    xml_a_midiport = trkX_insttr.findall('midiport')
    if len(xml_a_midiport) != 0:
        midiJ = {}
        midi_outJ = {}
        midi_inJ = {}
        midiportX = trkX_insttr.findall('midiport')[0]
        midi_inJ['enabled'] = int(midiportX.get('readable'))
        if midiportX.get('inputchannel') != '0' and midiportX.get('inputchannel') != None: 
            midi_inJ['channel'] = int(midiportX.get('inputchannel'))
        if midiportX.get('fixedinputvelocity') != '-1' and midiportX.get('fixedinputvelocity') != None: 
            midi_inJ['fixedvelocity'] = int(midiportX.get('fixedinputvelocity'))+1
        midi_outJ['enabled'] = int(midiportX.get('writable'))
        midi_outJ['channel'] = int(midiportX.get('outputchannel'))
        if midiportX.get('outputprogram') != None: 
            midi_outJ['program'] = int(midiportX.get('outputprogram'))
        if midiportX.get('fixedoutputvelocity') != '-1' and midiportX.get('fixedoutputvelocity') != None: 
            midi_outJ['fixedvelocity'] = int(midiportX.get('fixedoutputvelocity'))+1
        if midiportX.get('fixedoutputnote') != '-1' and midiportX.get('fixedoutputnote') != None: 
            midi_outJ['fixednote'] = int(midiportX.get('fixedoutputnote'))+1
        midiJ['basevelocity'] = int(midiportX.get('basevelocity'))
        midiJ['out'] = midi_outJ
        midiJ['in'] = midi_inJ
        cvpj_l_track_inst['midi'] = midiJ

    xml_a_fxchain = trkX_insttr.findall('fxchain')
    if len(xml_a_fxchain) != 0: 
        tracks.insert_fxslot(cvpj_l, ['track', trackid], 'audio', lmms_decode_fxchain(xml_a_fxchain[0]))

    track_color, pluginname = lmms_decodeplugin(trkX_insttr, cvpj_l_track_inst)

    tracks.r_param(cvpj_l, trackid, 'fxrack_channel', int(trkX_insttr.get('fxch')))
    tracks.r_param_inst(cvpj_l, trackid, 'usemasterpitch', int(trkX_insttr.get('usemasterpitch')))
    tracks.r_param_inst(cvpj_l, trackid, 'pitch', float(lmms_auto_getvalue(trkX_insttr, 'pitch', 0, 'float', [0, 0.01], ['track', trackid, 'pitch'])))
    tracks.r_basicdata(cvpj_l, trackid, cvpj_name, track_color, cvpj_vol, cvpj_pan)

    if 'basenote' in trkX_insttr.attrib:
        basenote = int(trkX_insttr.get('basenote'))-57
        noteoffset = 0
        if pluginname == 'sampler': noteoffset = 3
        if pluginname == 'soundfont2': noteoffset = -12
        middlenote = basenote - noteoffset
        if middlenote != 0: cvpj_l_track_inst['middlenote'] = middlenote


    xml_a_arpeggiator = trkX_insttr.findall('arpeggiator')
    if len(xml_a_arpeggiator) != 0:
        trkX_arpeggiator = xml_a_arpeggiator[0]
        pluginid = plugins.get_id()
        lmms_autovals = lmms_auto.get_params_notefx('arpeggiator')

        plugins.add_plug(cvpj_l, pluginid, 'native-lmms', 'arpeggiator')
        cvpj_l_arpeggiator_enabled = lmms_auto_getvalue(trkX_arpeggiator, 'arp-enabled', 0, 'bool', None, ['slot', pluginid, 'enabled'])
        plugins.add_plug_fxdata(cvpj_l, pluginid, cvpj_l_arpeggiator_enabled, None)

        for pluginparam in lmms_autovals[0]:
            plugins.add_plug_param(cvpj_l, pluginid, pluginparam, 
                lmms_auto_getvalue(trkX_arpeggiator, pluginparam, 0, 'float', None, ['plugin', pluginid, pluginparam])
                , 'float', pluginparam)

        tracks.insert_fxslot(cvpj_l, ['track', trackid], 'notes', pluginid)


    xml_a_chordcreator = trkX_insttr.findall('chordcreator')
    if len(xml_a_chordcreator) != 0:
        trkX_chordcreator = xml_a_chordcreator[0]
        pluginid = plugins.get_id()
        lmms_autovals = lmms_auto.get_params_notefx('chordcreator')

        plugins.add_plug(cvpj_l, pluginid, 'native-lmms', 'chordcreator')
        cvpj_l_chordcreator_enabled = lmms_auto_getvalue(trkX_arpeggiator, 'chord-enabled', 0, 'bool', None, ['slot', pluginid, 'enabled'])
        plugins.add_plug_fxdata(cvpj_l, pluginid, cvpj_l_chordcreator_enabled, None)

        for pluginparam in lmms_autovals[0]:
            plugins.add_plug_param(cvpj_l, pluginid, pluginparam, 
                lmms_auto_getvalue(trkX_chordcreator, pluginparam, 0, 'float', None, ['plugin', pluginid, pluginparam])
                , 'float', pluginparam)

        tracks.insert_fxslot(cvpj_l, ['track', trackid], 'notes', pluginid)


    tracks.r_pl_notes(cvpj_l, trackid, lmms_decode_nlplacements(trkX))

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
    tracks.r_create_audio(cvpj_l, trackid, None)
    cvpj_name = trkX.get('name')
    print('[input-lmms] Audio Track')
    print('[input-lmms]       Name: ' + cvpj_name)
    trkX_audiotr = trkX.findall('sampletrack')[0]
    cvpj_pan = hundredto1(float(lmms_auto_getvalue(trkX_audiotr, 'pan', 0, 'float', [0, 0.01], ['track', trackid, 'pan'])))
    cvpj_vol = hundredto1(float(lmms_auto_getvalue(trkX_audiotr, 'vol', 1, 'float', [0, 0.01], ['track', trackid, 'vol'])))
    tracks.r_basicdata(cvpj_l, trackid, cvpj_name, None, cvpj_vol, cvpj_pan)
    xml_fxch = trkX_audiotr.get('fxch')
    if xml_fxch != None: tracks.r_param(cvpj_l, trackid, 'fxrack_channel', int(xml_fxch))
    xml_a_fxchain = trkX_audiotr.findall('fxchain')
    if len(xml_a_fxchain) != 0: 
        tracks.insert_fxslot(cvpj_l, ['track', trackid], 'audio', lmms_decode_fxchain(xml_a_fxchain[0]))
    print('[input-lmms]')
    tracks.r_pl_audio(cvpj_l, trackid, lmms_decode_audioplacements(trkX))
    tracks.r_param(cvpj_l, trackid, 'enabled', int(lmms_auto_getvalue(trkX, 'muted', 1, 'bool', [-1, -1] ,['track', trackid, 'enabled'])))
    tracks.r_param(cvpj_l, trackid, 'solo', int(trkX.get('solo')))

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
            tracks.autoid_in_add_pl(str(autoobjectX[0].get('id')), placeJ)
    print(' ')

def lmms_decode_auto_track(trkX):
    lmms_decode_autoplacements(trkX)

# ------- Effects -------

def get_ladspa_path(ladname):
    temppath = lmms_ladspapath+ladname

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

        plugins.add_plug(cvpj_l, pluginid, 'eq', 'peaks')

        LPactive = lmms_auto_getvalue(fxxml_plugin, 'LPactive', 0, 'int', None, ['slot', pluginid, 'peak_1_on'])
        LPfreq   = lmms_auto_getvalue(fxxml_plugin, 'LPfreq', 0, 'float', None,   ['slot', pluginid, 'peak_1_freq'])
        LPres    = lmms_auto_getvalue(fxxml_plugin, 'LPres', 0, 'float', None,    ['slot', pluginid, 'peak_1_val'])
        plugins.add_eqband(cvpj_l, pluginid, LPactive, LPfreq, 0, 'low_pass', LPres)

        Lowshelfactive = lmms_auto_getvalue(fxxml_plugin, 'Lowshelfactive', 0, 'int', None, ['slot', pluginid, 'peak_2_on'])
        LowShelffreq   = lmms_auto_getvalue(fxxml_plugin, 'LowShelffreq', 0, 'float', None,   ['slot', pluginid, 'peak_2_freq'])
        Lowshelfgain   = lmms_auto_getvalue(fxxml_plugin, 'Lowshelfgain', 0, 'float', None,   ['slot', pluginid, 'peak_2_gain'])
        LowShelfres    = lmms_auto_getvalue(fxxml_plugin, 'LowShelfres', 0, 'float', None,    ['slot', pluginid, 'peak_2_val'])
        plugins.add_eqband(cvpj_l, pluginid, Lowshelfactive, LowShelffreq, Lowshelfgain, 'low_shelf', LowShelfres)

        Peak1active = lmms_auto_getvalue(fxxml_plugin, 'Peak1active', 0, 'int', None, ['slot', pluginid, 'peak_3_on'])
        Peak1bw     = lmms_auto_getvalue(fxxml_plugin, 'Peak1bw', 0, 'float', None,     ['slot', pluginid, 'peak_3_val'])
        Peak1freq   = lmms_auto_getvalue(fxxml_plugin, 'Peak1freq', 0, 'float', None,   ['slot', pluginid, 'peak_3_freq'])
        Peak1gain   = lmms_auto_getvalue(fxxml_plugin, 'Peak1gain', 0, 'float', None,   ['slot', pluginid, 'peak_3_gain'])
        plugins.add_eqband(cvpj_l, pluginid, Peak1active, Peak1freq, Peak1gain, 'peak', Peak1bw)

        Peak2active = lmms_auto_getvalue(fxxml_plugin, 'Peak2active', 0, 'int', None, ['slot', pluginid, 'peak_4_on'])
        Peak2bw     = lmms_auto_getvalue(fxxml_plugin, 'Peak2bw', 0, 'float', None,     ['slot', pluginid, 'peak_4_val'])
        Peak2freq   = lmms_auto_getvalue(fxxml_plugin, 'Peak2freq', 0, 'float', None,   ['slot', pluginid, 'peak_4_freq'])
        Peak2gain   = lmms_auto_getvalue(fxxml_plugin, 'Peak2gain', 0, 'float', None,   ['slot', pluginid, 'peak_4_gain'])
        plugins.add_eqband(cvpj_l, pluginid, Peak2active, Peak2freq, Peak2gain, 'peak', Peak2bw)

        Peak3active = lmms_auto_getvalue(fxxml_plugin, 'Peak3active', 0, 'int', None, ['slot', pluginid, 'peak_5_on'])
        Peak3bw     = lmms_auto_getvalue(fxxml_plugin, 'Peak3bw', 0, 'float', None,     ['slot', pluginid, 'peak_5_val'])
        Peak3freq   = lmms_auto_getvalue(fxxml_plugin, 'Peak3freq', 0, 'float', None,   ['slot', pluginid, 'peak_5_freq'])
        Peak3gain   = lmms_auto_getvalue(fxxml_plugin, 'Peak3gain', 0, 'float', None,   ['slot', pluginid, 'peak_5_gain'])
        plugins.add_eqband(cvpj_l, pluginid, Peak3active, Peak3freq, Peak3gain, 'peak', Peak3bw)

        Peak4active = lmms_auto_getvalue(fxxml_plugin, 'Peak4active', 0, 'int', None, ['slot', pluginid, 'peak_6_on'])
        Peak4bw     = lmms_auto_getvalue(fxxml_plugin, 'Peak4bw', 0, 'float', None,     ['slot', pluginid, 'peak_6_val'])
        Peak4freq   = lmms_auto_getvalue(fxxml_plugin, 'Peak4freq', 0, 'float', None,   ['slot', pluginid, 'peak_6_freq'])
        Peak4gain   = lmms_auto_getvalue(fxxml_plugin, 'Peak4gain', 0, 'float', None,   ['slot', pluginid, 'peak_6_gain'])
        plugins.add_eqband(cvpj_l, pluginid, Peak4active, Peak4freq, Peak4gain, 'peak', Peak4bw)

        Highshelfactive = lmms_auto_getvalue(fxxml_plugin, 'Highshelfactive', 0, 'int', None, ['slot', pluginid, 'peak_7_on'])
        Highshelffreq   = lmms_auto_getvalue(fxxml_plugin, 'Highshelffreq', 0, 'float', None,   ['slot', pluginid, 'peak_7_freq'])
        HighShelfgain   = lmms_auto_getvalue(fxxml_plugin, 'HighShelfgain', 0, 'float', None,   ['slot', pluginid, 'peak_7_gain'])
        HighShelfres    = lmms_auto_getvalue(fxxml_plugin, 'HighShelfres', 0, 'float', None,    ['slot', pluginid, 'peak_7_val'])
        plugins.add_eqband(cvpj_l, pluginid, Highshelfactive, Highshelffreq, HighShelfgain, 'high_shelf', HighShelfres)

        HPactive = lmms_auto_getvalue(fxxml_plugin, 'HPactive', 0, 'int', None, ['slot', pluginid, 'peak_8_on'])
        HPfreq   = lmms_auto_getvalue(fxxml_plugin, 'HPfreq', 0, 'float', None,   ['slot', pluginid, 'peak_8_freq'])
        HPres    = lmms_auto_getvalue(fxxml_plugin, 'HPres', 0, 'float', None,    ['slot', pluginid, 'peak_8_val'])
        plugins.add_eqband(cvpj_l, pluginid, HPactive, HPfreq, 0, 'high_pass', HPres)

    elif fxpluginname == 'vsteffect':
        fxxml_plugin = fxslotX.findall(fxlist[fxpluginname])[0]
        print('[vst2-dll',end='] ')
        plugins.add_plug(cvpj_l, pluginid, 'vst2', 'win')
        getvstparams(pluginid, fxxml_plugin)

    elif fxpluginname == 'ladspaeffect':
        fxxml_plugin = fxslotX.findall('ladspacontrols')[0]
        print('[ladspa',end='] ')
        fxxml_plugin_key = fxslotX.findall('key')[0]
        fxxml_plugin_ladspacontrols = fxslotX.findall('ladspacontrols')[0]

        plugins.add_plug(cvpj_l, pluginid, 'ladspa', 'win')

        for attribute in fxxml_plugin_key.findall('attribute'):
            attval = attribute.get('value')
            attname = attribute.get('name')
            if attname == 'file':
                if os.path.exists(attval): 
                    plugins.add_plug_data(cvpj_l, pluginid, 'name', attval)
                    plugins.add_plug_data(cvpj_l, pluginid, 'path', attval)
                else: 
                    plugins.add_plug_data(cvpj_l, pluginid, 'name', attval)
                    plugins.add_plug_data(cvpj_l, pluginid, 'path', get_ladspa_path(attval))
            if attname == 'plugin': 
                plugins.add_plug_data(cvpj_l, pluginid, 'plugin', attval)

        ladspa_ports = int(fxxml_plugin_ladspacontrols.get('ports'))
        ladspa_linked = fxxml_plugin_ladspacontrols.get('link')
        seperated_channels = False

        if ladspa_linked != None: 
            ladspa_ports //= 2
            if ladspa_linked == "0": seperated_channels = True

        plugins.add_plug_data(cvpj_l, pluginid, 'numparams', ladspa_ports)

        for node in fxxml_plugin_ladspacontrols.iter():
            notetagtxt = node.tag
            if notetagtxt.startswith('port'):
                l_ch = notetagtxt[4]
                l_val = notetagtxt[5:]
                t_data = node.get('data')
                if l_ch == '0': paramid = 'ladspa_param_'+l_val
                else: paramid = 'ladspa_param_'+l_val+'_'+l_ch
                paramval = float(lmms_auto_getvalue(node, 'data', '0', 'float', None, ['plugin', pluginid, paramid]))
                plugins.add_plug_param(cvpj_l, pluginid, paramid, paramval, 'float', paramid)

        if seperated_channels == False: 
            plugins.add_plug_data(cvpj_l, pluginid, 'seperated_channels', False)
        if seperated_channels == True: 
            plugins.add_plug_data(cvpj_l, pluginid, 'seperated_channels', True)
    else:
        fxxml_plugin = fxslotX.findall(fxlist[fxpluginname])[0]
        print('['+fxpluginname,end='] ')

        plugins.add_plug(cvpj_l, pluginid, 'native-lmms', fxpluginname)

        lmms_autovals = lmms_auto.get_params_fx(fxpluginname)
        for pluginparam in lmms_autovals[0]:
            plugins.add_plug_param(cvpj_l, pluginid, pluginparam, 
            lmms_auto_getvalue(fxxml_plugin, pluginparam, 0, 'float', None, 
                ['plugin', pluginid, pluginparam]), 
            'float', pluginparam)
        for pluginparam in lmms_autovals[1]:
            xml_pluginparam = fxxml_plugin.get(pluginparam)
            if xml_pluginparam: 
                plugins.add_plug_data(cvpj_l, pluginid, pluginparam, xml_pluginparam)

    fxenabled = lmms_auto_getvalue(fxslotX, 'on', 0, 'bool', None, ['slot', pluginid, 'enabled'])
    fxwet = lmms_auto_getvalue(fxslotX, 'wet', 0, 'float', None, ['slot', pluginid, 'wet'])

    plugins.add_plug_fxdata(cvpj_l, pluginid, fxenabled, fxwet)

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

def lmms_decode_fxmixer(fxX):
    fxlist = {}
    for fxcX in fxX:
        fx_name = fxcX.get('name')
        fx_num = fxcX.get('num')
        print('[input-lmms] FX ' + str(fx_num))
        print('[input-lmms]       Name: ' + fx_name)
        fxcJ = {}
        fxcJ['name'] = fx_name
        if fxcX.get('muted') != None: fxcJ['enabled'] = not int(fxcX.get('muted'))
        fxcJ['vol'] = float(lmms_auto_getvalue(fxcX, 'volume', 1, 'float', None, ['fxmixer', fx_num, 'vol']))
        fxchainX = fxcX.find('fxchain')
        if fxchainX != None:
            fxcJ['fxenabled'] = int(fxchainX.get('enabled'))
            fxcJ['chain_fx_audio'] = lmms_decode_fxchain(fxchainX)
        sendlist = []
        sendsxml = fxcX.findall('send')
        for sendxml in sendsxml:
            send_id = get_send_auto_id()
            sendentryjson = {}
            sendentryjson['channel'] = int(sendxml.get('channel'))
            sendentryjson['amount'] = lmms_auto_getvalue(sendxml, 'amount', 1, 'float', None, ['send', send_id, 'amount'])
            sendentryjson['sendautoid'] = send_id
            sendlist.append(sendentryjson)
        fxcJ['sends'] = sendlist
        fxlist[str(fx_num)] = fxcJ
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
        'auto_nopl': False,
        }
    def supported_autodetect(self): return True
    def detect(self, input_file):
        try:
            root = get_xml_tree(input_file)
            if root.tag == "lmms-project": output = True
        except ET.ParseError: output = False
        return output
    def parse(self, input_file, extra_param):
        print('[input-lmms] Input Start')
        global lmms_vstpath
        global lmms_ladspapath
        global cvpj_l

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

        if lmmsconfigpath_found == True:
            lmmsconfX = ET.parse(lmmsconfigpath).getroot()
            lmmsconf_pathsX = lmmsconfX.findall('paths')[0]
            lmms_vstpath = lmmsconf_pathsX.get('vstdir')
            lmms_ladspapath = lmmsconf_pathsX.get('ladspadir')
        else: 
            lmms_vstpath = ''
            lmms_ladspapath = ''

        tree = get_xml_tree(input_file)
        headX = tree.findall('head')[0]
        trksX = tree.findall('song/trackcontainer/track')
        fxX = tree.findall('song/fxmixer/fxchannel')
        tlX = tree.find('song/timeline')
        projnotesX = tree.find('song/projectnotes')

        cvpj_l = {}
        cvpj_l['bpm'] = float(lmms_auto_getvalue(headX, 'bpm', 140, 'float', None, ['main', 'bpm']))
        cvpj_l['vol'] = hundredto1(float(lmms_auto_getvalue(headX, 'mastervol', 1, 'float', [0, 0.01], ['main', 'vol'])))
        cvpj_l['pitch'] = float(lmms_auto_getvalue(headX, 'masterpitch', 0, 'float', None, ['main', 'pitch']))
        cvpj_l['timesig_numerator'] = lmms_auto_getvalue(headX, 'timesig_numerator', 4, 'int', None, None)
        cvpj_l['timesig_denominator'] = lmms_auto_getvalue(headX, 'timesig_denominator', 4, 'int', None, None)

        if projnotesX.text != None: song.add_info_msg(cvpj_l, 'html', projnotesX.text)

        lmms_decode_tracks(trksX)
        fxrackdata = lmms_decode_fxmixer(fxX)

        trackdata = cvpj_l['track_data']

        cvpj_l['use_fxrack'] = True
        cvpj_l['fxrack'] = fxrackdata

        tracks.autoid_in_output(cvpj_l)

        return json.dumps(cvpj_l, indent=2)
        
def get_xml_tree(path):
    with open(path, 'rb') as file:
        try:
            file.seek(4)
            data = zlib.decompress(file.read())
            return ET.fromstring(data)

        except zlib.error:
            return ET.parse(path).getroot()