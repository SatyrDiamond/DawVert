# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv_extern

import base64
import struct
import lxml.etree as ET

from functions import plugin_vst2
from functions import plugins
from functions import xtramath

from functions_tracks import auto_data

from functions_plugdata import data_nullbytegroup
from functions_plugdata import plugin_vital
from functions_plugdata import plugin_socalabs
from functions_plugdata import plugin_kickmess
from functions_plugdata import plugin_wolfshaper

from functions_plugdata import data_wave

def sid_shape(lmms_sid_shape):
    if lmms_sid_shape == 0: return 3 #squ
    if lmms_sid_shape == 1: return 1 #tri
    if lmms_sid_shape == 2: return 2 #saw
    if lmms_sid_shape == 3: return 4 #noise

def getparam(paramname):
    global cvpj_plugindata_gav
    paramval = cvpj_plugindata_g.param_get(paramname, 0)
    return paramval[0]

class plugconv(plugin_plugconv_extern.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv_ext'
    def getplugconvinfo(self): return ['native-lmms', None], ['vst2'], 'lmms'
    def convert(self, cvpj_l, pluginid, cvpj_plugindata, extra_json, extplugtype):
        global cvpj_plugindata_g
        cvpj_plugindata_g = cvpj_plugindata

        plugintype = cvpj_plugindata.type_get()

        if plugintype[1] == 'tripleoscillator' and extplugtype == 'vst2':
            print('[plug-conv] LMMS to VST2: Triple Oscillator > Vital:',pluginid)
            params_vital = plugin_vital.vital_data(cvpj_plugindata)

            for oscnum in range(3):
                vital_oscnum = 'osc_'+str(oscnum+1)
                str_oscnum = str(oscnum)

                params_vital.setvalue(vital_oscnum+'_on', 1)
                params_vital.setvalue(vital_oscnum+'_level', getparam('vol'+str_oscnum)/100)
                params_vital.setvalue(vital_oscnum+'_transpose', getparam('coarse'+str_oscnum))
                params_vital.setvalue(vital_oscnum+'_pan', getparam('pan'+str_oscnum)/100)

                soscfine_l = int(getparam('finel'+str_oscnum))/100
                soscfine_r = int(getparam('finer'+str_oscnum))/100

                finetune = (soscfine_l+soscfine_r)/2
                unison_detune = abs(soscfine_l)+abs(soscfine_r)

                params_vital.setvalue(vital_oscnum+'_tune', finetune )
                params_vital.setvalue(vital_oscnum+'_unison_detune', unison_detune*3.5)
                params_vital.setvalue(vital_oscnum+'_unison_voices', 2)
                params_vital.setvalue(vital_oscnum+'_phase', int(getparam('phoffset'+str_oscnum))/360)

                soscwave = int(getparam('wavetype'+str_oscnum))
                vital_shape = None
                if soscwave == 0: vital_shape = data_wave.create_wave('sine', 0, None)
                if soscwave == 1: vital_shape = data_wave.create_wave('triangle', 0, None)
                if soscwave == 2: vital_shape = data_wave.create_wave('saw', 0, None)
                if soscwave == 3: vital_shape = data_wave.create_wave('square', 0, 0.5)
                if soscwave == 4: vital_shape = data_wave.create_wave('mooglike', 0, None)
                if soscwave == 5: vital_shape = data_wave.create_wave('exp', 0, None)
                if vital_shape != None: params_vital.replacewave(oscnum, vital_shape)

            modalgo1 = int(getparam('modalgo1'))
            modalgo2 = int(getparam('modalgo2'))

            #coarse0','coarse1','coarse2',
            #'finel0','finel1','finel2','finer0','finer1','finer2',
            #'modalgo1','modalgo2','modalgo3',
            #'pan0','pan1','pan2',
            #'phoffset0','phoffset1','phoffset2',
            #'stphdetun0','stphdetun1','stphdetun2',
            #'vol0','vol1','vol2',
            #'wavetype0','wavetype1','wavetype2

            params_vital.importcvpj_env_asdr(cvpj_plugindata, 1, 'vol')
            params_vital.importcvpj_env_asdr(cvpj_plugindata, 2, 'cutoff')
            params_vital.importcvpj_env_asdr(cvpj_plugindata, 3, 'reso')

            params_vital.to_cvpj_vst2()
            return True

        if plugintype[1] == 'bitinvader' and extplugtype == 'vst2':
            print('[plug-conv] LMMS to VST2: BitInvader > Vital:',pluginid)
            interpolation = getparam('interpolation')
            params_vital = plugin_vital.vital_data(cvpj_plugindata)
            params_vital.setvalue('osc_1_on', 1)
            params_vital.setvalue('osc_1_transpose', 12)
            params_vital.importcvpj_wave(cvpj_plugindata, 1, 'main', smooth=bool(interpolation))
            params_vital.importcvpj_env_asdr(cvpj_plugindata, 1, 'vol')
            params_vital.importcvpj_env_asdr(cvpj_plugindata, 2, 'cutoff')
            params_vital.importcvpj_env_asdr(cvpj_plugindata, 3, 'reso')
            params_vital.to_cvpj_vst2()
            return True

        if plugintype[1] == 'papu' and extplugtype == 'vst2':
            print("[plug-conv] LMMS to VST2: Freeboy > SocaLabs's PAPU:",pluginid)
            data_socalabs = plugin_socalabs.socalabs_data(cvpj_plugindata)

            sweep_time = getparam('st')
            if getparam('sd'): sweep_time = -sweep_time

            data_socalabs.set_param("OL1", int(getparam('ch1so1')))
            data_socalabs.set_param("OR1", int(getparam('ch1so2')))
            data_socalabs.set_param("duty1", getparam('ch1wpd'))
            if getparam('ch1vsd'):
                data_socalabs.set_param("A1", getparam('ch1ssl'))
                data_socalabs.set_param("R1", 0.0)
            else:
                data_socalabs.set_param("A1", 0.0)
                data_socalabs.set_param("R1", getparam('ch1ssl'))
            data_socalabs.set_param("tune1", 0.0)
            data_socalabs.set_param("fine1", 0.0)
            data_socalabs.set_param("sweep1", sweep_time)
            data_socalabs.set_param("shift1", getparam('srs'))

            data_socalabs.set_param("OL2", int(getparam('ch2so1')))
            data_socalabs.set_param("OR2", int(getparam('ch2so2')))
            data_socalabs.set_param("duty2", getparam('ch2wpd'))
            if getparam('ch2vsd'):
                data_socalabs.set_param("A2", getparam('ch2ssl'))
                data_socalabs.set_param("R2", 0.0)
            else:
                data_socalabs.set_param("A2", 0.0)
                data_socalabs.set_param("R2", getparam('ch2ssl'))
            data_socalabs.set_param("tune2", 0.0)
            data_socalabs.set_param("fine2", 0.0)

            data_socalabs.set_param("OLN", int(getparam('ch4so1')))
            data_socalabs.set_param("ORL", int(getparam('ch4so2')))
            if getparam('ch4vsd'):
                data_socalabs.set_param("AN", getparam('ch4ssl'))
                data_socalabs.set_param("AR", 0.0)
            else:
                data_socalabs.set_param("AN", 0.0)
                data_socalabs.set_param("AR", getparam('ch4ssl'))
            data_socalabs.set_param("shiftN", 10)
            data_socalabs.set_param("stepN", int(getparam('srw')))
            data_socalabs.set_param("ratioN", 0.0)

            data_socalabs.set_param("output", 7.0)
            data_socalabs.set_param("param", 8.0)
            data_socalabs.to_cvpj_vst2(cvpj_plugindata, 1348563061)

        if plugintype[1] == 'sid' and extplugtype == 'vst2':
            print("[plug-conv] LMMS to VST2: SID > SocaLabs's SID:",pluginid)
            data_socalabs = plugin_socalabs.socalabs_data(cvpj_plugindata)
            data_socalabs.set_param("a1", getparam('attack0'))
            data_socalabs.set_param("a2", getparam('attack1'))
            data_socalabs.set_param("a3", getparam('attack2'))
            data_socalabs.set_param("cutoff", getparam('filterFC'))
            data_socalabs.set_param("d1", getparam('decay0'))
            data_socalabs.set_param("d2", getparam('decay1'))
            data_socalabs.set_param("d3", getparam('decay2'))
            data_socalabs.set_param("f1", getparam('filtered0'))
            data_socalabs.set_param("f2", getparam('filtered1'))
            data_socalabs.set_param("f3", getparam('filtered2'))
            data_socalabs.set_param("fine1", 0.0)
            data_socalabs.set_param("fine2", 0.0)
            data_socalabs.set_param("fine3", 0.0)
            filterMode = getparam('filterMode')
            data_socalabs.set_param("highpass", 1.0 if filterMode == 0.0 else 0.0)
            data_socalabs.set_param("bandpass", 1.0 if filterMode == 1.0 else 0.0)
            data_socalabs.set_param("lowpass", 1.0 if filterMode == 2.0 else 0.0)
            data_socalabs.set_param("output3", getparam('voice3Off'))
            data_socalabs.set_param("pw1", getparam('pulsewidth0'))
            data_socalabs.set_param("pw2", getparam('pulsewidth1'))
            data_socalabs.set_param("pw3", getparam('pulsewidth2'))
            data_socalabs.set_param("r1", getparam('release0'))
            data_socalabs.set_param("r2", getparam('release1'))
            data_socalabs.set_param("r3", getparam('release2'))
            data_socalabs.set_param("reso", getparam('filterResonance'))
            data_socalabs.set_param("ring1", getparam('ringmod0'))
            data_socalabs.set_param("ring2", getparam('ringmod1'))
            data_socalabs.set_param("ring3", getparam('ringmod2'))
            data_socalabs.set_param("s1", getparam('sustain0'))
            data_socalabs.set_param("s2", getparam('sustain1'))
            data_socalabs.set_param("s3", getparam('sustain2'))
            data_socalabs.set_param("sync1", getparam('sync0'))
            data_socalabs.set_param("sync2", getparam('sync1'))
            data_socalabs.set_param("sync3", getparam('sync2'))
            data_socalabs.set_param("tune1", getparam('coarse0'))
            data_socalabs.set_param("tune2", getparam('coarse1'))
            data_socalabs.set_param("tune3", getparam('coarse2'))
            data_socalabs.set_param("voices", 8.0)
            data_socalabs.set_param("vol", getparam('volume'))
            data_socalabs.set_param("w1", sid_shape(getparam('waveform0')))
            data_socalabs.set_param("w2", sid_shape(getparam('waveform1')))
            data_socalabs.set_param("w3", sid_shape(getparam('waveform2')))
            data_socalabs.to_cvpj_vst2(cvpj_plugindata, 1399415908)
            #cvpj_plugindata.dataval_get('middlenotefix', -12)
            return True

        if plugintype[1] == 'kicker' and extplugtype == 'vst2':
            print("[plug-conv] LMMS to VST2: Kicker > Kickmess:",pluginid)
            data_kickmess = plugin_kickmess.kickmess_data()
            data_kickmess.set_param('pub', 'freq_start', getparam('startfreq'))
            data_kickmess.set_param('pub', 'freq_end', getparam('endfreq'))
            data_kickmess.set_param('pub', 'f_env_release', getparam('decay'))
            data_kickmess.set_param('pub', 'dist_start', getparam('dist')/100)
            data_kickmess.set_param('pub', 'dist_end', getparam('distend')/100)
            data_kickmess.set_param('pub', 'gain', xtramath.clamp(getparam('gain'), 0, 2)/2)
            data_kickmess.set_param('pub', 'env_slope', getparam('env'))
            data_kickmess.set_param('pub', 'freq_slope', getparam('slope'))
            data_kickmess.set_param('pub', 'noise', getparam('noise'))
            if getparam('startnote') == 1: data_kickmess.set_param('pub', 'freq_note_start', 0.5)
            if getparam('endnote') == 1: data_kickmess.set_param('pub', 'freq_note_end', 0.5)
            data_kickmess.set_param('pub', 'phase_offs', getparam('click'))
            data_kickmess.to_cvpj_vst2(cvpj_plugindata)

            return True

        if plugintype[1] == 'lb302' and extplugtype == 'vst2':
            print("[plug-conv] LMMS to VST2: LB302 > Vital:",pluginid)
            params_vital = plugin_vital.vital_data(cvpj_plugindata)
            lb302_shape = getparam('shape')
            if lb302_shape == 0: vital_shape = data_wave.create_wave('saw', 0, None)
            if lb302_shape == 1: vital_shape = data_wave.create_wave('triangle', 0, None)
            if lb302_shape == 2: vital_shape = data_wave.create_wave('square', 0, 0.5)
            if lb302_shape == 3: vital_shape = data_wave.create_wave('square_roundend', 0, None)
            if lb302_shape == 4: vital_shape = data_wave.create_wave('mooglike', 0, None)
            if lb302_shape == 5: vital_shape = data_wave.create_wave('sine', 0, None)
            if lb302_shape == 6: vital_shape = data_wave.create_wave('exp', 0, None)
            if lb302_shape == 8: vital_shape = data_wave.create_wave('saw', 0, None)
            if lb302_shape == 9: vital_shape = data_wave.create_wave('square', 0, 0.5)
            if lb302_shape == 10: vital_shape = data_wave.create_wave('triangle', 0, None)
            if lb302_shape == 11: vital_shape = data_wave.create_wave('mooglike', 0, None)
            if lb302_shape != 7: 
                params_vital.setvalue('osc_1_on', 1)
                params_vital.replacewave(0, vital_shape)
            else: params_vital.setvalue('sample_on', 1)
            params_vital.setvalue('osc_1_level', 1)
            params_vital.setvalue('sample_level', 1)
            if getparam('db24') == 0:
                vitalcutoff_first = (getparam('vcf_cut')*40)+50
                vitalcutoff_minus = (getparam('vcf_mod')*16)
                params_vital.set_modulation(1, 'env_2', 'filter_fx_cutoff', (getparam('vcf_mod')+0.5)*0.25, 0, 0, 0, 0)
            else:
                vitalcutoff_first = (getparam('vcf_cut')*60)+20
                vitalcutoff_minus = (getparam('vcf_mod')*20)
                params_vital.set_modulation(1, 'env_2', 'filter_fx_cutoff', (getparam('vcf_mod')+0.2)*0.5, 0, 0, 0, 0)
            params_vital.setvalue('polyphony', 1)
            if getparam('slide') == 1:
                params_vital.setvalue('portamento_force', 1)
                params_vital.setvalue('portamento_slope', 5)
                params_vital.setvalue('portamento_time', (-5)+(pow(getparam('slide_dec')*2, 2.5)))
            params_vital.setvalue('filter_fx_on', 1)
            params_vital.setvalue('filter_fx_cutoff', vitalcutoff_first-vitalcutoff_minus)
            params_vital.setvalue('filter_fx_resonance', getparam('vcf_res')/1.7)
            if getparam('dead') == 0: params_vital.setvalue_timed('env_2_decay', 0.4+(getparam('vcf_dec')*3))
            else: params_vital.setvalue_timed('env_2_decay', 0)
            params_vital.setvalue('env_2_sustain', 0)
            params_vital.to_cvpj_vst2()
            #cvpj_plugindata.dataval_get('middlenotefix', -12)
            return True

        if plugintype[1] == 'zynaddsubfx' and extplugtype == 'vst2':
            print("[plug-conv] LMMS to VST2: ZynAddSubFX > ZynAddSubFX/Zyn-Fusion:",pluginid)
            zasfxdata = cvpj_plugindata.dataval_get('data', '')
            zasfxdatastart = '<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE ZynAddSubFX-data>' 
            zasfxdatafixed = zasfxdatastart.encode('utf-8') + base64.b64decode(zasfxdata)
            plugin_vst2.replace_data(cvpj_plugindata, 'name','any', 'ZynAddSubFX', 'chunk', zasfxdatafixed, None)
            return True

        if plugintype[1] == 'reverbsc' and extplugtype == 'vst2':
            print("[plug-conv] LMMS to VST2: ReverbSC > Castello Reverb:",pluginid)
            value_size = getparam('size')
            value_color = getparam('color')
            plugin_vst2.replace_data(cvpj_plugindata, 'name', 'any', 'Castello Reverb', 'chunk', 
                data_nullbytegroup.make(
                    [{'ui_size': ''}, 
                    {'mix': '1', 'size': str(value_size), 'brightness': str(value_color/15000)}]), 
                None)
            auto_data.to_ext_one(cvpj_l, pluginid, 'size', 'ext_param_1', 0, 1)
            auto_data.to_ext_one(cvpj_l, pluginid, 'color', 'ext_param_2', 0, 15000)
            return True

        if plugintype[1] == 'spectrumanalyzer' and extplugtype == 'vst2':
            print("[plug-conv] LMMS to VST2: Spectrum Analyzer > SocaLabs's SpectrumAnalyzer:",pluginid)
            data_socalabs = plugin_socalabs.socalabs_data(cvpj_plugindata)
            data_socalabs.set_param("mode", 0.0)
            data_socalabs.set_param("log", 1.0)
            data_socalabs.to_cvpj_vst2(cvpj_plugindata, 1399874915)
            return True

        if plugintype[1] == 'waveshaper' and extplugtype == 'vst2':
            print("[plug-conv] LMMS to VST2: Wave Shaper > Wolf Shaper:",pluginid)
            data_wolfshaper = plugin_wolfshaper.wolfshaper_data()
            waveshapebytes = base64.b64decode(cvpj_plugindata.dataval_get('waveShape', ''))
            waveshapepoints = [struct.unpack('f', waveshapebytes[i:i+4]) for i in range(0, len(waveshapebytes), 4)]
            for pointnum in range(50): data_wolfshaper.add_point(pointnum/49,waveshapepoints[pointnum*4][0],0.0,0)
            data_wolfshaper.to_cvpj_vst2(cvpj_plugindata)
            return True
