# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_output
import json
import lxml.etree as ET
from functions import xtramath
from functions import colors
from functions import data_values
from functions import params
from functions import plugins
from functions import tracks
from functions_plugin import waveform_values

def get_plugins(xml_tag, cvpj_fxids):
    for cvpj_fxid in cvpj_fxids:
        plugtype = plugins.get_plug_type(cvpj_l, cvpj_fxid)
        fxdata = data_values.nested_dict_get_value(cvpj_l, ['plugins', cvpj_fxid])
        fx_on = params.get(fxdata, [], 'enabled', True, groupname='params_slot')[0]
        if plugtype[0] == 'native-tracktion' and plugtype[1] in waveform_params:

            wf_PLUGIN = ET.SubElement(xml_tag, "PLUGIN")
            wf_PLUGIN.set('type', plugtype[1])
            wf_PLUGIN.set('presetDirty', '1')
            wf_PLUGIN.set('enabled', str(fx_on))

            for waveform_param in waveform_params[plugtype[1]]:
                defvaluevals = waveform_params[plugtype[1]][waveform_param]
                paramdata = plugins.get_plug_param(cvpj_l, cvpj_fxid, waveform_param, defvaluevals[1])[0]
                wf_PLUGIN.set(waveform_param, str(paramdata))



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
        'placement_loop': ['loop', 'loop_off', 'loop_adv'],
        'time_seconds': True,
        'track_hybrid': True,
        'placement_audio_stretch': ['rate']
        }
    def getsupportedplugformats(self): return []
    def getsupportedplugins(self): return []
    def getfileextension(self): return 'tracktionedit'
    def parse(self, convproj_json, output_file):
        global cvpj_l
        global waveform_params
        wf_proj = ET.Element("EDIT")
        wf_proj.set('appVersion', "Waveform 11.5.18")
        wf_proj.set('modifiedBy', "DawVert")

        waveform_params = waveform_values.devicesparam()

        cvpj_l = json.loads(convproj_json)

        wf_bpmdata = 120
        wf_numerator = 4
        wf_denominator = 4
        wf_bpmdata = params.get(cvpj_l, [], 'bpm', 120)[0]
        if 'timesig' in cvpj_l: wf_numerator, wf_denominator = cvpj_l['timesig']

        tempomul = 120/wf_bpmdata

        wf_globalid = 1000

        wf_TEMPOSEQUENCE = ET.SubElement(wf_proj, "TEMPOSEQUENCE")
        wf_TEMPO = ET.SubElement(wf_TEMPOSEQUENCE, "TEMPO")
        wf_TEMPO.set('startBeat', str(0.0))
        wf_TEMPO.set('bpm', str(wf_bpmdata))
        wf_TEMPO.set('curve', str(1.0))
        wf_TIMESIG = ET.SubElement(wf_TEMPOSEQUENCE, "TIMESIG")
        wf_TIMESIG.set('numerator', str(wf_numerator))
        wf_TIMESIG.set('denominator', str(wf_denominator))
        wf_TIMESIG.set('startBeat', str(0.0))

        if 'track_master' in cvpj_l:
            cvpj_track_master = cvpj_l['track_master']

            wf_MASTERPLUGINS = ET.SubElement(wf_proj, "MASTERPLUGINS")
            if 'chain_fx_audio' in cvpj_track_master: 
                get_plugins(wf_MASTERPLUGINS, cvpj_track_master['chain_fx_audio'])

            wf_MASTERTRACK = ET.SubElement(wf_proj, "MASTERTRACK")
            wf_MASTERTRACK.set('id', str(wf_globalid))
            if 'name' in cvpj_track_master: wf_MASTERTRACK.set('name', cvpj_track_master['name'])
            wf_globalid =+ 1

        for cvpj_trackid, s_trackdata, track_placements in tracks.r_track_iter(cvpj_l):

            wf_TRACK = ET.SubElement(wf_proj, "TRACK")
            wf_TRACK.set('id', str(wf_globalid))
            if 'name' in s_trackdata: wf_TRACK.set('name', s_trackdata['name'])
            if 'color' in s_trackdata: wf_TRACK.set('colour', 'ff'+colors.rgb_float_to_hex(s_trackdata['color']))
            
            #cvpj_track_vol = params.get(s_trackdata, [], 'vol', 1.0)
            #cvpj_track_pan = params.get(s_trackdata, [], 'pan', 0)

            #wf_PLUGINVOLPAN = ET.SubElement(wf_TRACK, "PLUGIN")
            #wf_PLUGINVOLPAN.set('type', 'volume')
            #wf_PLUGINVOLPAN.set('enabled', '1')
            #wf_PLUGINVOLPAN.set('volume', str(cvpj_track_vol))
            #wf_PLUGINVOLPAN.set('pan', str(cvpj_track_pan))

            wf_INST = ET.SubElement(wf_TRACK, "PLUGIN")
            wf_INST.set('type', '4osc')
            wf_INST.set('enabled', '1')

            if 'chain_fx_audio' in s_trackdata: 
                get_plugins(wf_TRACK, s_trackdata['chain_fx_audio'])

            wf_PLUGINMETER = ET.SubElement(wf_TRACK, "PLUGIN")
            wf_PLUGINMETER.set('type', 'level')
            wf_PLUGINMETER.set('enabled', '1')

            if 'notes' in track_placements:
                cvpj_midiplacements = track_placements['notes']
                for cvpj_midiplacement in cvpj_midiplacements:

                    wf_MIDICLIP = ET.SubElement(wf_TRACK, "MIDICLIP")
                    if 'cut' in cvpj_midiplacement:
                        cutdata = cvpj_midiplacement['cut']
                        if cutdata['type'] == 'cut':
                            wf_MIDICLIP.set('offset', str((cutdata['start']/8)*tempomul))
                            wf_MIDICLIP.set('start', str(cvpj_midiplacement['position']))
                            wf_MIDICLIP.set('length', str(cvpj_midiplacement['duration']))
                        if cutdata['type'] in ['loop', 'loop_off', 'loop_adv']:
                            wf_MIDICLIP.set('start', str(cvpj_midiplacement['position']))
                            wf_MIDICLIP.set('length', str(cvpj_midiplacement['duration']))
                            wf_MIDICLIP.set('offset', str((cutdata['start']/8 if 'start' in cutdata else 0)*tempomul))
                            wf_MIDICLIP.set('loopStartBeats', str((cutdata['loopstart']/4 if 'loopstart' in cutdata else 0)))
                            wf_MIDICLIP.set('loopLengthBeats', str((cutdata['loopend']/4)))
                    else:
                        wf_MIDICLIP.set('start', str(cvpj_midiplacement['position']))
                        wf_MIDICLIP.set('length', str(cvpj_midiplacement['duration']))

                    if 'name' in cvpj_midiplacement: wf_MIDICLIP.set('name', cvpj_midiplacement['name'])
                    if 'color' in cvpj_midiplacement: wf_MIDICLIP.set('colour', 'ff'+colors.rgb_float_to_hex(cvpj_midiplacement['color']))
                    if 'muted' in cvpj_midiplacement: wf_MIDICLIP.set('mute', str(int(cvpj_midiplacement['muted'])))
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

            wf_globalid += 1

        outfile = ET.ElementTree(wf_proj)
        ET.indent(outfile)
        outfile.write(output_file, encoding='utf-8', xml_declaration = True)
