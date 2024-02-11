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
from objects_convproj import wave

from functions_plugin_ext import plugin_vst2

from functions_plugin_ext import params_os_dragonfly_reverb
from functions_plugin_ext import params_os_kickmess
from functions_plugin_ext import params_os_vital
from functions_plugin_ext import params_os_wolfshaper
from functions_plugin_ext import params_os_socalabs

from objects import plugts

simsynth_shapes = {0.4: 'noise', 0.3: 'sine', 0.2: 'square', 0.1: 'saw', 0.0: 'triangle'}

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
'drumaxx': 'Drumaxx',
'toxic biohazard': 'ToxicBiohazard',
'morphine': 'Morphine',
'poizone': 'PoiZone',
'sakura': 'Sakura',
'sawer': 'Sawer',
#'slicex': 'IL Slicex',
#'vocodex': 'IL Vocodex',
'wave candy': 'IL Wave Candy'
}

loaded_plugtransform = False

class plugconv(plugin_plugconv_extern.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv_ext'
    def getplugconvinfo(self): return ['native-flstudio', None], ['vst2'], 'flp'
    def convert(self, convproj_obj, plugin_obj, pluginid, extra_json, extplugtype):
        global loaded_plugtransform
        global plugts_obj
        flpluginname = plugin_obj.plugin_subtype.lower()

        if loaded_plugtransform == False:
            plugts_obj = plugts.plugtransform()
            plugts_obj.load_file('./data_plugts/flstudio_vst2.pltr')
            loaded_plugtransform = True

        if 'nonfree-plugins' in extra_json:
            if flpluginname == 'fruity blood overdrive' and extplugtype == 'vst2':
                print("[plug-conv] FL Studio to VST2: Fruity Blood Overdrive > Blood Overdrive:",pluginid)
                plugts_obj.transform('vst2_fruity_blood_overdrive', convproj_obj, plugin_obj, pluginid, extra_json)
                plugin_vst2.replace_data(convproj_obj, plugin_obj, 'name', 'win', 'BloodOverdrive', 'param', None, 6)
                return True
            
            elif flpluginname == 'tuner' and extplugtype == 'vst2':
                print("[plug-conv] FL Studio to VST2: Tuner > GTune:",pluginid)
                plugts_obj.transform('vst2_tuner', convproj_obj, plugin_obj, pluginid, extra_json)
                plugin_vst2.replace_data(convproj_obj, plugin_obj, 'name', 'win', 'GTune', 'param', None, 1)
                return True


        if 'shareware-plugins' in extra_json:
            if flpluginname in shareware_il_plugnames and extplugtype == 'vst2':
                print("[plug-conv] FL Studio to VST2: "+plugin_obj.plugin_subtype+":",pluginid)

                ilchunk = plugin_obj.rawdata_get('fl')

                dataout = None

                if flpluginname in ['equo', 'fruity delay 2', 'fruity delay bank', 'fruity flangus', 'fruity love philter'
                                    'fruity multiband compressor', 'fruity notebook', 'fruity parametric eq 2', 'fruity parametric eq',
                                    'fruity spectroman','fruity stereo enhancer','fruity vocoder','fruity waveshaper', 'wave candy'
                                    ]: 

                    subdata = il_vst_chunk(1, bytes([0xFF])*512)
                    subdata += il_vst_chunk(2, bytes([0xFF])*64)
                    subdata += il_vst_chunk(3, bytes([0xFF])*64)

                    dataout = b'\xFA\xFF\xFF\x7F\x01\x00\x00\x00\x00'
                    headerpart = b'd\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

                    dataout += il_headersize(il_vst_chunk(5, headerpart))
                    dataout += il_vst_chunk('name', 'Defualt')
                    dataout += il_vst_chunk(1, subdata)
                    dataout += il_vst_chunk(0, ilchunk)

                elif flpluginname in ['toxic biohazard', 'sawer', 'sakura', 'poizone', 'morphine', 'drumaxx']:
                    dataout = b''
                    for chunkdata in data_bytes.riff_read(ilchunk, 0):
                        if chunkdata[0] == b'SSLF': dataout = chunkdata[1]

                elif flpluginname in ['directwave']:
                    dataout = ilchunk

                if dataout != None:
                    plugin_vst2.replace_data(convproj_obj, plugin_obj, 'name', 'win', shareware_il_plugnames[flpluginname], 'chunk', dataout, None)

                return True

        #---------------------------------------- Fruit Kick ----------------------------------------
        if flpluginname == 'fruit kick' and extplugtype == 'vst2':
            print("[plug-conv] FL Studio to VST2: Fruit Kick > Kickmess:",pluginid)
            plugts_obj.transform('vst2_fruit_kick', convproj_obj, plugin_obj, pluginid, extra_json)

            data_kickmess = params_os_kickmess.kickmess_data()
            data_kickmess.set_param('pub', 'freq_start', plugts_obj.get_storedval('freq_start'))
            data_kickmess.set_param('pub', 'freq_end', plugts_obj.get_storedval('freq_end'))
            data_kickmess.set_param('pub', 'env_slope', plugts_obj.get_storedval('env_slope'))
            data_kickmess.set_param('pub', 'freq_slope', 0.5)
            data_kickmess.set_param('pub', 'f_env_release', plugts_obj.get_storedval('f_env_release'))
            data_kickmess.set_param('pub', 'phase_offs', plugts_obj.get_storedval('phase_offs'))

            osc_dist = plugts_obj.get_storedval('osc_dist')
            if osc_dist != 0:
                data_kickmess.set_param('pub', 'dist_on', 1)
                data_kickmess.set_param('pub', 'dist_start', osc_dist)
                data_kickmess.set_param('pub', 'dist_end', osc_dist)
            data_kickmess.to_cvpj_vst2(convproj_obj, plugin_obj)
            plugin_obj.datavals.get('middlenotefix', -12)

            return True

        # ---------------------------------------- SimSynth ----------------------------------------
        elif flpluginname == 'simsynth' and extplugtype == 'vst2':
            print("[plug-conv] FL Studio to VST2: SimSynth > Vital:",pluginid)
            params_vital = params_os_vital.vital_data(plugin_obj)

            #plugin_obj.params.get(in_data[0], 0).value 
            for oscnum in range(3):
                starttextparam = 'osc'+str(oscnum+1)
                starttextparam_vital = 'osc_'+str(oscnum+1)
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
                params_vital.setvalue(starttextparam_vital+'_on', osc_on)
                params_vital.setvalue(starttextparam_vital+'_transpose', (osc_crs-0.5)*48)
                params_vital.setvalue(starttextparam_vital+'_tune', (osc_fine-0.5)*2)
                params_vital.setvalue(starttextparam_vital+'_level', osc_lvl)
                if osc_warm == 1:
                    params_vital.setvalue(starttextparam_vital+'_unison_detune', 2.2)
                    params_vital.setvalue(starttextparam_vital+'_unison_voices', 6)

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
            
            params_vital.to_cvpj_vst2(convproj_obj)
            return True

        # ---------------------------------------- DX10 ----------------------------------------
        elif flpluginname == 'fruity dx10' and extplugtype == 'vst2':
            print("[plug-conv] FL Studio to VST2: Fruity DX10 > mda DX10:",pluginid)
            plugts_obj.transform('vst2_fruity_dx10', convproj_obj, plugin_obj, pluginid, extra_json)
            plugin_vst2.replace_data(convproj_obj, plugin_obj, 'name', 'any', 'DX10', 'param', None, 16)
            return True

        # ---------------------------------------- fruity bass boost ----------------------------------------
        elif flpluginname == 'fruity bass boost' and extplugtype == 'vst2':
            print("[plug-conv] FL Studio to VST2: Fruity Bass Boost > Airwindows Weight:",pluginid)
            plugts_obj.transform('vst2_fruity_bass_boost', convproj_obj, plugin_obj, pluginid, extra_json)
            plugin_vst2.replace_data(convproj_obj, plugin_obj, 'name', 'any', 'Weight', 'param', None, 2)
            return True

        # ---------------------------------------- fruity phaser ----------------------------------------
        elif flpluginname == 'fruity phaser' and extplugtype == 'vst2':
            print("[plug-conv] FL Studio to VST2: Fruity Phaser > SupaPhaser:",pluginid)
            plugts_obj.transform('vst2_fruity_phaser', convproj_obj, plugin_obj, pluginid, extra_json)
            plugin_vst2.replace_data(convproj_obj, plugin_obj, 'name', 'any', 'SupaPhaser', 'param', None, 16)
            return True

        # ---------------------------------------- fruity spectroman ----------------------------------------
        elif flpluginname == 'fruity spectroman' and extplugtype == 'vst2':
            print("[plug-conv] FL Studio to VST2: Fruity Spectroman > SocaLabs's SpectrumAnalyzer:",pluginid)
            plugts_obj.transform('vst2_fruity_spectroman', convproj_obj, plugin_obj, pluginid, extra_json)
            data_socalabs = params_os_socalabs.socalabs_data()

            data_socalabs.set_param("mode", plugts_obj.get_storedval('mode'))
            data_socalabs.set_param("log", 1.0)
            data_socalabs.to_cvpj_vst2(convproj_obj, plugin_obj, 1399874915)
            return True

        # ---------------------------------------- fruity waveshaper ----------------------------------------
        elif flpluginname == 'fruity waveshaper' and extplugtype == 'vst2':
            print("[plug-conv] FL Studio to VST2: Fruity Waveshaper > Wolf Shaper:",pluginid)
            plugts_obj.transform('vst2_fruity_waveshaper', convproj_obj, plugin_obj, pluginid, extra_json)
            data_wolfshaper = params_os_wolfshaper.wolfshaper_data()
            data_wolfshaper.set_param('pregain',     plugts_obj.get_storedval('preamp'))
            data_wolfshaper.set_param('wet',         plugts_obj.get_storedval('wet'))
            data_wolfshaper.set_param('postgain',    plugts_obj.get_storedval('postgain'))
            data_wolfshaper.set_param('bipolarmode', plugts_obj.get_storedval('bipolarmode'))
            data_wolfshaper.set_param('removedc',    plugts_obj.get_storedval('removedc'))
            data_wolfshaper.add_env(plugin_obj.env_points_get('shape'))
            data_wolfshaper.to_cvpj_vst2(convproj_obj, plugin_obj)
            return True

        # ---------------------------------------- fruity stereo enhancer ----------------------------------------
        elif flpluginname == 'fruity stereo enhancer' and extplugtype == 'vst2':
            print("[plug-conv] FL Studio to VST2: Fruity Stereo Enhancer > SocaLabs's StereoProcessor:",pluginid)
            plugts_obj.transform('vst2_fruity_stereo_enhancer', convproj_obj, plugin_obj, pluginid, extra_json)
            data_socalabs = params_os_socalabs.socalabs_data()
            data_socalabs.set_param("width1", 0.5)
            data_socalabs.set_param("center1", plugts_obj.get_storedval('stereo'))
            data_socalabs.set_param("pan1", 0.0)
            data_socalabs.set_param("rotation", 0.5)
            data_socalabs.set_param("pan2", plugts_obj.get_storedval('pan'))
            data_socalabs.set_param("center2", 0.5)
            data_socalabs.set_param("width2", 0.5)
            data_socalabs.set_param("output", plugts_obj.get_storedval('vol'))
            data_socalabs.to_cvpj_vst2(convproj_obj, plugin_obj, 1282634853)
            return True

        # ---------------------------------------- fruity reeverb ----------------------------------------
        elif flpluginname == 'fruity reeverb' and extplugtype == 'vst2':

            print("[plug-conv] FL Studio to VST2: Fruity Reeverb > Dragonfly Hall Reverb:",pluginid)
            plugts_obj.transform('vst2_fruity_reeverb', convproj_obj, plugin_obj, pluginid, extra_json)

            data_dragonfly = params_os_dragonfly_reverb.dragonfly_hall_data()
            data_dragonfly.set_param('low_cut',    plugts_obj.get_storedval('low_cut'))
            data_dragonfly.set_param('high_cut',   plugts_obj.get_storedval('high_cut'))
            data_dragonfly.set_param('size',       int(plugts_obj.get_storedval('size')))
            data_dragonfly.set_param('delay',      plugts_obj.get_storedval('delay'))
            data_dragonfly.set_param('diffuse',    plugts_obj.get_storedval('diffuse'))
            data_dragonfly.set_param('decay',      plugts_obj.get_storedval('decay'))
            data_dragonfly.set_param('high_xo',    plugts_obj.get_storedval('high_xo'))
            data_dragonfly.set_param('dry_level',  plugts_obj.get_storedval('dry_level'))
            data_dragonfly.set_param('late_level', plugts_obj.get_storedval('late_level'))
            data_dragonfly.to_cvpj_vst2(convproj_obj, plugin_obj)

        # ---------------------------------------- fruity reeverb ----------------------------------------
        elif flpluginname == 'fruity reeverb 2' and extplugtype == 'vst2':

            print("[plug-conv] FL Studio to VST2: Fruity Reeverb 2 > Dragonfly Hall Reverb:",pluginid)
            plugts_obj.transform('vst2_fruity_reeverb_2', convproj_obj, plugin_obj, pluginid, extra_json)

            data_dragonfly = params_os_dragonfly_reverb.dragonfly_hall_data()
            data_dragonfly.set_param('low_cut',    plugts_obj.get_storedval('low_cut'))
            data_dragonfly.set_param('high_cut',   plugts_obj.get_storedval('high_cut'))
            data_dragonfly.set_param('size',       int(plugts_obj.get_storedval('size')))
            data_dragonfly.set_param('delay',      plugts_obj.get_storedval('delay'))
            data_dragonfly.set_param('diffuse',    plugts_obj.get_storedval('diffuse'))
            data_dragonfly.set_param('decay',      plugts_obj.get_storedval('decay'))
            data_dragonfly.set_param('high_xo',    plugts_obj.get_storedval('high_xo'))
            data_dragonfly.set_param('low_mult',   plugts_obj.get_storedval('low_mult'))
            data_dragonfly.set_param('dry_level',  plugts_obj.get_storedval('dry_level'))
            data_dragonfly.set_param('late_level', plugts_obj.get_storedval('late_level'))
            data_dragonfly.to_cvpj_vst2(convproj_obj, plugin_obj)

        # ---------------------------------------- fruity phase inverter ----------------------------------------
        elif flpluginname == 'fruity phase inverter' and extplugtype == 'vst2':
            print("[plug-conv] FL Studio to VST2: Fruity Phase Inverter > Airwindows Flipity:",pluginid)
            stateval = int((plugin_obj.params.get('state', 0).value/1024)*3)
            flipstate = 0
            if stateval == 1: flipstate = 1
            if stateval == 2: flipstate = 2
            outval = (flipstate/8)+0.01
            plugin_vst2.replace_data(convproj_obj, plugin_obj, 'name', 'any', 'Flipity', 'chunk', struct.pack('<f', outval), 0)
            return True

        #elif flpluginname == 'fruity free filter':
        #    fff_type = getparam('type')
        #    fff_freq = getparam('freq')
        #    fff_q = getparam('q')
        #    fff_gain = getparam('gain')
        #    fff_center = getparam('center')/512
        #    print(fff_type, fff_freq, fff_q, fff_gain, fff_center)
        #    exit()

        #elif flpluginname == 'fruity compressor':  
        #    print('[plug-conv] FL Studio to VST2: Fruity Compressor > Compressor:',pluginid)
        #    convproj_obj.del_automation(cvpj_l, pluginid)
        #    comp_threshold = plugin_obj.params.get('threshold', 0)[0]/10
        #    comp_ratio = plugin_obj.params.get('ratio', 0)[0]/10
        #    comp_gain = plugin_obj.params.get('gain', 0)[0]/10
        #    comp_attack = plugin_obj.params.get('attack', 0)[0]/10
        #    comp_release = plugin_obj.params.get('release', 0)[0]
        #    comp_type = plugin_obj.params.get('type', 0)[0]
        #    first_type = comp_type>>2
        #    second_type = comp_type%4

        #    if second_type == 0: vc_knee = 0
        #    if second_type == 1: vc_knee = 0.3
        #    if second_type == 2: vc_knee = 0.6
        #    if second_type == 3: vc_knee = 1

        #    data_socalabs = params_os_socalabs.socalabs_data()
        #    data_socalabs.set_param("attack", comp_attack)
        #    data_socalabs.set_param("release", comp_release)
        #    data_socalabs.set_param("ratio", comp_ratio)
        #    data_socalabs.set_param("threshold", comp_threshold)
        #    data_socalabs.set_param("knee", vc_knee)
        #    data_socalabs.set_param("input", 1.0)
        #    data_socalabs.set_param("output", 1.0)
        #    data_socalabs.to_cvpj_vst2(cvpj_plugindata, 1397515120)
        #    return True