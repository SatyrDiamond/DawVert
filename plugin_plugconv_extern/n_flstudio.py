# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv_extern

import struct
import os
import math
import lxml.etree as ET

from functions import note_data
from functions import data_bytes
from functions import xtramath
from functions import errorprint
from objects_convproj import wave

from functions_plugin_ext import plugin_vst2

from functions_plugin_ext import params_os_juicysfplugin
from functions_plugin_ext import params_os_dragonfly_reverb
from functions_plugin_ext import params_os_kickmess
from functions_plugin_ext import params_os_vital
from functions_plugin_ext import params_os_wolfshaper
from functions_plugin_ext import params_os_socalabs
from functions_plugin_ext import params_os_tal_chorus
from functions_plugin_ext_nonfree import params_nf_image_line

simsynth_shapes = {0.4: 'noise', 0.3: 'sine', 0.2: 'square', 0.1: 'saw', 0.0: 'triangle'}
wasp_shapes = {3: 'noise', 2: 'sine', 1: 'square', 0: 'saw'}

def simsynth_time(value): return pow(value*2, 3)
def simsynth_2time(value): return pow(value*2, 3)

def il_vst_chunk(i_type, i_data): 
    if i_type != 'name':
        if i_type != 0: return struct.pack('iii', i_type, len(i_data), 0)+i_data
        else: return bytes([0x00, 0x00, 0x00, 0x00])+i_data
    else:
        return bytes([0x01, 0x00, 0x00, 0x00])+data_bytes.makestring_fixedlen(i_data, 24)


def il_headersize(i_data): 
    return struct.pack('i', len(i_data))+i_data

shareware_il_plugnames = {
'autogun': 'IL Autogun',
'equo': 'IL EQUO',
'fruity delay 2': 'IL Delay',
'fruity delay bank': 'IL Delay Bank',
'fruity flangus': 'IL Flangus',
#'fruity love philter': 'IL Love Philter',
'fruity multiband compressor': 'IL Multiband Compressor',
#'fruity notebook': 'IL Notebook',
'fruity parametric eq': 'IL Parametric EQ',
'fruity parametric eq 2': 'IL Parametric EQ 2',
'fruity spectroman': 'IL Spectroman',
'fruity stereo enhancer': 'IL Stereo Enhancer',
'fruity vocoder': 'IL Vocoder',
#'fruity waveshaper': 'IL WaveShaper',
#'sytrus': 'IL Sytrus',
'directwave': 'DirectWave VSTi',
'drumaxx': 'IL Drumaxx',
'toxic biohazard': 'ToxicBiohazard',
'morphine': 'Morphine',
'poizone': 'PoiZone',
'sakura': 'Sakura',
'sawer': 'Sawer',
#'slicex': 'IL Slicex',
#'vocodex': 'IL Vocodex',
'wave candy': 'IL Wave Candy'
}

def get_flvst1(plugin_obj):
    fldata = params_nf_image_line.imageline_vststate()
    fldata.state_data = plugin_obj.rawdata_get('fl')
    fldata.startchunk_data = b'd\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    return fldata.write()

def get_flvst2(plugin_obj):
    fldata = params_nf_image_line.imageline_vststate()
    fldata.state_data = plugin_obj.rawdata_get('fl')
    fldata.otherp1_data[1] = 54
    fldata.otherp2_data = [41 for _ in range(16)]
    fldata.otherp3_data = [41 for _ in range(16)]
    fldata.startchunk_data = b'd\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00f\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xffg\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00P\x03\x00\x009\x02\x00\x00h\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    fldata.headertype = 1
    return fldata.write()

def get_sslf(plugin_obj):
    ilchunk = plugin_obj.rawdata_get('fl')
    dataout = b''
    for chunkdata in data_bytes.iff_read(ilchunk, 0):
        if chunkdata[0] == b'SSLF': dataout = chunkdata[1]
    return dataout

class plugconv(plugin_plugconv_extern.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv_ext'
    def getplugconvinfo(self): return ['native-flstudio', None], ['vst2'], 'flp'
    def convert(self, convproj_obj, plugin_obj, pluginid, dv_config, extplugtype, plugtransform):
        flpluginname = plugin_obj.plugin_subtype.lower()

        use_vst2 = 'vst2' in extplugtype
        use_nonfree = 'nonfree' in dv_config.flags_plugins
        use_shareware = 'shareware' in dv_config.flags_plugins

        # ---------------------------------------- morphine ----------------------------------------
        if flpluginname == 'drumaxx' and use_vst2 and use_shareware:
            if plugin_vst2.check_exists('id', 1145918257):
                plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'win', 1145918257, 'chunk', get_sslf(plugin_obj), None)
                return True
            else:
                errorprint.printerr('ext_notfound', ['Shareware VST2', 'IL Drumaxx'])

        #---------------------------------------- Fruit Kick ----------------------------------------
        elif flpluginname == 'fruit kick' and use_vst2:
            if plugin_vst2.check_exists('id', 934843292):
                print("[plug-conv] FL Studio to VST2: Fruit Kick > Kickmess:",pluginid)
                plugtransform.transform('./data_plugts/flstudio_vst.pltr', 'vst2_fruit_kick', convproj_obj, plugin_obj, pluginid, dv_config)

                data_kickmess = params_os_kickmess.kickmess_data()
                data_kickmess.set_param('pub', 'freq_start', plugtransform.get_storedval('freq_start'))
                data_kickmess.set_param('pub', 'freq_end', plugtransform.get_storedval('freq_end'))
                data_kickmess.set_param('pub', 'env_slope', plugtransform.get_storedval('env_slope'))
                data_kickmess.set_param('pub', 'freq_slope', 0.5)
                data_kickmess.set_param('pub', 'f_env_release', plugtransform.get_storedval('f_env_release'))
                data_kickmess.set_param('pub', 'phase_offs', plugtransform.get_storedval('phase_offs'))

                osc_dist = plugtransform.get_storedval('osc_dist')
                if osc_dist != 0:
                    data_kickmess.set_param('pub', 'dist_on', 1)
                    data_kickmess.set_param('pub', 'dist_start', osc_dist)
                    data_kickmess.set_param('pub', 'dist_end', osc_dist)
                data_kickmess.to_cvpj_vst2(convproj_obj, plugin_obj)
                plugin_obj.datavals.get('middlenotefix', -12)
                return True
            else: errorprint.printerr('ext_notfound', ['VST2', 'Kickmess'])

        # ---------------------------------------- FL Keys ----------------------------------------
        elif flpluginname == 'fl keys' and use_vst2:
            instrument = plugin_obj.datavals.get('instrument', 'mda Piano')
            if instrument in ['mda Piano', 'Grand Piano']:
                if plugin_vst2.check_exists('id', 1296318832):
                    print("[plug-conv] FL Studio to VST2: FL Keys > Piano [MDA]:",pluginid)
                    plugtransform.transform('./data_plugts/flstudio_vst.pltr', 'vst2_fl_keys_piano', convproj_obj, plugin_obj, pluginid, dv_config)
                    plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'any', 1296318832, 'param', None, 12)
                    return True
                else: errorprint.printerr('ext_notfound', ['VST2', 'Piano [MDA]'])
            if instrument == 'Rhodes (mda ePiano)':
                if plugin_vst2.check_exists('id', 1296318821):
                    print("[plug-conv] FL Studio to VST2: FL Keys > ePiano [MDA]:",pluginid)
                    plugtransform.transform('./data_plugts/flstudio_vst.pltr', 'vst2_fl_keys_epiano', convproj_obj, plugin_obj, pluginid, dv_config)
                    plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'any', 1296318821, 'param', None, 12)
                    return True
                else: errorprint.printerr('ext_notfound', ['VST2', 'ePiano [MDA]'])

        # ---------------------------------------- FL Keys ----------------------------------------
        elif flpluginname == 'fl slayer' and use_vst2 and use_shareware:
            if plugin_vst2.check_exists('id', 1397512498):
                print("[plug-conv] FL Studio to VST2: FL Slayer > ReFX Slayer 2:",pluginid)
                amp_type = plugin_obj.params.get('amp_type', 0).value
                cabinet = plugin_obj.params.get('cabinet', 0).value
                coil_type = plugin_obj.params.get('coil_type', 0).value
                damp = plugin_obj.params.get('damp', 0).value
                damp_vel = plugin_obj.params.get('damp_vel', 0).value
                drive = plugin_obj.params.get('drive', 0).value
                eq_high = plugin_obj.params.get('eq_high', 0).value
                eq_low = plugin_obj.params.get('eq_low', 0).value
                eq_mid = plugin_obj.params.get('eq_mid', 0).value
                feedback = plugin_obj.params.get('feedback', 0).value
                fret = plugin_obj.params.get('fret', 0).value
                fx_param1 = plugin_obj.params.get('fx_param1', 0).value
                fx_param2 = plugin_obj.params.get('fx_param2', 0).value
                fx_type = plugin_obj.params.get('fx_type', 0).value
                glissando = plugin_obj.params.get('glissando', 0).value
                harmonic = plugin_obj.params.get('harmonic', 0).value
                harmonic_vel = plugin_obj.params.get('harmonic_vel', 0).value
                hold = plugin_obj.params.get('hold', 0).value
                mode = plugin_obj.params.get('mode', 0).value
                pickup_position = plugin_obj.params.get('pickup_position', 0).value
                pitch_bend = plugin_obj.params.get('pitch_bend', 0).value
                presence = plugin_obj.params.get('presence', 0).value
                slap = plugin_obj.params.get('slap', 0).value
                string_type = plugin_obj.params.get('string_type', 0).value
                timing = plugin_obj.params.get('timing', 0).value
                tone = plugin_obj.params.get('tone', 0).value

                plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'win', 1397512498, 'param', None, 118)

                plugin_obj.params.add_named('ext_param_12', amp_type/5, 'float', 'Amp type')
                plugin_obj.params.add_named('ext_param_20', cabinet/5, 'float', 'Cab type')
                plugin_obj.params.add_named('ext_param_1', coil_type/2, 'float', 'Coils')
                plugin_obj.params.add_named('ext_param_115', damp/65535, 'float', 'Damping')
                plugin_obj.params.add_named('ext_param_116', damp_vel/65535, 'float', 'Vel->Damping')
                plugin_obj.params.add_named('ext_param_13', drive/65535, 'float', 'Drive')
                plugin_obj.params.add_named('ext_param_16', eq_low/65535, 'float', 'EQ low')
                plugin_obj.params.add_named('ext_param_17', eq_mid/65535, 'float', 'EQ mid')
                plugin_obj.params.add_named('ext_param_18', eq_high/65535, 'float', 'EQ high')
                plugin_obj.params.add_named('ext_param_15', feedback/65535, 'float', 'feedback')
                #fret
                #fx_param1
                #fx_param2
                #fx_type
                plugin_obj.params.add_named('ext_param_24', glissando, 'float', 'PB mode')
                plugin_obj.params.add_named('ext_param_23', pitch_bend/127, 'float', 'PB range')
                #harmonic
                #harmonic_vel
                #hold
                #mode
                plugin_obj.params.add_named('ext_param_2', pickup_position/65535, 'float', 'Pick pos')
                plugin_obj.params.add_named('ext_param_14', presence/65535, 'float', 'Presence')
                plugin_obj.params.add_named('ext_param_4', slap/65535, 'float', 'Slap lvl')
                plugin_obj.params.add_named('ext_param_0', string_type/8, 'float', 'String')
                plugin_obj.params.add_named('ext_param_22', timing/65535, 'float', 'timing')
                plugin_obj.params.add_named('ext_param_3', tone/65535, 'float', 'Tone')

                plugin_obj.params.add_named('ext_param_109', 1, 'float', 'dummy')
                plugin_obj.params.add_named('ext_param_110', 0, 'float', 'dummy')
                plugin_obj.params.add_named('ext_param_111', 1, 'float', 'dummy')
                plugin_obj.params.add_named('ext_param_112', 1, 'float', 'dummy')
                plugin_obj.params.add_named('ext_param_113', 1, 'float', 'dummy')
                plugin_obj.params.add_named('ext_param_25', 0.5, 'float', 'Gain')
                plugin_obj.params.add_named('ext_param_114', 0.5, 'float', 'Mst Vol')
                plugin_obj.params.add_named('ext_param_6', 0.75, 'float', 'Decay')
                plugin_obj.params.add_named('ext_param_7', 0, 'float', 'Release')
                plugin_obj.params.add_named('ext_param_26', 0.63, 'float', 'Body hue')
            else: errorprint.printerr('ext_notfound', ['Shareware VST2', 'ReFX Slayer 2'])

        # ---------------------------------------- DX10 ----------------------------------------
        elif flpluginname == 'fruity dx10' and use_vst2:
            if plugin_vst2.check_exists('id', 1296318840):
                print("[plug-conv] FL Studio to VST2: Fruity DX10 > DX10 [MDA]:",pluginid)
                plugtransform.transform('./data_plugts/flstudio_vst.pltr', 'vst2_fruity_dx10', convproj_obj, plugin_obj, pluginid, dv_config)
                plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'any', 1296318840, 'param', None, 16)
                return True
            else: errorprint.printerr('ext_notfound', ['VST2', 'DX10 [MDA]'])

        # ---------------------------------------- Harmless ----------------------------------------
        elif flpluginname == 'harmless' and use_vst2 and use_shareware:
            plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'win', 1229484653, 'chunk', get_flvst2(plugin_obj), None)

        # ---------------------------------------- Harmor ----------------------------------------
        elif flpluginname == 'harmor' and use_vst2 and use_shareware:
            plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'win', 1229483375, 'chunk', get_flvst2(plugin_obj), None)

        # ---------------------------------------- morphine ----------------------------------------
        elif flpluginname == 'morphine' and use_vst2 and use_shareware:
            if plugin_vst2.check_exists('id', 1299149382):
                plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'win', 1299149382, 'chunk', get_sslf(plugin_obj), None)
                return True
            else:
                errorprint.printerr('ext_notfound', ['Shareware VST2', 'Morphine'])

        # ---------------------------------------- poizone ----------------------------------------
        elif flpluginname == 'poizone' and use_vst2 and use_shareware:
            if plugin_vst2.check_exists('id', 1398893394):
                plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'win', 1398896471, 'chunk', get_sslf(plugin_obj), None)
                return True
            else:
                errorprint.printerr('ext_notfound', ['Shareware VST2', 'PoiZone'])

        # ---------------------------------------- sakura ----------------------------------------
        elif flpluginname == 'sakura' and use_vst2 and use_shareware:
            if plugin_vst2.check_exists('id', 1398893394):
                plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'win', 1398893394, 'chunk', get_sslf(plugin_obj), None)
                return True
            else:
                errorprint.printerr('ext_notfound', ['Shareware VST2', 'Sakura'])

        # ---------------------------------------- sawer ----------------------------------------
        elif flpluginname == 'sawer' and use_vst2 and use_shareware:
            if plugin_vst2.check_exists('id', 1398888274):
                plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'win', 1398888274, 'chunk', get_sslf(plugin_obj), None)
                return True
            else:
                errorprint.printerr('ext_notfound', ['Shareware VST2', 'Toxic Biohazard'])

        # ---------------------------------------- Sytrus ----------------------------------------
        elif flpluginname == 'sytrus' and use_vst2 and use_shareware:
            if plugin_vst2.check_exists('id', 1400468594):

                fldata = params_nf_image_line.imageline_vststate()
                fldata.state_data = plugin_obj.rawdata_get('fl')
                fldata.otherp1_data[1] = 19
                fldata.otherp1_data[1] = 18
                fldata.startchunk_data = b'd\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00f\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xffg\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00M\x03\x00\x00\xc2\x01\x00\x00h\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                fldata.headertype = 4

                plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'win', 1400468594, 'chunk', fldata.write(), None)
                return True
            else:
                errorprint.printerr('ext_notfound', ['Shareware VST2', 'Sytrus'])

        # ---------------------------------------- SimSynth ----------------------------------------
        elif flpluginname == 'simsynth' and use_vst2:
            if params_os_vital.checksupport(extplugtype):
                print("[plug-conv] FL Studio to VST2: SimSynth > Vital:",pluginid)
                params_vital = params_os_vital.vital_data(plugin_obj)

                for oscnum in range(3):
                    starttextparam = 'osc'+str(oscnum+1)
                    v_starttxt = 'osc_'+str(oscnum+1)
                    osc_shape = plugin_obj.params.get(starttextparam+'_shape', 0).value
                    osc_pw = plugin_obj.params.get(starttextparam+'_pw', 0).value
                    osc_o1 = int(plugin_obj.params.get(starttextparam+'_o1', 0).value)
                    osc_o2 = int(plugin_obj.params.get(starttextparam+'_o2', 0).value)
                    osc_on = float(plugin_obj.params.get(starttextparam+'_on', 0).value)
                    osc_crs = plugin_obj.params.get(starttextparam+'_crs', 0).value
                    osc_fine = plugin_obj.params.get(starttextparam+'_fine', 0).value
                    osc_lvl = plugin_obj.params.get(starttextparam+'_lvl', 0).value
                    osc_warm = int(plugin_obj.params.get(starttextparam+'_warm', 0).value)

                    vital_osc_shape = []

                    wave_obj = wave.cvpj_wave()
                    wave_obj.set_numpoints(2048)
                    wave_obj.add_wave(simsynth_shapes[osc_shape], 0.5, 1, 1)
                    if osc_o1: wave_obj.add_wave(simsynth_shapes[osc_shape], 0.5, 2, 0.5)
                    if osc_o2: wave_obj.add_wave(simsynth_shapes[osc_shape], 0.5, 4, 0.5)

                    params_vital.replacewave(oscnum, wave_obj.get_wave(2048))
                    params_vital.setvalue(v_starttxt+'_on', osc_on)
                    params_vital.setvalue(v_starttxt+'_transpose', (osc_crs-0.5)*48)
                    params_vital.setvalue(v_starttxt+'_tune', (osc_fine-0.5)*2)
                    params_vital.setvalue(v_starttxt+'_level', osc_lvl)
                    if osc_warm == 1:
                        params_vital.setvalue(v_starttxt+'_unison_detune', 2.2)
                        params_vital.setvalue(v_starttxt+'_unison_voices', 6)

                # ------------ AMP ------------
                params_vital.setvalue_timed('env_1_attack', simsynth_time(plugin_obj.params.get('amp_att', 0).value)*3.5)
                params_vital.setvalue_timed('env_1_decay', simsynth_2time(plugin_obj.params.get('amp_dec', 0).value)*3.5)
                params_vital.setvalue('env_1_sustain', plugin_obj.params.get('amp_sus', 0).value)
                params_vital.setvalue('env_1_attack_power', 0)
                params_vital.setvalue('env_1_decay_power', 0)
                params_vital.setvalue('env_1_release_power', 0)
                params_vital.setvalue_timed('env_1_release', simsynth_2time(plugin_obj.params.get('amp_rel', 0).value)*3.5)

                # ------------ SVF ------------
                params_vital.setvalue_timed('env_2_attack', simsynth_time(plugin_obj.params.get('svf_att', 0).value)*7)
                params_vital.setvalue_timed('env_2_decay', simsynth_2time(plugin_obj.params.get('svf_dec', 0).value)*7)
                params_vital.setvalue('env_2_sustain', plugin_obj.params.get('svf_sus', 0).value)
                params_vital.setvalue_timed('env_2_release', simsynth_2time(plugin_obj.params.get('svf_rel', 0).value)*7)

                outfilter = 100
                outfilter += (plugin_obj.params.get('svf_cut', 0).value-0.5)*40
                outfilter += (plugin_obj.params.get('svf_kb', 0).value-0.5)*10

                params_vital.setvalue('filter_fx_resonance', plugin_obj.params.get('svf_emph', 0).value*0.8)
                params_vital.setvalue('filter_fx_cutoff', outfilter)
                params_vital.setvalue('filter_fx_on', 1)
                params_vital.set_modulation(1, 'env_2', 'filter_fx_cutoff', plugin_obj.params.get('svf_env', 0).value*0.6, 0, 0, 0, 0)
                params_vital.set_modulation(2, 'env_1', 'osc_1_transpose', (plugin_obj.params.get('osc1_env', 0).value-0.5)*0.5, 0, 0, 0, 0)
                params_vital.set_modulation(3, 'env_1', 'osc_2_transpose', (plugin_obj.params.get('osc2_env', 0).value-0.5)*0.5, 0, 0, 0, 0)
                params_vital.set_modulation(4, 'env_1', 'osc_3_transpose', (plugin_obj.params.get('osc3_env', 0).value-0.5)*0.5, 0, 0, 0, 0)

                # ------------ Chorus ------------
                params_vital.setvalue('chorus_mod_depth', 0.35)
                params_vital.setvalue('chorus_delay_1', -9.5)
                params_vital.setvalue('chorus_delay_2', -9.0)
                if plugin_obj.params.get('chorus_on', 0).value == True: params_vital.setvalue('chorus_on', 1.0)
                
                params_vital.to_cvpj_any(convproj_obj, extplugtype)
                return True
            else: errorprint.printerr('ext_notfound', ['VST', 'Vital'])

        # ---------------------------------------- Toxic Biohazard ----------------------------------------
        elif flpluginname == 'toxic biohazard' and use_vst2 and use_shareware:
            if plugin_vst2.check_exists('id', 1416591412):
                plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'win', 1416591412, 'chunk', get_sslf(plugin_obj), None)
                return True
            else:
                errorprint.printerr('ext_notfound', ['Shareware VST2', 'Toxic Biohazard'])

        # ---------------------------------------- Wasp ----------------------------------------
        elif flpluginname == 'wasp' and use_vst2:
            if params_os_vital.checksupport(extplugtype):
                print("[plug-conv] FL Studio to VST2: WASP > Vital:",pluginid)
                params_vital = params_os_vital.vital_data(plugin_obj)
                params_vital.setvalue('polyphony', 1)
                params_vital.setvalue('portamento_force', 1)
                params_vital.setvalue('portamento_time', -5)
                params_vital.setvalue('legato', 1)

                fade12 = plugin_obj.params.get('12_fade', 0).value/128
                pw = plugin_obj.params.get('pw', 0).value

                for x in range(1,3):
                    v_starttxt = 'osc_'+str(x)

                    shape = int(plugin_obj.params.get(str(x)+'_shape', 0).value)
                    crs = ((plugin_obj.params.get(str(x)+'_crs', 0).value-64)/(64/36)).__floor__()
                    fine = (plugin_obj.params.get(str(x)+'_fine', 0).value-64)/(64/50)

                    wave_obj = wave.cvpj_wave()
                    wave_obj.set_numpoints(2048)
                    wave_obj.add_wave(wasp_shapes[shape], 0.5, 1, 1)
                    params_vital.replacewave(x-1, wave_obj.get_wave(2048))

                    params_vital.setvalue(v_starttxt+'_on', 1)
                    params_vital.setvalue(v_starttxt+'_transpose', crs)
                    params_vital.setvalue(v_starttxt+'_tune', fine/100)
                    params_vital.setvalue(v_starttxt+'_level', 1-fade12 if x == 1 else fade12)
                    params_vital.setvalue(v_starttxt+'_wave_frame', pw*2)

                    if x == 1:
                        amt3 = plugin_obj.params.get('3_amt', 0).value/128
                        shape3 = plugin_obj.params.get('3_shape', 0).value

                        wave_obj = wave.cvpj_wave()
                        wave_obj.set_numpoints(2048)
                        wave_obj.add_wave('square' if shape3 else 'saw', 0.5, 1, 1)
                        params_vital.replacewave(2, wave_obj.get_wave(2048))
                        params_vital.setvalue('osc_3_on', 1)
                        params_vital.setvalue('osc_3_transpose', crs-12)
                        params_vital.setvalue('osc_3_level', amt3/2)

                amp_A = (plugin_obj.params.get('amp_A', 0).value/64)**5
                amp_D = (plugin_obj.params.get('amp_D', 0).value/64)**5
                amp_S = plugin_obj.params.get('amp_S', 0).value/128
                amp_R = (plugin_obj.params.get('amp_R', 0).value/64)**5
                params_vital.setvalue_timed('env_1_attack', amp_A)
                params_vital.setvalue_timed('env_1_decay', amp_D)
                params_vital.setvalue('env_1_sustain', amp_S)
                params_vital.setvalue('env_1_attack_power', -5)
                params_vital.setvalue('env_1_decay_power', -5)
                params_vital.setvalue('env_1_release_power', -5)
                params_vital.setvalue_timed('env_1_release', amp_R)

                fil_A = (plugin_obj.params.get('fil_A', 0).value/64)**5
                fil_D = (plugin_obj.params.get('fil_D', 0).value/64)**5
                fil_S = plugin_obj.params.get('fil_S', 0).value/128
                fil_R = (plugin_obj.params.get('fil_R', 0).value/64)**5
                params_vital.setvalue_timed('env_2_attack', fil_A)
                params_vital.setvalue_timed('env_2_decay', fil_D)
                params_vital.setvalue('env_2_sustain', fil_S)
                params_vital.setvalue('env_2_attack_power', -5)
                params_vital.setvalue('env_2_decay_power', -5)
                params_vital.setvalue('env_2_release_power', -5)
                params_vital.setvalue_timed('env_2_release', fil_R)

                fil_cut = plugin_obj.params.get('fil_cut', 0).value/512
                fil_env = plugin_obj.params.get('fil_env', 0).value/128
                fil_kbtrack = plugin_obj.params.get('fil_kbtrack', 0).value
                fil_qtype = plugin_obj.params.get('fil_qtype', 0).value
                fil_res = plugin_obj.params.get('fil_res', 0).value/128

                params_vital.setvalue('filter_1_on', 1)
                params_vital.setvalue('filter_1_cutoff', (fil_cut**0.6)*128)
                params_vital.setvalue('filter_1_model', 3)
                params_vital.setvalue('filter_1_resonance', (fil_res**0.2)/1.3)
                params_vital.setvalue('filter_1_keytrack', fil_kbtrack/2)
                if fil_qtype == [1, 2, 3]: params_vital.setvalue('filter_1_style', 2)
                if fil_qtype == 3: 
                    params_vital.setvalue('filter_1_blend', 1)
                    params_vital.setvalue('filter_1_style', 2)
                if fil_qtype == 4: params_vital.setvalue('filter_1_blend', 1)
                if fil_qtype == 5: params_vital.setvalue('filter_1_blend', 2)

                params_vital.set_modulation(1, 'env_2', 'filter_1_cutoff', fil_env/2, 0, 1, 0, 0)

                params_vital.setvalue('random_1_style', 1)
                params_vital.setvalue('random_1_sync', 1)
                params_vital.setvalue('random_1_sync_type', 0)
                params_vital.setvalue('random_1_tempo', 13)

                params_vital.setvalue('random_2_style', 1)
                params_vital.setvalue('random_2_sync', 1)
                params_vital.setvalue('random_2_sync_type', 0)
                params_vital.setvalue('random_2_tempo', 13)

                modnum = 2

                for x in range(1,3):
                    w_starttxt = 'lfo'+str(x)+'_'
                    amt = (plugin_obj.params.get(w_starttxt+'amt', 0).value/128)**2
                    reset = plugin_obj.params.get(w_starttxt+'reset', 0).value
                    shape = plugin_obj.params.get(w_starttxt+'shape', 0).value
                    spd = (plugin_obj.params.get(w_starttxt+'spd', 0).value/128)**2
                    sync = plugin_obj.params.get(w_starttxt+'sync', 0).value
                    target = plugin_obj.params.get(w_starttxt+'target', 0).value

                    modto = []
                    if x == 1:
                        if target == 0: modto += [['osc_1_transpose', 0.1], ['osc_2_transpose', 0.1], ['osc_3_transpose', 0.1]]
                        if target == 1: modto += [['filter_1_cutoff', 0.5]]
                        if target == 2: modto += [['osc_1_wave_frame', 1], ['osc_2_wave_frame', 1], ['osc_3_wave_frame', 1]]

                    if x == 2:
                        if target == 0: modto += [['osc_1_transpose', 1], ['osc_3_transpose', 1]]
                        if target == 1: modto += [['osc_1_level', -1], ['osc_2_level', 1]]
                        if target == 2: modto += [['volume', 0.5]]

                    v_starttxt = 'lfo_'+str(x)

                    modfrom = 'lfo_'+str(x)

                    if shape == 0: params_vital.set_lfo(x, 2, [0.0,1.0,1.0,0.0], [0.0,0.0], False, 'Saw')
                    if shape == 1: params_vital.set_lfo(x, 5, [0.0,1.0,0.0,0.0,0.5,0.0,0.5,1.0,1.0,1.0], [0.0,0.0,0.0,0.0,0.0], False, 'Square')
                    if shape == 2: params_vital.set_lfo(x, 3, [0.0,1.0,0.5,0.0,1.0,1.0], [0.0,0.0,0.0], True, 'Sine')
                    if shape == 3: modfrom = 'random_'+str(x)

                    params_vital.setvalue(v_starttxt+'_sync', 0)
                    params_vital.setvalue(v_starttxt+'_frequency', -math.log2(1/((spd+0.1)*3)))

                    for m, v in modto:
                        params_vital.set_modulation(modnum, modfrom, m, v*amt, 0, 1, 0, 0)
                        modnum += 1

                params_vital.to_cvpj_any(convproj_obj, extplugtype)
                return True
            else: errorprint.printerr('ext_notfound', ['VST', 'Vital'])


        # ---------------------------------------- equo ----------------------------------------
        elif flpluginname == 'equo' and use_vst2 and use_shareware:
            if plugin_vst2.check_exists('id', 1162958159):
                plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'win', 1162958159, 'chunk', get_flvst1(plugin_obj), None)
                return True
            else:
                errorprint.printerr('ext_notfound', ['Shareware VST2', 'IL EQUO'])

        # ---------------------------------------- fruity bass boost ----------------------------------------
        elif flpluginname == 'fruity bass boost' and use_vst2:
            if plugin_vst2.check_exists('id', 2003265652):
                print("[plug-conv] FL Studio to VST2: Fruity Bass Boost > Weight [Airwindows]:",pluginid)
                plugtransform.transform('./data_plugts/flstudio_vst.pltr', 'vst2_fruity_bass_boost', convproj_obj, plugin_obj, pluginid, dv_config)
                plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'any', 2003265652, 'param', None, 2)
                return True
            else: errorprint.printerr('ext_notfound', ['VST2', 'Weight [Airwindows]'])

        # ---------------------------------------- Fruity Blood Overdrive ----------------------------------------
        elif flpluginname == 'fruity blood overdrive' and use_vst2:
            if use_vst2:
                if plugin_vst2.check_exists('id', 1684369011):
                    print("[plug-conv] FL Studio to VST2: Fruity Blood Overdrive > Density [Airwindows]:",pluginid)
                    plugtransform.transform('./data_plugts/flstudio_vst.pltr', 'vst2_fruity_blood_overdrive', convproj_obj, plugin_obj, pluginid, dv_config)
                    p_density = plugtransform.get_storedval('density')
                    p_hipass = plugtransform.get_storedval('hipass')
                    plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'any', 1684369011, 'chunk', struct.pack('<ffff', p_density, p_hipass, 1, 1), 0)
                    return True

                elif plugin_vst2.check_exists('id', 1112297284) and use_nonfree:
                    print("[plug-conv] FL Studio to VST2: Fruity Blood Overdrive > Blood Overdrive:",pluginid)
                    plugtransform.transform('./data_plugts/flstudio_vst.pltr', 'nf_vst2_fruity_blood_overdrive', convproj_obj, plugin_obj, pluginid, dv_config)
                    plugin_vst2.replace_data(convproj_obj, plugin_obj, 'name', 'win', 'BloodOverdrive', 'param', None, 6)
                    return True
                    
                if not use_nonfree:
                    errorprint.printerr('ext_notfound', ['VST2', 'Density [Airwindows]'])
                else:
                    errorprint.printerr('ext_notfound_multi', [['Shareware VST2', 'BloodOverdrive'], ['VST2', 'Density [Airwindows]']])

        # ---------------------------------------- fruity delay 2 ----------------------------------------
        elif flpluginname == 'fruity delay 2' and use_vst2 and use_shareware:
            if plugin_vst2.check_exists('id', 1178874454):
                plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'win', 1178874454, 'chunk', get_flvst1(plugin_obj), None)
                return True
            else: errorprint.printerr('ext_notfound', ['Shareware VST2', 'IL Delay'])

        # ---------------------------------------- fruity delay bank ----------------------------------------
        elif flpluginname == 'fruity delay bank' and use_vst2 and use_shareware:
            if plugin_vst2.check_exists('id', 1147945582):
                plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'win', 1147945582, 'chunk', get_flvst1(plugin_obj), None)
                return True
            else: errorprint.printerr('ext_notfound', ['Shareware VST2', 'IL Delay Bank'])

        # ---------------------------------------- Fruity Fast Dist ----------------------------------------
        elif flpluginname == 'fruity fast dist' and use_vst2:
            d_type = plugin_obj.params.get('type', 0).value
            if d_type == 0:
                if plugin_vst2.check_exists('id', 1835758713):
                    print("[plug-conv] FL Studio to VST2: Fruity Fast Dist > Mackity [Airwindows]:",pluginid)
                    plugtransform.transform('./data_plugts/flstudio_vst.pltr', 'vst2_fruity_fast_dist_type1', convproj_obj, plugin_obj, pluginid, dv_config)
                    plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'any', 1835758713, 'param', None, 3)
                    return True
                else: errorprint.printerr('ext_notfound', ['VST2', 'Mackity [Airwindows]'])
            if d_type == 1:
                if plugin_vst2.check_exists('id', 1835295055):
                    print("[plug-conv] FL Studio to VST2: Fruity Fast Dist > Overdrive [MDA]:",pluginid)
                    plugtransform.transform('./data_plugts/flstudio_vst.pltr', 'vst2_fruity_fast_dist_type2', convproj_obj, plugin_obj, pluginid, dv_config)
                    plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'any', 1835295055, 'param', None, 3)
                    return True
                else: errorprint.printerr('ext_notfound', ['VST2', 'Overdrive [MDA]'])

        # ---------------------------------------- fruity delay 2 ----------------------------------------
        elif flpluginname == 'fruity flangus' and use_vst2 and use_shareware:
            if plugin_vst2.check_exists('id', 1181509491):
                plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'win', 1181509491, 'chunk', get_flvst1(plugin_obj), None)
                return True
            else: errorprint.printerr('ext_notfound', ['Shareware VST2', 'IL Flangus'])

        # ---------------------------------------- fruity love philter ----------------------------------------
        elif flpluginname == 'fruity love philter' and use_vst2 and use_shareware:
            if plugin_vst2.check_exists('id', 1229737040):
                plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'win', 1229737040, 'chunk', get_flvst1(plugin_obj), None)
                return True
            else: errorprint.printerr('ext_notfound', ['Shareware VST2', 'IL Love Philter'])

        # ---------------------------------------- multiband compressor ----------------------------------------
        elif flpluginname == 'fruity multiband compressor' and use_vst2 and use_shareware:
            if plugin_vst2.check_exists('id', 1179476547):
                plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'win', 1179476547, 'chunk', get_flvst1(plugin_obj), None)
                return True
            else: errorprint.printerr('ext_notfound', ['Shareware VST2', 'IL Multiband Compressor'])

        # ---------------------------------------- gross beat ----------------------------------------
        elif flpluginname == 'gross beat' and use_vst2 and use_shareware:
            if plugin_vst2.check_exists('id', 1179545410):
                plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'win', 1229406821, 'chunk', get_flvst2(plugin_obj), None)
                return True
            else: errorprint.printerr('ext_notfound', ['Shareware VST2', 'IL Gross Beat'])

        # ---------------------------------------- hardcore ----------------------------------------
        elif flpluginname == 'hardcore' and use_vst2 and use_shareware:
            if plugin_vst2.check_exists('id', 1212371505):
                plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'win', 1212371505, 'chunk', get_sslf(plugin_obj), None)
                return True
            else:
                errorprint.printerr('ext_notfound', ['Shareware VST2', 'Hardcore'])

        # ---------------------------------------- maximus ----------------------------------------
        elif flpluginname == 'maximus' and use_vst2 and use_shareware:
            if plugin_vst2.check_exists('id', 1179545410):
                plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'win', 1229807992, 'chunk', get_flvst1(plugin_obj), None)
                return True
            else: errorprint.printerr('ext_notfound', ['Shareware VST2', 'IL Maximus'])

        # ---------------------------------------- notebook ----------------------------------------
        elif flpluginname == 'fruity notebook' and use_vst2 and use_shareware:
            if plugin_vst2.check_exists('id', 1179545410):
                plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'win', 1179545410, 'chunk', get_flvst1(plugin_obj), None)
                return True
            else: errorprint.printerr('ext_notfound', ['Shareware VST2', 'IL Notebook'])

        # ---------------------------------------- parametric eq ----------------------------------------
        elif flpluginname == 'fruity parametric eq' and use_vst2 and use_shareware:
            if plugin_vst2.check_exists('id', 1179665750):
                plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'win', 1179665750, 'chunk', get_flvst1(plugin_obj), None)
                return True
            else: errorprint.printerr('ext_notfound', ['Shareware VST2', 'IL Parametric EQ'])

        # ---------------------------------------- parametric eq 2 ----------------------------------------
        elif flpluginname == 'fruity parametric eq 2' and use_vst2 and use_shareware:
            if plugin_vst2.check_exists('id', 1346720050):
                plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'win', 1346720050, 'chunk', get_flvst1(plugin_obj), None)
                return True
            else: errorprint.printerr('ext_notfound', ['Shareware VST2', 'IL Parametric EQ 2'])

        # ---------------------------------------- fruity phase inverter ----------------------------------------
        elif flpluginname == 'fruity phase inverter' and use_vst2:
            if plugin_vst2.check_exists('id', 1718645881):
                print("[plug-conv] FL Studio to VST2: Fruity Phase Inverter > Airwindows Flipity:",pluginid)
                stateval = int((plugin_obj.params.get('state', 0).value/1024)*3)
                flipstate = 0
                if stateval == 1: flipstate = 1
                if stateval == 2: flipstate = 2
                outval = (flipstate/8)+0.01
                plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'any', 1718645881, 'chunk', struct.pack('<f', outval), 0)
                return True
            else: errorprint.printerr('ext_notfound', ['VST2', 'Flipity [Airwindows]'])

        # ---------------------------------------- fruity phaser ----------------------------------------
        elif flpluginname == 'fruity phaser' and use_vst2:
            if plugin_vst2.check_exists('id', 1095988560):
                print("[plug-conv] FL Studio to VST2: Fruity Phaser > SupaPhaser:",pluginid)
                plugtransform.transform('./data_plugts/flstudio_vst.pltr', 'vst2_fruity_phaser', convproj_obj, plugin_obj, pluginid, dv_config)
                plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'any', 1095988560, 'param', None, 16)
                return True
            else: errorprint.printerr('ext_notfound', ['VST2', 'SupaPhaser'])

        # ---------------------------------------- fruity reeverb ----------------------------------------
        elif flpluginname == 'fruity reeverb' and use_vst2:
            if plugin_vst2.check_exists('id', 1684435505):
                print("[plug-conv] FL Studio to VST2: Fruity Reeverb > Dragonfly Hall Reverb:",pluginid)
                plugtransform.transform('./data_plugts/flstudio_vst.pltr', 'vst2_fruity_reeverb', convproj_obj, plugin_obj, pluginid, dv_config)

                data_dragonfly = params_os_dragonfly_reverb.dragonfly_hall_data()
                data_dragonfly.set_param('low_cut',    plugtransform.get_storedval('low_cut'))
                data_dragonfly.set_param('high_cut',   plugtransform.get_storedval('high_cut'))
                data_dragonfly.set_param('size',       int(plugtransform.get_storedval('size')))
                data_dragonfly.set_param('delay',      plugtransform.get_storedval('delay'))
                data_dragonfly.set_param('diffuse',    plugtransform.get_storedval('diffuse'))
                data_dragonfly.set_param('decay',      plugtransform.get_storedval('decay'))
                data_dragonfly.set_param('high_xo',    plugtransform.get_storedval('high_xo'))
                data_dragonfly.set_param('dry_level',  plugtransform.get_storedval('dry_level'))
                data_dragonfly.set_param('late_level', plugtransform.get_storedval('late_level'))
                data_dragonfly.to_cvpj_vst2(convproj_obj, plugin_obj)
                return True
            else: errorprint.printerr('ext_notfound', ['VST2', 'Dragonfly Hall Reverb'])

        # ---------------------------------------- fruity reeverb 2 ----------------------------------------
        elif flpluginname == 'fruity reeverb 2' and use_vst2:
            if plugin_vst2.check_exists('id', 1684435505):
                print("[plug-conv] FL Studio to VST2: Fruity Reeverb 2 > Dragonfly Hall Reverb:",pluginid)
                plugtransform.transform('./data_plugts/flstudio_vst.pltr', 'vst2_fruity_reeverb_2', convproj_obj, plugin_obj, pluginid, dv_config)

                data_dragonfly = params_os_dragonfly_reverb.dragonfly_hall_data()
                data_dragonfly.set_param('low_cut',    plugtransform.get_storedval('low_cut'))
                data_dragonfly.set_param('high_cut',   plugtransform.get_storedval('high_cut'))
                data_dragonfly.set_param('size',       int(plugtransform.get_storedval('size')))
                data_dragonfly.set_param('delay',      plugtransform.get_storedval('delay'))
                data_dragonfly.set_param('diffuse',    plugtransform.get_storedval('diffuse'))
                data_dragonfly.set_param('decay',      plugtransform.get_storedval('decay'))
                data_dragonfly.set_param('high_xo',    plugtransform.get_storedval('high_xo'))
                data_dragonfly.set_param('low_mult',   plugtransform.get_storedval('low_mult'))
                data_dragonfly.set_param('dry_level',  plugtransform.get_storedval('dry_level'))
                data_dragonfly.set_param('late_level', plugtransform.get_storedval('late_level'))
                data_dragonfly.to_cvpj_vst2(convproj_obj, plugin_obj)
                return True
            else: errorprint.printerr('ext_notfound', ['VST2', 'Dragonfly Hall Reverb'])

        # ---------------------------------------- fruity spectroman ----------------------------------------
        elif flpluginname == 'fruity spectroman' and use_vst2:
            if use_shareware and plugin_vst2.check_exists('id', 1179873357):
                plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'win', 1179873357, 'chunk', get_flvst1(plugin_obj), None)
            elif plugin_vst2.check_exists('id', 1399874915):
                print("[plug-conv] FL Studio to VST2: Fruity Spectroman > SpectrumAnalyzer [SocaLabs]:",pluginid)
                plugtransform.transform('./data_plugts/flstudio_vst.pltr', 'vst2_fruity_spectroman', convproj_obj, plugin_obj, pluginid, dv_config)
                data_socalabs = params_os_socalabs.socalabs_data()

                data_socalabs.set_param("mode", plugtransform.get_storedval('mode'))
                data_socalabs.set_param("log", 1.0)
                data_socalabs.to_cvpj_vst2(convproj_obj, plugin_obj, 1399874915)
                return True
            else:
                if not use_shareware: errorprint.printerr('ext_notfound', ['VST2', 'SpectrumAnalyzer [SocaLabs]'])
                else: errorprint.printerr('ext_notfound_multi', [['Shareware VST2', 'IL Spectroman'], ['VST2', 'SpectrumAnalyzer [SocaLabs]']])

        # ---------------------------------------- fruity stereo enhancer ----------------------------------------
        elif flpluginname == 'fruity stereo enhancer' and use_vst2:
            if use_shareware and plugin_vst2.check_exists('id', 1179862358):
                plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'win', 1179862358, 'chunk', get_flvst1(plugin_obj), None)
            elif plugin_vst2.check_exists('id', 1282634853):
                print("[plug-conv] FL Studio to VST2: Fruity Stereo Enhancer > StereoProcessor [SocaLabs]:",pluginid)
                plugtransform.transform('./data_plugts/flstudio_vst.pltr', 'vst2_fruity_stereo_enhancer', convproj_obj, plugin_obj, pluginid, dv_config)
                data_socalabs = params_os_socalabs.socalabs_data()
                data_socalabs.set_param("width1", 0.5)
                data_socalabs.set_param("center1", plugtransform.get_storedval('stereo'))
                data_socalabs.set_param("pan1", 0.0)
                data_socalabs.set_param("rotation", 0.5)
                data_socalabs.set_param("pan2", plugtransform.get_storedval('pan'))
                data_socalabs.set_param("center2", 0.5)
                data_socalabs.set_param("width2", 0.5)
                data_socalabs.set_param("output", plugtransform.get_storedval('vol'))
                data_socalabs.to_cvpj_vst2(convproj_obj, plugin_obj, 1282634853)
                return True
            else: 
                if not use_shareware: errorprint.printerr('ext_notfound', ['VST2', 'StereoProcessor [SocaLabs]'])
                else: errorprint.printerr('ext_notfound_multi', [['Shareware VST2', 'IL Stereo Enhancer'], ['VST2', 'StereoProcessor [SocaLabs]']])

        # ---------------------------------------- fruity vocoder ----------------------------------------
        elif flpluginname == 'fruity vocoder' and use_vst2 and use_shareware:
            if plugin_vst2.check_exists('id', 1179407983):
                plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'win', 1179407983, 'chunk', get_flvst1(plugin_obj), None)
                return True
            else: 
                errorprint.printerr('ext_notfound', ['Shareware VST2', 'IL Vocoder'])

        # ---------------------------------------- fruity waveshaper ----------------------------------------
        elif flpluginname == 'fruity waveshaper':
            #if use_shareware and plugin_vst2.check_exists('id', 1229739891):
            #    plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'win', 1229739891, 'chunk', get_flvst1(plugin_obj), None)
            if params_os_wolfshaper.checksupport(extplugtype):
                print("[plug-conv] FL Studio to VST2: Fruity Waveshaper > Wolf Shaper:",pluginid)
                plugtransform.transform('./data_plugts/flstudio_vst.pltr', 'vst2_fruity_waveshaper', convproj_obj, plugin_obj, pluginid, dv_config)
                data_wolfshaper = params_os_wolfshaper.wolfshaper_data()
                data_wolfshaper.set_param('pregain',     plugtransform.get_storedval('preamp'))
                data_wolfshaper.set_param('wet',         plugtransform.get_storedval('wet'))
                data_wolfshaper.set_param('postgain',    plugtransform.get_storedval('postgain'))
                data_wolfshaper.set_param('bipolarmode', plugtransform.get_storedval('bipolarmode'))
                data_wolfshaper.set_param('removedc',    plugtransform.get_storedval('removedc'))
                data_wolfshaper.add_env(plugin_obj.env_points_get('shape'))
                data_wolfshaper.to_cvpj_any(convproj_obj, plugin_obj, extplugtype)
                return True
            else: 
                if not use_shareware: errorprint.printerr('ext_notfound', ['VST2', 'Wolf Shaper'])
                else: errorprint.printerr('ext_notfound_multi', [['Shareware VST2', 'IL Waveshaper'], ['VST2', 'Wolf Shaper']])

        # ---------------------------------------- Vintage Chorus ----------------------------------------
        elif flpluginname == 'vintage chorus' and use_vst2:
            if plugin_vst2.check_exists('id', 1665682481):
                c_mode = plugin_obj.params.get('mode', 0).value
                data_tal_c = params_os_tal_chorus.tal_chorus_data()
                data_tal_c.set_param('volume', 0.5)
                data_tal_c.set_param('drywet', 0.5)
                data_tal_c.set_param('stereowidth', 1.0)
                data_tal_c.set_param('chorus1enable', float(c_mode == 0))
                data_tal_c.set_param('chorus2enable', float(c_mode > 0))
                data_tal_c.to_cvpj_vst2(convproj_obj, plugin_obj)
                return True
            else: 
                errorprint.printerr('ext_notfound', ['VST2', 'TAL-Chorus-LX'])

        # ---------------------------------------- wave candy ----------------------------------------
        elif flpluginname == 'wave candy' and use_vst2 and use_shareware:
            if plugin_vst2.check_exists('id', 1229748067):
                plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'win', 1229748067, 'chunk', get_flvst1(plugin_obj), None)
                return True
            else: 
                errorprint.printerr('ext_notfound', ['Shareware VST2', 'IL Wave Candy'])