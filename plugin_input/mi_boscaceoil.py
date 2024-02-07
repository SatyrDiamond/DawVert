# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects import convproj
from objects import idvals
from objects import dv_dataset
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

globalfxname = ['delay','chorus','reverb','distortion','low_boost','compressor','high_pass']

def calc_cutoff(in_val): return pow(in_val, 2)*(925/2048)

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
    def parse(self, convproj_obj, input_file, extra_param):
        global datapos
        global ceol_data
        
        # ---------- CVPJ Start ----------
        convproj_obj.type = 'mi'
        convproj_obj.set_timings(4, False)

        dataset = dv_dataset.dataset('./data_dset/boscaceoil.dset')
        dataset_midi = dv_dataset.dataset('./data_dset/midi.dset')
        idvals_inst_bosca = idvals.idvals('data_idvals/boscaceoil_inst.csv')

        # ---------- File ----------
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

        # ---------- Master FX ----------
        convproj_obj.track_master.params.add('vol', 1, 'float')
        convproj_obj.track_master.visual.color = [0.31373, 0.39608, 0.41569]

        if ceol_basic_effect == 0: #delay
            masterfx_plugindata = convproj_obj.add_plugin('master-effect', 'universal', 'delay-c')
            masterfx_plugindata.fxdata_add(1, 0.5)
            masterfx_plugindata.datavals.add('time_type', 'seconds')
            masterfx_plugindata.datavals.add('time', ((300*ceol_basic_effectvalue)/100)/1000 )
            masterfx_plugindata.datavals.add('feedback', 0.1)

        elif ceol_basic_effect == 1: #chorus
            masterfx_plugindata = convproj_obj.add_plugin('master-effect', 'simple', 'chorus')
            masterfx_plugindata.params.add('amount', ceol_basic_effectvalue/100, 'float')

        elif ceol_basic_effect == 2: #reverb
            masterfx_plugindata = convproj_obj.add_plugin('master-effect', 'simple', 'reverb')
            masterfx_plugindata.fxdata_add(1, (0.3)*(ceol_basic_effectvalue/100))

        elif ceol_basic_effect == 3: #distortion
            masterfx_plugindata = convproj_obj.add_plugin('master-effect', 'simple', 'distortion')
            masterfx_plugindata.params.add('amount', ceol_basic_effectvalue/100, 'float')

        elif ceol_basic_effect == 4: #low_boost
            masterfx_plugindata = convproj_obj.add_plugin('master-effect', 'simple', 'bassboost')
            masterfx_plugindata.fxdata_add(1, ceol_basic_effectvalue/100)

        elif ceol_basic_effect == 5: #compressor
            masterfx_plugindata = convproj_obj.add_plugin('master-effect', 'universal', 'compressor')
            masterfx_plugindata.params.add('attack', 0.1, 'float')
            masterfx_plugindata.params.add('pregain', 0, 'float')
            masterfx_plugindata.params.add('knee', 6, 'float')
            masterfx_plugindata.params.add('postgain', 0, 'float')
            masterfx_plugindata.params.add('ratio', 4, 'float')
            masterfx_plugindata.params.add('release', 0.5, 'float')
            masterfx_plugindata.params.add('threshold', -20, 'float')

        elif ceol_basic_effect == 6: #high_pass
            masterfx_plugindata = convproj_obj.add_plugin('master-effect', 'universal', 'eq-bands')
            sband = masterfx_plugindata.filter_add()
            sband.on = True
            sband.type = 'high_pass'
            sband.freq = calc_cutoff(ceol_basic_effectvalue)

        masterfx_plugindata.visual.name, masterfx_plugindata.visual.color = dataset.object_get_name_color('fx', str(globalfxname[ceol_basic_effect]))
        convproj_obj.track_master.fxslots_audio.append('master-effect')

        # ---------- Instruments ----------
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

            calc_initcutoffval = calc_cutoff(ceol_inst_cutoff)
            cvpj_instcolor = ceol_colors[ceol_inst_palette] if (ceol_inst_palette in ceol_colors) else [0.55, 0.55, 0.55]

            if ceol_inst_number <= 127:
                convproj_obj.instrument_midi_dset(cvpj_instid, cvpj_instid, 0, ceol_inst_number, False, dataset_midi, None, cvpj_instcolor)

            elif ceol_inst_number == 365: 
                inst_obj, plugin_obj = convproj_obj.instrument_midi_dset(cvpj_instid, cvpj_instid, 0, 0, True, dataset_midi, None, cvpj_instcolor)
                inst_obj.visual.name = 'MIDI Drums'

            else: 
                inst_obj, plugin_obj = convproj_obj.add_instrument_from_dset(cvpj_instid, cvpj_instid, dataset, dataset_midi, str(ceol_inst_number), None, cvpj_instcolor)
                valsoundid = idvals_inst_bosca.get_idval(str(ceol_inst_number), 'valsoundid')
                if valsoundid not in [None, '']: plugin_obj.type_set('valsound', valsoundid)
                else: plugin_obj.type_set('native-boscaceoil', ceol_inst_number)

            if ceol_inst_number == 363: t_key_offset.append(60)
            elif ceol_inst_number == 364: t_key_offset.append(48)
            elif ceol_inst_number == 365: t_key_offset.append(24)
            else: t_key_offset.append(0)

            inst_obj.params.add('vol', ceol_inst_volume/256, 'float')

            if ceol_inst_cutoff != 127:
                inst_filt_plugindata = convproj.cvpj_plugin()
                inst_filt_plugindata.type_set('universal', 'eq-bands')
                inst_filt_plugindata.filter_add()
                sband = inst_filt_plugindata.filters[-1]
                sband.on = True
                sband.type = 'low_pass'
                sband.freq = calc_initcutoffval
                sband.q = ceol_inst_resonance+1
                inst_obj.fxslots_audio

                fx_id = cvpj_instid+'_filter'
                convproj_obj.plugins[fx_id] = inst_filt_plugindata
                inst_obj.fxslots_audio.append(fx_id)

        # ---------- Patterns ----------
        ceol_numpattern = ceol_read()
        for patnum in range(ceol_numpattern):
            print('[input-boscaceoil] Pattern ' + str(patnum), end=', ')

            t_notepos_table = {}
            for t_notepos in range(ceol_basic_patternlength): t_notepos_table[t_notepos] = []

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
                t_notepos_table[ceol_nl_pos].append(['ceol_'+str(ceol_pat_instrument).zfill(2), ceol_nl_len, ceol_nl_key])
                print_notes += 1

            ceol_recordfilter = ceol_read()
            if ceol_recordfilter == 1:
                for _ in range(32):
                    ceol_read()
                    ceol_read()
                    ceol_read()

            nle_obj = convproj_obj.add_notelistindex(cvpj_pat_id)
            for n_pos in t_notepos_table:
                for note in t_notepos_table[n_pos]: nle_obj.notelist.add_m(note[0], n_pos, note[1], note[2], 1, {})
            nle_obj.visual.name = str(patnum)
            nle_obj.visual.color = ceol_colors[ceol_pat_palette] if ceol_pat_palette in ceol_colors else [0.55, 0.55, 0.55]

        for num in range(8):
            playlist_obj = convproj_obj.add_playlist(num, 0, False)
            playlist_obj.visual.color = [0.43, 0.52, 0.55] if (num % 2) == 0 else [0.31, 0.40, 0.42]

        # ---------- Loop ----------
        ceol_arr_length = ceol_read()
        ceol_arr_loopstart = ceol_read()
        ceol_arr_loopend = ceol_read()

        # ---------- Placement ----------
        for plpos in range(ceol_arr_length):
            for plnum in range(8):
                plpatnum = ceol_read()
                if plpatnum != -1:
                    cvpj_placement = convproj_obj.playlist[plnum].placements.add_notes()
                    cvpj_placement.fromindex = 'ceol_'+str(plpatnum).zfill(3)
                    cvpj_placement.position = plpos*ceol_basic_patternlength
                    cvpj_placement.duration = ceol_basic_patternlength

        # ---------- Output ----------
        convproj_obj.add_timesig_lengthbeat(ceol_basic_patternlength, ceol_basic_barlength)
        convproj_obj.params.add('bpm', ceol_basic_bpm, 'float')
        convproj_obj.do_actions.append('do_addloop')