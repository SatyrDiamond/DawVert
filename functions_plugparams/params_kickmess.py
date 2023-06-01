# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import io
import math

def initparams():
    global params
    params = {}
    params['pub'] = {}
    params['pub']['freq_start'] = 440
    params['pub']['freq_end'] = 440
    params['pub']['f_env_release'] = 1000
    params['pub']['dist_start'] = 0
    params['pub']['dist_end'] = 0
    params['pub']['gain'] = 0.5
    params['pub']['env_slope'] = 0.5
    params['pub']['freq_slope'] = 0.5
    params['pub']['noise'] = 0
    params['pub']['freq_note_start'] = 0.25
    params['pub']['freq_note_end'] = 0.25
    params['pub']['env_release'] = 0
    params['pub']['phase_offs'] = 0
    params['pub']['dist_on'] = 0
    params['pub']['f1_cutoff'] = 1
    params['pub']['f1_res'] = 0
    params['pub']['f1_drive'] = 0.2
    params['pub']['main_gain'] = 0.70710677
    params['pub']['e1_attack'] = 0.1
    params['pub']['e1_decay'] = 0.14142135
    params['pub']['e1_sustain'] = 0.75
    params['pub']['e1_release'] = 0.1
    params['priv'] = {}
    params['priv']['f1_type'] = 0.5
    params['priv']['f1_on'] = 0.25
    params['priv']['midi_chan'] = 0

def setvalue(i_cat, i_name, i_value):
    global params
    params[i_cat][i_name] = i_value

def add(bio_data, i_cat, i_name, i_value):
    text = i_cat+' : '+i_name+'='+str(i_value)+';\n'
    bio_data.write(str.encode(text))

def getparams():
    global params

    out = io.BytesIO()
    out.write(b'!PARAMS;\n')

    for paramcat in params:
        for paramval in params[paramcat]:
            o_value = params[paramcat][paramval]
            if paramval in ['freq_start']: o_value = math.sqrt((o_value-2.51)/3000)
            if paramval in ['freq_end']: o_value = math.sqrt((o_value-2.51)/2000)
            if paramval in ['f_env_release']: 
                if o_value > 2.4: o_value = math.sqrt((o_value-2.51)/5000)
            add(out, paramcat, paramval, o_value)

    out.seek(0)
    return out.read()