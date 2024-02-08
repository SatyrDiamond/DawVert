# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import base64
import json
import lxml.etree as ET
import math
import plugin_output
from pathlib import Path
from objects import dv_dataset
from objects import auto_id
from functions import data_values
from functions import colors

lfoshape = {'sine': 0,'triangle': 1,'saw': 2,'square': 3,'custom': 4,'random': 5}
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

def oneto100(input): return round(float(input) * 100)

def add_window_data(xmltag, w_group, w_name, w_pos, w_size, w_open, w_max):
    wobj = convproj_obj.window_data_get([w_group, w_name])
    if w_pos != None and wobj.pos_x == -1 and wobj.pos_y == -1: wobj.pos_x, wobj.pos_y = w_pos
    if w_size != None and wobj.size_x == -1 and wobj.size_y == -1: wobj.size_x, wobj.size_y = w_size
    xmltag.set("visible", str(int(wobj.open if wobj.open != -1 else w_open)))
    xmltag.set("maximized", str(int(wobj.maximized if wobj.maximized != -1 else w_max)))
    xmltag.set("x", str(wobj.pos_x))
    xmltag.set("y", str(wobj.pos_y))
    xmltag.set("width", str(wobj.size_x))
    xmltag.set("height", str(wobj.size_y))

def add_autopattern(x_tag, x_name, i_pos, i_len, i_tens, i_name, i_mute, i_prog):
    xml_automationpattern = ET.SubElement(x_tag, x_name)
    xml_automationpattern.set('pos', str(int(i_pos)))
    xml_automationpattern.set('len', str(int(i_len)))
    xml_automationpattern.set('tens', str(int(i_tens)))
    xml_automationpattern.set('name', i_name)
    xml_automationpattern.set('mute', str(int(i_mute)))
    xml_automationpattern.set('prog', str(int(i_prog)))
    return xml_automationpattern

def fix_value(val_type, value):
    if val_type == 'float': return float(value)
    elif val_type == 'int': return int(value)
    elif val_type == 'bool': return int(value)
    else: return value

def create_autopoint(xmltag, value, pos, v_type):
    xml_time = ET.SubElement(xmltag, "time")
    xml_time.set('value', str(fix_value(v_type, value)))
    xml_time.set('pos', str(pos))

def parse_auto(xmltag, autopoints_obj):
    curpoint = 0
    for point in autopoints_obj.iter():
        if curpoint != 0 and autopoints_obj.val_type != 'bool' and point.type == 'instant': 
            create_autopoint(xmltag, prevvalue, point.pos-1, autopoints_obj.val_type)
        create_autopoint(xmltag, point.value, point.pos, autopoints_obj.val_type)
        prevvalue = point.value
        curpoint += 1

def make_auto_track(autoidnum, autodata, visualname, automode):
    global trkcX
    print('[output-lmms] Automation Track: '+visualname)
    xml_autotrack = ET.SubElement(trkcX, "track")
    xml_autotrack.set('type', '5')
    xml_autotrack.set('solo', '0')
    xml_autotrack.set('muted', '0')
    xml_autotrack.set('name', visualname)

    for autopl_obj in autodata.data:
        xml_automationpattern = add_autopattern(xml_autotrack, "automationpattern", autopl_obj.position, autopl_obj.duration, 0, visualname, 0, automode)
        parse_auto(xml_automationpattern, autopl_obj.data)
        if autoidnum != None:
            xml_object = ET.SubElement(xml_automationpattern, "object")
            xml_object.set('id', str(autoidnum))

def param_autoid(x_tag, x_name, i_value, i_scale_type, i_id):
    autovarX = ET.SubElement(x_tag, x_name)
    if i_value != None: autovarX.set('value', str(i_value))
    autovarX.set('scale_type', i_scale_type)
    autovarX.set('id', str(i_id))

def create_param_auto(x_tag, x_name, paramset_obj, c_name, c_defval, i_addmul, autoloc, v_type, v_name, writeparamxml):
    param_obj = paramset_obj.get(c_name, c_defval)
    i_value = fix_value(param_obj.type, param_obj.value)
    if i_addmul != None: i_value = (i_value+i_addmul[0])*i_addmul[1]
    aid_found, aid_id, aid_data = autoid_assoc.get(autoloc+[c_name], convproj_obj)
    if aid_found:
        if x_tag != None:
            if aid_data.data != 0:
                if i_addmul != None: aid_data.addmul(i_addmul[0], i_addmul[1])
                param_autoid(x_tag, x_name, i_value if writeparamxml else None, 'linear', aid_id)
        make_auto_track(aid_id, aid_data, v_type+': '+(v_name if v_name else param_obj.visual.name), 1 if param_obj.type != 'bool' else 0)
    elif writeparamxml: x_tag.set(x_name, str(i_value))

def dset_plugparams(pluginname, pluginid, xml_data, plugin_obj):
    global dataset
    paramlist = dataset.params_list('plugin', pluginname)
    if paramlist != None:
        for paramname in paramlist:
            paramlist = dataset.params_i_get('plugin', pluginname, paramname)
            pv_noauto,pv_type,pv_def,pv_min,pv_max,pv_name = paramlist
            if pv_noauto == False: create_param_auto(xml_data, paramname, plugin_obj.params, paramname, pv_def, None, ['plugin', pluginid], 'Plugin', pv_name, True)
            else: xml_data.set(paramname, str(plugin_obj.datavals.get(paramname, pv_def)) )

def lmms_encode_fxchain(xmltag, track_obj, trackname, autoloc):
    fxcX = ET.SubElement(xmltag, "fxchain")
    #create_param_auto(fxcX, 'enabled', track_obj.params, 'fx_enabled', True, None, autoloc, trackname, 'FX Enabled', True)
    fxcX.set('enabled', '1')
    fxcX.set('numofeffects', str(len(track_obj.fxslots_audio)))
    for pluginid in track_obj.fxslots_audio:
        plugin_found, plugin_obj = convproj_obj.get_plugin(pluginid)
        if plugin_found: lmms_encode_effectslot(plugin_obj, pluginid, fxcX)

def add_keyatt(xmltag, i_dict):
    xml_key = ET.SubElement(xmltag, 'key')
    for item in i_dict.items():
        xml_key_file = ET.SubElement(xml_key, 'attribute')
        xml_key_file.set('name', str(item[0]))
        xml_key_file.set('value', str(item[1]))

def sec2exp(value): return math.sqrt(value/5)

def asdrlfo(plugin_obj, xmlobj, asdrtype, xmltype):
    elmodX = ET.SubElement(xmlobj, 'el' + xmltype)

    adsr_obj = plugin_obj.env_asdr_get(asdrtype)
    if asdrtype == 'cutoff': elmodX.set('amt', str(adsr_obj.amount/6000))
    else: elmodX.set('amt', str(float(adsr_obj.amount)))
    elmodX.set('pdel', str(sec2exp(adsr_obj.predelay)))
    elmodX.set('att', str(sec2exp(adsr_obj.attack)))
    elmodX.set('hold', str(sec2exp(adsr_obj.hold)))
    elmodX.set('dec', str(sec2exp(adsr_obj.decay)))
    elmodX.set('sustain', str(adsr_obj.sustain))
    elmodX.set('rel', str(sec2exp(adsr_obj.release)))

    lfo_obj = plugin_obj.lfo_get(asdrtype)
    if asdrtype == 'cutoff': elmodX.set('lamt', str(lfo_obj.amount/6000))
    else: elmodX.set('lamt', str(lfo_obj.amount))
    elmodX.set('lpdel', str(lfo_obj.predelay))
    elmodX.set('latt', str(sec2exp(lfo_obj.attack)))
    elmodX.set('lshp', str(lfoshape[lfo_obj.shape] if lfo_obj.shape in lfoshape else 'sine'))
    elmodX.set('x100', '0')
    lfospeed = 1
    if lfo_obj.speed_type == 'seconds': lfospeed = float(lfo_obj.speed_time) / 20
    if lfospeed > 1:
        elmodX.set('x100', '1')
        lfospeed = lfospeed/100
    elmodX.set('lspd', str(lfospeed))


def asdrlfo_set(plugin_obj, trkX_insttr):
    eldataX = ET.SubElement(trkX_insttr, "eldata")
    filter_obj = plugin_obj.filter
    eldataX.set('fcut', str(filter_obj.freq))

    lmms_filternum = None
    if filter_obj.type == 'all_pass': lmms_filternum = 5

    if filter_obj.type == 'band_pass':
        if filter_obj.subtype == 'csg': lmms_filternum = 2
        if filter_obj.subtype == 'czpg': lmms_filternum = 3
        if filter_obj.subtype == 'rc12': lmms_filternum = 9
        if filter_obj.subtype == 'rc24': lmms_filternum = 12
        if filter_obj.subtype == 'sv': lmms_filternum = 17

    if filter_obj.type == 'formant':
        lmms_filternum = 14
        if filter_obj.subtype == 'fast': lmms_filternum = 20

    if filter_obj.type == 'high_pass':
        lmms_filternum = 1
        if filter_obj.subtype == 'rc12': lmms_filternum = 10
        if filter_obj.subtype == 'rc24': lmms_filternum = 13
        if filter_obj.subtype == 'sv': lmms_filternum = 18

    if filter_obj.type == 'low_pass':
        lmms_filternum = 0
        if filter_obj.subtype == 'double': lmms_filternum = 7
        if filter_obj.subtype == 'rc12': lmms_filternum = 8
        if filter_obj.subtype == 'rc24': lmms_filternum = 11
        if filter_obj.subtype == 'sv': lmms_filternum = 16

    if filter_obj.type == 'moog':
        lmms_filternum = 6
        if filter_obj.subtype == 'double': lmms_filternum = 15

    if filter_obj.type == 'notch':
        lmms_filternum = 4
        if filter_obj.subtype == 'sv': lmms_filternum = 19

    if filter_obj.type == 'tripole':
        lmms_filternum = 21

    if lmms_filternum != None: eldataX.set('ftype', str(lmms_filternum))
    eldataX.set('fwet', str(int(filter_obj.on)))
    eldataX.set('fres', str(filter_obj.q))

    asdrlfo(plugin_obj, eldataX, 'vol', 'vol')
    asdrlfo(plugin_obj, eldataX, 'cutoff', 'cut')
    asdrlfo(plugin_obj, eldataX, 'reso', 'res')


def lmms_encode_plugin(trkX_insttr, track_obj, trackid, trackname):
    xml_instrumentpreplugin = ET.SubElement(trkX_insttr, "instrument")
    visual_plugname = 'none'
    middlenotefix = 0

    plugin_found, plugin_obj = convproj_obj.get_plugin(track_obj.inst_pluginid)
    if plugin_found:
        if plugin_obj.check_match('sampler', 'single'):
            print('[output-lmms]       Plugin: Sampler (Single) > audiofileprocessor')
            xml_instrumentpreplugin.set('name', "audiofileprocessor")
            xml_sampler = ET.SubElement(xml_instrumentpreplugin, "audiofileprocessor")

            xml_sampler.set('reversed', str(int( plugin_obj.datavals.get('reverse', 0) )))
            xml_sampler.set('amp', str(oneto100( plugin_obj.datavals.get('amp', 1) )))
            xml_sampler.set('stutter', str(int( plugin_obj.datavals.get('continueacrossnotes', False) )))

            ref_found, sampleref_obj = plugin_obj.sampleref_fileref('sample', convproj_obj)
            if ref_found: 
                xml_sampler.set('src', sampleref_obj.fileref.get_path(None, True))

                point_value_type = plugin_obj.datavals.get('point_value_type', 'samples')
                sample_start = plugin_obj.datavals.get('start', 0)
                sample_loop = plugin_obj.datavals.get('loop', {})
                out_start, out_loop, out_end = plugin_obj.sampler_calc_pos(sampleref_obj, sample_start, sample_loop) 
                xml_sampler.set('sframe', str(out_start))
                xml_sampler.set('lframe', str(out_loop))
                xml_sampler.set('eframe', str(out_end))

                loopenabled = 0
                if sample_loop:
                    if 'enabled' in sample_loop: loopenabled = sample_loop['enabled']
                    if 'mode' in sample_loop: loopmode = sample_loop['mode']
                if loopenabled == 0: xml_sampler.set('looped', '0')
                if loopenabled == 1:
                    if loopmode == "normal": xml_sampler.set('looped', '1')
                    if loopmode == "pingpong": xml_sampler.set('looped', '2')

            interpolation = plugin_obj.datavals.get('interpolation', "sinc")
            if interpolation == "none": xml_sampler.set('interp', '0')
            elif interpolation == "linear": xml_sampler.set('interp', '1')
            elif interpolation == "sinc": xml_sampler.set('interp', '2')
            else: xml_sampler.set('interp', '2')
            middlenotefix += 3

        elif plugin_obj.check_wildmatch('soundfont2', None):
            print('[output-lmms]       Plugin: soundfont2 > sf2player')
            xml_instrumentpreplugin.set('name', "sf2player")
            xml_sf2 = ET.SubElement(xml_instrumentpreplugin, "sf2player")
            xml_sf2.set('bank', str(int(plugin_obj.datavals.get('bank', 0))))
            xml_sf2.set('patch', str(int(plugin_obj.datavals.get('patch', 0))))
            ref_found, fileref_obj = plugin_obj.get_fileref('file', convproj_obj)
            if ref_found: xml_sf2.set('src', fileref_obj.get_path(None, True))
            create_param_auto(xml_sf2, 'gain', plugin_obj.params, 'gain', 1, None, ['plugin', track_obj.inst_pluginid], 'Plugin', 'gain', True)
            middlenotefix += 12

        elif plugin_obj.check_match('vst2', 'win'):
            print('[output-lmms]       Plugin: vst2 > vestige')
            xml_instrumentpreplugin.set('name', "vestige")
            xml_vst = ET.SubElement(xml_instrumentpreplugin, "vestige")
            middlenotefix += setvstparams(xml_vst, plugin_obj, track_obj.inst_pluginid)

        elif plugin_obj.check_wildmatch('native-lmms', None):
            print('[output-lmms]       Plugin: '+plugin_obj.get_type_visual())
            xml_instrumentpreplugin.set('name', plugin_obj.plugin_subtype)
            xml_lmmsnat = ET.SubElement(xml_instrumentpreplugin, plugin_obj.plugin_subtype)
            dset_plugparams(plugin_obj.plugin_subtype, track_obj.inst_pluginid, xml_lmmsnat, plugin_obj)

            if plugin_obj.plugin_subtype == 'zynaddsubfx':
                zdata = plugin_obj.rawdata_get('data')
                if zdata != b'':
                    zdataxs = ET.fromstring(zdata.decode('ascii'))
                    xml_lmmsnat.append(zdataxs)

            if plugin_obj.plugin_subtype == 'tripleoscillator':
                for oscnum in range(1, 4):
                    out_str = 'userwavefile'+str(oscnum)
                    filepath = plugin_obj.getpath_sampleref(out_str, convproj_obj, None, True)
                    xml_lmmsnat.set(out_str, filepath)
        else:
            print('[output-lmms]       Plugin: '+plugin_obj.get_type_visual() if plugin_obj else None+' > None')
            xml_instrumentpreplugin.set('name', "audiofileprocessor")
        asdrlfo_set(plugin_obj, trkX_insttr)
        return [plugin_obj.plugin_type, plugin_obj.plugin_subtype], middlenotefix

    else:
        print('[output-lmms]       Plugin: None')
        xml_instrumentpreplugin.set('name', "audiofileprocessor")
        return [None, None], middlenotefix

def setvstparams(xml_vst, plugin_obj, pluginid):
    vstpath = plugin_obj.getpath_fileref(convproj_obj, 'plugin', None, True)

    xml_vst.set('program', str(plugin_obj.datavals.get('current_program', 0)))
    xml_vst.set('plugin', vstpath)
    add_keyatt(xml_vst, {'file': vstpath})

    middlenotefix = plugin_obj.datavals.get('middlenotefix', 0)
    datatype = plugin_obj.datavals.get('datatype', 'none')
    numparams = plugin_obj.datavals.get('numparams', 0)

    if datatype == 'bank':
        bank_programs = plugin_obj.datavals.get('programs', 0)
        cur_bank_prog = bank_programs[current_program]
        bankprog_type = cur_bank_prog['datatype']

        if bankprog_type == 'params':
            numparams = cur_bank_prog['numparams']
            xml_vst.set('numparams', str(numparams))
            for param in range(numparams):
                pval = cur_bank_prog['params'][str(param)]['value']
                xml_vst.set('param'+str(param), str(param)+':noname:'+str(pval) )

    if datatype == 'chunk':
        xml_vst.set('chunk', plugin_obj.rawdata_get_b64('chunk'))

    if datatype == 'param':
        xml_vst.set('numparams', str(numparams))
        for param in range(numparams):
            param_obj = plugin_obj.params.get('ext_param_'+str(param), 0)
            xml_vst.set('param'+str(param), str(param)+':'+(param_obj.visual.name if param_obj.visual.name else '')+':'+str(param_obj.value))

    for paramname in plugin_obj.params.list():
        if 'ext_param_' in paramname:
            aid_found, aid_id, aid_data = autoid_assoc.get(['plugin', pluginid, paramname], convproj_obj)
            if aid_found:
                make_auto_track(aid_id, aid_data, 'VST2: #'+str(int(paramname[10:])+1))
                param_autoid(xml_vst, 'param'+paramname[10:], None, 'linear', aid_id)
            
    return middlenotefix

def lmms_encode_effectslot(plugin_obj, pluginid, fxcX):
    fxslotX = ET.SubElement(fxcX, "effect")
    create_param_auto(fxslotX, 'on', plugin_obj.params_slot, 'enabled', True, None, ['slot', pluginid], 'Slot', 'On', True)
    create_param_auto(fxslotX, 'wet', plugin_obj.params_slot, 'wet', 1, None, ['slot', pluginid], 'Slot', 'Wet', True)

    if plugin_obj.check_match('simple', 'reverb'):
        print('[output-lmms]       Audio FX: [reverb] ')
        fxslotX.set('name', 'reverbsc')
        xml_lmmsreverbsc = ET.SubElement(fxslotX, 'ReverbSCControls')

    elif plugin_obj.check_match('universal', 'delay-c'):
        print('[output-lmms]       Audio FX: [delay] ')
        fxslotX.set('name', 'delay')
        xml_lmmsdelay = ET.SubElement(fxslotX, 'Delay')

        d_time_type = plugin_obj.datavals.get('time_type', 'seconds')
        d_time = plugin_obj.datavals.get('time', 1)
        d_wet = plugin_obj.datavals.get('wet', 0.5)
        d_feedback = plugin_obj.datavals.get('feedback', 0.0)

        if d_time_type == 'seconds': xml_lmmsdelay.set('DelayTimeSamples', str(d_time))
        if d_time_type == 'steps': xml_lmmsdelay.set('DelayTimeSamples', str((d_time/8)*((lmms_bpm)/120)))

        xml_lmmsdelay.set('FeebackAmount', str(d_feedback))
        xml_lmmsdelay.set('OutGain', str( plugin_obj.params.get('gain_out', 0) ))

    elif plugin_obj.check_match('vst2', 'win'):
        print('[output-lmms]       Audio FX: [vst2] ')
        fxslotX.set('name', 'vsteffect')
        xml_vst = ET.SubElement(fxslotX, "vsteffectcontrols")
        setvstparams(xml_vst, plugin_obj, pluginid)

    elif plugin_obj.check_wildmatch('native-lmms', None):
        xml_name = fxlist[plugin_obj.plugin_subtype]
        fxslotX.set('name', plugin_obj.plugin_subtype)
        print('[output-lmms]       Audio FX: ['+plugin_obj.plugin_subtype+'] ')
        xml_lmmsnat = ET.SubElement(fxslotX, xml_name)
        dset_plugparams(plugin_obj.plugin_subtype, pluginid, xml_lmmsnat, plugin_obj)

    elif plugin_obj.check_wildmatch('ladspa', None):
        print('[output-lmms]       Audio FX: [ladspa] ')
        fxslotX.set('name', 'ladspaeffect')
        ladspa_file = plugin_obj.datavals.get('path', '')
        ladspa_plugin = plugin_obj.datavals.get('plugin', '')
        ladspa_sep_chan = plugin_obj.datavals.get('seperated_channels', False)
        ladspa_numparams = plugin_obj.datavals.get('numparams', 0)
        xml_ladspa = ET.SubElement(fxslotX, 'ladspacontrols')
        xml_ladspa.set('ports', str(ladspa_numparams*2))
        xml_ladspa.set('link', str(int(not ladspa_sep_chan)))
        if ladspa_file != None: add_keyatt(fxslotX, {'file': Path(ladspa_file).stem, 'plugin': ladspa_plugin})

        for paramid in plugin_obj.params.list():
            if paramid.startswith('ext_param_'):
                paramdata = paramid[10:].split('_')
                if len(paramdata) == 2: paramnum, channum = paramdata
                else: paramnum, channum = paramdata[0], 0
                paramnum = int(paramnum)
                lmms_paramid = 'port'+str(channum)+str(paramnum)
                cvpj_paramvisname = 'LADSPA: #'+str(paramnum+1)

                aid_found, aid_id, aid_data = autoid_assoc.get(['plugin', pluginid], convproj_obj)
                lmms_paramdata = ET.SubElement(xml_ladspa, lmms_paramid)
                paramval = plugin_obj.params.get(paramid, -1).value

                if channum == 0: lmms_paramdata.set('link', str(int(not ladspa_sep_chan)))

                if not aid_found: 
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

def lmms_encode_fxmixer(xmltag):
    for num, fxchannel_obj in convproj_obj.fxrack.items():
        autoloc = ['fxmixer', str(num)]
        autoname = 'FX' + str(num)
        print('[output-lmms] FX ' + str(num))
        fxcX = ET.SubElement(xmltag, "fxchannel")
        fxcX.set('num', str(num))

        name = fxchannel_obj.visual.name if fxchannel_obj.visual.name else 'FX '+str(num)
        fxcX.set('name', data_values.xml_compat(name))
        print('[output-lmms]       Name: ' + name)
        if fxchannel_obj.visual.color: fxcX.set('color', '#' + colors.rgb_float_to_hex(fxchannel_obj.visual.color))

        create_param_auto(fxcX, 'soloed', fxchannel_obj.params, 'solo', False, None, autoloc, autoname, 'Solo', True)
        create_param_auto(fxcX, 'enabled', fxchannel_obj.params, 'muted', False, [-1, -1], autoloc, autoname, 'Enabled', True)
        create_param_auto(fxcX, 'volume', fxchannel_obj.params, 'vol', 1, None, autoloc, autoname, 'Volume', True)

        lmms_encode_fxchain(fxcX, fxchannel_obj, autoname, autoloc)

        if fxchannel_obj.sends.check():
            for target, send_obj in fxchannel_obj.sends.iter():
                sendX = ET.SubElement(fxcX, "send")
                sendX.set('channel', str(int(target)))
                send_obj.sendautoid = None
                if send_obj.sendautoid: 
                    visual_name = 'Send '+str(num)+' > '+str(json_send['channel'])
                    create_param_auto(fxcX, 'amount', send_obj.params, 'amount', 1, None, ['send', send_obj.sendautoid], visual_name, 'Amount', True)
                else:
                    sendX.set('amount', str(send_obj.params.get('amount', 1).value))
        else:
            sendX = ET.SubElement(fxcX, "send")
            sendX.set('channel', '0')
            sendX.set('amount', '1')

        print('[output-lmms]')

patternscount_forprinting = 0
notescount_forprinting = 0
trackscount_forprinting = 0

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
    def parse(self, i_convproj_obj, output_file):
        global trkcX
        global lmms_bpm
        global dataset
        global autoid_assoc
        global convproj_obj
        global trackscount_forprinting
        global notescount_forprinting
        global patternscount_forprinting

        i_convproj_obj.change_timings(48, False)

        convproj_obj = i_convproj_obj
        print('[output-lmms] Output Start')

        dataset = dv_dataset.dataset('./data_dset/lmms.dset')

        autoid_assoc = auto_id.autoid2convproj(convproj_obj)

        projX = ET.Element("lmms-project")
        projX.set('type', "song")
        projX.set('creator', "DawVert")
        projX.set('creatorversion', "1.2.2")
        projX.set('version', "1.0")
        headX = ET.SubElement(projX, "head") 
        songX = ET.SubElement(projX, "song")
        trkcX = ET.SubElement(songX, "trackcontainer")

        add_window_data(trkcX, 'main', 'tracklist', [5,5], [720,300], True, False)

        lmms_bpm = convproj_obj.params.get('bpm', 140).value

        create_param_auto(headX, 'bpm', convproj_obj.params, 'bpm', 120, None, ['main'], 'Main', 'Tempo', True)
        create_param_auto(headX, 'masterpitch', convproj_obj.params, 'pitch', 0, None, ['main'], 'Main', 'Pitch', True)
        create_param_auto(headX, 'mastervol', convproj_obj.params, 'vol', 1, [0, 100], ['main'], 'Main', 'Volume', True)

        headX.set("timesig_numerator", str(convproj_obj.timesig[0]))
        headX.set("timesig_denominator", str(convproj_obj.timesig[1]))

        for trackid, track_obj in convproj_obj.iter_track():
            trackscount_forprinting += 1

            autoloc = ['track', trackid]

            trackname = track_obj.visual.name if track_obj.visual.name else 'noname'
            trackcolor = track_obj.visual.color

            if track_obj.type in ['instrument', 'audio']:
                xml_track = ET.SubElement(trkcX, "track")
                xml_track.set('name', data_values.xml_compat(trackname) )

                create_param_auto(xml_track, 'solo', track_obj.params, 'solo', False, None, autoloc, trackname, 'Solo', True)
                create_param_auto(xml_track, 'enabled', track_obj.params, 'muted', False, [-1, -1], autoloc, trackname, 'On', True)

                if track_obj.type == 'instrument':
                    print('[output-lmms] Instrument Track')
                    print('[output-lmms]       Name: ' + trackname)
                    xml_track.set('type', "0")
                    trkX_insttr = ET.SubElement(xml_track, "instrumenttrack")

                    trkX_insttr.set('fxch', str(track_obj.fxrack_channel))
                    trkX_insttr.set('pitchrange', "12")

                    create_param_auto(trkX_insttr, 'vol', track_obj.params, 'vol', 1, [0, 100], autoloc, trackname, 'Vol', True)
                    create_param_auto(trkX_insttr, 'pan', track_obj.params, 'pan', 0, [0, -1], autoloc, trackname, 'Pan', True)
                    create_param_auto(trkX_insttr, 'usemasterpitch', track_obj.params, 'usemasterpitch', True, None, autoloc, trackname, 'Use Master Pitch', True)
                    create_param_auto(trkX_insttr, 'pitch', track_obj.params, 'pitch', 0, [0, 100], autoloc, trackname, 'Pitch', True)

                    for pluginid in track_obj.fxslots_notes:
                        plugin_found, plugin_obj = convproj_obj.get_plugin(pluginid)
                        if plugin_found:
                            if plugin_obj.check_match('native-lmms', 'arpeggiator'):
                                trkX_notefx = ET.SubElement(trkX_insttr, "arpeggiator")
                                create_param_auto(trkX_notefx, 'arp-enabled', plugin_obj.params_slot, 'enabled', False, None, ['slot', pluginid], 'Arp', 'On', True)
                                dset_plugparams('arpeggiator', pluginid, trkX_notefx, plugin_obj)
                            if plugin_obj.check_match('native-lmms', 'chordcreator'):
                                trkX_notefx = ET.SubElement(trkX_insttr, "chordcreator")
                                create_param_auto(trkX_notefx, 'chord-enabled', plugin_obj.params_slot, 'enabled', False, None, ['slot', pluginid], 'Chord', 'On', True)
                                dset_plugparams('chordcreator', pluginid, trkX_notefx, plugin_obj)

                    plugintype, middlenotefix = lmms_encode_plugin(trkX_insttr, track_obj, trackid, trackname)

                    middlenote = track_obj.datavals.get('middlenote', 0)+middlenotefix
                    trkX_insttr.set('basenote', str(middlenote+57))

                    printcountpat = 0
                    print('[output-lmms]       Placements: ', end='')

                    track_obj.placements.sort_notes()
                    for notespl_obj in track_obj.placements.iter_notes():
                        patternscount_forprinting += 1
                        patX = ET.SubElement(xml_track, "pattern")
                        patX.set('pos', str(int(notespl_obj.position)))
                        patX.set('muted', str(int(notespl_obj.muted)))
                        patX.set('steps', "16")
                        patX.set('name', notespl_obj.visual.name if notespl_obj.visual.name else "" )
                        patX.set('type', "1")
                        if notespl_obj.visual.color: patX.set('color', '#' + colors.rgb_float_to_hex(notespl_obj.visual.color))
                        notespl_obj.notelist.sort()
                        for t_pos, t_dur, t_keys, t_vol, t_inst, t_extra, t_auto, t_slide in notespl_obj.notelist.iter():
                            for t_key in t_keys:
                                notescount_forprinting += 1
                                #print(t_pos, t_dur, t_keys, t_vol, t_inst, t_extra, t_auto, t_slide)
                                noteX = ET.SubElement(patX, "note")
                                noteX.set('key', str(t_key+60))
                                noteX.set('pos', str(int(t_pos)))
                                noteX.set('pan', str(oneto100(t_extra['pan']) if 'pan' in t_extra else 0))
                                noteX.set('len', str(int(max(1,t_dur))))
                                noteX.set('vol', str(int(oneto100(t_vol))))
                                if t_auto:
                                    if 'pitch' in t_auto:
                                        xml_automationpattern = ET.SubElement(noteX, "automationpattern")
                                        xml_detuning = add_autopattern(xml_automationpattern, "detuning", 0, t_dur, 1, '', 0, 1)
                                        parse_auto(xml_detuning, t_auto['pitch'])

                        printcountpat += 1
                        print('['+str(printcountpat), end='] ')
                    print()

                    trkX_midiport = ET.SubElement(trkX_insttr, "midiport")
                    trkX_midiport.set('fixedoutputvelocity',str(track_obj.midi.out_fixedvelocity))
                    trkX_midiport.set('readable',str(int(track_obj.midi.in_enabled)))
                    trkX_midiport.set('outputcontroller',"0")
                    trkX_midiport.set('basevelocity',str(track_obj.midi.basevelocity))
                    trkX_midiport.set('outputprogram',str(track_obj.midi.out_patch))
                    trkX_midiport.set('writable',str(int(track_obj.midi.out_enabled)))
                    trkX_midiport.set('fixedinputvelocity',str(track_obj.midi.in_fixedvelocity))
                    trkX_midiport.set('inputchannel',str(track_obj.midi.in_chan+1))
                    trkX_midiport.set('inputcontroller',"0")
                    trkX_midiport.set('outputchannel',str(track_obj.midi.out_chan+1))
                    trkX_midiport.set('fixedoutputnote',str(track_obj.midi.out_fixednote))
                    lmms_encode_fxchain(trkX_insttr, track_obj, trackname, autoloc)

                if track_obj.type == 'audio':
                    print('[output-lmms] Audio Track')
                    print('[output-lmms]       Name: ' + trackname)
                    xml_track.set('type', "2")
                    trkX_samptr = ET.SubElement(xml_track, "sampletrack")
                    trkX_samptr.set('fxch', str(track_obj.fxrack_channel))

                    create_param_auto(trkX_samptr, 'vol', track_obj.params, 'vol', 1, [0, 100], autoloc, trackname, 'Vol', True)
                    create_param_auto(trkX_samptr, 'pan', track_obj.params, 'pan', 0, [-1, -1], autoloc, trackname, 'Pan', True)

                    printcountpat = 0
                    print('[output-lmms]       Placements: ', end='')

                    track_obj.placements.sort_audio()
                    for audiopl_obj in track_obj.placements.iter_audio():
                        xml_sampletco = ET.SubElement(xml_track, 'sampletco')
                        xml_sampletco.set('pos', str(int(audiopl_obj.position)))
                        xml_sampletco.set('len', str(int(audiopl_obj.duration)))

                        ref_found, sampleref_obj = convproj_obj.get_sampleref(audiopl_obj.sampleref)
                        if ref_found:
                            xml_sampletco.set('src', sampleref_obj.fileref.get_path(None, True))

                        xml_sampletco.set('muted', str(int(audiopl_obj.muted)))
                        if audiopl_obj.visual.color: xml_sampletco.set('color', '#' + colors.rgb_float_to_hex(audiopl_obj.visual.color))

                        if audiopl_obj.cut_type == 'cut':
                            if 'start' in audiopl_obj.cut_data:
                                xml_sampletco.set('off', str(int(audiopl_obj.cut_data['start']*-1)))

                        printcountpat += 1
                        print('['+str(printcountpat), end='] ')
                    print()
                    lmms_encode_fxchain(trkX_samptr, track_obj, trackname, autoloc)

                if trackcolor: xml_track.set('color', '#' + colors.rgb_float_to_hex(trackcolor))


                print('[output-lmms]')

        xml_fxmixer = ET.SubElement(songX, "fxmixer")
        add_window_data(xml_fxmixer, 'main', 'fxmixer', [102,280], [543,333], True, False)
        lmms_encode_fxmixer(xml_fxmixer)

        XControllerRackView = ET.SubElement(songX, "ControllerRackView")
        add_window_data(XControllerRackView, 'main', 'controller_rack_view', [680,310], [350,200], False, False)
        Xpianoroll = ET.SubElement(songX, "pianoroll")
        add_window_data(Xpianoroll, 'main', 'piano_roll', [5,5], [970,480], False, False)
        Xautomationeditor = ET.SubElement(songX, "automationeditor")
        add_window_data(Xautomationeditor, 'main', 'automation_editor', [1,1], [860,400], False, False)

        convproj_obj.metadata.comment_text
        convproj_obj.metadata.comment_datatype

        if convproj_obj.metadata.comment_text:
            notesX = ET.SubElement(songX, "projectnotes")
            add_window_data(notesX, 'main', 'project_notes', [728, 5], [389, 300], True, False)
            if convproj_obj.metadata.comment_datatype == 'html': 
                notesX.text = ET.CDATA(convproj_obj.metadata.comment_text)
            if convproj_obj.metadata.comment_datatype == 'text': 
                notesX.text = ET.CDATA(convproj_obj.metadata.comment_text.replace('\n', '<br/>').replace('\r', '<br/>'))
        else:
            notesX = ET.SubElement(songX, "projectnotes")
            notesX.text = ET.CDATA("")

        print("[output-lmms] Number of Notes: " + str(notescount_forprinting))
        print("[output-lmms] Number of Patterns: " + str(patternscount_forprinting))
        print("[output-lmms] Number of Tracks: " + str(trackscount_forprinting))      

        timelineX = ET.SubElement(songX, "timeline")
        timelineX.set("lpstate", str(convproj_obj.loop_active))
        timelineX.set("lp0pos", str(convproj_obj.loop_start))
        timelineX.set("lp1pos", str(convproj_obj.loop_end))

        outfile = ET.ElementTree(projX)
        
        ET.indent(outfile)
        outfile.write(output_file, encoding='utf-8', xml_declaration = True)
