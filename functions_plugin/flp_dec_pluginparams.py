# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import base64
import struct
import os
from functions import data_bytes
from functions import plugins
from functions import plugin_vst2
from functions import debug

def decode_pointdata(fl_plugstr):
    autoheader = struct.unpack('bii', fl_plugstr.read(12))
    pointdata_table = []

    positionlen = 0
    for num in range(autoheader[2]):
        chunkdata = struct.unpack('ddfbbbb', fl_plugstr.read(24))
        positionlen += round(chunkdata[0], 6)
        pointdata_table.append( [positionlen, chunkdata[1:], 0.0, 0] )
        if num != 0:
            pointdata_table[num-1][2] = chunkdata[2]
            pointdata_table[num-1][3] = chunkdata[3]

    fl_plugstr.read(20).hex()
    return pointdata_table

envshapes = {
    0: 'normal',
    1: 'doublecurve',
    2: 'instant',
    3: 'stairs',
    4: 'smooth_stairs',
    5: 'pulse',
    6: 'wave',
    7: 'curve2',
    8: 'doublecurve2',
    9: 'halfsine',
    10: 'smooth',
    11: 'curve3',
    12: 'doublecurve3',
}

def getparams(cvpj_l, pluginid, pluginname, chunkdata, foldername):
    fl_plugstr = data_bytes.to_bytesio(chunkdata)
    pluginname = pluginname.lower()

    # ------------------------------------------------------------------------------------------- Inst
    if pluginname == '3x osc':
        fl_plugstr.read(4)
        osc1_pan, osc1_shape, osc1_coarse, osc1_fine, osc1_ofs, osc1_detune, osc1_mixlevel = struct.unpack('iiiiiii', fl_plugstr.read(28))
        plugins.add_plug_param(cvpj_l, pluginid, 'osc1_pan', osc1_pan, 'int', "Osc 1 Pan")
        plugins.add_plug_param(cvpj_l, pluginid, 'osc1_shape', osc1_shape, 'int', "Osc 1 Shape")
        plugins.add_plug_param(cvpj_l, pluginid, 'osc1_coarse', osc1_coarse, 'int', "Osc 1 Coarse")
        plugins.add_plug_param(cvpj_l, pluginid, 'osc1_fine', osc1_fine, 'int', "Osc 1 Fine")
        plugins.add_plug_param(cvpj_l, pluginid, 'osc1_ofs', osc1_ofs, 'int', "Osc 1 Offset")
        plugins.add_plug_param(cvpj_l, pluginid, 'osc1_detune', osc1_detune, 'int', "Osc 1 Detune")
        plugins.add_plug_param(cvpj_l, pluginid, 'osc1_mixlevel', osc1_mixlevel, 'int', "Osc 1 Mix Level")
        osc2_pan, osc2_shape, osc2_coarse, osc2_fine, osc2_ofs, osc2_detune, osc2_mixlevel = struct.unpack('iiiiiii', fl_plugstr.read(28))
        plugins.add_plug_param(cvpj_l, pluginid, 'osc2_pan', osc2_pan, 'int', "Osc 2 Pan")
        plugins.add_plug_param(cvpj_l, pluginid, 'osc2_shape', osc2_shape, 'int', "Osc 2 Shape")
        plugins.add_plug_param(cvpj_l, pluginid, 'osc2_coarse', osc2_coarse, 'int', "Osc 2 Coarse")
        plugins.add_plug_param(cvpj_l, pluginid, 'osc2_fine', osc2_fine, 'int', "Osc 2 Fine")
        plugins.add_plug_param(cvpj_l, pluginid, 'osc2_ofs', osc2_ofs, 'int', "Osc 2 Offset")
        plugins.add_plug_param(cvpj_l, pluginid, 'osc2_detune', osc2_detune, 'int', "Osc 2 Detune")
        plugins.add_plug_param(cvpj_l, pluginid, 'osc2_mixlevel', osc2_mixlevel, 'int', "Osc 2 Mix Level")
        osc3_pan, osc3_shape, osc3_coarse, osc3_fine, osc3_ofs, osc3_detune, phase_rand = struct.unpack('iiiiiii', fl_plugstr.read(28))
        plugins.add_plug_param(cvpj_l, pluginid, 'osc3_pan', osc3_pan, 'int', "Osc 3 Pan")
        plugins.add_plug_param(cvpj_l, pluginid, 'osc3_shape', osc3_shape, 'int', "Osc 3 Shape")
        plugins.add_plug_param(cvpj_l, pluginid, 'osc3_coarse', osc3_coarse, 'int', "Osc 3 Coarse")
        plugins.add_plug_param(cvpj_l, pluginid, 'osc3_fine', osc3_fine, 'int', "Osc 3 Fine")
        plugins.add_plug_param(cvpj_l, pluginid, 'osc3_ofs', osc3_ofs, 'int', "Osc 3 Offset")
        plugins.add_plug_param(cvpj_l, pluginid, 'osc3_detune', osc3_detune, 'int', "Osc 3 Detune")
        plugins.add_plug_param(cvpj_l, pluginid, 'phase_rand', phase_rand, 'int', "Phase Rand")
        osc1_invert, osc2_invert, osc3_invert, osc3_am = struct.unpack('bbbb', fl_plugstr.read(4))
        plugins.add_plug_param(cvpj_l, pluginid, 'osc1_invert', osc1_invert, 'bool', "Osc 3 Invert")
        plugins.add_plug_param(cvpj_l, pluginid, 'osc2_invert', osc2_invert, 'bool', "Osc 3 Invert")
        plugins.add_plug_param(cvpj_l, pluginid, 'osc3_invert', osc3_invert, 'bool', "Osc 3 Invert")
        plugins.add_plug_param(cvpj_l, pluginid, 'osc3_am', osc3_am, 'bool', "Osc 3 AM")

    elif pluginname == 'fruit kick':
        flplugvals = struct.unpack('iiiiiii', fl_plugstr.read(28))
        plugins.add_plug_param(cvpj_l, pluginid, 'max_freq', flplugvals[1], 'int', "Max Freq")
        plugins.add_plug_param(cvpj_l, pluginid, 'min_freq', flplugvals[2], 'int', "Min Freq")
        plugins.add_plug_param(cvpj_l, pluginid, 'decay_freq', flplugvals[3], 'int', "Decay Freq")
        plugins.add_plug_param(cvpj_l, pluginid, 'decay_vol', flplugvals[4], 'int', "Decay Vol")
        plugins.add_plug_param(cvpj_l, pluginid, 'osc_click', flplugvals[5], 'int', "Osc Click")
        plugins.add_plug_param(cvpj_l, pluginid, 'osc_dist', flplugvals[6], 'int', "Osc Dist")

    elif pluginname == 'fruity dx10':
        int.from_bytes(fl_plugstr.read(4), "little")
        fldx_amp_att, fldx_amp_dec, fldx_amp_rel, fldx_mod_course = struct.unpack('iiii', fl_plugstr.read(16))
        fldx_mod_fine, fldx_mod_init, fldx_mod_time, fldx_mod_sus = struct.unpack('iiii', fl_plugstr.read(16))
        fldx_mod_rel, fldx_mod_velsen, fldx_vibrato, fldx_waveform = struct.unpack('iiii', fl_plugstr.read(16))
        fldx_mod_thru, fldx_lforate, fldx_mod2_course, fldx_mod2_fine = struct.unpack('iiii', fl_plugstr.read(16))
        fldx_mod2_init, fldx_mod2_time, fldx_mod2_sus, fldx_mod2_rel = struct.unpack('iiii', fl_plugstr.read(16))
        fldx_mod2_velsen = int.from_bytes(fl_plugstr.read(4), "little")
        fldx_octave = int.from_bytes(fl_plugstr.read(4), "little", signed="True")
        plugins.add_plug_param(cvpj_l, pluginid, 'amp_att', fldx_amp_att, 'int', "Attack")
        plugins.add_plug_param(cvpj_l, pluginid, 'amp_dec', fldx_amp_dec, 'int', "Decay")
        plugins.add_plug_param(cvpj_l, pluginid, 'amp_rel', fldx_amp_rel, 'int', "Release")
        plugins.add_plug_param(cvpj_l, pluginid, 'mod_course', fldx_mod_course, 'int', "Coarse")
        plugins.add_plug_param(cvpj_l, pluginid, 'mod_fine', fldx_mod_fine, 'int', "Fine")
        plugins.add_plug_param(cvpj_l, pluginid, 'mod_init', fldx_mod_init, 'int', "Mod Init")
        plugins.add_plug_param(cvpj_l, pluginid, 'mod_time', fldx_mod_time, 'int', "Mod Dec")
        plugins.add_plug_param(cvpj_l, pluginid, 'mod_sus', fldx_mod_sus, 'int', "Mod Sus")
        plugins.add_plug_param(cvpj_l, pluginid, 'mod_rel', fldx_mod_rel, 'int', "Mod Rel")
        plugins.add_plug_param(cvpj_l, pluginid, 'velsen', fldx_mod_velsen, 'int', "Vel Sen")
        plugins.add_plug_param(cvpj_l, pluginid, 'vibrato', fldx_vibrato, 'int', "Vibrato")
        plugins.add_plug_param(cvpj_l, pluginid, 'waveform', fldx_waveform, 'int', "Waveform")
        plugins.add_plug_param(cvpj_l, pluginid, 'mod_thru', fldx_mod_thru, 'int', "Mod Thru")
        plugins.add_plug_param(cvpj_l, pluginid, 'lforate', fldx_lforate, 'int', "LFO Rate")
        plugins.add_plug_param(cvpj_l, pluginid, 'mod2_course', fldx_mod2_course, 'int', "Mod 2 Coarse")
        plugins.add_plug_param(cvpj_l, pluginid, 'mod2_fine', fldx_mod2_fine, 'int', "Mod 2 Fine")
        plugins.add_plug_param(cvpj_l, pluginid, 'mod2_init', fldx_mod2_init, 'int', "Mod 2 Init")
        plugins.add_plug_param(cvpj_l, pluginid, 'mod2_time', fldx_mod2_time, 'int', "Mod 2 Dec")
        plugins.add_plug_param(cvpj_l, pluginid, 'mod2_sus', fldx_mod2_sus, 'int', "Mod 2 Sus")
        plugins.add_plug_param(cvpj_l, pluginid, 'mod2_rel', fldx_mod2_rel, 'int', "Mod 2 Rel")
        plugins.add_plug_param(cvpj_l, pluginid, 'octave', fldx_octave, 'int', "Octave")

    elif pluginname == 'plucked!':
        flplugvals = struct.unpack('iiiii', chunkdata)
        plugins.add_plug_param(cvpj_l, pluginid, 'decay', flplugvals[0], 'int', 'Decay')
        plugins.add_plug_param(cvpj_l, pluginid, 'color', flplugvals[1], 'int', 'Color')
        plugins.add_plug_param(cvpj_l, pluginid, 'norm_decay', flplugvals[2], 'bool', 'Normalize Decay')
        plugins.add_plug_param(cvpj_l, pluginid, 'release', flplugvals[3], 'bool', 'Short Release')
        plugins.add_plug_param(cvpj_l, pluginid, 'wide', flplugvals[4], 'bool', 'Widen')

    elif pluginname in ['wasp', 'wasp xt']:
        wasp_unk = int.from_bytes(fl_plugstr.read(4), "little")
        wasp_1_shape, wasp_1_crs, wasp_1_fine, wasp_2_shape, wasp_2_crs, wasp_2_fine = struct.unpack('iiiiii', fl_plugstr.read(24))
        plugins.add_plug_param(cvpj_l, pluginid, '1_shape', wasp_1_shape, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, '1_crs', wasp_1_crs, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, '1_fine', wasp_1_fine, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, '2_shape', wasp_2_shape, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, '2_crs', wasp_2_crs, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, '2_fine', wasp_2_fine, 'int', "")
        wasp_3_shape, wasp_3_amt, wasp_12_fade, wasp_pw, wasp_fm, wasp_ringmod = struct.unpack('iiiiii', fl_plugstr.read(24))
        plugins.add_plug_param(cvpj_l, pluginid, '3_shape', wasp_3_shape, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, '3_amt', wasp_3_amt, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, '12_fade', wasp_12_fade, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, 'pw', wasp_pw, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, 'fm', wasp_fm, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, 'ringmod', wasp_ringmod, 'int', "")
        wasp_amp_A, wasp_amp_S, wasp_amp_D, wasp_amp_R, wasp_fil_A, wasp_fil_S, wasp_fil_D, wasp_fil_R = struct.unpack('iiiiiiii', fl_plugstr.read(32))
        plugins.add_plug_param(cvpj_l, pluginid, 'amp_A', wasp_amp_A, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, 'amp_S', wasp_amp_S, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, 'amp_D', wasp_amp_D, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, 'amp_R', wasp_amp_R, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, 'fil_A', wasp_fil_A, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, 'fil_S', wasp_fil_S, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, 'fil_D', wasp_fil_D, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, 'fil_R', wasp_fil_R, 'int', "")
        wasp_fil_kbtrack, wasp_fil_qtype, wasp_fil_cut, wasp_fil_res, wasp_fil_env = struct.unpack('iiiii', fl_plugstr.read(20))
        plugins.add_plug_param(cvpj_l, pluginid, 'fil_kbtrack', wasp_fil_kbtrack, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, 'fil_qtype', wasp_fil_qtype, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, 'fil_cut', wasp_fil_cut, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, 'fil_res', wasp_fil_res, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, 'fil_env', wasp_fil_env, 'int', "")
        for lfonum in range(2):
            wasp_lfo_shape, wasp_lfo_target, wasp_lfo_amt, wasp_lfo_spd, wasp_lfo_sync, wasp_lfo_reset = struct.unpack('i'*6, fl_plugstr.read(24))
            plugins.add_plug_param(cvpj_l, pluginid, 'lfo'+str(lfonum+1)+'_shape', wasp_lfo_shape, 'int', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'lfo'+str(lfonum+1)+'_target', wasp_lfo_target, 'int', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'lfo'+str(lfonum+1)+'_amt', wasp_lfo_amt, 'int', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'lfo'+str(lfonum+1)+'_spd', wasp_lfo_spd, 'int', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'lfo'+str(lfonum+1)+'_sync', wasp_lfo_sync, 'int', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'lfo'+str(lfonum+1)+'_reset', wasp_lfo_reset, 'int', "")
        wasp_dist_on, wasp_dist_drv, wasp_dist_tone, wasp_dualvoice = struct.unpack('iiii', fl_plugstr.read(16))
        plugins.add_plug_param(cvpj_l, pluginid, 'dist_on', wasp_dist_on, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, 'dist_drv', wasp_dist_drv, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, 'dist_tone', wasp_dist_tone, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, 'dualvoice', wasp_dualvoice, 'int', "")

        if pluginname == 'wasp xt':
            waspxt_amp, waspxt_analog, waspxt_me_atk, waspxt_me_dec = struct.unpack('i'*4, fl_plugstr.read(16))
            plugins.add_plug_param(cvpj_l, pluginid, 'amp', waspxt_amp, 'int', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'analog', waspxt_analog, 'int', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'me_atk', waspxt_me_atk, 'int', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'me_dec', waspxt_me_dec, 'int', "")
            waspxt_me_amt, waspxt_me_1lvl, waspxt_me_2pitch, waspxt_me_1ami = struct.unpack('i'*4, fl_plugstr.read(16))
            plugins.add_plug_param(cvpj_l, pluginid, 'me_amt', waspxt_me_amt, 'int', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'me_1lvl', waspxt_me_1lvl, 'int', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'me_2pitch', waspxt_me_2pitch, 'int', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'me_1ami', waspxt_me_1ami, 'int', "")
            waspxt_me_pw, waspxt_vol, waspxt_lfo1_delay, waspxt_lfo2_delay = struct.unpack('i'*4, fl_plugstr.read(16))
            plugins.add_plug_param(cvpj_l, pluginid, 'me_pw', waspxt_me_pw, 'int', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'vol', waspxt_vol, 'int', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'lfo1_delay', waspxt_lfo1_delay, 'int', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'lfo2_delay', waspxt_lfo2_delay, 'int', "")
            waspxt_me_filter, waspxt_wnoise = struct.unpack('i'*2, fl_plugstr.read(8))
            plugins.add_plug_param(cvpj_l, pluginid, 'me_filter', waspxt_me_filter, 'int', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'wnoise', waspxt_wnoise, 'int', "")

    elif pluginname.lower() == 'simsynth':
        for oscnum in range(3):
            osc_pw, osc_crs, osc_fine, osc_lvl, osc_lfo, osc_env, osc_shape = struct.unpack('ddddddd', fl_plugstr.read(56))
            plugins.add_plug_param(cvpj_l, pluginid, 'osc'+str(oscnum+1)+'_pw', osc_pw, 'float', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'osc'+str(oscnum+1)+'_crs', osc_crs, 'float', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'osc'+str(oscnum+1)+'_fine', osc_fine, 'float', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'osc'+str(oscnum+1)+'_lvl', osc_lvl, 'float', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'osc'+str(oscnum+1)+'_lfo', osc_lfo, 'float', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'osc'+str(oscnum+1)+'_env', osc_env, 'float', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'osc'+str(oscnum+1)+'_shape', osc_shape, 'float', "")

        lfo_del, lfo_rate, unused, lfo_shape = struct.unpack('dddd', fl_plugstr.read(32))
        plugins.add_plug_param(cvpj_l, pluginid, 'lfo_del', lfo_del, 'float', "")
        plugins.add_plug_param(cvpj_l, pluginid, 'lfo_rate', lfo_rate, 'float', "")
        plugins.add_plug_param(cvpj_l, pluginid, 'lfo_shape', lfo_shape, 'float', "")
        UNK1, svf_cut, svf_emph, svf_env = struct.unpack('dddd', fl_plugstr.read(32))
        plugins.add_plug_param(cvpj_l, pluginid, 'svf_cut', svf_cut, 'float', "")
        plugins.add_plug_param(cvpj_l, pluginid, 'svf_emph', svf_emph, 'float', "")
        plugins.add_plug_param(cvpj_l, pluginid, 'svf_env', svf_env, 'float', "")
        svf_lfo, svf_kb, UNK2, svf_high = struct.unpack('dddd', fl_plugstr.read(32))
        plugins.add_plug_param(cvpj_l, pluginid, 'svf_lfo', svf_lfo, 'float', "")
        plugins.add_plug_param(cvpj_l, pluginid, 'svf_kb', svf_kb, 'float', "")
        plugins.add_plug_param(cvpj_l, pluginid, 'svf_high', svf_high, 'float', "")
        svf_band, UNK3, amp_att, amp_dec = struct.unpack('dddd', fl_plugstr.read(32))
        plugins.add_plug_param(cvpj_l, pluginid, 'svf_band', svf_band, 'float', "")
        plugins.add_plug_param(cvpj_l, pluginid, 'amp_att', amp_att, 'float', "")
        plugins.add_plug_param(cvpj_l, pluginid, 'amp_dec', amp_dec, 'float', "")
        amp_sus, amp_rel, amp_lvl, UNK4 = struct.unpack('dddd', fl_plugstr.read(32))
        plugins.add_plug_param(cvpj_l, pluginid, 'amp_sus', amp_sus, 'float', "")
        plugins.add_plug_param(cvpj_l, pluginid, 'amp_rel', amp_rel, 'float', "")
        plugins.add_plug_param(cvpj_l, pluginid, 'amp_lvl', amp_lvl, 'float', "")
        svf_att, svf_dec, svf_sus, svf_rel = struct.unpack('dddd', fl_plugstr.read(32))
        plugins.add_plug_param(cvpj_l, pluginid, 'svf_att', svf_att, 'float', "")
        plugins.add_plug_param(cvpj_l, pluginid, 'svf_dec', svf_dec, 'float', "")
        plugins.add_plug_param(cvpj_l, pluginid, 'svf_sus', svf_sus, 'float', "")
        plugins.add_plug_param(cvpj_l, pluginid, 'svf_rel', svf_rel, 'float', "")
        fl_plugstr.read(64)
        fl_plugstr.read(12)
        for oscnum in range(3):
            osc_on, osc_o1, osc_o2, osc_warm = struct.unpack('IIII', fl_plugstr.read(16))
            plugins.add_plug_param(cvpj_l, pluginid, 'osc'+str(oscnum+1)+'_on', osc_on, 'bool', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'osc'+str(oscnum+1)+'_o1', osc_o1, 'bool', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'osc'+str(oscnum+1)+'_o2', osc_o2, 'bool', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'osc'+str(oscnum+1)+'_warm', osc_warm, 'bool', "")

        lfo_on, lfo_retrigger, svf_on, UNK5 = struct.unpack('IIII', fl_plugstr.read(16))
        plugins.add_plug_param(cvpj_l, pluginid, 'lfo_on', lfo_on, 'bool', "")
        plugins.add_plug_param(cvpj_l, pluginid, 'lfo_retrigger', lfo_retrigger, 'bool', "")
        plugins.add_plug_param(cvpj_l, pluginid, 'svf_on', svf_on, 'bool', "")
        lfo_trackamp, UNK6, chorus_on, UNK7 = struct.unpack('IIII', fl_plugstr.read(16))
        plugins.add_plug_param(cvpj_l, pluginid, 'lfo_trackamp', lfo_trackamp, 'bool', "")
        plugins.add_plug_param(cvpj_l, pluginid, 'chorus_on', chorus_on, 'bool', "")


    elif pluginname == 'wasp xt':
        waspxt_amp, waspxt_analog, waspxt_me_atk, waspxt_me_dec = struct.unpack('i'*4, fl_plugstr.read(16))
        plugins.add_plug_param(cvpj_l, pluginid, 'amp', waspxt_amp, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, 'analog', waspxt_analog, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, 'me_atk', waspxt_me_atk, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, 'me_dec', waspxt_me_dec, 'int', "")
        waspxt_me_amt, waspxt_me_1lvl, waspxt_me_2pitch, waspxt_me_1ami = struct.unpack('i'*4, fl_plugstr.read(16))
        plugins.add_plug_param(cvpj_l, pluginid, 'me_amt', waspxt_me_amt, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, 'me_1lvl', waspxt_me_1lvl, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, 'me_2pitch', waspxt_me_2pitch, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, 'me_1ami', waspxt_me_1ami, 'int', "")
        waspxt_me_pw, waspxt_vol, waspxt_lfo1_delay, waspxt_lfo2_delay = struct.unpack('i'*4, fl_plugstr.read(16))
        plugins.add_plug_param(cvpj_l, pluginid, 'me_pw', waspxt_me_pw, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, 'vol', waspxt_vol, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, 'lfo1_delay', waspxt_lfo1_delay, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, 'lfo2_delay', waspxt_lfo2_delay, 'int', "")
        waspxt_me_filter, waspxt_wnoise = struct.unpack('i'*2, fl_plugstr.read(8))
        plugins.add_plug_param(cvpj_l, pluginid, 'me_filter', waspxt_me_filter, 'int', "")
        plugins.add_plug_param(cvpj_l, pluginid, 'wnoise', waspxt_wnoise, 'int', "")

    elif pluginname in ['fruity soundfont player', 'soundfont player']:
        # flsf_asdf_A max 5940 - flsf_asdf_D max 5940 - flsf_asdf_S max 127 - flsf_asdf_R max 5940
        # flsf_lfo_predelay max 5900 - flsf_lfo_amount max 127 - flsf_lfo_speed max 127 - flsf_cutoff max 127
        flsf_unk, flsf_patch, flsf_bank, flsf_reverb_sendlvl, flsf_chorus_sendlvl, flsf_mod = struct.unpack('iiiiii', fl_plugstr.read(24))
        flsf_asdf_A, flsf_asdf_D, flsf_asdf_S, flsf_asdf_R = struct.unpack('iiii', fl_plugstr.read(16))
        flsf_lfo_predelay, flsf_lfo_amount, flsf_lfo_speed, flsf_cutoff = struct.unpack('iiii', fl_plugstr.read(16))
        flsf_filelen = int.from_bytes(fl_plugstr.read(1), "little")
        flsf_filename = fl_plugstr.read(flsf_filelen).decode('utf-8')
        flsf_reverb_sendto, flsf_reverb_builtin = struct.unpack('ib', fl_plugstr.read(5))
        flsf_chorus_sendto, flsf_chorus_builtin = struct.unpack('ib', fl_plugstr.read(5))
        flsf_hqrender = int.from_bytes(fl_plugstr.read(1), "little")

        plugins.add_plug(cvpj_l, pluginid, 'soundfont2', None)

        plugins.add_plug_data(cvpj_l, pluginid, 'reverb_enabled', flsf_reverb_builtin)
        plugins.add_plug_data(cvpj_l, pluginid, 'chorus_enabled', flsf_chorus_builtin)

        asdflfo_att = 0
        asdflfo_dec = 0
        asdflfo_sus = 1
        asdflfo_rel = 0
        if flsf_asdf_A != -1: asdflfo_att = flsf_asdf_A/1024
        if flsf_asdf_D != -1: asdflfo_dec = flsf_asdf_D/1024
        if flsf_asdf_S != -1: asdflfo_sus = flsf_asdf_S/127
        if flsf_asdf_R != -1: asdflfo_rel = flsf_asdf_R/1024

        plugins.add_plug_data(cvpj_l, pluginid, 'file', flsf_filename)
        plugins.add_asdr_env(cvpj_l, pluginid, 'vol', 0, asdflfo_att, 0, asdflfo_dec, asdflfo_sus, asdflfo_rel, 1)

        if flsf_patch > 127:
            plugins.add_plug_data(cvpj_l, pluginid, 'bank', 128)
            plugins.add_plug_data(cvpj_l, pluginid, 'patch', flsf_patch-128)
        else:
            plugins.add_plug_data(cvpj_l, pluginid, 'bank', flsf_bank)
            plugins.add_plug_data(cvpj_l, pluginid, 'patch', flsf_patch)
        
        pitch_amount = 0
        pitch_predelay = 0
        pitch_speed = 1

        if flsf_lfo_amount != -128: pitch_amount = flsf_lfo_amount/128
        if flsf_lfo_predelay != -1: pitch_predelay = flsf_lfo_predelay/256
        if flsf_lfo_speed != -1: pitch_speed = 1/(flsf_lfo_speed/6)

        plugins.add_lfo(cvpj_l, pluginid, 'pitch', 'sine', 'seconds', 
            pitch_speed, pitch_predelay, 0, pitch_amount)

    elif pluginname == 'fruity slicer':
        plugins.add_plug(cvpj_l, pluginid, 'sampler', 'slicer')
        fl_plugstr.read(4)
        slicer_beats = struct.unpack('f', fl_plugstr.read(4))[0]
        slicer_bpm = struct.unpack('f', fl_plugstr.read(4))[0]
        slicer_pitch, slicer_fitlen, slicer_unk1, slicer_att, slicer_dec = struct.unpack('iiiii', fl_plugstr.read(20))

        plugins.add_plug_data(cvpj_l, pluginid, 'pitch', slicer_pitch/100)

        slicer_filelen = int.from_bytes(fl_plugstr.read(1), "little")
        slicer_filename = fl_plugstr.read(slicer_filelen).decode('utf-8')
        if slicer_filename != "": 
            plugins.add_plug_data(cvpj_l, pluginid, 'file', slicer_filename)
        slicer_numslices = int.from_bytes(fl_plugstr.read(4), "little")

        cvpj_slices = []
        for _ in range(slicer_numslices):
            sd = {}
            slicer_slicenamelen = int.from_bytes(fl_plugstr.read(1), "little")
            slicer_slicename = fl_plugstr.read(slicer_slicenamelen).decode('utf-8')
            slicer_s_slice = struct.unpack('iihBBB', fl_plugstr.read(13))
            if slicer_slicename != "": sd['file'] = slicer_slicename
            sd['pos'] = slicer_s_slice[0]
            if slicer_s_slice[1] != -1: sd['note'] = slicer_s_slice[1]
            sd['reverse'] = slicer_s_slice[5]
            cvpj_slices.append(sd)

        for slicenum in range(len(cvpj_slices)):
            if slicenum-1 >= 0 and slicenum != len(cvpj_slices): cvpj_slices[slicenum-1]['end'] = cvpj_slices[slicenum]['pos']-1
            if slicenum == len(cvpj_slices)-1: cvpj_slices[slicenum]['end'] = cvpj_slices[slicenum]['pos']+100000000

        plugins.add_plug_data(cvpj_l, pluginid, 'trigger', 'oneshot')
        plugins.add_plug_data(cvpj_l, pluginid, 'bpm', slicer_bpm)
        plugins.add_plug_data(cvpj_l, pluginid, 'beats', slicer_beats)
        plugins.add_plug_data(cvpj_l, pluginid, 'slices', cvpj_slices)

    # ------------------------------------------------------------------------------------------- FX

    elif pluginname == 'effector':
        chunkdata = data_bytes.riff_read(chunkdata, 0)
        flplugvals = struct.unpack('fffffffffffff', chunkdata[0][1][256:])
        plugins.add_plug_param(cvpj_l, pluginid, 'effect', flplugvals[1], 'float', "Effect")
        plugins.add_plug_param(cvpj_l, pluginid, 'bypass', flplugvals[2], 'float', "Bypass")
        plugins.add_plug_param(cvpj_l, pluginid, 'wet', flplugvals[3], 'float', "Wet")
        plugins.add_plug_param(cvpj_l, pluginid, 'x_param', flplugvals[4], 'float', "X Param")
        plugins.add_plug_param(cvpj_l, pluginid, 'y_param', flplugvals[5], 'float', "Y Param")
        plugins.add_plug_param(cvpj_l, pluginid, 'mod_rate', flplugvals[6], 'float', "Mod Rate")
        plugins.add_plug_param(cvpj_l, pluginid, 'tempo', flplugvals[7], 'float', "Tempo Reduce")
        plugins.add_plug_param(cvpj_l, pluginid, 'x_mod', flplugvals[8], 'float', "X Mod")
        plugins.add_plug_param(cvpj_l, pluginid, 'y_mod', flplugvals[9], 'float', "Y Mod")
        plugins.add_plug_param(cvpj_l, pluginid, 'mod_shape', flplugvals[10], 'float', "Mod Shape")
        plugins.add_plug_param(cvpj_l, pluginid, 'input_level', flplugvals[11], 'float', "Input Level")
        plugins.add_plug_param(cvpj_l, pluginid, 'output_gain', flplugvals[12], 'float', "Output Gain")

    elif pluginname == 'frequency shifter':
        version = fl_plugstr.read(4)
        flplugvals = struct.unpack('i'*12, fl_plugstr.read())
        plugins.add_plug_param(cvpj_l, pluginid, 'mix', flplugvals[0], 'float', "Mix")
        plugins.add_plug_param(cvpj_l, pluginid, 'type', flplugvals[1], 'float', "Type")
        plugins.add_plug_param(cvpj_l, pluginid, 'frequency', flplugvals[2], 'float', "Frequency")
        plugins.add_plug_param(cvpj_l, pluginid, 'lr_phase', flplugvals[3], 'float', "L/R Phase")
        plugins.add_plug_param(cvpj_l, pluginid, 'shape_left', flplugvals[4], 'float', "Shape Left")
        plugins.add_plug_param(cvpj_l, pluginid, 'shape_right', flplugvals[5], 'float', "Shape Right")
        plugins.add_plug_param(cvpj_l, pluginid, 'feedback', flplugvals[6], 'float', "Feedback")
        plugins.add_plug_param(cvpj_l, pluginid, 'stereo', flplugvals[7], 'float', "Stereo")
        plugins.add_plug_param(cvpj_l, pluginid, 'freqtype', flplugvals[8], 'float', "Freq Type")
        plugins.add_plug_param(cvpj_l, pluginid, 'start_phase', flplugvals[9], 'float', "Start Phase")
        plugins.add_plug_param(cvpj_l, pluginid, 'mixer_track', flplugvals[11], 'float', "Mixer Track")

    # ------------------------------------------------------------------------------------------- F

    elif pluginname == 'fruity 7 band eq':
        flplugvals = struct.unpack('<iiiiiiii', chunkdata)
        for paramnum in range(7):
            plugins.add_plug_param(cvpj_l, pluginid, str(paramnum+1), flplugvals[paramnum+1], 'int', 'Band '+str(paramnum+1))

    elif pluginname == 'fruity balance':
        flplugvals = struct.unpack('<ii', chunkdata)
        plugins.add_plug_param(cvpj_l, pluginid, 'pan', flplugvals[0], 'int', 'Balance')
        plugins.add_plug_param(cvpj_l, pluginid, 'vol', flplugvals[1], 'int', 'Volume')

    elif pluginname == 'fruity bass boost':
        flplugvals = struct.unpack('<iii', chunkdata)
        plugins.add_plug_param(cvpj_l, pluginid, 'freq', flplugvals[1], 'int', 'Frequency')
        plugins.add_plug_param(cvpj_l, pluginid, 'amount', flplugvals[2], 'int', 'Amount')

    elif pluginname == 'fruity big clock':
        version = fl_plugstr.read(1)[0]
        if version == 2:
            plugins.add_plug_data(cvpj_l, pluginid, 'beats', fl_plugstr.read(1)[0])
            plugins.add_plug_data(cvpj_l, pluginid, 'color', fl_plugstr.read(1)[0])

    elif pluginname == 'fruity blood overdrive':
        flplugvals = struct.unpack('IIIIIIIII', chunkdata)
        plugins.add_plug_param(cvpj_l, pluginid, 'preband', flplugvals[1], 'int', 'PreBand')
        plugins.add_plug_param(cvpj_l, pluginid, 'color', flplugvals[2], 'int', 'Color')
        plugins.add_plug_param(cvpj_l, pluginid, 'preamp', flplugvals[3], 'int', 'PreAmp')
        plugins.add_plug_param(cvpj_l, pluginid, 'x100', flplugvals[4], 'bool', 'x 100')
        plugins.add_plug_param(cvpj_l, pluginid, 'postfilter', flplugvals[5], 'int', 'PostFilter')
        plugins.add_plug_param(cvpj_l, pluginid, 'postgain', flplugvals[6], 'int', 'PostGain')

    elif pluginname == 'fruity center':
        flplugvals = struct.unpack('II', chunkdata)
        plugins.add_plug_param(cvpj_l, pluginid, 'on', flplugvals[1], 'bool', 'Status')

    elif pluginname == 'fruity chorus':
        flplugvals = struct.unpack('I'*13, chunkdata)
        plugins.add_plug_param(cvpj_l, pluginid, 'delay', flplugvals[1], 'int', 'Delay')
        plugins.add_plug_param(cvpj_l, pluginid, 'depth', flplugvals[2], 'int', 'Depth')
        plugins.add_plug_param(cvpj_l, pluginid, 'stereo', flplugvals[3], 'int', 'Stereo')
        plugins.add_plug_param(cvpj_l, pluginid, 'lfo1_freq', flplugvals[4], 'int', 'LFO 1 Freq')
        plugins.add_plug_param(cvpj_l, pluginid, 'lfo2_freq', flplugvals[5], 'int', 'LFO 2 Freq')
        plugins.add_plug_param(cvpj_l, pluginid, 'lfo3_freq', flplugvals[6], 'int', 'LFO 3 Freq')
        plugins.add_plug_param(cvpj_l, pluginid, 'lfo1_wave', flplugvals[7], 'int', 'LFO 1 wave')
        plugins.add_plug_param(cvpj_l, pluginid, 'lfo2_wave', flplugvals[8], 'int', 'LFO 2 wave')
        plugins.add_plug_param(cvpj_l, pluginid, 'lfo3_wave', flplugvals[9], 'int', 'LFO 3 wave')
        plugins.add_plug_param(cvpj_l, pluginid, 'crosstype', flplugvals[10], 'int', 'Cross Type')
        plugins.add_plug_param(cvpj_l, pluginid, 'crosscutoff', flplugvals[11], 'int', 'Cross Cutoff')
        plugins.add_plug_param(cvpj_l, pluginid, 'wetonly', flplugvals[12], 'int', 'Wet Only')

    elif pluginname == 'fruity compressor':
        flplugvals = struct.unpack('i'*8, chunkdata)
        plugins.add_plug_param(cvpj_l, pluginid, 'threshold', flplugvals[1], 'int', 'Threshold')
        plugins.add_plug_param(cvpj_l, pluginid, 'ratio', flplugvals[2], 'int', 'Ratio')
        plugins.add_plug_param(cvpj_l, pluginid, 'gain', flplugvals[3], 'int', 'Gain')
        plugins.add_plug_param(cvpj_l, pluginid, 'attack', flplugvals[4], 'int', 'Attack')
        plugins.add_plug_param(cvpj_l, pluginid, 'release', flplugvals[5], 'int', 'Release')
        plugins.add_plug_param(cvpj_l, pluginid, 'type', flplugvals[6], 'int', 'Type')
        ##print(flplugvals)

    elif pluginname == 'fruity convolver':
        fl_plugstr.read(20)
        fromstorage = fl_plugstr.read(1)[0]
        stringlen = fl_plugstr.read(1)[0]
        filename = fl_plugstr.read(stringlen)
        if fromstorage == 0:
            audiosize = int.from_bytes(fl_plugstr.read(4), "little")
            filename = os.path.join(foldername, pluginid+'_custom_audio.wav')
            with open(filename, "wb") as customconvolverfile:
                customconvolverfile.write(fl_plugstr.read(audiosize))
        plugins.add_plug_data(cvpj_l, pluginid, 'file', filename.decode())
        fl_plugstr.read(36)
        autodata = {}
        for autoname in ['pan', 'vol', 'stereo', 'allpurpose', 'eq']:
            autodata_table = decode_pointdata(fl_plugstr)
            for point in autodata_table:
                #print(autoname, test)
                plugins.add_env_point(cvpj_l, pluginid, autoname, point[0], point[1][0], tension=point[2], type=envshapes[point[3]])
            autodata[autoname] = autodata_table

    elif pluginname == 'fruity delay':
        flplugvals = struct.unpack('i'*7, chunkdata)
        plugins.add_plug_param(cvpj_l, pluginid, 'input', flplugvals[1], 'int', 'Input')
        plugins.add_plug_param(cvpj_l, pluginid, 'fb', flplugvals[2], 'int', 'Feedback')
        plugins.add_plug_param(cvpj_l, pluginid, 'cutoff', flplugvals[3], 'int', 'Cutoff')
        plugins.add_plug_param(cvpj_l, pluginid, 'tempo', flplugvals[4], 'int', 'Tempo')
        plugins.add_plug_param(cvpj_l, pluginid, 'steps', flplugvals[5], 'int', 'Steps')
        plugins.add_plug_param(cvpj_l, pluginid, 'mode', flplugvals[6], 'int', 'Mode')

    elif pluginname == 'fruity delay 2':
        flplugvals = struct.unpack('i'*8, chunkdata)
        plugins.add_plug_param(cvpj_l, pluginid, 'input_pan', flplugvals[0], 'int', 'Input Pan')
        plugins.add_plug_param(cvpj_l, pluginid, 'input_vol', flplugvals[1], 'int', 'Input Vol')
        plugins.add_plug_param(cvpj_l, pluginid, 'dry', flplugvals[2], 'int', 'Dry')
        plugins.add_plug_param(cvpj_l, pluginid, 'fb_vol', flplugvals[3], 'int', 'Feedback Vol')
        plugins.add_plug_param(cvpj_l, pluginid, 'time', flplugvals[4], 'int', 'Time')
        plugins.add_plug_param(cvpj_l, pluginid, 'time_stereo_offset', flplugvals[5], 'int', 'Stereo Offset')
        plugins.add_plug_param(cvpj_l, pluginid, 'fb_mode', flplugvals[6], 'int', 'Feedback Mode')
        plugins.add_plug_param(cvpj_l, pluginid, 'fb_cut', flplugvals[7], 'int', 'Feedback Cut')

    #elif pluginname == 'fruity delay 3':

    elif pluginname == 'fruity fast dist':
        flplugvals = struct.unpack('i'*5, chunkdata)
        plugins.add_plug_param(cvpj_l, pluginid, 'pre', flplugvals[0], 'int', 'Pre Amp')
        plugins.add_plug_param(cvpj_l, pluginid, 'threshold', flplugvals[1], 'int', 'Threshold')
        plugins.add_plug_param(cvpj_l, pluginid, 'type', flplugvals[2], 'bool', 'Type')
        plugins.add_plug_param(cvpj_l, pluginid, 'mix', flplugvals[3], 'int', 'Mix')
        plugins.add_plug_param(cvpj_l, pluginid, 'post', flplugvals[4], 'int', 'Post')

    elif pluginname == 'fruity fast lp':
        flplugvals = struct.unpack('III', chunkdata)
        plugins.add_plug_param(cvpj_l, pluginid, 'cutoff', flplugvals[0], 'int', 'Cutoff')
        plugins.add_plug_param(cvpj_l, pluginid, 'reso', flplugvals[1], 'int', 'Reso')

    elif pluginname == 'fruity filter':
        flplugvals = struct.unpack('IIIIIIIb', chunkdata)
        plugins.add_plug_param(cvpj_l, pluginid, 'cutoff', flplugvals[0], 'int', 'Cutoff')
        plugins.add_plug_param(cvpj_l, pluginid, 'reso', flplugvals[1], 'int', 'Reso')
        plugins.add_plug_param(cvpj_l, pluginid, 'lowpass', flplugvals[2], 'int', 'Low Pass')
        plugins.add_plug_param(cvpj_l, pluginid, 'bandpass', flplugvals[3], 'int', 'Band Pass')
        plugins.add_plug_param(cvpj_l, pluginid, 'hipass', flplugvals[4], 'int', 'High Pass')
        plugins.add_plug_param(cvpj_l, pluginid, 'x2', flplugvals[5], 'bool', 'x2')
        plugins.add_plug_param(cvpj_l, pluginid, 'center', flplugvals[6], 'bool', 'Center')

    elif pluginname == 'fruity free filter':
        flplugvals = struct.unpack('IIIII', chunkdata[0:20])
        plugins.add_plug_param(cvpj_l, pluginid, 'type', flplugvals[0], 'int', 'Type')
        plugins.add_plug_param(cvpj_l, pluginid, 'freq', flplugvals[1], 'int', 'Frequency')
        plugins.add_plug_param(cvpj_l, pluginid, 'lowpass', flplugvals[2], 'int', 'Q')
        plugins.add_plug_param(cvpj_l, pluginid, 'gain', flplugvals[3], 'int', 'Gain')
        plugins.add_plug_param(cvpj_l, pluginid, 'center', flplugvals[4], 'bool', 'Center')

    elif pluginname == 'fruity html notebook':
        version = int.from_bytes(fl_plugstr.read(4), "little")
        if version == 1: plugins.add_plug_data(cvpj_l, pluginid, 'url', data_bytes.readstring_lenbyte(fl_plugstr, 1, 'little', 'utf-8'))

    elif pluginname == 'fruity mute 2':
        flplugvals = struct.unpack('III', chunkdata)
        plugins.add_plug_param(cvpj_l, pluginid, 'mute', flplugvals[0], 'int', 'Mute')
        plugins.add_plug_param(cvpj_l, pluginid, 'channel', flplugvals[1], 'int', 'Channel')
        ##print(flplugvals)

    elif pluginname == 'fruity limiter':
        fl_plugstr.read(4)
        flplugvals = struct.unpack('i'*18, fl_plugstr.read(18*4))
        plugins.add_plug_param(cvpj_l, pluginid, 'gain', flplugvals[0], 'int', 'Gain')
        plugins.add_plug_param(cvpj_l, pluginid, 'sat', flplugvals[1], 'int', 'Soft Saturation Threshold')
        plugins.add_plug_param(cvpj_l, pluginid, 'limiter_ceil', flplugvals[2], 'int', 'Limiter Ceil')
        plugins.add_plug_param(cvpj_l, pluginid, 'limiter_att', flplugvals[3], 'int', 'Limiter Attack')
        plugins.add_plug_param(cvpj_l, pluginid, 'limiter_att_curve', flplugvals[4], 'int', 'Limiter Attack Curve')
        plugins.add_plug_param(cvpj_l, pluginid, 'limiter_rel', flplugvals[5], 'int', 'Limiter Release')
        plugins.add_plug_param(cvpj_l, pluginid, 'limiter_rel_curve', flplugvals[6], 'int', 'Limiter Release Curve')
        plugins.add_plug_param(cvpj_l, pluginid, 'limiter_sus', flplugvals[7], 'int', 'Limiter Sustain')
        plugins.add_plug_param(cvpj_l, pluginid, 'comp_thres', flplugvals[8], 'int', 'Comp Threshold')
        plugins.add_plug_param(cvpj_l, pluginid, 'comp_knee', flplugvals[9], 'int', 'Comp Knee')
        plugins.add_plug_param(cvpj_l, pluginid, 'comp_ratio', flplugvals[10], 'int', 'Comp Ratio')
        plugins.add_plug_param(cvpj_l, pluginid, 'comp_att', flplugvals[11], 'int', 'Comp Attack')
        plugins.add_plug_param(cvpj_l, pluginid, 'comp_rel', flplugvals[12], 'int', 'Comp Release')
        plugins.add_plug_param(cvpj_l, pluginid, 'comp_att_curve', flplugvals[13], 'int', 'Comp Attack Curve')
        plugins.add_plug_param(cvpj_l, pluginid, 'comp_sus', flplugvals[14], 'int', 'Comp Sustain')
        plugins.add_plug_param(cvpj_l, pluginid, 'noise_gain', flplugvals[15], 'int', 'Noise Gain')
        plugins.add_plug_param(cvpj_l, pluginid, 'noise_thres', flplugvals[16], 'int', 'Noise Threshold')
        plugins.add_plug_param(cvpj_l, pluginid, 'noise_rel', flplugvals[17], 'int', 'Noise Release')
        fl_plugstr.read(18*4)
        flplugflags = struct.unpack('ibbbbbbbbbbbb', fl_plugstr.read(16))
        plugins.add_plug_data(cvpj_l, pluginid, 'mode', flplugflags[1])

    elif pluginname in ['fruity notebook 2', 'fruity notebook']:
        version = int.from_bytes(fl_plugstr.read(4), "little")
        if version == 0 and pluginname == 'fruity notebook 2' or version == 1000 and pluginname == 'fruity notebook': 
            plugins.add_plug_data(cvpj_l, pluginid, 'currentpage', int.from_bytes(fl_plugstr.read(4), "little"))
            pagesdata = {}
            while True:
                pagenum = int.from_bytes(fl_plugstr.read(4), "little")
                if pagenum == 0 or pagenum > 100: break
                if pluginname == 'fruity notebook 2': 
                    length = varint.decode_stream(fl_plugstr)
                    text = fl_plugstr.read(length*2).decode('utf-16le')
                if pluginname == 'fruity notebook': 
                    length = int.from_bytes(fl_plugstr.read(4), "little")
                    text = fl_plugstr.read(length).decode('ascii')
                pagesdata[pagenum] = text
            plugins.add_plug_data(cvpj_l, pluginid, 'pages', pagesdata)
            plugins.add_plug_data(cvpj_l, pluginid, 'editing_enabled', fl_plugstr.read(1)[0])

    elif pluginname == 'fruity panomatic':
        flplugvals = struct.unpack('IIIIII', chunkdata)
        plugins.add_plug_param(cvpj_l, pluginid, 'pan', flplugvals[0], 'int', "Pan")
        plugins.add_plug_param(cvpj_l, pluginid, 'vol', flplugvals[1], 'int', "Vol")
        plugins.add_plug_param(cvpj_l, pluginid, 'lfo_shape', flplugvals[2], 'int', "LFO Shape")
        plugins.add_plug_param(cvpj_l, pluginid, 'lfo_target', flplugvals[3], 'int', "LFO Target")
        plugins.add_plug_param(cvpj_l, pluginid, 'lfo_amount', flplugvals[4], 'int', "LFO Amount")
        plugins.add_plug_param(cvpj_l, pluginid, 'lfo_speed', flplugvals[5], 'int', "LFO Speed")

    elif pluginname == 'fruity parametric eq 2':
        version = int.from_bytes(fl_plugstr.read(4), "little")
        eqparams = struct.unpack('iiiiiii', fl_plugstr.read(28))
        for num in range(7): plugins.add_plug_param(cvpj_l, pluginid, str(num)+'_q', eqparams[num], 'int', "Band "+str(num)+" Q")
        eqparams = struct.unpack('iiiiiii', fl_plugstr.read(28))
        for num in range(7): plugins.add_plug_param(cvpj_l, pluginid, str(num)+'_freq', eqparams[num], 'int', "Band "+str(num)+" Freq")
        eqparams = struct.unpack('iiiiiii', fl_plugstr.read(28))
        for num in range(7): plugins.add_plug_param(cvpj_l, pluginid, str(num)+'_width', eqparams[num], 'int', "Band "+str(num)+" Width")
        eqparams = struct.unpack('iiiiiii', fl_plugstr.read(28))
        for num in range(7): plugins.add_plug_param(cvpj_l, pluginid, str(num)+'_type', eqparams[num], 'int', "Band "+str(num)+" Type")
        eqparams = struct.unpack('iiiiiii', fl_plugstr.read(28))
        for num in range(7): plugins.add_plug_param(cvpj_l, pluginid, str(num)+'_order', eqparams[num], 'int', "Band "+str(num)+" Order")
        eqparams = struct.unpack('iiiiiii', fl_plugstr.read(28))
        plugins.add_plug_param(cvpj_l, pluginid, 'main_lvl', eqparams[0], 'int', "Main Level")

    elif pluginname == 'fruity parametric eq':
        eqparams = struct.unpack('iiiiiii', fl_plugstr.read(28))
        for num in range(7): plugins.add_plug_param(cvpj_l, pluginid, str(num)+'_q', eqparams[num], 'int', "Band "+str(num)+" Q")
        eqparams = struct.unpack('iiiiiii', fl_plugstr.read(28))
        for num in range(7): plugins.add_plug_param(cvpj_l, pluginid, str(num)+'_freq', eqparams[num], 'int', "Band "+str(num)+" Freq")
        eqparams = struct.unpack('iiiiiii', fl_plugstr.read(28))
        for num in range(7): plugins.add_plug_param(cvpj_l, pluginid, str(num)+'_width', eqparams[num], 'int', "Band "+str(num)+" Width")
        eqparams = struct.unpack('iiiiiii', fl_plugstr.read(28))
        for num in range(7): plugins.add_plug_param(cvpj_l, pluginid, str(num)+'_type', eqparams[num], 'int', "Band "+str(num)+" Type")
        mainlvl = int.from_bytes(fl_plugstr.read(4), "little")
        plugins.add_plug_param(cvpj_l, pluginid, 'main_lvl', mainlvl, 'int', "Main Level")

    elif pluginname == 'fruity phase inverter':
        flplugvals = struct.unpack('ii', fl_plugstr.read(8))
        plugins.add_plug_param(cvpj_l, pluginid, 'state', flplugvals[1], 'int', "State")

    elif pluginname == 'fruity phaser':
        flplugvals = struct.unpack('iiiiiiiiii', chunkdata)
        plugins.add_plug_param(cvpj_l, pluginid, 'sweep_freq', flplugvals[1], 'int', "Sweep Freq")
        plugins.add_plug_param(cvpj_l, pluginid, 'depth_min', flplugvals[2], 'int', "Min Depth")
        plugins.add_plug_param(cvpj_l, pluginid, 'depth_max', flplugvals[3], 'int', "Max Depth")
        plugins.add_plug_param(cvpj_l, pluginid, 'freq_range', flplugvals[4], 'int', "Freq Range")
        plugins.add_plug_param(cvpj_l, pluginid, 'stereo', flplugvals[5], 'int', "Stereo")
        plugins.add_plug_param(cvpj_l, pluginid, 'num_stages', flplugvals[6], 'int', "NR. Stages")
        plugins.add_plug_param(cvpj_l, pluginid, 'feedback', flplugvals[7], 'int', "Feedback")
        plugins.add_plug_param(cvpj_l, pluginid, 'drywet', flplugvals[8], 'int', "Dry-Wet")
        plugins.add_plug_param(cvpj_l, pluginid, 'gain', flplugvals[9], 'int', "gain")

    elif pluginname == 'fruity reeverb':
        flplugvals = struct.unpack('iiiiiiiiiii', chunkdata)
        plugins.add_plug_param(cvpj_l, pluginid, 'lowcut', flplugvals[1], 'int', "Low Cut")
        plugins.add_plug_param(cvpj_l, pluginid, 'highcut', flplugvals[2], 'int', "High Cut")
        plugins.add_plug_param(cvpj_l, pluginid, 'predelay', flplugvals[3], 'int', "Predelay")
        plugins.add_plug_param(cvpj_l, pluginid, 'room_size', flplugvals[4], 'int', "Room Size")
        plugins.add_plug_param(cvpj_l, pluginid, 'diffusion', flplugvals[5], 'int', "Diffusion")
        plugins.add_plug_param(cvpj_l, pluginid, 'color', flplugvals[6], 'int', "Color")
        plugins.add_plug_param(cvpj_l, pluginid, 'decay', flplugvals[7], 'int', "Decay")
        plugins.add_plug_param(cvpj_l, pluginid, 'hidamping', flplugvals[8], 'int', "High Damping")
        plugins.add_plug_param(cvpj_l, pluginid, 'dry', flplugvals[9], 'int', "Dry")
        plugins.add_plug_param(cvpj_l, pluginid, 'reverb', flplugvals[10], 'int', "Reverb")

    elif pluginname == 'fruity reeverb 2':
        flplugvals = struct.unpack('iiiiiiiiiiiiiiiibb', chunkdata)
        plugins.add_plug_param(cvpj_l, pluginid, 'lowcut', flplugvals[1], 'int', "Low Cut")
        plugins.add_plug_param(cvpj_l, pluginid, 'highcut', flplugvals[2], 'int', "High Cut")
        plugins.add_plug_param(cvpj_l, pluginid, 'predelay', flplugvals[3], 'int', "Predelay")
        plugins.add_plug_param(cvpj_l, pluginid, 'room_size', flplugvals[4], 'int', "Room Size")
        plugins.add_plug_param(cvpj_l, pluginid, 'diffusion', flplugvals[5], 'int', "Diffusion")
        plugins.add_plug_param(cvpj_l, pluginid, 'decay', flplugvals[6], 'int', "Decay")
        plugins.add_plug_param(cvpj_l, pluginid, 'hidamping', flplugvals[7], 'int', "High Damping")
        plugins.add_plug_param(cvpj_l, pluginid, 'bass', flplugvals[8], 'int', "Bass Multi")
        plugins.add_plug_param(cvpj_l, pluginid, 'cross', flplugvals[9], 'int', "Crossover")
        plugins.add_plug_param(cvpj_l, pluginid, 'stereo', flplugvals[10], 'int', "Stereo Seperation")
        plugins.add_plug_param(cvpj_l, pluginid, 'dry', flplugvals[11], 'int', "Dry")
        plugins.add_plug_param(cvpj_l, pluginid, 'er', flplugvals[12], 'int', "Early Reflection")
        plugins.add_plug_param(cvpj_l, pluginid, 'wet', flplugvals[13], 'int', "Wet")
        plugins.add_plug_param(cvpj_l, pluginid, 'mod_speed', flplugvals[14], 'int', "Mod Speed")
        plugins.add_plug_param(cvpj_l, pluginid, 'mod', flplugvals[15], 'int', "Mod Depth")
        plugins.add_plug_param(cvpj_l, pluginid, 'tempo_predelay', flplugvals[16], 'bool', "Tempo Based Predelay")
        plugins.add_plug_param(cvpj_l, pluginid, 'mid_side', flplugvals[17], 'bool', "Mid/Side Input")

    elif pluginname == 'fruity soft clipper':
        flplugvals = struct.unpack('ii', chunkdata)
        plugins.add_plug_param(cvpj_l, pluginid, 'threshold', flplugvals[0], 'int', "Threshold")
        plugins.add_plug_param(cvpj_l, pluginid, 'postgain', flplugvals[1], 'int', "PostGain")

    elif pluginname == 'fruity stereo enhancer':
        flplugvals = struct.unpack('iiiiii', chunkdata)
        plugins.add_plug_param(cvpj_l, pluginid, 'pan', flplugvals[0], 'int', "Pan")
        plugins.add_plug_param(cvpj_l, pluginid, 'vol', flplugvals[1], 'int', "Volume")
        plugins.add_plug_param(cvpj_l, pluginid, 'stereo', flplugvals[2], 'int', "Stereo Seperation")
        plugins.add_plug_param(cvpj_l, pluginid, 'phase_offs', flplugvals[3], 'int', "Phase Offset")
        plugins.add_plug_param(cvpj_l, pluginid, 'prepost', flplugvals[4], 'bool', "Pre/Post")
        plugins.add_plug_param(cvpj_l, pluginid, 'phaseinvert', flplugvals[5], 'int', "Phase Invert")

    elif pluginname == 'fruity stereo shaper':
        flplugvals = struct.unpack('iiiiiiiii', chunkdata)
        plugins.add_plug_param(cvpj_l, pluginid, 'r2l', flplugvals[1], 'int', "Right to Left")
        plugins.add_plug_param(cvpj_l, pluginid, 'l2l', flplugvals[2], 'int', "Left")
        plugins.add_plug_param(cvpj_l, pluginid, 'r2r', flplugvals[3], 'int', "Right")
        plugins.add_plug_param(cvpj_l, pluginid, 'l2r', flplugvals[4], 'int', "Left to Right")
        plugins.add_plug_param(cvpj_l, pluginid, 'delay', flplugvals[5], 'int', "Delay")
        plugins.add_plug_param(cvpj_l, pluginid, 'dephase', flplugvals[6], 'int', "Dephaseing")
        plugins.add_plug_param(cvpj_l, pluginid, 'iodiff', flplugvals[7], 'bool', "In/Out Diffrence")
        plugins.add_plug_param(cvpj_l, pluginid, 'prepost', flplugvals[8], 'bool', "Pre/Post")
        ##print(flplugvals)

    elif pluginname == 'fruity spectroman':
        flplugvals = struct.unpack('bIIIbbb', chunkdata)
        plugins.add_plug_param(cvpj_l, pluginid, 'outputmode', flplugvals[1], 'bool', "Output Mode")
        plugins.add_plug_param(cvpj_l, pluginid, 'amp', flplugvals[2], 'int', "Amp")
        plugins.add_plug_param(cvpj_l, pluginid, 'scale', flplugvals[3], 'int', "Freq Scale")
        plugins.add_plug_data(cvpj_l, pluginid, 'stereo', flplugvals[6])
        plugins.add_plug_data(cvpj_l, pluginid, 'show_peaks', flplugvals[5])
        plugins.add_plug_data(cvpj_l, pluginid, 'windowing', flplugvals[4])

    elif pluginname == 'fruity vocoder':
        flplugvals = struct.unpack('iiiib', fl_plugstr.read(17))
        vocbands = struct.unpack('f'*flplugvals[1], fl_plugstr.read(flplugvals[1]*4))
        plugins.add_plug_data(cvpj_l, pluginid, 'bands', vocbands)
        plugins.add_plug_data(cvpj_l, pluginid, 'filter', flplugvals[2])
        plugins.add_plug_data(cvpj_l, pluginid, 'left_right', flplugvals[4])
        flplugvalsafter = struct.unpack('i'*12, fl_plugstr.read(12*4))
        #print(flplugvalsafter)
        plugins.add_plug_param(cvpj_l, pluginid, 'freq_min', flplugvalsafter[0], 'int', "Freq Min")
        plugins.add_plug_param(cvpj_l, pluginid, 'freq_max', flplugvalsafter[1], 'int', "Freq Max")
        plugins.add_plug_param(cvpj_l, pluginid, 'freq_scale', flplugvalsafter[2], 'int', "Freq Scale")
        plugins.add_plug_param(cvpj_l, pluginid, 'freq_invert', flplugvalsafter[3], 'bool', "Freq Invert")
        plugins.add_plug_param(cvpj_l, pluginid, 'freq_formant', flplugvalsafter[4], 'int', "Freq Formant")
        plugins.add_plug_param(cvpj_l, pluginid, 'freq_bandwidth', flplugvalsafter[5], 'int', "Freq BandWidth")
        plugins.add_plug_param(cvpj_l, pluginid, 'env_att', flplugvalsafter[6], 'int', "Env Att")
        plugins.add_plug_param(cvpj_l, pluginid, 'env_rel', flplugvalsafter[7], 'int', "Env Rel")
        plugins.add_plug_param(cvpj_l, pluginid, 'mix_mod', flplugvalsafter[9], 'int', "Mix Mod")
        plugins.add_plug_param(cvpj_l, pluginid, 'mix_car', flplugvalsafter[10], 'int', "Mix Car")
        plugins.add_plug_param(cvpj_l, pluginid, 'mix_wet', flplugvalsafter[11], 'int', "Mix Wet")

    elif pluginname == 'fruity waveshaper':
        flplugvals = struct.unpack('bHHIIbbbbbb', fl_plugstr.read(22))
        #print(flplugvals)
        plugins.add_plug_param(cvpj_l, pluginid, 'preamp', flplugvals[2], 'int', "Pre Amp")
        plugins.add_plug_param(cvpj_l, pluginid, 'wet', flplugvals[3], 'int', "Wet")
        plugins.add_plug_param(cvpj_l, pluginid, 'postgain', flplugvals[4], 'int', "Post Gain")
        plugins.add_plug_param(cvpj_l, pluginid, 'bipolarmode', flplugvals[5], 'bool', "Bi-polar Mode")
        plugins.add_plug_param(cvpj_l, pluginid, 'removedc', flplugvals[6], 'bool', "Remove DC")

        autodata_table = decode_pointdata(fl_plugstr)
        for point in autodata_table:
            plugins.add_env_point(cvpj_l, pluginid, 'shape', point[0], point[1][0], tension=point[2], type=envshapes[point[3]])

    elif pluginname == 'pitch shifter':
        flplugvals = struct.unpack('iiiiiiiiiiiiiiiiii', fl_plugstr.read(18*4))
        #print(flplugvals)

    #elif pluginname == 'pitcher': LATER
    #    chunkdata = data_bytes.riff_read(chunkdata, 0)
    #    riffbio = data_bytes.to_bytesio(chunkdata[0][1][4:])
    #    flplugvals = struct.unpack('f'*33, riffbio.read(33*4))
    #    flplugflags = struct.unpack('b'*16, riffbio.read(16))
    #    for test in range(len(flplugvals)):
    #        print(test, flplugvals[test])
    #    plugins.add_plug_param(cvpj_l, pluginid, 'speed', flplugvals[0], 'int', "Correction Speed")
    #    plugins.add_plug_param(cvpj_l, pluginid, 'gender', flplugvals[2], 'int', "Gender")
    #    plugins.add_plug_param(cvpj_l, pluginid, 'finetune', flplugvals[3], 'int', "Fine Tune")

    # ------------------------------------------------------------------------------------------- VST
    elif pluginname == 'fruity wrapper':
        fl_plugstr.seek(0,2)
        fl_plugstr_size = fl_plugstr.tell()
        fl_plugstr.seek(0)
        fl_plugstr.read(4)

        wrapperdata = {}
        while fl_plugstr.tell() < fl_plugstr_size:
            chunktype = int.from_bytes(fl_plugstr.read(4), "little")
            chunksize = int.from_bytes(fl_plugstr.read(4), "little")
            fl_plugstr.read(4)
            chunkdata = fl_plugstr.read(chunksize)
            if chunktype == 1: wrapperdata['midi'] = chunkdata
            if chunktype == 2: wrapperdata['flags'] = chunkdata
            if chunktype == 30: wrapperdata['io'] = chunkdata
            if chunktype == 32: wrapperdata['outputs'] = chunkdata
            if chunktype == 50: wrapperdata['plugin_info'] = chunkdata
            if chunktype == 51: wrapperdata['fourid'] = int.from_bytes(chunkdata, "little")
            if chunktype == 53: wrapperdata['state'] = chunkdata
            if chunktype == 54: wrapperdata['name'] = chunkdata.decode()
            if chunktype == 55: wrapperdata['file'] = chunkdata.decode()
            if chunktype == 56: wrapperdata['vendor'] = chunkdata.decode()
            if chunktype == 57: wrapperdata['57'] = chunkdata

        if 'plugin_info' in wrapperdata:
            wrapper_vsttype = int.from_bytes(wrapperdata['plugin_info'][0:4], "little")
            if 'fourid' in wrapperdata:
                pluginstate = wrapperdata['state']
                wrapper_vststate = pluginstate[0:9]
                wrapper_vstsize = int.from_bytes(pluginstate[9:13], "little")
                wrapper_vstpad = pluginstate[13:17]
                wrapper_vstprogram = int.from_bytes(pluginstate[17:21], "little")
                wrapper_vstdata = pluginstate[21:]
                plugin_vst2.replace_data(cvpj_l, pluginid, 'win', wrapperdata['name'], 'chunk', wrapper_vstdata, 0)
                plugins.add_plug_data(cvpj_l, pluginid, 'current_program', wrapper_vstprogram)

    # ------------------------------------------------------------------------------------------- Other

    else:
        plugins.add_plug_data(cvpj_l, pluginid, 'chunk', base64.b64encode(chunkdata).decode('ascii'))
