# SPDX-FileCopyrightText: 2022 Colby Ray
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_input
import xml.etree.ElementTree as ET
import json

def midiparseports(inputtxt):
    if inputtxt != None :
        splitted = inputtxt.split(',')
        outtable = []
        for splittedtext in splitted:
            splittedportentry = splittedtext.split(" ", 1)
            splittedports = splittedportentry[0].split(":", 1)
            splittednames = splittedportentry[1].split(":", 1)
            entryjson = {}
            entryjson['devicenum'] = int(splittedports[0])
            entryjson['portnum'] = int(splittedports[1])
            entryjson['devicename'] = splittednames[0]
            entryjson['portname'] = splittednames[1]
            outtable.append(entryjson)
        return outtable
    else:
        return []

def hundredto1(input):
    return float(input) * 0.01

def lmms_getvalue(defualt, jsonvar, xmltag, xmlname, json_name):
    jsonvar[json_name] = defualt
    if xmltag.get(xmlname) != None:
        jsonvar[json_name] = float(xmltag.get(xmlname))
    if xmltag.findall(xmlname):
        realvalue = xmltag.findall(xmlname)[0]
        jsonvar[json_name] = realvalue.get('value')

def lmms_decode_pattern(notesX):
    notelist = []
    print('Notes:', end=' ')
    printcountpat = 0
    for noteX in notesX:
        noteJ = {}
        noteJ['key'] = int(noteX.get('key')) - 48
        noteJ['position'] = float(noteX.get('pos')) / 48
        noteJ['pan'] = hundredto1(noteX.get('pan'))
        noteJ['duration'] = float(noteX.get('len')) / 48
        noteJ['vol'] = hundredto1(noteX.get('vol'))
        printcountpat += 1
        print(str(printcountpat), end=' ')
        notelist.append(noteJ)
    print(' ')
    return notelist

def lmms_decode_nlplacements(trkX):
    nlplacements = []
    patsX = trkX.findall('pattern')
    printcountplace = 0
    for patX in patsX:
        print('[input-lmms] └──── Placement ' + str(printcountplace+1) + ': ', end='')
        printcountplace += 1
        placeJ = {}
        placeJ["position"] = float(patX.get('pos')) / 48
        notesX = patX.findall('note')
        notesJ = lmms_decode_pattern(notesX)
        placeJ["notelist"] = notesJ
        placeJ["duration"] = note_list_getduration(notesJ)
        nlplacements.append(placeJ)
    return nlplacements

def note_list_getduration(notelistjsontable):
    notelistdurationfinal = 0
    for x in notelistjsontable:
        notelistduration = x['position'] + x['duration']
        if notelistduration > notelistdurationfinal:
            notelistdurationfinal = notelistduration
    return notelistdurationfinal

def asdflfo(trkJ, xmlO, type):
    trkJ['mod.' + type] = {}
    trkJ['mod.' + type]['envelope'] = {}
    trkJ['mod.' + type]['envelope']['predelay'] = float(xmlO.get('pdel'))
    trkJ['mod.' + type]['envelope']['attack'] = float(xmlO.get('att'))
    trkJ['mod.' + type]['envelope']['hold'] = float(xmlO.get('hold'))
    trkJ['mod.' + type]['envelope']['decay'] = float(xmlO.get('dec'))
    trkJ['mod.' + type]['envelope']['sustain'] = float(xmlO.get('sustain'))
    trkJ['mod.' + type]['envelope']['release'] = float(xmlO.get('rel'))
    trkJ['mod.' + type]['envelope']['amount'] = float(xmlO.get('amt'))
    speedx100 = float(xmlO.get('x100')) * 100
    trkJ['mod.' + type]['lfo'] = {}
    trkJ['mod.' + type]['lfo']['predelay'] = float(xmlO.get('lpdel'))
    trkJ['mod.' + type]['lfo']['attack'] = float(xmlO.get('latt'))
    trkJ['mod.' + type]['lfo']['speed'] = float((float(xmlO.get('lspd')) * 20000) * speedx100)
    trkJ['mod.' + type]['lfo']['amount'] = float(xmlO.get('lamt'))

def lmms_decodeplugin(trkX_insttr, plugJ, instJ):
    instJ['plugin'] = "none"
    trkX_instrument = trkX_insttr.findall('instrument')[0]
    pluginname = trkX_instrument.get('name')
    plugX = trkX_instrument.findall(pluginname)[0]
    if pluginname == "sf2player":
        instJ['plugin'] = "soundfont2"
        plugJ['bank'] = int(plugX.get('bank'))
        plugJ['patch'] = int(plugX.get('patch'))
        plugJ['file'] = plugX.get('src')
        plugJ['gain'] = float(plugX.get('gain'))
        plugJ['reverb'] = {}
        plugJ['chorus'] = {}
        plugJ['chorus']['depth'] = float(plugX.get('chorusDepth'))
        plugJ['chorus']['level'] = float(plugX.get('chorusLevel'))
        plugJ['chorus']['lines'] = float(plugX.get('chorusNum'))
        plugJ['chorus']['enabled'] = float(plugX.get('chorusOn'))
        plugJ['chorus']['speed'] = float(plugX.get('chorusSpeed'))
        plugJ['reverb']['damping'] = float(plugX.get('reverbDamping'))
        plugJ['reverb']['level'] = float(plugX.get('reverbLevel'))
        plugJ['reverb']['enabled'] = float(plugX.get('reverbOn'))
        plugJ['reverb']['roomsize'] = float(plugX.get('reverbRoomSize'))
        plugJ['reverb']['width'] = float(plugX.get('reverbWidth'))

    if pluginname == "audiofileprocessor":
        instJ['plugin'] = "sampler"
        plugJ['reverse'] = int(plugX.get('reversed'))
        plugJ['amp'] = hundredto1(float(plugX.get('amp')))
        plugJ['continueacrossnotes'] = int(plugX.get('stutter'))
        plugJ['file'] = plugX.get('src')
        plugJ['loop'] = {}
        plugJ['loop']['points'] = {}
        plugJ['loop']['points']['end'] = float(plugX.get('eframe'))
        plugJ['loop']['points']['loop'] = float(plugX.get('lframe'))
        plugJ['loop']['points']['start'] = float(plugX.get('sframe'))
        looped = int(plugX.get('looped'))
        if looped == 0:
            plugJ['loop']['enabled'] = 0
        if looped == 1:
            plugJ['loop']['enabled'] = 1
            plugJ['loop']['mode'] = "normal"
        if looped == 2:
            plugJ['loop']['enabled'] = 1
            plugJ['loop']['mode'] = "pingpong"
        interpolation = int(plugX.get('interp'))
        if interpolation == 0:
            plugJ['interpolation'] = "none"
        if interpolation == 1:
            plugJ['interpolation'] = "linear"
        if interpolation == 2:
            plugJ['interpolation'] = "sinc"


def lmms_decode_inst_track(trkX):
    trkJ = {}
    trkJ['type'] = "instrument"
    instJ = {}
    plugindata_json = {}
    trkJ['instrumentdata'] = instJ
    trkJ['placements'] = {}
    trkJ['name'] = trkX.get('name')
    print('[input-lmms] Instrument Track Name: ' + trkJ['name'])
    trkJ['enabled'] = int(not int(trkX.get('muted')))
    color = trkX.get('color')
    if color != None:
        color = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        print(color)
        trkJ['color'] = [color[0]/255,color[1]/255,color[2]/255]
    trkJ_inst = trkJ['instrumentdata']
    trkJ_inst['plugindata'] = plugindata_json
    trkX_insttr = trkX.findall('instrumenttrack')[0]
    trkJ['fxrack_channel'] = int(trkX_insttr.get('fxch'))
    trkJ['pan'] = hundredto1(trkX_insttr.get('pan'))
    trkJ['vol'] = hundredto1(trkX_insttr.get('vol'))
    #midiportX

    midiJ = {}
    midi_outJ = {}
    midi_inJ = {}
    
    midiportX = trkX_insttr.findall('midiport')[0]
    
    midi_inJ['enabled'] = midiportX.get('readable')
    midi_inJ['ports'] = midiparseports(midiportX.get('inports'))
    if midiportX.get('inputchannel') != '0':
        midi_inJ['channel'] = int(midiportX.get('inputchannel'))
    if midiportX.get('fixedinputvelocity') != '-1':
        midi_inJ['fixedvelocity'] = int(midiportX.get('fixedinputvelocity'))+1

    midi_outJ['enabled'] = midiportX.get('writable')
    midi_outJ['ports'] = midiparseports(midiportX.get('outports'))
    midi_outJ['channel'] = int(midiportX.get('outputchannel'))
    midi_outJ['program'] = midiportX.get('outputprogram')
    if midiportX.get('fixedoutputvelocity') != '-1':
        midi_outJ['fixedvelocity'] = int(midiportX.get('fixedoutputvelocity'))+1
    if midiportX.get('fixedoutputnote') != '-1':
        midi_outJ['fixednote'] = int(midiportX.get('fixedoutputnote'))+1

    midiJ['basevelocity'] = midiportX.get('basevelocity')
    
    midiJ['out'] = midi_outJ
    midiJ['in'] = midi_inJ

    trkJ['midi'] = midiJ

    #eldataX
    eldataX = trkX_insttr.findall('eldata')[0]
    if eldataX.findall('elvol'):
        realvalue = eldataX.findall('elvol')[0]
        asdflfo(trkJ_inst, realvalue, 'volume')
    if eldataX.findall('elcut'):
        realvalue = eldataX.findall('elcut')[0]
        asdflfo(trkJ_inst, realvalue, 'cutoff')
    if eldataX.findall('elres'):
        realvalue = eldataX.findall('elres')[0]
        asdflfo(trkJ_inst, realvalue, 'reso')
    trkJ_inst['filter'] = {}
    trkJ_inst['filter']['cutoff'] = float(eldataX.get('fcut'))
    trkJ_inst['filter']['wet'] = float(eldataX.get('fwet'))
    trkJ_inst['filter']['type'] = float(eldataX.get('ftype'))
    trkJ_inst['filter']['reso'] = float(eldataX.get('fres'))
    trkJ_inst['usemasterpitch'] = int(trkX_insttr.get('usemasterpitch'))
    
    trkJ_inst['pitch'] = 0
    if trkX_insttr.get('pitch') != None:
        trkJ_inst['pitch'] = float(trkX_insttr.get('pitch'))
    basenote = int(trkX_insttr.get('basenote'))-48
    trkJ_inst['basenote'] = int(basenote)
    trkX_chordcreator = trkX_insttr.findall('chordcreator')[0]
    trkJ_inst['chordcreator'] = {}
    trkJ_inst['chordcreator']['enabled'] = int(trkX_chordcreator.get('chord-enabled'))
    trkJ_inst['chordcreator']['chordrange'] = int(trkX_chordcreator.get('chordrange'))
    trkJ_inst['chordcreator']['chord'] = int(trkX_chordcreator.get('chord'))
    trkX_arpeggiator = trkX_insttr.findall('arpeggiator')[0]
    trkJ_inst['arpeggiator'] = {}
    trkJ_inst['arpeggiator']['gate'] = int(trkX_arpeggiator.get('arpgate'))
    trkJ_inst['arpeggiator']['arprange'] = int(trkX_arpeggiator.get('arprange'))
    trkJ_inst['arpeggiator']['enabled'] = int(trkX_arpeggiator.get('arp-enabled'))
    trkJ_inst['arpeggiator']['mode'] = int(trkX_arpeggiator.get('arpmode'))
    trkJ_inst['arpeggiator']['direction'] = int(trkX_arpeggiator.get('arpdir'))
    trkJ_inst['arpeggiator']['skiprate'] = int(trkX_arpeggiator.get('arpskip')) #percent
    trkJ_inst['arpeggiator']['time'] = int(trkX_arpeggiator.get('arptime')) #ms
    trkJ_inst['arpeggiator']['missrate'] = int(trkX_arpeggiator.get('arpmiss')) #percent
    trkJ_inst['arpeggiator']['cyclenotes'] = int(trkX_arpeggiator.get('arpcycle'))
    trkJ_inst['arpeggiator']['chord'] = int(trkX_arpeggiator.get('arp'))
    trkJ['placements'] = lmms_decode_nlplacements(trkX)
    trkJ_plugindata = trkJ_inst['plugindata']
    lmms_decodeplugin(trkX_insttr, trkJ_plugindata, instJ)
    return trkJ

def lmms_decode_audioplacements(trkX):
    audioplacements = []
    patsX = trkX.findall('sampletco')
    printcountplace = 0
    print('[input-lmms] └──── Placements:', end=' ')
    for patX in patsX:
        printcountplace += 1
        print(str(printcountplace), end=' ')
        audioplacementsjson = {}
        audioplacementsjson['position'] = float(patX.get('pos')) / 48
        audioplacementsjson['duration'] = (int(patX.get('len'))/bpm)*(1.25)
        audioplacementsjson['file'] = patX.get('src')
        audioplacements.append(audioplacementsjson)
    print('')
    return audioplacements

def lmms_decode_audio_track(trkX):
    trkJ = {}
    trkJ['type'] = "audio"
    trkJ['name'] = trkX.get('name')
    trkJ['enabled'] = int(not int(trkX.get('muted')))
    print('[input-lmms] Audio Track Name: ' + trkJ['name'])
    trkX_insttr = trkX.findall('sampletrack')[0]
    trkJ['pan'] = hundredto1(trkX_insttr.get('pan'))
    trkJ['vol'] = hundredto1(trkX_insttr.get('vol'))
    trkJ['placements'] = lmms_decode_audioplacements(trkX)
    return trkJ

def lmms_decode_tracks(trksX):
    tracklist = []
    for trkX in trksX:
        tracktype = trkX.get('type')
        if tracktype == "0":
            tracklist.append(lmms_decode_inst_track(trkX))
        if tracktype == "2":
            tracklist.append(lmms_decode_audio_track(trkX))
    return tracklist

def lmms_decode_fx(fxcX):
    fxchain = []
    fxchainxml = fxcX.get('fxchain')
    
    
    output = {}
    return output

def lmms_decode_fxmixer(fxX):
    fxlist = []
    for fxcX in fxX:
        fxcJ = {}
        fxcJ['name'] = fxcX.get('name')
        fxcJ['muted'] = int(fxcX.get('muted'))
        fxcJ['num'] = int(fxcX.get('num'))
        fxcJ['vol'] = float(fxcX.get('volume'))
        fxcJ['fxchain'] = lmms_decode_fx(fxcX)
        sendlist = []
        sendsxml = fxcX.findall('send')
        for sendxml in sendsxml:
            sendentryjson = {}
            sendentryjson['channel'] = sendxml.get('channel')
            sendentryjson['amount'] = sendxml.get('amount')
            sendlist.append(sendentryjson)
        fxcJ['sends'] = sendlist
        fxlist.append(fxcJ)
    return fxlist


class input_lmms(plugin_input.base):
    def __init__(self):
        pass

    def getname(self):
        return 'LMMS'

    def detect(self, input_file):
        output = False
        try:
            tree = ET.parse(input_file)
            root = tree.getroot()
            if root.tag == "lmms-project":
                output = True
        except ET.ParseError:
            output = False
        return output

    def parse(self, input_file, extra_param):
        tree = ET.parse(input_file).getroot()
        headX = tree.findall('head')[0]
        trksX = tree.findall('song/trackcontainer/track')
        fxX = tree.findall('song/fxmixer/fxchannel')
        tlX = tree.find('song/timeline')
        
        bpm = 140
        if headX.get('bpm') != None:
            bpm = int(headX.get('bpm'))
        
        loop = {}
        loop['enabled'] = int(tlX.get('lpstate'))
        loop['start'] = int(tlX.get('lp0pos'))/192
        loop['end'] = int(tlX.get('lp1pos'))/192
        
        rootJ = {}
        rootJ['mastervol'] = float(hundredto1(headX.get('mastervol')))
        rootJ['masterpitch'] = float(hundredto1(headX.get('masterpitch')))
        lmms_getvalue(4, rootJ, headX, 'timesig_numerator', 'timesig_numerator')
        lmms_getvalue(4, rootJ, headX, 'timesig_denominator', 'timesig_denominator')
        lmms_getvalue(140, rootJ, headX, 'bpm', 'bpm')
        rootJ['loop'] = loop
        rootJ['tracks'] = lmms_decode_tracks(trksX)
        rootJ['fxrack'] = lmms_decode_fxmixer(fxX)
        rootJ['cvpjtype'] = 'single'
        return json.dumps(rootJ, indent=2)
