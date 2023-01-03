# SPDX-FileCopyrightText: 2022 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import base64
import json
import lxml.etree as ET
import math
import plugin_output
from functions import placements
from functions import note_mod

lfoshape = {'sine': 0,'tri': 1,'saw': 2,'square': 3,'custom': 4,'random': 5}
chord = {'0': 0, '0,4,7': 1, '0,4,6': 2, '0,3,7': 3, '0,3,6': 4, '0,2,7': 5, '0,5,7': 6, '0,4,8': 7, '0,5,8': 8, '0,3,6,9': 9, '0,4,7,9': 10, '0,5,7,9': 11, '0,4,7,9,14': 12, '0,3,7,9': 13, '0,3,7,9,14': 14, '0,4,7,10': 15, '0,5,7,10': 16, '0,4,8,10': 17, '0,4,6,10': 18, '0,4,7,10,15': 19, '0,4,7,10,13': 20, '0,4,8,10,15': 21, '0,4,8,10,13': 22, '0,4,6,10,13': 23, '0,4,7,10,17': 24, '0,4,7,10,21': 25, '0,4,7,10,18': 26, '0,4,7,11': 27, '0,4,6,11': 28, '0,4,8,11': 29, '0,4,7,11,18': 30, '0,4,7,11,21': 31, '0,3,7,10': 32, '0,3,6,10': 33, '0,3,7,10,13': 34, '0,3,7,10,17': 35, '0,3,7,10,21': 36, '0,3,7,11': 37, '0,3,7,11,17': 38, '0,3,7,11,21': 39, '0,4,7,10,14': 40, '0,5,7,10,14': 41, '0,4,7,14': 42, '0,4,8,10,14': 43, '0,4,6,10,14': 44, '0,4,7,10,14,18': 45, '0,4,7,10,14,20': 46, '0,4,7,11,14': 47, '0,5,7,11,15': 48, '0,4,8,11,14': 49, '0,4,7,11,14,18': 50, '0,3,7,10,14': 51, '0,3,7,14': 52, '0,3,6,10,14': 53, '0,3,7,11,14': 54, '0,4,7,10,14,17': 55, '0,4,7,10,13,17': 56, '0,4,7,11,14,17': 57, '0,3,7,10,14,17': 58, '0,3,7,11,14,17': 59, '0,4,7,10,14,21': 60, '0,4,7,10,15,21': 61, '0,4,7,10,13,21': 62, '0,4,6,10,13,21': 63, '0,4,7,11,14,21': 64, '0,3,7,10,14,21': 65, '0,3,7,11,14,21': 66, '0,2,4,5,7,9,11': 67, '0,2,3,5,7,8,11': 68, '0,2,3,5,7,9,11': 69, '0,2,4,6,8,10': 70, '0,2,3,5,6,8,9,11': 71, '0,2,4,7,9': 72, '0,3,5,7,10': 73, '0,1,5,7,10': 74, '0,2,4,5,7,8,9,11': 75, '0,2,4,5,7,9,10,11': 76, '0,3,5,6,7,10': 77, '0,1,4,5,7,8,11': 78, '0,1,4,6,8,10,11': 79, '0,1,3,5,7,9,11': 80, '0,1,3,5,7,8,11': 81, '0,2,3,6,7,8,11': 82, '0,2,3,5,7,9,10': 83, '0,1,3,5,7,8,10': 84, '0,2,4,6,7,9,11': 85, '0,2,4,5,7,9,10': 86, '0,2,3,5,7,8,10': 87, '0,1,3,5,6,8,10': 88, '0,1,2,3,4,5,6,7,8,9,10,11': 90, '0,1,3,4,6,7,9,10': 91, '0,7': 92, '0,1,4,5,7,8,10': 93, '0,1,4,5,6,8,11': 94}
arpdirection = {'up': 0,'down': 1,'updown': 2,'downup': 3,'random': 4}
filtertype = {'lowpass': 0 ,'hipass': 1 ,'bandpass_csg': 2 ,'bandpass_czpg': 3 ,'notch': 4 ,'allpass': 5 ,'moog': 6 ,'lowpass_double': 7 ,'lowpass_rc12': 8 ,'bandpass_rc12': 9 ,'Highpass_rc12': 10 ,'lowpass_rc24': 11 ,'bandpass_rc24': 12 ,'Highpass_rc24': 13 ,'formant': 14 ,'moog_double': 15 ,'lowpass_sv': 16 ,'bandpass_sv': 17 ,'Highpass_sv': 18 ,'notch_sv': 19 ,'formant_fast': 20 ,'tripole': 21}
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
    if 'plugin' in plugindata:
        if 'path' in plugindata['plugin']:
            xmldata.set('plugin', str(plugindata['plugin']['path']))
    if plugindata['datatype'] == 'raw':
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

def rgb_to_hex(rgb): return '%02x%02x%02x' % rgb
def onetime2lmmstime(input): return int(round(float(input * 12)))
def oneto100(input): return round(float(input) * 100)

# ------- Instruments and Plugins -------

def sec2exp(value): 
    #print(value, math.sqrt(value/5))
    return math.sqrt(value/5)
def asdrlfo_set(jsonpath, trkX_insttr):
    eldataX = ET.SubElement(trkX_insttr, "eldata")
    if 'filter' in jsonpath:
        json_filter = jsonpath['filter']
        if json_filter['type'] in filtertype:
            if 'cutoff' in json_filter: eldataX.set('fcut', str(json_filter['cutoff']))
            if 'wet' in json_filter: eldataX.set('fwet', str(json_filter['wet']))
            if 'type' in json_filter: eldataX.set('ftype', str(filtertype[json_filter['type']]))
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
                if 'amount' in elmodJenv: elmodX.set('amt', str(elmodJenv['amount']))
                if 'predelay' in elmodJenv: elmodX.set('pdel', str(sec2exp(elmodJenv['predelay'])))
                if 'attack' in elmodJenv: elmodX.set('att', str(sec2exp(elmodJenv['attack'])))
                if 'hold' in elmodJenv: elmodX.set('hold', str(sec2exp(elmodJenv['hold'])))
                if 'decay' in elmodJenv: elmodX.set('dec', str(sec2exp(elmodJenv['decay'])))
                if 'sustain' in elmodJenv: elmodX.set('sustain', str(elmodJenv['sustain']))
                if 'release' in elmodJenv: elmodX.set('rel', str(sec2exp(elmodJenv['release'])))
            if 'lfo' in elmodJ:
                elmodJlfo = elmodJ['lfo']
                if 'predelay' in elmodJenv:elmodX.set('lpdel', str(elmodJlfo['predelay']))
                if 'attack' in elmodJenv:elmodX.set('latt', str(elmodJlfo['attack']))
                if 'shape' in elmodJenv:elmodX.set('lshp', str(lfoshape[elmodJlfo['shape']]))
                elmodX.set('x100', '0')
                if 'speed' in elmodJenv:
                    lfospeed = float(elmodJlfo['speed']) / 20000
                    if lfospeed > 1:
                        elmodX.set('x100', '1')
                        lfospeed = lfospeed / 100
                    elmodX.set('lspd', str(lfospeed))
                if 'shape' in elmodJenv: elmodX.set('lshp', str(lfoshape[elmodJlfo['shape']]))

def lmms_encode_plugin(xmltag, trkJ):
    instJ = trkJ['instdata']
    pluginname = instJ['plugin']
    xml_instrumentpreplugin = ET.SubElement(xmltag, "instrument")
    if 'plugindata' in instJ:
        plugJ = instJ['plugindata']

    if pluginname == 'sampler':
        print('[output-lmms]       Plugin: sampler > AudioFileProcessor')
        asdrlfo_set(plugJ, xmltag)
        xml_instrumentpreplugin.set('name', "audiofileprocessor")
        xml_sampler = ET.SubElement(xml_instrumentpreplugin, "audiofileprocessor")
        if 'reversed' in plugJ: xml_sampler.set('reversed', str(plugJ['reverse']))
        if 'amp' in plugJ: xml_sampler.set('amp', str(oneto100(plugJ['amp'])))
        if 'continueacrossnotes' in plugJ: xml_sampler.set('stutter', str(plugJ['continueacrossnotes']))
        if 'file' in plugJ: xml_sampler.set('src', str(plugJ['file']))
        loopenabled = 0
        loopmode = "normal"
        if 'loop' in plugJ:
            trkJ_loop = plugJ['loop']
            if 'custompoints' in trkJ_loop:
                if 'end' in trkJ_loop['custompoints']:
                    xml_sampler.set('eframe', str(trkJ_loop['custompoints']['end']))
                if 'loop' in trkJ_loop['custompoints']:
                    xml_sampler.set('lframe', str(trkJ_loop['custompoints']['loop']))
                if 'start' in trkJ_loop['custompoints']:
                    xml_sampler.set('sframe', str(trkJ_loop['custompoints']['start']))
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
        xml_opl2.set('op1_a', str(plugJ['op1']['envelope']['attack']))
        xml_opl2.set('op1_d', str(plugJ['op1']['envelope']['decay']))
        xml_opl2.set('op1_r', str(plugJ['op1']['envelope']['release']))
        xml_opl2.set('op1_s', str(plugJ['op1']['envelope']['sustain']))
        xml_opl2.set('op1_mul', str(plugJ['op1']['freqmul']))
        xml_opl2.set('op1_ksr', str(plugJ['op1']['ksr']))
        xml_opl2.set('op1_lvl', str(plugJ['op1']['level']))
        xml_opl2.set('op1_perc', str(plugJ['op1']['perc_env']))
        xml_opl2.set('op1_scale', str(plugJ['op1']['scale']))
        xml_opl2.set('op1_trem', str(plugJ['op1']['tremolo']))
        xml_opl2.set('op1_vib', str(plugJ['op1']['vibrato']))
        xml_opl2.set('op1_waveform', str(plugJ['op1']['waveform']))
        xml_opl2.set('op2_a', str(plugJ['op2']['envelope']['attack']))
        xml_opl2.set('op2_d', str(plugJ['op2']['envelope']['decay']))
        xml_opl2.set('op2_r', str(plugJ['op2']['envelope']['release']))
        xml_opl2.set('op2_s', str(plugJ['op2']['envelope']['sustain']))
        xml_opl2.set('op2_mul', str(plugJ['op2']['freqmul']))
        xml_opl2.set('op2_ksr', str(plugJ['op2']['ksr']))
        xml_opl2.set('op2_lvl', str(plugJ['op2']['level']))
        xml_opl2.set('op2_perc', str(plugJ['op2']['perc_env']))
        xml_opl2.set('op2_scale', str(plugJ['op2']['scale']))
        xml_opl2.set('op2_trem', str(plugJ['op2']['tremolo']))
        xml_opl2.set('op2_vib', str(plugJ['op2']['vibrato']))
        xml_opl2.set('op2_waveform', str(plugJ['op2']['waveform']))
        xml_opl2.set('feedback', str(plugJ['feedback']))
        xml_opl2.set('fm', str(plugJ['fm']))
        xml_opl2.set('trem_depth', str(plugJ['tremolo_depth']))
        xml_opl2.set('vib_depth', str(plugJ['vibrato_depth']))
    elif pluginname == 'vst2':
        print('[output-lmms]       Plugin: vst2 > vestige')
        plugJ = instJ['plugindata']
        xml_instrumentpreplugin.set('name', "vestige")
        xml_vst = ET.SubElement(xml_instrumentpreplugin, "vestige")
        setvstparams(plugJ, xml_vst)
    elif pluginname == 'zynaddsubfx-lmms':
        print('[output-lmms]       Plugin: zynaddsubfx > zynaddsubfx')
        xml_instrumentpreplugin.set('name', "zynaddsubfx")
        xml_zynaddsubfx = ET.SubElement(xml_instrumentpreplugin, "zynaddsubfx")
        xml_zynaddsubfx.set('bandwidth', str(plugJ['bandwidth']))
        xml_zynaddsubfx.set('filterfreq', str(plugJ['filterfreq']))
        xml_zynaddsubfx.set('filterq', str(plugJ['filterq']))
        xml_zynaddsubfx.set('fmgain', str(plugJ['fmgain']))
        xml_zynaddsubfx.set('forwardmidicc', str(plugJ['forwardmidicc']))
        xml_zynaddsubfx.set('modifiedcontrollers', str(plugJ['modifiedcontrollers']))
        xml_zynaddsubfx.set('portamento', str(plugJ['portamento']))
        xml_zynaddsubfx.set('resbandwidth', str(plugJ['resbandwidth']))
        xml_zynaddsubfx.set('rescenterfreq', str(plugJ['rescenterfreq']))
        zdata = plugJ['data'].encode('ascii')
        zdataxs = ET.fromstring(base64.b64decode(zdata).decode('ascii'))
        xml_zynaddsubfx.append(zdataxs)
    elif pluginname == 'native-lmms':
        lmmsplugdata = plugJ['data']
        lmmsplugname = plugJ['name']
        xml_instrumentpreplugin.set('name', lmmsplugname)
        xml_lmmsnat = ET.SubElement(xml_instrumentpreplugin, lmmsplugname)
        asdrlfo_set(plugJ, xmltag)
        for lplugname in lmmsplugdata: xml_lmmsnat.set(lplugname, str(lmmsplugdata[lplugname]))
    else:
        print('[output-lmms]       Plugin: '+pluginname+' > None')
        xml_instrumentpreplugin.set('name', "audiofileprocessor")

# ------- Notelist -------

def lmms_encode_notelist(xmltag, json_notelist):
    printcountpat = 0
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
        printcountpat += 1
    print('['+str(printcountpat), end='] ')
def lmms_encode_inst_track(xmltag, trkJ):
    global trackscount_forprinting
    trackscount_forprinting += 1
    xmltag.set('type', "0")

    if 'solo' in trkJ: xmltag.set('solo', str(trkJ['solo']))
    else: xmltag.set('solo', '0')

    if 'enabled' in trkJ: xmltag.set('muted', str(int(not trkJ['enabled'])))
    else: xmltag.set('muted', '0')

    if 'name' in trkJ: xmltag.set('name', trkJ['name'])
    else: xmltag.set('name', 'untitled')

    if 'color' in trkJ: 
        color = trkJ['color']
        xmltag.set('color', '#' + rgb_to_hex((int(color[0]*255),int(color[1]*255),int(color[2]*255))))

    instJ = trkJ['instdata']

    #instrumenttrack
    trkX_insttr = ET.SubElement(xmltag, "instrumenttrack")
    trkX_insttr.set('usemasterpitch', "1")
    if 'usemasterpitch' in instJ: trkX_insttr.set('usemasterpitch', str(instJ['usemasterpitch']))
    trkX_insttr.set('pitch', "0")
    if 'pitch' in instJ: trkX_insttr.set('pitch', str(instJ['pitch']))
    if 'plugin' in instJ: instplugin = instJ['plugin']
    else: instplugin = None

    if 'fxrack_channel' in trkJ: trkX_insttr.set('fxch', str(trkJ['fxrack_channel']))
    else: trkX_insttr.set('fxch', '0')
    trkX_insttr.set('pan', "0")
    trkX_insttr.set('pitchrange', "12")
    trkX_insttr.set('vol', "100")
    if 'pan' in trkJ: trkX_insttr.set('pan', str(oneto100(trkJ['pan'])))
    if 'vol' in trkJ: trkX_insttr.set('vol', str(oneto100(trkJ['vol'])))
    if 'notefx' in instJ:
        instJ_notefx = instJ['notefx']
        if 'arpeggiator' in instJ_notefx:
            trkX_arpeggiator = ET.SubElement(trkX_insttr, "arpeggiator")
            json_arpeggiator = instJ_notefx['arpeggiator']
            trkX_arpeggiator.set('arpgate', str(json_arpeggiator['gate']))
            trkX_arpeggiator.set('arprange', str(json_arpeggiator['arprange']))
            trkX_arpeggiator.set('arp-enabled', str(json_arpeggiator['enabled']))
            trkX_arpeggiator.set('arpmode', str(json_arpeggiator['mode']))
            trkX_arpeggiator.set('arpdir', str(arpdirection[json_arpeggiator['direction']]))
            trkX_arpeggiator.set('arpskip', str(oneto100(json_arpeggiator['skiprate'])))
            arpvalue = json_arpeggiator['time']['value']
            arptype = json_arpeggiator['time']['type']
            if arptype == 'ms': trkX_arpeggiator.set('arptime', str(arpvalue))
            if arptype == 'step': trkX_arpeggiator.set('arptime', str((arpvalue*(1000*60/bpm))/4))
            trkX_arpeggiator.set('arpmiss', str(json_arpeggiator['miss']))
            trkX_arpeggiator.set('arpcycle', str(json_arpeggiator['cyclenotes']))
            if json_arpeggiator['chord'] in chord: trkX_arpeggiator.set('arp', str(chord[json_arpeggiator['chord']]))
            else: trkX_arpeggiator.set('arp', '0')
        if 'chordcreator' in instJ_notefx:
            trkX_chordcreator = ET.SubElement(trkX_insttr, "chordcreator")
            trkJ_chordcreator = instJ_notefx['chordcreator']
            trkX_chordcreator.set('chord-enabled', str(trkJ_chordcreator['enabled']))
            trkX_chordcreator.set('chordrange', str(trkJ_chordcreator['chordrange']))
            if trkJ_chordcreator['chord'] in chord: trkX_chordcreator.set('chord', str(chord[trkJ_chordcreator['chord']]))
            else: trkX_chordcreator.set('chord', '0')
        if 'pitch' in instJ_notefx:
            if 'semitones' in instJ_notefx['pitch']:
                middlenote = instJ_notefx['pitch']['semitones']
                if instplugin == 'sampler': middlenote += 3
                if instplugin == 'soundfont2': middlenote += 12
                trkX_insttr.set('basenote', str(middlenote+57))
            else: trkX_insttr.set('basenote', str(57))
        else: 
            if instplugin == 'sampler': trkX_insttr.set('basenote', str(60))
            elif instplugin == 'soundfont2': trkX_insttr.set('basenote', str(69))
            else: trkX_insttr.set('basenote', str(57))
    else: 
        if instplugin == 'sampler': trkX_insttr.set('basenote', str(60))
        elif instplugin == 'soundfont2': trkX_insttr.set('basenote', str(69))
        else: trkX_insttr.set('basenote', str(57))

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
    print('[output-lmms]       Name: ' + trkJ['name'])
    if 'fxchain' in trkJ:
        lmms_encode_fxchain(trkX_insttr, trkJ)
    lmms_encode_plugin(trkX_insttr, trkJ)

    #placements
    if 'placements' in trkJ:
        json_placementlist = trkJ['placements']
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
            patX.set('muted', "0")
            patX.set('steps', "16")
            patX.set('name', "")
            if 'cut' in json_placement: 
                if json_placement['cut']['type'] == 'cut': 
                    if 'start' in json_placement['cut']: cut_start = json_placement['cut']['start']
                    if 'end' in json_placement['cut']: cut_end = json_placement['cut']['end']
                    json_notelist = note_mod.trimmove(json_notelist, cut_start, cut_end)
            if 'name' in json_placement: patX.set('name', json_placement['name'])
            patX.set('type', "1")
            if 'color' in json_placement:
                color = json_placement['color']
                patX.set('color', '#' + rgb_to_hex((int(color[0]*255),int(color[1]*255),int(color[2]*255))))
            lmms_encode_notelist(patX, json_notelist)
            tracksnum += 1
        print(' ')

    print('[output-lmms]')

# ------- Effects -------

def lmms_encode_effectplugin(fxslotX, json_fxslot):
    fxplugname = json_fxslot['plugin']
    fxplugJ = json_fxslot['plugindata']
    if fxplugname == 'native-lmms':
        fxslotX.set('name', str(json_fxslot['plugindata']['name']))
        lmmsplugdata = fxplugJ['data']
        lmmsplugname = fxplugJ['name']
        print('['+lmmsplugname,end='] ')
        xml_name = fxlist[lmmsplugname]
        xml_lmmsnat = ET.SubElement(fxslotX, xml_name)
        for lplugname in lmmsplugdata: xml_lmmsnat.set(lplugname, str(lmmsplugdata[lplugname]))
    if fxplugname == 'vst2':
        fxslotX.set('name', 'vsteffect')
        print('[vst2',end='] ')
        xml_vst2 = ET.SubElement(fxslotX, 'vsteffectcontrols')
        setvstparams(fxplugJ, xml_vst2)
        xml_vst2key = ET.SubElement(fxslotX, 'key')
        xml_vst2keyatt = ET.SubElement(xml_vst2key, 'attribute')
        xml_vst2keyatt.set('value', xml_vst2.get('plugin'))
        xml_vst2keyatt.set('name', 'file')

def lmms_encode_effectslot(fxcX, json_fxslot):
    fxslotX = ET.SubElement(fxcX, "effect")
    if 'wet' in json_fxslot:
        wetvalue = json_fxslot['wet']
        if 'add_dry_minus_wet' in json_fxslot:
            if json_fxslot['add_dry_minus_wet'] == 1:
                wetvalue = -wetvalue
        fxslotX.set('wet', str(wetvalue))
    else: 
        fxslotX.set('wet', str(1))
    if 'enabled' in json_fxslot: fxslotX.set('on', str(json_fxslot['enabled']))
    else: fxslotX.set('on', str('1'))

    lmms_encode_effectplugin(fxslotX, json_fxslot)
    return fxslotX
def lmms_encode_fxchain(xmltag, json_fxchannel):
    if 'fxchain' in json_fxchannel:
        print('[output-lmms]       FX Chain: ',end='')
        fxcX = ET.SubElement(xmltag, "fxchain")
        json_fxchain = json_fxchannel['fxchain']
        if 'fxenabled' in json_fxchannel: fxcX.set('enabled', str(json_fxchannel['fxenabled']))
        else: fxcX.set('enabled', str('1'))
        fxcX.set('numofeffects', str(len(json_fxchannel['fxchain'])))
        for json_fxslot in json_fxchain:
            if json_fxslot['plugin'] == 'native-lmms' or 'vst2':
                fxslotX = lmms_encode_effectslot(fxcX, json_fxslot)
        print('')
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

        if 'color' in fxchannelJ:
            color = fxchannelJ['color']
            fxcX.set('color', '#' + rgb_to_hex((int(color[0]*255),int(color[1]*255),int(color[2]*255))))

        if 'vol' in fxchannelJ: volume = fxchannelJ['vol']
        else: volume = 1

        if 'muted' in fxchannelJ: muted = fxchannelJ['muted']
        else: muted = 0

        fxcX.set('name', name)
        fxcX.set('volume', str(volume))
        fxcX.set('muted', str(muted))
        lmms_encode_fxchain(fxcX, fxchannelJ)
        if 'sends' in fxchannelJ:
            sendsJ = fxchannelJ['sends']
            for json_send in sendsJ:
                sendX = ET.SubElement(fxcX, "send")
                sendX.set('channel', str(json_send['channel']))
                sendX.set('amount', str(json_send['amount']))
        else:
            sendX = ET.SubElement(fxcX, "send")
            sendX.set('channel', '0')
            sendX.set('amount', '1')
        print('[output-lmms]')

# ------- Automation -------

def auto_multiply(s_autopl_data, addval, mulval):
    for autopl in s_autopl_data:
        if 'points' in autopl:
            for point in autopl['points']:
                if 'value' in point:
                    point['value'] = (point['value']+addval)*mulval
    return s_autopl_data

def setvalue(tagJ, nameJ, xmltagX, nameX, fallbackval, addval, mulval, autodata):
    if nameJ in tagJ:
        if tagJ[nameJ] is not None:
            if nameX in autodata:
                t_ad = autodata[nameX]
                autovarX = ET.SubElement(xmltagX, nameX)
                if mulval != None and addval != None: autovarX.set('value', str((tagJ[nameJ]+addval)*mulval))
                else: autovarX.set('value', str(tagJ[nameJ]))
                autovarX.set('scale_type', 'linear')
                autovarX.set('id', str(t_ad))
            else:
                if mulval != None and addval != None: xmltagX.set('value', str((tagJ[nameJ]+addval)*mulval))
                else: xmltagX.set(nameX, str(tagJ[nameJ]))

def lmms_make_main_auto_track(xmltag, autodata, nameid, autoid):
    if nameid in nameid_cvpj_lmms_main:
        out_name = nameid_cvpj_lmms_main[nameid][1]
    else:
        out_name = 'unknown: '+nameid

    print('[output-lmms] Automation Track: '+out_name)

    if nameid == 'mastervol': autodata = auto_multiply(autodata, 0, 100)
    if nameid == 'masterpitch': autodata = auto_multiply(autodata, 0, 0.01)

    xml_autotrack = ET.SubElement(xmltag, "track")
    xml_autotrack.set('type', '5')
    xml_autotrack.set('solo', '0')
    xml_autotrack.set('muted', '0')
    xml_autotrack.set('name', out_name)
    for autoplacement in autodata:
        xml_automationpattern = ET.SubElement(xml_autotrack, "automationpattern")
        xml_automationpattern.set('pos', str(int(autoplacement['position']*12)))
        xml_automationpattern.set('len', str(int(autoplacement['duration']*12)))
        xml_automationpattern.set('tens', "1")
        xml_automationpattern.set('name', "")
        xml_automationpattern.set('mute', "0")
        xml_automationpattern.set('prog', "1")
        prevvalue = 0
        if 'points' in autoplacement:
            curpoint = 0
            for point in autoplacement['points']:
                if 'type' in point and curpoint != 0:
                    xml_time = ET.SubElement(xml_automationpattern, "time")
                    xml_time.set('value', str(prevvalue))
                    xml_time.set('pos', str(int(point['position']*12)-1))
                xml_time = ET.SubElement(xml_automationpattern, "time")
                xml_time.set('value', str(point['value']))
                xml_time.set('pos', str(int(point['position']*12)))
                prevvalue = point['value']
                curpoint += 1
        if autoid != None:
            xml_object = ET.SubElement(xml_automationpattern, "object")
            xml_object.set('id', str(autoid))

global nameid_cvpj_lmms
nameid_cvpj_lmms = {}
nameid_cvpj_lmms_main = {}
nameid_cvpj_lmms_main['bpm'] = ['bpm', "Tempo"]
nameid_cvpj_lmms_main['mastervol'] = ['mastervol', "Master Volume"]
nameid_cvpj_lmms_main['masterpitch'] = ['masterpitch', "Master Pitch"]

# ------- Main -------

def lmms_encode_tracks(xmltag, trksJ, trkorderJ):
    for trkeJ in trkorderJ:
        trkJ = trksJ[trkeJ]
        xml_track = ET.SubElement(xmltag, "track")
        if trkJ['type'] == "instrument": lmms_encode_inst_track(xml_track, trkJ)

class output_lmms(plugin_output.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'output'
    def getname(self): return 'LMMS'
    def getshortname(self): return 'lmms'
    def gettype(self): return 'f'
    def parse(self, convproj_json, output_file):
        print('[output-lmms] Output Start')

        projJ = json.loads(convproj_json)
        
        placements.removelanes(projJ)

        trksJ = projJ['trackdata']
        trkorderJ = projJ['trackordering']
        projX = ET.Element("lmms-project")
        projX.set('type', "song")
        projX.set('creator', "DawVert")
        projX.set('creatorversion', "1.2.2")
        projX.set('version', "1.0")
        headX = ET.SubElement(projX, "head")

        global auto_curnum

        main_auto_data = None
        main_auto_idnumdata = {}

        if 'placements_auto_main' in projJ: main_auto_data = projJ['placements_auto_main']

        songX = ET.SubElement(projX, "song")
        trkcX = ET.SubElement(songX, "trackcontainer")

        auto_curnum = 70000
        if main_auto_data != None:
            for autoname in main_auto_data:
                out_curnum = None
                if autoname in nameid_cvpj_lmms_main:
                    main_auto_idnumdata[nameid_cvpj_lmms_main[autoname][0]] = auto_curnum
                    out_curnum = auto_curnum
                lmms_make_main_auto_track(trkcX, main_auto_data[autoname], autoname, out_curnum)
                auto_curnum += 1

        setvalue(projJ, 'masterpitch', headX, 'masterpitch', 100, 0, 0.01, main_auto_idnumdata)
        setvalue(projJ, 'mastervol', headX, 'mastervol', 100, 0, 100, main_auto_idnumdata)
        setvalue(projJ, 'timesig_numerator', headX, 'timesig_numerator', 4, None, None, main_auto_idnumdata)
        setvalue(projJ, 'timesig_denominator', headX, 'timesig_denominator', 4, None, None, main_auto_idnumdata)
        setvalue(projJ, 'bpm', headX, 'bpm', 140, None, None, main_auto_idnumdata)
        
        lmms_encode_tracks(trkcX, trksJ, trkorderJ)
        
        if 'fxrack' in projJ:
            xml_fxmixer = ET.SubElement(songX, "fxmixer")
            json_fxrack = projJ['fxrack']
            lmms_encode_fxmixer(xml_fxmixer, json_fxrack)


        if 'message' in projJ:
            notesX = ET.SubElement(songX, "projectnotes")
            notesX.set("visible", "1")
            notesX.set("x", "728" )
            notesX.set("height", "300")
            notesX.set("y", "5" )
            notesX.set("width", "389")
            if 'type' in projJ['message']:
                if projJ['message']['type'] == 'html':
                    notesX.text = ET.CDATA(projJ['message']['text'])
                if projJ['message']['type'] == 'text':
                    notesX.text = ET.CDATA(projJ['message']['text'].replace('\n', '<br/>').replace('\r', '<br/>'))
        else:
            notesX = ET.SubElement(songX, "projectnotes")
            notesX.text = ET.CDATA("")

        print("[output-lmms] Number of Notes: " + str(notescount_forprinting))
        print("[output-lmms] Number of Patterns: " + str(patternscount_forprinting))
        print("[output-lmms] Number of Tracks: " + str(trackscount_forprinting))      

        trksJ = projJ['trackdata']
        
        
        outfile = ET.ElementTree(projX)
        
        ET.indent(outfile)
        outfile.write(output_file, encoding='utf-8', xml_declaration = True)
