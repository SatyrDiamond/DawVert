# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import base64
import json
import lxml.etree as ET
import math
import plugin_output
from pathlib import Path
from functions_plugin import lmms_auto
from functions import auto
from functions import placements
from functions import data_values
from functions import plugins
from functions import note_mod
from functions import notelist_data
from functions import song_convert
from functions import colors
from functions import tracks
from functions import params

lfoshape = {'sine': 0,'tri': 1,'saw': 2,'square': 3,'custom': 4,'random': 5}
chord = {'0': 0, '0,4,7': 1, '0,4,6': 2, '0,3,7': 3, '0,3,6': 4, '0,2,7': 5, '0,5,7': 6, '0,4,8': 7, '0,5,8': 8, '0,3,6,9': 9, '0,4,7,9': 10, '0,5,7,9': 11, '0,4,7,9,14': 12, '0,3,7,9': 13, '0,3,7,9,14': 14, '0,4,7,10': 15, '0,5,7,10': 16, '0,4,8,10': 17, '0,4,6,10': 18, '0,4,7,10,15': 19, '0,4,7,10,13': 20, '0,4,8,10,15': 21, '0,4,8,10,13': 22, '0,4,6,10,13': 23, '0,4,7,10,17': 24, '0,4,7,10,21': 25, '0,4,7,10,18': 26, '0,4,7,11': 27, '0,4,6,11': 28, '0,4,8,11': 29, '0,4,7,11,18': 30, '0,4,7,11,21': 31, '0,3,7,10': 32, '0,3,6,10': 33, '0,3,7,10,13': 34, '0,3,7,10,17': 35, '0,3,7,10,21': 36, '0,3,7,11': 37, '0,3,7,11,17': 38, '0,3,7,11,21': 39, '0,4,7,10,14': 40, '0,5,7,10,14': 41, '0,4,7,14': 42, '0,4,8,10,14': 43, '0,4,6,10,14': 44, '0,4,7,10,14,18': 45, '0,4,7,10,14,20': 46, '0,4,7,11,14': 47, '0,5,7,11,15': 48, '0,4,8,11,14': 49, '0,4,7,11,14,18': 50, '0,3,7,10,14': 51, '0,3,7,14': 52, '0,3,6,10,14': 53, '0,3,7,11,14': 54, '0,4,7,10,14,17': 55, '0,4,7,10,13,17': 56, '0,4,7,11,14,17': 57, '0,3,7,10,14,17': 58, '0,3,7,11,14,17': 59, '0,4,7,10,14,21': 60, '0,4,7,10,15,21': 61, '0,4,7,10,13,21': 62, '0,4,6,10,13,21': 63, '0,4,7,11,14,21': 64, '0,3,7,10,14,21': 65, '0,3,7,11,14,21': 66, '0,2,4,5,7,9,11': 67, '0,2,3,5,7,8,11': 68, '0,2,3,5,7,9,11': 69, '0,2,4,6,8,10': 70, '0,2,3,5,6,8,9,11': 71, '0,2,4,7,9': 72, '0,3,5,7,10': 73, '0,1,5,7,10': 74, '0,2,4,5,7,8,9,11': 75, '0,2,4,5,7,9,10,11': 76, '0,3,5,6,7,10': 77, '0,1,4,5,7,8,11': 78, '0,1,4,6,8,10,11': 79, '0,1,3,5,7,9,11': 80, '0,1,3,5,7,8,11': 81, '0,2,3,6,7,8,11': 82, '0,2,3,5,7,9,10': 83, '0,1,3,5,7,8,10': 84, '0,2,4,6,7,9,11': 85, '0,2,4,5,7,9,10': 86, '0,2,3,5,7,8,10': 87, '0,1,3,5,6,8,10': 88, '0,1,2,3,4,5,6,7,8,9,10,11': 90, '0,1,3,4,6,7,9,10': 91, '0,7': 92, '0,1,4,5,7,8,10': 93, '0,1,4,5,6,8,11': 94}
arpdirection = {'up': 0,'down': 1,'updown': 2,'downup': 3,'random': 4}
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

patternscount_forprinting = 0
notescount_forprinting = 0
trackscount_forprinting = 0

# ------- functions -------

def setvstparams(cvpj_plugindata, pluginid, xmldata):

    vstpath = data_values.get_value(cvpj_plugindata, 'path', '')
    xmldata.set('program', str(data_values.get_value(cvpj_plugindata, 'current_program', 0)) )
    xmldata.set('plugin', vstpath)

    xml_vst_key = ET.SubElement(xmldata, 'key')
    xml_vst_key_file = ET.SubElement(xml_vst_key, 'attribute')
    xml_vst_key_file.set('name', 'file')
    xml_vst_key_file.set('value', vstpath)

    middlenotefix = data_values.get_value(cvpj_plugindata, 'middlenotefix', 0)

    datatype = data_values.get_value(cvpj_plugindata, 'datatype', 'none')
    numparams = data_values.get_value(cvpj_plugindata, 'numparams', 0)

    if datatype == 'chunk':
        xmldata.set('chunk', data_values.get_value(cvpj_plugindata, 'chunk', 0))

    if datatype == 'param':
        xmldata.set('numparams', str(data_values.get_value(cvpj_plugindata, 'numparams', 0)))
        for param in range(numparams):
            pval, ptype, pname = plugins.get_plug_param(cvpj_l, pluginid, 'vst_param_'+str(param), 0)
            xmldata.set('param'+str(param), str(param)+':'+pname+':'+str(pval))
             
    pluginautoid = tracks.autoid_out_getlist(['plugin', pluginid])
    if pluginautoid != None:
        for paramname in pluginautoid:
            if 'vst_param_' in paramname:
                paramid = paramname[10:]
                paramvisname = int(paramname[10:])+1
                aid_id, aid_data = tracks.autoid_out_get(['plugin', pluginid, paramname])
                if aid_id != None and len(aid_data['placements']) != 0:
                    lmms_make_main_auto_track(aid_id, aid_data, 'VST2: #'+str(paramvisname))
                    autovarX = ET.SubElement(xmldata, 'param'+paramid)
                    autovarX.set('scale_type', 'linear')
                    autovarX.set('id', str(aid_id))

    return middlenotefix


def onetime2lmmstime(input): return int(round(float(input * 12)))

def oneto100(input): return round(float(input) * 100)

def sec2exp(value): return math.sqrt(value/5)

# ------- Instruments and Plugins -------

def asdrlfo_set(pluginid, trkX_insttr):
    eldataX = ET.SubElement(trkX_insttr, "eldata")

    filt_enabled, filt_cutoff, filt_reso, filt_type, filt_subtype = plugins.get_filter(cvpj_l, pluginid)
    eldataX.set('fcut', str(filt_cutoff))
    filtertable_e = [filt_type, filt_subtype]
    lmms_filternum = None
    if filtertable_e[0] == 'allpass': lmms_filternum = 5

    if filtertable_e[0] == 'bandpass':
        if filtertable_e[1] == 'csg': lmms_filternum = 2
        if filtertable_e[1] == 'czpg': lmms_filternum = 3
        if filtertable_e[1] == 'rc12': lmms_filternum = 9
        if filtertable_e[1] == 'rc24': lmms_filternum = 12
        if filtertable_e[1] == 'sv': lmms_filternum = 17

    if filtertable_e[0] == 'formant':
        lmms_filternum = 14
        if filtertable_e[1] == 'fast': lmms_filternum = 20

    if filtertable_e[0] == 'highpass':
        lmms_filternum = 1
        if filtertable_e[1] == 'rc12': lmms_filternum = 10
        if filtertable_e[1] == 'rc24': lmms_filternum = 13
        if filtertable_e[1] == 'sv': lmms_filternum = 18

    if filtertable_e[0] == 'lowpass':
        lmms_filternum = 0
        if filtertable_e[1] == 'double': lmms_filternum = 7
        if filtertable_e[1] == 'rc12': lmms_filternum = 8
        if filtertable_e[1] == 'rc24': lmms_filternum = 11
        if filtertable_e[1] == 'sv': lmms_filternum = 16

    if filtertable_e[0] == 'moog':
        lmms_filternum = 6
        if filtertable_e[1] == 'double': lmms_filternum = 15

    if filtertable_e[0] == 'notch':
        lmms_filternum = 4
        if filtertable_e[1] == 'sv': lmms_filternum = 19

    if filtertable_e[0] == 'tripole':
        lmms_filternum = 21

    if lmms_filternum != None: eldataX.set('ftype', str(lmms_filternum))
    eldataX.set('fwet', str(int(filt_enabled)))
    eldataX.set('fres', str(filt_reso))

    asdrlfo(pluginid, eldataX, 'vol', 'vol')
    asdrlfo(pluginid, eldataX, 'cutoff', 'cut')
    asdrlfo(pluginid, eldataX, 'reso', 'res')

def asdrlfo(pluginid, xmlobj, asdrtype, xmltype):

    elmodX = ET.SubElement(xmlobj, 'el' + xmltype)

    a_predelay, a_attack, a_hold, a_decay, a_sustain, a_release, a_amount = plugins.get_asdr_env(cvpj_l, pluginid, asdrtype)
    t_attack, t_decay, t_release = plugins.get_asdr_env_tension(cvpj_l, pluginid, asdrtype)
    a_attack *= pow(2, min(t_attack*3.14, 0))
    a_decay *= pow(2, min(t_decay*3.14, 0))
    a_release *= pow(2, min(t_release*3.14, 0))

    if asdrtype == 'cutoff': elmodX.set('amt', str(a_amount/6000))
    else: elmodX.set('amt', str(float(a_amount)))
    elmodX.set('pdel', str(sec2exp(a_predelay)))
    elmodX.set('att', str(sec2exp(a_attack)))
    elmodX.set('hold', str(sec2exp(a_hold)))
    elmodX.set('dec', str(sec2exp(a_decay)))
    elmodX.set('sustain', str(a_sustain))
    elmodX.set('rel', str(sec2exp(a_release)))

    l_predelay, l_attack, l_shape, l_speed_type, l_speed_time, l_amount = plugins.get_lfo(cvpj_l, pluginid, asdrtype)
    if asdrtype == 'cutoff': elmodX.set('lamt', str(l_amount/1500))
    else: elmodX.set('lamt', str(l_amount))
    elmodX.set('lpdel', str(l_predelay))
    elmodX.set('latt', str(sec2exp(l_attack)))
    elmodX.set('lshp', str(lfoshape[l_shape]))
    elmodX.set('x100', '0')
    lfospeed = 1
    if l_speed_type == 'seconds': lfospeed = float(l_speed_time) / 20
    if lfospeed > 1:
        elmodX.set('x100', '1')
        lfospeed = lfospeed/100
    elmodX.set('lspd', str(lfospeed))
    elmodX.set('lshp', str(lfoshape[l_shape]))

def get_plugin_param(pluginautoid, xmltag, xmlname, pluginid, paramname, fallback, **kwargs):
    pluginparam = plugins.get_plug_param(cvpj_l, pluginid, paramname, fallback)

    aid_id, aid_data = tracks.autoid_out_get(['plugin', pluginid, paramname])

    if pluginparam[1] != 'bool': outparam = pluginparam[0]
    else: outparam = int(pluginparam[0])

    if pluginparam[2] != '': v_name = pluginparam[2]
    else: v_name = paramname

    visname = 'Plugin: '+v_name

    if 'visualname' in kwargs: visname = kwargs['visualname']

    if aid_id != None and len(aid_data['placements']) != 0:
        aid_data['placements'] = auto.multiply(aid_data['placements'], 0, 1)
        lmms_make_main_auto_track(aid_id, aid_data, visname)
        autovarX = ET.SubElement(xmltag, xmlname)
        autovarX.set('value', str(outparam))
        autovarX.set('scale_type', 'linear')
        autovarX.set('id', str(aid_id))
        for name in kwargs:
            autovarX.set(name, str(kwargs[name]))
        return autovarX
    else:
        xmltag.set(xmlname, str(outparam))



def lmms_encode_plugin(xmltag, trkJ, trackid, trackname, trkX_insttr):
    instJ = data_values.get_value(trkJ, 'instdata', {})
    xml_instrumentpreplugin = ET.SubElement(xmltag, "instrument")

    visual_plugname = 'none'
    middlenotefix = 0

    if 'pluginid' in instJ: 
        pluginid = instJ['pluginid']
        plugintype = plugins.get_plug_type(cvpj_l, pluginid)

        visual_plugname = str(plugintype[0])+' ('+str(plugintype[1])+')'

        cvpj_plugindata = plugins.get_plug_data(cvpj_l, pluginid)

        pluginautoid = tracks.autoid_out_getlist(['plugin', pluginid])

        if plugintype == ['sampler', 'single']:
            print('[output-lmms]       Plugin: Sampler (Single) > audiofileprocessor')
            xml_instrumentpreplugin.set('name', "audiofileprocessor")
            xml_sampler = ET.SubElement(xml_instrumentpreplugin, "audiofileprocessor")

            xml_sampler.set('reversed', str(int(data_values.get_value(cvpj_plugindata, 'reverse', 0))))
            xml_sampler.set('amp', str(oneto100(data_values.get_value(cvpj_plugindata, 'amp', 1))))
            xml_sampler.set('stutter', str(int(data_values.get_value(cvpj_plugindata, 'continueacrossnotes', False))))
            xml_sampler.set('src', data_values.get_value(cvpj_plugindata, 'file', ''))

            point_value_type = data_values.get_value(cvpj_plugindata, 'point_value_type', 'samples')

            if point_value_type == 'samples' and 'length' in cvpj_plugindata:
                trkJ_length = cvpj_plugindata['length']
                if trkJ_length != 0:
                    if 'start' in cvpj_plugindata: xml_sampler.set('sframe', str(cvpj_plugindata['start']/trkJ_length))
                    else: xml_sampler.set('sframe', '0')
                    if 'loop' in cvpj_plugindata:
                        trkJ_loop = cvpj_plugindata['loop']
                        if 'points' in trkJ_loop:
                            trkJ_loop_points = trkJ_loop['points']
                            start = trkJ_loop_points[0] / trkJ_length
                            end = trkJ_loop_points[1] / trkJ_length
                            if end == 0 or start == end: end = 1.0
                            xml_sampler.set('lframe', str(start))
                            xml_sampler.set('eframe', str(end))

            if point_value_type == 'percent':
                if 'start' in cvpj_plugindata: xml_sampler.set('sframe', str(cvpj_plugindata['start']))
                else: xml_sampler.set('sframe', '0')
                if 'loop' in cvpj_plugindata:
                    trkJ_loop = cvpj_plugindata['loop']
                    if 'points' in trkJ_loop:
                        trkJ_loop_points = trkJ_loop['points']
                        xml_sampler.set('lframe', str(trkJ_loop_points[0]))
                        xml_sampler.set('eframe', str(trkJ_loop_points[1]))

            loopenabled = 0
            loopmode = "normal"
            if 'loop' in cvpj_plugindata:
                trkJ_loop = cvpj_plugindata['loop']
                if 'enabled' in trkJ_loop: loopenabled = trkJ_loop['enabled']
                if 'mode' in trkJ_loop: loopmode = trkJ_loop['mode']
            if loopenabled == 0: xml_sampler.set('looped', '0')
            if loopenabled == 1:
                if loopmode == "normal": xml_sampler.set('looped', '1')
                if loopmode == "pingpong": xml_sampler.set('looped', '2')
            interpolation = "none"
            if 'interpolation' in cvpj_plugindata: interpolation = cvpj_plugindata['interpolation']
            if interpolation == "none": xml_sampler.set('interp', '0')
            if interpolation == "linear": xml_sampler.set('interp', '1')
            if interpolation == "sinc": xml_sampler.set('interp', '2')
            else: xml_sampler.set('interp', '2')
            middlenotefix += 3

        elif plugintype[0] == 'soundfont2':
            print('[output-lmms]       Plugin: soundfont2 > sf2player')
            xml_instrumentpreplugin.set('name', "sf2player")
            xml_sf2 = ET.SubElement(xml_instrumentpreplugin, "sf2player")
            xml_sf2.set('bank', str(int(data_values.get_value(cvpj_plugindata, 'bank', 0))))
            xml_sf2.set('patch', str(int(data_values.get_value(cvpj_plugindata, 'patch', 0))))
            xml_sf2.set('src', str(data_values.get_value(cvpj_plugindata, 'file', '')))
            get_plugin_param(pluginautoid, xml_sf2, 'gain', pluginid, 'gain', 1)
            get_plugin_param(pluginautoid, xml_sf2, 'chorusDepth', pluginid, 'chorus_depth', 0)
            get_plugin_param(pluginautoid, xml_sf2, 'chorusLevel', pluginid, 'chorus_level', 0)
            get_plugin_param(pluginautoid, xml_sf2, 'chorusNum', pluginid, 'chorus_lines', 0)
            get_plugin_param(pluginautoid, xml_sf2, 'chorusOn', pluginid, 'chorus_enabled', 0)
            get_plugin_param(pluginautoid, xml_sf2, 'chorusSpeed', pluginid, 'chorus_speed', 0)
            get_plugin_param(pluginautoid, xml_sf2, 'reverbDamping', pluginid, 'reverb_damping', 0)
            get_plugin_param(pluginautoid, xml_sf2, 'reverbLevel', pluginid, 'reverb_level', 0)
            get_plugin_param(pluginautoid, xml_sf2, 'reverbOn', pluginid, 'reverb_enabled', 0)
            get_plugin_param(pluginautoid, xml_sf2, 'reverbRoomSize', pluginid, 'reverb_roomsize', 0)
            get_plugin_param(pluginautoid, xml_sf2, 'reverbWidth', pluginid, 'reverb_width', 0)
            middlenotefix = 12

        elif plugintype == ['fm', 'opl2']:
            print('[output-lmms]       Plugin: OPL2 > OPL2')
            xml_instrumentpreplugin.set('name', "OPL2")
            xml_opl2 = ET.SubElement(xml_instrumentpreplugin, "OPL2")
            for opnum in range(2):
                opl2_optxt = 'op'+str(opnum+1)
                for varname in opl2opvarnames:
                    get_plugin_param(pluginautoid, xml_opl2, opl2_optxt+varname[0], pluginid, opl2_optxt+varname[1], 0)
            for varname in opl2varnames:
                get_plugin_param(pluginautoid, xml_opl2, varname[0], pluginid, varname[1], 0)

        elif plugintype == ['vst2', 'win']:
            print('[output-lmms]       Plugin: vst2 > vestige')
            xml_instrumentpreplugin.set('name', "vestige")
            xml_vst = ET.SubElement(xml_instrumentpreplugin, "vestige")
            middlenotefix += setvstparams(cvpj_plugindata, pluginid, xml_vst)

        elif plugintype[0] == 'native-lmms':
            print('[output-lmms]       Plugin: '+plugintype[1]+' > '+plugintype[1])
            xml_instrumentpreplugin.set('name', plugintype[1])
            xml_lmmsnat = ET.SubElement(xml_instrumentpreplugin, plugintype[1])
            lmms_autovals = lmms_auto.get_params_inst(plugintype[1])
            for pluginparam in lmms_autovals[0]: 
                get_plugin_param(pluginautoid, xml_lmmsnat, pluginparam, pluginid, pluginparam, 0)
            for pluginparam in lmms_autovals[1]: 
                xml_lmmsnat.set(pluginparam, 
                    str(plugins.get_plug_dataval(cvpj_l, pluginid, pluginparam, ''))
                    )
            if plugintype[1] == 'zynaddsubfx':
                zdata = cvpj_plugindata['data'].encode('ascii')
                zdataxs = ET.fromstring(base64.b64decode(zdata).decode('ascii'))
                xml_lmmsnat.append(zdataxs)
            if plugintype[1] == 'tripleoscillator':
                for names in [['userwavefile0', 'osc_1'],
                            ['userwavefile1', 'osc_2'],
                            ['userwavefile2', 'osc_3']]:
                    filedata = plugins.get_fileref(cvpj_l, pluginid, names[1])
                    if filedata != None: xml_lmmsnat.set(names[0], filedata['path'])

        else:
            print('[output-lmms]       Plugin: '+visual_plugname+' > None')
            xml_instrumentpreplugin.set('name', "audiofileprocessor")
            paramlist = plugins.get_plug_paramlist(cvpj_l, pluginid)

            if trackname not in ['', None]: visual_plugname = trackname
            add_auto_unused(paramlist, pluginautoid, pluginid, visual_plugname)

        asdrlfo_set(pluginid, trkX_insttr)

    else:
        plugintype = [None, None]
        print('[output-lmms]       Plugin: '+visual_plugname+' > None')
        xml_instrumentpreplugin.set('name', "audiofileprocessor")

    return plugintype, middlenotefix

# ------- Inst and Notelist -------

def lmms_encode_notelist(xmltag, json_notelist):
    printcountpat = 0
    json_notelist = notelist_data.sort(json_notelist)

    for json_note in json_notelist:
        global notescount_forprinting
        notescount_forprinting += 1
        patX = ET.SubElement(xmltag, "note")
        key = json_note['key'] + 60
        position = int(round(float(json_note['position']) * 12))
        pan = 0
        if 'pan' in json_note: pan = oneto100(json_note['pan'])
        duration = int(round(float(json_note['duration']) * 12))
        if 'vol' in json_note: vol = oneto100(json_note['vol'])
        else: vol = 100
        patX.set('key', str(key))
        patX.set('pos', str(int(round(position))))
        patX.set('pan', str(pan))
        patX.set('len', str(int(round(duration))))
        patX.set('vol', str(vol))
        if 'notemod' in json_note:
            if 'auto' in json_note['notemod']:
                if 'pitch' in json_note['notemod']['auto']:
                    xml_automationpattern = ET.SubElement(patX, "automationpattern")
                    xml_detuning = ET.SubElement(xml_automationpattern, "detuning")
                    xml_detuning.set('pos', "0")
                    xml_detuning.set('len', str(int(round(duration))))
                    xml_detuning.set('tens', "1")
                    xml_detuning.set('name', "")
                    xml_detuning.set('mute', "0")
                    xml_detuning.set('prog', "1")
                    parse_auto(xml_detuning, json_note['notemod']['auto']['pitch'], 'float')
                    note_mod.notemod_conv(json_note['notemod'])

        printcountpat += 1
    print('['+str(printcountpat), end='] ')

def lmms_encode_inst_track(xmltag, trkJ, trackid, trkplacementsJ):
    global trkcX
    global trackscount_forprinting
    trackscount_forprinting += 1

    auto_nameiddata = {}

    xmltag.set('type', "0")

    if 'solo' in trkJ: xmltag.set('solo', str(trkJ['solo']))
    else: xmltag.set('solo', '0')

    if 'name' in trkJ: trackname = trkJ['name']
    else: trackname = 'noname'
    xmltag.set('name', trackname)

    if 'color' in trkJ: xmltag.set('color', '#' + colors.rgb_float_2_hex(trkJ['color']))

    if 'instdata' not in trkJ: instJ = {}
    else: instJ = trkJ['instdata']

    #instrumenttrack
    trkX_insttr = ET.SubElement(xmltag, "instrumenttrack")
    trkX_insttr.set('usemasterpitch', "1")
    if 'usemasterpitch' in instJ: trkX_insttr.set('usemasterpitch', str(instJ['usemasterpitch']))
    trkX_insttr.set('pitch', "0")
    if 'plugin' in instJ: instplugin = instJ['plugin']
    else: instplugin = None

    if 'fxrack_channel' in trkJ: trkX_insttr.set('fxch', str(trkJ['fxrack_channel']))
    else: trkX_insttr.set('fxch', '0')
    trkX_insttr.set('pitchrange', "12")

    add_auto_placements(1, [0, 100], ['track', trackid], 'vol', trkJ, 'vol', trkX_insttr, 'vol', trackname, 'Volume')
    add_auto_placements(0, [0, 100], ['track', trackid], 'pan', trkJ, 'pan', trkX_insttr, 'pan', trackname, 'Pan')
    add_auto_placements(1, [-1, -1], ['track', trackid], 'enabled', trkJ, 'enabled', xmltag, 'muted', trackname, 'Muted')
    add_auto_placements(0, None, ['track', trackid], 'pitch', trkJ, 'pitch', trkX_insttr, 'pitch', trackname, 'Pitch')

    #TO BE DONE
    if 'chain_fx_notes' in trkJ:
        trkJ_notefx = trkJ['chain_fx_notes']

        for pluginid in trkJ_notefx:
            plugintype = plugins.get_plug_type(cvpj_l, pluginid)

            if plugintype[0] == 'native-lmms' and plugintype[1] in ['arpeggiator', 'chordcreator']:
                pluginautoid = tracks.autoid_out_getlist(['plugin', pluginid])
                slotautoid = tracks.autoid_out_getlist(['slot', pluginid])
                fxdata = plugins.get_plug_fxdata(cvpj_l, pluginid)

                if plugintype[1] == 'arpeggiator':
                    trkX_notefx = ET.SubElement(trkX_insttr, "arpeggiator")
                    paramlist = ['arpgate', 'arprange', 'arpmode', 'arpdir', 'arpmiss', 'arpskip', 'arptime', 'arpcycle', 'arp']
                    add_auto_placements(0, None, ['slot', pluginid], 'enabled', fxdata, 'enabled', trkX_notefx, 'arp-enabled', 'Arp', 'On')

                if plugintype[1] == 'chordcreator':
                    trkX_notefx = ET.SubElement(trkX_insttr, "chordcreator")
                    paramlist = ['chordrange', 'chord']
                    add_auto_placements(0, None, ['slot', pluginid], 'enabled', fxdata, 'enabled', trkX_notefx, 'chord-enabled', 'Chord', 'On')

                for paramid in paramlist:
                    get_plugin_param(pluginautoid, trkX_notefx, paramid, pluginid, paramid, 0)


    middlenote = 0

    print('[output-lmms] Instrument Track')
    if 'name' in trkJ: print('[output-lmms]       Name: ' + trkJ['name'])

    if 'chain_fx_audio' in trkJ: 
        lmms_encode_fxchain(trkX_insttr, trkJ)

    plugintype, middlenotefix = lmms_encode_plugin(trkX_insttr, trkJ, trackid, trackname, trkX_insttr)

    if 'middlenote' in trkJ: middlenote = trkJ['middlenote']
    middlenote += middlenotefix
    trkX_insttr.set('basenote', str(middlenote+57))

    #placements
    if trackid in trkplacementsJ:
        if 'notes' in trkplacementsJ[trackid]:
            json_placementlist = trkplacementsJ[trackid]['notes']
        
            tracksnum = 0
            printcountplace = 0
            print('[output-lmms]       Placements: ', end='')
            while tracksnum <= len(json_placementlist)-1:
                global patternscount_forprinting
                patternscount_forprinting += 1
                printcountplace += 1
                json_placement = json_placementlist[tracksnum-1]
                json_notelist = json_placement['notelist']
                patX = ET.SubElement(xmltag, "pattern")
                patX.set('pos', str(int(json_placement['position'] * 12)))
                if 'muted' in json_placement: 
                    if json_placement['muted'] == True: patX.set('muted', "1")
                    if json_placement['muted'] == False: patX.set('muted', "0")
                else: patX.set('muted', "0")
                patX.set('steps', "16")
                patX.set('name', "")
                if 'name' in json_placement: patX.set('name', json_placement['name'])
                patX.set('type', "1")
                if 'color' in json_placement: patX.set('color', '#' + colors.rgb_float_2_hex(json_placement['color']))
                lmms_encode_notelist(patX, json_notelist)
                tracksnum += 1
            print(' ')

    trkX_midiport = ET.SubElement(trkX_insttr, "midiport")
    if 'midi' in instJ:
        trkJ_midiport = instJ['midi']

        if 'in' in trkJ_midiport:
            trkJ_m_i = trkJ_midiport['in']
            if 'enabled' in trkJ_m_i: trkX_midiport.set('readable', str(trkJ_m_i['enabled']))
            if 'fixedvelocity' in trkJ_m_i: trkX_midiport.set('fixedinputvelocity', str(trkJ_m_i['fixedvelocity']-1))
            if 'channel' in trkJ_m_i: trkX_midiport.set('inputchannel', str(trkJ_m_i['channel']))

        if 'out' in trkJ_midiport:
            trkJ_m_o = trkJ_midiport['out']
            if 'enabled' in trkJ_m_o: trkX_midiport.set('writable', str(trkJ_m_o['enabled']))
            if 'fixedvelocity' in trkJ_m_o: trkX_midiport.set('fixedoutputvelocity', str(trkJ_m_o['fixedvelocity']-1))
            if 'channel' in trkJ_m_o: trkX_midiport.set('outputchannel', str(trkJ_m_o['channel']))
            if 'fixednote' in trkJ_m_o: trkX_midiport.set('fixedoutputnote', str(trkJ_m_o['fixednote']-1))
            if 'basevelocity' in trkJ_midiport: trkX_midiport.set('basevelocity', str(trkJ_midiport['basevelocity']))
            if 'program' in trkJ_m_o: trkX_midiport.set('outputprogram', str(trkJ_m_o['program']))
    else:
        trkX_midiport.set('fixedoutputvelocity',"-1")
        trkX_midiport.set('readable',"0")
        trkX_midiport.set('outputcontroller',"0")
        trkX_midiport.set('basevelocity',"63")
        trkX_midiport.set('outputprogram',"1")
        trkX_midiport.set('writable',"0")
        trkX_midiport.set('fixedinputvelocity',"-1")
        trkX_midiport.set('inputchannel',"0")
        trkX_midiport.set('inputcontroller',"0")
        trkX_midiport.set('outputchannel',"1")
        trkX_midiport.set('fixedoutputnote',"-1")

    print('[output-lmms]')

# ------- Audio -------

def lmms_encode_audio_track(xmltag, trkJ, trackid, trkplacementsJ):

    print('[output-lmms] Audio Track')
    if 'name' in trkJ: print('[output-lmms]       Name: ' + trkJ['name'])

    global trkcX
    global trackscount_forprinting
    trackscount_forprinting += 1

    auto_nameid = {}

    xmltag.set('type', "2")

    if 'solo' in trkJ: xmltag.set('solo', str(trkJ['solo']))
    else: xmltag.set('solo', '0')

    if 'enabled' in trkJ: xmltag.set('muted', str(int(not trkJ['enabled'])))
    else: xmltag.set('muted', '0')

    if 'name' in trkJ: trackname = trkJ['name']
    else: trackname = 'untitled'
    xmltag.set('name', trackname)

    if 'color' in trkJ: xmltag.set('color', '#' + colors.rgb_float_2_hex(trkJ['color']))
    
    trkX_samptr = ET.SubElement(xmltag, "sampletrack")
    trkX_samptr.set('pan', "0")
    trkX_samptr.set('vol', "100")

    if 'fxrack_channel' in trkJ: trkX_samptr.set('fxch', str(trkJ['fxrack_channel']))
    
    if 'chain_fx_audio' in trkJ: lmms_encode_fxchain(trkX_samptr, trkJ)

    printcountplace = 0

    if trackid in trkplacementsJ:
        if 'audio' in trkplacementsJ[trackid]:
            print('[output-lmms]       Placements: ', end='')
            for json_placement in trkplacementsJ[trackid]['audio']:
                xml_sampletco = ET.SubElement(xmltag, 'sampletco')
                xml_sampletco.set('pos', str(int(json_placement['position'] * 12)))
                xml_sampletco.set('len', str(int(json_placement['duration'] * 12)))
                if 'file' in json_placement: xml_sampletco.set('src', json_placement['file'])
                if 'enabled' in json_placement: xml_sampletco.set('muted', str(int(not json_placement['enabled'])))
                if 'sample_rate' in json_placement: xml_sampletco.set('sample_rate', str(json_placement['sample_rate']))
                if 'color' in json_placement: xml_sampletco.set('color', '#' + colors.rgb_float_2_hex(json_placement['color']))

                if 'cut' in json_placement: 
                    if 'type' in json_placement['cut']:
                        json_placement_cut = json_placement['cut']
                        if json_placement_cut['type'] == 'cut': 
                            if 'start' in json_placement_cut:
                                xml_sampletco.set('off', str(int(json_placement_cut['start'] * 12)*-1))
                printcountplace += 1
            print('['+str(printcountplace)+']')

    print('[output-lmms]')

# ------- Effects -------

def lmms_encode_effectplugin(pluginid, fxslotX):
    plugintype = plugins.get_plug_type(cvpj_l, pluginid)

    cvpj_plugindata = plugins.get_plug_data(cvpj_l, pluginid)

    pluginautoid = tracks.autoid_out_getlist(['plugin', pluginid])

    if plugintype == ['eq', 'peaks']:
        #used, active, freq, gain, res/bw

        print('[output-lmms]       Audio FX: [eq] ')
        fxslotX.set('name', 'eq')
        xml_lmmseq = ET.SubElement(fxslotX, 'Eq')

        data_LP =        [False,0,0,0,0]
        data_Lowshelf =  [False,0,0,0,0]
        data_Peaks =     [[False,0,0,0,0],[False,0,0,0,0],[False,0,0,0,0],[False,0,0,0,0]]
        data_HighShelf = [False,0,0,0,0]
        data_HP =        [False,0,0,0,0]

        banddata = plugins.get_eqband(cvpj_l, pluginid)

        for s_band in banddata:
            bandtype = s_band['type']

            part = [True,
            data_values.get_value(s_band, 'on', 0),
            data_values.get_value(s_band, 'freq', 0),
            data_values.get_value(s_band, 'gain', 0),
            data_values.get_value(s_band, 'var', 0)
            ]

            if bandtype == 'low_pass': data_LP = part
            if bandtype == 'low_shelf': data_Lowshelf = part
            if bandtype == 'peak': 
                for peaknum in range(4):
                    peakdata = data_Peaks[peaknum]
                    if peakdata[0] == False: 
                        data_Peaks[peaknum] = part
                        break
            if bandtype == 'high_shelf': data_HighShelf = part
            if bandtype == 'high_pass': data_HP = part

        xml_lmmseq.set('LPactive', str(data_LP[1]))
        xml_lmmseq.set('LPfreq', str(data_LP[2]))
        xml_lmmseq.set('LPres', str(data_LP[4]))

        xml_lmmseq.set('Lowshelfactive', str(data_Lowshelf[1]))
        xml_lmmseq.set('LowShelffreq', str(data_Lowshelf[2]))
        xml_lmmseq.set('Lowshelfgain', str(data_Lowshelf[3]))
        xml_lmmseq.set('LowShelfres', str(data_Lowshelf[4]))

        for num in range(4):
            xml_lmmseq.set('Peak'+str(num+1)+'active', str(data_Peaks[num][1]))
            xml_lmmseq.set('Peak'+str(num+1)+'freq', str(data_Peaks[num][2]))
            xml_lmmseq.set('Peak'+str(num+1)+'gain', str(data_Peaks[num][3]))
            xml_lmmseq.set('Peak'+str(num+1)+'bw', str(data_Peaks[num][4]))

        xml_lmmseq.set('Highshelfactive', str(data_HighShelf[1]))
        xml_lmmseq.set('Highshelffreq', str(data_HighShelf[2]))
        xml_lmmseq.set('HighShelfgain', str(data_HighShelf[3]))
        xml_lmmseq.set('HighShelfres', str(data_HighShelf[4]))

        xml_lmmseq.set('HPactive', str(data_HP[1]))
        xml_lmmseq.set('HPfreq', str(data_HP[2]))
        xml_lmmseq.set('HPres', str(data_HP[4]))

        get_plugin_param(pluginautoid, xml_lmmseq, 'Outputgain', pluginid, 'gain_out', 0)
        get_plugin_param(pluginautoid, xml_lmmseq, 'Inputgain', pluginid, 'gain_in', 0)

    elif plugintype == ['delay', 'single']:

        print('[output-lmms]       Audio FX: [delay] ')
        fxslotX.set('name', 'delay')
        xml_lmmsdelay = ET.SubElement(fxslotX, 'Delay')

        time_type = plugins.get_plug_dataval(cvpj_l, pluginid, 'timetype', 'seconds')

        if time_type == 'seconds': 
            get_plugin_param(pluginautoid, xml_lmmsdelay, 'DelayTimeSamples', pluginid, 'time_seconds', 0)
        get_plugin_param(pluginautoid, xml_lmmsdelay, 'FeebackAmount', pluginid, 'feedback', 0)
        get_plugin_param(pluginautoid, xml_lmmsdelay, 'LfoAmount', pluginid, 'lfo_amount', 0)
        get_plugin_param(pluginautoid, xml_lmmsdelay, 'LfoFrequency', pluginid, 'lfo_freq', 0)
        get_plugin_param(pluginautoid, xml_lmmsdelay, 'OutGain', pluginid, 'gain_out', 0)

    elif plugintype == ['vst2', 'win']:
        print('[output-lmms]       Audio FX: [vst2] ')
        fxslotX.set('name', 'vsteffect')
        xml_vst = ET.SubElement(fxslotX, "vsteffectcontrols")
        setvstparams(cvpj_plugindata, pluginid, xml_vst)

    elif plugintype[0] == 'native-lmms':
        lmms_autovals = lmms_auto.get_params_fx(plugintype[1])
        xml_name = fxlist[plugintype[1]]
        fxslotX.set('name', plugintype[1])
        print('[output-lmms]       Audio FX: ['+plugintype[1]+'] ')
        xml_lmmsnat = ET.SubElement(fxslotX, xml_name)
        for pluginparam in lmms_autovals[0]: 
            get_plugin_param(pluginautoid, xml_lmmsnat, pluginparam, pluginid, pluginparam, 0)
        for pluginparam in lmms_autovals[1]: 
            xml_lmmsnat.set(pluginparam, str(data_values.get_value(cvpj_plugindata, pluginparam, 0)))

    elif plugintype[0] == 'ladspa':
        print('[output-lmms]       Audio FX: [ladspa] ')
        fxslotX.set('name', 'ladspaeffect')

        ladspa_file = data_values.get_value(cvpj_plugindata, 'path', '')

        ladspa_plugin = data_values.get_value(cvpj_plugindata, 'plugin', '')
        ladspa_sep_chan = data_values.get_value(cvpj_plugindata, 'seperated_channels', False)
        ladspa_numparams = data_values.get_value(cvpj_plugindata, 'numparams', '1')

        xml_ladspa = ET.SubElement(fxslotX, 'ladspacontrols')
        xml_ladspa_key = ET.SubElement(fxslotX, 'key')
        xml_ladspa_key_file = ET.SubElement(xml_ladspa_key, 'attribute')
        xml_ladspa_key_file.set('name', 'file')
        xml_ladspa_key_file.set('value', Path(ladspa_file).stem)
        xml_ladspa_key_plugin = ET.SubElement(xml_ladspa_key, 'attribute')
        xml_ladspa_key_plugin.set('name', 'plugin')
        xml_ladspa_key_plugin.set('value', ladspa_plugin)

        for param in range(ladspa_numparams):
            paramid = 'ladspa_param_'+str(param)
            paramvisname = 'LADSPA: #'+str(param+1)
            paramxml = get_plugin_param(pluginautoid, xml_ladspa, 'port0'+str(param), pluginid, paramid, 0, visualname=paramvisname)
            get_plugin_param(pluginautoid, xml_ladspa, 'port1'+str(param), pluginid, paramid+'_1', 0, visualname=paramvisname)

    else:
        fxslotX.set('name', 'stereomatrix')
        xml_lmmsnat = ET.SubElement(fxslotX, 'stereomatrixcontrols')
        paramlist = plugins.get_plug_paramlist(cvpj_l, pluginid)
        add_auto_unused(paramlist, pluginautoid, pluginid, 'FX Plug')


def lmms_encode_effectslot(pluginid, fxcX):
    fxslotX = ET.SubElement(fxcX, "effect")

    pluginautoid = tracks.autoid_out_getlist(['slot', pluginid])
    fxdata = plugins.get_plug_fxdata(cvpj_l, pluginid)

    add_auto_placements(1, None, ['slot', pluginid], 'enabled', fxdata, 'enabled', fxslotX, 'on', 'Slot', 'On')
    add_auto_placements(1, None, ['slot', pluginid], 'wet', fxdata, 'wet', fxslotX, 'wet', 'Slot', 'Wet')

    lmms_encode_effectplugin(pluginid, fxslotX)
    return fxslotX

def lmms_encode_fxchain(xmltag, json_fxchannel):
    if 'chain_fx_audio' in json_fxchannel:
        fxcX = ET.SubElement(xmltag, "fxchain")
        json_fxchain = json_fxchannel['chain_fx_audio']

        if 'chain_fx_audio' in json_fxchannel:
            fxcX.set('enabled', str(data_values.get_value(json_fxchannel, 'fxenabled', 1)) )
            fxcX.set('numofeffects', str(len(json_fxchannel['chain_fx_audio'])))

            for pluginid in json_fxchain:
                fxslotX = lmms_encode_effectslot(pluginid, fxcX)

def lmms_encode_fxmixer(xmltag, json_fxrack):
    for json_fxchannel in json_fxrack:

        fxchannelJ = json_fxrack[json_fxchannel]
        fxcX = ET.SubElement(xmltag, "fxchannel")
        fxcX.set('soloed', "0")
        num = json_fxchannel
        fxcX.set('num', str(num))
        print('[output-lmms] FX ' + str(num))

        if 'name' in fxchannelJ: name = fxchannelJ['name']
        else: name = 'FX ' + str(num)
        print('[output-lmms]       Name: ' + name)

        if 'color' in fxchannelJ: fxcX.set('color', '#' + colors.rgb_float_2_hex(fxchannelJ['color']))

        add_auto_placements(1, None, ['fxmixer', num], 'vol', fxchannelJ, 'vol', fxcX, 'volume', 'FX '+str(num), 'Volume')

        if 'muted' in fxchannelJ: muted = fxchannelJ['muted']
        else: muted = 0

        fxcX.set('name', name)
        fxcX.set('muted', str(muted))
        lmms_encode_fxchain(fxcX, fxchannelJ)
        if 'sends' in fxchannelJ:
            sendsJ = fxchannelJ['sends']
            for json_send in sendsJ:
                sendX = ET.SubElement(fxcX, "send")
                sendX.set('channel', str(json_send['channel']))
                sendautoid = None
                if 'sendautoid' in json_send: sendautoid = ['send', json_send['sendautoid']]
                add_auto_placements(1, None, sendautoid, 'amount', json_send, 'amount', sendX, 'amount', 'Send '+num+' > '+str(json_send['channel']), 'Amount')
        else:
            sendX = ET.SubElement(fxcX, "send")
            sendX.set('channel', '0')
            sendX.set('amount', '1')

        print('[output-lmms]')

# ------- Automation -------

def parse_auto(xml_automationpattern, l_points, val_type):
    curpoint = 0
    for point in l_points:
        if 'type' in point and curpoint != 0 and val_type != 'bool ':
            if point['type'] == 'instant':
                xml_time = ET.SubElement(xml_automationpattern, "time")
                xml_time.set('value', str(prevvalue))
                xml_time.set('pos', str(int(point['position']*12)-1))
        xml_time = ET.SubElement(xml_automationpattern, "time")
        if val_type == 'float': xml_time.set('value', str(point['value']))
        elif val_type == 'int': xml_time.set('value', str(int(point['value'])))
        else: xml_time.set('value', str(int(point['value'])))
        xml_time.set('pos', str(int(point['position']*12)))
        prevvalue = point['value']
        curpoint += 1

def lmms_make_main_auto_track(autoidnum, autodata, visualname):
    global trkcX
    print('[output-lmms] Automation Track: '+visualname)
    xml_autotrack = ET.SubElement(trkcX, "track")
    xml_autotrack.set('type', '5')
    xml_autotrack.set('solo', '0')
    xml_autotrack.set('muted', '0')
    xml_autotrack.set('name', visualname)

    autodata_type = autodata['type']
    autodata_placements = autodata['placements']

    for autoplacement in autodata_placements:
        xml_automationpattern = ET.SubElement(xml_autotrack, "automationpattern")
        xml_automationpattern.set('pos', str(int(autoplacement['position']*12)))
        xml_automationpattern.set('len', str(int(autoplacement['duration']*12)))
        xml_automationpattern.set('tens', "0")
        xml_automationpattern.set('name', visualname)
        xml_automationpattern.set('mute', "0")
        if autodata_type != 'bool': xml_automationpattern.set('prog', "1")
        else: xml_automationpattern.set('prog', "0")
        prevvalue = 0
        if 'points' in autoplacement:
            parse_auto(xml_automationpattern, autoplacement['points'], autodata_type)
        if autoidnum != None:
            xml_object = ET.SubElement(xml_automationpattern, "object")
            xml_object.set('id', str(autoidnum))

def add_auto_placements(i_fallback, i_addmul, i_id, i_autoname, j_tag, j_name, x_tag, x_name, v_type, v_name):
    i_value = i_fallback
    if j_tag != None:
        if j_name in j_tag: i_value = j_tag[j_name]
        paramdata = params.get(j_tag, [], j_name, i_fallback)
        if paramdata != None: i_value = paramdata[0]

    if i_addmul != None: i_value = (i_value+i_addmul[0])*i_addmul[1]

    if isinstance(i_value, bool):
        i_value = int(i_value)

    if i_id != None and i_autoname != None: aid_id, aid_data = tracks.autoid_out_get(i_id+[i_autoname])
    else: aid_id, aid_data = None, None

    if x_tag != None:
        if aid_id != None and len(aid_data['placements']) != 0:
            if i_addmul != None: aid_data['placements'] = auto.multiply(aid_data['placements'], i_addmul[0], i_addmul[1])
            lmms_make_main_auto_track(aid_id, aid_data, v_type+': '+v_name)
            autovarX = ET.SubElement(x_tag, x_name)
            autovarX.set('value', str(i_value))
            autovarX.set('scale_type', 'linear')
            autovarX.set('id', str(aid_id))
        else:
            x_tag.set(x_name, str(i_value))
    elif aid_id != None and aid_data != None:
        lmms_make_main_auto_track(aid_id, aid_data, v_type+': '+v_name)

def add_auto_unused(paramlist, pluginautoid, pluginid, i_name):
    if pluginautoid != None:
        for paramid in pluginautoid:
            add_auto_placements(1, None, ['plugin', pluginid], paramid, None, paramid, None, paramid, i_name, paramid)

# ------- Main -------

def lmms_encode_tracks(xmltag, trksJ, trkorderJ, trkplacementsJ):
    for trackid in trkorderJ:
        trkJ = trksJ[trackid]
        xml_track = ET.SubElement(xmltag, "track")
        if trkJ['type'] == "instrument": lmms_encode_inst_track(xml_track, trkJ, trackid, trkplacementsJ)
        if trkJ['type'] == "audio": lmms_encode_audio_track(xml_track, trkJ, trackid, trkplacementsJ)


class output_lmms(plugin_output.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'output'
    def getname(self): return 'LMMS'
    def getshortname(self): return 'lmms'
    def gettype(self): return 'r'
    def plugin_archs(self): return ['amd64', 'i386']
    def getdawcapabilities(self): 
        return {
        'fxrack': True,
        'track_lanes': False,
        'placement_cut': False,
        'placement_loop': False,
        'auto_nopl': False,
        'track_nopl': False,
        'traits_fx_delay': ['time_seconds', 'lfo', 'gain_out'],
        }
    def getsupportedplugins(self): return ['sampler', 'sf2', 'vst2', 'ladspa', 'opl2']
    def parse(self, convproj_json, output_file):
        global autoidnum
        global trkcX
        global cvpj_l

        autoidnum = 340000
        print('[output-lmms] Output Start')

        cvpj_l = json.loads(convproj_json)

        tracks.autoid_out_load(cvpj_l)

        trksJ = cvpj_l['track_data']
        trkorderJ = cvpj_l['track_order']
        if 'track_placements' in cvpj_l: trkplacementsJ = cvpj_l['track_placements']
        else: trkplacementsJ = {}

        projX = ET.Element("lmms-project")
        projX.set('type', "song")
        projX.set('creator', "DawVert")
        projX.set('creatorversion', "1.2.2")
        projX.set('version', "1.0")
        headX = ET.SubElement(projX, "head") 
        songX = ET.SubElement(projX, "song")
        trkcX = ET.SubElement(songX, "trackcontainer")

        auto_nameiddata_main = {}

        add_auto_placements(120, None, ['main'], 'bpm', cvpj_l, 'bpm', headX, 'bpm', 'Song', 'Tempo')
        add_auto_placements(0, None, ['main'], 'pitch', cvpj_l, 'pitch', headX, 'masterpitch', 'Song', 'Pitch')
        add_auto_placements(1, [0, 100], ['main'], 'vol', cvpj_l, 'vol', headX, 'mastervol', 'Song', 'Volume')

        if 'timesig' in cvpj_l:
            timesig = cvpj_l['timesig']
            headX.set("timesig_numerator", str(timesig[0]))
            headX.set("timesig_denominator", str(timesig[1]))
        else:
            headX.set("timesig_numerator", str(4))
            headX.set("timesig_denominator", str(4))

        lmms_encode_tracks(trkcX, trksJ, trkorderJ, trkplacementsJ)

        xml_fxmixer = ET.SubElement(songX, "fxmixer")
        if 'fxrack' in cvpj_l:
            lmms_encode_fxmixer(xml_fxmixer, cvpj_l['fxrack'])


        if 'info' in cvpj_l:
            infoJ = cvpj_l['info']
            if 'message' in infoJ:
                notesX = ET.SubElement(songX, "projectnotes")
                notesX.set("visible", "1")
                notesX.set("x", "728" )
                notesX.set("height", "300")
                notesX.set("y", "5" )
                notesX.set("width", "389")
                if 'type' in infoJ['message']:
                    if infoJ['message']['type'] == 'html': notesX.text = ET.CDATA(infoJ['message']['text'])
                    if infoJ['message']['type'] == 'text': notesX.text = ET.CDATA(infoJ['message']['text'].replace('\n', '<br/>').replace('\r', '<br/>'))
            else:
                notesX = ET.SubElement(songX, "projectnotes")
                notesX.text = ET.CDATA("")
        else:
            notesX = ET.SubElement(songX, "projectnotes")
            notesX.text = ET.CDATA("")

        print("[output-lmms] Number of Notes: " + str(notescount_forprinting))
        print("[output-lmms] Number of Patterns: " + str(patternscount_forprinting))
        print("[output-lmms] Number of Tracks: " + str(trackscount_forprinting))      

        trksJ = cvpj_l['track_data']
        
        
        outfile = ET.ElementTree(projX)
        
        ET.indent(outfile)
        outfile.write(output_file, encoding='utf-8', xml_declaration = True)
