# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_output
import json
import lxml.etree as ET
import mido
import zlib
import base64
from functions import placements
from functions import colors

def addvalue(xmltag, name, value):
    x_temp = ET.SubElement(xmltag, name)
    x_temp.text = str(value)


def addcontroller(xmltag, i_id, i_value, i_color):
    x_temp = ET.SubElement(xmltag, 'controller')
    x_temp.set('id', str(i_id))
    x_temp.set('cur', str(i_value))
    x_temp.set('color', i_color)
    x_temp.set('visible', '0')

def addroute_audioout(xmltag, in_channel, in_track, in_type, in_name):
    x_Route = ET.SubElement(xmltag, "Route")
    x_Route.set('channel', str(in_channel))
    x_RouteSource = ET.SubElement(x_Route, "source")
    x_RouteSource.set('track', str(in_track))
    x_RouteDest = ET.SubElement(x_Route, "dest")
    x_RouteDest.set('type', str(in_type))
    x_RouteDest.set('name', str(in_name))

def addroute_audio(xmltag, in_source, in_dest):
    x_Route = ET.SubElement(xmltag, "Route")
    x_RouteSource = ET.SubElement(x_Route, "source")
    x_RouteSource.set('track', str(in_source))
    x_RouteDest = ET.SubElement(x_Route, "dest")
    x_RouteDest.set('track', str(in_dest))

def maketrack_master(x_song):
    global tracknum
    x_AudioOutput = ET.SubElement(x_song, "AudioOutput")
    addvalue(x_AudioOutput, 'name', 'Out')
    addvalue(x_AudioOutput, 'record', 0)
    addvalue(x_AudioOutput, 'mute', 0)
    addvalue(x_AudioOutput, 'solo', 0)
    addvalue(x_AudioOutput, 'off', 0)
    addvalue(x_AudioOutput, 'channels', 2)
    addvalue(x_AudioOutput, 'height', 24)
    addvalue(x_AudioOutput, 'locked', 0)
    addvalue(x_AudioOutput, 'recMonitor', 0)
    addvalue(x_AudioOutput, 'prefader', 0)
    addvalue(x_AudioOutput, 'sendMetronome', 1)
    addvalue(x_AudioOutput, 'automation', 0)
    addvalue(x_AudioOutput, 'gain', 1)
    tracknum += 1

def maketrack_synth(xmltag, insttrackdata, portnum):
    global tracknum
    print('[output-muse] Synth Track '+str(tracknum)+':', insttrackdata['name'])
    global NoteStep
    global synthidnum
    routelist.append([tracknum, 0])
    x_miditrack = ET.SubElement(xmltag, "SynthI")
    if 'name' in insttrackdata: addvalue(x_miditrack, 'name', insttrackdata['name'])
    else: addvalue(x_miditrack, 'name', 'Out')
    if 'vol' in insttrackdata: addcontroller(x_miditrack, 0, insttrackdata['vol'], '#ff0000')
    addvalue(x_miditrack, 'record', 0)
    track_mute = 0
    if 'muted' in insttrackdata: track_mute = insttrackdata['muted']
    else: track_mute = 0
    if 'color' in insttrackdata: addvalue(x_miditrack, 'color', '#'+colors.rgb_float_2_hex(insttrackdata['color']))
    addvalue(x_miditrack, 'solo', 0)
    addvalue(x_miditrack, 'channels', 2)
    addvalue(x_miditrack, 'height', 24)
    addvalue(x_miditrack, 'locked', 0)
    addvalue(x_miditrack, 'recMonitor', 0)
    addvalue(x_miditrack, 'selected', 0)
    addvalue(x_miditrack, 'selectionOrder', 0)
    addvalue(x_miditrack, 'prefader', 0)
    addvalue(x_miditrack, 'sendMetronome', 0)
    addvalue(x_miditrack, 'off', 0)
    addvalue(x_miditrack, 'automation', 0)
    addvalue(x_miditrack, 'port', portnum)
    if 'instdata' in insttrackdata: 
        insttrackdata_instdata = insttrackdata['instdata']
        if 'plugin' in insttrackdata_instdata and 'plugindata' in insttrackdata_instdata: 
            if insttrackdata_instdata['plugin'] == 'vst2-so':
                addvalue(x_miditrack, 'synthType', 'VST (synths)')
                if 'name' in insttrackdata_instdata['plugindata']['plugin']:
                    vstname = insttrackdata_instdata['plugindata']['plugin']['name']
                    if vstname == 'Drops': addvalue(x_miditrack, 'class', 'drops-vst')
                    else: addvalue(x_miditrack, 'class', vstname)
                vstdata = insttrackdata_instdata['plugindata']['data'].encode('ascii')
                vstdata_bytes = base64.b64decode(vstdata)
                musevst = b''
                musevst += len(vstdata_bytes).to_bytes(4, 'big')
                musevst += zlib.compress(vstdata_bytes)
                addvalue(x_miditrack, 'customData', base64.b64encode(musevst).decode('ascii'))

            else:
                addvalue(x_miditrack, 'synthType', 'MESS')
                addvalue(x_miditrack, 'class', 'vam')
                track_mute = 1
        else: 
            addvalue(x_miditrack, 'synthType', 'MESS')
            addvalue(x_miditrack, 'class', 'vam')
            track_mute = 1
    else:
        addvalue(x_miditrack, 'synthType', 'MESS')
        addvalue(x_miditrack, 'class', 'vam')
        track_mute = 1

    addvalue(x_miditrack, 'mute', track_mute)

    tracknum += 1
    synthidnum += 1

def maketrack_midi(xmltag, cvpj_trackplacements, trackname, portnum, insttrackdata):
    global tracknum
    print('[output-muse]  Midi Track '+str(tracknum)+':', insttrackdata['name'])
    global NoteStep
    global synthidnum
    track_transposition = 0
    x_miditrack = ET.SubElement(xmltag, "miditrack")
    if 'color' in insttrackdata: addvalue(x_miditrack, 'color', '#'+colors.rgb_float_2_hex(insttrackdata['color']))
    if 'name' in insttrackdata: addvalue(x_miditrack, 'name', insttrackdata['name'])
    if 'instdata' in insttrackdata:
        if 'middlenote' in insttrackdata['instdata']: 
            track_transposition = -insttrackdata['instdata']['middlenote']

    addvalue(x_miditrack, 'height', 70)
    addvalue(x_miditrack, 'record', 0)
    addvalue(x_miditrack, 'mute', 0)
    addvalue(x_miditrack, 'solo', 0)
    addvalue(x_miditrack, 'device', portnum)
    addvalue(x_miditrack, 'off', 0)
    addvalue(x_miditrack, 'transposition', track_transposition)
    for placement in cvpj_trackplacements:
        x_part = ET.SubElement(x_miditrack, "part")
        if 'name' in placement: addvalue(x_part, 'name', placement['name'])
        p_dur = int(placement['duration']*NoteStep)
        p_pos = int(placement['position']*NoteStep)
        x_poslen = ET.SubElement(x_part, 'poslen')
        x_poslen.set('len', str(p_dur))
        x_poslen.set('tick', str(p_pos))
        if 'notelist' in placement: 
            notelist = placement['notelist']
            for note in notelist:
                x_event = ET.SubElement(x_part, "event")
                x_event.set('tick', str(int(note['position']*NoteStep)+p_pos))
                x_event.set('len', str(int(note['duration']*NoteStep)))
                x_event.set('a', str(note['key']+60))
                if 'vol' in note: x_event.set('b', str(int(note['vol']*100)))
                else: x_event.set('b', '100')
    tracknum += 1

def add_timesig(x_siglist, pos, numerator, denominator):
    x_sig = ET.SubElement(x_siglist, "sig")
    x_sig.set('at', str(int(pos*NoteStep)))
    addvalue(x_sig, 'tick', 0)
    addvalue(x_sig, 'nom', str(int(numerator)))
    addvalue(x_sig, 'denom', str(int(denominator)))

class output_cvpj(plugin_output.base):
    def __init__(self): pass
    def getname(self): return 'MusE'
    def is_dawvert_plugin(self): return 'output'
    def getshortname(self): return 'muse'
    def gettype(self): return 'r'
    def plugin_archs(self): return None
    def getdawcapabilities(self): 
        return {
        'fxrack': False,
        'track_lanes': True,
        'placement_cut': True,
        'placement_loop': False,
        'auto_nopl': True,
        'track_nopl': False
        }
    def parse(self, convproj_json, output_file):
        global NoteStep
        global tracknum
        global synthidnum
        global routelist

        tracknum = 0
        synthidnum = 5

        projJ = json.loads(convproj_json)
        
        midiDivision = 384
        NoteStep = midiDivision/4
        
        cvpj_trackdata = projJ['track_data']
        cvpj_trackordering = projJ['track_order']
        cvpj_trackplacements = projJ['track_placements']

        x_muse = ET.Element("muse")
        x_muse.set('version', "3.4")
        x_song = ET.SubElement(x_muse, "song")
        addvalue(x_song, 'info', '')
        addvalue(x_song, 'showinfo', 1)
        addvalue(x_song, 'cpos', 0) #start
        addvalue(x_song, 'rpos', 0) #end
        addvalue(x_song, 'lpos', 0)
        addvalue(x_song, 'master', 1)
        addvalue(x_song, 'loop', 0)
        addvalue(x_song, 'punchin', 0)
        addvalue(x_song, 'punchout', 0)
        addvalue(x_song, 'record', 0)
        addvalue(x_song, 'solo', 0)
        addvalue(x_song, 'recmode', 0)
        addvalue(x_song, 'cycle', 0)
        addvalue(x_song, 'click', 0)
        addvalue(x_song, 'quantize', 0)
        addvalue(x_song, 'len', 1000000)
        addvalue(x_song, 'follow', 1)
        addvalue(x_song, 'midiDivision', midiDivision)
        addvalue(x_song, 'sampleRate', 44100)
        
        # ---------------------------------- master track ----------------------------------

        maketrack_master(x_song)

        routelist = []

        for cvpj_trackentry in cvpj_trackordering:
            if cvpj_trackentry in cvpj_trackdata:
                s_trkdata = cvpj_trackdata[cvpj_trackentry]
                if s_trkdata['type'] == 'instrument':
                    if cvpj_trackentry in cvpj_trackplacements:
                        cvpj_tr = cvpj_trackplacements[cvpj_trackentry]
                        cvpj_tr_islaned = False
                        if 'laned' in cvpj_tr: 
                            if cvpj_tr['laned'] == 1: 
                                cvpj_tr_islaned = True
                        if cvpj_tr_islaned == False:
                            if 'notes' in cvpj_tr: 
                                maketrack_midi(x_song, cvpj_tr['notes'], s_trkdata['name'], synthidnum, s_trkdata)
                        else:
                            for laneid in cvpj_tr['laneorder']:
                                lanedata = cvpj_tr['lanedata'][laneid]
                                lanename = ''
                                if 'name' in lanedata: lanename = lanedata['name']
                                maketrack_midi(x_song, lanedata['notes'], lanename, synthidnum, s_trkdata)
    
                    maketrack_synth(x_song, s_trkdata, synthidnum)

        addroute_audioout(x_song, 0, 0, 1, "system:playback_1")
        addroute_audioout(x_song, 1, 0, 1, "system:playback_2")

        for routeid in routelist:
            addroute_audio(x_song, routeid[0], routeid[1])

        if 'bpm' in projJ: muse_bpm = int(projJ['bpm'])
        else: muse_bpm = 120

        x_tempolist = ET.SubElement(x_song, "tempolist")
        x_tempolist.set('fix', "0")
        x_tempo = ET.SubElement(x_tempolist, "tempo")
        x_tempo.set('at', "21474837")
        addvalue(x_tempo, 'tick', 0)
        addvalue(x_tempo, 'val', mido.bpm2tempo(muse_bpm))

        if 'timesig_numerator' in projJ: muse_numerator = projJ['timesig_numerator']
        else: muse_numerator = 4
        if 'timesig_denominator' in projJ: muse_denominator = projJ['timesig_denominator']
        else: muse_denominator = 4

        x_siglist = ET.SubElement(x_song, "siglist")

        x_sig = ET.SubElement(x_siglist, "sig")
        x_sig.set('at', "21474836")
        addvalue(x_sig, 'tick', 0)
        addvalue(x_sig, 'nom', str(int(muse_numerator)))
        addvalue(x_sig, 'denom', str(int(muse_denominator)))

        #if 'timemarkers' in projJ: 
        #    for cvpj_timemarker in projJ['timemarkers']:
        #        if 'type' in cvpj_timemarker:
        #            if cvpj_timemarker['type'] == 'timesig':
        #                add_timesig(x_siglist, cvpj_timemarker['position'], cvpj_timemarker['numerator'], cvpj_timemarker['denominator'])

        outfile = ET.ElementTree(x_muse)
        ET.indent(outfile)
        outfile.write(output_file, encoding='utf-8', xml_declaration = True)
        