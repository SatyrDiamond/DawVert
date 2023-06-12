# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_output
import json
import lxml.etree as ET
from functions import xtramath
from functions import colors

class output_waveform_edit(plugin_output.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'output'
    def getname(self): return 'Waveform Edit'
    def getshortname(self): return 'waveform_edit'
    def gettype(self): return 'r'
    def plugin_archs(self): return None
    def getdawcapabilities(self): 
        return {
        'placement_cut': True,
        'placement_loop': True,
        'time_seconds': True,
        'placement_audio_stretch': ['rate']
        }
    def getsupportedplugins(self): return []
    def parse(self, convproj_json, output_file):
        wf_proj = ET.Element("EDIT")
        wf_proj.set('appVersion', "Waveform 11.5.18")
        wf_proj.set('modifiedBy', "DawVert")

        projJ = json.loads(convproj_json)

        wf_bpmdata = 120
        wf_numerator = 4
        wf_denominator = 4
        if 'bpm' in projJ: wf_bpmdata = projJ['bpm']
        if 'timesig_numerator' in projJ: wf_numerator = projJ['timesig_numerator']
        if 'timesig_denominator' in projJ: wf_denominator = projJ['timesig_denominator']

        tempomul = 120/wf_bpmdata

        wf_trackid = 1000

        wf_TEMPOSEQUENCE = ET.SubElement(wf_proj, "TEMPOSEQUENCE")
        wf_TEMPO = ET.SubElement(wf_TEMPOSEQUENCE, "TEMPO")
        wf_TEMPO.set('startBeat', str(0.0))
        wf_TEMPO.set('bpm', str(wf_bpmdata))
        wf_TEMPO.set('curve', str(1.0))
        wf_TIMESIG = ET.SubElement(wf_TEMPOSEQUENCE, "TIMESIG")
        wf_TIMESIG.set('numerator', str(wf_numerator))
        wf_TIMESIG.set('denominator', str(wf_denominator))
        wf_TIMESIG.set('startBeat', str(0.0))

        if 'track_master' in projJ:
            cvpj_track_master = projJ['track_master']
            wf_MASTERTRACK = ET.SubElement(wf_proj, "MASTERTRACK")
            wf_MASTERTRACK.set('id', str(wf_trackid))
            if 'name' in cvpj_track_master: wf_MASTERTRACK.set('name', cvpj_track_master['name'])
            wf_trackid =+ 1

        if 'track_order' in projJ and 'track_data' in projJ:
            for cvpj_trackid in projJ['track_order']:
                cvpj_s_track_data = projJ['track_data'][cvpj_trackid]
                #print(cvpj_s_track_data)
                wf_TRACK = ET.SubElement(wf_proj, "TRACK")
                wf_TRACK.set('id', str(wf_trackid))
                if 'name' in cvpj_s_track_data: wf_TRACK.set('name', cvpj_s_track_data['name'])
                if 'color' in cvpj_s_track_data: wf_TRACK.set('colour', 'ff'+colors.rgb_float_2_hex(cvpj_s_track_data['color']))
                
                if cvpj_trackid in projJ['track_placements']:
                    if 'notes' in projJ['track_placements'][cvpj_trackid]:
                        cvpj_midiplacements = projJ['track_placements'][cvpj_trackid]['notes']
                        for cvpj_midiplacement in cvpj_midiplacements:

                            wf_MIDICLIP = ET.SubElement(wf_TRACK, "MIDICLIP")
                            if 'cut' in cvpj_midiplacement:
                                cutdata = cvpj_midiplacement['cut']
                                if cutdata['type'] == 'cut':
                                    wf_MIDICLIP.set('offset', str((cutdata['start']/8)*tempomul))
                                    wf_MIDICLIP.set('start', str(cvpj_midiplacement['position']))
                                    wf_MIDICLIP.set('length', str(cvpj_midiplacement['duration']))
                                if cutdata['type'] == 'loop':
                                    wf_MIDICLIP.set('offset', str((cutdata['start']/8)*tempomul))
                                    wf_MIDICLIP.set('start', str(cvpj_midiplacement['position']))
                                    wf_MIDICLIP.set('length', str(cvpj_midiplacement['duration']))
                                    wf_MIDICLIP.set('offset', str((cutdata['start']/8)*tempomul))
                                    wf_MIDICLIP.set('loopStartBeats', str((cutdata['loopstart']/4)))
                                    wf_MIDICLIP.set('loopLengthBeats', str((cutdata['loopend']/4)))
                            else:
                                wf_MIDICLIP.set('start', str(cvpj_midiplacement['position']))
                                wf_MIDICLIP.set('length', str(cvpj_midiplacement['duration']))

                            if 'name' in cvpj_midiplacement: wf_MIDICLIP.set('name', cvpj_midiplacement['name'])
                            if 'color' in cvpj_midiplacement: wf_MIDICLIP.set('colour', 'ff'+colors.rgb_float_2_hex(cvpj_midiplacement['color']))
                            if 'notelist' in cvpj_midiplacement: 
                                wf_SEQUENCE = ET.SubElement(wf_MIDICLIP, "SEQUENCE")
                                wf_SEQUENCE.set('ver', '1')
                                wf_SEQUENCE.set('channelNumber', '1')
                                for cvpj_note in cvpj_midiplacement['notelist']:
                                    wf_NOTE = ET.SubElement(wf_SEQUENCE, "NOTE")
                                    wf_NOTE.set('p', str(cvpj_note['key']+60))
                                    wf_NOTE.set('b', str(cvpj_note['position']/4))
                                    wf_NOTE.set('l', str(cvpj_note['duration']/4))
                                    if 'vol' in cvpj_note: wf_NOTE.set('v', str(int(xtramath.clamp(cvpj_note['vol']*127, 0, 127))))

                wf_trackid += 1

        outfile = ET.ElementTree(wf_proj)
        ET.indent(outfile)
        outfile.write(output_file, encoding='utf-8', xml_declaration = True)
