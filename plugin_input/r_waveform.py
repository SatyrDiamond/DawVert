# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import colors
from objects import dv_dataset
from lxml import etree
import plugin_input
import json
import math

def xml_getvalue(xmltag, xmlname, fallbackval): 
    xmlval = xmltag.get(xmlname)
    if xmlval != None: return xmlval
    else: return fallbackval

def get_plugins(convproj_obj, xml_track, track_obj): 
    for xml_part in xml_track:
        if xml_part.tag == 'PLUGIN':
            plugintype = xml_part.get('type')
            plugin_xpos = xml_part.get('windowX')
            plugin_ypos = xml_part.get('windowY')

            if plugintype not in ['volume', 'level'] and plugintype != None:
                plugin_obj, pluginid = convproj_obj.add_plugin_genid('native-tracktion', plugintype)

                if plugin_xpos and plugin_ypos:
                    windata_obj = convproj_obj.window_data_add(['plugin',pluginid])
                    windata_obj.pos_x = plugin_xpos
                    windata_obj.pos_y = plugin_ypos

                paramlist = dataset.params_list('plugin', plugintype)
                if paramlist:
                    for paramid in paramlist:
                        dset_paramdata = dataset.params_i_get('plugin', plugintype, paramid)
                        paramval = xml_getvalue(xml_part, paramid, dset_paramdata[2])
                        plugin_obj.add_from_dset(paramid, paramval, dataset, 'plugin', plugintype)

                plugin_obj.fxdata_add(int(xml_getvalue(xml_part, 'enabled', 1)), 1)
                    
                track_obj.fxslots_audio.append(pluginid)

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
    def parse(self, convproj_obj, input_file, extra_param):
        global dataset
        global cvpj_l

        convproj_obj.type = 'r'
        convproj_obj.set_timings(4, True)

        parser = etree.XMLParser(recover=True, encoding='utf-8')
        xml_data = etree.parse(input_file, parser)
        xml_waveform = xml_data.getroot()

        dataset = dv_dataset.dataset('./data_dset/waveform.dset')

        convproj_obj.params.add('bpm', 120, 'float')

        tracknum = 1
        for xml_part in xml_waveform:

            if xml_part.tag == 'TEMPOSEQUENCE':
                TEMPO_parts = xml_part.findall('TEMPO')
                for TEMPO_part in TEMPO_parts:
                    TEMPO_startBeat = float(xml_getvalue(TEMPO_part, 'startBeat', '0.0'))
                    TEMPO_bpm = float(xml_getvalue(TEMPO_part, 'bpm', '120.0'))
                    if TEMPO_startBeat == 0: convproj_obj.params.add('bpm', TEMPO_bpm, 'float')

                TIMESIG_parts = xml_part.findall('TIMESIG')
                for TIMESIG_part in TIMESIG_parts:
                    TIMESIG_startBeat = float(xml_getvalue(TIMESIG_part, 'startBeat', '0.0'))
                    TIMESIG_numerator = int(xml_getvalue(TIMESIG_part, 'numerator', '4'))
                    TIMESIG_denominator = int(xml_getvalue(TIMESIG_part, 'denominator', '4'))
                    if TIMESIG_startBeat == 0: convproj_obj.timesig = [TIMESIG_numerator,TIMESIG_denominator]

            if xml_part.tag == 'MASTERPLUGINS':
                get_plugins(convproj_obj, xml_part, convproj_obj.track_master)

            if xml_part.tag == 'TRACK':
                cvpj_trackid = str(tracknum)
                track_obj = convproj_obj.track_add(j_wvtl_trackid, 'instrument')
                track_obj.visual.name = xml_getvalue(xml_part, 'name', '')
                track_colour = xml_getvalue(xml_part, 'colour', None)
                if track_colour != None: track_obj.visual.color = colors.hex_to_rgb_float(track_colour[2:])

                MIDICLIP_parts = xml_part.findall('MIDICLIP')
                for MIDICLIP_part in MIDICLIP_parts:
                    placement_obj = track_obj.pl_notes.add()
                    clip_start = float(xml_getvalue(MIDICLIP_part, 'start', '0'))
                    clip_length = float(xml_getvalue(MIDICLIP_part, 'length', '0'))
                    clip_offset = float(xml_getvalue(MIDICLIP_part, 'offset', '0'))
                    clip_loopStartBeats = float(xml_getvalue(MIDICLIP_part, 'loopStartBeats', '0'))
                    clip_loopLengthBeats = float(xml_getvalue(MIDICLIP_part, 'loopLengthBeats', '0'))

                    placement_obj.position = clip_start
                    placement_obj.duration = clip_length
                    if clip_loopStartBeats == 0 and clip_loopLengthBeats == 0:
                        if clip_start == 0:
                            self.cut_type = 'cut'
                            self.cut_data['start'] = clip_offset
                    else:
                        placement_obj.cut_loop_data(clip_offset, clip_loopStartBeats, clip_loopStartBeats+clip_loopLengthBeats)
    
                    MIDICLIP_SEQUENCES = MIDICLIP_part.findall('SEQUENCE')
                    for MIDICLIP_SEQUENCE in MIDICLIP_SEQUENCES:
                        for seqdata in MIDICLIP_SEQUENCE:
                            if seqdata.tag == 'NOTE':
                                cvpj_note_key = int(xml_getvalue(seqdata, 'p', '60'))-60
                                cvpj_note_pos = float(xml_getvalue(seqdata, 'b', '0'))
                                cvpj_note_dur = float(xml_getvalue(seqdata, 'l', '0'))
                                cvpj_note_vel = float(xml_getvalue(seqdata, 'v', '100'))/100
                                placement_obj.notelist.add_r(cvpj_note_pos, cvpj_note_dur, cvpj_note_key, cvpj_note_vel, {})

                get_plugins(convproj_obj, xml_part, track_obj)

                tracknum += 1

        convproj_obj.timesig = timesig
        convproj_obj.params.add('bpm', tempo, 'float')

        return json.dumps(cvpj_l)

