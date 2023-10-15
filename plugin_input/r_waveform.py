# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import placement_data
from functions import note_data
from functions import song
from functions import colors
from functions import plugins
from functions_plugin import waveform_values
from functions_tracks import tracks_r
from functions_tracks import fxslot
from lxml import etree
import plugin_input
import json

def xml_getvalue(xmltag, xmlname, fallbackval): 
    xmlval = xmltag.get(xmlname)
    if xmlval != None: return xmlval
    else: return fallbackval

def get_plugins(xml_track, trackid): 
    for xml_part in xml_track:
        if xml_part.tag == 'PLUGIN':
            plugintype = xml_part.get('type')
            if plugintype not in ['volume', 'level']:

                if plugintype != None:

                    pluginid = plugins.get_id()

                    if plugintype == '8bandEq':
                        plugins.add_plug(cvpj_l, pluginid, 'universal', 'eq-bands')
                        plugins.add_plug_data(cvpj_l, pluginid, 'num_bands', 8)

                        for num in range(8):
                            eqnumtxt = str(num+1)
                            for typenames in [['lm',None], ['rs','b']]:

                                band_enable = float(xml_getvalue(xml_part, "enable"+eqnumtxt+typenames[0], 0))
                                band_freq = float(xml_getvalue(xml_part, "freq"+eqnumtxt+typenames[0], 0))
                                band_gain = float(xml_getvalue(xml_part, "gain"+eqnumtxt+typenames[0], 0))
                                band_q = (10-float(xml_getvalue(xml_part, "q"+eqnumtxt+typenames[0], 0)))/10
                                band_shape = int(xml_getvalue(xml_part, "shape"+eqnumtxt+typenames[0], 1))

                                if band_shape == 0: band_shape = 'low_pass'
                                if band_shape == 1: band_shape = 'low_shelf'
                                if band_shape == 2: band_shape = 'peak'
                                if band_shape == 3: band_shape = 'band_pass'
                                if band_shape == 4: band_shape = 'band_stop'
                                if band_shape == 5: band_shape = 'high_shelf'
                                if band_shape == 6: band_shape = 'high_pass'

                                band_freq = note_data.note_to_freq(band_freq-72)

                                plugins.add_eqband(cvpj_l, pluginid, int(band_enable), band_freq, band_gain, band_shape, band_q, typenames[1])

                    elif plugintype == 'comp':
                        plugins.add_plug(cvpj_l, pluginid, 'universal', 'compressor')
                        waveform_pvs = waveform_params[plugintype]
                        for waveform_pv in waveform_pvs:
                            #print('-', waveform_pv)
                            paramtype, paramfb = waveform_pvs[waveform_pv]
                            paramval = xml_getvalue(xml_part, waveform_pv, paramfb)
                            if waveform_pv == 'attack': plugins.add_plug_param(cvpj_l, pluginid, 'attack', float(paramval)/1000, 'float', 'threshold')
                            if waveform_pv == 'inputDb': plugins.add_plug_param(cvpj_l, pluginid, 'pregain', float(paramval), 'float', 'pregain')
                            if waveform_pv == 'knee': plugins.add_plug_param(cvpj_l, pluginid, 'knee', float(paramval), 'float', 'knee')
                            if waveform_pv == 'outputDb': plugins.add_plug_param(cvpj_l, pluginid, 'postgain', float(paramval), 'float', 'postgain')
                            if waveform_pv == 'ratio': plugins.add_plug_param(cvpj_l, pluginid, 'ratio', float(paramval), 'float', 'ratio')
                            if waveform_pv == 'release': plugins.add_plug_param(cvpj_l, pluginid, 'release', float(paramval)/1000, 'float', 'threshold')
                            if waveform_pv == 'sidechainTrigger': plugins.add_plug_param(cvpj_l, pluginid, 'sidechain_on', bool(paramval), 'float', 'sidechain on')
                            if waveform_pv == 'threshold': plugins.add_plug_param(cvpj_l, pluginid, 'threshold', float(paramval), 'float', 'threshold')

                    elif plugintype in waveform_params:
                        waveform_pvs = waveform_params[plugintype]
                        plugins.add_plug(cvpj_l, pluginid, 'native-tracktion', plugintype)
                        plugins.add_plug_fxdata(cvpj_l, pluginid, int(xml_getvalue(xml_part, 'enabled', 1)), 1)
                        
                        for waveform_pv in waveform_pvs:
                            paramtype, paramfb = waveform_pvs[waveform_pv]
                            paramval = xml_getvalue(xml_part, waveform_pv, paramfb)
                            plugins.add_plug_param(cvpj_l, pluginid, waveform_pv, paramval, paramtype, waveform_pv)
                    
                        if plugintype == 'pitchShifter': plugins.add_plug_data(cvpj_l, pluginid, 'elastiqueOptions', xml_getvalue(xml_part, 'elastiqueOptions', '1/0/0/0/64'))
                        if plugintype == 'lowpass': plugins.add_plug_data(cvpj_l, pluginid, 'mode', xml_getvalue(xml_part, 'mode', 'lowpass'))

                    if trackid == None: fxslot.insert(cvpj_l, ['master'], 'audio', pluginid)
                    else: fxslot.insert(cvpj_l, ['track', trackid], 'audio', pluginid)

class input_cvpj_f(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'waveform_edit'
    def getname(self): return 'Waveform Edit'
    def gettype(self): return 'r'
    def getdawcapabilities(self): 
        return {
        'placement_cut': True,
        'placement_loop': ['loop', 'loop_off', 'loop_adv'],
        'time_seconds': True,
        'placement_audio_stretch': ['rate']
        }
    def supported_autodetect(self): return False
    def parse(self, input_file, extra_param):
        global waveform_params
        global cvpj_l
        #bytestream = open(input_file, 'r')
        #file_data = bytestream.read()
        parser = etree.XMLParser(recover=True, encoding='utf-8')
        xml_data = etree.parse(input_file, parser)
        xml_waveform = xml_data.getroot()

        cvpj_l = {}

        waveform_params = waveform_values.devicesparam()

        tempo = 120
        timesig = [4,4]

        tracknum = 1
        for xml_part in xml_waveform:

            if xml_part.tag == 'TEMPOSEQUENCE':
                TEMPO_parts = xml_part.findall('TEMPO')
                for TEMPO_part in TEMPO_parts:
                    TEMPO_startBeat = float(xml_getvalue(TEMPO_part, 'startBeat', '0.0'))
                    TEMPO_bpm = float(xml_getvalue(TEMPO_part, 'bpm', '120.0'))
                    if TEMPO_startBeat == 0: tempo = TEMPO_bpm

                TIMESIG_parts = xml_part.findall('TIMESIG')
                for TIMESIG_part in TIMESIG_parts:
                    TIMESIG_startBeat = float(xml_getvalue(TIMESIG_part, 'startBeat', '0.0'))
                    TIMESIG_numerator = int(xml_getvalue(TIMESIG_part, 'numerator', '4'))
                    TIMESIG_denominator = int(xml_getvalue(TIMESIG_part, 'denominator', '4'))
                    if TIMESIG_startBeat == 0: timesig = [TIMESIG_numerator,TIMESIG_denominator]

            if xml_part.tag == 'MASTERPLUGINS':
                get_plugins(xml_part, None)

            if xml_part.tag == 'TRACK':
                cvpj_trackid = str(tracknum)
                track_name = xml_getvalue(xml_part, 'name', '')
                track_colour = xml_getvalue(xml_part, 'colour', None)
                if track_colour != None: track_colour = colors.hex_to_rgb_float(track_colour[2:])
                tracks_r.track_create(cvpj_l, cvpj_trackid, 'instrument')
                tracks_r.track_visual(cvpj_l, cvpj_trackid, name=track_name, color=track_colour)

                MIDICLIP_parts = xml_part.findall('MIDICLIP')
                for MIDICLIP_part in MIDICLIP_parts:
                    clip_start = float(xml_getvalue(MIDICLIP_part, 'start', '0'))
                    clip_length = float(xml_getvalue(MIDICLIP_part, 'length', '0'))
                    clip_offset = float(xml_getvalue(MIDICLIP_part, 'offset', '0'))
                    clip_loopStartBeats = float(xml_getvalue(MIDICLIP_part, 'loopStartBeats', '0'))
                    clip_loopLengthBeats = float(xml_getvalue(MIDICLIP_part, 'loopLengthBeats', '0'))

                    cvpj_notelist = []
                    cvpj_pldata = {}
                    cvpj_pldata["position"] = clip_start
                    cvpj_pldata["duration"] = clip_length
                    if clip_loopStartBeats == 0 and clip_loopLengthBeats == 0:
                        if clip_start == 0:
                            cvpj_pldata['cut'] = {}
                            cvpj_pldata['cut']['type'] = 'cut'
                            cvpj_pldata['cut']['start'] = clip_offset
                    else:
                        cvpj_pldata['cut'] = placement_data.cutloopdata(clip_offset, clip_loopStartBeats, clip_loopStartBeats+clip_loopLengthBeats)
    
                    MIDICLIP_SEQUENCES = MIDICLIP_part.findall('SEQUENCE')
                    for MIDICLIP_SEQUENCE in MIDICLIP_SEQUENCES:
                        for seqdata in MIDICLIP_SEQUENCE:
                            if seqdata.tag == 'NOTE':
                                cvpj_note = {}
                                cvpj_note["key"] = int(xml_getvalue(seqdata, 'p', '60'))-60
                                cvpj_note["position"] = float(xml_getvalue(seqdata, 'b', '0'))*4
                                cvpj_note["duration"] = float(xml_getvalue(seqdata, 'l', '0'))*4
                                cvpj_note["velocity"] = float(xml_getvalue(seqdata, 'v', '100'))/100
                                cvpj_notelist.append(cvpj_note)

                    cvpj_pldata["notelist"] = cvpj_notelist
                    tracks_r.add_pl(cvpj_l, cvpj_trackid, 'notes', cvpj_pldata)

                get_plugins(xml_part, cvpj_trackid)

                tracknum += 1

        song.add_timesig(cvpj_l, timesig[0], timesig[1])
        song.add_param(cvpj_l, 'bpm', tempo)

        return json.dumps(cvpj_l)

