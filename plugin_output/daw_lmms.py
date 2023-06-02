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
from functions import note_mod
from functions import notelist_data
from functions import song_convert
from functions import colors
from functions import tracks

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

patternscount_forprinting = 0
notescount_forprinting = 0
trackscount_forprinting = 0

# ------- functions -------

def setvstparams(plugindata, xmldata):
    if 'current_program' in plugindata: xmldata.set('program', str(plugindata['current_program']))
    if 'plugin' in plugindata:
        if 'path' in plugindata['plugin']:
            xmldata.set('plugin', str(plugindata['plugin']['path']))
    if 'datatype' in plugindata:
        if plugindata['datatype'] == 'chunk':
            xmldata.set('chunk', str(plugindata['data']))
        elif plugindata['datatype'] == 'param':
            numparams = plugindata['numparams']
            params = plugindata['params']
            xmldata.set('numparams', str(numparams))
            for param in range(numparams):
                paramdata = params[str(param)]
                pname = paramdata['name']
                pval = paramdata['value']
                xmldata.set('param'+str(param), str(param)+':'+pname+':'+str(pval))

def onetime2lmmstime(input): return int(round(float(input * 12)))

def oneto100(input): return round(float(input) * 100)

def sec2exp(value): return math.sqrt(value/5)

# ------- Instruments and Plugins -------

def asdrlfo_set(jsonpath, trkX_insttr):
    eldataX = ET.SubElement(trkX_insttr, "eldata")
    if 'filter' in jsonpath:
        json_filter = jsonpath['filter']
        if 'cutoff' in json_filter: eldataX.set('fcut', str(json_filter['cutoff']))
        filtertable_e = [None, None]
        lmms_filternum = None
        if 'type' in json_filter: filtertable_e[0] = json_filter['type']
        if 'subtype' in json_filter: filtertable_e[1] = json_filter['subtype']

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
        if 'wet' in json_filter: eldataX.set('fwet', str(json_filter['wet']))
        if 'reso' in json_filter: eldataX.set('fres', str(json_filter['reso']))

    asdrlfo(jsonpath, eldataX, 'volume', 'vol')
    asdrlfo(jsonpath, eldataX, 'cutoff', 'cut')
    asdrlfo(jsonpath, eldataX, 'reso', 'res')

def asdrlfo(jsonin, xmlobj, asdrtype, xmltype):
    if 'asdrlfo' in jsonin:
        jsondata = jsonin['asdrlfo']
        if asdrtype in jsondata:
            elmodX = ET.SubElement(xmlobj, 'el' + xmltype)
            elmodJ = jsondata[asdrtype]
            if 'envelope' in elmodJ:
                elmodJenv = elmodJ['envelope']
                if 'amount' in elmodJenv: 
                    if asdrtype == 'cutoff': elmodX.set('amt', str(elmodJenv['amount']/6000))
                    else: elmodX.set('amt', str(elmodJenv['amount']))
                if 'predelay' in elmodJenv: elmodX.set('pdel', str(sec2exp(elmodJenv['predelay'])))
                if 'attack' in elmodJenv: elmodX.set('att', str(sec2exp(elmodJenv['attack'])))
                if 'hold' in elmodJenv: elmodX.set('hold', str(sec2exp(elmodJenv['hold'])))
                if 'decay' in elmodJenv: elmodX.set('dec', str(sec2exp(elmodJenv['decay'])))
                if 'sustain' in elmodJenv: elmodX.set('sustain', str(elmodJenv['sustain']))
                if 'release' in elmodJenv: elmodX.set('rel', str(sec2exp(elmodJenv['release'])))
            if 'lfo' in elmodJ:
                elmodJlfo = elmodJ['lfo']
                if 'amount' in elmodJlfo: 
                    if asdrtype == 'cutoff': elmodX.set('lamt', str(elmodJlfo['amount']/1500))
                    else: elmodX.set('lamt', str(elmodJlfo['amount']))
                if 'predelay' in elmodJlfo: elmodX.set('lpdel', str(elmodJlfo['predelay']))
                if 'attack' in elmodJlfo: elmodX.set('latt', str(sec2exp(elmodJlfo['attack'])))
                if 'shape' in elmodJlfo: elmodX.set('lshp', str(lfoshape[elmodJlfo['shape']]))
                elmodX.set('x100', '0')
                if 'speed' in elmodJlfo:
                    if 'type' in elmodJlfo['speed']:
                        lfospeed = 1
                        if elmodJlfo['speed']['type'] == 'seconds':
                            lfospeed = float(elmodJlfo['speed']['time']) / 20
                        if lfospeed > 1:
                            elmodX.set('x100', '1')
                            lfospeed = lfospeed/100
                        elmodX.set('lspd', str(lfospeed))
                if 'shape' in elmodJlfo: elmodX.set('lshp', str(lfoshape[elmodJlfo['shape']]))

def lmms_encode_plugin(xmltag, trkJ, trackid, trackname):
    instJ = trkJ['instdata']
    xml_instrumentpreplugin = ET.SubElement(xmltag, "instrument")
    if 'plugin' in instJ: pluginname = instJ['plugin']
    else: pluginname = 'none'
    if 'plugindata' in instJ: plugJ = instJ['plugindata']

    pluginautoid = None
    if 'pluginautoid' in instJ: pluginautoid = ['plugin', instJ['pluginautoid']]

    if pluginname == 'sampler':
        print('[output-lmms]       Plugin: sampler > AudioFileProcessor')
        asdrlfo_set(plugJ, xmltag)
        xml_instrumentpreplugin.set('name', "audiofileprocessor")
        xml_sampler = ET.SubElement(xml_instrumentpreplugin, "audiofileprocessor")
        if 'reversed' in plugJ: xml_sampler.set('reversed', str(plugJ['reverse']))
        if 'amp' in plugJ: xml_sampler.set('amp', str(oneto100(plugJ['amp'])))
        if 'continueacrossnotes' in plugJ: xml_sampler.set('stutter', str(plugJ['continueacrossnotes']))
        if 'file' in plugJ: xml_sampler.set('src', str(plugJ['file']))

        point_value_type = 'samples'
        if 'point_value_type' in plugJ: point_value_type = plugJ['point_value_type']

        if point_value_type == 'samples' and 'length' in plugJ:
            trkJ_length = plugJ['length']
            if trkJ_length != 0:
                if 'start' in plugJ: xml_sampler.set('sframe', str(plugJ['start']/trkJ_length))
                else: xml_sampler.set('sframe', '0')
                if 'loop' in plugJ:
                    trkJ_loop = plugJ['loop']
                    if 'points' in trkJ_loop:
                        trkJ_loop_points = trkJ_loop['points']

                        start = trkJ_loop_points[0] / trkJ_length
                        end = trkJ_loop_points[1] / trkJ_length

                        if end == 0 or start == end:
                            end = 1.0

                        xml_sampler.set('lframe', str(start))
                        xml_sampler.set('eframe', str(end))

        if point_value_type == 'percent':
            if 'start' in plugJ: xml_sampler.set('sframe', str(plugJ['start']))
            else: xml_sampler.set('sframe', '0')
            if 'loop' in plugJ:
                trkJ_loop = plugJ['loop']
                if 'points' in trkJ_loop:
                    trkJ_loop_points = trkJ_loop['points']
                    xml_sampler.set('lframe', str(trkJ_loop_points[0]))
                    xml_sampler.set('eframe', str(trkJ_loop_points[1]))

        loopenabled = 0
        loopmode = "normal"

        if 'loop' in plugJ:
            trkJ_loop = plugJ['loop']
            if 'enabled' in trkJ_loop: loopenabled = trkJ_loop['enabled']
            if 'mode' in trkJ_loop: mode = trkJ_loop['mode']

        if loopenabled == 0: xml_sampler.set('looped', '0')
        if loopenabled == 1:
            if loopmode == "normal": xml_sampler.set('looped', '1')
            if loopmode == "pingpong": xml_sampler.set('looped', '2')
        interpolation = "none"
        if 'interpolation' in plugJ: interpolation = plugJ['interpolation']
        if interpolation == "none": xml_sampler.set('interp', '0')
        if interpolation == "linear": xml_sampler.set('interp', '1')
        if interpolation == "sinc": xml_sampler.set('interp', '2')
        else: xml_sampler.set('interp', '2')
    elif pluginname == 'soundfont2':
        print('[output-lmms]       Plugin: soundfont2 > sf2player')
        xml_instrumentpreplugin.set('name', "sf2player")
        xml_sf2 = ET.SubElement(xml_instrumentpreplugin, "sf2player")
        xml_sf2.set('bank', str(plugJ['bank']))
        if 'gain' in plugJ: xml_sf2.set('gain', str(plugJ['gain']))
        xml_sf2.set('patch', str(plugJ['patch']))
        xml_sf2.set('src', str(plugJ['file']))
        if 'reverb' in plugJ: 
            xml_sf2.set('reverbDamping', str(plugJ['reverb']['damping']))
            xml_sf2.set('reverbLevel', str(plugJ['reverb']['level']))
            xml_sf2.set('reverbOn', str(plugJ['reverb']['enabled']))
            xml_sf2.set('reverbRoomSize', str(plugJ['reverb']['roomsize']))
            xml_sf2.set('reverbWidth', str(plugJ['reverb']['width']))
        if 'chorus' in plugJ: 
            xml_sf2.set('chorusDepth', str(plugJ['chorus']['depth']))
            xml_sf2.set('chorusLevel', str(plugJ['chorus']['level']))
            xml_sf2.set('chorusNum', str(plugJ['chorus']['lines']))
            xml_sf2.set('chorusOn', str(plugJ['chorus']['enabled']))
            xml_sf2.set('chorusSpeed', str(plugJ['chorus']['speed']))
    elif pluginname == 'opl2':
        print('[output-lmms]       Plugin: OPL2 > OPL2')
        xml_instrumentpreplugin.set('name', "OPL2")
        xml_opl2 = ET.SubElement(xml_instrumentpreplugin, "OPL2")
        for opnum in range(2):
            opl2_optxt = 'op'+str(opnum+1)
            xml_opl2.set(opl2_optxt+'_a', str(int(plugJ[opl2_optxt]['env_attack'])))
            xml_opl2.set(opl2_optxt+'_d', str(int(plugJ[opl2_optxt]['env_decay'])))
            xml_opl2.set(opl2_optxt+'_r', str(int(plugJ[opl2_optxt]['env_release'])))
            xml_opl2.set(opl2_optxt+'_s', str(int(plugJ[opl2_optxt]['env_sustain'])))
            xml_opl2.set(opl2_optxt+'_mul', str(int(plugJ[opl2_optxt]['freqmul'])))
            xml_opl2.set(opl2_optxt+'_ksr', str(int(plugJ[opl2_optxt]['ksr'])))
            xml_opl2.set(opl2_optxt+'_lvl', str(int(plugJ[opl2_optxt]['level'])))
            xml_opl2.set(opl2_optxt+'_perc', str(int(plugJ[opl2_optxt]['perc_env'])))
            xml_opl2.set(opl2_optxt+'_scale', str(int(plugJ[opl2_optxt]['scale'])))
            xml_opl2.set(opl2_optxt+'_trem', str(int(plugJ[opl2_optxt]['tremolo'])))
            xml_opl2.set(opl2_optxt+'_vib', str(int(plugJ[opl2_optxt]['vibrato'])))
            xml_opl2.set(opl2_optxt+'_waveform', str(int(plugJ[opl2_optxt]['waveform'])))
        xml_opl2.set('feedback', str(int(plugJ['feedback'])))
        xml_opl2.set('fm', str(int(plugJ['fm'])))
        xml_opl2.set('trem_depth', str(int(plugJ['tremolo_depth'])))
        xml_opl2.set('vib_depth', str(int(plugJ['vibrato_depth'])))
    elif pluginname == 'vst2-dll':
        print('[output-lmms]       Plugin: vst2 > vestige')
        plugJ = instJ['plugindata']
        xml_instrumentpreplugin.set('name', "vestige")
        xml_vst = ET.SubElement(xml_instrumentpreplugin, "vestige")
        setvstparams(plugJ, xml_vst)

        if pluginautoid != None:
            autoidlist = tracks.autoid_out_getlist(pluginautoid)
            if autoidlist != None:
                for vstparam in autoidlist:
                    if vstparam.startswith('vst_param_'):
                        xmlparamname = 'param'+vstparam[10:]
                        add_auto_placements_noset(0, None, pluginautoid, vstparam, xml_vst, xmlparamname, 'VST', '#'+vstparam[10:])

    elif pluginname == 'zynaddsubfx-lmms':
        print('[output-lmms]       Plugin: zynaddsubfx > zynaddsubfx')
        xml_instrumentpreplugin.set('name', "zynaddsubfx")
        xml_zynaddsubfx = ET.SubElement(xml_instrumentpreplugin, "zynaddsubfx")

        add_auto_placements(0, None, pluginautoid, 'bandwidth', plugJ, 'bandwidth', xml_zynaddsubfx, 'bandwidth', 'Plugin', 'Bandwidth')
        add_auto_placements(0, None, pluginautoid, 'filterfreq', plugJ, 'filterfreq', xml_zynaddsubfx, 'filterfreq', 'Plugin', 'Filter Freq')
        add_auto_placements(0, None, pluginautoid, 'filterq', plugJ, 'filterq', xml_zynaddsubfx, 'filterq', 'Plugin', 'Filter Q')
        add_auto_placements(0, None, pluginautoid, 'fmgain', plugJ, 'fmgain', xml_zynaddsubfx, 'fmgain', 'Plugin', 'FM Gain')
        add_auto_placements(0, None, pluginautoid, 'forwardmidicc', plugJ, 'forwardmidicc', xml_zynaddsubfx, 'forwardmidicc', 'Plugin', 'Forward MIDI CC')
        add_auto_placements(0, None, pluginautoid, 'modifiedcontrollers', plugJ, 'modifiedcontrollers', xml_zynaddsubfx, 'modifiedcontrollers', 'Plugin', 'Modified Cont.')
        add_auto_placements(0, None, pluginautoid, 'portamento', plugJ, 'portamento', xml_zynaddsubfx, 'portamento', 'Plugin', 'Portamento')
        add_auto_placements(0, None, pluginautoid, 'resbandwidth', plugJ, 'resbandwidth', xml_zynaddsubfx, 'resbandwidth', 'Plugin', 'Res BandWidth')
        add_auto_placements(0, None, pluginautoid, 'rescenterfreq', plugJ, 'rescenterfreq', xml_zynaddsubfx, 'rescenterfreq', 'Plugin', 'Res Center Freq')
        zdata = plugJ['data'].encode('ascii')
        zdataxs = ET.fromstring(base64.b64decode(zdata).decode('ascii'))
        xml_zynaddsubfx.append(zdataxs)
    elif pluginname == 'native-lmms':
        lmmsplugdata = plugJ['data']
        lmmsplugname = plugJ['name']
        lmms_autovals = lmms_auto.get_params_inst(lmmsplugname)
        xml_instrumentpreplugin.set('name', lmmsplugname)
        xml_lmmsnat = ET.SubElement(xml_instrumentpreplugin, lmmsplugname)
        asdrlfo_set(plugJ, xmltag)
        for pluginparam in lmms_autovals[0]: 
            add_auto_placements(0, None, pluginautoid, pluginparam, lmmsplugdata, pluginparam, xml_lmmsnat, pluginparam, 'Plugin', pluginparam)
        for pluginparam in lmms_autovals[1]: 
            if pluginparam in lmmsplugdata: xml_lmmsnat.set(pluginparam, str(lmmsplugdata[pluginparam]))
    else:
        print('[output-lmms]       Plugin: '+pluginname+' > None')
        xml_instrumentpreplugin.set('name', "audiofileprocessor")
        if pluginautoid != None:
            autoidlist = tracks.autoid_out_getlist(pluginautoid)
            add_auto_unused(autoidlist, pluginautoid, trackname)

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
    add_auto_placements(0, None, ['track', trackid], 'pitch', instJ, 'pitch', trkX_insttr, 'pitch', trackname, 'Pitch')

    if 'chain_fx_notes' in trkJ:
        trkJ_notefx = trkJ['chain_fx_notes']
        for trkJ_notefxslot in trkJ_notefx:
            trkJ_plugindata = trkJ_notefxslot['plugindata']

            pluginautoid = None
            if 'pluginautoid' in trkJ_notefxslot: pluginautoid = ['plugin', trkJ_notefxslot['pluginautoid']]

            if trkJ_notefxslot['plugin'] == 'native-lmms':
                trkJ_nativelmms_name = trkJ_plugindata['name']
                trkJ_nativelmms_data = trkJ_plugindata['data']
                if trkJ_nativelmms_name == 'arpeggiator':
                    trkX_arpeggiator = ET.SubElement(trkX_insttr, "arpeggiator")
                    trkX_arpeggiator.set('arp-enabled', str(trkJ_notefxslot['enabled']))

                    lmms_autovals = lmms_auto.get_params_notefx('arpeggiator')
                    for pluginparam in lmms_autovals[0]: 
                        add_auto_placements(0, None, pluginautoid, pluginparam, trkJ_nativelmms_data, pluginparam, 
                            trkX_arpeggiator, pluginparam, 'FX Slot: Arpeggiator', pluginparam)

                if trkJ_nativelmms_name == 'chordcreator':
                    trkX_chordcreator = ET.SubElement(trkX_insttr, "chordcreator")
                    trkX_chordcreator.set('chord-enabled', str(trkJ_notefxslot['enabled']))

                    lmms_autovals = lmms_auto.get_params_notefx('chordcreator')
                    for pluginparam in lmms_autovals[0]: 
                        add_auto_placements(0, None, pluginautoid, pluginparam, trkJ_nativelmms_data, pluginparam, 
                            trkX_chordcreator, pluginparam, 'FX Slot: Chord Creator', pluginparam)



    middlenote = 0

    if 'middlenote' in instJ: middlenote = instJ['middlenote']

    if instplugin == 'sampler': middlenote += 3
    if instplugin == 'soundfont2': middlenote += 12
    trkX_insttr.set('basenote', str(middlenote+57))

    trkX_midiport = ET.SubElement(trkX_insttr, "midiport")
    if 'midi' in instJ:
        trkJ_midiport = instJ['midi']
        trkJ_m_i = trkJ_midiport['in']
        trkJ_m_o = trkJ_midiport['out']
        if 'enabled' in trkJ_m_i: trkX_midiport.set('readable', str(trkJ_m_i['enabled']))
        if 'fixedvelocity' in trkJ_m_i: trkX_midiport.set('fixedinputvelocity', str(trkJ_m_i['fixedvelocity']-1))
        if 'channel' in trkJ_m_i: trkX_midiport.set('inputchannel', str(trkJ_m_i['channel']))
        if 'enabled' in trkJ_m_o: trkX_midiport.set('writable', str(trkJ_m_o['enabled']))
        if 'fixedvelocity' in trkJ_m_o: trkX_midiport.set('fixedoutputvelocity', str(trkJ_m_o['fixedvelocity']-1))
        if 'channel' in trkJ_m_o: trkX_midiport.set('outputchannel', str(trkJ_m_o['channel']))
        if 'fixednote' in trkJ_m_o: trkX_midiport.set('fixedoutputnote', str(trkJ_m_o['fixednote']-1))
        if 'basevelocity' in trkJ_midiport: trkX_midiport.set('basevelocity', str(trkJ_midiport['basevelocity']))
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

    print('[output-lmms] Instrument Track')
    if 'name' in trkJ: print('[output-lmms]       Name: ' + trkJ['name'])
    if 'chain_fx_audio' in trkJ: lmms_encode_fxchain(trkX_insttr, trkJ)
    lmms_encode_plugin(trkX_insttr, trkJ, trackid, trackname)

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
                xml_sampletco.set('src', json_placement['file'])
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

def lmms_encode_effectplugin(fxslotX, json_fxslot):
    fxplugname = json_fxslot['plugin']
    fxplugJ = json_fxslot['plugindata']

    pluginautoid = None
    if 'pluginautoid' in json_fxslot: pluginautoid = ['plugin', json_fxslot['pluginautoid']]

    if fxplugname == 'native-lmms':
        fxslotX.set('name', str(json_fxslot['plugindata']['name']))
        lmmsplugdata = fxplugJ['data']
        lmmsplugname = fxplugJ['name']
        print('[output-lmms]       Audio FX: ['+lmmsplugname+'] ')
        lmms_autovals = lmms_auto.get_params_fx(lmmsplugname)
        xml_name = fxlist[lmmsplugname]
        xml_lmmsnat = ET.SubElement(fxslotX, xml_name)
        for pluginparam in lmms_autovals[0]: 
            add_auto_placements(0, None, pluginautoid, pluginparam, lmmsplugdata, pluginparam, xml_lmmsnat, pluginparam, 'FX Plug: '+lmmsplugname, pluginparam)
        for pluginparam in lmms_autovals[1]: 
            if pluginparam in lmmsplugdata: xml_lmmsnat.set(pluginparam, str(lmmsplugdata[pluginparam]))

    elif fxplugname == 'vst2-dll':
        fxslotX.set('name', 'vsteffect')
        print('[output-lmms]       Audio FX: [vst2] ')
        xml_vst2 = ET.SubElement(fxslotX, 'vsteffectcontrols')
        setvstparams(fxplugJ, xml_vst2)
        xml_vst2key = ET.SubElement(fxslotX, 'key')
        xml_vst2keyatt = ET.SubElement(xml_vst2key, 'attribute')
        xml_vst2keyatt.set('value', xml_vst2.get('plugin'))
        xml_vst2keyatt.set('name', 'file')

        if pluginautoid != None:
            autoidlist = tracks.autoid_out_getlist(pluginautoid)
            if autoidlist != None:
                for vstparam in autoidlist:
                    if vstparam.startswith('vst_param_'):
                        xmlparamname = 'param'+vstparam[10:]
                        add_auto_placements_noset(0, None, pluginautoid, vstparam, xml_vst2, xmlparamname, 'VST', '#'+vstparam[10:])

    elif fxplugname == 'ladspa':
        fxslotX.set('name', 'ladspaeffect')
        print('[output-lmms]       Audio FX: [ladspa] ')
        cvpj_plugindata = json_fxslot['plugindata']
        xml_ladspa = ET.SubElement(fxslotX, 'ladspacontrols')
        xml_ladspa_key = ET.SubElement(fxslotX, 'key')
        xml_ladspa_key_file = ET.SubElement(xml_ladspa_key, 'attribute')
        xml_ladspa_key_file.set('name', 'file')
        xml_ladspa_key_file.set('value', Path(cvpj_plugindata['path']).stem)
        xml_ladspa_key_plugin = ET.SubElement(xml_ladspa_key, 'attribute')
        xml_ladspa_key_plugin.set('name', 'plugin')
        xml_ladspa_key_plugin.set('value', str(cvpj_plugindata['plugin']))

        seperated_channels = False
        if 'seperated_channels' in cvpj_plugindata:
            if cvpj_plugindata['seperated_channels'] == True:
                seperated_channels = True

        cvpj_params = cvpj_plugindata['params']

        if seperated_channels == False:
            xml_ladspa.set('link', '1')
            for param in cvpj_params:
                xml_param = ET.SubElement(xml_ladspa, 'port0'+param)
                add_auto_placements(cvpj_params[param], None, pluginautoid, 'ladspa_param_0_'+param, param, 'ladspa_param_0_'+param, xml_param, 'data', 'LADSPA', '#'+param)
                xml_param.set('link', '1')
                xml_param = ET.SubElement(xml_ladspa, 'port1'+param)
                add_auto_placements(cvpj_params[param], None, pluginautoid, 'ladspa_param_1_'+param, param, 'ladspa_param_1_'+param, xml_param, 'data', 'LADSPA', '#'+param)
        else:
            xml_ladspa.set('link', '0')
            for param in cvpj_params['0']:
                xml_param = ET.SubElement(xml_ladspa, 'port0'+param)
                add_auto_placements(cvpj_params['0'][param], None, pluginautoid, 'ladspa_param_0_'+param, param, 'ladspa_param_0_'+param, xml_param, 'data', 'LADSPA', 'L #'+param)
                xml_param.set('link', '0')
            for param in cvpj_params['1']:
                xml_param = ET.SubElement(xml_ladspa, 'port1'+param)
                add_auto_placements(cvpj_params['1'][param], None, pluginautoid, 'ladspa_param_1_'+param, param, 'ladspa_param_1_'+param, xml_param, 'data', 'LADSPA', 'R #'+param)
 
    else:
        fxslotX.set('name', 'stereomatrix')
        xml_lmmsnat = ET.SubElement(fxslotX, 'stereomatrixcontrols')

        #if pluginautoid != None:
        #    autoidlist = tracks.autoid_out_getlist(pluginautoid)
        #    add_auto_unused(autoidlist, pluginautoid, 'FX Plug')


def lmms_encode_effectslot(fxcX, json_fxslot):

    fxslotX = ET.SubElement(fxcX, "effect")

    slotautoid = None
    if 'slotautoid' in json_fxslot: 
        slotautoid = ['slot', json_fxslot['slotautoid']]
    add_auto_placements(1, None, slotautoid, 'enabled', json_fxslot, 'enabled', fxslotX, 'on', 'Slot', 'On')
    add_auto_placements(1, None, slotautoid, 'wet', json_fxslot, 'wet', fxslotX, 'wet', 'Slot', 'Wet')

    lmms_encode_effectplugin(fxslotX, json_fxslot)
    return fxslotX

def lmms_encode_fxchain(xmltag, json_fxchannel):
    if 'chain_fx_audio' in json_fxchannel:
        fxcX = ET.SubElement(xmltag, "fxchain")
        json_fxchain = json_fxchannel['chain_fx_audio']
        if 'fxenabled' in json_fxchannel: fxcX.set('enabled', str(json_fxchannel['fxenabled']))
        else: fxcX.set('enabled', str('1'))
        fxcX.set('numofeffects', str(len(json_fxchannel['chain_fx_audio'])))
        for json_fxslot in json_fxchain:
            fxslotX = lmms_encode_effectslot(fxcX, json_fxslot)

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
    if j_name in j_tag: i_value = j_tag[j_name]
    else: i_value = i_fallback

    if i_addmul != None: i_value = (i_value+i_addmul[0])*i_addmul[1]

    if i_id != None and i_autoname != None: aid_id, aid_data = tracks.autoid_out_get(i_id+[i_autoname])
    else: aid_id, aid_data = None, None

    if aid_id != None and len(aid_data['placements']) != 0:
        if i_addmul != None: aid_data['placements'] = auto.multiply(aid_data['placements'], i_addmul[0], i_addmul[1])
        lmms_make_main_auto_track(aid_id, aid_data, v_type+': '+v_name)
        autovarX = ET.SubElement(x_tag, x_name)
        autovarX.set('value', str(i_value))
        autovarX.set('scale_type', 'linear')
        autovarX.set('id', str(aid_id))
    else:
        x_tag.set(x_name, str(i_value))

def add_auto_placements_noset(i_value, i_addmul, i_id, i_autoname, x_tag, x_name, v_type, v_name):
    if i_addmul != None: i_value = (i_value+i_addmul[0])*i_addmul[1]

    if i_id != None and i_autoname != None: aid_id, aid_data = tracks.autoid_out_get(i_id+[i_autoname])
    else: aid_id, aid_data = None, None

    if aid_id != None and len(aid_data['placements']) != 0:
        if i_addmul != None: aid_data['placements'] = auto.multiply(aid_data['placements'], i_addmul[0], i_addmul[1])
        lmms_make_main_auto_track(aid_id, aid_data, v_type+': '+v_name)
        if x_tag != None:
            autovarX = ET.SubElement(x_tag, x_name)
            autovarX.set('value', str(i_value))
            autovarX.set('scale_type', 'linear')
            autovarX.set('id', str(aid_id))

def add_auto_unused(i_ids, pluginautoid, i_name):
    #print(i_ids, i_name)
    if pluginautoid != None and i_ids != None:
        for i_id in i_ids:
            add_auto_placements_noset(0, None, pluginautoid, i_id, None, None, i_name, str(i_id))

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
        'track_nopl': False
        }
    def parse(self, convproj_json, output_file):
        global autoidnum
        global trkcX
        global projJ

        autoidnum = 340000
        print('[output-lmms] Output Start')

        projJ = json.loads(convproj_json)

        tracks.autoid_out_load(projJ)

        trksJ = projJ['track_data']
        trkorderJ = projJ['track_order']
        if 'track_placements' in projJ: trkplacementsJ = projJ['track_placements']
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

        add_auto_placements(120, None, ['main'], 'bpm', projJ, 'bpm', headX, 'bpm', 'Song', 'Tempo')
        add_auto_placements(0, None, ['main'], 'pitch', projJ, 'pitch', headX, 'masterpitch', 'Song', 'Pitch')
        add_auto_placements(1, [0, 100], ['main'], 'vol', projJ, 'vol', headX, 'mastervol', 'Song', 'Volume')
        add_auto_placements(4, None, ['main'], 'timesig_numerator', projJ, 'timesig_numerator', headX, 'timesig_numerator', 'Song', 'Numerator')
        add_auto_placements(4, None, ['main'], 'timesig_denominator', projJ, 'timesig_denominator', headX, 'timesig_denominator', 'Song', 'Denominator')

        lmms_encode_tracks(trkcX, trksJ, trkorderJ, trkplacementsJ)

        xml_fxmixer = ET.SubElement(songX, "fxmixer")
        if 'fxrack' in projJ:
            lmms_encode_fxmixer(xml_fxmixer, projJ['fxrack'])


        if 'info' in projJ:
            infoJ = projJ['info']
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

        trksJ = projJ['track_data']
        
        
        outfile = ET.ElementTree(projX)
        
        ET.indent(outfile)
        outfile.write(output_file, encoding='utf-8', xml_declaration = True)
