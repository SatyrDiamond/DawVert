# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

def fake_tension(cvpj_plugindata):
    a_predelay, a_attack, a_hold, a_decay, a_sustain, a_release, a_amount = cvpj_plugindata.asdr_env_get(asdrtype)
    t_attack, t_decay, t_release = plugins.asdr_env_tension_get(asdrtype)
    a_attack *= pow(2, min(t_attack*3.14, 0))
    a_decay *= pow(2, min(t_decay*3.14, 0))
    a_release *= pow(2, min(t_release*3.14, 0))
    return a_predelay, a_attack, a_hold, a_decay, a_sustain, a_release, a_amount