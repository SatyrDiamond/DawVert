# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import base64
import json
import lxml.etree as ET
import math
import plugin_output
from pathlib import Path
from functions import data_dataset
from functions import auto
from functions import placements
from functions import data_values
from functions import plugins
from functions import note_mod
from functions import notelist_data
from functions import colors
from functions import params
from functions import song
from functions_tracks import auto_id
from functions_tracks import tracks_r

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

patternscount_forprinting = 0
notescount_forprinting = 0
trackscount_forprinting = 0

def dset_plugparams(pluginname, pluginid, xml_data, cvpj_plugindata):
    global dataset
    paramlist = dataset.params_list('plugin', pluginname)
    if paramlist != None:
        for paramname in paramlist:
            paramlist = dataset.params_i_get('plugin', pluginname, paramname)
            pv_noauto,pv_type,pv_def,pv_min,pv_max,pv_name = paramlist
            if pv_noauto == False:
                pl_val, pl_type, pl_name = cvpj_plugindata.param_get(paramname, pv_def)
                create_param_auto(xml_data, paramname, ['plugin', pluginid, paramname], pl_val, None, 'Plugin', pv_name, True)
            else:
                xml_data.set(paramname, str(cvpj_plugindata.dataval_get(paramname, pv_def)) )

# -------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------- functions ----------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------

def add_window_data(xmltag, cvpj_l, w_group, w_name, w_pos, w_size, w_open, w_max):
    out_pos, out_size, out_open, out_max = song.get_visual_window(cvpj_l, w_group, w_name, w_pos, w_size, w_open, w_max)

    if out_open != None: xmltag.set("visible", str(int(out_open)))
    if out_max != None: xmltag.set("maximized", str(int(out_max)))

    if out_pos != None: 
        xmltag.set("x", str(out_pos[0]))
        xmltag.set("y", str(out_pos[1]))

    if out_size != None: 
        xmltag.set("width", str(out_size[0]))
        xmltag.set("height", str(out_size[1]))

def add_keyatt(xmltag, i_dict):
    xml_key = ET.SubElement(xmltag, 'key')
    for item in i_dict.items():
        xml_key_file = ET.SubElement(xml_key, 'attribute')
        xml_key_file.set('name', str(item[0]))
        xml_key_file.set('value', str(item[1]))

# -------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------ math -------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------

def oneto100(input): return round(float(input) * 100)

def sec2exp(value): return math.sqrt(value/5)

# -------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------- vst -------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------

def setvstparams(cvpj_plugindata, pluginid, xmldata):
    vstpath = cvpj_plugindata.dataval_get('path', '')

    current_program = cvpj_plugindata.dataval_get('current_program', 0)
    xmldata.set('program', str(current_program) )
    xmldata.set('plugin', vstpath)

    add_keyatt(xmldata, {'file': vstpath})

    middlenotefix = cvpj_plugindata.dataval_get('middlenotefix', 0)
    datatype = cvpj_plugindata.dataval_get('datatype', 'none')
    numparams = cvpj_plugindata.dataval_get('numparams', 0)


    if datatype == 'bank':
        bank_programs = cvpj_plugindata.dataval_get('programs', 0)
        cur_bank_prog = bank_programs[current_program]
        bankprog_type = cur_bank_prog['datatype']

        if bankprog_type == 'params':
            numparams = cur_bank_prog['numparams']
            xmldata.set('numparams', str(numparams))
            for param in range(numparams):
                pval = cur_bank_prog['params'][str(param)]['value']
                xmldata.set('param'+str(param), str(param)+':noname:'+str(pval) )

    if datatype == 'chunk':
        xmldata.set('chunk', cvpj_plugindata.rawdata_get_b64())

    if datatype == 'param':
        xmldata.set('numparams', str(numparams))
        for param in range(numparams):
            pval, ptype, pname = cvpj_plugindata.param_get('vst_param_'+str(param), 0)
            xmldata.set('param'+str(param), str(param)+':'+pname+':'+str(pval))
             
    pluginautoid = auto_id.out_getlist(['plugin', pluginid])
    if pluginautoid != None:
        for paramname in pluginautoid:
            if 'vst_param_' in paramname:
                paramid = paramname[10:]
                paramvisname = int(paramname[10:])+1
                aid_id, aid_data = auto_id.out_get(['plugin', pluginid, paramname])
                if aid_id != None and len(aid_data['placements']) != 0:
                    make_auto_track(aid_id, aid_data, 'VST2: #'+str(paramvisname))
                    autovarX = ET.SubElement(xmldata, 'param'+paramid)
                    autovarX.set('scale_type', 'linear')
                    autovarX.set('id', str(aid_id))

    return middlenotefix

# -------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------ auto -------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------

def auto_add_main(xmltag, j_name, x_name, i_fallback, i_addmul, v_name):
    i_value = params.get(cvpj_l, [], j_name, i_fallback)[0]
    create_param_auto(xmltag, x_name, ['main', j_name], i_value, i_addmul, 'Main', v_name, True)

def auto_add_track(xmltag, j_name, x_name, i_fallback, i_addmul, i_trackid, v_trackname, v_name):
    i_value = params.get(cvpj_l, ['track_data', i_trackid], j_name, i_fallback)[0]
    create_param_auto(xmltag, x_name, ['track', i_trackid, j_name], i_value, i_addmul, v_trackname, v_name, True)

def auto_add_fxmixer(xmltag, j_name, x_name, i_fallback, i_addmul, i_fxnum, v_name):
    i_value = params.get(cvpj_l, ['fxmixer', i_fxnum], j_name, i_fallback)[0]
    create_param_auto(xmltag, x_name, ['fxmixer', i_fxnum, j_name], i_value, i_addmul, 'FX '+str(i_fxnum), v_name, True)

def auto_add_plugin(xmltag, j_name, x_name, i_fallback, i_addmul, i_pluginid, cvpj_plugindata):
    pval, ptype, pname = cvpj_plugindata.param_get(j_name, i_fallback)
    create_param_auto(xmltag, x_name, ['plugin', i_pluginid, j_name], float(pval), i_addmul, 'Plugin', pname, True)

#def add_auto_unused(paramlist, pluginautoid, pluginid, i_name):
#    if pluginautoid != None:
#        for paramid in pluginautoid:
#            add_auto_placements(1, None, ['plugin', pluginid], paramid, None, paramid, None, paramid, i_name, paramid)
#
def create_param_auto(x_tag, x_name, autoloc, i_value, i_addmul, v_type, v_name, writeparamxml):
    if i_addmul != None: i_value = (i_value+i_addmul[0])*i_addmul[1]
    if isinstance(i_value, bool): i_value = int(i_value)
    aid_id, aid_data = auto_id.out_get(autoloc)
    if x_tag != None:
        if aid_data != None and aid_id != None:
            if len(aid_data['placements']) != 0:
                writeparamxml = False
                if i_addmul != None: aid_data['placements'] = auto.multiply(aid_data['placements'], i_addmul[0], i_addmul[1])
                make_auto_track(aid_id, aid_data, v_type+': '+v_name)
                autovarX = ET.SubElement(x_tag, x_name)
                autovarX.set('value', str(i_value))
                autovarX.set('scale_type', 'linear')
                autovarX.set('id', str(aid_id))

    elif aid_id != None and aid_data != None:
        writeparamxml = False
        make_auto_track(aid_id, aid_data, v_type+': '+v_name)

    if writeparamxml:
        x_tag.set(x_name, str(i_value))

def parse_auto(xmltag, i_points, i_val_type):
    curpoint = 0
    for point in i_points:
        if 'type' in point and curpoint != 0 and i_val_type != 'bool ':
            if point['type'] == 'instant':
                xml_time = ET.SubElement(xmltag, "time")
                xml_time.set('value', str(prevvalue))
                xml_time.set('pos', str(int(point['position']*12)-1))
        xml_time = ET.SubElement(xmltag, "time")
        if i_val_type == 'float': xml_time.set('value', str(point['value']))
        elif i_val_type == 'int': xml_time.set('value', str(int(point['value'])))
        else: xml_time.set('value', str(int(point['value'])))
        xml_time.set('pos', str(int(point['position']*12)))
        prevvalue = point['value']
        curpoint += 1

def make_auto_track(autoidnum, autodata, visualname):
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
        xml_automationpattern.set('prog', "1" if autodata_type != 'bool' else "0")
        prevvalue = 0
        if 'points' in autoplacement: parse_auto(xml_automationpattern, autoplacement['points'], autodata_type)
        if autoidnum != None:
            xml_object = ET.SubElement(xml_automationpattern, "object")
            xml_object.set('id', str(autoidnum))

# -------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------- Instruments and Plugins -------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------

def asdrlfo_set(inst_plugindata, trkX_insttr):
    eldataX = ET.SubElement(trkX_insttr, "eldata")

    filt_enabled, filt_cutoff, filt_reso, filt_type, filt_subtype = inst_plugindata.filter_get()
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

    asdrlfo(inst_plugindata, eldataX, 'vol', 'vol')
    asdrlfo(inst_plugindata, eldataX, 'cutoff', 'cut')
    asdrlfo(inst_plugindata, eldataX, 'reso', 'res')

def asdrlfo(inst_plugindata, xmlobj, asdrtype, xmltype):
    elmodX = ET.SubElement(xmlobj, 'el' + xmltype)

    a_predelay, a_attack, a_hold, a_decay, a_sustain, a_release, a_amount = inst_plugindata.asdr_env_get_fake_tension(asdrtype)

    if asdrtype == 'cutoff': elmodX.set('amt', str(a_amount/6000))
    else: elmodX.set('amt', str(float(a_amount)))
    elmodX.set('pdel', str(sec2exp(a_predelay)))
    elmodX.set('att', str(sec2exp(a_attack)))
    elmodX.set('hold', str(sec2exp(a_hold)))
    elmodX.set('dec', str(sec2exp(a_decay)))
    elmodX.set('sustain', str(a_sustain))
    elmodX.set('rel', str(sec2exp(a_release)))

    l_predelay, l_attack, l_shape, l_speed_type, l_speed_time, l_amount = inst_plugindata.lfo_get(asdrtype)
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

def lmms_encode_plugin(xmltag, trkJ, trackid, trackname, trkX_insttr):
    instJ = data_values.get_value(trkJ, 'instdata', {})
    xml_instrumentpreplugin = ET.SubElement(xmltag, "instrument")

    visual_plugname = 'none'
    middlenotefix = 0

    if 'pluginid' in instJ: 
        pluginid = instJ['pluginid']

        inst_plugindata = plugins.cvpj_plugin('cvpj', cvpj_l, pluginid)
        plugintype = inst_plugindata.type_get()
        pluginautoid = auto_id.out_getlist(['plugin', pluginid])
        visual_plugname = str(plugintype[0])+' ('+str(plugintype[1])+')'

        if plugintype == ['sampler', 'single']:
            print('[output-lmms]       Plugin: Sampler (Single) > audiofileprocessor')
            xml_instrumentpreplugin.set('name', "audiofileprocessor")
            xml_sampler = ET.SubElement(xml_instrumentpreplugin, "audiofileprocessor")

            xml_sampler.set('reversed', str(int( inst_plugindata.dataval_get('reverse', 0) )))
            xml_sampler.set('amp', str(oneto100( inst_plugindata.dataval_get('amp', 1) )))
            xml_sampler.set('stutter', str(int( inst_plugindata.dataval_get('continueacrossnotes', False) )))
            xml_sampler.set('src', inst_plugindata.dataval_get('file', ''))

            point_value_type = inst_plugindata.dataval_get('point_value_type', 'samples')
            sample_length = inst_plugindata.dataval_get('length', None)
            sample_start = inst_plugindata.dataval_get('start', 0)
            sample_loop = inst_plugindata.dataval_get('loop', 0)

            out_start = 0
            out_loop = 0
            out_end = 1

            if point_value_type == 'samples' and sample_length:
                if sample_length != 0:
                    out_start = sample_start/sample_length

                    if sample_loop:
                        if 'points' in sample_loop:
                            sample_loop_points = sample_loop['points']
                            out_loop = sample_loop_points[0] / sample_length
                            out_end = sample_loop_points[1] / sample_length
                            if out_end == 0 or out_start == out_end: out_end = 1.0

            if point_value_type == 'percent':
                out_start = sample_start
                if sample_loop:
                    if 'points' in sample_loop:
                        trkJ_loop_points = sample_loop['points']
                        out_loop = trkJ_loop_points[0]
                        out_end = trkJ_loop_points[1]

            xml_sampler.set('sframe', str(out_start))
            xml_sampler.set('lframe', str(out_loop))
            xml_sampler.set('eframe', str(out_end))

            loopenabled = 0
            loopmode = "normal"
            if sample_loop:
                if 'enabled' in sample_loop: loopenabled = sample_loop['enabled']
                if 'mode' in sample_loop: loopmode = sample_loop['mode']
            if loopenabled == 0: xml_sampler.set('looped', '0')
            if loopenabled == 1:
                if loopmode == "normal": xml_sampler.set('looped', '1')
                if loopmode == "pingpong": xml_sampler.set('looped', '2')

            interpolation = inst_plugindata.dataval_get('interpolation', "sinc")
            if interpolation == "none": xml_sampler.set('interp', '0')
            elif interpolation == "linear": xml_sampler.set('interp', '1')
            elif interpolation == "sinc": xml_sampler.set('interp', '2')
            else: xml_sampler.set('interp', '2')

            middlenotefix += 3

        elif plugintype[0] == 'soundfont2':
            print('[output-lmms]       Plugin: soundfont2 > sf2player')
            xml_instrumentpreplugin.set('name', "sf2player")
            xml_sf2 = ET.SubElement(xml_instrumentpreplugin, "sf2player")
            xml_sf2.set('bank', str(int(inst_plugindata.dataval_get('bank', 0))))
            xml_sf2.set('patch', str(int(inst_plugindata.dataval_get('patch', 0))))
            xml_sf2.set('src', str(inst_plugindata.dataval_get('file', '')))
            auto_add_plugin(xml_sf2, 'gain', 'gain', 1, None, pluginid, inst_plugindata)
            auto_add_plugin(xml_sf2, 'chorusDepth', 'chorus_depth', 0, None, pluginid, inst_plugindata)
            auto_add_plugin(xml_sf2, 'chorusLevel', 'chorus_level', 0, None, pluginid, inst_plugindata)
            auto_add_plugin(xml_sf2, 'chorusNum', 'chorus_lines', 0, None, pluginid, inst_plugindata)
            auto_add_plugin(xml_sf2, 'chorusOn', 'chorus_enabled', 0, None, pluginid, inst_plugindata)
            auto_add_plugin(xml_sf2, 'chorusSpeed', 'chorus_speed', 0, None, pluginid, inst_plugindata)
            auto_add_plugin(xml_sf2, 'reverbDamping', 'reverb_damping', 0, None, pluginid, inst_plugindata)
            auto_add_plugin(xml_sf2, 'reverbLevel', 'reverb_level', 0, None, pluginid, inst_plugindata)
            auto_add_plugin(xml_sf2, 'reverbOn', 'reverb_enabled', 0, None, pluginid, inst_plugindata)
            auto_add_plugin(xml_sf2, 'reverbRoomSize', 'reverb_roomsize', 0, None, pluginid, inst_plugindata)
            auto_add_plugin(xml_sf2, 'reverbWidth', 'reverb_width', 0, None, pluginid, inst_plugindata)
            middlenotefix += 12

        elif plugintype == ['fm', 'opl2']:
            print('[output-lmms]       Plugin: OPL2 > OPL2')
            xml_instrumentpreplugin.set('name', "OPL2")
            xml_opl2 = ET.SubElement(xml_instrumentpreplugin, "OPL2")
            for lmms_opname, cvpj_opname in [['op1', 'mod'],['op2', 'car']]:
                for varname in opl2opvarnames:
                    auto_add_plugin(xml_opl2, cvpj_opname+varname[1], lmms_opname+varname[0], 0, None, pluginid, inst_plugindata)
            for varname in opl2varnames:
                auto_add_plugin(xml_opl2, varname[1], varname[0], 0, None, pluginid, inst_plugindata)
            middlenotefix = 24

        elif plugintype == ['vst2', 'win']:
            print('[output-lmms]       Plugin: vst2 > vestige')
            xml_instrumentpreplugin.set('name', "vestige")
            xml_vst = ET.SubElement(xml_instrumentpreplugin, "vestige")
            middlenotefix += setvstparams(inst_plugindata, pluginid, xml_vst)

        elif plugintype[0] == 'native-lmms':
            print('[output-lmms]       Plugin: '+plugintype[1]+' > '+plugintype[1])
            xml_instrumentpreplugin.set('name', plugintype[1])
            xml_lmmsnat = ET.SubElement(xml_instrumentpreplugin, plugintype[1])

            dset_plugparams(plugintype[1], pluginid, xml_lmmsnat, inst_plugindata)

            if plugintype[1] == 'zynaddsubfx':
                zdata = inst_plugindata.dataval_get('data', None)
                if zdata != None:
                    zdataxs = ET.fromstring(base64.b64decode(zdata.encode('ascii')).decode('ascii'))
                    xml_lmmsnat.append(zdataxs)
            if plugintype[1] == 'tripleoscillator':
                for names in [['userwavefile0', 'osc_1'],
                            ['userwavefile1', 'osc_2'],
                            ['userwavefile2', 'osc_3']]:
                    filedata = inst_plugindata.fileref_get(names[1])
                    if filedata != None: xml_lmmsnat.set(names[0], filedata['path'])

        else:
            print('[output-lmms]       Plugin: '+visual_plugname+' > None')
            xml_instrumentpreplugin.set('name', "audiofileprocessor")
            #paramlist = plugins.get_plug_paramlist(cvpj_l, pluginid)

            #if trackname not in ['', None]: visual_plugname = trackname
            #add_auto_unused(paramlist, pluginautoid, pluginid, visual_plugname)

        asdrlfo_set(inst_plugindata, trkX_insttr)

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
        duration = int(round(float(json_note['duration']) * 12))
        pan = oneto100(json_note['pan']) if 'pan' in json_note else 0
        vol = oneto100(json_note['vol']) if 'vol' in json_note else 100
        
        patX.set('key', str(key))
        patX.set('pos', str(int(round(position))))
        patX.set('pan', str(pan))
        patX.set('len', str(  max(1,int(round(duration))))   )
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

    xmltag.set('solo', str(trkJ['solo'] if 'solo' in trkJ else 0))

    trackname = trkJ['name'] if 'name' in trkJ else 'noname'

    xmltag.set('name', data_values.xml_compat(trackname) )

    if 'color' in trkJ: xmltag.set('color', '#' + colors.rgb_float_to_hex(trkJ['color']))

    instJ = trkJ['instdata'] if 'instdata' in trkJ else {}

    #instrumenttrack
    trkX_insttr = ET.SubElement(xmltag, "instrumenttrack")
    instplugin = instJ['pluginid'] if 'pluginid' in instJ else None

    if instplugin != None:
        add_window_data(xmltag, cvpj_l, 'plugin', instplugin, None, None, False, False)

    trkX_insttr.set('fxch', str(tracks_r.track_fxrackchan_get(cvpj_l, trackid)))
    trkX_insttr.set('pitchrange', "12")

    auto_add_track(trkX_insttr, 'usemasterpitch', 'usemasterpitch', 1, None, trackid, trackname, 'Use Master Pitch')
    auto_add_track(trkX_insttr, 'vol', 'vol', 1, [0, 100], trackid, trackname, 'Vol')
    auto_add_track(trkX_insttr, 'pan', 'pan', 0, [0, 100], trackid, trackname, 'Pan')
    auto_add_track(xmltag, 'enabled', 'muted', 1, [-1, -1], trackid, trackname, 'On')
    auto_add_track(trkX_insttr, 'pitch', 'pitch', 0, [0, 100], trackid, trackname, 'Pitch')

    if 'chain_fx_notes' in trkJ:
        trkJ_notefx = trkJ['chain_fx_notes']

        for pluginid in trkJ_notefx:
            notefx_plugindata = plugins.cvpj_plugin('cvpj', cvpj_l, pluginid)
            plugintype = notefx_plugindata.type_get()

            if plugintype[0] == 'native-lmms' and plugintype[1] in ['arpeggiator', 'chordcreator']:
                i_enabled, i_wet = notefx_plugindata.fxdata_get()

                if plugintype[1] == 'arpeggiator':
                    trkX_notefx = ET.SubElement(trkX_insttr, "arpeggiator")
                    create_param_auto(trkX_notefx, 'arp-enabled', ['slot', pluginid, 'enabled'], i_enabled, None, 'Arp', 'On', True)
                    dset_plugparams(plugintype[1], pluginid, trkX_notefx, notefx_plugindata)

                if plugintype[1] == 'chordcreator':
                    trkX_notefx = ET.SubElement(trkX_insttr, "chordcreator")
                    create_param_auto(trkX_notefx, 'chord-enabled', ['slot', pluginid, 'enabled'], i_enabled, None, 'Chord', 'On', True)
                    dset_plugparams(plugintype[1], pluginid, trkX_notefx, notefx_plugindata)

    print('[output-lmms] Instrument Track')
    if 'name' in trkJ: print('[output-lmms]       Name: ' + trkJ['name'])

    if 'chain_fx_audio' in trkJ: lmms_encode_fxchain(trkX_insttr, trkJ)

    plugintype, middlenotefix = lmms_encode_plugin(trkX_insttr, trkJ, trackid, trackname, trkX_insttr)

    middlenote = data_values.nested_dict_get_value(trkJ, ['instdata', 'middlenote'])
    if middlenote == None: middlenote = 0

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
                patX.set('muted', str(int(json_placement['muted'] if 'muted' in json_placement else 0)))
                patX.set('steps', "16")
                patX.set('name', json_placement['name'] if 'name' in json_placement else "" )
                patX.set('type', "1")
                if 'color' in json_placement: 
                    patX.set('color', '#' + colors.rgb_float_to_hex(json_placement['color']))
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

    xmltag.set('solo', str(trkJ['solo'] if 'solo' in trkJ else 0))

    trackname = trkJ['name'] if 'name' in trkJ else 'noname'
    xmltag.set('name', trackname)

    if 'color' in trkJ: xmltag.set('color', '#' + colors.rgb_float_to_hex(trkJ['color']))
    
    trkX_samptr = ET.SubElement(xmltag, "sampletrack")

    auto_add_track(trkX_samptr, 'vol', 'vol', 1, [0, 100], trackid, trackname, 'Vol')
    auto_add_track(trkX_samptr, 'pan', 'pan', 0, [0, 100], trackid, trackname, 'Pan')
    auto_add_track(xmltag, 'enabled', 'muted', 1, [-1, -1], trackid, trackname, 'On')

    trkX_samptr.set('mixch', str(tracks_r.track_fxrackchan_get(cvpj_l, trackid)))
    
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
                if 'color' in json_placement: xml_sampletco.set('color', '#' + colors.rgb_float_to_hex(json_placement['color']))

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

def lmms_encode_effectslot(pluginid, fxcX):
    fx_plugindata = plugins.cvpj_plugin('cvpj', cvpj_l, pluginid)
    i_enabled, i_wet = fx_plugindata.fxdata_get()

    fxslotX = ET.SubElement(fxcX, "effect")
    create_param_auto(fxslotX, 'on', ['slot', pluginid, 'enabled'], i_enabled, None, 'Slot', 'On', True)
    create_param_auto(fxslotX, 'wet', ['slot', pluginid, 'wet'], i_wet, None, 'Slot', 'Wet', True)

    plugintype = fx_plugindata.type_get()

    pluginautoid = auto_id.out_getlist(['plugin', pluginid])

    if plugintype == ['simple', 'reverb']:
        print('[output-lmms]       Audio FX: [reverb] ')
        fxslotX.set('name', 'reverbsc')
        xml_lmmsreverbsc = ET.SubElement(fxslotX, 'ReverbSCControls')
        xml_lmmsreverbsc.set('input_gain', '0')
        xml_lmmsreverbsc.set('size', '0.8')
        xml_lmmsreverbsc.set('output_gain', '0')
        xml_lmmsreverbsc.set('color', '10000')

    elif plugintype == ['universal', 'eq-bands']:
        data_LP, data_Lowshelf, data_Peaks, data_HighShelf, data_HP, data_auto = fx_plugindata.eqband_get_limited(None)

        print('[output-lmms]       Audio FX: [eq] ')
        fxslotX.set('name', 'eq')
        xml_lmmseq = ET.SubElement(fxslotX, 'Eq')

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

        xml_lmmseq.set('Outputgain', str( fx_plugindata.param_get('gain_out', 0) ))
        xml_lmmseq.set('Inputgain', str( fx_plugindata.param_get('gain_in', 0) ))

    elif plugintype == ['universal', 'delay-c']:
        print('[output-lmms]       Audio FX: [delay] ')
        fxslotX.set('name', 'delay')
        xml_lmmsdelay = ET.SubElement(fxslotX, 'Delay')

        d_time_type = fx_plugindata.dataval_get('time_type', 'seconds')
        d_time = fx_plugindata.dataval_get('time', 1)
        d_wet = fx_plugindata.dataval_get('wet', 0.5)
        d_feedback = fx_plugindata.dataval_get('feedback', 0.0)

        if d_time_type == 'seconds': 
            xml_lmmsdelay.set('DelayTimeSamples', str(d_time))
        if d_time_type == 'steps':
            xml_lmmsdelay.set('DelayTimeSamples', str((d_time/8)*((lmms_bpm)/120)))

        xml_lmmsdelay.set('FeebackAmount', str(d_feedback))
        xml_lmmsdelay.set('LfoAmount', str( fx_plugindata.param_get('lfo_amount', 0) ))
        xml_lmmsdelay.set('LfoFrequency', str( fx_plugindata.param_get('lfo_freq', 0) ))
        xml_lmmsdelay.set('OutGain', str( fx_plugindata.param_get('gain_out', 0) ))

    elif plugintype == ['vst2', 'win']:
        print('[output-lmms]       Audio FX: [vst2] ')
        fxslotX.set('name', 'vsteffect')
        xml_vst = ET.SubElement(fxslotX, "vsteffectcontrols")
        setvstparams(fx_plugindata, pluginid, xml_vst)

    elif plugintype[0] == 'native-lmms':
        xml_name = fxlist[plugintype[1]]
        fxslotX.set('name', plugintype[1])
        print('[output-lmms]       Audio FX: ['+plugintype[1]+'] ')
        xml_lmmsnat = ET.SubElement(fxslotX, xml_name)
        dset_plugparams(plugintype[1], pluginid, xml_lmmsnat, fx_plugindata)

    elif plugintype[0] == 'ladspa':
        print('[output-lmms]       Audio FX: [ladspa] ')
        fxslotX.set('name', 'ladspaeffect')

        ladspa_file = fx_plugindata.dataval_get('path', '')
        ladspa_plugin = fx_plugindata.dataval_get('plugin', '')
        ladspa_sep_chan = fx_plugindata.dataval_get('seperated_channels', False)
        ladspa_numparams = fx_plugindata.dataval_get('numparams', 0)
        xml_ladspa = ET.SubElement(fxslotX, 'ladspacontrols')
        xml_ladspa.set('ports', str(ladspa_numparams*2))
        xml_ladspa.set('link', str(int(not ladspa_sep_chan)))

        if ladspa_file != None: add_keyatt(fxslotX, {'file': Path(ladspa_file).stem, 'plugin': ladspa_plugin})
        for param in range(ladspa_numparams):
            for channum in range(2):
                cvpj_paramid = 'ladspa_param_'+str(param)
                if channum == 1: cvpj_paramid += '_1'
                lmms_paramid = 'port'+str(channum)+str(param)
                cvpj_paramvisname = 'LADSPA: #'+str(param+1)

                aid_id, aid_data = auto_id.out_get(['plugin', pluginid, cvpj_paramid])
                lmms_paramdata = ET.SubElement(xml_ladspa, lmms_paramid)
                paramval = fx_plugindata.param_get(cvpj_paramid, 0)[0]
                if channum == 0: lmms_paramdata.set('link', str(int(not ladspa_sep_chan)))
                if aid_id == None:
                    lmms_paramdata.set('data', str(paramval))
                else:
                    lmms_paramdata_data = ET.SubElement(lmms_paramdata, 'data')
                    lmms_paramdata_data.set('value', str(paramval))
                    lmms_paramdata_data.set('scale_type', 'linear')
                    lmms_paramdata_data.set('id', str(aid_id))
                    make_auto_track(aid_id, aid_data, cvpj_paramvisname)

    else:
        fxslotX.set('name', 'stereomatrix')
        xml_lmmsnat = ET.SubElement(fxslotX, 'stereomatrixcontrols')
    #    paramlist = plugins.get_plug_paramlist(cvpj_l, pluginid)
    #    add_auto_unused(paramlist, pluginautoid, pluginid, 'FX Plug')


def lmms_encode_fxchain(xmltag, json_fxchannel):
    if 'chain_fx_audio' in json_fxchannel:
        fxcX = ET.SubElement(xmltag, "fxchain")
        json_fxchain = json_fxchannel['chain_fx_audio']

        if 'chain_fx_audio' in json_fxchannel:
            fxcX.set('enabled', str(data_values.get_value(json_fxchannel, 'fxenabled', 1)) )
            fxcX.set('numofeffects', str(len(json_fxchannel['chain_fx_audio'])))

            for pluginid in json_fxchain:
                lmms_encode_effectslot(pluginid, fxcX)

def lmms_encode_fxmixer(xmltag, json_fxrack):
    for json_fxchannel in json_fxrack:

        fxchannelJ = json_fxrack[json_fxchannel]
        fxcX = ET.SubElement(xmltag, "fxchannel")
        fxcX.set('soloed', "0")
        num = json_fxchannel
        fxcX.set('num', str(num))
        print('[output-lmms] FX ' + str(num))

        name = fxchannelJ['name'] if 'name' in fxchannelJ else 'FX '+str(num)
        print('[output-lmms]       Name: ' + name)
        fxcX.set('name', data_values.xml_compat(name))

        if 'color' in fxchannelJ: fxcX.set('color', '#' + colors.rgb_float_to_hex(fxchannelJ['color']))

        auto_add_fxmixer(fxcX, 'vol', 'volume', 1, None, num, 'Volume')
        fxcX.set('muted', str(fxchannelJ['muted'] if 'muted' in fxchannelJ else 0))

        lmms_encode_fxchain(fxcX, fxchannelJ)

        if 'sends' in fxchannelJ:
            sendsJ = fxchannelJ['sends']
            for json_send in sendsJ:
                sendX = ET.SubElement(fxcX, "send")
                sendX.set('channel', str(json_send['channel']))
                sendautoid = None
                if 'sendautoid' in json_send: 
                    visual_name = 'Send '+str(num)+' > '+str(json_send['channel'])
                    create_param_auto(sendX, 'amount', ['send', json_send['sendautoid'], 'amount'], json_send['amount'], None, visual_name, 'Amount', True)
                else:
                    sendX.set('amount', str(json_send['amount']))
        else:
            sendX = ET.SubElement(fxcX, "send")
            sendX.set('channel', '0')
            sendX.set('amount', '1')

        print('[output-lmms]')

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
        'fxrack_params': ['enabled','vol']
        }
    def getsupportedplugformats(self): return ['vst2', 'ladspa', 'native-lmms']
    def getsupportedplugins(self): return ['sampler:single', 'soundfont2', 'universal:eq-bands', 'universal:delay-c', 'simple:reverb']
    def getfileextension(self): return 'mmp'
    def parse(self, convproj_json, output_file):
        global autoidnum
        global trkcX
        global cvpj_l
        global lmms_bpm
        global dataset

        autoidnum = 340000
        print('[output-lmms] Output Start')

        cvpj_l = json.loads(convproj_json)

        dataset = data_dataset.dataset('./data_dset/lmms.dset')

        auto_id.out_load(cvpj_l)

        trksJ = cvpj_l['track_data'] if 'track_data' in cvpj_l else {}
        trkorderJ = cvpj_l['track_order'] if 'track_order' in cvpj_l else []
        trkplacementsJ = cvpj_l['track_placements'] if 'track_placements' in cvpj_l else {}

        projX = ET.Element("lmms-project")
        projX.set('type', "song")
        projX.set('creator', "DawVert")
        projX.set('creatorversion', "1.2.2")
        projX.set('version', "1.0")
        headX = ET.SubElement(projX, "head") 
        songX = ET.SubElement(projX, "song")
        trkcX = ET.SubElement(songX, "trackcontainer")
        add_window_data(trkcX, cvpj_l, 'main', 'tracklist', [5,5], [720,300], True, False)

        auto_nameiddata_main = {}

        lmms_bpm = params.get(cvpj_l, [], 'bpm', 140)[0]

        auto_add_main(headX, 'bpm', 'bpm', 120, None, 'Tempo')
        auto_add_main(headX, 'pitch', 'masterpitch', 0, None, 'Pitch')
        auto_add_main(headX, 'vol', 'mastervol', 1, [0, 100], 'Volume')

        timesig = song.get_timesig(cvpj_l)
        headX.set("timesig_numerator", str(timesig[0]))
        headX.set("timesig_denominator", str(timesig[1]))

        lmms_encode_tracks(trkcX, trksJ, trkorderJ, trkplacementsJ)

        xml_fxmixer = ET.SubElement(songX, "fxmixer")
        add_window_data(xml_fxmixer, cvpj_l, 'main', 'fxmixer', [102,280], [543,333], True, False)
        if 'fxrack' in cvpj_l:
            lmms_encode_fxmixer(xml_fxmixer, cvpj_l['fxrack'])

        XControllerRackView = ET.SubElement(songX, "ControllerRackView")
        add_window_data(XControllerRackView, cvpj_l, 'main', 'controller_rack_view', [680,310], [350,200], False, False)
        Xpianoroll = ET.SubElement(songX, "pianoroll")
        add_window_data(Xpianoroll, cvpj_l, 'main', 'piano_roll', [5,5], [970,480], False, False)
        Xautomationeditor = ET.SubElement(songX, "automationeditor")
        add_window_data(Xautomationeditor, cvpj_l, 'main', 'automation_editor', [1,1], [860,400], False, False)


        notes_nothing = True
        if 'info' in cvpj_l:
            infoJ = cvpj_l['info']
            if 'message' in infoJ:
                notes_nothing = False
                notesX = ET.SubElement(songX, "projectnotes")
                add_window_data(notesX, cvpj_l, 'main', 'project_notes', [728, 5], [389, 300], True, False)

                if 'type' in infoJ['message']:
                    if infoJ['message']['type'] == 'html': notesX.text = ET.CDATA(infoJ['message']['text'])
                    if infoJ['message']['type'] == 'text': notesX.text = ET.CDATA(infoJ['message']['text'].replace('\n', '<br/>').replace('\r', '<br/>'))

        if notes_nothing:
            notesX = ET.SubElement(songX, "projectnotes")
            notesX.text = ET.CDATA("")

        print("[output-lmms] Number of Notes: " + str(notescount_forprinting))
        print("[output-lmms] Number of Patterns: " + str(patternscount_forprinting))
        print("[output-lmms] Number of Tracks: " + str(trackscount_forprinting))      

        trksJ = cvpj_l['track_data'] if 'track_data' in trksJ else {}
        
        loop_on, loop_start, loop_end = song.get_loopdata(cvpj_l, 'r')

        timelineX = ET.SubElement(songX, "timeline")
        timelineX.set("lp0pos", str(int(loop_start*12)))
        timelineX.set("lpstate", str(int(loop_on)))
        timelineX.set("lp1pos", str(int(loop_end*12)))

        outfile = ET.ElementTree(projX)
        
        ET.indent(outfile)
        outfile.write(output_file, encoding='utf-8', xml_declaration = True)
