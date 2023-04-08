# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import base64
import json
import math
import plugin_input
import os
import sys
import xml.etree.ElementTree as ET
from functions_plugin import lmms_auto
from functions import note_mod
from functions import note_data
from functions import notelist_data
from functions import colors
from functions import auto
from functions import tracks

plugin_auto_id = 1000
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


def get_plugin_auto_id():
    global plugin_auto_id
    plugin_auto_id += 1
    return 'plugin'+str(plugin_auto_id)


def getvstparams(plugindata, xmldata, cvpj_data):
    plugindata['plugin'] = {}
    if os.path.exists( xmldata.get('plugin')):
        plugindata['plugin']['path'] = xmldata.get('plugin')
    else:
        plugindata['plugin']['path'] = lmms_vstpath+xmldata.get('plugin')
    vst_data = xmldata.get('chunk')
    vst_numparams = xmldata.get('numparams')
    if vst_data != None:
        plugindata['datatype'] = 'raw'
        plugindata['data'] = vst_data
    elif vst_numparams != None:
        plugindata['datatype'] = 'param'
        plugindata['numparams'] = int(vst_numparams)
        plugindata['params'] = {}
        for param in range(int(vst_numparams)):
            paramdata = xmldata.get('param'+str(param)).split(':')
            plugindata['params'][str(param)] = {}
            plugindata['params'][str(param)]['name'] = paramdata[1]
            plugindata['params'][str(param)]['value'] = float(paramdata[-1])
    if 'pluginautoid' in cvpj_data:
        for node in xmldata.iter():
            notetagtxt = node.tag
            if notetagtxt.startswith('param'):
                value = node.get('value')
                if value != None:
                    l_autoid[str(node.get('id'))] = ['plugin', cvpj_data['pluginautoid'], 'vst_param_'+notetagtxt[5:]]

def hundredto1(lmms_input): return float(lmms_input) * 0.01

def lmms_auto_getvalue(xmltag, xmlname, fallbackval, autoname):
    #print(xmltag, xmlname, fallbackval, autoname, xmltag.get(xmlname))
    if xmltag.get(xmlname) != None: return float(xmltag.get(xmlname))
    elif xmltag.findall(xmlname) != []: 
        realvaluetag = xmltag.findall(xmlname)[0]
        value = realvaluetag.get('value')
        if value != None:
            if autoname != None: l_autoid[str(realvaluetag.get('id'))] = autoname
            return realvaluetag.get('value')
    else: return fallbackval

def lmms_getvalue_int(json_in, json_name, xml_in): 
    if xml_in != None: json_in[json_name] = int(xml_in)
def lmms_getvalue_float(json_in, json_name, xml_in): 
    if xml_in != None: json_in[json_name] = float(xml_in)
def lmms_getvalue_100(json_in, json_name, xml_in): 
    if xml_in != None: json_in[json_name] = hundredto1(float(xml_in))
def lmms_getvalue_exp(json_in, json_name, xml_in): 
    if xml_in != None: json_in[json_name] = exp2sec(float(xml_in))

# ------- Instruments and Plugins -------

def exp2sec(value): return (value*value)*5

def asdflfo_get(trkX_insttr, cvpj_l_plugindata):
    elcX = trkX_insttr.findall('eldata')
    if len(elcX) != 0:
        cvpj_l_plugindata_asdrlfo = {}
        eldataX = elcX[0]
        if eldataX.findall('elvol'): asdflfo(cvpj_l_plugindata_asdrlfo, eldataX.findall('elvol')[0], 'volume')
        if eldataX.findall('elcut'): asdflfo(cvpj_l_plugindata_asdrlfo, eldataX.findall('elcut')[0], 'cutoff')
        if eldataX.findall('elres'): asdflfo(cvpj_l_plugindata_asdrlfo, eldataX.findall('elres')[0], 'reso')
        cvpj_l_plugindata['asdrlfo'] = cvpj_l_plugindata_asdrlfo
        filterparams = {}
        lmms_getvalue_float(filterparams, 'cutoff', eldataX.get('fcut'))
        lmms_getvalue_float(filterparams, 'wet', eldataX.get('fwet'))
        if eldataX.get('ftype') != None: 
            filtertype_out = filtertype[int(eldataX.get('ftype'))]
            filterparams['type'] = filtertype_out[0]
            if filtertype_out[1] != None: filterparams['subtype'] = filtertype_out[1]
        lmms_getvalue_float(filterparams, 'reso', eldataX.get('fres'))

        if filterparams != {}:
            cvpj_l_plugindata['filter'] = {}
            if 'cutoff' in filterparams: cvpj_l_plugindata['filter']['cutoff'] = filterparams['cutoff']
            if 'wet' in filterparams: cvpj_l_plugindata['filter']['wet'] = filterparams['wet']
            if 'type' in filterparams: cvpj_l_plugindata['filter']['type'] = filterparams['type']
            if 'subtype' in filterparams: cvpj_l_plugindata['filter']['subtype'] = filterparams['subtype']
            if 'reso' in filterparams: cvpj_l_plugindata['filter']['reso'] = filterparams['reso']

def asdflfo(cvpj_l_track, xmlO, asdrtype):
    envelopeparams = {}
    lmms_getvalue_exp(envelopeparams, 'predelay', xmlO.get('pdel'))
    lmms_getvalue_exp(envelopeparams, 'attack', xmlO.get('att'))
    lmms_getvalue_exp(envelopeparams, 'hold', xmlO.get('hold'))
    lmms_getvalue_exp(envelopeparams, 'decay', xmlO.get('dec'))
    lmms_getvalue_float(envelopeparams, 'sustain', xmlO.get('sustain'))
    lmms_getvalue_exp(envelopeparams, 'release', xmlO.get('rel'))
    lmms_getvalue_float(envelopeparams, 'amount', xmlO.get('amt'))

    if asdrtype == 'cutoff':
        if 'amount' in envelopeparams: 
            envelopeparams['amount'] = envelopeparams['amount']*6000

    cvpj_l_track[asdrtype] = {}
    if envelopeparams != {}:
        cvpj_l_track[asdrtype]['envelope'] = envelopeparams

    lfoparams = {}

    speedx100 = xmlO.get('x100')
    if speedx100 != None: speedx100 = int(speedx100)
    else: speedx100 = 0

    lmms_getvalue_float(lfoparams, 'predelay', xmlO.get('pdel'))
    lmms_getvalue_exp(lfoparams, 'attack', xmlO.get('latt'))
    if xmlO.get('lshp') != None: lfoparams['shape'] = lfoshape[int(xmlO.get('lshp'))]
    lmms_getvalue_float(lfoparams, 'amount', xmlO.get('lamt'))

    if asdrtype == 'cutoff':
        if 'amount' in lfoparams: 
            lfoparams['amount'] = lfoparams['amount']*1500

    if xmlO.get('lspd') != None: 
        lfoparams['speed'] = {'type': 'seconds'}
        if speedx100 == 1: lfoparams['speed']['time'] = float(xmlO.get('lspd')) * 0.2
        else: lfoparams['speed']['time'] = float(xmlO.get('lspd')) * 20

    if lfoparams != {}: cvpj_l_track[asdrtype]['lfo'] = lfoparams

def lmms_decodeplugin(trkX_insttr, cvpj_l_plugindata, cvpj_l_inst):
    cvpj_l_inst['plugin'] = "none"
    trkX_instrument = trkX_insttr.findall('instrument')[0]
    pluginname = trkX_instrument.get('name')

    out_color = None

    xml_a_plugin = trkX_instrument.findall(pluginname)
    if len(xml_a_plugin) != 0: 
        xml_plugin = xml_a_plugin[0]

        auto_id_plugin = get_plugin_auto_id()

        cvpj_l_inst['pluginautoid'] = auto_id_plugin

        if pluginname == "sf2player":
            cvpj_l_inst['plugin'] = "soundfont2"
            cvpj_l_plugindata['bank'] = int(xml_plugin.get('bank'))
            cvpj_l_plugindata['patch'] = int(xml_plugin.get('patch'))
            cvpj_l_plugindata['file'] = xml_plugin.get('src')
            cvpj_l_plugindata['gain'] = float(xml_plugin.get('gain'))
            cvpj_l_plugindata['reverb'] = {}
            cvpj_l_plugindata['chorus'] = {}
            cvpj_l_plugindata['chorus']['depth'] = float(xml_plugin.get('chorusDepth'))
            cvpj_l_plugindata['chorus']['level'] = float(xml_plugin.get('chorusLevel'))
            cvpj_l_plugindata['chorus']['lines'] = float(xml_plugin.get('chorusNum'))
            cvpj_l_plugindata['chorus']['enabled'] = float(xml_plugin.get('chorusOn'))
            cvpj_l_plugindata['chorus']['speed'] = float(xml_plugin.get('chorusSpeed'))
            cvpj_l_plugindata['reverb']['damping'] = float(xml_plugin.get('reverbDamping'))
            cvpj_l_plugindata['reverb']['level'] = float(xml_plugin.get('reverbLevel'))
            cvpj_l_plugindata['reverb']['enabled'] = float(xml_plugin.get('reverbOn'))
            cvpj_l_plugindata['reverb']['roomsize'] = float(xml_plugin.get('reverbRoomSize'))
            cvpj_l_plugindata['reverb']['width'] = float(xml_plugin.get('reverbWidth'))


        elif pluginname == "audiofileprocessor":
            cvpj_l_inst['plugin'] = "sampler"
            lmms_getvalue_int(cvpj_l_plugindata, 'reverse', xml_plugin.get('reversed'))
            lmms_getvalue_100(cvpj_l_plugindata, 'amp', xml_plugin.get('amp'))
            lmms_getvalue_int(cvpj_l_plugindata, 'continueacrossnotes', xml_plugin.get('stutter'))
            cvpj_l_plugindata['file'] = xml_plugin.get('src')
            cvpj_l_plugindata['trigger'] = 'normal'
            cvpj_l_plugindata['point_value_type'] = "percent"
            cvpj_l_plugindata['loop'] = {}
            looped = int(xml_plugin.get('looped'))
            if looped == 0: cvpj_l_plugindata['loop'] = {'enabled': 0}
            if looped == 1: cvpj_l_plugindata['loop'] = {'enabled': 1, 'mode': "normal"}
            if looped == 2: cvpj_l_plugindata['loop'] = {'enabled': 1, 'mode': "pingpong"}
            cvpj_l_plugindata['loop']['points'] = [float(xml_plugin.get('lframe')), float(xml_plugin.get('eframe'))]
            lmms_getvalue_float(cvpj_l_plugindata, 'end', xml_plugin.get('eframe'))
            lmms_getvalue_float(cvpj_l_plugindata, 'start', xml_plugin.get('sframe'))
            interpolation = int(xml_plugin.get('interp'))
            if interpolation == 0: cvpj_l_plugindata['interpolation'] = "none"
            if interpolation == 1: cvpj_l_plugindata['interpolation'] = "linear"
            if interpolation == 2: cvpj_l_plugindata['interpolation'] = "sinc"
            asdflfo_get(trkX_insttr, cvpj_l_plugindata)


        elif pluginname == "OPL2":
            cvpj_l_inst['plugin'] = "opl2"
            for opnum in range(2):
                opl2_optxt = 'op'+str(opnum+1)
                cvpj_l_plugindata[opl2_optxt] = {}
                cvpj_l_plugindata[opl2_optxt]['env_attack'] = lmms_auto_getvalue(xml_plugin, opl2_optxt+'_a', 0, ['plugin', auto_id_plugin, opl2_optxt+'_env_attack'])
                cvpj_l_plugindata[opl2_optxt]['env_decay'] = lmms_auto_getvalue(xml_plugin, opl2_optxt+'_d', 0, ['plugin', auto_id_plugin, opl2_optxt+'_env_decay'])
                cvpj_l_plugindata[opl2_optxt]['env_release'] = lmms_auto_getvalue(xml_plugin, opl2_optxt+'_r', 0, ['plugin', auto_id_plugin, opl2_optxt+'_env_release'])
                cvpj_l_plugindata[opl2_optxt]['env_sustain'] = lmms_auto_getvalue(xml_plugin, opl2_optxt+'_s', 0, ['plugin', auto_id_plugin, opl2_optxt+'_env_sustain'])
                cvpj_l_plugindata[opl2_optxt]['freqmul'] = lmms_auto_getvalue(xml_plugin, opl2_optxt+'_mul', 0, ['plugin', auto_id_plugin, opl2_optxt+'_freqmul'])
                cvpj_l_plugindata[opl2_optxt]['ksr'] = lmms_auto_getvalue(xml_plugin, opl2_optxt+'_ksr', 0, ['plugin', auto_id_plugin, opl2_optxt+'_ksr'])
                cvpj_l_plugindata[opl2_optxt]['level'] = lmms_auto_getvalue(xml_plugin, opl2_optxt+'_lvl', 0, ['plugin', auto_id_plugin, opl2_optxt+'_level'])
                cvpj_l_plugindata[opl2_optxt]['perc_env'] = lmms_auto_getvalue(xml_plugin, opl2_optxt+'_perc', 0, ['plugin', auto_id_plugin, opl2_optxt+'_perc_env'])
                cvpj_l_plugindata[opl2_optxt]['scale'] = lmms_auto_getvalue(xml_plugin, opl2_optxt+'_scale', 0, ['plugin', auto_id_plugin, opl2_optxt+'_scale'])
                cvpj_l_plugindata[opl2_optxt]['tremolo'] = lmms_auto_getvalue(xml_plugin, opl2_optxt+'_trem', 0, ['plugin', auto_id_plugin, opl2_optxt+'_tremolo'])
                cvpj_l_plugindata[opl2_optxt]['vibrato'] = lmms_auto_getvalue(xml_plugin, opl2_optxt+'_vib', 0, ['plugin', auto_id_plugin, opl2_optxt+'_vibrato'])
                cvpj_l_plugindata[opl2_optxt]['waveform'] = lmms_auto_getvalue(xml_plugin, opl2_optxt+'_waveform', 0, ['plugin', auto_id_plugin, opl2_optxt+'_env_attack'])
            cvpj_l_plugindata['feedback'] = lmms_auto_getvalue(xml_plugin, 'feedback', 0, ['plugin', auto_id_plugin, 'feedback'])
            cvpj_l_plugindata['fm'] = lmms_auto_getvalue(xml_plugin, 'fm', 0, ['plugin', auto_id_plugin, 'fm'])
            cvpj_l_plugindata['tremolo_depth'] = lmms_auto_getvalue(xml_plugin, 'trem_depth', 0, ['plugin', auto_id_plugin, 'tremolo_depth'])
            cvpj_l_plugindata['vibrato_depth'] = lmms_auto_getvalue(xml_plugin, 'vib_depth', 0, ['plugin', auto_id_plugin, 'vibrato_depth'])
            

        elif pluginname == "zynaddsubfx":
            cvpj_l_inst['plugin'] = "zynaddsubfx-lmms"
            cvpj_l_plugindata['bandwidth'] = lmms_auto_getvalue(xml_plugin, 'bandwidth', 0, ['plugin', auto_id_plugin, 'bandwidth'])
            cvpj_l_plugindata['filterfreq'] = lmms_auto_getvalue(xml_plugin, 'filterfreq', 0, ['plugin', auto_id_plugin, 'filterfreq'])
            cvpj_l_plugindata['filterq'] = lmms_auto_getvalue(xml_plugin, 'filterq', 0, ['plugin', auto_id_plugin, 'filterq'])
            cvpj_l_plugindata['fmgain'] = lmms_auto_getvalue(xml_plugin, 'fmgain', 0, ['plugin', auto_id_plugin, 'fmgain'])
            cvpj_l_plugindata['forwardmidicc'] = lmms_auto_getvalue(xml_plugin, 'forwardmidicc', 0, ['plugin', auto_id_plugin, 'forwardmidicc'])
            cvpj_l_plugindata['modifiedcontrollers'] = xml_plugin.get('modifiedcontrollers')
            cvpj_l_plugindata['portamento'] = lmms_auto_getvalue(xml_plugin, 'portamento', 0, ['plugin', auto_id_plugin, 'portamento'])
            cvpj_l_plugindata['resbandwidth'] = lmms_auto_getvalue(xml_plugin, 'resbandwidth', 0, ['plugin', auto_id_plugin, 'resbandwidth'])
            cvpj_l_plugindata['rescenterfreq'] = lmms_auto_getvalue(xml_plugin, 'rescenterfreq', 0, ['plugin', auto_id_plugin, 'rescenterfreq'])
            zdata = xml_plugin.findall('ZynAddSubFX-data')[0]
            cvpj_l_plugindata['data'] = base64.b64encode(ET.tostring(zdata, encoding='utf-8')).decode('ascii')


        elif pluginname == "vestige":
            cvpj_l_inst['plugin'] = "vst2-dll"
            getvstparams(cvpj_l_plugindata, xml_plugin, cvpj_l_inst)


        else:
            cvpj_l_inst['plugin'] = "native-lmms"
            cvpj_l_plugindata['name'] = pluginname
            cvpj_l_plugindata['data'] = {}
            lmms_autovals = lmms_auto.get_params_inst(pluginname)
            for pluginparam in lmms_autovals[0]:
                cvpj_l_plugindata['data'][pluginparam] = lmms_auto_getvalue(xml_plugin, pluginparam, 0, ['plugin', auto_id_plugin, pluginparam])
            for pluginparam in lmms_autovals[1]:
                xml_pluginparam = xml_plugin.get(pluginparam)
                if xml_pluginparam: cvpj_l_plugindata['data'][pluginparam] = xml_pluginparam

            asdflfo_get(trkX_insttr, cvpj_l_plugindata)

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

    tracks.r_addtrack_inst(cvpj_l, trackid, cvpj_l_track_inst)

    tracks.r_addinst_param(cvpj_l, trackid, 'enabled', int(not int( lmms_auto_getvalue(trkX, 'muted', 0, ['track', trackid, 'enabled']) )))
    tracks.r_addinst_param(cvpj_l, trackid, 'solo', int(trkX.get('solo')))

    #trkX_insttr
    trkX_insttr = trkX.findall('instrumenttrack')[0]
    cvpj_pan = hundredto1(float(lmms_auto_getvalue(trkX_insttr, 'pan', 0, ['track', trackid, 'pan'])))
    cvpj_vol = hundredto1(float(lmms_auto_getvalue(trkX_insttr, 'vol', 1, ['track', trackid, 'vol'])))
    
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
    if len(xml_a_fxchain) != 0: tracks.r_audiofx_chain(cvpj_l, trackid, lmms_decode_fxchain(xml_a_fxchain[0]))

    cvpj_l_track_inst['plugindata'] = {}

    track_color = lmms_decodeplugin(trkX_insttr, cvpj_l_track_inst['plugindata'], cvpj_l_track_inst)

    tracks.r_addinst_param(cvpj_l, trackid, 'fxrack_channel', int(trkX_insttr.get('fxch')))
    tracks.r_addinst_param(cvpj_l, trackid, 'usemasterpitch', int(trkX_insttr.get('usemasterpitch')))
    tracks.r_addinst_param(cvpj_l, trackid, 'pitch', float(lmms_auto_getvalue(trkX_insttr, 'pitch', 0, ['track', trackid, 'pitch'])))
    tracks.r_addtrack_data(cvpj_l, trackid, cvpj_name, track_color, cvpj_vol, cvpj_pan)

    if 'basenote' in trkX_insttr.attrib:
        basenote = int(trkX_insttr.get('basenote'))-57
        noteoffset = 0
        if cvpj_l_track_inst['plugin'] == 'sampler': noteoffset = 3
        if cvpj_l_track_inst['plugin'] == 'soundfont2': noteoffset = 12
        middlenote = basenote - noteoffset
        if middlenote != 0: cvpj_l_track_inst['middlenote'] = middlenote

    tracks.r_notefx_chain(cvpj_l, trackid, [])
    xml_a_arpeggiator = trkX_insttr.findall('arpeggiator')
    if len(xml_a_arpeggiator) != 0:
        trkX_arpeggiator = xml_a_arpeggiator[0]
        cvpj_l_arpeggiator_enabled = int(trkX_arpeggiator.get('arp-enabled'))
        cvpj_l_arpeggiator = {}
        cvpj_l_arpeggiator['gate'] = int(trkX_arpeggiator.get('arpgate'))
        cvpj_l_arpeggiator['arprange'] = int(trkX_arpeggiator.get('arprange'))
        cvpj_l_arpeggiator['mode'] = int(trkX_arpeggiator.get('arpmode'))
        cvpj_l_arpeggiator['direction'] = arpdirection[int(trkX_arpeggiator.get('arpdir'))]
        cvpj_l_arpeggiator['miss'] = int(trkX_arpeggiator.get('arpmiss'))
        cvpj_l_arpeggiator['skiprate'] = hundredto1(int(trkX_arpeggiator.get('arpskip')))
        cvpj_l_arpeggiator['time'] = float(trkX_arpeggiator.get('arptime'))
        cvpj_l_arpeggiator['missrate'] = hundredto1(int(trkX_arpeggiator.get('arpmiss')))
        cvpj_l_arpeggiator['cyclenotes'] = int(trkX_arpeggiator.get('arpcycle'))
        cvpj_l_arpeggiator['chord'] = ','.join(str(item) for item in chord[int(trkX_arpeggiator.get('arp'))])
        cvpj_l_arpeggiator_plugindata = {"name": "arpeggiator", "data": cvpj_l_arpeggiator}
        tracks.r_notefx_chain_append(cvpj_l, trackid, cvpj_l_arpeggiator_enabled, "native-lmms", cvpj_l_arpeggiator_plugindata)
    xml_a_chordcreator = trkX_insttr.findall('chordcreator')
    if len(xml_a_chordcreator) != 0:
        trkX_chordcreator = xml_a_chordcreator[0]
        cvpj_l_chordcreator_enabled = int(trkX_chordcreator.get('chord-enabled'))
        cvpj_l_chordcreator = {}
        cvpj_l_chordcreator['chordrange'] = int(trkX_chordcreator.get('chordrange'))
        cvpj_l_chordcreator['chord'] = ','.join(str(item) for item in chord[int(trkX_chordcreator.get('chord'))])
        cvpj_l_chordcreator_plugindata = {"name": "chordcreator", "data": cvpj_l_chordcreator}
        tracks.r_notefx_chain_append(cvpj_l, trackid, cvpj_l_arpeggiator_enabled, "native-lmms", cvpj_l_chordcreator_plugindata)

    tracks.r_addtrackpl(cvpj_l, trackid, lmms_decode_nlplacements(trkX))

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
    tracks.r_addtrack_audio(cvpj_l, trackid, None)
    cvpj_name = trkX.get('name')
    print('[input-lmms] Audio Track')
    print('[input-lmms]       Name: ' + cvpj_name)
    trkX_audiotr = trkX.findall('sampletrack')[0]
    cvpj_pan = hundredto1(float(lmms_auto_getvalue(trkX_audiotr, 'pan', 0, ['track', trackid, 'pan'])))
    cvpj_vol = hundredto1(float(lmms_auto_getvalue(trkX_audiotr, 'vol', 1, ['track', trackid, 'vol'])))
    tracks.r_addtrack_data(cvpj_l, trackid, cvpj_name, None, cvpj_vol, cvpj_pan)
    xml_a_fxchain = trkX_audiotr.findall('fxchain')
    if len(xml_a_fxchain) != 0: tracks.r_audiofx_chain(cvpj_l, trackid, lmms_decode_fxchain(xml_a_fxchain[0]))
    print('[input-lmms]')
    tracks.r_addtrackpl_audio(cvpj_l, trackid, lmms_decode_audioplacements(trkX))
    tracks.r_addinst_param(cvpj_l, trackid, 'enabled', int(not int(lmms_auto_getvalue(trkX, 'muted', 1, ['track', trackid, 'enabled']))))
    tracks.r_addinst_param(cvpj_l, trackid, 'solo', int(trkX.get('solo')))

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
            if internal_id not in l_autodata: l_autodata[internal_id] = []
            l_autodata[internal_id].append(placeJ)
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
    fxslotJ = {}
    fxpluginname = fxslotX.get('name')
    fxcvpj_l_plugindata = {}
    fxslotJ['enabled'] = int(fxslotX.get('on'))
    wet = float(fxslotX.get('wet'))
    if wet < 0:
        fxslotJ['add_dry_minus_wet'] = 1
        fxslotJ['wet'] = -wet
    else:
        fxslotJ['add_dry_minus_wet'] = 0
        fxslotJ['wet'] = wet

    auto_id_plugin = get_plugin_auto_id()
    fxslotJ['pluginautoid'] = auto_id_plugin

    if fxpluginname == 'vsteffect':
        fxxml_plugin = fxslotX.findall(fxlist[fxpluginname])[0]
        print('[vst2-dll',end='] ')
        fxslotJ['plugin'] = "vst2-dll"
        getvstparams(fxcvpj_l_plugindata, fxxml_plugin, fxslotJ)
        fxslotJ['plugindata'] = fxcvpj_l_plugindata
        return fxslotJ

    elif fxpluginname == 'ladspaeffect':
        fxxml_plugin = fxslotX.findall('ladspacontrols')[0]
        print('[ladspa',end='] ')
        fxxml_plugin_key = fxslotX.findall('key')[0]
        fxxml_plugin_ladspacontrols = fxslotX.findall('ladspacontrols')[0]

        fxslotJ['plugin'] = 'ladspa'
        fxcvpj_l_plugindata = {}

        for attribute in fxxml_plugin_key.findall('attribute'):
            attval = attribute.get('value')
            attname = attribute.get('name')
            if attname == 'file':
                if os.path.exists(attval): fxcvpj_l_plugindata['path'] = attval
                else: fxcvpj_l_plugindata['path'] = get_ladspa_path(attval)
            if attname == 'plugin': fxcvpj_l_plugindata['plugin'] = attval

        ladspa_ports = int(fxxml_plugin_ladspacontrols.get('ports'))
        ladspa_linked = fxxml_plugin_ladspacontrols.get('link')
        seperated_channels = False

        if ladspa_linked != None: 
            ladspa_ports //= 2
            if ladspa_linked == "0": seperated_channels = True

        t_params = {}
        t_params["0"] = {}

        for node in fxxml_plugin_ladspacontrols.iter():
            notetagtxt = node.tag
            if notetagtxt.startswith('port'):
                l_ch = notetagtxt[4]
                l_val = notetagtxt[5:]
                t_data = node.get('data')
                if l_ch not in t_params: t_params[l_ch] = {}
                t_params[l_ch][l_val] = float(lmms_auto_getvalue(node, 'data', '0', ['plugin', auto_id_plugin, 'ladspa_param_'+l_ch+'_'+l_val]))

        if seperated_channels == False: 
            fxcvpj_l_plugindata['seperated_channels'] = False
            fxcvpj_l_plugindata['params'] = t_params["0"]
        if seperated_channels == True: 
            fxcvpj_l_plugindata['seperated_channels'] = True
            fxcvpj_l_plugindata['params'] = t_params
        fxslotJ['plugindata'] = fxcvpj_l_plugindata
        return fxslotJ

    else:
        fxxml_plugin = fxslotX.findall(fxlist[fxpluginname])[0]
        print('['+fxpluginname,end='] ')

        auto_id_plugin = get_plugin_auto_id()
        fxslotJ['pluginautoid'] = auto_id_plugin

        fxslotJ['plugin'] = 'native-lmms'
        fxcvpj_l_plugindata['name'] = fxpluginname
        fxcvpj_l_plugindata['data'] = {}

        lmms_autovals = lmms_auto.get_params_fx(fxpluginname)
        for pluginparam in lmms_autovals[0]:
            fxcvpj_l_plugindata['data'][pluginparam] = lmms_auto_getvalue(fxxml_plugin, pluginparam, 0, ['plugin', auto_id_plugin, pluginparam])
        for pluginparam in lmms_autovals[1]:
            xml_pluginparam = fxxml_plugin.get(pluginparam)
            if xml_pluginparam: fxcvpj_l_plugindata['data'][pluginparam] = xml_pluginparam

        fxslotJ['plugindata'] = fxcvpj_l_plugindata
        return fxslotJ

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
        if fxcX.get('muted') != None: fxcJ['muted'] = int(fxcX.get('muted'))
        fxcJ['vol'] = float(lmms_auto_getvalue(fxcX, 'volume', 1, ['fxmixer', fx_num, 'vol']))
        fxchainX = fxcX.find('fxchain')
        if fxchainX != None:
            fxcJ['fxenabled'] = int(fxchainX.get('enabled'))
            fxcJ['chain_fx_audio'] = lmms_decode_fxchain(fxchainX)
        sendlist = []
        sendsxml = fxcX.findall('send')
        for sendxml in sendsxml:
            sendentryjson = {}
            sendentryjson['channel'] = int(sendxml.get('channel'))
            sendentryjson['amount'] = float(sendxml.get('amount'))
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
    def getdawcapabilities(self): return {'fxrack': True}
    def supported_autodetect(self): return True
    def detect(self, input_file):
        output = False
        try:
            tree = ET.parse(input_file)
            root = tree.getroot()
            if root.tag == "lmms-project": output = True
        except ET.ParseError: output = False
        return output
    def parse(self, input_file, extra_param):
        print('[input-lmms] Input Start')
        global lmms_vstpath
        global lmms_ladspapath
        global l_autoid
        global l_autodata
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

        l_autoid = {}
        l_autodata = {}
        l_automation = {}

        tree = ET.parse(input_file).getroot()
        headX = tree.findall('head')[0]
        trksX = tree.findall('song/trackcontainer/track')
        fxX = tree.findall('song/fxmixer/fxchannel')
        tlX = tree.find('song/timeline')
        projnotesX = tree.find('song/projectnotes')

        cvpj_l = {}
        cvpj_l['bpm'] = lmms_auto_getvalue(headX, 'bpm', 140, ['main', 'bpm'])
        cvpj_l['vol'] = hundredto1(float(lmms_auto_getvalue(headX, 'mastervol', 1, ['main', 'vol'])))
        cvpj_l['pitch'] = float(lmms_auto_getvalue(headX, 'masterpitch', 0, ['main', 'pitch']))*100
        cvpj_l['timesig_numerator'] = lmms_auto_getvalue(headX, 'timesig_numerator', 4, None)
        cvpj_l['timesig_denominator'] = lmms_auto_getvalue(headX, 'timesig_denominator', 4, None)

        if projnotesX.text != None: cvpj_l['info'] = {'message': {'type': 'html', 'text': projnotesX.text}}

        lmms_decode_tracks(trksX)
        fxrackdata = lmms_decode_fxmixer(fxX)

        l_automation['main'] = {}
        l_automation['track'] = {}
        l_automation['fxmixer'] = {}
        l_automation['plugin'] = {}

        trackdata = cvpj_l['track_data']

        for part in l_autodata:
            if part in l_autoid:
                s_autopl_id = l_autoid[part]
                s_autopl_data = l_autodata[part]
                if s_autopl_id[0] == 'track':
                    if s_autopl_id[1] in trackdata:
                        if s_autopl_id[1] not in l_automation['track']: l_automation['track'][s_autopl_id[1]] = {}
                        s_trkdata = trackdata[s_autopl_id[1]]
                        temp_pla = l_automation['track'][s_autopl_id[1]]
                        if s_autopl_id[2] == 'vol': temp_pla[s_autopl_id[2]] = auto.multiply(s_autopl_data, 0, 0.01)
                        elif s_autopl_id[2] == 'pan': temp_pla[s_autopl_id[2]] = auto.multiply(s_autopl_data, 0, 0.01)
                        elif s_autopl_id[2] == 'enabled': temp_pla[s_autopl_id[2]] = auto.multiply(s_autopl_data, -1, -1)
                        else: temp_pla[s_autopl_id[2]] = auto.multiply(s_autopl_data, 0, 1)
                if s_autopl_id[0] == 'main':
                    if s_autopl_id[1] == 'vol': l_automation['main'][s_autopl_id[1]] = auto.multiply(s_autopl_data, 0, 0.01)
                    elif s_autopl_id[1] == 'pitch': l_automation['main'][s_autopl_id[1]] = auto.multiply(s_autopl_data, 0, 100)
                    else: l_automation['main'][s_autopl_id[1]] = auto.multiply(s_autopl_data, 0, 1)
                if s_autopl_id[0] == 'fxmixer':
                    if str(s_autopl_id[1]) in fxrackdata:
                        if s_autopl_id[1] not in l_automation['fxmixer']: l_automation['fxmixer'][s_autopl_id[1]] = {}
                        temp_pla = l_automation['fxmixer'][s_autopl_id[1]]
                        if s_autopl_id[2] == 'vol': temp_pla[s_autopl_id[2]] = s_autopl_data
                if s_autopl_id[0] == 'plugin':
                    if s_autopl_id[1] not in l_automation['plugin']: l_automation['plugin'][s_autopl_id[1]] = {}
                    temp_pla = l_automation['plugin'][s_autopl_id[1]]
                    temp_pla[s_autopl_id[2]] = s_autopl_data

                        
        cvpj_l['automation'] = l_automation

        cvpj_l['use_fxrack'] = True
        
        cvpj_l['fxrack'] = fxrackdata

        return json.dumps(cvpj_l, indent=2)
