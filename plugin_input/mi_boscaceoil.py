# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from functions import placements
from functions import idvals
import plugin_input
import json

ceol_colors = {}
ceol_colors[0] = [0.23, 0.15, 0.93]
ceol_colors[1] = [0.61, 0.04, 0.94]
ceol_colors[2] = [0.82, 0.16, 0.23]
ceol_colors[3] = [0.82, 0.60, 0.16]
ceol_colors[4] = [0.21, 0.84, 0.14]
ceol_colors[5] = [0.07, 0.56, 0.91]

datapos = 0

def ceol_read():
    global datapos
    global ceol_data
    output = int(ceol_data[datapos])
    datapos += 1
    return output

class input_ceol(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'ceol'
    def getname(self): return 'Bosca Ceoil'
    def gettype(self): return 'mi'
    def supported_autodetect(self): return False
    def parse(self, input_file, extra_param):
        cvpj_l_instrument_data = {}
        cvpj_l_instrument_order = []
        cvpj_l_notelistindex = {}
        cvpj_l_playlist = {}

        idvals_inst_midi = idvals.parse_idvalscsv('idvals/midi_inst.csv')
        idvals_inst_bosca = idvals.parse_idvalscsv('idvals/boscaceoil_inst.csv')

        global datapos
        global ceol_data
        bio_mainfile = open(input_file, 'r')
        ceol_data = bio_mainfile.readline().split(',')

        ceol_basic_versionnum = ceol_read()
        print('[input-boscaceoil] Version Number: '+str(ceol_basic_versionnum))
        ceol_basic_swing = ceol_read()
        print('[input-boscaceoil] Swing: '+str(ceol_basic_swing))
        ceol_basic_effect = ceol_read()
        print('[input-boscaceoil] Effect: '+str(ceol_basic_effect))
        ceol_basic_effectvalue = ceol_read()
        print('[input-boscaceoil] Effect Value: '+str(ceol_basic_effectvalue))
        ceol_basic_bpm = ceol_read()
        print('[input-boscaceoil] BPM: '+str(ceol_basic_bpm))
        ceol_basic_patternlength = ceol_read()
        print('[input-boscaceoil] Pattern Length: '+str(ceol_basic_patternlength))
        ceol_basic_barlength = ceol_read()
        print('[input-boscaceoil] Bar Length: '+str(ceol_basic_barlength))
        print('[input-boscaceoil] ')

        ceol_numinstrument = ceol_read()

        t_key_offset = []

        for instnum in range(ceol_numinstrument):
            cvpj_instid = 'ceol_'+str(instnum).zfill(2)
            print('[input-boscaceoil] Instrument:', end=' ')

            ceol_inst_number = ceol_read()
            ceol_inst_type = ceol_read()
            ceol_inst_palette = ceol_read()
            ceol_inst_cutoff = ceol_read()
            ceol_inst_resonance = ceol_read()
            ceol_inst_volume = ceol_read()

            print('[input-boscaceoil]    Volume: '+str(ceol_inst_volume/256))
            print('[input-boscaceoil]    Type: '+str(ceol_inst_type))
            print('[input-boscaceoil]    Palette: '+str(ceol_inst_palette))
            print('[input-boscaceoil]    Cutoff/Reso: '+str(ceol_inst_cutoff)+'/'+str(ceol_inst_resonance))
            print('[input-boscaceoil] ')

            cvpj_inst = {}
            cvpj_inst["vol"] = ceol_inst_volume/256

            if ceol_inst_palette in ceol_colors:  cvpj_inst["color"] = ceol_colors[ceol_inst_palette]
            else: cvpj_inst["color"] = [0.55, 0.55, 0.55]

            cvpj_inst["instdata"] = {}
            cvpj_instdata = cvpj_inst["instdata"]
            cvpj_instdata['plugindata'] = {}

            if ceol_inst_number <= 127:
                cvpj_inst["name"] = idvals.get_idval(idvals_inst_midi, str(ceol_inst_number), 'name')
                cvpj_instdata['plugin'] = 'general-midi'
                cvpj_instdata['plugindata'] = {'bank':0, 'inst':ceol_inst_number}
            elif ceol_inst_number == 365: 
                cvpj_inst["name"] = 'MIDI Drums'
                cvpj_instdata['plugin'] = 'general-midi'
                cvpj_instdata['plugindata'] = {'bank':128, 'inst':0}
            else: 
                cvpj_inst["name"] = idvals.get_idval(idvals_inst_bosca, str(ceol_inst_number), 'name')
                cvpj_instdata['plugin'] = 'none'

            if ceol_inst_number == 363: t_key_offset.append(60)
            if ceol_inst_number == 364: t_key_offset.append(48)
            if ceol_inst_number == 365: t_key_offset.append(24)
            else: t_key_offset.append(0)

            cvpj_l_instrument_data[cvpj_instid] = cvpj_inst
            cvpj_l_instrument_order.append(cvpj_instid)

        ceol_numpattern = ceol_read()
        for patnum in range(ceol_numpattern):
            print('[input-boscaceoil] Pattern ' + str(patnum), end=', ')

            cvpj_notelist = []

            t_notepos_table = {}
            for t_notepos in range(ceol_basic_patternlength):
                t_notepos_table[t_notepos] = []

            cvpj_pat_id = 'ceol_'+str(patnum).zfill(3)
            ceol_pat_key = ceol_read()
            ceol_pat_scale = ceol_read()
            ceol_pat_instrument = ceol_read()
            print('Inst:'+str(ceol_pat_instrument), end=', ')
            ceol_pat_palette = ceol_read()
            print('Pal:'+str(ceol_pat_palette), end=', ')
            ceol_numnotes = ceol_read()
            print('#Notes:'+str(ceol_numnotes))

            print_notes = 0
            for _ in range(ceol_numnotes):
                ceol_nl_key = ceol_read()-60 + t_key_offset[ceol_pat_instrument]
                ceol_nl_len = ceol_read()
                ceol_nl_pos = ceol_read()
                ceol_read()
                t_notepos_table[ceol_nl_pos].append({'key': ceol_nl_key, 'instrument': 'ceol_'+str(ceol_pat_instrument).zfill(2), 'duration': ceol_nl_len})
                print_notes += 1

            ceol_recordfilter = ceol_read()
            if ceol_recordfilter == 1:
                for _ in range(32):
                    ceol_read()
                    ceol_read()
                    ceol_read()

            for position in t_notepos_table:
            	for note in t_notepos_table[position]:
            		cvpj_notelist.append(note | {'position': position})

            cvpj_pat = {}
            if ceol_pat_palette in ceol_colors: cvpj_pat["color"] = ceol_colors[ceol_pat_palette]
            else: cvpj_pat["color"] = [0.55, 0.55, 0.55]
            cvpj_pat["notelist"] = cvpj_notelist
            cvpj_pat["name"] = str(patnum)
            cvpj_l_notelistindex[cvpj_pat_id] = cvpj_pat

        cvpj_l_playlist['1'] = {'color': [0.43, 0.52, 0.55], 'placements_notes':[]}
        cvpj_l_playlist['2'] = {'color': [0.31, 0.40, 0.42], 'placements_notes':[]}
        cvpj_l_playlist['3'] = {'color': [0.43, 0.52, 0.55], 'placements_notes':[]}
        cvpj_l_playlist['4'] = {'color': [0.31, 0.40, 0.42], 'placements_notes':[]}
        cvpj_l_playlist['5'] = {'color': [0.43, 0.52, 0.55], 'placements_notes':[]}
        cvpj_l_playlist['6'] = {'color': [0.31, 0.40, 0.42], 'placements_notes':[]}
        cvpj_l_playlist['7'] = {'color': [0.43, 0.52, 0.55], 'placements_notes':[]}
        cvpj_l_playlist['8'] = {'color': [0.31, 0.40, 0.42], 'placements_notes':[]}

        ceol_arr_length = ceol_read()
        ceol_arr_loopstart = ceol_read()
        ceol_arr_loopend = ceol_read()

        for plpos in range(ceol_arr_length):
            for plnum in range(8):
                plpatnum = ceol_read()
                if plpatnum != -1:
                    cvpj_l_placement = {}
                    cvpj_l_placement['position'] = plpos*ceol_basic_patternlength
                    cvpj_l_placement['duration'] = ceol_basic_patternlength
                    cvpj_l_placement['fromindex'] = 'ceol_'+str(plpatnum).zfill(3)
                    cvpj_l_playlist[str(plnum+1)]['placements_notes'].append(cvpj_l_placement)

        print('[input-boscaceoil] ')

        for channelnum in cvpj_l_playlist:
        	print('[input-boscaceoil] Channel '+str(channelnum)+': ' + str(len(cvpj_l_playlist[channelnum]['placements_notes'])) + ' Placements')

        timesig = placements.get_timesig(ceol_basic_patternlength, ceol_basic_barlength)

        cvpj_l = {}
        cvpj_l['do_addwrap'] = True
        
        cvpj_l['use_instrack'] = False
        cvpj_l['use_fxrack'] = False
        cvpj_l['notelistindex'] = cvpj_l_notelistindex
        cvpj_l['instruments_data'] = cvpj_l_instrument_data
        cvpj_l['instruments_order'] = cvpj_l_instrument_order
        cvpj_l['playlist'] = cvpj_l_playlist
        cvpj_l['bpm'] = ceol_basic_bpm
        return json.dumps(cvpj_l)