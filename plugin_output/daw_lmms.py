# SPDX-FileCopyrightText: 2022 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import base64
import json
import lxml.etree as ET
import math
import plugin_output

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

def rgb_to_hex(rgb): return '%02x%02x%02x' % rgb
def onetime2lmmstime(input): return int(round(float(input * 12)))
def oneto100(input): return round(float(input) * 100)

# ------- Instruments and Plugins -------

def sec2exp(value): return (value * value)*5
def asdflfo_set(jsonpath, trkX_insttr):
    eldataX = ET.SubElement(trkX_insttr, "eldata")
    if 'filter' in jsonpath:
        json_filter = jsonpath['filter']
        if json_filter['type'] in filtertype:
            eldataX.set('fcut', str(json_filter['cutoff']))
            eldataX.set('fwet', str(json_filter['wet']))
            eldataX.set('ftype', str(filtertype[json_filter['type']]))
            eldataX.set('fres', str(json_filter['reso']))

    asdflfo(jsonpath, eldataX, 'volume', 'vol')
    asdflfo(jsonpath, eldataX, 'cutoff', 'cut')
    asdflfo(jsonpath, eldataX, 'reso', 'res')
def asdflfo(jsonin, xmlobj, asdrtype, xmltype):
    if 'asdflfo' in jsonin:
        jsondata = jsonin['asdflfo']
        if asdrtype in jsondata:
            elmodX = ET.SubElement(xmlobj, 'el' + xmltype)
            elmodJ = jsondata[asdrtype]
            if 'envelope' in elmodJ:
                elmodJenv = elmodJ['envelope']
                elmodX.set('amt', str(elmodJenv['amount']))
                elmodX.set('pdel', str(sec2exp(elmodJenv['predelay'])))
                elmodX.set('att', str(sec2exp(elmodJenv['attack'])))
                elmodX.set('hold', str(sec2exp(elmodJenv['hold'])))
                elmodX.set('dec', str(sec2exp(elmodJenv['decay'])))
                elmodX.set('sustain', str(sec2exp(elmodJenv['sustain'])))
                elmodX.set('rel', str(sec2exp(elmodJenv['release'])))
            if 'lfo' in elmodJ:
                elmodJlfo = elmodJ['lfo']
                elmodX.set('lpdel', str(elmodJlfo['predelay']))
                elmodX.set('latt', str(elmodJlfo['attack']))
                elmodX.set('lshp', str(lfoshape[elmodJlfo['shape']]))
                elmodX.set('x100', '0')
                lfospeed = float(elmodJlfo['speed']) / 20000
                if lfospeed > 1:
                    elmodX.set('x100', '1')
                    lfospeed = lfospeed / 100
                elmodX.set('lspd', str(lfospeed))
                elmodX.set('lamt', str(elmodJlfo['amount']))
def lmms_encode_plugin(xmltag, trkJ):
    instJ = trkJ['instdata']
    pluginname = instJ['plugin']
    xml_instrumentpreplugin = ET.SubElement(xmltag, "instrument")
    if 'plugindata' in instJ:
        plugJ = instJ['plugindata']

    if pluginname == 'sampler':
        print('[output-lmms]       Plugin: sampler > AudioFileProcessor')
        asdflfo_set(plugJ, xmltag)
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
                xml_sampler.set('eframe', str(trkJ_loop['custompoints']['end']))
                xml_sampler.set('lframe', str(trkJ_loop['custompoints']['loop']))
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
        else: xml_sampler.set('interp', '0')
    elif pluginname == 'soundfont2':
        print('[output-lmms]       Plugin: soundfont2 > sf2player')
        xml_instrumentpreplugin.set('name', "sf2player")
        xml_sf2 = ET.SubElement(xml_instrumentpreplugin, "sf2player")
        xml_sf2.set('bank', str(plugJ['bank']))
        xml_sf2.set('gain', str(plugJ['gain']))
        xml_sf2.set('patch', str(plugJ['patch']))
        xml_sf2.set('src', str(plugJ['file']))
        xml_sf2.set('reverbDamping', str(plugJ['reverb']['damping']))
        xml_sf2.set('reverbLevel', str(plugJ['reverb']['level']))
        xml_sf2.set('reverbOn', str(plugJ['reverb']['enabled']))
        xml_sf2.set('reverbRoomSize', str(plugJ['reverb']['roomsize']))
        xml_sf2.set('reverbWidth', str(plugJ['reverb']['width']))
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
        xml_instrumentpreplugin.set('name', "vestige")
        xml_vst = ET.SubElement(xml_instrumentpreplugin, "vestige")
        if 'plugin' in plugJ:
            if 'path' in plugJ['plugin']:
                xml_vst.set('plugin', str(plugJ['plugin']['path']))
        if plugJ['datatype'] == 'raw':
            xml_vst.set('chunk', str(plugJ['data']))
        elif plugJ['datatype'] == 'param':
            numparams = plugJ['numparams']
            params = plugJ['params']
            xml_vst.set('numparams', str(numparams))
            for param in range(numparams):
                paramdata = params[str(param)]
                pname = paramdata['name']
                pval = paramdata['value']
                xml_vst.set('param'+str(param), str(param)+':'+pname+':'+str(pval))
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
        asdflfo_set(plugJ, xmltag)
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
    if 'middlenote' in instJ:
        middlenote = instJ['middlenote']
        if instplugin == 'sampler': middlenote += 3
        if instplugin == 'soundfont2':  middlenote += 12
        if 'middlenote' in instJ: trkX_insttr.set('basenote', str(middlenote+57))
    else:
        if instplugin == 'sampler': trkX_insttr.set('basenote', str(60))
        if instplugin == 'soundfont2': trkX_insttr.set('basenote', str(48))
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
            trkX_arpeggiator.set('arpskip', str(json_arpeggiator['skiprate']))
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

    if 'midi' in instJ:
        trkX_midiport = ET.SubElement(trkX_insttr, "midiport")
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

    print('[output-lmms] Instrument Track')
    print('[output-lmms]       Name: ' + trkJ['name'])
    if 'fxchain' in instJ:
        lmms_encode_fxchain(trkX_insttr, instJ)
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
        lmmsplugdata = fxplugJ['data']
        lmmsplugname = fxplugJ['name']
        print('['+lmmsplugname,end='] ')
        xml_name = fxlist[lmmsplugname]
        xml_lmmsnat = ET.SubElement(fxslotX, xml_name)
        for lplugname in lmmsplugdata: xml_lmmsnat.set(lplugname, str(lmmsplugdata[lplugname]))
def lmms_encode_effectslot(fxcX, json_fxslot):
    fxslotX = ET.SubElement(fxcX, "effect")
    fxslotX.set('name', str(json_fxslot['plugindata']['name']))
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
    print('[output-lmms]       FX Chain: ',end='')
    fxcX = ET.SubElement(xmltag, "fxchain")
    json_fxchain = json_fxchannel['fxchain']
    if 'enabled' in json_fxchannel: fxcX.set('enabled', str(json_fxchannel['enabled']))
    else: fxcX.set('enabled', str('1'))
    fxcX.set('numofeffects', str(len(json_fxchannel['fxchain'])))
    for json_fxslot in json_fxchain:
        if json_fxslot['plugin'] == 'native-lmms':
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

# ------- Main -------

def lmms_encode_tracks(xmltag, trksJ, trkorderJ):
    for trkeJ in trkorderJ:
        trkJ = trksJ[trkeJ]
        xml_track = ET.SubElement(xmltag, "track")
        if trkJ['type'] == "instrument": lmms_encode_inst_track(xml_track, trkJ)

class output_lmms(plugin_output.base):
    def __init__(self): pass
    def getname(self): return 'LMMS'
    def getshortname(self): return 'lmms'
    def gettype(self): return 'r'
    def parse(self, convproj_json, output_file):
        print('[output-lmms] Output Start')
        projJ = json.loads(convproj_json)
        
        trksJ = projJ['trackdata']
        trkorderJ = projJ['trackordering']
        projX = ET.Element("lmms-project")
        projX.set('type', "song")
        projX.set('creator', "DawVert")
        projX.set('creatorversion', "1.2.2")
        projX.set('version', "1.0")
        headX = ET.SubElement(projX, "head")
        if 'masterpitch' in projJ: headX.set('masterpitch', str(int(projJ['masterpitch']/100)))
        else: headX.set('masterpitch', "0")

        if 'mastervol' in projJ: 
            if projJ['mastervol'] is not None:
                headX.set('mastervol', str(oneto100(projJ['mastervol'])))
        else: headX.set('mastervol', '100')

        if 'timesig_numerator' in projJ: 
            if projJ['timesig_numerator'] is not None:
                headX.set('timesig_numerator', str(projJ['timesig_numerator']))
        else: headX.set('timesig_numerator', '4')

        if 'timesig_denominator' in projJ: 
            if projJ['timesig_denominator'] is not None:
                headX.set('timesig_denominator', str(projJ['timesig_denominator']))
        else: headX.set('timesig_denominator', '4')

        global bpm
        if 'bpm' in projJ: 
            if projJ['bpm'] is not None:
                headX.set('bpm', str(projJ['bpm']))
                bpm = projJ['bpm']
        else: bpm = 140
        
        songX = ET.SubElement(projX, "song")
        trkcX = ET.SubElement(songX, "trackcontainer")
        
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
            print(projJ['message']['type'])
            if 'type' in projJ['message']:
                if projJ['message']['type'] == 'html':
                    notesX.text = ET.CDATA(projJ['message']['text'])
                if projJ['message']['type'] == 'text':
                    notesX.text = ET.CDATA(projJ['message']['text'].replace('\n', '<br/>'))

        print("[output-lmms] Number of Notes: " + str(notescount_forprinting))
        print("[output-lmms] Number of Patterns: " + str(patternscount_forprinting))
        print("[output-lmms] Number of Tracks: " + str(trackscount_forprinting))      

        trksJ = projJ['trackdata']
        
        outfile = ET.ElementTree(projX)
        
        ET.indent(outfile)
        outfile.write(output_file, encoding='utf-8')
