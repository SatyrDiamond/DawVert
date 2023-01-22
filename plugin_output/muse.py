# SPDX-FileCopyrightText: 2022 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_output
import json
import lxml.etree as ET
import mido
from functions import placements

def addvalue(xmltag, name, value):
    x_temp = ET.SubElement(xmltag, name)
    x_temp.text = str(value)

def insttrack(xmltag, insttrackdata):
    global NoteStep
    x_miditrack = ET.SubElement(xmltag, "miditrack")
    if 'name' in insttrackdata: addvalue(x_miditrack, 'name', insttrackdata['name'])
    else: addvalue(x_miditrack, 'name', 'Out')
    addvalue(x_miditrack, 'record', 0)
    if 'muted' in insttrackdata: addvalue(x_miditrack, 'mute', insttrackdata['muted'])
    else: addvalue(x_miditrack, 'mute', 0)
    addvalue(x_miditrack, 'solo', 0)
    addvalue(x_miditrack, 'off', 0)
    if 'placements' in insttrackdata:
        placements = insttrackdata['placements']
        for placement in placements:
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
                    x_event.set('a', str(note['key']+84))
                    if 'vol' in note: x_event.set('b', str(int(note['vol']*100)))
                    else: x_event.set('b', '100')


class output_cvpj(plugin_output.base):
    def __init__(self): pass
    def getname(self): return 'MusE'
    def is_dawvert_plugin(self): return 'output'
    def getshortname(self): return 'muse'
    def gettype(self): return 'r'
    def parse(self, convproj_json, output_file):
        projJ = json.loads(convproj_json)
        
        placements.removelanes(projJ)

        global NoteStep
        midiDivision = 384
        NoteStep = midiDivision/4
        
        cvpj_trackdata = projJ['trackdata']
        cvpj_trackordering = projJ['trackordering']

        x_muse = ET.Element("muse")
        x_muse.set('version', "3.3")
        x_song = ET.SubElement(x_muse, "song")
        addvalue(x_song, 'info', '')
        addvalue(x_song, 'showinfo', 1)
        addvalue(x_song, 'cpos', 0) #start
        addvalue(x_song, 'rpos', 0) #end
        addvalue(x_song, 'lpos', 10000)
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

        for cvpj_trackentry in cvpj_trackordering:
            if cvpj_trackentry in cvpj_trackdata:
                s_trkdata = cvpj_trackdata[cvpj_trackentry]
                if s_trkdata['type'] == 'instrument':
                    insttrack(x_song, s_trkdata)

        x_tempolist = ET.SubElement(x_song, "tempolist")
        x_tempolist.set('fix', "500000")
        x_tempo = ET.SubElement(x_tempolist, "tempo")
        x_tempo.set('at', "21474837")
        addvalue(x_tempo, 'tick', 0)
        addvalue(x_tempo, 'val', mido.bpm2tempo(projJ['bpm']))

        outfile = ET.ElementTree(x_muse)
        ET.indent(outfile)
        outfile.write(output_file, encoding='utf-8', xml_declaration = True)
        