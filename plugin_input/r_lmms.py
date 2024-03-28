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
from functions_plugin_ext import plugin_vst2
from objects import manager_extplug
from objects import counter
from objects import dv_dataset
from objects import auto_id
from functions import colors

def get_sample(i_value):
    if i_value:
        if not os.path.exists(i_value):
            for t in [
            '/usr/share/lmms/samples/', 
            'C:\\Program Files\\LMMS\\data\\samples\\'
            ]:
                if os.path.exists(t+i_value): return t+i_value
            return i_value
        else:
            return i_value
    else:
        return ''

lfoshape = ['sine', 'tri', 'saw', 'square', 'custom', 'random']
arpdirection = ['up', 'down', 'updown', 'downup', 'random']

chordids = ["major","majb5","minor","minb5","sus2","sus4","aug","augsus4","tri","6","6sus4","6add9","m6","m6add9","7","7sus4","7#5","7b5","7#9","7b9","7#5#9","7#5b9","7b5b9","7add11","7add13","7#11","maj7","maj7b5","maj7#5","maj7#11","maj7add13","m7","m7b5","m7b9","m7add11","m7add13","m-maj7","m-maj7add11","m-maj7add13","9","9sus4","add9","9#5","9b5","9#11","9b13","maj9","maj9sus4","maj9#5","maj9#11","m9","madd9","m9b5","m9-maj7","11","11b9","maj11","m11","m-maj11","13","13#9","13b9","13b5b9","maj13","m13","m-maj13","full_major","harmonic_minor","melodic_minor","whole_tone","diminished","major_pentatonic","minor_pentatonic","jap_in_sen","major_bebop","dominant_bebop","blues","arabic","enigmatic","neopolitan","neopolitan_minor","hungarian_minor","dorian","phrygian","lydian","mixolydian","aeolian","locrian","full_minor","chromatic","half-whole_diminished","5","phrygian_dominant","persian"]

filtertype = [
['low_pass', None], ['high_pass', None], ['band_pass','csg'], 
['band_pass','czpg'], ['notch', None], ['all_pass', None], 
['moog', None], ['low_pass','double'], ['low_pass','rc12'], 
['band_pass','rc12'], ['high_pass','rc12'], ['low_pass','rc24'], 
['band_pass','rc24'], ['high_pass','rc24'], ['formant', None], 
['moog','double'], ['low_pass','sv'], ['band_pass','sv'], 
['high_pass','sv'], ['notch','sv'], ['formant','fast'], ['tripole', None]
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
fxlist['vectorscope'] = 'Vectorscope'

# ------- functions -------

def get_timedata(xmltag, x_name):
    syncmode = xmltag.get(x_name+'_syncmode')
    denominator = xmltag.get(x_name+'_denominator')
    numerator = xmltag.get(x_name+'_numerator')

    steps = None
    if syncmode == '1': steps = 16*8
    elif syncmode == '2': steps = 16
    elif syncmode == '3': steps = 8
    elif syncmode == '4': steps = 4
    elif syncmode == '5': steps = 2
    elif syncmode == '6': steps = 1
    elif syncmode == '7': steps = 0.5
    elif syncmode == '8': 
        if denominator and numerator: steps = (int(numerator)/int(denominator))*4

    return (steps != None), steps




send_auto_id_counter = counter.counter(1000, 'send_')

def add_window_data(xmltag, convproj_obj, w_group, w_name):
    window_x = xmltag.get('x')
    window_y = xmltag.get('y')
    window_visible = xmltag.get('visible')
    window_width = xmltag.get('width')
    window_height = xmltag.get('height')
    window_maximized = xmltag.get('maximized')

    windata_obj = convproj_obj.window_data_add([w_group,w_name])

    if window_x != None and window_y != None: 
        windata_obj.pos_x = int(window_x)
        windata_obj.pos_y = int(window_y)
    if window_width != None and window_height != None: 
        windata_obj.size_x = int(window_width)
        windata_obj.size_y = int(window_height)
    if window_visible != None: 
        windata_obj.open = int(window_visible)
    if window_maximized != None: 
        windata_obj.maximized = int(window_maximized)



def getvstparams(convproj_obj, plugin_obj, pluginid, xmldata):
    global autoid_assoc
    
    pluginpath = xmldata.get('plugin')

    plugin_obj.datavals.add('path', pluginpath)

    vst2_pathid = pluginid+'_vstpath'
    convproj_obj.add_fileref(vst2_pathid, pluginpath)
    plugin_obj.filerefs['plugin'] = vst2_pathid

    vst_numparams = xmldata.get('numparams')

    w_open = xmldata.get('guivisible')
    if w_open == None: w_open = False
    windata_obj = convproj_obj.window_data_add(['plugin', pluginid])
    windata_obj.open = bool(int(w_open))

    vst_program = xmldata.get('program')
    if vst_program != None: 
        plugin_obj.datavals.add('current_program', int(vst_program))

    vst_data = xmldata.get('chunk')
    if vst_data != None:
        plugin_obj.datavals.add('datatype', 'chunk')
        plugin_obj.rawdata_add_b64('chunk', vst_data)

    elif vst_numparams != None:
        plugin_obj.datavals.add('datatype', 'param')
        plugin_obj.datavals.add('numparams', int(vst_numparams))
        for param in range(int(vst_numparams)):
            paramdata = xmldata.get('param'+str(param)).split(':')
            paramnum = 'ext_param_'+str(param)
            param_obj = plugin_obj.params.add(paramnum, float(paramdata[-1]), 'float')
            param_obj.visual.name = paramdata[1]

    for node in xmldata:
        notetagtxt = node.tag
        if notetagtxt.startswith('param'):
            value = node.get('value')
            if value != None:
                autoid_assoc.define(str(node.get('id')), ['plugin', pluginid, 'ext_param_'+notetagtxt[5:]], 'float', None)

    pluginfo_obj = manager_extplug.vst2_get('path', pluginpath, 'win', [32, 64])

    if pluginfo_obj.out_exists:
        plugin_obj.datavals.add('name', pluginfo_obj.name)
        plugin_obj.datavals.add('fourid', int(pluginfo_obj.id))
        plugin_obj.datavals.add('version', vst_version)

def hundredto1(lmms_input): return float(lmms_input) * 0.01

def lmms_auto_getvalue(x_tag, x_name, i_fbv, i_type, i_addmul, i_loc):
    global autoid_assoc
    outval = i_fbv

    xmlval = None
    if x_tag.get(x_name) != None:
        xmlval = x_tag.get(x_name)
    elif x_tag.findall(x_name) != []: 
        realvaluetag = x_tag.findall(x_name)[0]
        xmlval = realvaluetag.get('value')
        if xmlval != None and i_loc: autoid_assoc.define(str(realvaluetag.get('id')), i_loc, i_type, i_addmul)
    
    if xmlval != None: outval = (float(xmlval)+i_addmul[0])*i_addmul[1] if i_addmul != None else float(xmlval)
    if i_type == 'float': outval = outval
    if i_type == 'int': outval = int(outval)
    if i_type == 'bool': outval = bool(int(outval))

    return outval

def lmms_getvalue(xmltag, xmlname, fallbackval): 
    xmlval = xmltag.get(xmlname)
    if xmlval == None: xmlval = fallbackval
    return xmlval

def dset_plugparams(pluginname, pluginid, xml_data, plugin_obj):
    paramlist = dataset.params_list('plugin', pluginname)
    if paramlist != None:
        for paramname in paramlist:
            paramlist = dataset.params_i_get('plugin', pluginname, paramname)
            pv_noauto,pv_type,pv_def,pv_min,pv_max,pv_name = paramlist
            if pv_noauto == False:
                plugval = lmms_auto_getvalue(xml_data, paramname, 0, pv_type, None, ['plugin', pluginid, paramname])
                param_obj = plugin_obj.params.add(paramname, plugval, pv_type)
                param_obj.visual.name = pv_name
            else:
                xml_pluginparam = xml_data.get(paramname)
                if xml_pluginparam: plugin_obj.datavals.add(paramname, xml_pluginparam)



# ------- Instruments and Plugins -------

def exp2sec(value): return (value*value)*5

def asdflfo_get(trkX_insttr, plugin_obj):
    elcX = trkX_insttr.findall('eldata')
    if len(elcX) != 0:
        eldataX = elcX[0]
        if eldataX.findall('elvol'): asdflfo(plugin_obj, eldataX.findall('elvol')[0], 'vol')
        if eldataX.findall('elcut'): asdflfo(plugin_obj, eldataX.findall('elcut')[0], 'cutoff')
        if eldataX.findall('elres'): asdflfo(plugin_obj, eldataX.findall('elres')[0], 'reso')

        if eldataX.get('ftype') != None: 
            plugin_obj.filter.on = bool(float(lmms_getvalue(eldataX, 'fwet', 0)))
            plugin_obj.filter.freq = float(lmms_getvalue(eldataX, 'fcut', 0))
            plugin_obj.filter.q = float(lmms_getvalue(eldataX, 'fres', 0))
            plugin_obj.filter.type, plugin_obj.filter.subtype = filtertype[int(eldataX.get('ftype'))]

def asdflfo(plugin_obj, xmlO, asdrtype):
    envelopeparams = {}

    asdr_predelay = exp2sec(float(lmms_getvalue(xmlO, 'pdel', 0)))
    asdr_attack = exp2sec(float(lmms_getvalue(xmlO, 'att', 0)))
    asdr_hold = exp2sec(float(lmms_getvalue(xmlO, 'hold', 0)))
    asdr_decay = exp2sec(float(lmms_getvalue(xmlO, 'dec', 0)))
    asdr_sustain = float(lmms_getvalue(xmlO, 'sustain', 1))
    asdr_release = exp2sec(float(lmms_getvalue(xmlO, 'rel', 0)))
    asdr_amount = float(lmms_getvalue(xmlO, 'amt', 0))
    if asdrtype == 'cutoff': asdr_amount *= 6000

    plugin_obj.env_asdr_add(asdrtype, asdr_predelay, asdr_attack, asdr_hold, asdr_decay, asdr_sustain, asdr_release, asdr_amount)

    lfoparams = {}

    speedx100 = xmlO.get('x100')
    speedx100 = int(speedx100) if speedx100 != None else 0

    lfo_predelay = float(lmms_getvalue(xmlO, 'pdel', 0))
    lfo_attack = exp2sec(float(lmms_getvalue(xmlO, 'latt', 0)))
    lfo_amount = float(lmms_getvalue(xmlO, 'lamt', 0))
    lfo_shape = lfoshape[int(lmms_getvalue(xmlO, 'lshape', 0))]
    if asdrtype == 'cutoff': lfo_amount *= 6000

    lfo_speed = 0
    if xmlO.get('lspd') != None: lfo_speed = float(xmlO.get('lspd'))
    lfo_speed = (lfo_speed*0.2) if speedx100 == 1 else (lfo_speed*20)

    lfo_obj = plugin_obj.lfo_add(asdrtype)
    lfo_obj.predelay = exp2sec(lfo_predelay*4)
    lfo_obj.attack = lfo_attack
    lfo_obj.shape = lfo_shape
    lfo_obj.time.set_seconds(lfo_speed)
    lfo_obj.amount = lfo_amount

def lmms_decodeplugin(convproj_obj, trkX_insttr):
    trkX_instrument = trkX_insttr.findall('instrument')[0]
    pluginname = trkX_instrument.get('name')

    out_color = None

    pluginid = ''

    xml_a_plugin = trkX_instrument.findall(pluginname)
    if len(xml_a_plugin) != 0: 
        xml_plugin = xml_a_plugin[0]

        if pluginname == "sf2player":
            plugin_obj, pluginid = convproj_obj.add_plugin_genid('soundfont2', None)
            plugin_obj.role = 'synth'
            plugin_obj.datavals.add('bank', int(xml_plugin.get('bank')))
            plugin_obj.datavals.add('patch', int(xml_plugin.get('patch')))
            sf2_path = xml_plugin.get('src')
            convproj_obj.add_fileref(sf2_path, sf2_path)
            plugin_obj.filerefs['file'] = sf2_path

            param_obj = plugin_obj.params.add('gain', float(xml_plugin.get('gain')), 'float')
            param_obj.visual.name = 'Gain'
            for cvpj_name, lmmsname in [['chorus_depth','chorusDepth'],['chorus_level','chorusLevel'],['chorus_lines','chorusNum'],['chorus_speed','chorusSpeed'],['reverb_damping','reverbDamping'],['reverb_level','reverbLevel'],['reverb_roomsize','reverbRoomSize'],['reverb_width','reverbWidth']]:
                plugin_obj.params.add(cvpj_name, float(xml_plugin.get(lmmsname)), 'float')
                param_obj.visual.name = lmmsname
            param_obj = plugin_obj.params.add('chorus_enabled', float(xml_plugin.get('chorusOn')), 'bool')
            param_obj.visual.name = 'chorusOn'
            param_obj = plugin_obj.params.add('reverb_enabled', float(xml_plugin.get('reverbOn')), 'bool')
            param_obj.visual.name = 'reverbOn'

        elif pluginname == "audiofileprocessor":
            filepath = get_sample(lmms_getvalue(xml_plugin, 'src', ''))
            plugin_obj, pluginid, sampleref_obj = convproj_obj.add_plugin_sampler_genid(filepath)
            plugin_obj.datavals.add('reverse', bool(int(lmms_getvalue(xml_plugin, 'reversed', 0))))
            plugin_obj.datavals.add('amp', float(lmms_getvalue(xml_plugin, 'amp', 1))/100)
            plugin_obj.datavals.add('continueacrossnotes', bool(int(lmms_getvalue(xml_plugin, 'stutter', 0))))
            plugin_obj.datavals.add('trigger', 'normal')
            plugin_obj.datavals.add('point_value_type', "percent")

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
            plugin_obj.datavals.add('loop', cvpj_loop)
            plugin_obj.datavals.add('end', float(lmms_getvalue(xml_plugin, 'eframe', 1)))
            plugin_obj.datavals.add('start', float(lmms_getvalue(xml_plugin, 'sframe', 0)))
            plugin_obj.datavals.add('point_value_type', "percent")

            lmms_interpolation = int(xml_plugin.get('interp'))
            if lmms_interpolation == 0: cvpj_interpolation = "none"
            if lmms_interpolation == 1: cvpj_interpolation = "linear"
            if lmms_interpolation == 2: cvpj_interpolation = "sinc"
            plugin_obj.datavals.add('interpolation', cvpj_interpolation)

            asdflfo_get(trkX_insttr, plugin_obj)


        #elif pluginname == "OPL2" or pluginname == "opulenz":
        #    plugin_obj, pluginid = convproj_obj.add_plugin_genid('fm', 'opl2')
        #    for lmms_opname, cvpj_opname in [['op1', 'mod'],['op2', 'car']]:
        #        for varname in opl2opvarnames:
        #            plugval = lmms_auto_getvalue(xml_plugin, lmms_opname+varname[0], 0, 'int', None, ['plugin', pluginid, cvpj_opname+varname[1]])
        #            convproj_obj.params.add(cvpj_opname+varname[1], plugval, 'int', lmms_opname+varname[1])
                
        #    for varname in opl2varnames:
        #        plugval = lmms_auto_getvalue(xml_plugin, varname[0], 0, 'int', None,  ['plugin', pluginid, varname[1]])
        #        convproj_obj.params.add(varname[1], plugval, 'int', varname[1])

        elif pluginname == "vestige":
            plugin_obj, pluginid = convproj_obj.add_plugin_genid('vst2', 'win')
            plugin_obj.role = 'synth'
            getvstparams(convproj_obj, plugin_obj, pluginid, xml_plugin)

        else:
            plugin_obj, pluginid = convproj_obj.add_plugin_genid('native-lmms', pluginname)
            plugin_obj.role = 'synth'
            dset_plugparams(pluginname, pluginid, xml_plugin, plugin_obj)
            asdflfo_get(trkX_insttr, plugin_obj)

            if pluginname == "vibedstrings":
                for num in range(9):
                    graphid = 'graph'+str(num)
                    vibegraph = xml_plugin.get(graphid)
                    if vibegraph:
                        vibegraph = base64.b64decode(vibegraph.encode('ascii'))
                        vibegraph_size = len(vibegraph)//4
                        wave_data = struct.unpack('f'*vibegraph_size, vibegraph)
                        wave_obj = plugin_obj.wave_add(graphid)
                        wave_obj.set_all_range(wave_data, 0, 1)
                        wave_obj.smooth = True

            if pluginname == "bitinvader":
                sampleshape = xml_plugin.get('sampleShape')
                sampleshape = base64.b64decode(sampleshape.encode('ascii'))
                sampleshape_size = len(sampleshape)//4
                wave_data = struct.unpack('f'*sampleshape_size, sampleshape)

                wave_obj = plugin_obj.wave_add('main')
                wave_obj.set_all_range(wave_data, -1, 1)
                wave_obj.smooth = False

                wave_obj = plugin_obj.wave_add('main_smooth')
                wave_obj.set_all_range(wave_data, -1, 1)
                wave_obj.smooth = True

                wavetable_obj = plugin_obj.wavetable_add('main')
                wavetable_obj.ids = ['main', 'main_smooth']
                wavetable_obj.locs = [0, 1]

                osc_data = plugin_obj.osc_add()
                osc_data.shape = 'custom_wave'
                osc_data.name_id = 'main'

            if pluginname == "sid":
                for num in range(3):
                    sid_waveform = plugin_obj.params.get('waveform'+str(num), 0).value
                    sid_pulsewidth = plugin_obj.params.get('pulsewidth'+str(num), 0).value
                    sid_coarse = plugin_obj.params.get('coarse'+str(num), 0).value
                    sid_attack = plugin_obj.params.get('attack'+str(num), 0).value
                    sid_decay = plugin_obj.params.get('decay'+str(num), 0).value
                    sid_sustain = plugin_obj.params.get('sustain'+str(num), 0).value
                    sid_release = plugin_obj.params.get('release'+str(num), 0).value
                    sid_attack = sid_att[int(sid_attack)]/1000
                    sid_decay = sid_decrel[int(sid_decay)]/1000
                    sid_sustain = sid_sustain/15
                    sid_release = sid_decrel[int(sid_release)]/1000
                    asdr_name = 'osc'+str(num)
                    plugin_obj.env_asdr_add(asdr_name, 0, sid_attack, 0, sid_decay, sid_sustain, sid_release, 1)

                    osc_data = plugin_obj.osc_add()
                    osc_data.shape = sid_wave[int(sid_waveform)]
                    osc_data.env['vol'] =  asdr_name
                    osc_data.params['pulse_width'] = int(sid_pulsewidth)/4095
                    osc_data.params['coarse'] = int(sid_coarse)
                    if num == 2: 
                        sid_voice3Off = plugin_obj.params.get('voice3Off', 0).value
                        osc_data.params['coarse'] = int(not int(sid_voice3Off))

            if pluginname == "zynaddsubfx":
                zdata = xml_plugin.findall('ZynAddSubFX-data')
                if zdata: 
                    xsdata = ET.tostring(zdata[0], encoding='utf-8')
                    plugin_obj.rawdata_add('data', xsdata)

            if pluginname == "tripleoscillator":
                for oscnum in range(1, 4):
                    out_str = 'userwavefile'+str(oscnum)
                    filepath = xml_plugin.get(out_str)
                    filepath = get_sample(filepath)
                    convproj_obj.add_sampleref(pluginid+'_'+out_str, filepath)
                    plugin_obj.samplerefs[out_str] = pluginid+'_'+out_str

    _, plugincolor = dataset.object_get_name_color('plugin', pluginname)

    return plugincolor, pluginname, pluginid

# ------- Notelist -------

def lmms_decode_nlpattern(notesX, cvpj_notelist):
    for noteX in notesX:
        cvpj_notelist.add_r(float(noteX.get('pos')), float(noteX.get('len')), int(noteX.get('key'))-60, hundredto1(noteX.get('vol')), {'pan': hundredto1(noteX.get('pan'))})
        noteX_auto = noteX.findall('automationpattern')
        if len(noteX_auto) != 0: 
            noteX_auto = noteX.findall('automationpattern')[0]
            if len(noteX_auto.findall('detuning')) != 0: 
                noteX_detuning = noteX_auto.findall('detuning')[0]
                if len(noteX_detuning.findall('time')) != 0: 
                    prognum = int(noteX_detuning.get('prog'))
                    for pointX in noteX_detuning.findall('time'):
                        autopoint_obj = cvpj_notelist.last_add_auto('pitch')
                        autopoint_obj.pos = pointX.get('pos')
                        autopoint_obj.value = float(pointX.get('value'))
                        autopoint_obj.type = 'instant' if prognum == 0 else 'normal'
    
def lmms_decode_nlplacements(trkX, track_obj):
    patsX = trkX.findall('pattern')
    for patX in patsX:
        placement_obj = track_obj.placements.add_notes()
        lmms_decode_nlpattern(patX.findall('note'), placement_obj.notelist)
        placement_obj.position = float(patX.get('pos'))
        placement_obj.duration = placement_obj.notelist.get_dur()
        if placement_obj.duration != 0: placement_obj.duration = (placement_obj.duration/192).__ceil__()*192
        else: placement_obj.duration = 16
        placement_obj.visual.name = patX.get('name')
        placement_obj.muted = bool(int(patX.get('muted')))

# ------- Track: Inst -------

def lmms_decode_inst_track(convproj_obj, trkX, trackid):
    #trkX_insttr
    trkX_insttr = trkX.findall('instrumenttrack')[0]
    plug_color, pluginname, instpluginid = lmms_decodeplugin(convproj_obj, trkX_insttr)
    track_color = trkX.get('color')
    if track_color == None: track_color = plug_color
    else: track_color = colors.hex_to_rgb_float(track_color)
    add_window_data(trkX, convproj_obj, 'plugin', instpluginid)

    cvpj_enabled = int(lmms_auto_getvalue(trkX, 'muted', 1, 'bool', [-1, -1], ['track', trackid, 'enabled']))
    cvpj_solo = int(lmms_auto_getvalue(trkX, 'solo', 1, 'bool', None, ['track', trackid, 'solo']))
    cvpj_pan = float(lmms_auto_getvalue(trkX_insttr, 'pan', 0, 'float', [0, 0.01], ['track', trackid, 'pan']))
    cvpj_vol = float(lmms_auto_getvalue(trkX_insttr, 'vol', 100, 'float', [0, 0.01], ['track', trackid, 'vol']))
    cvpj_pitch = float(lmms_auto_getvalue(trkX_insttr, 'pitch', 0, 'float', [0, 0.01], ['track', trackid, 'pitch']))
    
    track_obj = convproj_obj.add_track(trackid, 'instrument', 1, False)
    track_obj.visual.name = trkX.get('name')
    track_obj.visual.color = track_color
    track_obj.params.add('vol', cvpj_vol, 'float')
    track_obj.params.add('pan', cvpj_pan, 'float')
    track_obj.params.add('enabled', cvpj_enabled, 'bool')
    track_obj.params.add('solo', cvpj_solo, 'bool')
    track_obj.params.add('usemasterpitch', trkX_insttr.get('usemasterpitch'), 'bool')
    track_obj.params.add('pitch', cvpj_pitch, 'float')
    track_obj.inst_pluginid = instpluginid

    #midi
    xml_a_midiport = trkX_insttr.findall('midiport')
    if len(xml_a_midiport) != 0:
        midiportX = trkX_insttr.findall('midiport')[0]
        if midiportX.get('readable') != None: track_obj.midi.in_enabled = bool(int(midiportX.get('readable')))
        if midiportX.get('inputchannel') != None: track_obj.midi.in_chan = int(midiportX.get('inputchannel'))-1
        if midiportX.get('fixedinputvelocity') != None: track_obj.midi.in_fixedvelocity = int(midiportX.get('fixedinputvelocity'))
        if midiportX.get('writable') != None: track_obj.midi.out_enabled = int(midiportX.get('writable'))
        if midiportX.get('outputchannel') != None: track_obj.midi.out_chan = int(midiportX.get('outputchannel'))
        if midiportX.get('outputprogram') != None: track_obj.midi.out_patch = int(midiportX.get('outputprogram'))
        if midiportX.get('fixedoutputvelocity') != None: track_obj.midi.out_fixedvelocity = int(midiportX.get('fixedoutputvelocity'))
        if midiportX.get('fixedoutputnote') != None: track_obj.midi.out_fixednote = int(midiportX.get('fixedoutputnote'))
        if midiportX.get('basevelocity') != None: track_obj.midi.basevelocity = int(midiportX.get('basevelocity'))

    xml_a_fxchain = trkX_insttr.findall('fxchain')
    if len(xml_a_fxchain) != 0: 
        track_obj.fxslots_audio += lmms_decode_fxchain(convproj_obj, track_obj, xml_a_fxchain[0])

    xml_fxch = trkX_insttr.get('fxch')
    if xml_fxch != None: track_obj.fxrack_channel = int(xml_fxch)
    
    if 'basenote' in trkX_insttr.attrib:
        basenote = int(trkX_insttr.get('basenote'))-57
        noteoffset = 0
        if pluginname == 'audiofileprocessor': noteoffset = 3
        if pluginname == 'sf2player': noteoffset = 12
        if pluginname == 'OPL2': noteoffset = 24
        middlenote = basenote - noteoffset
        track_obj.datavals.add('middlenote', middlenote)

    xml_a_arpeggiator = trkX_insttr.findall('arpeggiator')
    if len(xml_a_arpeggiator) != 0:
        trkX_arpeggiator = xml_a_arpeggiator[0]

        nfx_plugin_obj, pluginid = convproj_obj.add_plugin_genid('universal', 'arpeggiator')
        nfx_plugin_obj.role = 'notefx'
        cvpj_l_arpeggiator_enabled = lmms_auto_getvalue(trkX_arpeggiator, 'arp-enabled', 0, 'bool', None, ['slot', pluginid, 'enabled'])
        #dset_plugparams('arpeggiator', pluginid, trkX_arpeggiator, nfx_plugin_obj)

        arp_arp = int(lmms_getvalue(trkX_arpeggiator, 'arp', 0))
        arp_arpcycle = float(lmms_getvalue(trkX_arpeggiator, 'arpcycle', 0))
        arp_arpdir = float(lmms_getvalue(trkX_arpeggiator, 'arpdir', 0))
        arp_arpgate = float(lmms_getvalue(trkX_arpeggiator, 'arpgate', 0))/100
        arp_arpmiss = float(lmms_getvalue(trkX_arpeggiator, 'arpmiss', 0))/100
        arp_arpmode = float(lmms_getvalue(trkX_arpeggiator, 'arpmode', 0))
        arp_arprange = float(lmms_getvalue(trkX_arpeggiator, 'arprange', 0))
        arp_arpskip = float(lmms_getvalue(trkX_arpeggiator, 'arpskip', 0))/100

        is_steps, timeval = get_timedata(trkX_arpeggiator, 'arptime')

        timing_obj = nfx_plugin_obj.timing_add('main')
        if is_steps: timing_obj.set_steps(timeval, convproj_obj)
        else: timing_obj.set_seconds(int(lmms_getvalue(trkX_arpeggiator, 'arptime', 1000))/1000)

        chord_obj = nfx_plugin_obj.chord_add('main')
        chord_obj.find_by_id(0, chordids[arp_arp])

        direction = ['up','down','up_down','up_down','random'][int(arp_arpdir)]
        nfx_plugin_obj.datavals.add('direction', direction)
        if arp_arpdir == 3: nfx_plugin_obj.datavals.add('direction_mode', 'reverse')
        nfx_plugin_obj.datavals.add('mode', ['free','sort','sync'][int(arp_arpmode)])
        nfx_plugin_obj.datavals.add('range', int(arp_arprange))
        nfx_plugin_obj.datavals.add('gate', arp_arpgate)
        nfx_plugin_obj.datavals.add('miss_rate', arp_arpmiss)
        nfx_plugin_obj.datavals.add('skip_rate', arp_arpskip)
        nfx_plugin_obj.datavals.add('cycle', int(arp_arpcycle))

        nfx_plugin_obj.fxdata_add(cvpj_l_arpeggiator_enabled, None)
        track_obj.fxslots_notes.append(pluginid)

    xml_a_chordcreator = trkX_insttr.findall('chordcreator')
    if len(xml_a_chordcreator) != 0:
        trkX_chordcreator = xml_a_chordcreator[0]

        nfx_plugin_obj, pluginid = convproj_obj.add_plugin_genid('universal', 'chord_creator')
        nfx_plugin_obj.role = 'notefx'
        cvpj_l_chordcreator_enabled = lmms_auto_getvalue(trkX_chordcreator, 'chord-enabled', 0, 'bool', None, ['slot', pluginid, 'enabled'])
        #dset_plugparams('chordcreator', pluginid, trkX_chordcreator, nfx_plugin_obj)

        stack_chord = int(lmms_getvalue(trkX_arpeggiator, 'chord', 0))
        stack_chordrange = int(lmms_getvalue(trkX_arpeggiator, 'chordrange', 0))

        chord_obj = nfx_plugin_obj.chord_add('main')
        chord_obj.find_by_id(0, chordids[stack_chord])
        nfx_plugin_obj.datavals.add('range', int(stack_chordrange))

        nfx_plugin_obj.fxdata_add(cvpj_l_chordcreator_enabled, None)
        track_obj.fxslots_notes.append(pluginid)

    lmms_decode_nlplacements(trkX, track_obj)


# ------- Audio Placements -------

def lmms_decode_audioplacements(convproj_obj, trkX, track_obj):
    for samplecX in trkX.findall('sampletco')+trkX.findall('sampleclip'):
        placement_obj = track_obj.placements.add_audio()
        placement_obj.position = float(samplecX.get('pos'))
        placement_obj.duration = float(samplecX.get('len'))
        placement_obj.muted = bool(int(samplecX.get('muted')))
        filepath = get_sample(samplecX.get('src'))
        convproj_obj.add_sampleref(filepath, filepath)
        placement_obj.sampleref = filepath
        placement_obj.stretch_method = 'rate_speed'
        if samplecX.get('off') != None:
            cut_start = float(samplecX.get('off'))*-1
            placement_obj.cut_type = 'cut'
            placement_obj.cut_data = {'start': cut_start}

# ------- Track: audio -------

def lmms_decode_audio_track(convproj_obj, trkX, trackid):
    trkX_audiotr = trkX.findall('sampletrack')[0]

    cvpj_enabled = int(lmms_auto_getvalue(trkX, 'muted', 1, 'bool', [-1, -1], ['track', trackid, 'enabled']))
    cvpj_solo = int(lmms_auto_getvalue(trkX, 'solo', 1, 'bool', None, ['track', trackid, 'solo']))
    cvpj_pan = float(lmms_auto_getvalue(trkX_audiotr, 'pan', 0, 'float', [0, 0.01], ['track', trackid, 'pan']))
    cvpj_vol = float(lmms_auto_getvalue(trkX_audiotr, 'vol', 100, 'float', [0, 0.01], ['track', trackid, 'vol']))

    track_obj = convproj_obj.add_track(trackid, 'audio', True, False)
    track_obj.visual.name = trkX.get('name')
    track_obj.params.add('vol', cvpj_vol, 'float')
    track_obj.params.add('pan', cvpj_pan, 'float')
    track_obj.params.add('enabled', cvpj_enabled, 'bool')
    track_obj.params.add('solo', cvpj_solo, 'bool')

    xml_fxch = trkX_audiotr.get('fxch')
    if xml_fxch != None: track_obj.fxrack_channel = int(xml_fxch)

    xml_a_fxchain = trkX_audiotr.findall('fxchain')
    if len(xml_a_fxchain) != 0: 
        #fx_enabled = lmms_auto_getvalue(fxchainX, 'enabled', True, 'bool', None, ['track', trackid, 'fx_enabled'])
        #track_obj.params.add('fx_enabled', bool(int(fx_enabled)), 'bool')
        track_obj.fxslots_audio += lmms_decode_fxchain(convproj_obj, track_obj, xml_a_fxchain[0])

    lmms_decode_audioplacements(convproj_obj, trkX, track_obj)

# ------- Track: Automation -------

def lmms_decode_autoplacements(convproj_obj, trkX):
    autoplacements = []
    autopatsX = trkX.findall('automationpattern')
    for autopatX in autopatsX:
        autoobjectX = autopatX.findall('object')
        if len(autoobjectX) != 0:
            internal_id = autoobjectX[0].get('id')
            autopl_obj = convproj_obj.automation.add_pl_points(['id', str(autoobjectX[0].get('id'))], 'float')
            autopl_obj.position = float(autopatX.get('pos'))
            autopl_obj.duration = float(autopatX.get('len'))
            for pointX in autopatX.findall('time'):
                autopoint_obj = autopl_obj.data.add_point()
                autopoint_obj.pos = int(pointX.get('pos'))
                autopoint_obj.value = float(pointX.get('value'))
                autopoint_obj.type = 'normal'

def lmms_decode_auto_track(convproj_obj, trkX):
    lmms_decode_autoplacements(convproj_obj, trkX)

# ------- Effects -------

def lmms_decode_effectslot(convproj_obj, fxslotX):
    fxpluginname = fxslotX.get('name')

    if fxpluginname == 'vsteffect':
        fxxml_plugin = fxslotX.findall(fxlist[fxpluginname])[0]
        plugin_obj, pluginid = convproj_obj.add_plugin_genid('vst2', 'win')
        plugin_obj.role = 'effect'
        getvstparams(convproj_obj, plugin_obj, pluginid, fxxml_plugin)

    elif fxpluginname == 'ladspaeffect':
        fxxml_plugin = fxslotX.findall('ladspacontrols')[0]
        #print('[ladspa',end='] ')
        fxxml_plugin_key = fxslotX.findall('key')[0]
        fxxml_plugin_ladspacontrols = fxslotX.findall('ladspacontrols')[0]

        plugin_obj, pluginid = convproj_obj.add_plugin_genid('ladspa', None)
        plugin_obj.role = 'effect'

        for attribute in fxxml_plugin_key.findall('attribute'):
            attval = attribute.get('value')
            attname = attribute.get('name')
            if attname == 'file':
                plugin_obj.datavals.add('name', attval)
                plugin_obj.datavals.add('path', attval)
            if attname == 'plugin': 
                plugin_obj.datavals.add('plugin', attval)

        ladspa_ports = int(fxxml_plugin_ladspacontrols.get('ports'))
        ladspa_linked = fxxml_plugin_ladspacontrols.get('link')
        seperated_channels = False

        if ladspa_linked != None: 
            ladspa_ports //= 2
            if ladspa_linked == "0": seperated_channels = True

        plugin_obj.datavals.add('numparams', ladspa_ports)

        for node in fxxml_plugin_ladspacontrols.iter():
            notetagtxt = node.tag
            if notetagtxt.startswith('port'):
                l_ch = notetagtxt[4]
                l_val = notetagtxt[5:]
                t_data = node.get('data')
                paramid = 'ext_param_'+l_val if l_ch == '0' else 'ext_param_'+l_val+'_'+l_ch
                paramval = float(lmms_auto_getvalue(node, 'data', '0', 'float', None, ['plugin', pluginid, paramid]))
                plugin_obj.params.add(paramid, paramval, 'float')
        plugin_obj.datavals.add('seperated_channels', seperated_channels)
        
    elif fxpluginname in fxlist:
        fxxml_plugin = fxslotX.findall(fxlist[fxpluginname])[0]
        if fxpluginname == 'delay':
            plugin_obj, pluginid = convproj_obj.add_plugin_genid('universal', 'delay')
            plugin_obj.role = 'effect'
            DelayTimeSamples = float(lmms_getvalue(fxxml_plugin, 'DelayTimeSamples', 1))
            FeebackAmount = float(lmms_getvalue(fxxml_plugin, 'FeebackAmount', 0.5))
            plugin_obj.datavals.add('c_fb', FeebackAmount)
            is_steps, timeval = get_timedata(fxxml_plugin, 'DelayTimeSamples')
            timing_obj = plugin_obj.timing_add('center')
            if is_steps: timing_obj.set_steps(timeval, convproj_obj)
            else: timing_obj.set_seconds(DelayTimeSamples)
        else:
            plugin_obj, pluginid = convproj_obj.add_plugin_genid('native-lmms', fxpluginname)
            plugin_obj.role = 'effect'
            dset_plugparams(fxpluginname, pluginid, fxxml_plugin, plugin_obj)

    fxenabled = lmms_auto_getvalue(fxslotX, 'on', 1, 'bool', None, ['slot', pluginid, 'enabled'])
    fxwet = lmms_auto_getvalue(fxslotX, 'wet', 1, 'float', None, ['slot', pluginid, 'wet'])
    plugin_obj.fxdata_add(fxenabled, fxwet)
    return pluginid

def lmms_decode_fxchain(convproj_obj, track_obj, fxchainX):
    #print('[input-lmms]       Audio FX Chain: ',end='')
    fxchain = []
    fxslotsX = fxchainX.findall('effect')
    for fxslotX in fxslotsX:
        fxslotJ = lmms_decode_effectslot(convproj_obj, fxslotX)
        if fxslotJ != None: fxchain.append(fxslotJ)
    #print('')
    return fxchain

def lmms_decode_fxmixer(convproj_obj, fxX):
    fxlist = {}
    for fxcX in fxX:
        fx_name = fxcX.get('name')
        fx_num = int(fxcX.get('num'))

        fxchannel_obj = convproj_obj.add_fxchan(fx_num)
        if fx_name: fxchannel_obj.visual.name = fx_name
        fxchannel_obj.params.add('vol', float(lmms_auto_getvalue(fxcX, 'volume', 1, 'float', None, ['fxmixer', str(fx_num), 'vol'])), 'float')

        fxc_enabled = True
        if fxcX.get('muted') != None: fxc_enabled = not int(fxcX.get('muted'))
        fxchannel_obj.params.add('enabled', fxc_enabled, 'bool')

        fxchainX = fxcX.find('fxchain')
        if fxchainX != None:
            fx_enabled = lmms_auto_getvalue(fxchainX, 'enabled', 1, 'bool', None, ['fxmixer', str(fx_num), 'fx_enabled'])
            fxchannel_obj.params.add('fx_enabled', bool(int(fx_enabled)), 'bool')
            fxchannel_obj.fxslots_audio += lmms_decode_fxchain(convproj_obj, fxchannel_obj, fxchainX)

        sendsxml = fxcX.findall('send')
        for sendxml in sendsxml:
            send_id = send_auto_id_counter.get_str()
            fx_to_num = int(sendxml.get('channel'))
            fx_amount = lmms_auto_getvalue(sendxml, 'amount', 1, 'float', None, ['send', send_id, 'amount'])
            fxchannel_obj.sends.add(fx_to_num, send_id, fx_amount)

    return fxlist

# ------- Main -------

def lmms_decode_tracks(convproj_obj, trksX):
    idtracknum = 0
    for trkX in trksX:
        idtracknum += 1
        tracktype = int(trkX.get('type'))
        if tracktype == 0: lmms_decode_inst_track(convproj_obj, trkX, 'LMMS_Inst_'+str(idtracknum))
        if tracktype == 2: lmms_decode_audio_track(convproj_obj, trkX, 'LMMS_Audio_'+str(idtracknum))
        if tracktype == 5: lmms_decode_auto_track(convproj_obj, trkX)

class input_lmms(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'lmms'
    def gettype(self): return 'r'
    def getdawinfo(self, dawinfo_obj): 
        dawinfo_obj.name = 'LMMS'
        dawinfo_obj.file_ext = 'mmp'
        dawinfo_obj.fxrack = True
        dawinfo_obj.fxrack_params = ['enabled','vol']
        dawinfo_obj.auto_types = ['pl_points']
        dawinfo_obj.plugin_included = ['sampler:single','vst2','fm:opl2','soundfont2','native-lmms','universal:arpeggiator','universal:chord_creator','universal:delay','ladspa']

    def supported_autodetect(self): return True
    def detect(self, input_file):
        try:
            root = get_xml_tree(input_file)
            if root.tag == "lmms-project": output = True
            else: output = False
        except ET.ParseError: output = False
        return output
    def parse(self, convproj_obj, input_file, dv_config):
        global dataset
        global autoid_assoc

        autoid_assoc = auto_id.convproj2autoid(48, False)

        dataset = dv_dataset.dataset('./data_dset/lmms.dset')

        convproj_obj.type = 'r'
        convproj_obj.set_timings(48, False)

        tree = get_xml_tree(input_file)
        headX = tree.findall('head')[0]
        songX = tree.findall('song')[0]
        trkscX = songX.findall('trackcontainer')
        if len(trkscX): add_window_data(trkscX[0], convproj_obj, 'main', 'tracklist')
        trksX = trkscX[0].findall('track')
        fxmixerX = songX.findall('fxmixer')
        if len(fxmixerX): 
            add_window_data(fxmixerX[0], convproj_obj, 'main', 'fxmixer')
            fxX = fxmixerX[0].findall('fxchannel')

        tlX = songX.find('timeline')

        cvpj_bpm = float(lmms_auto_getvalue(headX, 'bpm', 140, 'float', None, ['main', 'bpm']))
        cvpj_vol = float(lmms_auto_getvalue(headX, 'mastervol', 100, 'float', [0, 0.01], ['main', 'vol']))
        cvpj_pitch = float(lmms_auto_getvalue(headX, 'masterpitch', 0, 'float', None, ['main', 'pitch']))
        timesig_numerator = lmms_auto_getvalue(headX, 'timesig_numerator', 4, 'int', None, None)
        timesig_denominator = lmms_auto_getvalue(headX, 'timesig_denominator', 4, 'int', None, None)

        self.timesig = [timesig_numerator, timesig_denominator]
        convproj_obj.params.add('bpm', cvpj_bpm, 'float')
        convproj_obj.params.add('vol', cvpj_vol, 'float')
        convproj_obj.params.add('pitch', cvpj_pitch, 'float')

        projnotesX = songX.findall('projectnotes')

        lmms_decode_tracks(convproj_obj, trksX)
        if len(fxmixerX): lmms_decode_fxmixer(convproj_obj, fxX)

        autoid_assoc.output(convproj_obj)

        X_controllerrackview = songX.findall('ControllerRackView')
        if len(X_controllerrackview): add_window_data(X_controllerrackview[0], convproj_obj, 'main', 'controller_rack_view')

        X_pianoroll = songX.findall('pianoroll')
        if len(X_pianoroll): add_window_data(X_pianoroll[0], convproj_obj, 'main', 'piano_roll')

        X_automationeditor = songX.findall('automationeditor')
        if len(X_automationeditor): add_window_data(X_automationeditor[0], convproj_obj, 'main', 'automation_editor')

        if len(projnotesX): 
            convproj_obj.metadata.comment_text = projnotesX[0].text
            convproj_obj.metadata.comment_datatype = 'html'
            add_window_data(projnotesX[0], convproj_obj, 'main', 'project_notes')

        if len(X_pianoroll): add_window_data(X_pianoroll[0], convproj_obj, 'main', 'piano_roll')

        X_timeline = songX.findall('timeline')
        if len(X_timeline): 
            convproj_obj.loop_active = int(X_timeline[0].get('lpstate'))
            convproj_obj.loop_start = int(X_timeline[0].get('lp0pos'))
            convproj_obj.loop_end = int(X_timeline[0].get('lp1pos'))


def get_xml_tree(path):
    with open(path, 'rb') as file:
        try:
            file.seek(4)
            data = zlib.decompress(file.read())
            return ET.fromstring(data)

        except zlib.error:
            return ET.parse(path).getroot()