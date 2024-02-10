# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv_extern

import math
import base64
import struct
import lxml.etree as ET

from functions_plugin_ext import plugin_vst2
from functions import xtramath

from functions_plugin_ext import data_nullbytegroup
from functions_plugin_ext import params_os_vital
from functions_plugin_ext import params_os_socalabs
from functions_plugin_ext import params_os_kickmess
from functions_plugin_ext import params_os_wolfshaper

from objects_convproj import wave

from objects import plugts

loaded_plugtransform = False

def sid_shape(lmms_sid_shape):
    if lmms_sid_shape == 0: return 3 #squ
    if lmms_sid_shape == 1: return 1 #tri
    if lmms_sid_shape == 2: return 2 #saw
    if lmms_sid_shape == 3: return 4 #noise

def mooglike(x, i_var):
    return (x*2) if x<0.5 else ((1-x)*2)**2

def exp_curve(x, i_var):
    return ((abs(x%(2)-1)-0.5)*2)**2

class plugconv(plugin_plugconv_extern.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv_ext'
    def getplugconvinfo(self): return ['native-lmms', None], ['vst2'], 'lmms'
    def convert(self, convproj_obj, plugin_obj, pluginid, extra_json, extplugtype):
        global loaded_plugtransform
        global plugts_obj

        if loaded_plugtransform == False:
            plugts_obj = plugts.plugtransform()
            plugts_obj.load_file('./data_plugts/lmms_vst2.pltr')
            loaded_plugtransform = True

        if plugin_obj.plugin_subtype == 'bitinvader' and extplugtype == 'vst2':
            print('[plug-conv] LMMS to VST2: BitInvader > Vital:',pluginid)
            interpolation = bool(plugin_obj.params.get('interpolation', 0).value)

            params_vital = params_os_vital.vital_data(plugin_obj)
            params_vital.setvalue('osc_1_on', 1)
            params_vital.setvalue('osc_1_transpose', 12)
            params_vital.setvalue('osc_1_wave_frame', int(interpolation)*256)
            params_vital.importcvpj_wavetable(0, 1, 'main')
            params_vital.importcvpj_env_asdr(1, 'vol')
            params_vital.importcvpj_env_asdr(2, 'cutoff')
            params_vital.importcvpj_env_asdr(3, 'reso')
            params_vital.to_cvpj_vst2(convproj_obj)
            return True

        if plugin_obj.plugin_subtype == 'tripleoscillator' and extplugtype == 'vst2':
            print('[plug-conv] LMMS to VST2: Triple Oscillator > Vital:',pluginid)
            params_vital = params_os_vital.vital_data(plugin_obj)

            for oscnum in range(3):
                vital_oscnum = 'osc_'+str(oscnum+1)
                str_oscnum = str(oscnum)

                v_vol = plugin_obj.params.get('vol'+str_oscnum, 0).value
                v_coarse = plugin_obj.params.get('coarse'+str_oscnum, 0).value
                v_pan = plugin_obj.params.get('pan'+str_oscnum, 0).value
                v_finel = plugin_obj.params.get('finel'+str_oscnum, 0).value
                v_finer = plugin_obj.params.get('finer'+str_oscnum, 0).value
                v_wave = int(plugin_obj.params.get('wavetype'+str_oscnum, 0).value)
                v_phoffset = plugin_obj.params.get('phoffset'+str_oscnum, 0).value

                finetune = (v_finel+v_finer)/2
                unison_detune = abs(v_finel)+abs(v_finer)

                params_vital.setvalue(vital_oscnum+'_on', 1)
                params_vital.setvalue(vital_oscnum+'_level', v_vol/100)
                params_vital.setvalue(vital_oscnum+'_transpose', v_coarse)
                params_vital.setvalue(vital_oscnum+'_pan', v_pan/100)
                params_vital.setvalue(vital_oscnum+'_tune', finetune )
                params_vital.setvalue(vital_oscnum+'_unison_detune', unison_detune*3.5)
                params_vital.setvalue(vital_oscnum+'_unison_voices', 2)
                params_vital.setvalue(vital_oscnum+'_phase', int(v_phoffset)/360)

                wave_obj = wave.cvpj_wave()
                wave_obj.set_numpoints(2048)

                if v_wave == 0: wave_obj.add_wave('sine', 0, 1, 1)
                if v_wave == 1: wave_obj.add_wave('triangle', 0, 1, 1)
                if v_wave == 2: wave_obj.add_wave('saw', 0, 1, 1)
                if v_wave == 3: wave_obj.add_wave('square', 0.5, 1, 1)
                if v_wave == 4: wave_obj.add_wave_func(mooglike, 0, 1, 1)
                if v_wave == 5: wave_obj.add_wave_func(exp_curve, 0, 1, 1)
                #print(v_wave)
                #exit()

                params_vital.replacewave(oscnum, wave_obj.get_wave(2048))

            modalgo1 = plugin_obj.params.get('modalgo1', 0).value
            modalgo2 = plugin_obj.params.get('modalgo2', 0).value

            #coarse0','coarse1','coarse2',
            #'finel0','finel1','finel2','finer0','finer1','finer2',
            #'modalgo1','modalgo2','modalgo3',
            #'pan0','pan1','pan2',
            #'phoffset0','phoffset1','phoffset2',
            #'stphdetun0','stphdetun1','stphdetun2',
            #'vol0','vol1','vol2',
            #'wavetype0','wavetype1','wavetype2

            params_vital.importcvpj_env_asdr(1, 'vol')
            params_vital.importcvpj_env_asdr(2, 'cutoff')
            params_vital.importcvpj_env_asdr(3, 'reso')

            params_vital.to_cvpj_vst2(convproj_obj)

        if plugin_obj.plugin_subtype == 'papu' and extplugtype == 'vst2':
            print("[plug-conv] LMMS to VST2: Freeboy > SocaLabs's PAPU:",pluginid)

            data_socalabs = params_os_socalabs.socalabs_data()

            # Channel 1
            papu_ch1so1 = plugin_obj.params.get('ch1so1', 0).value
            papu_ch1so2 = plugin_obj.params.get('ch1so2', 0).value
            papu_ch1wpd = plugin_obj.params.get('ch1wpd', 0).value
            papu_ch1vsd = plugin_obj.params.get('ch1vsd', 0).value
            papu_ch1ssl = plugin_obj.params.get('ch1ssl', 0).value

            papu_st = plugin_obj.params.get('st', 0).value
            papu_sd = plugin_obj.params.get('sd', 0).value
            if papu_sd: papu_st = -papu_st

            papu_srs = plugin_obj.params.get('srs', 0).value

            data_socalabs.set_param("OL1", int(papu_ch1so1))
            data_socalabs.set_param("OR1", int(papu_ch1so2))
            data_socalabs.set_param("duty1", papu_ch1wpd)
            if papu_ch1vsd:
                data_socalabs.set_param("A1", papu_ch1ssl)
                data_socalabs.set_param("R1", 0.0)
            else:
                data_socalabs.set_param("A1", 0.0)
                data_socalabs.set_param("R1", papu_ch1ssl)
            data_socalabs.set_param("tune1", 12.0)
            data_socalabs.set_param("fine1", 0.0)
            data_socalabs.set_param("sweep1", papu_st)
            data_socalabs.set_param("shift1", papu_srs)

            # Channel 2
            papu_ch2so1 = plugin_obj.params.get('ch2so1', 0).value
            papu_ch2so2 = plugin_obj.params.get('ch2so2', 0).value
            papu_ch2wpd = plugin_obj.params.get('ch2wpd', 0).value
            papu_ch2vsd = plugin_obj.params.get('ch2vsd', 0).value
            papu_ch2ssl = plugin_obj.params.get('ch2ssl', 0).value

            data_socalabs.set_param("OL2", int(papu_ch2so1))
            data_socalabs.set_param("OR2", int(papu_ch2so2))
            data_socalabs.set_param("duty2", papu_ch2wpd)
            if papu_ch2vsd:
                data_socalabs.set_param("A2", papu_ch2ssl)
                data_socalabs.set_param("R2", 0.0)
            else:
                data_socalabs.set_param("A2", 0.0)
                data_socalabs.set_param("R2", papu_ch2ssl)
            data_socalabs.set_param("tune2", 12.0)
            data_socalabs.set_param("fine2", 0.0)

            # Channel 4
            papu_ch4so1 = plugin_obj.params.get('ch4so1', 0).value
            papu_ch4so2 = plugin_obj.params.get('ch4so2', 0).value
            papu_ch4vsd = plugin_obj.params.get('ch4vsd', 0).value
            papu_ch4ssl = plugin_obj.params.get('ch4ssl', 0).value
            papu_ch2ssl = plugin_obj.params.get('ch2ssl', 0).value

            papu_srw = plugin_obj.params.get('srw', 0).value

            data_socalabs.set_param("OLN", int(papu_ch4so1))
            data_socalabs.set_param("ORL", int(papu_ch4so2))
            if papu_ch4vsd:
                data_socalabs.set_param("AN", papu_ch4ssl)
                data_socalabs.set_param("AR", 0.0)
            else:
                data_socalabs.set_param("AN", 0.0)
                data_socalabs.set_param("AR", papu_ch4ssl)
            data_socalabs.set_param("shiftN", 10)
            data_socalabs.set_param("stepN", int(papu_srw))
            data_socalabs.set_param("ratioN", 0.0)

            data_socalabs.set_param("output", 7.0)
            data_socalabs.set_param("param", 8.0)
            data_socalabs.to_cvpj_vst2(convproj_obj, plugin_obj, 1348563061)

        if plugin_obj.plugin_subtype == 'sid' and extplugtype == 'vst2':
            print("[plug-conv] LMMS to VST2: SID > SocaLabs's SID:",pluginid)
            plugts_obj.transform('vst2_sid', convproj_obj, plugin_obj, pluginid, extra_json)
            data_socalabs = params_os_socalabs.socalabs_data()
            data_socalabs.set_param("a1", plugts_obj.get_storedval('a1'))
            data_socalabs.set_param("a2", plugts_obj.get_storedval('a2'))
            data_socalabs.set_param("a3", plugts_obj.get_storedval('a3'))
            data_socalabs.set_param("cutoff", plugts_obj.get_storedval('cutoff'))
            data_socalabs.set_param("d1", plugts_obj.get_storedval('d1'))
            data_socalabs.set_param("d2", plugts_obj.get_storedval('d2'))
            data_socalabs.set_param("d3", plugts_obj.get_storedval('d3'))
            data_socalabs.set_param("f1", int(plugts_obj.get_storedval('f1')))
            data_socalabs.set_param("f2", int(plugts_obj.get_storedval('f2')))
            data_socalabs.set_param("f3", int(plugts_obj.get_storedval('f3')))
            data_socalabs.set_param("fine1", 0.0)
            data_socalabs.set_param("fine2", 0.0)
            data_socalabs.set_param("fine3", 0.0)
            filterMode = int(plugts_obj.get_storedval('filterMode'))
            data_socalabs.set_param("highpass", 1.0 if filterMode == 0 else 0.0)
            data_socalabs.set_param("bandpass", 1.0 if filterMode == 1 else 0.0)
            data_socalabs.set_param("lowpass", 1.0 if filterMode == 2 else 0.0)
            data_socalabs.set_param("output3", plugts_obj.get_storedval('output3'))
            data_socalabs.set_param("pw1", plugts_obj.get_storedval('pw1'))
            data_socalabs.set_param("pw2", plugts_obj.get_storedval('pw2'))
            data_socalabs.set_param("pw3", plugts_obj.get_storedval('pw3'))
            data_socalabs.set_param("r1", plugts_obj.get_storedval('r1'))
            data_socalabs.set_param("r2", plugts_obj.get_storedval('r2'))
            data_socalabs.set_param("r3", plugts_obj.get_storedval('r3'))
            data_socalabs.set_param("reso", plugts_obj.get_storedval('reso'))
            data_socalabs.set_param("ring1", int(plugts_obj.get_storedval('ring1')))
            data_socalabs.set_param("ring2", int(plugts_obj.get_storedval('ring2')))
            data_socalabs.set_param("ring3", int(plugts_obj.get_storedval('ring3')))
            data_socalabs.set_param("s1", plugts_obj.get_storedval('s1'))
            data_socalabs.set_param("s2", plugts_obj.get_storedval('s2'))
            data_socalabs.set_param("s3", plugts_obj.get_storedval('s3'))
            data_socalabs.set_param("sync1", int(plugts_obj.get_storedval('sync1')))
            data_socalabs.set_param("sync2", int(plugts_obj.get_storedval('sync2')))
            data_socalabs.set_param("sync3", int(plugts_obj.get_storedval('sync3')))
            data_socalabs.set_param("tune1", plugts_obj.get_storedval('tune1'))
            data_socalabs.set_param("tune2", plugts_obj.get_storedval('tune2'))
            data_socalabs.set_param("tune3", plugts_obj.get_storedval('tune3'))
            data_socalabs.set_param("voices", 8.0)
            data_socalabs.set_param("vol", plugts_obj.get_storedval('vol'))
            data_socalabs.set_param("w1", sid_shape(plugts_obj.get_storedval('w1')))
            data_socalabs.set_param("w2", sid_shape(plugts_obj.get_storedval('w2')))
            data_socalabs.set_param("w3", sid_shape(plugts_obj.get_storedval('w3')))
            data_socalabs.to_cvpj_vst2(convproj_obj, plugin_obj, 1399415908)

        if plugin_obj.plugin_subtype == 'kicker' and extplugtype == 'vst2':
            print("[plug-conv] LMMS to VST2: Kicker > Kickmess:",pluginid)
            plugts_obj.transform('vst2_kicker', convproj_obj, plugin_obj, pluginid, extra_json)
            data_kickmess = params_os_kickmess.kickmess_data()
            data_kickmess.set_param('pub', 'freq_start',     plugts_obj.get_storedval('freq_start'))
            data_kickmess.set_param('pub', 'freq_end',       plugts_obj.get_storedval('freq_end'))
            data_kickmess.set_param('pub', 'f_env_release',  plugts_obj.get_storedval('f_env_release'))
            data_kickmess.set_param('pub', 'dist_start',     plugts_obj.get_storedval('dist_start'))
            data_kickmess.set_param('pub', 'dist_end',       plugts_obj.get_storedval('dist_end'))
            data_kickmess.set_param('pub', 'gain',           plugts_obj.get_storedval('gain'))
            data_kickmess.set_param('pub', 'env_slope',      plugts_obj.get_storedval('env_slope'))
            data_kickmess.set_param('pub', 'freq_slope',     plugts_obj.get_storedval('freq_slope'))
            data_kickmess.set_param('pub', 'noise',          plugts_obj.get_storedval('noise'))
            if plugts_obj.get_storedval('startnote') == 1:   data_kickmess.set_param('pub', 'freq_note_start', 0.5)
            if plugts_obj.get_storedval('endnote') == 1:     data_kickmess.set_param('pub', 'freq_note_end', 0.5)
            data_kickmess.set_param('pub', 'phase_offs',     plugts_obj.get_storedval('phase_offs'))
            data_kickmess.to_cvpj_vst2(convproj_obj, plugin_obj)

        if plugin_obj.plugin_subtype == 'lb302' and extplugtype == 'vst2':
            print("[plug-conv] LMMS to VST2: LB302 > Vital:",pluginid)

            lb_db24 = plugin_obj.params.get('db24', 0).value
            lb_dead = plugin_obj.params.get('dead', 0).value
            lb_shape = plugin_obj.params.get('shape', 0).value
            lb_slide = plugin_obj.params.get('slide', 0).value
            lb_slide_dec = plugin_obj.params.get('slide_dec', 0).value
            lb_vcf_cut = plugin_obj.params.get('vcf_cut', 0).value
            lb_vcf_dec = plugin_obj.params.get('vcf_dec', 0).value
            lb_vcf_mod = plugin_obj.params.get('vcf_mod', 0).value
            lb_vcf_res = plugin_obj.params.get('vcf_res', 0).value

            params_vital = params_os_vital.vital_data(plugin_obj)

            wave_obj = wave.cvpj_wave()
            wave_obj.set_numpoints(2048)
            if lb_shape == 0: wave_obj.add_wave('saw', 0, 1, 1)
            if lb_shape == 1: wave_obj.add_wave('triangle', 0, 1, 1)
            if lb_shape == 2: wave_obj.add_wave('square', 0.5, 1, 1)
            if lb_shape == 3: wave_obj.add_wave('square', 0.5, 1, 1) #square_roundend
            if lb_shape == 4: wave_obj.add_wave_func(mooglike, 0, 1, 1)
            if lb_shape == 5: wave_obj.add_wave('sine', 0, 1, 1)
            if lb_shape == 6: wave_obj.add_wave_func(exp_curve, 0, 1, 1)
            if lb_shape == 8: wave_obj.add_wave('saw', 0, 1, 1)
            if lb_shape == 9: wave_obj.add_wave('square', 0.5, 1, 1)
            if lb_shape == 10: wave_obj.add_wave('triangle', 0, 1, 1)
            if lb_shape == 11: wave_obj.add_wave_func(mooglike, 0, 1, 1)
            if lb_shape != 7: 
                params_vital.setvalue('osc_1_on', 1)
                params_vital.replacewave(0, wave_obj.get_wave(2048))
            else: params_vital.setvalue('sample_on', 1)
            params_vital.setvalue('osc_1_level', 1)
            params_vital.setvalue('osc_1_transpose', 12)
            params_vital.setvalue('sample_level', 1)
            if lb_db24 == 0:
                vitalcutoff_first = (lb_vcf_cut*40)+50
                vitalcutoff_minus = (lb_vcf_mod*16)
                params_vital.set_modulation(1, 'env_2', 'filter_fx_cutoff', (lb_vcf_mod+0.5)*0.25, 0, 0, 0, 0)
            else:
                vitalcutoff_first = (lb_vcf_cut*60)+20
                vitalcutoff_minus = (lb_vcf_mod*20)
                params_vital.set_modulation(1, 'env_2', 'filter_fx_cutoff', (lb_vcf_mod+0.2)*0.5, 0, 0, 0, 0)
            params_vital.setvalue('polyphony', 1)
            if lb_slide == 1:
                params_vital.setvalue('portamento_force', 1)
                params_vital.setvalue('portamento_slope', 5)
                params_vital.setvalue('portamento_time', (-5)+(pow(lb_slide_dec*2, 2.5)))
            params_vital.setvalue('filter_fx_on', 1)
            params_vital.setvalue('filter_fx_cutoff', vitalcutoff_first-vitalcutoff_minus)
            params_vital.setvalue('filter_fx_resonance', lb_vcf_res/1.7)
            params_vital.setvalue_timed('env_2_decay', 0.4+(lb_vcf_dec*3) if lb_dead == 0 else 0)
            params_vital.setvalue('env_2_sustain', 0)
            params_vital.to_cvpj_vst2(convproj_obj)
            return True

        if plugin_obj.plugin_subtype == 'zynaddsubfx' and extplugtype == 'vst2':
            print("[plug-conv] LMMS to VST2: ZynAddSubFX > ZynAddSubFX/Zyn-Fusion:",pluginid)
            zasfxdata = plugin_obj.rawdata_get('data')
            zasfxdatastart = '<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE ZynAddSubFX-data>' 
            zasfxdatafixed = zasfxdatastart.encode('utf-8') + zasfxdata
            plugin_vst2.replace_data(convproj_obj, plugin_obj, 'name','any', 'ZynAddSubFX', 'chunk', zasfxdatafixed, None)
            return True

        if plugin_obj.plugin_subtype == 'reverbsc' and extplugtype == 'vst2':
            print("[plug-conv] LMMS to VST2: ReverbSC > Castello Reverb:",pluginid)
            plugts_obj.transform('vst2_reverbsc', convproj_obj, plugin_obj, pluginid, extra_json)
            plugin_vst2.replace_data(convproj_obj, plugin_obj, 'name', 'any', 'Castello Reverb', 'chunk', 
                data_nullbytegroup.make(
                    [{'ui_size': ''}, 
                    {'mix': '1', 'size': str(plugts_obj.get_storedval('size')), 'brightness': str(plugts_obj.get_storedval('color'))}]), 
                None)
            return True

        if plugin_obj.plugin_subtype == 'spectrumanalyzer' and extplugtype == 'vst2':
            print("[plug-conv] LMMS to VST2: Spectrum Analyzer > SocaLabs's SpectrumAnalyzer:",pluginid)
            data_socalabs = params_os_socalabs.socalabs_data()
            data_socalabs.set_param("mode", 0.0)
            data_socalabs.set_param("log", 1.0)
            data_socalabs.to_cvpj_vst2(convproj_obj, plugin_obj, 1399874915)
            return True

        if plugin_obj.plugin_subtype == 'waveshaper' and extplugtype == 'vst2':
            print("[plug-conv] LMMS to VST2: Wave Shaper > Wolf Shaper:",pluginid)
            data_wolfshaper = params_os_wolfshaper.wolfshaper_data()
            waveshapebytes = base64.b64decode(plugin_obj.datavals.get('waveShape', ''))
            waveshapepoints = [struct.unpack('f', waveshapebytes[i:i+4]) for i in range(0, len(waveshapebytes), 4)]
            for pointnum in range(50): data_wolfshaper.add_point(pointnum/49,waveshapepoints[pointnum*4][0],0.0,0)
            data_wolfshaper.to_cvpj_vst2(convproj_obj, plugin_obj)
            return True
