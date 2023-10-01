# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import plugins
from functions import data_bytes

def opl2sbi_plugin(cvpj_l, pluginid, 
    iModChar, iCarChar, iModScale, iCarScale, 
    iModAttack, iCarAttack, iModSustain, iCarSustain, 
    iModWaveSel, iCarWaveSel, iFeedback):
    print('opl2sbi_plugin')

    opl_mod_flags, opl_mod_mul = data_bytes.splitbyte(iModChar) 
    opl_mod_trem, opl_mod_vib, opl_mod_sust, opl_mod_krs = data_bytes.to_bin(opl_mod_flags, 4)
    opl_car_flags, opl_car_mul = data_bytes.splitbyte(iCarChar)
    opl_car_trem, opl_car_vib, opl_car_sust, opl_car_krs = data_bytes.to_bin(opl_car_flags, 4)
    opl_mod_kls = iModScale >> 6
    opl_mod_out = iModScale & 0x3F
    opl_car_kls = iCarScale >> 6
    opl_car_out = iCarScale & 0x3F
    opl_fb = iFeedback

    opl_fb = iFeedback & 0x07
    opl_con = iFeedback >> 3

    opl_mod_wave = iModWaveSel
    opl_car_wave = iCarWaveSel
    opl_mod_att, opl_mod_dec = data_bytes.splitbyte(iModAttack) 
    opl_car_att, opl_car_dec = data_bytes.splitbyte(iCarAttack) 
    opl_mod_sus, opl_mod_rel = data_bytes.splitbyte(iModSustain) 
    opl_car_sus, opl_car_rel = data_bytes.splitbyte(iCarSustain)

    print(opl_mod_wave, opl_car_wave)

    plugins.replace_plug(cvpj_l, pluginid, 'fm', 'opl2')

    plugins.add_plug_param(cvpj_l, pluginid, "feedback", opl_fb, 'int', "")
    plugins.add_plug_param(cvpj_l, pluginid, "percussive", 0, 'int', "")
    plugins.add_plug_param(cvpj_l, pluginid, "perctype", 0, 'int', "")
    plugins.add_plug_param(cvpj_l, pluginid, "tremolo_depth", 0, 'int', "")
    plugins.add_plug_param(cvpj_l, pluginid, "vibrato_depth", 0, 'int', "")
    plugins.add_plug_param(cvpj_l, pluginid, "fm", opl_con, 'int', "")

    plugins.add_plug_param(cvpj_l, pluginid, "mod_scale", opl_mod_kls, 'int', "")
    plugins.add_plug_param(cvpj_l, pluginid, "mod_freqmul", opl_mod_mul, 'int', "")
    plugins.add_plug_param(cvpj_l, pluginid, "mod_env_attack", (opl_mod_att*-1)+15, 'int', "")
    plugins.add_plug_param(cvpj_l, pluginid, "mod_env_sustain", (opl_mod_sus*-1)+15, 'int', "")
    plugins.add_plug_param(cvpj_l, pluginid, "mod_perc_env", 0, 'int', "")
    plugins.add_plug_param(cvpj_l, pluginid, "mod_env_decay", (opl_mod_dec*-1)+15, 'int', "")
    plugins.add_plug_param(cvpj_l, pluginid, "mod_env_release", opl_mod_rel, 'int', "")
    plugins.add_plug_param(cvpj_l, pluginid, "mod_level", (opl_mod_out*-1)+63, 'int', "")
    plugins.add_plug_param(cvpj_l, pluginid, "mod_tremolo", opl_mod_trem, 'int', "")
    plugins.add_plug_param(cvpj_l, pluginid, "mod_vibrato", opl_mod_vib, 'int', "")
    plugins.add_plug_param(cvpj_l, pluginid, "mod_ksr", opl_mod_krs, 'int', "")
    plugins.add_plug_param(cvpj_l, pluginid, "mod_waveform", opl_mod_wave, 'int', "")

    plugins.add_plug_param(cvpj_l, pluginid, "car_scale", opl_car_kls, 'int', "")
    plugins.add_plug_param(cvpj_l, pluginid, "car_freqmul", opl_car_mul, 'int', "")
    plugins.add_plug_param(cvpj_l, pluginid, "car_env_attack", (opl_car_att*-1)+15, 'int', "")
    plugins.add_plug_param(cvpj_l, pluginid, "car_env_sustain", (opl_car_sus*-1)+15, 'int', "")
    plugins.add_plug_param(cvpj_l, pluginid, "car_perc_env", 0, 'int', "")
    plugins.add_plug_param(cvpj_l, pluginid, "car_env_decay", (opl_car_dec*-1)+15, 'int', "")
    plugins.add_plug_param(cvpj_l, pluginid, "car_env_release", opl_car_rel, 'int', "")
    plugins.add_plug_param(cvpj_l, pluginid, "car_level", (opl_car_out*-1)+63, 'int', "")
    plugins.add_plug_param(cvpj_l, pluginid, "car_tremolo", opl_car_trem, 'int', "")
    plugins.add_plug_param(cvpj_l, pluginid, "car_vibrato", opl_car_vib, 'int', "")
    plugins.add_plug_param(cvpj_l, pluginid, "car_ksr", opl_car_krs, 'int', "")
    plugins.add_plug_param(cvpj_l, pluginid, "car_waveform", opl_car_wave, 'int', "")