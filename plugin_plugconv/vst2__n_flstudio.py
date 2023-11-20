# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

import base64
import struct
import os
import math
import lxml.etree as ET

from functions import note_data
from functions import data_bytes
from functions import plugin_vst2
from functions import xtramath
from functions_tracks import auto_data
from functions_plugparams import wave

from functions_plugdata import plugin_dragonfly_reverb
from functions_plugdata import plugin_kickmess
from functions_plugdata import plugin_vital
from functions_plugdata import plugin_wolfshaper
from functions_plugdata import plugin_socalabs

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


def getparam(paramname):
    global cvpj_plugindata_g
    paramval = cvpj_plugindata_g.param_get(paramname, 0)
    return paramval[0]


nonfree_il_plugnames = {
'autogun': 'IL Autogun',
'equo': 'IL EQUO',
'fruity delay 2': 'IL Delay',
'fruity delay bank': 'IL Delay Bank',
'fruity flangus': 'IL Flangus',
'fruity love philter': 'IL Love Philter',
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
'wave candy': 'IL Wave Candy'
}


class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['native-flstudio', None, 'flp'], ['vst2', None, None], True, False
    def convert(self, cvpj_l, pluginid, cvpj_plugindata, extra_json):
        global cvpj_plugindata_g
        cvpj_plugindata_g = cvpj_plugindata

        plugintype = cvpj_plugindata.type_get()
        #---------------------------------------- nonfree ----------------------------------------

        flpluginname = plugintype[1].lower()

        if 'nonfree-plugins' in extra_json:
            if flpluginname == 'fruity blood overdrive':
                print("[plug-conv] FL Studio to VST2: Fruity Blood Overdrive > Blood Overdrive:",pluginid)

                paramvals = [getparam('preband')/10000, getparam('color')/10000, getparam('preamp')/10000,
                getparam('x100'), getparam('postfilter')/10000, getparam('postgain')/10000]
                plugin_vst2.replace_data(cvpj_plugindata, 'name', 'win', 'BloodOverdrive', 'param', None, 6)
                cvpj_plugindata.param_add('vst_param_0', paramvals[0], 'float', " PreBand  ")
                cvpj_plugindata.param_add('vst_param_1', paramvals[1], 'float', "  Color   ")
                cvpj_plugindata.param_add('vst_param_2', paramvals[2], 'float', "  PreAmp  ")
                cvpj_plugindata.param_add('vst_param_3', paramvals[3], 'float', "  x 100   ")
                cvpj_plugindata.param_add('vst_param_4', paramvals[4], 'float', "PostFilter")
                cvpj_plugindata.param_add('vst_param_5', paramvals[5], 'float', " PostGain ")
                return True

            if flpluginname in nonfree_il_plugnames:
                print("[plug-conv] FL Studio to VST2: "+plugintype[1]+":",pluginid)

                chunkb64 = cvpj_plugindata.dataval_get('chunk', '')
                ilchunk = base64.b64decode(chunkb64)

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
                        print(chunkdata)
                        if chunkdata[0] == b'SSLF': dataout = chunkdata[1]

                elif flpluginname in ['directwave']:
                    dataout = ilchunk

                plugin_vst2.replace_data(cvpj_plugindata, 'name', 'win', nonfree_il_plugnames[flpluginname], 'chunk', dataout, None)

                return True


        if flpluginname not in []:
            auto_data.del_plugin(cvpj_l, pluginid)

        #---------------------------------------- Fruit Kick ----------------------------------------
        if flpluginname == 'fruit kick':
            print("[plug-conv] FL Studio to VST2: Fruit Kick > Kickmess:",pluginid)
            max_freq = note_data.note_to_freq((getparam('max_freq')/100)+12) #1000
            min_freq = note_data.note_to_freq((getparam('min_freq')/100)-36) #130.8128
            decay_freq = getparam('decay_freq')/256
            decay_vol = getparam('decay_vol')/256
            osc_click = getparam('osc_click')/64
            osc_dist = getparam('osc_dist')/128
            #print(fkp, max_freq, min_freq, decay_freq, decay_vol, osc_click, osc_dist  )
            data_kickmess = plugin_kickmess.kickmess_data()
            data_kickmess.set_param('pub', 'freq_start', max_freq)
            data_kickmess.set_param('pub', 'freq_end', min_freq)
            data_kickmess.set_param('pub', 'env_slope', decay_vol)
            data_kickmess.set_param('pub', 'freq_slope', 0.5)
            data_kickmess.set_param('pub', 'f_env_release', decay_freq*150)
            data_kickmess.set_param('pub', 'phase_offs', osc_click)
            if osc_dist != 0:
                data_kickmess.set_param('pub', 'dist_on', 1)
                data_kickmess.set_param('pub', 'dist_start', osc_dist*0.1)
                data_kickmess.set_param('pub', 'dist_end', osc_dist*0.1)
            data_kickmess.to_cvpj_vst2(cvpj_plugindata)
            #cvpj_plugindata.dataval_get('middlenotefix', -12)
            return True

        # ---------------------------------------- DX10 ----------------------------------------
        elif flpluginname == 'fruity dx10':
            print("[plug-conv] FL Studio to VST2: Fruity DX10 > mda DX10:",pluginid)
            param_amp_att = getparam('amp_att')/65536
            param_amp_dec = getparam('amp_dec')/65536
            param_amp_rel = getparam('amp_rel')/65536
            param_mod_course = getparam('mod_course')/65536
            param_mod_fine = getparam('mod_fine')/65536
            param_mod_init = getparam('mod_init')/65536
            param_mod_time = getparam('mod_time')/65536
            param_mod_sus = getparam('mod_sus')/65536
            param_mod_rel = getparam('mod_rel')/65536
            param_velsen = getparam('velsen')/65536
            param_vibrato = getparam('vibrato')/65536
            param_octave = (getparam('octave')+2)/5
            param_waveform = getparam('waveform')/65536
            param_mod_thru = getparam('mod_thru')/65536
            param_lforate = getparam('lforate')/65536

            plugin_vst2.replace_data(cvpj_plugindata, 'name','any', 'DX10', 'param', None, 16)
            cvpj_plugindata.param_add('vst_param_0', param_amp_att, 'float', "Attack  ", )
            cvpj_plugindata.param_add('vst_param_1', param_amp_dec, 'float', "Decay   ", )
            cvpj_plugindata.param_add('vst_param_2', param_amp_rel, 'float', "Release ", )
            cvpj_plugindata.param_add('vst_param_3', param_mod_course, 'float', "Coarse  ", )
            cvpj_plugindata.param_add('vst_param_4', param_mod_fine, 'float', "Fine    ", )
            cvpj_plugindata.param_add('vst_param_5', param_mod_init, 'float', "Mod Init", )
            cvpj_plugindata.param_add('vst_param_6', param_mod_time, 'float', "Mod Dec ", )
            cvpj_plugindata.param_add('vst_param_7', param_mod_sus, 'float', "Mod Sus ", )
            cvpj_plugindata.param_add('vst_param_8', param_mod_rel, 'float', "Mod Rel ", )
            cvpj_plugindata.param_add('vst_param_9', param_velsen, 'float', "Mod Vel ", )
            cvpj_plugindata.param_add('vst_param_10', param_vibrato, 'float', "Vibrato ", )
            cvpj_plugindata.param_add('vst_param_11', param_octave, 'float', "Octave  ", )
            cvpj_plugindata.param_add('vst_param_12', 0.5, 'float', "FineTune", )
            cvpj_plugindata.param_add('vst_param_13', param_waveform, 'float', "Waveform", )
            cvpj_plugindata.param_add('vst_param_14', param_mod_thru, 'float', "Mod Thru", )
            cvpj_plugindata.param_add('vst_param_15', param_lforate, 'float', "LFO Rate", )
            return True

        # ---------------------------------------- SimSynth ----------------------------------------
        elif flpluginname == 'simsynth':
            print("[plug-conv] FL Studio to VST2: SimSynth > Vital:",pluginid)
            params_vital = plugin_vital.vital_data(cvpj_plugindata)

            for oscnum in range(3):
                starttextparam = 'osc'+str(oscnum+1)
                starttextparam_vital = 'osc_'+str(oscnum+1)
                osc_shape = getparam(starttextparam+'_shape')
                osc_pw = getparam(starttextparam+'_pw')
                osc_o1 = int(getparam(starttextparam+'_o1'))
                osc_o2 = int(getparam(starttextparam+'_o2'))
                osc_on = float(getparam(starttextparam+'_on'))
                osc_crs = getparam(starttextparam+'_crs')
                osc_fine = getparam(starttextparam+'_fine')
                osc_lvl = getparam(starttextparam+'_lvl')
                osc_warm = int(getparam(starttextparam+'_warm'))

                vital_osc_shape = []
                for num in range(2048): vital_osc_shape.append(wave.tripleoct(num/2048, simsynth_shapes[osc_shape], osc_pw, osc_o1, osc_o2))
                params_vital.replacewave(oscnum, vital_osc_shape)
                params_vital.setvalue(starttextparam_vital+'_on', osc_on)
                params_vital.setvalue(starttextparam_vital+'_transpose', (osc_crs-0.5)*48)
                params_vital.setvalue(starttextparam_vital+'_tune', (osc_fine-0.5)*2)
                params_vital.setvalue(starttextparam_vital+'_level', osc_lvl)
                if osc_warm == 1:
                    params_vital.setvalue(starttextparam_vital+'_unison_detune', 2.2)
                    params_vital.setvalue(starttextparam_vital+'_unison_voices', 6)

            # ------------ AMP ------------
            params_vital.setvalue_timed('env_1_attack', simsynth_time(getparam('amp_att'))*3.5)
            params_vital.setvalue_timed('env_1_decay', simsynth_2time(getparam('amp_dec'))*3.5)
            params_vital.setvalue('env_1_sustain', getparam('amp_sus'))
            params_vital.setvalue('env_1_attack_power', 0)
            params_vital.setvalue('env_1_decay_power', 0)
            params_vital.setvalue('env_1_release_power', 0)
            params_vital.setvalue_timed('env_1_release', simsynth_2time(getparam('amp_rel'))*3.5)

            # ------------ SVF ------------
            params_vital.setvalue_timed('env_2_attack', simsynth_time(getparam('svf_att'))*7)
            params_vital.setvalue_timed('env_2_decay', simsynth_2time(getparam('svf_dec'))*7)
            params_vital.setvalue('env_2_sustain', getparam('svf_sus'))
            params_vital.setvalue_timed('env_2_release', simsynth_2time(getparam('svf_rel'))*7)

            outfilter = 100
            outfilter += (getparam('svf_cut')-0.5)*40
            outfilter += (getparam('svf_kb')-0.5)*10

            params_vital.setvalue('filter_fx_resonance', getparam('svf_emph')*0.8)
            params_vital.setvalue('filter_fx_cutoff', outfilter)
            params_vital.setvalue('filter_fx_on', 1)
            params_vital.set_modulation(1, 'env_2', 'filter_fx_cutoff', getparam('svf_env')*0.6, 0, 0, 0, 0)
            params_vital.set_modulation(2, 'env_1', 'osc_1_transpose', (getparam('osc1_env')-0.5)*0.5, 0, 0, 0, 0)
            params_vital.set_modulation(3, 'env_1', 'osc_2_transpose', (getparam('osc2_env')-0.5)*0.5, 0, 0, 0, 0)
            params_vital.set_modulation(4, 'env_1', 'osc_3_transpose', (getparam('osc3_env')-0.5)*0.5, 0, 0, 0, 0)

            # ------------ Chorus ------------
            params_vital.setvalue('chorus_mod_depth', 0.35)
            params_vital.setvalue('chorus_delay_1', -9.5)
            params_vital.setvalue('chorus_delay_2', -9.0)
            if getparam('chorus_on') == True: params_vital.setvalue('chorus_on', 1.0)
            
            params_vital.to_cvpj_vst2()
            return True

        elif flpluginname == 'fruity bass boost':
            print("[plug-conv] FL Studio to VST2: Fruity Bass Boost > Airwindows Weight:",pluginid)
            param_freq = (getparam('freq')/1024)*0.8
            param_amount = (getparam('amount')/1024)*0.8
            plugin_vst2.replace_data(cvpj_plugindata, 'name', 'any', 'Weight', 'param', None, 2)
            cvpj_plugindata.param_add('vst_param_0', param_freq, 'float', "Freq")
            cvpj_plugindata.param_add('vst_param_1', param_amount, 'float', "Weight")
            return True

        elif flpluginname == 'fruity phaser':
            print("[plug-conv] FL Studio to VST2: Fruity Phaser > SupaPhaser:",pluginid)
            param_sweep_freq = getparam('sweep_freq')/5000
            param_depth_min = getparam('depth_min')/1000
            param_depth_max = getparam('depth_max')/1000
            param_freq_range = getparam('freq_range')/1024
            param_stereo = getparam('stereo')/1024
            param_num_stages = getparam('num_stages')/22
            param_feedback = getparam('feedback')/1000
            param_drywet = getparam('drywet')/1024
            param_gain = getparam('gain')/5000
            plugin_vst2.replace_data(cvpj_plugindata, 'name', 'any', 'SupaPhaser', 'param', None, 16)
            cvpj_plugindata.param_add('vst_param_0', 0, 'float', "attack")
            cvpj_plugindata.param_add('vst_param_1', 0, 'float', "release")
            cvpj_plugindata.param_add('vst_param_2', 0, 'float', "min env")
            cvpj_plugindata.param_add('vst_param_3', 0, 'float', "max env")
            cvpj_plugindata.param_add('vst_param_4', 0, 'float', "env-lfo mixture")
            cvpj_plugindata.param_add('vst_param_5', param_sweep_freq, 'float', "sweep freq.")
            cvpj_plugindata.param_add('vst_param_6', param_depth_min, 'float', "min. depth")
            cvpj_plugindata.param_add('vst_param_7', param_depth_max, 'float', "max. depth")
            cvpj_plugindata.param_add('vst_param_8', param_freq_range, 'float', "freq. range")
            cvpj_plugindata.param_add('vst_param_9', param_stereo, 'float', "stereo")
            cvpj_plugindata.param_add('vst_param_10', param_num_stages, 'float', "nr. stages")
            cvpj_plugindata.param_add('vst_param_11', 0, 'float', "distortion")
            cvpj_plugindata.param_add('vst_param_12', param_feedback, 'float', "feedback")
            cvpj_plugindata.param_add('vst_param_13', param_drywet, 'float', "dry-wet")
            cvpj_plugindata.param_add('vst_param_14', param_gain, 'float', "out gain")
            cvpj_plugindata.param_add('vst_param_15', 0, 'float', "invert")
            return True

        elif flpluginname == 'fruity spectroman':
            print("[plug-conv] FL Studio to VST2: Fruity Spectroman > SocaLabs's SpectrumAnalyzer:",pluginid)
            spectroman_mode = getparam('outputmode')
            data_socalabs = plugin_socalabs.socalabs_data(cvpj_plugindata)
            data_socalabs.set_param("mode", float(spectroman_mode))
            data_socalabs.set_param("log", 1.0)
            data_socalabs.to_cvpj_vst2(cvpj_plugindata, 1399874915)
            return True

        elif flpluginname == 'fruity waveshaper':
            print("[plug-conv] FL Studio to VST2: Fruity Waveshaper > Wolf Shaper:",pluginid)
            data_wolfshaper = plugin_wolfshaper.wolfshaper_data()
            data_wolfshaper.set_param('pregain', ((getparam('preamp')/128)-0.5)*2)
            data_wolfshaper.set_param('wet', getparam('wet')/128)
            data_wolfshaper.set_param('postgain', getparam('postgain')/128)
            data_wolfshaper.set_param('bipolarmode', float(getparam('bipolarmode')))
            data_wolfshaper.set_param('removedc', float(getparam('removedc')))
            shapeenv = cvpj_plugindata.env_points_get('shape')
            if shapeenv != None: data_wolfshaper.add_env(shapeenv)
            data_wolfshaper.to_cvpj_vst2(cvpj_plugindata)
            return True

        elif flpluginname == 'fruity stereo enhancer':
            print("[plug-conv] FL Studio to VST2: Fruity Stereo Enhancer > SocaLabs's StereoProcessor:",pluginid)
            data_socalabs = plugin_socalabs.socalabs_data(cvpj_plugindata)
            data_socalabs.set_param("width1", 0.5)
            data_socalabs.set_param("center1", (getparam('stereo')/(256))+0.5)
            data_socalabs.set_param("pan1", 0.0)
            data_socalabs.set_param("rotation", 0.5)
            data_socalabs.set_param("pan2", getparam('pan')/128)
            data_socalabs.set_param("center2", 0.5)
            data_socalabs.set_param("width2", 0.5)
            data_socalabs.set_param("output", getparam('vol')/640)
            data_socalabs.to_cvpj_vst2(cvpj_plugindata, 1282634853)

        elif flpluginname == 'fruity reeverb':
            print("[plug-conv] FL Studio to VST2: Fruity Reeverb > Dragonfly Hall Reverb:",pluginid)
            data_dragonfly = plugin_dragonfly_reverb.dragonfly_hall_data()
            flr_lowcut = getparam('lowcut')
            flr_lowcut = xtramath.between_from_one(20, 3000, flr_lowcut/65536) if flr_lowcut != 0 else 0
            data_dragonfly.set_param('low_cut', xtramath.clamp(flr_lowcut, 0, 200))
            flr_highcut = getparam('highcut')
            flr_highcut = xtramath.between_from_one(500, 22050, flr_highcut/65536)
            data_dragonfly.set_param('high_cut', xtramath.clamp(flr_highcut, 0, 16000))
            flr_room_size = getparam('room_size')
            flr_room_size = xtramath.between_from_one(1, 100, flr_room_size/65536)
            data_dragonfly.set_param('delay', xtramath.clamp(getparam('predelay'), 0, 100))
            data_dragonfly.set_param('size', int(xtramath.clamp(flr_room_size, 10, 60)))
            data_dragonfly.set_param('diffuse', (getparam('diffusion')/65536)*100)
            flr_decay = xtramath.between_from_one(0.1, 20, getparam('decay')/65536)
            data_dragonfly.set_param('decay', xtramath.clamp(flr_decay, 0.1, 10))
            flr_hidamping = xtramath.between_from_one(500, 22050, getparam('hidamping')/65536)
            data_dragonfly.set_param('high_xo', xtramath.clamp(flr_hidamping, 0, 16000))
            data_dragonfly.set_param('dry_level', (getparam('dry')/65536)*100)
            data_dragonfly.set_param('late_level', (getparam('reverb')/65536)*100)
            data_dragonfly.to_cvpj_vst2(cvpj_plugindata)

        elif flpluginname == 'fruity reeverb 2':
            print("[plug-conv] FL Studio to VST2: Fruity Reeverb 2 > Dragonfly Hall Reverb:",pluginid)
            data_dragonfly = plugin_dragonfly_reverb.dragonfly_hall_data()
            data_dragonfly.set_param('low_cut', xtramath.clamp(getparam('lowcut'), 0, 200))
            data_dragonfly.set_param('high_cut', xtramath.clamp(getparam('highcut')*100, 0, 16000))
            data_dragonfly.set_param('delay', xtramath.clamp((getparam('predelay')/384)*1000, 0, 100))
            data_dragonfly.set_param('size', int(xtramath.clamp(getparam('room_size'), 10, 60)))
            data_dragonfly.set_param('diffuse', getparam('diffusion'))
            data_dragonfly.set_param('decay', xtramath.clamp(getparam('decay')/10, 0.1, 10))
            data_dragonfly.set_param('high_xo', xtramath.clamp(getparam('hidamping')*100, 0, 16000))
            data_dragonfly.set_param('low_mult', xtramath.clamp(getparam('bass')/100, 0.5, 2.5))
            data_dragonfly.set_param('high_mult', 0.7)
            data_dragonfly.set_param('dry_level', xtramath.clamp((getparam('dry')/128)*100, 0, 100))
            #data_dragonfly.set_param('early_level', xtramath.clamp((getparam('er')/128)*100, 0, 100))
            data_dragonfly.set_param('late_level', xtramath.clamp((getparam('wet')/128)*100, 0, 100))
            data_dragonfly.to_cvpj_vst2(cvpj_plugindata)

        elif flpluginname == 'fruity phase inverter':
            print("[plug-conv] FL Studio to VST2: Fruity Phase Inverter > Airwindows Flipity:",pluginid)
            stateval = int((getparam('state')/1024)*3)
            flipstate = 0
            if stateval == 1: flipstate = 1
            if stateval == 2: flipstate = 2
            plugin_vst2.replace_data(cvpj_plugindata, 'name', 'any', 'Flipity', 'chunk', struct.pack('<f', (flipstate/8)+0.01), 0)

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
        #    auto_data.del_plugin(cvpj_l, pluginid)
        #    comp_threshold = cvpj_plugindata.param_get('threshold', 0)[0]/10
        #    comp_ratio = cvpj_plugindata.param_get('ratio', 0)[0]/10
        #    comp_gain = cvpj_plugindata.param_get('gain', 0)[0]/10
        #    comp_attack = cvpj_plugindata.param_get('attack', 0)[0]/10
        #    comp_release = cvpj_plugindata.param_get('release', 0)[0]
        #    comp_type = cvpj_plugindata.param_get('type', 0)[0]
        #    first_type = comp_type>>2
        #    second_type = comp_type%4

        #    if second_type == 0: vc_knee = 0
        #    if second_type == 1: vc_knee = 0.3
        #    if second_type == 2: vc_knee = 0.6
        #    if second_type == 3: vc_knee = 1

        #    data_socalabs = plugin_socalabs.socalabs_data()
        #    data_socalabs.set_param("attack", comp_attack)
        #    data_socalabs.set_param("release", comp_release)
        #    data_socalabs.set_param("ratio", comp_ratio)
        #    data_socalabs.set_param("threshold", comp_threshold)
        #    data_socalabs.set_param("knee", vc_knee)
        #    data_socalabs.set_param("input", 1.0)
        #    data_socalabs.set_param("output", 1.0)
        #    data_socalabs.to_cvpj_vst2(cvpj_plugindata, 1397515120)
        #    return True