# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

import math
from functions import xtramath
from functions import note_data

def comp_threshold(i_val):
    return -math.log(i_val, 0.8913)

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['native-ableton', None, 'ableton'], ['universal', None, None], False, False
    def convert(self, convproj_obj, plugin_obj, pluginid, dv_config, plugtransform):


        if plugin_obj.plugin_subtype == 'AutoFilter':
            print('[plug-conv] Ableton to Universal: AutoFilter > Filter:',pluginid)
            
            comp_Cutoff = plugin_obj.params.get('Cutoff', 60).value-72
            comp_Resonance = plugin_obj.params.get('Resonance', 1).value
            comp_FilterType = plugin_obj.params.get('FilterType', 1).value
            comp_Slope = plugin_obj.params.get('Slope', 0).value
            comp_Resonance = 1+(comp_Resonance-0.12)

            plugin_obj.replace('universal', 'filter')
            plugin_obj.filter.on = True
            if comp_FilterType == 0: plugin_obj.filter.type = 'low_pass'
            if comp_FilterType == 1: plugin_obj.filter.type = 'high_pass'
            if comp_FilterType == 2: plugin_obj.filter.type = 'band_pass'
            if comp_FilterType == 3: plugin_obj.filter.type = 'notch'
            plugin_obj.filter.freq = comp_Cutoff
            plugin_obj.filter.q = comp_Resonance**3
            plugin_obj.filter.slope = 24 if comp_Slope else 12
            return 1
                
        if plugin_obj.plugin_subtype == 'Redux2':
            print('[plug-conv] Ableton to Universal: Redux2 > Bitcrush:',pluginid)
            plugtransform.transform('./data_plugts/ableton_univ.pltr', 'redux2', convproj_obj, plugin_obj, pluginid, dv_config)
            return 1

        if plugin_obj.plugin_subtype == 'Limiter':
            print('[plug-conv] Ableton to Universal: Limiter > Limiter:',pluginid)
            plugtransform.transform('./data_plugts/ableton_univ.pltr', 'limiter', convproj_obj, plugin_obj, pluginid, dv_config)
            return 1

        if plugin_obj.plugin_subtype == 'Gate':
            print('[plug-conv] Ableton to Universal: Gate > Gate:',pluginid)
            plugtransform.transform('./data_plugts/ableton_univ.pltr', 'gate', convproj_obj, plugin_obj, pluginid, dv_config)
            return 1

        if plugin_obj.plugin_subtype == 'FilterEQ3':
            print('[plug-conv] Ableton to Universal: FilterEQ3 > 3 Band EQ:',pluginid)
            plugtransform.transform('./data_plugts/ableton_univ.pltr', 'filtereq3', convproj_obj, plugin_obj, pluginid, dv_config)

        if plugin_obj.plugin_subtype == 'FrequencyShifter':
            p_Coarse = plugin_obj.params.get("Coarse", 0).value
            p_Fine = plugin_obj.params.get("Fine", 0).value
            p_ModulationMode = plugin_obj.params.get("ModulationMode", 0).value
            p_RingModCoarse = plugin_obj.params.get("RingModCoarse", 0).value

            if p_ModulationMode == 0:
                print('[plug-conv] Ableton to Universal: Frequency Shifter:',pluginid)
                f = p_Coarse+p_Fine
                plugin_obj.replace('universal', 'frequency_shifter')
                plugin_obj.params.add('pitch', f, 'float')
                return 1

            if p_ModulationMode == 1:
                print('[plug-conv] Ableton to Universal: Frequency Shifter > Ringmod:',pluginid)
                f = abs(p_RingModCoarse+p_Fine)
                plugin_obj.replace('universal', 'ringmod')
                plugin_obj.params.add('rate', f, 'float')
                lfo_obj = plugin_obj.lfo_add('amount')
                lfo_obj.time.set_hz(f)
                lfo_obj.amount = 1
                return 1

        if plugin_obj.plugin_subtype == 'Compressor2':
            comp_Model = plugin_obj.params.get('Model', 0).value
            modeldata = 'peak'
            if comp_Model == 1: modeldata = 'rms'
            if comp_Model != 2: 
                print('[plug-conv] Ableton to Universal: Compressor2 > Compressor:',pluginid)
                plugtransform.transform('./data_plugts/ableton_univ.pltr', 'compressor2_comp', convproj_obj, plugin_obj, pluginid, dv_config)
            else: 
                print('[plug-conv] Ableton to Universal: Compressor2 > Expander:',pluginid)
                plugtransform.transform('./data_plugts/ableton_univ.pltr', 'compressor2_expand', convproj_obj, plugin_obj, pluginid, dv_config)
            plugin_obj.datavals.add('mode', modeldata)
            return 1

        if plugin_obj.plugin_subtype == 'Eq8':
            print('[plug-conv] Ableton to Universal: EQ8 > EQ Bands:',pluginid)
            for band_num in range(8):
                groupname = ['main', 'b']
                abe_starttxt = "Bands."+str(band_num)+"/ParameterA/"
                abe_starttxt_alt = "Bands."+str(band_num)+"/ParameterB/"
                    
                band_mode = plugin_obj.params.get(abe_starttxt+"Mode", 0).value
                band_mode_alt = plugin_obj.params.get(abe_starttxt_alt+"Mode", 0).value

                cvpj_bandtype = ['high_pass', 'high_pass', 'low_shelf', 'peak', 'notch', 'high_shelf', 'low_pass', 'low_pass'][band_mode]
                cvpj_bandtype_alt = ['high_pass', 'high_pass', 'low_shelf', 'peak', 'notch', 'high_shelf', 'low_pass', 'low_pass'][band_mode_alt]

                cvpj_slope = 12 if band_mode not in [0,7] else 48
                cvpj_slope_alt = 12 if band_mode_alt not in [0,7] else 48

                filter_obj, filter_id = plugin_obj.eq_add()
                filter_obj.on = bool(plugin_obj.params.get(abe_starttxt+"IsOn", 0).value)
                filter_obj.freq = int(plugin_obj.params.get(abe_starttxt+"Freq", 0).value)
                filter_obj.gain = plugin_obj.params.get(abe_starttxt+"Gain", 0).value
                filter_obj.q = plugin_obj.params.get(abe_starttxt+"Q", 0).value
                filter_obj.type = cvpj_bandtype
                filter_obj.slope = cvpj_slope

                convproj_obj.automation.move(['plugin', pluginid, abe_starttxt+"IsOn"], ['n_filter', pluginid, filter_id, 'on'])
                convproj_obj.automation.move(['plugin', pluginid, abe_starttxt+"Freq"], ['n_filter', pluginid, filter_id, 'freq'])
                convproj_obj.automation.move(['plugin', pluginid, abe_starttxt+"Gain"], ['n_filter', pluginid, filter_id, 'gain'])
                convproj_obj.automation.move(['plugin', pluginid, abe_starttxt+"Q"], ['n_filter', pluginid, filter_id, 'q'])

                filter_obj, filter_id = plugin_obj.named_eq_add('alt')
                filter_obj.on = bool(plugin_obj.params.get(abe_starttxt_alt+"IsOn", 0).value)
                filter_obj.freq = int(plugin_obj.params.get(abe_starttxt_alt+"Freq", 0).value)
                filter_obj.gain = plugin_obj.params.get(abe_starttxt_alt+"Gain", 0).value
                filter_obj.q = plugin_obj.params.get(abe_starttxt_alt+"Q", 0).value
                filter_obj.type = cvpj_bandtype_alt
                filter_obj.slope = cvpj_slope_alt

                convproj_obj.automation.move(['plugin', pluginid, abe_starttxt_alt+"IsOn"], ['n_filter', pluginid, filter_id, 'on'])
                convproj_obj.automation.move(['plugin', pluginid, abe_starttxt_alt+"Freq"], ['n_filter', pluginid, filter_id, 'freq'])
                convproj_obj.automation.move(['plugin', pluginid, abe_starttxt_alt+"Gain"], ['n_filter', pluginid, filter_id, 'gain'])
                convproj_obj.automation.move(['plugin', pluginid, abe_starttxt_alt+"Q"], ['n_filter', pluginid, filter_id, 'q'])

            plugin_obj.replace('universal', 'eq-bands')
            return 1

        return 2