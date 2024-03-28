# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_output
import json
import lxml.etree as ET
import mido
import zlib
import base64
import math
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

def maketrack_synth(convproj_obj, xmltag, track_obj, portnum):
    global tracknum
    global synthidnum
    print('[output-muse] Synth Track '+str(tracknum)+':', track_obj.visual.name)
    routelist.append([tracknum, 0])
    x_synthtrack = ET.SubElement(xmltag, "SynthI")
    addcontroller(x_synthtrack, 0, track_obj.params.get('vol', 1).value, '#ff0000')
    addvalue(x_synthtrack, 'record', 0)
    track_mute = not track_obj.params.get('enabled', True).value
    if track_obj.visual.name: addvalue(x_synthtrack, 'name', track_obj.visual.name)
    if track_obj.visual.color: addvalue(x_synthtrack, 'color', '#'+colors.rgb_float_to_hex(track_obj.visual.color))
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

    pluginsupported = False

    plugin_found, plugin_obj = convproj_obj.get_plugin(track_obj.inst_pluginid)
    if plugin_found: 
        if plugin_obj.check_match('vst2', 'win'):
            pluginsupported = True
            addvalue(x_synthtrack, 'synthType', 'VST (synths)')

            vstname = plugin_obj.dataval_get('name', '')
            vstclass = plugin_obj.dataval_get('name', '')
            if vstclass == 'Vitalium': vstclass = 'vitalium'
            addvalue(x_synthtrack, 'class', vstclass)
            addvalue(x_synthtrack, 'label', vstname)

            vstdata_bytes = plugin_obj.rawdata_get('chunk')
            musevst = b''
            musevst += len(vstdata_bytes).to_bytes(4, 'big')
            musevst += zlib.compress(vstdata_bytes)
            addvalue(x_synthtrack, 'customData', base64.b64encode(musevst).decode('ascii'))

    if pluginsupported == False:
        addvalue(x_synthtrack, 'synthType', 'MESS')
        addvalue(x_synthtrack, 'class', 'vam')
        track_mute = 1

    addvalue(x_synthtrack, 'mute', track_mute)

    tracknum += 1
    synthidnum += 1

def maketrack_midi(xmltag, placements_obj, trackname, portnum, track_obj):
    global tracknum
    global synthidnum
    print('[output-muse]  Midi Track '+str(tracknum)+':', trackname)
    track_transposition = 0
    x_miditrack = ET.SubElement(xmltag, "miditrack")
    if track_obj.visual.color: addvalue(x_miditrack, 'color', '#'+colors.rgb_float_to_hex(track_obj.visual.color))
    addvalue(x_miditrack, 'name', trackname)
    addvalue(x_miditrack, 'height', 70)
    addvalue(x_miditrack, 'record', 0)
    addvalue(x_miditrack, 'mute', 0)
    addvalue(x_miditrack, 'solo', 0)
    addvalue(x_miditrack, 'device', portnum)
    addvalue(x_miditrack, 'off', 0)
    addvalue(x_miditrack, 'transposition', -track_obj.datavals.get('middlenote', 0))

    for notespl_obj in placements_obj.pl_notes:
        x_part = ET.SubElement(x_miditrack, "part")
        if notespl_obj.visual.name: addvalue(x_part, 'name', notespl_obj.visual.name)
        p_dur = int(notespl_obj.duration)
        p_pos = int(notespl_obj.position)
        x_poslen = ET.SubElement(x_part, 'poslen')
        x_poslen.set('len', str(p_dur))
        x_poslen.set('tick', str(p_pos))

        notespl_obj.notelist.sort()
        for t_pos, t_dur, t_keys, t_vol, t_inst, t_extra, t_auto, t_slide in notespl_obj.notelist.iter():
            for t_key in t_keys:
                x_event = ET.SubElement(x_part, "event")
                x_event.set('tick', str(t_pos+p_pos))
                x_event.set('len', str(t_dur))
                x_event.set('a', str(int(t_key+60)))
                x_event.set('b', str(int(t_vol*100)))

    tracknum += 1

wavetime = 57.422

def maketrack_wave(convproj_obj, xmltag, placements_obj, track_obj):
    global tracknum
    global synthidnum
    global muse_bpm
    print('[output-muse]  Wave Track '+str(tracknum)+':', track_obj.visual.name)
    x_wavetrack = ET.SubElement(xmltag, "wavetrack")
    routelist.append([tracknum, 0])
    if track_obj.visual.color: addvalue(x_miditrack, 'color', '#'+colors.rgb_float_to_hex(track_obj.visual.color))
    if track_obj.visual.name: addvalue(x_miditrack, 'name', track_obj.visual.name)
    addvalue(x_wavetrack, 'height', 70)
    addvalue(x_wavetrack, 'record', 0)
    addvalue(x_wavetrack, 'mute', 0)
    addvalue(x_wavetrack, 'solo', 0)
    addvalue(x_wavetrack, 'off', 0)

    for audiopl_obj in placements_obj.iter_audio():
        x_part = ET.SubElement(x_wavetrack, "part")
        if audiopl_obj.visual.name: addvalue(x_part, 'name', audiopl_obj.visual.name)
        p_dur = int(audiopl_obj.duration)
        p_pos = int(audiopl_obj.position)

        p_dur = int((p_dur*wavetime)*(120/muse_bpm))
        p_pos = int((p_pos*wavetime)*(120/muse_bpm))

        x_poslen = ET.SubElement(x_part, 'poslen')
        x_poslen.set('len', str(p_dur))
        x_poslen.set('sample', str(p_pos))

        offset = audiopl_obj.cut_data['start'] if 'start' in audiopl_obj.cut_data else 0
        frameval = int((offset*(wavetime))*(120/muse_bpm))

        xp_event = ET.SubElement(x_part, 'event')
        xp_poslen = ET.SubElement(xp_event, 'poslen')
        xp_poslen.set('len', str(int(p_dur)))
        xp_poslen.set('sample', str(int(p_pos)))
        ref_found, sampleref_obj = convproj_obj.get_sampleref(audiopl_obj.sampleref)
        if ref_found: 
            addvalue(xp_event, 'file', sampleref_obj.fileref.get_path('unix', True))

            #print(frameval, sampleref_obj.hz)

            frameval *= sampleref_obj.hz/44100

            addvalue(xp_event, 'frame', int(frameval))

            if not audiopl_obj.stretch.is_warped:
                stretchlist = [0, 1, 1, 1, 7]

                muse_pitch = pow(2, audiopl_obj.pitch/12)
                stretchlist[0] = 1

                muse_stretch = (1/audiopl_obj.stretch.rate_tempo)

                if audiopl_obj.stretch.algorithm != 'resample':
                    stretchlist[1] = muse_stretch*muse_pitch
                    stretchlist[2] = muse_pitch
                else:
                    stretchlist[2] = 1/muse_stretch

                xp_stretchlist = ET.SubElement(xp_event, 'stretchlist')
                xp_stretchlist.text = ' '.join([str(x) for x in stretchlist])

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
    def plugin_archs(self): return ['amd64', 'i386']
    def getdawinfo(self, dawinfo_obj): 
        dawinfo_obj.name = 'Online Sequencer'
        dawinfo_obj.file_ext = 'sequence'
        dawinfo_obj.fxrack = False
        dawinfo_obj.track_lanes = True
        dawinfo_obj.placement_cut = True
        dawinfo_obj.audio_stretch = ['rate']
        dawinfo_obj.auto_types = ['nopl_points']
        dawinfo_obj.track_nopl = False
        dawinfo_obj.plugin_included = []
    def getsupportedplugformats(self): return ['vst2']
    def getsupportedplugins(self): return []
    def getfileextension(self): return 'med'
    def parse(self, convproj_obj, output_file):
        global tracknum
        global synthidnum
        global routelist
        global muse_bpm

        midiDivision = 384

        convproj_obj.change_timings(midiDivision, False)

        tracknum = 0
        synthidnum = 5

        muse_bpm = convproj_obj.params.get('bpm', 120).value

        x_muse = ET.Element("muse")
        x_muse.set('version', "3.4")
        x_song = ET.SubElement(x_muse, "song")
        addvalue(x_song, 'info', '')
        addvalue(x_song, 'showinfo', 1)
        addvalue(x_song, 'cpos', 0) #start
        addvalue(x_song, 'rpos', -1) #end
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

        for trackid, track_obj in convproj_obj.iter_track():

            if track_obj.type == 'instrument':
                maketrack_midi(x_song, track_obj.placements, track_obj.visual.name, synthidnum, track_obj)

                if track_obj.is_laned:
                    for laneid, lane_obj in track_obj.lanes.items():
                        lanename = lane_obj.visual.name if lane_obj.visual.name else laneid
                        maketrack_midi(x_song, lane_obj.placements, lanename, synthidnum, track_obj)

                maketrack_synth(convproj_obj, x_song, track_obj, synthidnum)

            if track_obj.type == 'audio':
                maketrack_wave(convproj_obj, x_song, track_obj.placements, track_obj)

        addroute_audioout(x_song, 0, 0, 1, "system:playback_1")
        addroute_audioout(x_song, 1, 0, 1, "system:playback_2")

        for routeid in routelist:
            addroute_audio(x_song, routeid[0], routeid[1])

        x_tempolist = ET.SubElement(x_song, "tempolist")
        x_tempolist.set('fix', "0")
        x_tempo = ET.SubElement(x_tempolist, "tempo")
        x_tempo.set('at', "21474837")
        addvalue(x_tempo, 'tick', 0)
        addvalue(x_tempo, 'val', mido.bpm2tempo(muse_bpm))

        muse_numerator, muse_denominator = convproj_obj.timesig

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
        