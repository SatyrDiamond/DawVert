# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects import convproj
from objects import idvals
from objects import dv_dataset
from functions_plugin_cvpj import params_fm
from functions import xtramath
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
    def gettype(self): return 'mi'
    def getdawinfo(self, dawinfo_obj): 
        dawinfo_obj.name = 'Bosca Ceoil'
        dawinfo_obj.file_ext = 'ceol'
        dawinfo_obj.track_lanes = True
        dawinfo_obj.audio_filetypes = []
        dawinfo_obj.plugin_included = ['simple:chorus','simple:reverb','simple:distortion','simple:bassboost','universal:compressor','universal:filter','fm:opm','native-boscaceoil','universal:filter','midi']
    def supported_autodetect(self): return False
    def parse(self, convproj_obj, input_file, dv_config):
        global datapos
        global ceol_data
        
        # ---------- CVPJ Start ----------
        convproj_obj.type = 'mi'
        convproj_obj.set_timings(4, False)

        dataset = dv_dataset.dataset('./data_dset/boscaceoil.dset')
        dataset_midi = dv_dataset.dataset('./data_dset/midi.dset')
        idvals_inst_bosca = idvals.idvals('data_idvals/boscaceoil_inst.csv')
        idvals_valsound_opm = idvals.idvals('data_idvals/valsound_opm.csv')

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
            plugin_obj = convproj_obj.add_plugin('master-effect', 'universal', 'delay-c')
            plugin_obj.fxdata_add(1, 0.5)
            plugin_obj.datavals.add('traits', [])
            plugin_obj.datavals.add('c_fb', 0.1)
            timing_obj = plugin_obj.timing_add('center')
            timing_obj.set_seconds(((300*ceol_basic_effectvalue)/100)/1000)

        elif ceol_basic_effect == 1: #chorus
            plugin_obj = convproj_obj.add_plugin('master-effect', 'simple', 'chorus')
            plugin_obj.params.add('amount', ceol_basic_effectvalue/100, 'float')

        elif ceol_basic_effect == 2: #reverb
            plugin_obj = convproj_obj.add_plugin('master-effect', 'simple', 'reverb')
            plugin_obj.fxdata_add(1, (0.3)*(ceol_basic_effectvalue/100))

        elif ceol_basic_effect == 3: #distortion
            plugin_obj = convproj_obj.add_plugin('master-effect', 'simple', 'distortion')
            plugin_obj.params.add('amount', ceol_basic_effectvalue/100, 'float')

        elif ceol_basic_effect == 4: #low_boost
            plugin_obj = convproj_obj.add_plugin('master-effect', 'simple', 'bassboost')
            plugin_obj.fxdata_add(1, ceol_basic_effectvalue/100)

        elif ceol_basic_effect == 5: #compressor
            plugin_obj = convproj_obj.add_plugin('master-effect', 'universal', 'compressor')
            plugin_obj.params.add('attack', 0.1, 'float')
            plugin_obj.params.add('pregain', 0, 'float')
            plugin_obj.params.add('knee', 6, 'float')
            plugin_obj.params.add('postgain', 0, 'float')
            plugin_obj.params.add('ratio', 4, 'float')
            plugin_obj.params.add('release', 0.5, 'float')
            plugin_obj.params.add('threshold', -20, 'float')

        elif ceol_basic_effect == 6: #high_pass
            plugin_obj = convproj_obj.add_plugin('master-effect', 'universal', 'filter')
            plugin_obj.filter.on = True
            plugin_obj.filter.type = 'high_pass'
            plugin_obj.filter.freq = xtramath.midi_filter(ceol_basic_effectvalue/100)
            
        plugin_obj.role = 'effect'

        plugin_obj.visual.name, plugin_obj.visual.color = dataset.object_get_name_color('fx', str(globalfxname[ceol_basic_effect]))
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

            calc_initcutoffval = xtramath.midi_filter(ceol_inst_cutoff/100)
            cvpj_instcolor = ceol_colors[ceol_inst_palette] if (ceol_inst_palette in ceol_colors) else [0.55, 0.55, 0.55]

            if ceol_inst_number <= 127:
                inst_obj, plugin_obj = convproj_obj.instrument_midi_dset(cvpj_instid, cvpj_instid, 0, ceol_inst_number, False, dataset_midi, None, cvpj_instcolor)

            elif ceol_inst_number == 365: 
                inst_obj, plugin_obj = convproj_obj.instrument_midi_dset(cvpj_instid, cvpj_instid, 0, 0, True, dataset_midi, None, cvpj_instcolor)
                inst_obj.visual.name = 'MIDI Drums'

            else: 
                inst_obj, plugin_obj = convproj_obj.add_instrument_from_dset(cvpj_instid, cvpj_instid, dataset, dataset_midi, str(ceol_inst_number), None, cvpj_instcolor)
                valsoundid = idvals_inst_bosca.get_idval(str(ceol_inst_number), 'valsoundid')
                if valsoundid not in [None, '']: 
                    opm_main = [int(x) for x in idvals_valsound_opm.get_idval(valsoundid, 'opm_main').split(',')]
                    opm_op1 = [int(x) for x in idvals_valsound_opm.get_idval(valsoundid, 'opm_op1').split(',')]
                    opm_op2 = [int(x) for x in idvals_valsound_opm.get_idval(valsoundid, 'opm_op2').split(',')]
                    opm_op3 = [int(x) for x in idvals_valsound_opm.get_idval(valsoundid, 'opm_op3').split(',')]
                    opm_op4 = [int(x) for x in idvals_valsound_opm.get_idval(valsoundid, 'opm_op4').split(',')]
                    opm_ops = [opm_op1, opm_op2, opm_op3, opm_op4]

                    fmdata = params_fm.fm_data('opm')
                    fmdata.set_param('opmsk', 120)
                    fmdata.set_param('alg', opm_main[0])
                    fmdata.set_param('fb', opm_main[1])
                    for o in range(4):
                        print(opm_ops[o])
                        for n, t in enumerate(['ar','d1r','d2r','rr','d1l','tl','ks','ml','dt1','dt2']):
                            fmdata.set_op_param(o, t, opm_ops[o][n])
                    fmdata.to_cvpj(convproj_obj, cvpj_instid)

                else: 
                    plugin_obj.type_set('native-boscaceoil', str(ceol_inst_number))

            plugin_obj.role = 'synth'

            if ceol_inst_number == 363: t_key_offset.append(60)
            elif ceol_inst_number == 364: t_key_offset.append(48)
            elif ceol_inst_number == 365: t_key_offset.append(24)
            else: t_key_offset.append(0)

            inst_obj.params.add('vol', ceol_inst_volume/256, 'float')

            if ceol_inst_cutoff < 110:
                fx_id = cvpj_instid+'_filter'
                plugin_obj = convproj_obj.add_plugin(fx_id, 'universal', 'filter')
                plugin_obj.filter.on = True
                plugin_obj.filter.type = 'low_pass'
                plugin_obj.filter.freq = calc_initcutoffval
                plugin_obj.filter.q = ceol_inst_resonance+1
                plugin_obj.role = 'effect'
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

            for _ in range(ceol_numnotes):
                ceol_nl_key = ceol_read()-60 + t_key_offset[ceol_pat_instrument]
                ceol_nl_len = ceol_read()
                ceol_nl_pos = ceol_read()
                ceol_read()
                t_notepos_table[ceol_nl_pos].append(['ceol_'+str(ceol_pat_instrument).zfill(2), ceol_nl_len, ceol_nl_key])

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
            playlist_obj = convproj_obj.add_playlist(num, 1, True)
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
                    cvpj_placement = convproj_obj.playlist[plnum].placements.add_notes_indexed()
                    cvpj_placement.fromindex = 'ceol_'+str(plpatnum).zfill(3)
                    cvpj_placement.position = plpos*ceol_basic_patternlength
                    cvpj_placement.duration = ceol_basic_patternlength

        # ---------- Output ----------
        convproj_obj.add_timesig_lengthbeat(ceol_basic_patternlength, ceol_basic_barlength)
        convproj_obj.params.add('bpm', ceol_basic_bpm, 'float')
        convproj_obj.do_actions.append('do_addloop')