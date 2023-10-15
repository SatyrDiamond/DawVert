# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_output
import json
import lxml.etree as ET
import mido
import zlib
import os
import base64
from functions import placements
from functions import colors
from functions import params
from functions import data_values
from functions import plugins
from functions import song
from functions_tracks import tracks_r

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
    x_synthtrack = ET.SubElement(xmltag, "SynthI")
    if 'name' in insttrackdata: addvalue(x_synthtrack, 'name', insttrackdata['name'])
    else: addvalue(x_synthtrack, 'name', 'Out')
    if 'vol' in insttrackdata: addcontroller(x_synthtrack, 0, insttrackdata['vol'], '#ff0000')
    addvalue(x_synthtrack, 'record', 0)
    track_mute = insttrackdata['muted'] if 'muted' in insttrackdata else 0
    if 'color' in insttrackdata: addvalue(x_synthtrack, 'color', '#'+colors.rgb_float_to_hex(insttrackdata['color']))
    addvalue(x_synthtrack, 'solo', 0)
    addvalue(x_synthtrack, 'channels', 2)
    addvalue(x_synthtrack, 'height', 24)
    addvalue(x_synthtrack, 'locked', 0)
    addvalue(x_synthtrack, 'recMonitor', 0)
    addvalue(x_synthtrack, 'selected', 0)
    addvalue(x_synthtrack, 'selectionOrder', 0)
    addvalue(x_synthtrack, 'prefader', 0)
    addvalue(x_synthtrack, 'sendMetronome', 0)
    addvalue(x_synthtrack, 'off', 0)
    addvalue(x_synthtrack, 'automation', 0)
    addvalue(x_synthtrack, 'port', portnum)

    if 'chain_fx_audio' in insttrackdata: 
        chain_fx_audio = insttrackdata['chain_fx_audio']
        for pluginid in chain_fx_audio:
            plugintype = plugins.get_plug_type(cvpj_l, pluginid)
            if plugintype[0] == 'ladspa':
                cvpj_plugindata = plugins.get_plug_data(cvpj_l, pluginid)
                x_fx_plugin = ET.SubElement(x_synthtrack, "plugin")
                x_fx_plugin.set('file', cvpj_plugindata['name'])
                x_fx_plugin.set('label', cvpj_plugindata['plugin'])
                x_fx_plugin.set('channel', '1')
                for paramnum in range(cvpj_plugindata['numparams']):
                    pval, ptype, pname = plugins.get_plug_param(cvpj_l, pluginid, 'ladspa_param_'+str(paramnum), 0)
                    x_fx_control = ET.SubElement(x_fx_plugin, "control")
                    x_fx_control.set('name', pname)
                    x_fx_control.set('val', str(pval))

    if 'instdata' in insttrackdata: 
        insttrackdata_instdata = insttrackdata['instdata']
        if 'pluginid' in insttrackdata_instdata: 
            pluginid = insttrackdata_instdata['pluginid']
            plugintype = plugins.get_plug_type(cvpj_l, pluginid)
            if plugintype == ['vst2', 'lin']:
                cvpj_plugindata = plugins.get_plug_data(cvpj_l, pluginid)
                addvalue(x_synthtrack, 'synthType', 'VST (synths)')
                vstpath = data_values.get_value(cvpj_plugindata, 'path', '')
                vstname = os.path.splitext(os.path.basename(vstpath))[0]
                addvalue(x_synthtrack, 'class', vstname)
                datatype = data_values.get_value(cvpj_plugindata, 'datatype', 'none')
                if datatype == 'chunk':
                    vstdata = data_values.get_value(cvpj_plugindata, 'chunk', '')
                    vstdata_bytes = base64.b64decode(vstdata)
                    musevst = b''
                    musevst += len(vstdata_bytes).to_bytes(4, 'big')
                    musevst += zlib.compress(vstdata_bytes)
                    addvalue(x_synthtrack, 'customData', base64.b64encode(musevst).decode('ascii'))
                else: 
                    numparams = data_values.get_value(cvpj_plugindata, 'numparams', 0)
                    for param in range(numparams):
                        pval, ptype, pname = plugins.get_plug_param(cvpj_l, pluginid, 'vst_param_'+str(param), 0)
                        addvalue(x_synthtrack, 'param', pval)

            else: 
                addvalue(x_synthtrack, 'synthType', 'MESS')
                addvalue(x_synthtrack, 'class', 'vam')
                track_mute = 1

        else: 
            addvalue(x_synthtrack, 'synthType', 'MESS')
            addvalue(x_synthtrack, 'class', 'vam')
            track_mute = 1
    else:
        addvalue(x_synthtrack, 'synthType', 'MESS')
        addvalue(x_synthtrack, 'class', 'vam')
        track_mute = 1

    addvalue(x_synthtrack, 'mute', track_mute)

    tracknum += 1
    synthidnum += 1

def maketrack_midi(xmltag, cvpj_trackplacements, trackname, portnum, insttrackdata):
    global tracknum
    print('[output-muse]  Midi Track '+str(tracknum)+':', insttrackdata['name'])
    global NoteStep
    global synthidnum
    track_transposition = 0
    x_miditrack = ET.SubElement(xmltag, "miditrack")
    if 'color' in insttrackdata: addvalue(x_miditrack, 'color', '#'+colors.rgb_float_to_hex(insttrackdata['color']))
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
        if p_dur != 0:
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
        'track_lanes': True,
        'placement_cut': True,
        'auto_nopl': True,
        }
    def getsupportedplugformats(self): return ['vst2']
    def getsupportedplugins(self): return []
    def getfileextension(self): return 'med'
    def parse(self, convproj_json, output_file):
        global NoteStep
        global tracknum
        global synthidnum
        global routelist
        global cvpj_l

        tracknum = 0
        synthidnum = 5

        cvpj_l = json.loads(convproj_json)
        
        midiDivision = 384
        NoteStep = midiDivision/4
        
        x_muse = ET.Element("muse")
        x_muse.set('version', "3.4")
        x_song = ET.SubElement(x_muse, "song")
        addvalue(x_song, 'info', '')
        addvalue(x_song, 'showinfo', 1)

        loop_on, loop_start, loop_end = song.get_loopdata(cvpj_l, 'r')

        addvalue(x_song, 'cpos', 0) #start
        addvalue(x_song, 'rpos', int(loop_end*NoteStep)) #end
        addvalue(x_song, 'lpos', int(loop_start*NoteStep))
        addvalue(x_song, 'master', 1)
        addvalue(x_song, 'loop', int(loop_on))
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

        for cvpj_trackid, cvpj_trackdata, track_placements in tracks_r.iter(cvpj_l):
            if cvpj_trackdata['type'] == 'instrument':
                track_placements_islaned = bool(track_placements['laned']) if 'laned' in track_placements else False

                if track_placements_islaned == False:
                    if 'notes' in track_placements: 
                        maketrack_midi(x_song, track_placements['notes'], cvpj_trackdata['name'], synthidnum, cvpj_trackdata)
                else:
                    for laneid in track_placements['laneorder']:
                        lanedata = track_placements['lanedata'][laneid]
                        lanename = lanedata['name'] if 'name' in lanedata else ''
                        maketrack_midi(x_song, lanedata['notes'], lanename, synthidnum, cvpj_trackdata)
    
                maketrack_synth(x_song, cvpj_trackdata, synthidnum)

        addroute_audioout(x_song, 0, 0, 1, "system:playback_1")
        addroute_audioout(x_song, 1, 0, 1, "system:playback_2")

        for routeid in routelist:
            addroute_audio(x_song, routeid[0], routeid[1])

        muse_bpm = int(params.get(cvpj_l, [], 'bpm', 120)[0])

        muse_numerator, muse_denominator = song.get_timesig(cvpj_l)

        x_tempolist = ET.SubElement(x_song, "tempolist")
        x_tempolist.set('fix', "0")
        x_tempo = ET.SubElement(x_tempolist, "tempo")
        x_tempo.set('at', "21474837")
        addvalue(x_tempo, 'tick', 0)
        addvalue(x_tempo, 'val', mido.bpm2tempo(muse_bpm))

        x_siglist = ET.SubElement(x_song, "siglist")

        x_sig = ET.SubElement(x_siglist, "sig")
        x_sig.set('at', "21474836")
        addvalue(x_sig, 'tick', 0)
        addvalue(x_sig, 'nom', str(int(muse_numerator)))
        addvalue(x_sig, 'denom', str(int(muse_denominator)))

        #if 'timemarkers' in cvpj_l: 
        #    for cvpj_timemarker in cvpj_l['timemarkers']:
        #        if 'type' in cvpj_timemarker:
        #            if cvpj_timemarker['type'] == 'timesig':
        #                add_timesig(x_siglist, cvpj_timemarker['position'], cvpj_timemarker['numerator'], cvpj_timemarker['denominator'])

        outfile = ET.ElementTree(x_muse)
        ET.indent(outfile)
        outfile.write(output_file, encoding='utf-8', xml_declaration = True)
        