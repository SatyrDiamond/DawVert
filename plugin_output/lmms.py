# SPDX-FileCopyrightText: 2022 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_output
import lxml.etree as ET
from functions import song
import json

patternscount_forprinting = 0
notescount_forprinting = 0
trackscount_forprinting = 0

def midiparseports(inputtable):
    if inputtable != [] :
        outputtxt = ''
        for portentry in inputtable:
            outputtxt += str(portentry['devicenum'])+':'+str(portentry['portnum'])+' '+str(portentry['devicename'])+':'+str(portentry['portname'])+','
        return outputtxt
    else:
        return ""

def rgb_to_hex(rgb):
    return '%02x%02x%02x' % rgb

def onetime2lmmstime(input):
    return int(round(float(input * 48)))

def oneto100(input):
    return round(float(input) * 100)

def lmms_encode_notelist(xmltag, json_notelist):
    print('Notes:', end=' ')
    printcountpat = 0
    for json_note in json_notelist:
        global notescount_forprinting
        notescount_forprinting += 1
        patX = ET.SubElement(xmltag, "note")
        key = json_note['key'] + 60
        position = int(round(float(json_note['position']) * 48))
        pan = 0
        if 'pan' in json_note:
            pan = oneto100(json_note['pan'])
        duration = int(round(float(json_note['duration']) * 48))
        if 'vol' in json_note:
            vol = oneto100(json_note['vol'])
        else:
            vol = 100
        patX.set('key', str(key))
        patX.set('pos', str(int(round(position))))
        patX.set('pan', str(pan))
        patX.set('len', str(int(round(duration))))
        patX.set('vol', str(vol))
        printcountpat += 1
        print(str(printcountpat), end=' ')
    print(' ')

def lmms_encode_plugin(xmltag, trkJ):
    pluginname = trkJ['instrumentdata']['plugin']
    xml_instrumentpreplugin = ET.SubElement(xmltag, "instrument")
    if pluginname == 'soundfont2':
        xml_instrumentpreplugin.set('name', "sf2player")
        xml_sf2 = ET.SubElement(xml_instrumentpreplugin, "sf2player")
        xml_sf2.set('bank', str(trkJ['instrumentdata']['plugindata']['bank']))
        xml_sf2.set('gain', str(trkJ['instrumentdata']['plugindata']['gain']))
        xml_sf2.set('patch', str(trkJ['instrumentdata']['plugindata']['patch']))
        xml_sf2.set('src', str(trkJ['instrumentdata']['plugindata']['file']))
        xml_sf2.set('reverbDamping', str(trkJ['instrumentdata']['plugindata']['reverb']['damping']))
        xml_sf2.set('reverbLevel', str(trkJ['instrumentdata']['plugindata']['reverb']['level']))
        xml_sf2.set('reverbOn', str(trkJ['instrumentdata']['plugindata']['reverb']['enabled']))
        xml_sf2.set('reverbRoomSize', str(trkJ['instrumentdata']['plugindata']['reverb']['roomsize']))
        xml_sf2.set('reverbWidth', str(trkJ['instrumentdata']['plugindata']['reverb']['width']))
        xml_sf2.set('chorusDepth', str(trkJ['instrumentdata']['plugindata']['chorus']['depth']))
        xml_sf2.set('chorusLevel', str(trkJ['instrumentdata']['plugindata']['chorus']['level']))
        xml_sf2.set('chorusNum', str(trkJ['instrumentdata']['plugindata']['chorus']['lines']))
        xml_sf2.set('chorusOn', str(trkJ['instrumentdata']['plugindata']['chorus']['enabled']))
        xml_sf2.set('chorusSpeed', str(trkJ['instrumentdata']['plugindata']['chorus']['speed']))
    if pluginname == 'sampler':
        xml_instrumentpreplugin.set('name', "audiofileprocessor")
        xml_sampler = ET.SubElement(xml_instrumentpreplugin, "audiofileprocessor")
        if 'reversed' in trkJ['instrumentdata']['plugindata']:
            xml_sampler.set('reversed', str(trkJ['instrumentdata']['plugindata']['reverse']))
        if 'amp' in trkJ['instrumentdata']['plugindata']:
            xml_sampler.set('amp', str(oneto100(trkJ['instrumentdata']['plugindata']['amp'])))
        if 'continueacrossnotes' in trkJ['instrumentdata']['plugindata']:
            xml_sampler.set('stutter', str(trkJ['instrumentdata']['plugindata']['continueacrossnotes']))
        if 'file' in trkJ['instrumentdata']['plugindata']:
            xml_sampler.set('src', str(trkJ['instrumentdata']['plugindata']['file']))
        loopenabled = 0
        loopmode = "normal"
        if 'loop' in trkJ['instrumentdata']['plugindata']:
            trkJ_loop = trkJ['instrumentdata']['plugindata']['loop']
            if 'points' in trkJ_loop:
                xml_sampler.set('eframe', str(trkJ_loop['points']['end']))
                xml_sampler.set('lframe', str(trkJ_loop['points']['loop']))
                xml_sampler.set('sframe', str(trkJ_loop['points']['start']))
            if 'enabled' in trkJ_loop:
                loopenabled = trkJ_loop['enabled']
            if 'mode' in trkJ_loop:
                mode = trkJ_loop['mode']
        if loopenabled == 0:
            xml_sampler.set('looped', '0')
        if loopenabled == 1:
            if loopmode == "normal":
                xml_sampler.set('looped', '1')
            if loopmode == "pingpong":
                xml_sampler.set('looped', '2')
        interpolation = "none"
        if 'interpolation' in trkJ['instrumentdata']['plugindata']:
            interpolation = trkJ['instrumentdata']['plugindata']['interpolation']
        if interpolation == "none":
            xml_sampler.set('interp', '0')
        if interpolation == "linear":
            xml_sampler.set('interp', '1')
        if interpolation == "sinc":
            xml_sampler.set('interp', '2')
    else:
        xml_instrumentpreplugin.set('name', "audiofileprocessor")


def asdflfo(jsondata, xmlobj, type, xmltype):
    if 'mod.' + type in jsondata:
        elmodX = ET.SubElement(xmlobj, 'el' + xmltype)
        elmodJ = jsondata['mod.' + type]
        elmodX.set('amt', str(elmodJ['envelope']['amount']))
        elmodX.set('pdel', str(elmodJ['envelope']['predelay']))
        elmodX.set('att', str(elmodJ['envelope']['attack']))
        elmodX.set('hold', str(elmodJ['envelope']['hold']))
        elmodX.set('dec', str(elmodJ['envelope']['decay']))
        elmodX.set('sustain', str(elmodJ['envelope']['sustain']))
        elmodX.set('rel', str(elmodJ['envelope']['release']))
        elmodX.set('lpdel', str(elmodJ['lfo']['predelay']))
        elmodX.set('latt', str(elmodJ['lfo']['attack']))
        elmodX.set('x100', '0')
        lfospeed = float(elmodJ['lfo']['speed']) / 20000
        if lfospeed > 1:
            elmodX.set('x100', '1')
            lfospeed = lfospeed / 100
        elmodX.set('lspd', str(lfospeed))
        elmodX.set('lamt', str(elmodJ['lfo']['amount']))

def lmms_encode_inst_track(xmltag, trkJ):
    global trackscount_forprinting
    trackscount_forprinting += 1
    xmltag.set('solo', "0")
    xmltag.set('type', "0")
    if 'color' in trkJ:
        color = trkJ['color']
        xmltag.set('color', '#' + rgb_to_hex((int(color[0]*255),int(color[1]*255),int(color[2]*255))))

    if 'enabled' in trkJ:
        xmltag.set('muted', str(int(not trkJ['enabled'])))
    else:
        xmltag.set('muted', '0')

    if 'name' in trkJ:
        xmltag.set('name', trkJ['name'])
    else:
        xmltag.set('name', 'untitled')

    #instrumenttrack
    instJ = trkJ['instrumentdata']
    trkX_insttr = ET.SubElement(xmltag, "instrumenttrack")
    trkX_insttr.set('usemasterpitch', "1")
    if 'usemasterpitch'in instJ:
        trkX_insttr.set('usemasterpitch', str(instJ['usemasterpitch']))
    trkX_insttr.set('pitch', "0")
    if 'pitch' in instJ:
        trkX_insttr.set('pitch', str(instJ['pitch']))
    trkX_insttr.set('basenote', "57")
    if 'basenote' in instJ:
        basenote = instJ['basenote']+60
    else:
        basenote = 60
    if instJ['plugin'] != 'sampler':
        basenote += -3
    trkX_insttr.set('basenote', str(basenote))
    if 'fxrack_channel' in trkJ:
        trkX_insttr.set('fxch', str(trkJ['fxrack_channel']))
    else:
        trkX_insttr.set('fxch', '0')
    trkX_insttr.set('pan', "0")
    trkX_insttr.set('pitchrange', "12")
    trkX_insttr.set('vol', "100")
    if 'pan' in trkJ:
        trkX_insttr.set('pan', str(oneto100(trkJ['pan'])))
    if 'vol' in trkJ:
        trkX_insttr.set('vol', str(oneto100(trkJ['vol'])))

    eldataX = ET.SubElement(trkX_insttr, "eldata")
    if 'filter' in instJ:
        json_filter = instJ['filter']
        eldataX.set('fcut', str(json_filter['cutoff']))
        eldataX.set('fwet', str(json_filter['wet']))
        eldataX.set('ftype', str(json_filter['type']))
        eldataX.set('fres', str(json_filter['reso']))

    asdflfo(instJ, eldataX, 'volume', 'vol')
    asdflfo(instJ, eldataX, 'cutoff', 'cut')
    asdflfo(instJ, eldataX, 'reso', 'res')

    if 'arpeggiator' in instJ:
        trkX_arpeggiator = ET.SubElement(trkX_insttr, "arpeggiator")
        json_arpeggiator = instJ['arpeggiator']
        trkX_arpeggiator.set('arpgate', str(json_arpeggiator['gate']))
        trkX_arpeggiator.set('arprange', str(json_arpeggiator['arprange']))
        trkX_arpeggiator.set('arp-enabled', str(json_arpeggiator['enabled']))
        trkX_arpeggiator.set('arpmode', str(json_arpeggiator['mode']))
        trkX_arpeggiator.set('arpdir', str(json_arpeggiator['direction']))
        trkX_arpeggiator.set('arpskip', str(json_arpeggiator['skiprate']))
        trkX_arpeggiator.set('arptime', str(json_arpeggiator['time']))
        trkX_arpeggiator.set('arpmiss', str(json_arpeggiator['missrate']))
        trkX_arpeggiator.set('arpcycle', str(json_arpeggiator['cyclenotes']))
        trkX_arpeggiator.set('arp', str(json_arpeggiator['chord']))

    if 'chordcreator' in instJ:
        trkX_chordcreator = ET.SubElement(trkX_insttr, "chordcreator")
        trkJ_chordcreator = instJ['chordcreator']
        trkX_chordcreator.set('chord-enabled', str(trkJ_chordcreator['enabled']))
        trkX_chordcreator.set('chordrange', str(trkJ_chordcreator['chordrange']))
        trkX_chordcreator.set('chord', str(trkJ_chordcreator['chord']))

    if 'midi' in trkJ:
        trkX_midiport = ET.SubElement(trkX_insttr, "midiport")
        trkJ_midiport = trkJ['midi']
        trkJ_m_i = trkJ_midiport['in']
        trkJ_m_o = trkJ_midiport['out']
        if 'enabled' in trkJ_m_i: trkX_midiport.set('readable', str(trkJ_m_i['enabled']))
        if 'ports' in trkJ_m_i: trkX_midiport.set('inports', midiparseports(trkJ_m_i['ports']))
        if 'fixedvelocity' in trkJ_m_i: trkX_midiport.set('fixedinputvelocity', str(trkJ_m_i['fixedvelocity']-1))
        if 'channel' in trkJ_m_i: trkX_midiport.set('inputchannel', str(trkJ_m_i['channel']))

        if 'enabled' in trkJ_m_o: trkX_midiport.set('writable', str(trkJ_m_o['enabled']))
        if 'ports' in trkJ_m_o: trkX_midiport.set('outports', midiparseports(trkJ_m_o['ports']))
        if 'fixedvelocity' in trkJ_m_o: trkX_midiport.set('fixedoutputvelocity', str(trkJ_m_o['fixedvelocity']-1))
        if 'channel' in trkJ_m_o: trkX_midiport.set('outputchannel', str(trkJ_m_o['channel']))
        if 'fixednote' in trkJ_m_o: trkX_midiport.set('fixedoutputnote', str(trkJ_m_o['fixednote']-1))

        if 'basevelocity' in trkJ_midiport: trkX_midiport.set('basevelocity', str(trkJ_midiport['basevelocity']))


    print('[output-lmms] Instrument Track Name: ' + trkJ['name'])
    lmms_encode_plugin(trkX_insttr, trkJ)

    #placements
    json_placementlist = trkJ['placements']
    tracksnum = 0
    printcountplace = 0
    while tracksnum <= len(json_placementlist)-1:
        global patternscount_forprinting
        patternscount_forprinting += 1
        printcountplace += 1
        print('[output-lmms] └──── Placement ' + str(printcountplace) + ': ', end='')
        json_placement = json_placementlist[tracksnum-1]
        json_notelist = json_placement['notelist']
        patX = ET.SubElement(xmltag, "pattern")
        patX.set('pos', str(int(json_placement['position'] * 48)))
        patX.set('muted', "0")
        patX.set('steps', "16")
        patX.set('name', "")
        patX.set('type', "1")
        if 'color' in json_placement:
            color = json_placement['color']
            patX.set('color', '#' + rgb_to_hex((int(color[0]*255),int(color[1]*255),int(color[2]*255))))
        lmms_encode_notelist(patX, json_notelist)
        tracksnum += 1

def lmms_encode_audio_track(xmltag, trkJ):
    global trackscount_forprinting
    trackscount_forprinting += 1
    xmltag.set('solo', "0")
    xmltag.set('type', "2")
    if 'enabled' in trkJ:
        xmltag.set('muted', str(int(not trkJ['enabled'])))
    else:
        xmltag.set('muted', '0')

    if 'name' in trkJ:
        xmltag.set('name', trkJ['name'])
    else:
        xmltag.set('name', 'untitled')
    tracksnum = 0
    xml_sampletrack = ET.SubElement(xmltag, "sampletrack")
    xml_sampletrack.set('pan', "0")
    xml_sampletrack.set('vol', "100")
    if 'pan' in trkJ:
        xml_sampletrack.set('pan', str(oneto100(trkJ['pan'])))
    if 'vol' in trkJ:
        xml_sampletrack.set('vol', str(oneto100(trkJ['vol'])))
    print('[output-lmms] Audio Track Name: ' + trkJ['name'])

    #placements
    printcountplace = 0
    print('[output-lmms] └──── Placements:', end=' ')
    json_placementlist = trkJ['placements']
    while tracksnum <= len(json_placementlist)-1:
        printcountplace += 1
        print(str(printcountplace), end=' ')
        json_placement = json_placementlist[tracksnum-1]
        patX = ET.SubElement(xmltag, "sampletco")
        patX.set('pos', str(int(round(json_placement['position'] * 48))))
        patX.set('len', str(int(round((json_placement['duration']*bpm)*0.8))))
        patX.set('src', str(json_placement['file']))
        tracksnum += 1
    print('')

def lmms_encode_tracks(xmltag, trksJ):
    for trkJ in trksJ:
        xml_track = ET.SubElement(xmltag, "track")
        if trkJ['type'] == "instrument":
            lmms_encode_inst_track(xml_track, trkJ)
        if trkJ['type'] == "audio":
            lmms_encode_audio_track(xml_track, trkJ)

def lmms_encode_fxrack(xmltag, json_fxrack):
    for json_fxchannel in json_fxrack:
        fxcX = ET.SubElement(xmltag, "fxchannel")
        fxcX.set('soloed', "0")
        fxcX.set('num', str(json_fxchannel['num']))
        num = json_fxchannel['num']

        if 'name' in json_fxchannel:
            name = json_fxchannel['name']
        else:
            name = 'FX ' + str(num)

        if 'vol' in json_fxchannel:
            volume = json_fxchannel['vol']
        else:
            volume = 1

        if 'muted' in json_fxchannel:
            muted = json_fxchannel['muted']
        else:
            muted = 0

        fxcX.set('name', name)
        fxcX.set('volume', str(volume))
        fxcX.set('muted', str(muted))
        if 'sends' in json_fxchannel:
            sendsJ = json_fxchannel['sends']
            for json_send in sendsJ:
                sendX = ET.SubElement(fxcX, "send")
                sendX.set('channel', json_send['channel'])
                sendX.set('amount', json_send['amount'])
        else:
            sendX = ET.SubElement(fxcX, "send")
            sendX.set('channel', '0')
            sendX.set('amount', '1')


class output_lmms(plugin_output.base):
    def __init__(self):
        pass

    def getname(self):
        return 'LMMS'

    def getshortname(self):
        return 'lmms'

    def getcvpjtype(self):
        return 'single'

    def parse(self, convproj_json, output_file):
        print('[output-lmms] Output Start')
        projJ = json.loads(convproj_json)
        
        song.removenotecut(projJ)

        trksJ = projJ['tracks']
        projX = ET.Element("lmms-project")
        projX.set('type', "song")
        projX.set('creator', "DawVert")
        headX = ET.SubElement(projX, "head")
        headX.set('masterpitch', "0")

        if 'timesig_numerator' in projJ: 
            if projJ['mastervol'] is not None:
                headX.set('mastervol', str(oneto100(projJ['mastervol'])))
        else:
            headX.set('mastervol', '100')

        if 'timesig_numerator' in projJ: 
            if projJ['timesig_numerator'] is not None:
                headX.set('timesig_numerator', str(projJ['timesig_numerator']))
        else:
            headX.set('timesig_numerator', '4')

        if 'timesig_denominator' in projJ: 
            if projJ['timesig_denominator'] is not None:
                headX.set('timesig_denominator', str(projJ['timesig_denominator']))
        else:
            headX.set('timesig_denominator', '4')

        if 'bpm' in projJ: 
            if projJ['bpm'] is not None:
                headX.set('bpm', str(projJ['bpm']))
                bpm = projJ['bpm']
        else:
            bpm = 140
        
        songX = ET.SubElement(projX, "song")
        trkcX = ET.SubElement(songX, "trackcontainer")
        
        if 'fxrack' in projJ:
            xml_fxmixer = ET.SubElement(songX, "fxmixer")
            json_fxrack = projJ['fxrack']
            lmms_encode_fxrack(xml_fxmixer, json_fxrack)
        
        lmms_encode_tracks(trkcX, trksJ)
        
        if 'message' in projJ:
            notesX = ET.SubElement(songX, "projectnotes")
            notesX.set("visible", "1")
            notesX.set("x", "728" )
            notesX.set("height", "300")
            notesX.set("y", "5" )
            notesX.set("width", "389")
            notesX.text = ET.CDATA(projJ['message'].replace('\n', '<br/>'))

        print("[output-lmms] Number of Notes: " + str(notescount_forprinting))
        print("[output-lmms] Number of Patterns: " + str(patternscount_forprinting))
        print("[output-lmms] Number of Tracks: " + str(trackscount_forprinting))      

        if 'loop' in projJ:
            tlX = ET.SubElement(songX, "timeline")
            tlX.set('lpstate', str(projJ['loop']['enabled']))
            tlX.set('lp0pos', str(round(projJ['loop']['start']*192)))
            tlX.set('lp1pos', str(round(projJ['loop']['end']*192)))
        
        trksJ = projJ['tracks']
        
        outfile = ET.ElementTree(projX)
        
        ET.indent(outfile)
        outfile.write(output_file, encoding='utf-8')
