# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import placement_data
from functions import note_data
from functions import song
from functions import colors
from functions import plugins
from functions import data_dataset
from functions_tracks import tracks_r
from functions_tracks import fxslot
from lxml import etree
import plugin_input
import json
import math

def xml_getvalue(xmltag, xmlname, fallbackval): 
    xmlval = xmltag.get(xmlname)
    if xmlval != None: return xmlval
    else: return fallbackval

def get_plugins(xml_track, trackid): 
    for xml_part in xml_track:
        if xml_part.tag == 'PLUGIN':
            plugintype = xml_part.get('type')

            plugin_xpos = xml_part.get('windowX')
            plugin_ypos = xml_part.get('windowY')

            if plugintype not in ['volume', 'level']:

                if plugintype != None:
                    pluginid = plugins.get_id()

                    if plugin_xpos and plugin_ypos:
                        song.add_visual_window(cvpj_l, 'plugin', pluginid, [int(plugin_xpos), int(plugin_ypos)], None, False, False)

                    fx_plugindata = plugins.cvpj_plugin('deftype', 'native-tracktion', plugintype)
                    paramlist = dataset.params_list('plugin', plugintype)
                    if paramlist:
                        for paramid in paramlist:
                            dset_paramdata = dataset.params_i_get('plugin', plugintype, paramid)
                            paramval = xml_getvalue(xml_part, paramid, dset_paramdata[2])
                            fx_plugindata.param_add_dset(paramid, paramval, dataset, 'plugin', plugintype)
                    fx_plugindata.fxdata_add(int(xml_getvalue(xml_part, 'enabled', 1)), 1)
                    
                    fx_plugindata.to_cvpj(cvpj_l, pluginid)

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
        global dataset
        global cvpj_l
        #bytestream = open(input_file, 'r')
        #file_data = bytestream.read()
        parser = etree.XMLParser(recover=True, encoding='utf-8')
        xml_data = etree.parse(input_file, parser)
        xml_waveform = xml_data.getroot()

        cvpj_l = {}

        dataset = data_dataset.dataset('./data_dset/waveform.dset')

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

