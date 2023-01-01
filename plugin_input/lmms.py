# SPDX-FileCopyrightText: 2022 Colby Ray
# SPDX-License-Identifier: GPL-3.0-or-later

import base64
import json
import math
import plugin_input
import os
import xml.etree.ElementTree as ET


lfoshape = ['sine', 'tri', 'saw', 'square', 'custom', 'random']
arpdirection = ['up', 'down', 'updown', 'downup', 'random']
filtertype = ['lowpass', 'hipass', 'bandpass_csg', 'bandpass_czpg', 'notch', 'allpass', 'moog', 'lowpass_double', 'lowpass_rc12', 'bandpass_rc12', 'Highpass_rc12', 'lowpass_rc24', 'bandpass_rc24', 'Highpass_rc24', 'formant', 'moog_double', 'lowpass_sv', 'bandpass_sv', 'Highpass_sv', 'notch_sv', 'formant_fast', 'tripole']
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

def getvstparams(plugindata, xmldata):
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
def hex_to_rgb(hexcodeinput):
    hexcode = hexcodeinput.lstrip('#')
    colorbytes = tuple(int(hexcode[i:i+2], 16) for i in (0, 2, 4))
    return [colorbytes[0]/255, colorbytes[1]/255, colorbytes[2]/255]
def hundredto1(lmms_input): return float(lmms_input) * 0.01
def lmms_auto_getvalue(xmltag, xmlname, autoname):
    if xmltag.get(xmlname) != None: return float(xmltag.get(xmlname))
    else:
        realvaluetag = xmltag.findall(xmlname)[0]
        value = realvaluetag.get('value')
        if value != None:
            if autoname != None:
                l_autoid[str(realvaluetag.get('id'))] = autoname
            return realvaluetag.get('value')
        else: return None

def lmms_getvalue_int(json_in, json_name, xml_in): 
    if xml_in != None: json_in['json_name'] = int(xml_in)
def lmms_getvalue_float(json_in, json_name, xml_in): 
    if xml_in != None: json_in['json_name'] = float(xml_in)
def lmms_getvalue_100(json_in, json_name, xml_in): 
    if xml_in != None: json_in['json_name'] = hundredto1(float(xml_in))
def lmms_getvalue_exp(json_in, json_name, xml_in): 
    if xml_in != None: json_in['json_name'] = exp2sec(float(xml_in))

# ------- Instruments and Plugins -------

def exp2sec(value): 
    #print(value, (value*value)*5)
    return (value*value)*5
def asdflfo_get(trkX_insttr, cvpj_l_plugindata):
    elcX = trkX_insttr.findall('eldata')
    if len(elcX) != 0:
        cvpj_l_plugindata_asdrlfo = {}
        eldataX = elcX[0]
        if eldataX.findall('elvol'):
            realvalue = eldataX.findall('elvol')[0]
            asdflfo(cvpj_l_plugindata_asdrlfo, realvalue, 'volume')
        if eldataX.findall('elcut'):
            realvalue = eldataX.findall('elcut')[0]
            asdflfo(cvpj_l_plugindata_asdrlfo, realvalue, 'cutoff')
        if eldataX.findall('elres'):
            realvalue = eldataX.findall('elres')[0]
            asdflfo(cvpj_l_plugindata_asdrlfo, realvalue, 'reso')
        cvpj_l_plugindata['asdrlfo'] = cvpj_l_plugindata_asdrlfo
        filterparams = {}
        lmms_getvalue_float(filterparams, 'cutoff', eldataX.get('fcut'))
        lmms_getvalue_float(filterparams, 'wet', eldataX.get('fwet'))
        if eldataX.get('ftype') != None: filterparams['type'] = filtertype[int(eldataX.get('ftype'))]
        lmms_getvalue_float(filterparams, 'reso', eldataX.get('fres'))

        if filterparams != {}:
            cvpj_l_plugindata['filter'] = {}
            if 'cutoff' in filterparams: cvpj_l_plugindata['filter']['cutoff'] = filterparams['cutoff']
            if 'wet' in filterparams: cvpj_l_plugindata['filter']['wet'] = filterparams['wet']
            if 'type' in filterparams: cvpj_l_plugindata['filter']['type'] = filterparams['type']
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

    cvpj_l_track[asdrtype] = {}
    if envelopeparams != {}:
        cvpj_l_track[asdrtype]['envelope'] = envelopeparams


    lfoparams = {}

    speedx100 = xmlO.get('x100')
    if speedx100 != None: speedx100 == int(speedx100)
    else: speedx100 == 0

    lmms_getvalue_float(lfoparams, 'predelay', xmlO.get('pdel'))
    lmms_getvalue_float(lfoparams, 'attack', xmlO.get('latt'))
    if xmlO.get('lshp') != None: lfoparams['shape'] = lfoshape[int(xmlO.get('lshp'))]
    lmms_getvalue_float(lfoparams, 'amount', xmlO.get('lamt'))

    if xmlO.get('lspd') != None: 
        if speedx100 == 0: lfoparams['speed'] = float(xmlO.get('lspd')) * 20000
        else: lfoparams['speed'] = float(xmlO.get('lspd')) * 2000000

    if lfoparams != {}:
        cvpj_l_track[asdrtype]['lfo'] = lfoparams

def lmms_decodeplugin(trkX_insttr, cvpj_l_plugindata, cvpj_l_inst, cvpj_l_track):
    cvpj_l_inst['plugin'] = "none"
    trkX_instrument = trkX_insttr.findall('instrument')[0]
    pluginname = trkX_instrument.get('name')

    xml_a_plugin = trkX_instrument.findall(pluginname)
    if len(xml_a_plugin) != 0: 
        xml_plugin = xml_a_plugin[0]
        if 'color' not in cvpj_l_track:
            cvpj_l_track['color'] = plugincolors[pluginname]
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
            cvpj_l_plugindata['loop'] = {}
            cvpj_l_plugindata['loop']['custompoints'] = {}
            lmms_getvalue_float(cvpj_l_plugindata['loop']['custompoints'], 'end', xml_plugin.get('eframe'))
            lmms_getvalue_float(cvpj_l_plugindata['loop']['custompoints'], 'loop', xml_plugin.get('lframe'))
            lmms_getvalue_float(cvpj_l_plugindata['loop']['custompoints'], 'start', xml_plugin.get('sframe'))
            looped = int(xml_plugin.get('looped'))
            if looped == 0:
                cvpj_l_plugindata['loop']['enabled'] = 0
            if looped == 1:
                cvpj_l_plugindata['loop']['enabled'] = 1
                cvpj_l_plugindata['loop']['mode'] = "normal"
            if looped == 2:
                cvpj_l_plugindata['loop']['enabled'] = 1
                cvpj_l_plugindata['loop']['mode'] = "pingpong"
            interpolation = int(xml_plugin.get('interp'))
            if interpolation == 0: cvpj_l_plugindata['interpolation'] = "none"
            if interpolation == 1: cvpj_l_plugindata['interpolation'] = "linear"
            if interpolation == 2: cvpj_l_plugindata['interpolation'] = "sinc"
            asdflfo_get(trkX_insttr, cvpj_l_plugindata)
        elif pluginname == "OPL2":
            cvpj_l_inst['plugin'] = "opl2"
            cvpj_l_plugindata['op1'] = {}
            cvpj_l_plugindata['op1']['envelope'] = {}
            cvpj_l_plugindata['op1']['envelope']['attack'] = int(xml_plugin.get('op1_a'))
            cvpj_l_plugindata['op1']['envelope']['decay'] = int(xml_plugin.get('op1_d'))
            cvpj_l_plugindata['op1']['envelope']['release'] = int(xml_plugin.get('op1_r'))
            cvpj_l_plugindata['op1']['envelope']['sustain'] = int(xml_plugin.get('op1_s'))
            cvpj_l_plugindata['op1']['freqmul'] = int(xml_plugin.get('op1_mul'))
            cvpj_l_plugindata['op1']['ksr'] = int(xml_plugin.get('op1_ksr'))
            cvpj_l_plugindata['op1']['level'] = int(xml_plugin.get('op1_lvl'))
            cvpj_l_plugindata['op1']['perc_env'] = int(xml_plugin.get('op1_perc'))
            cvpj_l_plugindata['op1']['scale'] = int(xml_plugin.get('op1_scale'))
            cvpj_l_plugindata['op1']['tremolo'] = int(xml_plugin.get('op1_trem'))
            cvpj_l_plugindata['op1']['vibrato'] = int(xml_plugin.get('op1_vib'))
            cvpj_l_plugindata['op1']['waveform'] = int(xml_plugin.get('op1_waveform'))

            cvpj_l_plugindata['op2'] = {}
            cvpj_l_plugindata['op2']['envelope'] = {}
            cvpj_l_plugindata['op2']['envelope']['attack'] = int(xml_plugin.get('op2_a'))
            cvpj_l_plugindata['op2']['envelope']['decay'] = int(xml_plugin.get('op2_d'))
            cvpj_l_plugindata['op2']['envelope']['release'] = int(xml_plugin.get('op2_r'))
            cvpj_l_plugindata['op2']['envelope']['sustain'] = int(xml_plugin.get('op2_s'))
            cvpj_l_plugindata['op2']['freqmul'] = int(xml_plugin.get('op2_mul'))
            cvpj_l_plugindata['op2']['ksr'] = int(xml_plugin.get('op2_ksr'))
            cvpj_l_plugindata['op2']['level'] = int(xml_plugin.get('op2_lvl'))
            cvpj_l_plugindata['op2']['perc_env'] = int(xml_plugin.get('op2_perc'))
            cvpj_l_plugindata['op2']['scale'] = int(xml_plugin.get('op2_scale'))
            cvpj_l_plugindata['op2']['tremolo'] = int(xml_plugin.get('op2_trem'))
            cvpj_l_plugindata['op2']['vibrato'] = int(xml_plugin.get('op2_vib'))
            cvpj_l_plugindata['op2']['waveform'] = int(xml_plugin.get('op2_waveform'))

            cvpj_l_plugindata['feedback'] = int(xml_plugin.get('feedback'))
            cvpj_l_plugindata['fm'] = int(xml_plugin.get('fm'))
            cvpj_l_plugindata['tremolo_depth'] = int(xml_plugin.get('trem_depth'))
            cvpj_l_plugindata['vibrato_depth'] = int(xml_plugin.get('vib_depth'))
        elif pluginname == "zynaddsubfx":
            cvpj_l_inst['plugin'] = "zynaddsubfx-lmms"
            cvpj_l_plugindata['bandwidth'] = xml_plugin.get('bandwidth')
            cvpj_l_plugindata['filterfreq'] = xml_plugin.get('filterfreq')
            cvpj_l_plugindata['filterq'] = xml_plugin.get('filterq')
            cvpj_l_plugindata['fmgain'] = xml_plugin.get('fmgain')
            cvpj_l_plugindata['forwardmidicc'] = xml_plugin.get('forwardmidicc')
            cvpj_l_plugindata['modifiedcontrollers'] = xml_plugin.get('modifiedcontrollers')
            cvpj_l_plugindata['portamento'] = xml_plugin.get('portamento')
            cvpj_l_plugindata['resbandwidth'] = xml_plugin.get('resbandwidth')
            cvpj_l_plugindata['rescenterfreq'] = xml_plugin.get('rescenterfreq')
            zdata = xml_plugin.findall('ZynAddSubFX-data')[0]
            cvpj_l_plugindata['data'] = base64.b64encode(ET.tostring(zdata, encoding='utf-8')).decode('ascii')
        elif pluginname == "vestige":
            cvpj_l_inst['plugin'] = "vst2"
            getvstparams(cvpj_l_plugindata, xml_plugin)
        else:
            cvpj_l_inst['plugin'] = "native-lmms"
            cvpj_l_plugindata['name'] = pluginname
            cvpj_l_plugindata['data'] = {}
            for name, value in xml_plugin.attrib.items(): cvpj_l_plugindata['data'][name] = value
            for name in xml_plugin: cvpj_l_plugindata['data'][name.tag] = name.get('value')
            asdflfo_get(trkX_insttr, cvpj_l_plugindata)

# ------- Notelist -------

def note_list_getduration(notelistjsontable):
    notelistdurationfinal = 0
    for x in notelistjsontable:
        notelistduration = x['position'] + x['duration']
        if notelistduration > notelistdurationfinal:
            notelistdurationfinal = notelistduration
    return notelistdurationfinal
def lmms_decode_nlpattern(notesX):
    notelist = []
    printcountpat = 0
    for noteX in notesX:
        noteJ = {}
        noteJ['key'] = int(noteX.get('key')) - 60
        noteJ['position'] = float(noteX.get('pos')) / 12
        noteJ['pan'] = hundredto1(noteX.get('pan'))
        noteJ['duration'] = float(noteX.get('len')) / 12
        noteJ['vol'] = hundredto1(noteX.get('vol'))
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
        notesX = patX.findall('note')
        notesJ = lmms_decode_nlpattern(notesX)
        placeJ["notelist"] = notesJ
        placeJ["duration"] = note_list_getduration(notesJ)
        nlplacements.append(placeJ)
    print(' ')
    return nlplacements

# ------- Track: Inst -------

def lmms_decode_inst_track(trkX, name):
    cvpj_l_track = {}
    cvpj_l_inst = {}
    cvpj_l_inst['notefx'] = {}
    cvpj_l_inst_plugin = {}
    cvpj_l_track_inst = cvpj_l_inst
    cvpj_l_track_inst['plugindata'] = cvpj_l_inst_plugin
    cvpj_l_track['type'] = "instrument"
    cvpj_l_track['placements'] = {}

    cvpj_l_track['name'] = trkX.get('name')
    print('[input-lmms] Instrument Track')
    print('[input-lmms]       Name: ' + cvpj_l_track['name'])

    mutedval = int(lmms_auto_getvalue(trkX, 'muted', ['track', name, 'enabled']))
    cvpj_l_track['enabled'] = int(not int(mutedval))
    cvpj_l_track['solo'] = int(trkX.get('solo'))

    cvpj_l_inst_notefx = cvpj_l_inst['notefx']

    #trkX_insttr
    trkX_insttr = trkX.findall('instrumenttrack')[0]
    cvpj_l_track['fxrack_channel'] = int(trkX_insttr.get('fxch'))
    cvpj_l_track['pan'] = hundredto1(float(lmms_auto_getvalue(trkX_insttr, 'pan', ['track', name, 'pan'])))
    cvpj_l_track['vol'] = hundredto1(float(lmms_auto_getvalue(trkX_insttr, 'vol', ['track', name, 'vol'])))
    
    if trkX.get('color') != None:
        cvpj_l_track['color'] = hex_to_rgb(trkX.get('color'))

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
        cvpj_l_inst['midi'] = midiJ

    xml_a_fxchain = trkX_insttr.findall('fxchain')
    if len(xml_a_fxchain) != 0: cvpj_l_track['fxchain'] = lmms_decode_fxchain(xml_a_fxchain[0])

    cvpj_l_track_inst['usemasterpitch'] = int(trkX_insttr.get('usemasterpitch'))

    # notefx
    cvpj_l_track_inst['pitch'] = 0
    if trkX_insttr.get('pitch') != None: cvpj_l_track_inst['pitch'] = float(trkX_insttr.get('pitch'))
    cvpj_l_track_inst['pitch'] = float(lmms_auto_getvalue(trkX_insttr, 'pitch', ['track', name, 'pitch']))

    xml_a_chordcreator = trkX_insttr.findall('chordcreator')
    if len(xml_a_chordcreator) != 0:
        trkX_chordcreator = xml_a_chordcreator[0]
        cvpj_l_inst_notefx['chordcreator'] = {}
        cvpj_l_inst_notefx['chordcreator']['enabled'] = int(trkX_chordcreator.get('chord-enabled'))
        cvpj_l_inst_notefx['chordcreator']['chordrange'] = int(trkX_chordcreator.get('chordrange'))
        cvpj_l_inst_notefx['chordcreator']['chord'] = ','.join(str(item) for item in chord[int(trkX_chordcreator.get('chord'))])

    xml_a_chordcreator = trkX_insttr.findall('arpeggiator')
    if len(xml_a_chordcreator) != 0:
        trkX_arpeggiator = xml_a_chordcreator[0]
        cvpj_l_inst_notefx['arpeggiator'] = {}
        cvpj_l_inst_notefx['arpeggiator']['gate'] = int(trkX_arpeggiator.get('arpgate'))
        cvpj_l_inst_notefx['arpeggiator']['arprange'] = int(trkX_arpeggiator.get('arprange'))
        cvpj_l_inst_notefx['arpeggiator']['enabled'] = int(trkX_arpeggiator.get('arp-enabled'))
        cvpj_l_inst_notefx['arpeggiator']['mode'] = int(trkX_arpeggiator.get('arpmode'))
        cvpj_l_inst_notefx['arpeggiator']['direction'] = arpdirection[int(trkX_arpeggiator.get('arpdir'))]
        cvpj_l_inst_notefx['arpeggiator']['miss'] = int(trkX_arpeggiator.get('arpmiss'))
        cvpj_l_inst_notefx['arpeggiator']['skiprate'] = hundredto1(int(trkX_arpeggiator.get('arpskip')))
        cvpj_l_inst_notefx['arpeggiator']['time'] = {'value': float(trkX_arpeggiator.get('arptime')), 'type': 'ms'}
        cvpj_l_inst_notefx['arpeggiator']['missrate'] = hundredto1(int(trkX_arpeggiator.get('arpmiss')))
        cvpj_l_inst_notefx['arpeggiator']['cyclenotes'] = int(trkX_arpeggiator.get('arpcycle'))
        cvpj_l_inst_notefx['arpeggiator']['chord'] = ','.join(str(item) for item in chord[int(trkX_arpeggiator.get('arp'))])

    cvpj_l_track_plugindata = cvpj_l_track_inst['plugindata']
    lmms_decodeplugin(trkX_insttr, cvpj_l_track_plugindata, cvpj_l_inst, cvpj_l_track)

    xml_a_chordcreator = trkX_insttr.findall('arpeggiator')

    if 'basenote' in trkX_insttr.attrib:
        basenote = int(trkX_insttr.get('basenote'))-57
        noteoffset = 0
        if cvpj_l_track_inst['plugin'] == 'sampler': noteoffset = 3
        if cvpj_l_track_inst['plugin'] == 'soundfont2': noteoffset = 12

        cvpj_l_inst_notefx['pitch'] = {}
        cvpj_l_inst_notefx['pitch']['semitones'] = basenote - noteoffset

    cvpj_l_track['placements'] = lmms_decode_nlplacements(trkX)

    cvpj_l_track['instdata'] = cvpj_l_inst
    print('[input-lmms]')
    return cvpj_l_track

# ------- Track: Automation -------

def auto_multiply(s_autopl_data, addval, mulval):
    for autopl in s_autopl_data:
        if 'points' in autopl:
            for point in autopl['points']:
                if 'value' in point:
                    point['value'] = (point['value']*mulval)+addval
    return s_autopl_data

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
    print('[input-lmms]       Placements: ', end='')
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

    if fxpluginname == 'vsteffect':
        fxxml_plugin = fxslotX.findall(fxlist[fxpluginname])[0]
        print('[vst2',end='] ')
        fxslotJ['plugin'] = "vst2"
        getvstparams(fxcvpj_l_plugindata, fxxml_plugin)
        fxslotJ['plugindata'] = fxcvpj_l_plugindata
        return fxslotJ
    elif fxpluginname != 'ladspaeffect':
        fxxml_plugin = fxslotX.findall(fxlist[fxpluginname])[0]
        print('['+fxpluginname,end='] ')
        fxslotJ['plugin'] = 'native-lmms'
        fxcvpj_l_plugindata['name'] = fxpluginname
        fxcvpj_l_plugindata['data'] = {}
        for name, value in fxxml_plugin.attrib.items(): fxcvpj_l_plugindata['data'][name] = value
        for name in fxxml_plugin: fxcvpj_l_plugindata['data'][name.tag] = name.get('value')
        fxslotJ['plugindata'] = fxcvpj_l_plugindata
        return fxslotJ
    else:
        return None
def lmms_decode_fxchain(fxchainX):
    print('[input-lmms]       FX Chain: ',end='')
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
        fxcJ['vol'] = float(fxcX.get('volume'))
        fxchainX = fxcX.find('fxchain')
        if fxchainX != None:
            fxcJ['fxenabled'] = int(fxchainX.get('enabled'))
            fxcJ['fxchain'] = lmms_decode_fxchain(fxchainX)
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
    tracklist = {}
    instdata = {}
    trackordering = []
    idtracknum = 0
    for trkX in trksX:
        idtracknum += 1
        tracktype = trkX.get('type')
        if tracktype == "0":
            tracklist['LMMS_Inst_'+str(idtracknum)] = lmms_decode_inst_track(trkX, 'LMMS_Inst_'+str(idtracknum))
            trackordering.append('LMMS_Inst_'+str(idtracknum))
        if tracktype == "5":
            lmms_decode_auto_track(trkX)
    return [tracklist, trackordering]

class input_lmms(plugin_input.base):
    def __init__(self): pass
    def getshortname(self): return 'lmms'
    def getname(self): return 'LMMS'
    def gettype(self): return 'r'
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
        homepath = os.path.expanduser('~')
        lmmsconfigpath = homepath+'\\.lmmsrc.xml'
        if os.path.exists(lmmsconfigpath):
            lmmsconfX = ET.parse(lmmsconfigpath).getroot()
            lmmsconf_pathsX = lmmsconfX.findall('paths')[0]
            lmms_vstpath = lmmsconf_pathsX.get('vstdir')
        else: lmms_vstpath = ''

        global l_autoid
        global l_autodata
        l_autoid = {}
        l_autodata = {}
        main_autoplacements = {}

        tree = ET.parse(input_file).getroot()
        headX = tree.findall('head')[0]
        trksX = tree.findall('song/trackcontainer/track')
        fxX = tree.findall('song/fxmixer/fxchannel')
        tlX = tree.find('song/timeline')
        projnotesX = tree.find('song/projectnotes')

        bpm = 140
        if headX.get('bpm') != None: bpm = float(headX.get('bpm'))

        rootJ = {}
        if headX.get('mastervol') != None: rootJ['mastervol'] = hundredto1(float(lmms_auto_getvalue(headX, 'mastervol', ['main', 'mastervol'])))
        if headX.get('masterpitch') != None: rootJ['masterpitch'] = float(lmms_auto_getvalue(headX, 'masterpitch', ['main', 'masterpitch']))*100
        if headX.get('timesig_numerator') != None: rootJ['timesig_numerator'] = lmms_auto_getvalue(headX, 'timesig_numerator', None)
        if headX.get('timesig_denominator') != None: rootJ['timesig_denominator'] = lmms_auto_getvalue(headX, 'timesig_denominator', None)
        rootJ['bpm'] = lmms_auto_getvalue(headX, 'bpm', ['main', 'bpm'])

        if projnotesX.text != None:
            rootJ['message'] = {}
            rootJ['message']['type'] = 'html'
            rootJ['message']['text'] = projnotesX.text

        trackdata, trackordering = lmms_decode_tracks(trksX)

        for part in l_autodata:
            s_autopl_id = l_autoid[part]
            s_autopl_data = l_autodata[part]
            #print()
            #print(s_autopl_id)
            #print(s_autopl_data)
            if s_autopl_id[0] == 'track':
                if s_autopl_id[1] in trackdata:
                    s_trkdata = trackdata[s_autopl_id[1]]
                    if 'placements_auto_main' not in s_trkdata: s_trkdata['placements_auto_main'] = {}
                    temp_pla = s_trkdata['placements_auto_main']
                    if s_autopl_id[2] == 'vol': temp_pla[s_autopl_id[2]] = auto_multiply(s_autopl_data, 0, 0.01)
                    elif s_autopl_id[2] == 'pan': temp_pla[s_autopl_id[2]] = auto_multiply(s_autopl_data, 0, 0.01)
                    elif s_autopl_id[2] == 'enabled': temp_pla[s_autopl_id[2]] = auto_multiply(s_autopl_data, 1, -1)
                    else: temp_pla[s_autopl_id[2]] = auto_multiply(s_autopl_data, 0, 1)
            else:
                if s_autopl_id[1] == 'mastervol': main_autoplacements[s_autopl_id[1]] = auto_multiply(s_autopl_data, 0, 0.01)
                elif s_autopl_id[1] == 'masterpitch': main_autoplacements[s_autopl_id[1]] = auto_multiply(s_autopl_data, 0, 100)
                else: main_autoplacements[s_autopl_id[1]] = auto_multiply(s_autopl_data, 0, 1)


        rootJ['trackdata'] = trackdata
        rootJ['trackordering'] = trackordering
        rootJ['placements_auto_main'] = main_autoplacements
        rootJ['fxrack'] = lmms_decode_fxmixer(fxX)

        return json.dumps(rootJ, indent=2)
