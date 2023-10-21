# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import placement_data
from functions import note_data
from functions import song
from functions_tracks import tracks_r
from functions_tracks import tracks_master
from functions_tracks import auto_nopl
from functions_tracks import auto_data
import xml.etree.ElementTree as ET
import plugin_input
import json

def get_dur_len(xmltag): 
    pos = xmltag.get('td')
    dur = xmltag.get('d')

    if pos == None: pos = 0
    if dur == None: dur = 0

    pos = int(pos)
    dur = int(dur)

    return pos, dur



class input_cvpj_f(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'temper'
    def getname(self): return 'Temper'
    def gettype(self): return 'r'
    def getdawcapabilities(self): 
        return {
        #'track_hybrid': True
        'auto_nopl': True
        }
    def supported_autodetect(self): return True
    def detect(self, input_file):
        output = False
        try:
            tree = ET.parse(input_file)
            root = tree.getroot()
            if root.tag == "music-sequence": output = True
        except ET.ParseError: output = False
        return output
    def parse(self, input_file, extra_param):
        cvpj_l = {}

        temper_tempo, temper_num, temper_denum = 120, 4, 4

        temper_root = ET.parse(input_file).getroot()

        tracknum = 0

        for temper_part in temper_root:
            
            if temper_part.tag == 'meta-track':
                temper_tempo = temper_part.findall('tempo')
                temper_meter = temper_part.findall('meter')
                if temper_tempo:
                    temper_v_tempo = temper_tempo[0].get('bpm')
                    if temper_v_tempo != None: temper_tempo = temper_v_tempo
                if temper_meter:
                    temper_v_num = temper_meter[0].get('beats')
                    temper_v_denum = temper_meter[0].get('beat-value')
                    if temper_v_num != None: temper_num = temper_v_num
                    if temper_v_denum != None: temper_denum = temper_v_denum

            if temper_part.tag == 'track':
                tracknum += 1
                cvpj_trackid = 'track_'+str(tracknum)

                trackname = temper_part.get('name')
                trackphrases = temper_part.findall('phrase')

                tracks_r.track_create(cvpj_l, cvpj_trackid, 'instrument')
                tracks_r.track_visual(cvpj_l, cvpj_trackid, name=trackname, color=[0.66, 0.66, 0.73])

                mpl_pos = 0
                for trackphrase in trackphrases:
                    placement_pos, placement_dur = get_dur_len(trackphrase)

                    placement_pos = (mpl_pos+placement_pos)

                    cvpj_pldata = {}
                    cvpj_pldata["position"] = placement_pos/1679
                    cvpj_pldata["duration"] = placement_dur/1679

                    cvpj_notelist = []

                    ipl_pos = 0
                    for phrasepart in trackphrase:
                        phpa_pos, phpa_dur = get_dur_len(phrasepart)
                        iphpa_pos = ipl_pos+phpa_pos

                        if phrasepart.tag == 'note':
                            cvpj_note_pos = iphpa_pos/1679
                            cvpj_note_dur = phpa_dur/1679
                            cvpj_note_key = note_data.text_to_note(phrasepart.get('p'))
                            cvpj_note_vol = int(phrasepart.get('v'))/127

                            cvpj_notelist.append(
                                note_data.rx_makenote(cvpj_note_pos, cvpj_note_dur, cvpj_note_key, cvpj_note_vol, None)
                                )

                        ipl_pos += phpa_pos

                    cvpj_pldata["notelist"] = cvpj_notelist
                    tracks_r.add_pl(cvpj_l, cvpj_trackid, 'notes', cvpj_pldata)

                    mpl_pos += int(placement_pos)






        song.add_param(cvpj_l, 'bpm', temper_tempo)
        song.add_timesig(cvpj_l, temper_num, temper_denum)

        #temper_seq = temper_root.findall('head')[0]
        #temper_tracks = temper_seq.findall('music-sequence')


        return json.dumps(cvpj_l)

