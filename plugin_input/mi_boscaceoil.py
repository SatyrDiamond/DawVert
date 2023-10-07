# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import placements
from functions import placement_data
from functions import idvals
from functions import plugins
from functions import song
from functions_tracks import fxslot
from functions_tracks import tracks_mi
from functions_tracks import tracks_master
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

globalfxname = ['delay','chorus','reverb','distortion','low_boost','compresser','high_pass']
globalfxname_vis = ['Delay','Chorus','Reverb','Distortion','Low Boost','Compresser','High Pass']

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
    def getdawcapabilities(self): 
        return {
        'track_lanes': True
        }
    def supported_autodetect(self): return False
    def parse(self, input_file, extra_param):
        global datapos
        global ceol_data
        
        cvpj_l = {}

        cvpj_l_keynames_data = {}

        idvals_inst_midi = idvals.parse_idvalscsv('data_idvals/midi_inst.csv')
        idvals_inst_bosca = idvals.parse_idvalscsv('data_idvals/boscaceoil_inst.csv')
        idvals_drumkit_midi = idvals.parse_idvalscsv('data_idvals/boscaceoil_drumkit_midi.csv')
        idvals_drumkit_simple = idvals.parse_idvalscsv('data_idvals/boscaceoil_drumkit_simple.csv')
        idvals_drumkit_sion = idvals.parse_idvalscsv('data_idvals/boscaceoil_drumkit_sion.csv')

        cvpj_l_keynames_data['drumkit_midi'] = idvals.idval2drumkeynames(idvals_drumkit_midi)
        cvpj_l_keynames_data['drumkit_simple'] = idvals.idval2drumkeynames(idvals_drumkit_simple)
        cvpj_l_keynames_data['drumkit_sion'] = idvals.idval2drumkeynames(idvals_drumkit_sion)

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

        tracks_master.create(cvpj_l, 1)
        tracks_master.visual(cvpj_l, name='Master', color=[0.31373, 0.39608, 0.41569])

        plugins.add_plug(cvpj_l, 'master-effect', 'native-boscaceoil', globalfxname[ceol_basic_effect])
        plugins.add_plug_param(cvpj_l, 'master-effect', 'power', ceol_basic_effectvalue, 'int', 'power')
        fxslot.insert(cvpj_l, ['master'], 'audio', 'master-effect')
        plugins.add_plug_fxvisual(cvpj_l, 'master-effect', globalfxname_vis[ceol_basic_effect], None)

        ceol_numinstrument = ceol_read()

        t_key_offset = []

        for instnum in range(ceol_numinstrument):
            cvpj_instid = 'ceol_'+str(instnum).zfill(2)
            print('[input-boscaceoil] Inst '+ str(instnum), end=', ')

            ceol_inst_number = ceol_read()
            ceol_inst_type = ceol_read()
            ceol_inst_palette = ceol_read()
            ceol_inst_cutoff = ceol_read()
            ceol_inst_resonance = ceol_read()
            ceol_inst_volume = ceol_read()

            print('Volume: '+str(ceol_inst_volume/256), end=', ')
            print('Type: '+str(ceol_inst_type), end=', ')
            print('Pal: '+str(ceol_inst_palette), end=', ')
            print('CutRes: '+str(ceol_inst_cutoff)+'/'+str(ceol_inst_resonance))

            initcutoffval = ceol_inst_cutoff
            calc_initcutoffval = pow(initcutoffval, 2)*(925/2048)

            cvpj_instvol = ceol_inst_volume/256

            if ceol_inst_palette in ceol_colors:  cvpj_instcolor = ceol_colors[ceol_inst_palette]
            else: cvpj_instcolor = [0.55, 0.55, 0.55]

            pluginid = plugins.get_id()
            if ceol_inst_number <= 127:
                cvpj_instname = idvals.get_idval(idvals_inst_midi, str(ceol_inst_number), 'name')
                plugins.add_plug_gm_midi(cvpj_l, pluginid, 0, ceol_inst_number)
            elif ceol_inst_number == 365: 
                cvpj_instname = 'MIDI Drums'
                plugins.add_plug_gm_midi(cvpj_l, pluginid, 128, 0)
            else: 
                cvpj_instname = idvals.get_idval(idvals_inst_bosca, str(ceol_inst_number), 'name')
                valsoundid = idvals.get_idval(idvals_inst_bosca, str(ceol_inst_number), 'valsoundid')
                if valsoundid not in [None, '']:
                    plugins.add_plug(cvpj_l, pluginid, 'valsound', valsoundid)
                else:
                    plugins.add_plug(cvpj_l, pluginid, 'native-boscaceoil', 'instrument')
                    plugins.add_plug_data(cvpj_l, pluginid, 'instrument', ceol_inst_number)

            plugins.add_filter(cvpj_l, pluginid, True, calc_initcutoffval, ceol_inst_resonance, "lowpass", None)

            if ceol_inst_number == 363: t_key_offset.append(60)
            if ceol_inst_number == 364: t_key_offset.append(48)
            if ceol_inst_number == 365: t_key_offset.append(24)
            else: t_key_offset.append(0)

            tracks_mi.inst_create(cvpj_l, cvpj_instid)
            tracks_mi.inst_visual(cvpj_l, cvpj_instid, name=cvpj_instname, color=cvpj_instcolor)
            tracks_mi.inst_pluginid(cvpj_l, cvpj_instid, pluginid)
            tracks_mi.inst_param_add(cvpj_l, cvpj_instid, 'vol', cvpj_instvol, 'float')

            if ceol_inst_number <= 127:
                tracks_mi.inst_dataval_add(cvpj_l, cvpj_instid, 'midi', 'output', {'program': ceol_inst_number})

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

            patcolor = {}
            if ceol_pat_palette in ceol_colors: patcolor = ceol_colors[ceol_pat_palette]
            else: patcolor = [0.55, 0.55, 0.55]

            tracks_mi.notelistindex_add(cvpj_l, cvpj_pat_id, cvpj_notelist)
            tracks_mi.notelistindex_visual(cvpj_l, cvpj_pat_id, name=str(patnum), color=patcolor)

        for num in range(8):
            tracks_mi.playlist_add(cvpj_l, num+1)
            if (num % 2) == 0: color = [0.43, 0.52, 0.55]
            else: color = [0.31, 0.40, 0.42]
            tracks_mi.playlist_visual(cvpj_l, num+1, color=color)

        ceol_arr_length = ceol_read()
        ceol_arr_loopstart = ceol_read()
        ceol_arr_loopend = ceol_read()

        for plpos in range(ceol_arr_length):
            for plnum in range(8):
                plpatnum = ceol_read()
                if plpatnum != -1:
                    cvpj_l_placement = placement_data.makepl_n_mi(plpos*ceol_basic_patternlength, ceol_basic_patternlength, 'ceol_'+str(plpatnum).zfill(3))
                    tracks_mi.add_pl(cvpj_l, plnum+1, 'notes', cvpj_l_placement)

        timesig = placements.get_timesig(ceol_basic_patternlength, ceol_basic_barlength)

        cvpj_l['do_addloop'] = True
        
        cvpj_l['use_instrack'] = False
        cvpj_l['use_fxrack'] = False
        
        cvpj_l['keynames_data'] = cvpj_l_keynames_data
        song.add_param(cvpj_l, 'bpm', ceol_basic_bpm)
        return json.dumps(cvpj_l)