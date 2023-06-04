# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

def initparams():
    global samplefile
    global params
    samplefile = {'filepath': '','ui_sample_loaded': 'ui_sample_loaded yes/no'}
    params = {'sample_in': 0.000000,'sample_out': 1.000000,'sample_loop_start': 0.000000,'sample_loop_end': 1.000000,'pitch_center': '60.000000','pitch': '100.000000','no_pitch': 0.000000,'playmode': 0.000000,'play_direction': 0.000000,'oversampling': 1.000000,'amp_attack': 0.000000,'amp_decay': 0.000000,'amp_sustain': 1.000000,'amp_release': 0.000000,'amp_lfo_type': 0.000000,'amp_lfo_sync': 0.000000,'amp_lfo_freq': 0.000000,'amp_lfo_sync_freq': 0.000000,'amp_lfo_depth': 0.000000,'amp_lfo_fade': 0.000000,'filter_type': 0.000000,'cutoff': 1.000000,'resonance': 1.000000,'filter_eg_depth': 0.000000,'filter_attack': 0.000000,'filter_decay': 0.000000,'filter_sustain': 0.000000,'filter_release': 0.000000,'filter_lfo_type': 0.000000,'filter_lfo_sync': 0.000000,'filter_lfo_freq': 0.000000,'filter_lfo_sync_freq': 0.000000,'filter_lfo_depth': 0.000000,'filter_lfo_fade': 0.000000,'pitch_eg_depth': 0.000000,'pitch_attack': 0.000000,'pitch_decay': 0.000000,'pitch_sustain': 0.000000,'pitch_release': 0.000000,'pitch_lfo_type': 0.000000}

def setfile(value):
    global samplefile
    samplefile['filepath'] = value

def setvalue(name, value):
    global params
    params[name] = value

def getparams():
    global samplefile
    global params
    return [samplefile, params]

def shape(input_val):
    output_val = 0
    if input_val == "triangle": output_val = 0.0
    if input_val == "sine": output_val = 1.0
    if input_val == "square": output_val = 2.0
    if input_val == "saw": output_val = 3.0
    if input_val == "saw up": output_val = 3.0
    if input_val == "saw down": output_val = 4.0
    if input_val == "random": output_val = 5.0
    return output_val
