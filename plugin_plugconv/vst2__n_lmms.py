# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

import base64
import struct
import lxml.etree as ET

from functions import plugin_vst2
from functions import plugins
from functions import xtramath

from functions_plugparams import params_various_inst
from functions_plugparams import params_various_fx
from functions_plugparams import params_vital
from functions_plugparams import wave
from functions_plugparams import params_kickmess
from functions_plugparams import data_nullbytegroup

def sid_shape(lmms_sid_shape):
    if lmms_sid_shape == 0: return 3 #squ
    if lmms_sid_shape == 1: return 1 #tri
    if lmms_sid_shape == 2: return 2 #saw
    if lmms_sid_shape == 3: return 4 #noise

def getparam(paramname):
    global pluginid_g
    global cvpj_l_g
    paramval = plugins.get_plug_param(cvpj_l_g, pluginid_g, paramname, 0)
    return paramval[0]

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['native-lmms', None, 'lmms'], ['vst2', None, None], True, False
    def convert(self, cvpj_l, pluginid, plugintype, extra_json):

        global pluginid_g
        global cvpj_l_g
        pluginid_g = pluginid
        cvpj_l_g = cvpj_l

        if plugintype[1] == 'bitinvader':
            params_vital.create()
            bitinvader_shape_data = base64.b64decode(plugins.get_plug_dataval(cvpj_l, pluginid, 'sampleShape', ''))
            bitinvader_shape_vals = struct.unpack('f'*(len(bitinvader_shape_data)//4), bitinvader_shape_data)
            params_vital.setvalue('osc_1_on', 1)
            params_vital.setvalue('osc_1_transpose', 12)
            params_vital.replacewave(0, wave.resizewave(bitinvader_shape_vals))
            params_vital.importcvpj_env_asdr(cvpj_l, pluginid, 1, 'volume')
            vitaldata = params_vital.getdata()
            plugin_vst2.replace_data(cvpj_l, pluginid, 'any', 'Vital', 'chunk', vitaldata.encode('utf-8'), None)
            return True

        if plugintype[1] == 'sid':
            x_sid = ET.Element("state")
            x_sid.set('valueTree', '<?xml version="1.0" encoding="UTF-8"?>\n<state/>')
            x_sid.set('program', '0')
            params_various_inst.socalabs_addparam(x_sid, "a1", getparam('attack0'))
            params_various_inst.socalabs_addparam(x_sid, "a2", getparam('attack1'))
            params_various_inst.socalabs_addparam(x_sid, "a3", getparam('attack2'))
            params_various_inst.socalabs_addparam(x_sid, "cutoff", getparam('filterFC'))
            params_various_inst.socalabs_addparam(x_sid, "d1", getparam('decay0'))
            params_various_inst.socalabs_addparam(x_sid, "d2", getparam('decay1'))
            params_various_inst.socalabs_addparam(x_sid, "d3", getparam('decay2'))
            params_various_inst.socalabs_addparam(x_sid, "f1", getparam('filtered0'))
            params_various_inst.socalabs_addparam(x_sid, "f2", getparam('filtered1'))
            params_various_inst.socalabs_addparam(x_sid, "f3", getparam('filtered2'))
            params_various_inst.socalabs_addparam(x_sid, "fine1", 0.0)
            params_various_inst.socalabs_addparam(x_sid, "fine2", 0.0)
            params_various_inst.socalabs_addparam(x_sid, "fine3", 0.0)
            filterMode = getparam('filterMode')
            if filterMode == 0.0: params_various_inst.socalabs_addparam(x_sid, "highpass", 1.0)
            else: params_various_inst.socalabs_addparam(x_sid, "highpass", 0.0)
            if filterMode == 1.0: params_various_inst.socalabs_addparam(x_sid, "bandpass", 1.0)
            else: params_various_inst.socalabs_addparam(x_sid, "bandpass", 0.0)
            if filterMode == 2.0: params_various_inst.socalabs_addparam(x_sid, "lowpass", 1.0)
            else: params_various_inst.socalabs_addparam(x_sid, "lowpass", 0.0)
            params_various_inst.socalabs_addparam(x_sid, "output3", getparam('voice3Off'))
            params_various_inst.socalabs_addparam(x_sid, "pw1", getparam('pulsewidth0'))
            params_various_inst.socalabs_addparam(x_sid, "pw2", getparam('pulsewidth1'))
            params_various_inst.socalabs_addparam(x_sid, "pw3", getparam('pulsewidth2'))
            params_various_inst.socalabs_addparam(x_sid, "r1", getparam('release0'))
            params_various_inst.socalabs_addparam(x_sid, "r2", getparam('release1'))
            params_various_inst.socalabs_addparam(x_sid, "r3", getparam('release2'))
            params_various_inst.socalabs_addparam(x_sid, "reso", getparam('filterResonance'))
            params_various_inst.socalabs_addparam(x_sid, "ring1", getparam('ringmod0'))
            params_various_inst.socalabs_addparam(x_sid, "ring2", getparam('ringmod1'))
            params_various_inst.socalabs_addparam(x_sid, "ring3", getparam('ringmod2'))
            params_various_inst.socalabs_addparam(x_sid, "s1", getparam('sustain0'))
            params_various_inst.socalabs_addparam(x_sid, "s2", getparam('sustain1'))
            params_various_inst.socalabs_addparam(x_sid, "s3", getparam('sustain2'))
            params_various_inst.socalabs_addparam(x_sid, "sync1", getparam('sync0'))
            params_various_inst.socalabs_addparam(x_sid, "sync2", getparam('sync1'))
            params_various_inst.socalabs_addparam(x_sid, "sync3", getparam('sync2'))
            params_various_inst.socalabs_addparam(x_sid, "tune1", getparam('coarse0'))
            params_various_inst.socalabs_addparam(x_sid, "tune2", getparam('coarse1'))
            params_various_inst.socalabs_addparam(x_sid, "tune3", getparam('coarse2'))
            params_various_inst.socalabs_addparam(x_sid, "voices", 8.0)
            params_various_inst.socalabs_addparam(x_sid, "vol", getparam('volume'))
            params_various_inst.socalabs_addparam(x_sid, "w1", sid_shape(getparam('waveform0')))
            params_various_inst.socalabs_addparam(x_sid, "w2", sid_shape(getparam('waveform1')))
            params_various_inst.socalabs_addparam(x_sid, "w3", sid_shape(getparam('waveform2')))
            plugin_vst2.replace_data(cvpj_l, pluginid, 'any', 'SID', 'chunk', ET.tostring(x_sid, encoding='utf-8'), None)
            plugins.add_plug_data(cvpj_l, pluginid, 'middlenotefix', -12)
            return True

        if plugintype[1] == 'kicker':
            params_kickmess.initparams()
            params_kickmess.setvalue('pub', 'freq_start', getparam('startfreq'))
            params_kickmess.setvalue('pub', 'freq_end', getparam('endfreq'))
            params_kickmess.setvalue('pub', 'f_env_release', getparam('decay'))
            params_kickmess.setvalue('pub', 'dist_start', getparam('dist')/100)
            params_kickmess.setvalue('pub', 'dist_end', getparam('distend')/100)
            params_kickmess.setvalue('pub', 'gain', xtramath.clamp(getparam('gain'), 0, 2)/2)
            params_kickmess.setvalue('pub', 'env_slope', getparam('env'))
            params_kickmess.setvalue('pub', 'freq_slope', getparam('slope'))
            params_kickmess.setvalue('pub', 'noise', getparam('noise'))
            if getparam('startnote') == 1: params_kickmess.setvalue('pub', 'freq_note_start', 0.5)
            if getparam('endnote') == 1: params_kickmess.setvalue('pub', 'freq_note_end', 0.5)
            params_kickmess.setvalue('pub', 'phase_offs', getparam('click'))
            plugin_vst2.replace_data(cvpj_l, pluginid, 'any', 'Kickmess (VST)', 'chunk', params_kickmess.getparams(), None)
            plugins.add_plug_data(cvpj_l, pluginid, 'middlenotefix', -12)
            return True

        if plugintype[1] == 'lb302':
            params_vital.create()
            lb302_shape = getparam('shape')
            if lb302_shape == 0: vital_shape = wave.create_wave('saw', 0, None)
            if lb302_shape == 1: vital_shape = wave.create_wave('triangle', 0, None)
            if lb302_shape == 2: vital_shape = wave.create_wave('square', 0, 0.5)
            if lb302_shape == 3: vital_shape = wave.create_wave('square_roundend', 0, None)
            if lb302_shape == 4: vital_shape = wave.create_wave('mooglike', 0, None)
            if lb302_shape == 5: vital_shape = wave.create_wave('sine', 0, None)
            if lb302_shape == 6: vital_shape = wave.create_wave('exp', 0, None)
            if lb302_shape == 8: vital_shape = wave.create_wave('saw', 0, None)
            if lb302_shape == 9: vital_shape = wave.create_wave('square', 0, 0.5)
            if lb302_shape == 10: vital_shape = wave.create_wave('triangle', 0, None)
            if lb302_shape == 11: vital_shape = wave.create_wave('mooglike', 0, None)
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
            vitaldata = params_vital.getdata()
            plugin_vst2.replace_data(cvpj_l, pluginid, 'any', 'Vital', 'chunk', vitaldata.encode('utf-8'), None)
            plugins.add_plug_data(cvpj_l, pluginid, 'middlenotefix', -12)
            return True

        if plugintype[1] == 'zynaddsubfx':
            zasfxdata = plugins.get_plug_dataval(cvpj_l, pluginid, 'data', '')
            zasfxdatastart = '<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE ZynAddSubFX-data>' 
            zasfxdatafixed = zasfxdatastart.encode('utf-8') + base64.b64decode(zasfxdata)
            plugin_vst2.replace_data(cvpj_l, pluginid, 'any', 'ZynAddSubFX', 'chunk', zasfxdatafixed, None)
            return True

        if plugintype[1] == 'spectrumanalyzer':
            x_spectrumanalyzer = ET.Element("state")
            x_spectrumanalyzer.set('valueTree', '<?xml version="1.0" encoding="UTF-8"?>\n<state width="400" height="328"/>')
            x_spectrumanalyzer.set('program', '0')
            params_various_inst.socalabs_addparam(x_spectrumanalyzer, "mode", 0.0)
            params_various_inst.socalabs_addparam(x_spectrumanalyzer, "log", 1.0)
            plugin_vst2.replace_data(cvpj_l, pluginid, 'any', 'SpectrumAnalyzer', 'chunk', ET.tostring(x_spectrumanalyzer, encoding='utf-8'), None)
            return True

        if plugintype[1] == 'waveshaper':
            waveshapebytes = base64.b64decode(plugins.get_plug_dataval(cvpj_l, pluginid, 'waveShape', ''))
            waveshapepoints = [struct.unpack('f', waveshapebytes[i:i+4]) for i in range(0, len(waveshapebytes), 4)]
            params_various_fx.wolfshaper_init()
            for pointnum in range(50):
                pointdata = waveshapepoints[pointnum*4][0]
                params_various_fx.wolfshaper_addpoint(pointnum/49,pointdata,0.5,0)
            plugin_vst2.replace_data(cvpj_l, pluginid, 'any', 'Wolf Shaper', 'chunk', data_nullbytegroup.make(params_various_fx.wolfshaper_get()), None)
            return True
