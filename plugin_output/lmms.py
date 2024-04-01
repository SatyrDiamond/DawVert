# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import base64
import json
import lxml.etree as ET
import math
import plugin_output
import struct
from pathlib import Path
from objects import dv_dataset
from objects import auto_id
from functions import data_values
from functions import colors

chordids = [None,"major","majb5","minor","minb5","sus2","sus4","aug","augsus4","tri","6","6sus4","6add9","m6","m6add9","7","7sus4","7#5","7b5","7#9","7b9","7#5#9","7#5b9","7b5b9","7add11","7add13","7#11","maj7","maj7b5","maj7#5","maj7#11","maj7add13","m7","m7b5","m7b9","m7add11","m7add13","m-maj7","m-maj7add11","m-maj7add13","9","9sus4","add9","9#5","9b5","9#11","9b13","maj9","maj9sus4","maj9#5","maj9#11","m9","madd9","m9b5","m9-maj7","11","11b9","maj11","m11","m-maj11","13","13#9","13b9","13b5b9","maj13","m13","m-maj13","full_major","harmonic_minor","melodic_minor","whole_tone","diminished","major_pentatonic","minor_pentatonic","jap_in_sen","major_bebop","dominant_bebop","blues","arabic","enigmatic","neopolitan","neopolitan_minor","hungarian_minor","dorian","phrygian","lydian","mixolydian","aeolian","locrian","full_minor","chromatic","half-whole_diminished","5","phrygian_dominant","persian"]

lfoshape = {'sine': 0,'triangle': 1,'saw': 2,'square': 3,'custom': 4,'random': 5}
l_arpdirection = {'up': 0,'down': 1,'updown': 2,'downup': 3,'random': 4}
l_arpmode = {'free': 0,'sort': 1,'sync': 2}

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

def filternum(i_type, i_subtype):
    lmms_filternum = 0
    if i_type == 'all_pass': lmms_filternum = 5

    if i_type == 'band_pass':
        if i_subtype == 'csg': lmms_filternum = 2
        if i_subtype == 'czpg': lmms_filternum = 3
        if i_subtype == 'rc12': lmms_filternum = 9
        if i_subtype == 'rc24': lmms_filternum = 12
        if i_subtype == 'sv': lmms_filternum = 17

    if i_type == 'formant':
        lmms_filternum = 14
        if i_subtype == 'fast': lmms_filternum = 20

    if i_type == 'high_pass':
        lmms_filternum = 1
        if i_subtype == 'rc12': lmms_filternum = 10
        if i_subtype == 'rc24': lmms_filternum = 13
        if i_subtype == 'sv': lmms_filternum = 18

    if i_type == 'low_pass':
        lmms_filternum = 0
        if i_subtype == 'double': lmms_filternum = 7
        if i_subtype == 'rc12': lmms_filternum = 8
        if i_subtype == 'rc24': lmms_filternum = 11
        if i_subtype == 'sv': lmms_filternum = 16

    if i_type == 'moog':
        lmms_filternum = 6
        if i_subtype == 'double': lmms_filternum = 15

    if i_type == 'notch':
        lmms_filternum = 4
        if i_subtype == 'sv': lmms_filternum = 19

    if i_type == 'tripole':
        lmms_filternum = 21

    return lmms_filternum

def set_timedata(xmltag, x_name, timing_obj):
    if timing_obj.type == 'steps':
        syncmode = 8
        if timing_obj.speed_steps == 16*8: syncmode = 1
        elif timing_obj.speed_steps == 16: syncmode = 2
        elif timing_obj.speed_steps == 8: syncmode = 3
        elif timing_obj.speed_steps == 4: syncmode = 4
        elif timing_obj.speed_steps == 2: syncmode = 5
        elif timing_obj.speed_steps == 1: syncmode = 6
        elif timing_obj.speed_steps == 0.5: syncmode = 7
        else: 
            numerator, denominator = timing_obj.get_frac()
            xmltag.set(x_name+'_numerator', str(numerator))
            xmltag.set(x_name+'_denominator', str(denominator))
        xmltag.set(x_name+'_syncmode', str(syncmode))
        return True

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
    xml_time.set('pos', str(int(pos)))

def parse_auto(xmltag, autopoints_obj):
    curpoint = 0
    auto_points = {}
    #print('-----')
    for point in autopoints_obj.iter():
        #print(point.pos, point.value, point.type
        if point.pos in auto_points: 
            auto_points[point.pos-1] = auto_points[point.pos]
            del auto_points[point.pos]
        auto_points[point.pos] = [point.value, point.type]

    for p, d in auto_points.items():
        if curpoint != 0 and autopoints_obj.val_type != 'bool' and d[1] == 'instant': 
            create_autopoint(xmltag, prevvalue, p-1, autopoints_obj.val_type)
        create_autopoint(xmltag, d[0], p, autopoints_obj.val_type)
        prevvalue = d[0]
        curpoint += 1

def make_auto_track(autoidnum, autodata, visualname, automode):
    global trkcX
    #print('[output-lmms] Automation Track: '+visualname)
    xml_autotrack = ET.SubElement(trkcX, "track")
    xml_autotrack.set('type', '5')
    xml_autotrack.set('solo', '0')
    xml_autotrack.set('muted', '0')
    xml_autotrack.set('name', visualname)

    for autopl_obj in autodata.iter():

        autopl_obj.remove_cut()

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
    aid_found, aid_data = convproj_obj.automation.get(autoloc+[c_name], 'float')
    if aid_found:
        if x_tag != None:
            if i_addmul != None: aid_data.calc_addmul(i_addmul[0], i_addmul[1])
            param_autoid(x_tag, x_name, i_value if writeparamxml else None, 'linear', aid_data.id)
        if aid_data.pl_points:
            make_auto_track(aid_data.id, aid_data.pl_points, v_type+': '+(v_name if v_name else param_obj.visual.name), 1 if param_obj.type != 'bool' else 0)
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
    elmodX.set('rel', str(sec2exp(adsr_obj.release*( pow(2, adsr_obj.release_tension*2) ))))

    lfo_obj = plugin_obj.lfo_get(asdrtype)
    if asdrtype == 'cutoff': elmodX.set('lamt', str(lfo_obj.amount/6000))
    else: elmodX.set('lamt', str(lfo_obj.amount))
    elmodX.set('lpdel', str(sec2exp(lfo_obj.predelay/4)))
    elmodX.set('latt', str(sec2exp(lfo_obj.attack)))
    elmodX.set('lshp', str(lfoshape[lfo_obj.shape] if lfo_obj.shape in lfoshape else 'sine'))
    elmodX.set('x100', '0')
    lfospeed = 1
    lfospeed = float(lfo_obj.time.speed_seconds) / 20
    if lfospeed > 1:
        elmodX.set('x100', '1')
        lfospeed = lfospeed/100
    elmodX.set('lspd', str(lfospeed))


def asdrlfo_set(plugin_obj, trkX_insttr):
    eldataX = ET.SubElement(trkX_insttr, "eldata")
    filter_obj = plugin_obj.filter
    eldataX.set('fcut', str(filter_obj.freq))

    eldataX.set('ftype', str(filternum(filter_obj.type, filter_obj.subtype)))
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
        if plugin_obj.check_match('sampler', 'single') or plugin_obj.check_match('sampler', 'drumsynth'):
            #print('[output-lmms]       Plugin: Sampler (Single) > audiofileprocessor')
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

        elif plugin_obj.check_match('sampler', 'slicer') and False:
            #print('test')
            xml_instrumentpreplugin.set('name', "slicert")
            xml_slicert = ET.SubElement(xml_instrumentpreplugin, "slicert")

            ref_found, sampleref_obj = plugin_obj.sampleref_fileref('sample', convproj_obj)
            #print(ref_found, sampleref_obj)
            if ref_found and sampleref_obj.dur_samples: 
                slice_bpm = plugin_obj.datavals.get('bpm', 120)
                xml_slicert.set('src', sampleref_obj.fileref.get_path(None, True))
                xml_slicert.set('totalSlices', str(len(plugin_obj.regions.data)))
                xml_slicert.set('version', str(1))
                xml_slicert.set('fadeOut', str(10))
                xml_slicert.set('origBPM', str(slice_bpm))
                for c, x in enumerate(plugin_obj.regions): 
                    xml_slicert.set('slice_'+str(c+1), str(x[0]/sampleref_obj.dur_samples))
            middlenotefix += 1

        elif plugin_obj.check_wildmatch('soundfont2', None):
            #print('[output-lmms]       Plugin: soundfont2 > sf2player')
            xml_instrumentpreplugin.set('name', "sf2player")
            xml_sf2 = ET.SubElement(xml_instrumentpreplugin, "sf2player")
            xml_sf2.set('bank', str(int(plugin_obj.datavals.get('bank', 0))))
            xml_sf2.set('patch', str(int(plugin_obj.datavals.get('patch', 0))))
            ref_found, fileref_obj = plugin_obj.get_fileref('file', convproj_obj)
            if ref_found: xml_sf2.set('src', fileref_obj.get_path(None, True))
            create_param_auto(xml_sf2, 'gain', plugin_obj.params, 'gain', 1, None, ['plugin', track_obj.inst_pluginid], 'Plugin', 'gain', True)
            middlenotefix += 12

        elif plugin_obj.check_match('vst2', 'win'):
            #print('[output-lmms]       Plugin: vst2 > vestige')
            xml_instrumentpreplugin.set('name', "vestige")
            xml_vst = ET.SubElement(xml_instrumentpreplugin, "vestige")
            middlenotefix += setvstparams(xml_vst, plugin_obj, track_obj.inst_pluginid)

        elif plugin_obj.check_wildmatch('native-lmms', None):
            #print('[output-lmms]       Plugin: '+plugin_obj.get_type_visual())
            xml_instrumentpreplugin.set('name', plugin_obj.plugin_subtype)
            xml_lmmsnat = ET.SubElement(xml_instrumentpreplugin, plugin_obj.plugin_subtype)
            dset_plugparams(plugin_obj.plugin_subtype, track_obj.inst_pluginid, xml_lmmsnat, plugin_obj)

            if plugin_obj.plugin_subtype == 'zynaddsubfx':
                zdata = plugin_obj.rawdata_get('data')
                if zdata != b'':
                    zdataxs = ET.fromstring(zdata.decode('ascii'))
                    xml_lmmsnat.append(zdataxs)

            if plugin_obj.plugin_subtype == 'tripleoscillator':
                for oscnum in range(3):
                    out_str = 'userwavefile'+str(oscnum)
                    filepath = plugin_obj.getpath_sampleref(out_str, convproj_obj, None, True)
                    xml_lmmsnat.set(out_str, filepath)

            if plugin_obj.plugin_subtype == 'vibedstrings':
                for num in range(9):
                    graphid = 'graph'+str(num)
                    wave_obj = plugin_obj.wave_get(graphid)
                    wave_data = wave_obj.get_wave(128)
                    graphdata = base64.b64encode(struct.pack('f'*128, *wave_data)).decode()
                    xml_lmmsnat.set(graphid, graphdata)
        else:
            #print('[output-lmms]       Plugin: '+plugin_obj.get_type_visual() if plugin_obj else None+' > None')
            xml_instrumentpreplugin.set('name', "audiofileprocessor")
        asdrlfo_set(plugin_obj, trkX_insttr)
        return [plugin_obj.plugin_type, plugin_obj.plugin_subtype], middlenotefix

    else:
        #print('[output-lmms]       Plugin: None')
        xml_instrumentpreplugin.set('name', "audiofileprocessor")
        return [None, None], middlenotefix

def setvstparams(xml_vst, plugin_obj, pluginid):
    vstpath = plugin_obj.getpath_fileref(convproj_obj, 'plugin', 'win', True)

    current_program = plugin_obj.datavals.get('current_program', 0)

    xml_vst.set('program', str(current_program))
    xml_vst.set('plugin', vstpath)
    add_keyatt(xml_vst, {'file': vstpath})

    middlenotefix = plugin_obj.datavals.get('middlenotefix', 0)
    datatype = plugin_obj.datavals.get('datatype', 'none')
    numparams = plugin_obj.datavals.get('numparams', 0)

    if datatype == 'bank':
        bank_programs = plugin_obj.datavals.get('programs', {})
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
            aid_found, aid_data = convproj_obj.automation.get(['plugin', pluginid, paramname], 'float')
            if aid_found:
                make_auto_track(aid_data.id, aid_data.pl_points, 'VST2: #'+str(int(paramname[10:])+1), 1)
                param_autoid(xml_vst, 'param'+paramname[10:], None, 'linear', aid_data.id)
            
    return middlenotefix

def lmms_encode_effectslot(plugin_obj, pluginid, fxcX):
    fxslotX = ET.SubElement(fxcX, "effect")
    create_param_auto(fxslotX, 'on', plugin_obj.params_slot, 'enabled', True, None, ['slot', pluginid], 'Slot', 'On', True)
    create_param_auto(fxslotX, 'wet', plugin_obj.params_slot, 'wet', 1, None, ['slot', pluginid], 'Slot', 'Wet', True)

    if plugin_obj.check_match('simple', 'reverb'):
        #print('[output-lmms]       Audio FX: [reverb] ')
        fxslotX.set('name', 'reverbsc')
        xml_lmmsreverbsc = ET.SubElement(fxslotX, 'ReverbSCControls')
        xml_lmmsreverbsc.set('size', str(0.2))
        xml_lmmsreverbsc.set('color', str(15000))

    elif plugin_obj.check_match('universal', 'delay'):
        #print('[output-lmms]       Audio FX: [delay] ')
        fxslotX.set('name', 'delay')
        xml_lmmsdelay = ET.SubElement(fxslotX, 'Delay')
        timing_obj = plugin_obj.timing_get('center')
        is_steps = set_timedata(xml_lmmsdelay, 'DelayTimeSamples', timing_obj)
        if not is_steps: xml_lmmsdelay.set('DelayTimeSamples', str(timing_obj.speed_seconds))
        d_feedback = plugin_obj.datavals.get('c_fb', 0.0)
        xml_lmmsdelay.set('FeebackAmount', str(d_feedback))

    elif plugin_obj.check_match('universal', 'filter'):
        fxslotX.set('name', 'dualfilter')

        filter_obj = plugin_obj.filter
        xml_filter = ET.SubElement(fxslotX, 'DualFilterControls')
        xml_filter.set('cut1', str(filter_obj.freq))
        xml_filter.set('cut2', "7000")
        xml_filter.set('enabled1', str(int(filter_obj.on)))
        xml_filter.set('enabled2', "0")
        xml_filter.set('filter1', str(filternum(filter_obj.type, filter_obj.subtype)))
        xml_filter.set('filter2', "0")
        xml_filter.set('gain1', "100")
        xml_filter.set('gain2', "100")
        xml_filter.set('mix', "-1")
        xml_filter.set('res1', str(filter_obj.q))
        xml_filter.set('res2', "0.5")

    elif plugin_obj.check_match('vst2', 'win'):
        #print('[output-lmms]       Audio FX: [vst2] ')
        fxslotX.set('name', 'vsteffect')
        xml_vst = ET.SubElement(fxslotX, "vsteffectcontrols")
        setvstparams(xml_vst, plugin_obj, pluginid)

    elif plugin_obj.check_wildmatch('native-lmms', None):
        xml_name = fxlist[plugin_obj.plugin_subtype]
        fxslotX.set('name', plugin_obj.plugin_subtype)
        #print('[output-lmms]       Audio FX: ['+plugin_obj.plugin_subtype+'] ')
        xml_lmmsnat = ET.SubElement(fxslotX, xml_name)
        dset_plugparams(plugin_obj.plugin_subtype, pluginid, xml_lmmsnat, plugin_obj)

    elif plugin_obj.check_wildmatch('ladspa', None):
        #print('[output-lmms]       Audio FX: [ladspa] ')
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

                aid_found, aid_data = convproj_obj.automation.get(['plugin', pluginid, paramid], 'float')
                lmms_paramdata = ET.SubElement(xml_ladspa, lmms_paramid)
                paramval = plugin_obj.params.get(paramid, -1).value

                if channum == 0: lmms_paramdata.set('link', str(int(not ladspa_sep_chan)))

                if not aid_found: 
                    lmms_paramdata.set('data', str(paramval))
                else:
                    lmms_paramdata_data = ET.SubElement(lmms_paramdata, 'data')
                    lmms_paramdata_data.set('value', str(paramval))
                    lmms_paramdata_data.set('scale_type', 'linear')
                    lmms_paramdata_data.set('id', str(aid_data.id))
                    make_auto_track(aid_data.id, aid_data.pl_points, cvpj_paramvisname, 1)

    else:
        fxslotX.set('name', 'stereomatrix')
        xml_lmmsnat = ET.SubElement(fxslotX, 'stereomatrixcontrols')

def lmms_encode_fxmixer(xmltag):
    for num, fxchannel_obj in convproj_obj.fxrack.items():
        autoloc = ['fxmixer', str(num)]
        autoname = 'FX' + str(num)
        #print('[output-lmms] FX ' + str(num))
        fxcX = ET.SubElement(xmltag, "fxchannel")
        fxcX.set('num', str(num))

        name = fxchannel_obj.visual.name if fxchannel_obj.visual.name else 'FX '+str(num)
        fxcX.set('name', data_values.xml_compat(name))
        #print('[output-lmms]       Name: ' + name)
        if fxchannel_obj.visual.color: fxcX.set('color', '#' + colors.rgb_float_to_hex(fxchannel_obj.visual.color))

        create_param_auto(fxcX, 'soloed', fxchannel_obj.params, 'solo', False, None, autoloc, autoname, 'Solo', True)
        create_param_auto(fxcX, 'enabled', fxchannel_obj.params, 'muted', False, [-1, -1], autoloc, autoname, 'Enabled', True)
        create_param_auto(fxcX, 'volume', fxchannel_obj.params, 'vol', 1, None, autoloc, autoname, 'Volume', True)

        lmms_encode_fxchain(fxcX, fxchannel_obj, autoname, autoloc)

        if fxchannel_obj.sends.to_master_active:
            master_send_obj = fxchannel_obj.sends.to_master
            sendX = ET.SubElement(fxcX, "send")
            sendX.set('channel', str(0))
            sendX.set('amount', str(master_send_obj.params.get('amount', 1).value))

        if fxchannel_obj.sends.check():
            for target, send_obj in fxchannel_obj.sends.iter():
                target = int(target)
                sendX = ET.SubElement(fxcX, "send")
                sendX.set('channel', str(target))
                if send_obj.sendautoid: 
                    visual_name = 'Send '+str(num)+' > '+str(target)
                    create_param_auto(fxcX, 'amount', send_obj.params, 'amount', 1, None, [('send' if target else 'send_master'), send_obj.sendautoid], visual_name, 'Amount', True)
                else:
                    sendX.set('amount', str(send_obj.params.get('amount', 1).value))
        else:
            sendX = ET.SubElement(fxcX, "send")
            sendX.set('channel', '0')
            sendX.set('amount', '1')

        #print('[output-lmms]')

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
    def getdawinfo(self, dawinfo_obj): 
        dawinfo_obj.name = 'LMMS'
        dawinfo_obj.file_ext = 'mmp'
        dawinfo_obj.fxtype = 'rack'
        dawinfo_obj.fxrack_params = ['enabled','vol']
        dawinfo_obj.auto_types = ['pl_points']
        dawinfo_obj.plugin_included = ['sampler:single','fm:opl2','soundfont2','native-lmms','universal:arpeggiator','universal:chord_creator','universal:delay']
        dawinfo_obj.plugin_ext = ['vst2','ladspa']
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
        #print('[output-lmms] Output Start')

        dataset = dv_dataset.dataset('./data_dset/lmms.dset')

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
                    #print('[output-lmms] Instrument Track')
                    #print('[output-lmms]       Name: ' + trackname)
                    xml_track.set('type', "0")
                    trkX_insttr = ET.SubElement(xml_track, "instrumenttrack")

                    trkX_insttr.set('fxch', str(track_obj.fxrack_channel))
                    trkX_insttr.set('pitchrange', "12")

                    create_param_auto(trkX_insttr, 'vol', track_obj.params, 'vol', 1, [0, 100], autoloc, trackname, 'Vol', True)
                    create_param_auto(trkX_insttr, 'pan', track_obj.params, 'pan', 0, [0, -100], autoloc, trackname, 'Pan', True)
                    create_param_auto(trkX_insttr, 'usemasterpitch', track_obj.params, 'usemasterpitch', True, None, autoloc, trackname, 'Use Master Pitch', True)
                    create_param_auto(trkX_insttr, 'pitch', track_obj.params, 'pitch', 0, [0, 100], autoloc, trackname, 'Pitch', True)

                    for pluginid in track_obj.fxslots_notes:
                        plugin_found, plugin_obj = convproj_obj.get_plugin(pluginid)
                        if plugin_found:

                            if plugin_obj.check_match('universal', 'arpeggiator'):
                                trkX_notefx = ET.SubElement(trkX_insttr, "arpeggiator")
                                create_param_auto(trkX_notefx, 'arp-enabled', plugin_obj.params_slot, 'enabled', False, None, ['slot', pluginid], 'Arp', 'On', True)
                                #dset_plugparams('arpeggiator', pluginid, trkX_notefx, plugin_obj)

                                arpdir = plugin_obj.datavals.get('direction', 'up')
                                arpmode = plugin_obj.datavals.get('mode', 'free')
                                timing_obj = plugin_obj.timing_get('main')
                                is_steps = set_timedata(trkX_notefx, 'arptime', timing_obj)
                                if not is_steps: trkX_notefx.set('arptime', str(timing_obj.speed_seconds*1000))
                                trkX_notefx.set('arpdir', str(l_arpdirection[arpdir] if arpdir in l_arpdirection else 0))
                                trkX_notefx.set('arpmode', str(l_arpmode[arpmode] if arpmode in l_arpmode else 0))
                                trkX_notefx.set('arpgate', str(plugin_obj.datavals.get('gate', 1)*100))
                                trkX_notefx.set('arpcycle', str(plugin_obj.datavals.get('cycle', 0)))
                                trkX_notefx.set('arprange', str(plugin_obj.datavals.get('range', 0)))
                                trkX_notefx.set('arpmiss', str(plugin_obj.datavals.get('miss_rate', 0)*100))
                                trkX_notefx.set('arpskip', str(plugin_obj.datavals.get('skip_rate', 0)*100))
                                chord_obj = plugin_obj.chord_get('main')
                                chordid = chordids.index(chord_obj.chord_type) if chord_obj.chord_type in chordids else 0
                                trkX_notefx.set('arp', str(chordid))

                            if plugin_obj.check_match('universal', 'chord_creator'):
                                trkX_notefx = ET.SubElement(trkX_insttr, "chordcreator")
                                create_param_auto(trkX_notefx, 'chord-enabled', plugin_obj.params_slot, 'enabled', False, None, ['slot', pluginid], 'Chord', 'On', True)
                                chord_obj = plugin_obj.chord_get('main')
                                chordid = chordids.index(chord_obj.chord_type) if chord_obj.chord_type in chordids else 0
                                trkX_notefx.set('chord', str(chordid))
                                trkX_notefx.set('chordrange', str(plugin_obj.datavals.get('range', 0)))


                    plugintype, middlenotefix = lmms_encode_plugin(trkX_insttr, track_obj, trackid, trackname)

                    middlenote = track_obj.datavals.get('middlenote', 0)+middlenotefix
                    trkX_insttr.set('basenote', str(middlenote+57))

                    #printcountpat = 0
                    #print('[output-lmms]       Placements: ', end='')

                    track_obj.placements.pl_notes.sort()
                    for notespl_obj in track_obj.placements.pl_notes:
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

                        #printcountpat += 1
                        #print('['+str(printcountpat), end='] ')
                    #print()

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
                    #print('[output-lmms] Audio Track')
                    #print('[output-lmms]       Name: ' + trackname)
                    xml_track.set('type', "2")
                    trkX_samptr = ET.SubElement(xml_track, "sampletrack")
                    trkX_samptr.set('fxch', str(track_obj.fxrack_channel))

                    create_param_auto(trkX_samptr, 'vol', track_obj.params, 'vol', 1, [0, 100], autoloc, trackname, 'Vol', True)
                    create_param_auto(trkX_samptr, 'pan', track_obj.params, 'pan', 0, [-1, -1], autoloc, trackname, 'Pan', True)

                    #printcountpat = 0
                    #print('[output-lmms]       Placements: ', end='')

                    track_obj.placements.pl_audio.sort()
                    for audiopl_obj in track_obj.placements.pl_audio:
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

                        #printcountpat += 1
                        #print('['+str(printcountpat), end='] ')
                    #print()
                    lmms_encode_fxchain(trkX_samptr, track_obj, trackname, autoloc)

                if trackcolor: xml_track.set('color', '#' + colors.rgb_float_to_hex(trackcolor))


                #print('[output-lmms]')

        xml_fxmixer = ET.SubElement(songX, "fxmixer")
        add_window_data(xml_fxmixer, 'main', 'fxmixer', [102,280], [543,333], True, False)
        lmms_encode_fxmixer(xml_fxmixer)

        XControllerRackView = ET.SubElement(songX, "ControllerRackView")
        add_window_data(XControllerRackView, 'main', 'controller_rack_view', [680,310], [350,200], False, False)
        Xpianoroll = ET.SubElement(songX, "pianoroll")
        add_window_data(Xpianoroll, 'main', 'piano_roll', [5,5], [970,480], False, False)
        Xautomationeditor = ET.SubElement(songX, "automationeditor")
        add_window_data(Xautomationeditor, 'main', 'automation_editor', [1,1], [860,400], False, False)

        song_name = convproj_obj.metadata.name
        outtxt = ''
        if convproj_obj.metadata.name: 
            outtxt += '"'+convproj_obj.metadata.name+'"'
            if convproj_obj.metadata.author: outtxt += ' by ' + convproj_obj.metadata.author
            outtxt += '<hr>'


        if convproj_obj.metadata.comment_text:
            notesX = ET.SubElement(songX, "projectnotes")
            add_window_data(notesX, 'main', 'project_notes', [728, 5], [389, 300], True, False)

            if convproj_obj.metadata.comment_datatype == 'html': 
                outtxt += convproj_obj.metadata.comment_text
            if convproj_obj.metadata.comment_datatype == 'text': 
                outtxt += convproj_obj.metadata.comment_text.replace('\n', '<br/>').replace('\r', '<br/>')

        notesX = ET.SubElement(songX, "projectnotes")
        notesX.text = ET.CDATA(outtxt)

        #print("[output-lmms] Number of Notes: " + str(notescount_forprinting))
        #print("[output-lmms] Number of Patterns: " + str(patternscount_forprinting))
        #print("[output-lmms] Number of Tracks: " + str(trackscount_forprinting))      

        timelineX = ET.SubElement(songX, "timeline")
        timelineX.set("lpstate", str(convproj_obj.loop_active))
        timelineX.set("lp0pos", str(convproj_obj.loop_start))
        timelineX.set("lp1pos", str(convproj_obj.loop_end))

        outfile = ET.ElementTree(projX)
        
        ET.indent(outfile)
        outfile.write(output_file, encoding='utf-8', xml_declaration = True)
