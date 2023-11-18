# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_output
import json
import lxml.etree as ET
from functions import xtramath
from functions import colors
from functions import data_values
from functions import note_data
from functions import params
from functions import plugins
from functions import song
from functions import data_dataset
from functions_tracks import tracks_r
import math

delaytime = [
    [0, 16*32],
    [1, 16*28],
    [2, 16*24],
    [3, 16*20],
    [4, 16*16],
    [5, 16*12],
    [6, 16*10],
    [7, 16*8],
    [8, 16*6],
    [9, 16*5],
    [10, 16*4],
    [11, 16*3],
    [12, 16*2],
    [13, 16*1],
    [14, 20],
    [15, 16],
    [16, 11],
    [17, 12],
    [18, 8],
    [19, 5],
    [20, 6],
    [21, 4],
    [22, 2.5],
    [23, 3],
    [24, 2],
    [25, 1.5],
    [26, 1.5],
    [27, 1],
    [28, 0.75],
    [29, 0.75],
    [30, 0.5],
    [31, 3/8],
    [32, 0.25],
    [33, 0.125],
    [34, 0],
]

def get_plugins(xml_tag, cvpj_fxids):
    for cvpj_fxid in cvpj_fxids:
        fx_plugindata = plugins.cvpj_plugin('cvpj', cvpj_l, cvpj_fxid)
        plugtype = fx_plugindata.type_get()
        fx_on, fx_wet = fx_plugindata.fxdata_get()

        if plugtype == ['universal', 'eq-bands']:
            wf_PLUGIN = ET.SubElement(xml_tag, "PLUGIN")
            wf_PLUGIN.set('type', '8bandEq')
            wf_PLUGIN.set('presetDirty', '1')
            num_bands = fx_plugindata.dataval_get('num_bands', 8)

            cvpj_bands_a = fx_plugindata.eqband_get(None)
            cvpj_bands_b = fx_plugindata.eqband_get('b')

            for typedata in [['lm',cvpj_bands_a], ['rs',cvpj_bands_b]]:
                for num in range(min(len(typedata[1]),8)):
                    eqnumtxt = str(num+1)

                    eqbanddata = typedata[1][num]
                    in_band_shape = eqbanddata['type']

                    if in_band_shape == 'low_pass': band_shape = 0
                    elif in_band_shape == 'low_shelf': band_shape = 1
                    elif in_band_shape == 'peak': band_shape = 2
                    elif in_band_shape == 'band_pass': band_shape = 3
                    elif in_band_shape == 'band_stop': band_shape = 4
                    elif in_band_shape == 'high_shelf': band_shape = 5
                    elif in_band_shape == 'high_pass': band_shape = 6
                    else: in_band_shape = 2

                    if in_band_shape in ['low_pass', 'high_pass']: 
                        eq_var = eqbanddata['var']
                        eq_var = xtramath.logpowmul(eq_var, 0.5) if eq_var != 0 else 0
                    elif in_band_shape in ['low_shelf', 'high_shelf']: 
                        eq_var = eqbanddata['var']
                    else: eq_var = (10-eqbanddata['var'])*10

                    if eqbanddata['freq'] != 0: band_freq = note_data.freq_to_note_noround(eqbanddata['freq'])+72
                    else: band_freq = 0

                    wf_PLUGIN.set("enable"+eqnumtxt+typedata[0], str(float(eqbanddata['on'])))
                    wf_PLUGIN.set("freq"+eqnumtxt+typedata[0], str(band_freq))
                    wf_PLUGIN.set("gain"+eqnumtxt+typedata[0], str(eqbanddata['gain']))
                    wf_PLUGIN.set("q"+eqnumtxt+typedata[0], str( eq_var ))
                    wf_PLUGIN.set("shape"+eqnumtxt+typedata[0], str(band_shape))


        elif plugtype == ['universal', 'delay-c']:
            d_time_type = fx_plugindata.dataval_get('time_type', 'seconds')
            d_time = fx_plugindata.dataval_get('time', 1)
            d_feedback = fx_plugindata.dataval_get('feedback', 0.0)

            wf_PLUGIN = ET.SubElement(xml_tag, "PLUGIN")
            wf_PLUGIN.set('type', 'stereoDelay')
            wf_PLUGIN.set('presetDirty', '1')
            wf_PLUGIN.set('enabled', str(fx_on))

            if d_time_type == 'seconds':
                wf_PLUGIN.set('sync', '0.0')
                wf_PLUGIN.set('delaySyncOffL', str(d_time*1000))
                wf_PLUGIN.set('delaySyncOffR', str(d_time*1000))

            if d_time_type == 'steps':
                wf_delaySync = data_values.list_tab_closest(delaytime, d_time, 1)
                wf_PLUGIN.set('sync', '1.0')
                wf_PLUGIN.set('delaySyncOnL', str(wf_delaySync[0][0]))
                wf_PLUGIN.set('delaySyncOnR', str(wf_delaySync[0][0]))

            wf_PLUGIN.set('crossL', '0.0')
            wf_PLUGIN.set('crossR', '0.0')
            wf_PLUGIN.set('feedbackL', str(d_feedback*100))
            wf_PLUGIN.set('feedbackR', str(d_feedback*100))
            wf_PLUGIN.set('mix', str(fx_wet))
            wf_PLUGIN.set('mixLock', '0.0')
            wf_PLUGIN.set('panL', '-1.0')
            wf_PLUGIN.set('panR', '1.0')

        elif plugtype == ['universal', 'compressor']:
            wf_PLUGIN = ET.SubElement(xml_tag, "PLUGIN")
            wf_PLUGIN.set('type', 'comp')
            wf_PLUGIN.set('presetDirty', '1')
            wf_PLUGIN.set('enabled', str(fx_on))

            v_attack = cvpj_plugindata.param_get('attack', 0)[0]*1000
            v_postgain = cvpj_plugindata.param_get('postgain', 0)[0]
            v_pregain = cvpj_plugindata.param_get('pregain', 0)[0]
            v_ratio = cvpj_plugindata.param_get('ratio', 0)[0]
            v_knee = cvpj_plugindata.param_get('knee', 0)[0]
            v_release = cvpj_plugindata.param_get('release', 0)[0]*1000
            v_sidechain_on = int(cvpj_plugindata.param_get('sidechain_on', 0)[0])
            v_threshold = cvpj_plugindata.param_get('threshold', 0)[0]

            wf_PLUGIN.set('threshold', str(v_threshold))
            wf_PLUGIN.set('ratio', str(v_ratio))
            wf_PLUGIN.set('attack', str(v_attack))
            wf_PLUGIN.set('release', str(v_release))
            wf_PLUGIN.set('knee', str(v_knee))
            wf_PLUGIN.set('outputDb', str(v_postgain))
            wf_PLUGIN.set('sidechainTrigger', str(v_sidechain_on))
            wf_PLUGIN.set('inputDb', str(v_pregain))

        elif plugtype[0] == 'native-tracktion' and plugtype[1] in waveform_params:
            wf_PLUGIN = ET.SubElement(xml_tag, "PLUGIN")
            wf_PLUGIN.set('type', plugtype[1])
            wf_PLUGIN.set('presetDirty', '1')
            wf_PLUGIN.set('enabled', str(fx_on))

            paramlist = dataset.params_list('plugin', plugintype)

            for paramid in paramlist:
                dset_paramdata = dataset.params_i_get('plugin', plugintype, paramid)
                paramdata = cvpj_plugindata.param_get(paramid, dset_paramdata[2])[0]
                wf_PLUGIN.set(paramid, str(paramdata))



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
    def getsupportedplugins(self): return ['universal:compressor', 'universal:expander']
    def getfileextension(self): return 'tracktionedit'
    def parse(self, convproj_json, output_file):
        global cvpj_l
        global dataset

        wf_proj = ET.Element("EDIT")
        wf_proj.set('appVersion', "Waveform 11.5.18")
        wf_proj.set('modifiedBy', "DawVert")

        cvpj_l = json.loads(convproj_json)

        dataset = data_dataset.dataset('./data_dset/waveform.dset')

        wf_bpmdata = 120
        wf_numerator = 4
        wf_denominator = 4
        wf_bpmdata = params.get(cvpj_l, [], 'bpm', 120)[0]
        wf_numerator, wf_denominator = song.get_timesig(cvpj_l)

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

        for cvpj_trackid, s_trackdata, track_placements in tracks_r.iter(cvpj_l):

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
                            note_volume = cvpj_note['vol'] if 'vol' in cvpj_note else 1
                            wf_NOTE.set('v', str(int(xtramath.clamp(note_volume*127, 0, 127))))

            wf_globalid += 1

        outfile = ET.ElementTree(wf_proj)
        ET.indent(outfile)
        outfile.write(output_file, encoding='utf-8', xml_declaration = True)
