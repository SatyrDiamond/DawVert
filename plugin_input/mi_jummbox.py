# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from functions import auto
from functions import idvals
from functions import tracks
from functions import plugins
from functions import note_data
from functions import data_values
from functions import placement_data
from functions import song
import plugin_input
import json

global colornum_p
global colornum_d
colornum_p = 0
colornum_d = 0

colors_pitch = [[0, 0.6, 0.63], [0.63, 0.63, 0], [0.78, 0.31, 0], [0, 0.63, 0], [0.82, 0.13, 0.82], [0.47, 0.47, 0.69], [0.54, 0.63, 0], [0.87, 0, 0.1], [0, 0.63, 0.44], [0.57, 0.12, 1]]

colors_drums = [ [0.44, 0.44, 0.44], [0.6, 0.4, 0.2], [0.29, 0.43, 0.56], [0.48, 0.31, 0.6], [0.38, 0.47, 0.22]]

rawChipWaves = {}
rawChipWaves["rounded"] = {"expression": 0.94, "samples": [0,0.2,0.4,0.5,0.6,0.7,0.8,0.85,0.9,0.95,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0.95,0.9,0.85,0.8,0.7,0.6,0.5,0.4,0.2,0,-0.2,-0.4,-0.5,-0.6,-0.7,-0.8,-0.85,-0.9,-0.95,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-0.95,-0.9,-0.85,-0.8,-0.7,-0.6,-0.5,-0.4,-0.2]}
rawChipWaves["triangle"] = {"expression": 1, "samples": [1/15,0.2,5/15,7/15,0.6,11/15,13/15,1,1,13/15,11/15,0.6,7/15,5/15,0.2,1/15,-1/15,-0.2,-5/15,-7/15,-0.6,-11/15,-13/15,-1,-1,-13/15,-11/15,-0.6,-7/15,-5/15,-0.2,-1/15]}
rawChipWaves["square"] = {"expression": 0.5, "samples": [1,-1]}
rawChipWaves["1/4 pulse"] = {"expression": 0.5, "samples": [1,-1,-1,-1]}
rawChipWaves["1/8 pulse"] = {"expression": 0.5, "samples": [1,-1,-1,-1,-1,-1,-1,-1]}
rawChipWaves["sawtooth"] = {"expression": 0.65, "samples": [1/31,3/31,5/31,7/31,9/31,11/31,13/31,15/31,17/31,19/31,21/31,23/31,25/31,27/31,29/31,1,-1,-29/31,-27/31,-25/31,-23/31,-21/31,-19/31,-17/31,-15/31,-13/31,-11/31,-9/31,-7/31,-5/31,-3/31,-1/31]}
rawChipWaves["double saw"] = {"expression": 0.5, "samples": [0,-0.2,-0.4,-0.6,-0.8,-1,1,-0.8,-0.6,-0.4,-0.2,1,0.8,0.6,0.4,0.2]}
rawChipWaves["double pulse"] = {"expression": 0.4, "samples": [1,1,1,1,1,-1,-1,-1,1,1,1,1,-1,-1,-1,-1]}
rawChipWaves["spiky"] = {"expression": 0.4, "samples": [1,-1,1,-1,1,0]}
rawChipWaves["sine"] = {"expression": 0.88, "samples": [8,9,11,12,13,14,15,15,15,15,14,14,13,11,10,9,7,6,4,3,2,1,0,0,0,0,1,1,2,4,5,6]}
rawChipWaves["flute"] = {"expression": 0.8, "samples": [3,4,6,8,10,11,13,14,15,15,14,13,11,8,5,3]}
rawChipWaves["harp"] = {"expression": 0.8, "samples": [0,3,3,3,4,5,5,6,7,8,9,11,11,13,13,15,15,14,12,11,10,9,8,7,7,5,4,3,2,1,0,0]}
rawChipWaves["sharp clarinet"] = {"expression": 0.38, "samples": [0,0,0,1,1,8,8,9,9,9,8,8,8,8,8,9,9,7,9,9,10,4,0,0,0,0,0,0,0,0,0,0]}
rawChipWaves["soft clarinet"] = {"expression": 0.45, "samples": [0,1,5,8,9,9,9,9,9,9,9,11,11,12,13,12,10,9,7,6,4,3,3,3,1,1,1,1,1,1,1,1]}
rawChipWaves["alto sax"] = {"expression": 0.3, "samples": [5,5,6,4,3,6,8,7,2,1,5,6,5,4,5,7,9,11,13,14,14,14,14,13,10,8,7,7,4,3,4,2]}
rawChipWaves["bassoon"] = {"expression": 0.35, "samples": [9,9,7,6,5,4,4,4,4,5,7,8,9,10,11,13,13,11,10,9,7,6,4,2,1,1,1,2,2,5,11,14]}
rawChipWaves["trumpet"] = {"expression": 0.22, "samples": [10,11,8,6,5,5,5,6,7,7,7,7,6,6,7,7,7,7,7,6,6,6,6,6,6,6,6,7,8,9,11,14]}
rawChipWaves["electric guitar"] = {"expression": 0.2, "samples": [11,12,12,10,6,6,8,0,2,4,8,10,9,10,1,7,11,3,6,6,8,13,14,2,0,12,8,4,13,11,10,13]}
rawChipWaves["organ"] = {"expression": 0.2, "samples": [11,10,12,11,14,7,5,5,12,10,10,9,12,6,4,5,13,12,12,10,12,5,2,2,8,6,6,5,8,3,2,1]}
rawChipWaves["pan flute"] = {"expression": 0.35, "samples": [1,4,7,6,7,9,7,7,11,12,13,15,13,11,11,12,13,10,7,5,3,6,10,7,3,3,1,0,1,0,1,0]}
rawChipWaves["glitch"] = {"expression": 0.5, "samples": [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,-1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,-1,-1,1,1,1,1,1,1,1,1,1,1,1,1,1,-1,-1,-1,1,1,1,1,1,1,1,1,1,1,1,1,-1,-1,-1,-1,1,1,1,1,1,1,1,1,1,1,1,-1,-1,-1,-1,-1,1,1,1,1,1,1,1,1,1,1,-1,-1,-1,-1,-1,-1,1,1,1,1,1,1,1,1,1,-1,-1,-1,-1,-1,-1,-1,1,1,1,1,1,1,1,1,-1,-1,-1,-1,-1,-1,-1,-1,1,1,1,1,1,1,1,1,1,-1,-1,-1,-1,-1,-1,-1,1,1,1,1,1,1,1,1,1,1,-1,-1,-1,-1,-1,-1,1,1,1,1,1,1,1,1,1,1,1,-1,-1,-1,-1,-1,1,1,1,1,1,1,1,1,1,1,1,1,-1,-1,-1,-1,1,1,1,1,1,1,1,1,1,1,1,1,1,-1,-1,-1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,-1,-1]}

noteoffset = {}
noteoffset['B'] = 11
noteoffset['A♯'] = 10
noteoffset['A'] = 9
noteoffset['G♯'] = 8
noteoffset['G'] = 7
noteoffset['F♯'] = 6
noteoffset['F'] = 5
noteoffset['E'] = 4
noteoffset['D♯'] = 3
noteoffset['D'] = 2
noteoffset['C♯'] = 1
noteoffset['C'] = 0

inst_names = {
"chip": "Chip Wave",
"PWM": "Pulse Width",
"harmonics": "Harmonics",
"Picked String": "Picked String",
"spectrum": "Spectrum",
"FM": "FM",
"custom chip": "Custom Chip",
"noise": "Basic Noise",
"drumset": "Drum Set"
}

def getcolor_p():
    global colornum_p
    out_color = colors_pitch[colornum_p]
    colornum_p += 1
    if colornum_p == 10: colornum_p = 0
    return out_color

def getcolor_d():
    global colornum_d
    out_color = colors_drums[colornum_d]
    colornum_d += 1
    if colornum_d == 5: colornum_d = 0
    return out_color

def calcval(value):
    global jummbox_beatsPerBar
    global jummbox_ticksPerBeat
    return (value*(jummbox_beatsPerBar/jummbox_ticksPerBeat))/2

def addfx(trackid, fxname):
    pluginid = trackid+'_'+fxname
    plugins.add_plug(cvpj_l, pluginid, 'native-jummbox', fxname)
    plugins.add_plug_fxdata(cvpj_l, pluginid, True, 1)
    tracks.insert_fxslot(cvpj_l, ['instrument', trackid], 'audio', pluginid)
    return pluginid

def addfx_eq(trackid):
    pluginid = trackid+'_'+'eq'
    plugins.add_plug(cvpj_l, pluginid, 'eq', 'peaks')
    plugins.add_plug_fxdata(cvpj_l, pluginid, True, 1)
    tracks.insert_fxslot(cvpj_l, ['instrument', trackid], 'audio', pluginid)
    return pluginid

def get_harmonics(i_harmonics):
    harmonics = [i/100 for i in i_harmonics]
    harmonics.append(harmonics[-1])
    harmonics.append(harmonics[-1])
    harmonics.append(harmonics[-1])
    return harmonics

def parse_instrument(channum, instnum, bb_instrument, bb_type, bb_color):
    global idvals_inst_beepbox
    bb_volume = bb_instrument['volume']

    if 'preset' in bb_instrument: bb_preset = str(bb_instrument['preset'])
    else: bb_preset = None

    trackid = 'bb_ch'+str(channum)+'_inst'+str(instnum)

    instslot = {}
    cvpj_volume = (bb_volume/50)+0.5

    a_decay = 3
    a_sustain = 1

    gm_inst = None
    if bb_preset in idvals_inst_beepbox:
        gm_inst = idvals.get_idval(idvals_inst_beepbox, bb_preset, 'gm_inst')

    if gm_inst != None:
        plugins.add_plug_gm_midi(cvpj_l, trackid, 0, gm_inst)
        cvpj_instname = idvals.get_idval(idvals_inst_beepbox, bb_preset, 'name')

        tracks.m_create_inst(cvpj_l, trackid, {'pluginid': trackid})
        tracks.m_basicdata_inst(cvpj_l, trackid, cvpj_instname, bb_color, None, None)
    else:
        bb_inst_effects = bb_instrument['effects']
        bb_inst_type = bb_instrument['type']
        plugins.add_plug(cvpj_l, trackid, 'native-jummbox', bb_inst_type)

        if 'unison' in bb_instrument:
            plugins.add_plug_data(cvpj_l, trackid, 'unison', bb_instrument['unison'])

        cvpj_instname = inst_names[bb_inst_type]

        if bb_inst_type == 'chip':
            bb_inst_wave = bb_instrument['wave']
            cvpj_instname = bb_inst_wave+' ('+cvpj_instname+')'
            if bb_inst_wave in rawChipWaves:
                wavesample = rawChipWaves[bb_inst_wave]['samples']
                plugins.add_wave(cvpj_l, trackid, 'chipwave', wavesample, min(wavesample), max(wavesample))

        if bb_inst_type == 'PWM':
            pulseWidth = bb_instrument['pulseWidth']
            cvpj_instname = str(pulseWidth)+'% pulse ('+cvpj_instname+')'
            plugins.add_plug_param(cvpj_l, trackid, "pulse_width", pulseWidth/100, 'float', "Pulse Width")

        if bb_inst_type == 'harmonics':
            harmonics = get_harmonics(bb_instrument['harmonics'])
            plugins.add_harmonics(cvpj_l, trackid, 'harmonics', harmonics)

        if bb_inst_type == 'Picked String':
            harmonics = get_harmonics(bb_instrument['harmonics'])
            plugins.add_harmonics(cvpj_l, trackid, 'harmonics', harmonics)
            a_sustain = bb_instrument['stringSustain']/100

        if bb_inst_type == 'spectrum':
            plugins.add_plug_data(cvpj_l, trackid, 'spectrum', bb_instrument['spectrum'])

        if bb_inst_type == 'FM':
            plugins.add_plug_data(cvpj_l, trackid, 'algorithm', bb_instrument['algorithm'])
            plugins.add_plug_data(cvpj_l, trackid, 'feedback_type', bb_instrument['feedbackType'])
            plugins.add_plug_param(cvpj_l, trackid, "feedback_amplitude", bb_instrument['feedbackAmplitude'], 'int', "Feedback Amplitude")

            for opnum in range(4):
                opdata = bb_instrument['operators'][opnum]
                opnumtext = 'op'+str(opnum+1)+'_'
                plugins.add_plug_data(cvpj_l, trackid, opnumtext+'frequency', opdata['frequency'])
                op_waveform = data_values.get_value(opdata, 'waveform', 'sine')
                plugins.add_plug_data(cvpj_l, trackid, opnumtext+'waveform', op_waveform)
                op_pulseWidth = data_values.get_value(opdata, 'waveform', 'sine')
                plugins.add_plug_data(cvpj_l, trackid, opnumtext+'pulseWidth', 5)
                plugins.add_plug_param(cvpj_l, trackid, opnumtext+"amplitude", opdata['amplitude'], 'int', "")

        if bb_inst_type == 'custom chip':
            customChipWave = bb_instrument['customChipWave']
            customChipWave = [customChipWave[str(i)] for i in range(64)]
            plugins.add_wave(cvpj_l, trackid, 'chipwave', customChipWave, -24, 24)

        tracks.m_create_inst(cvpj_l, trackid, {'pluginid': trackid})
        tracks.m_basicdata_inst(cvpj_l, trackid, cvpj_instname, bb_color, cvpj_volume, None)

        if 'eqFilterType' in bb_instrument:
            if bb_instrument['eqFilterType'] == False:
                if 'eqSubFilters0' in bb_instrument:
                    pluginid = addfx_eq(trackid)
                    plugins.add_plug_fxvisual(cvpj_l, pluginid, 'EQ', None)
                    for eqfiltdata in bb_instrument['eqSubFilters0']:
                        eqgain_pass = eqfiltdata['linearGain']
                        eqgain = (eqfiltdata['linearGain']-2)*6
                        eqtype = eqfiltdata['type']
                        if eqtype == 'low-pass':
                            plugins.add_eqband(cvpj_l, pluginid, 1, eqfiltdata['cutoffHz'], 0, 'low_pass', eqgain_pass)
                        if eqtype == 'peak':
                            plugins.add_eqband(cvpj_l, pluginid, 1, eqfiltdata['cutoffHz'], eqgain, 'peak', 1)
                        if eqtype == 'high-pass':
                            plugins.add_eqband(cvpj_l, pluginid, 1, eqfiltdata['cutoffHz'], 0, 'high_pass', eqgain_pass)
            else:
                pluginid = addfx(trackid, 'filter')
                plugins.add_plug_fxvisual(cvpj_l, pluginid, 'Filter', None)
                plugins.add_plug_param(cvpj_l, pluginid, 'cutoff', bb_instrument['eqSimpleCut'], 'int', "")
                plugins.add_plug_param(cvpj_l, pluginid, 'reso', bb_instrument['eqSimplePeak'], 'int', "")
        elif 'eqFilter' in bb_instrument:
            bb_eqFilter = bb_instrument['eqFilter']
            if bb_eqFilter != []:
                pluginid = addfx_eq(trackid)
                plugins.add_plug_fxvisual(cvpj_l, pluginid, 'EQ', None)
                for eqfiltdata in bb_eqFilter:
                    eqgain_pass = eqfiltdata['linearGain']
                    eqgain = (eqfiltdata['linearGain']-2)*6
                    eqtype = eqfiltdata['type']
                    if eqtype == 'low-pass':
                        plugins.add_eqband(cvpj_l, pluginid, 1, eqfiltdata['cutoffHz'], 0, 'low_pass', eqgain_pass)
                    if eqtype == 'peak':
                        plugins.add_eqband(cvpj_l, pluginid, 1, eqfiltdata['cutoffHz'], eqgain, 'peak', 1)
                    if eqtype == 'high-pass':
                        plugins.add_eqband(cvpj_l, pluginid, 1, eqfiltdata['cutoffHz'], 0, 'high_pass', eqgain_pass)

        if 'distortion' in bb_inst_effects:
            pluginid = addfx(trackid, 'distortion')
            plugins.add_plug_fxvisual(cvpj_l, pluginid, 'Distortion', None)
            plugins.add_plug_param(cvpj_l, pluginid, 'amount', bb_instrument['distortion']/100, 'float', "")
            if 'aliases' in bb_instrument: plugins.add_plug_data(cvpj_l, pluginid, 'aliases', bb_instrument['aliases'])

        if 'bitcrusher' in bb_inst_effects:
            pluginid = addfx(trackid, 'bitcrusher')
            plugins.add_plug_fxvisual(cvpj_l, pluginid, 'Bitcrusher', None)
            plugins.add_plug_param(cvpj_l, pluginid, 'octave', bb_instrument['bitcrusherOctave'], 'float', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'quantization', bb_instrument['bitcrusherQuantization']/100, 'float', "")

        if 'chorus' in bb_inst_effects:
            pluginid = addfx(trackid, 'chorus')
            plugins.add_plug_fxvisual(cvpj_l, pluginid, 'Chorus', None)
            plugins.add_plug_param(cvpj_l, pluginid, 'amount', bb_instrument['chorus']/100, 'float', "")

        if 'echo' in bb_inst_effects:
            pluginid = addfx(trackid, 'echo')
            plugins.add_plug_fxvisual(cvpj_l, pluginid, 'Echo', None)
            plugins.add_plug_param(cvpj_l, pluginid, 'sustain', bb_instrument['echoSustain']/100, 'float', "")
            plugins.add_plug_param(cvpj_l, pluginid, 'delay_beats', bb_instrument['echoDelayBeats'], 'int', "")

        if 'reverb' in bb_inst_effects:
            pluginid = addfx(trackid, 'reverb')
            plugins.add_plug_fxvisual(cvpj_l, pluginid, 'Reverb', None)
            plugins.add_plug_param(cvpj_l, pluginid, 'amount', bb_instrument['reverb']/100, 'float', "")

        if 'vibrato' in bb_inst_effects:
            if 'vibratoSpeed' in bb_instrument and 'vibratoDelay' in bb_instrument:
                if bb_instrument['vibratoSpeed'] != 0 and bb_instrument['vibratoDelay'] != 50:
                    vibrato_speed = 0.7*(1/bb_instrument['vibratoSpeed'])
                    vibrato_amount = bb_instrument['vibratoDepth']
                    vibrato_delay = (bb_instrument['vibratoDelay']/49)*2
                    plugins.add_lfo(cvpj_l, pluginid, 'pitch', 'sine', 'seconds', vibrato_speed, vibrato_delay, 0, vibrato_amount)

        a_attack = data_values.get_value(bb_instrument, 'fadeInSeconds', 0)
        a_release = abs(data_values.get_value(bb_instrument, 'fadeOutTicks', 0)/(jummbox_ticksPerBeat*32))
        plugins.add_asdr_env(cvpj_l, trackid, 'vol', 0, a_attack, 0, a_decay, a_sustain, a_release, 1)


def parse_notes(channum, bb_notes, bb_instruments):
    cvpj_notelist = []
    for note in bb_notes:
        points = note['points']
        pitches = note['pitches']

        cvpj_note_pos = (points[-1]['tick'] - points[0]['tick'])

        t_duration = calcval(cvpj_note_pos)
        t_position = calcval(points[0]['tick'])
        t_auto_pitch = []
        t_auto_gain = []

        arr_bendvals = []
        arr_volvals = []

        for point in points:
            t_auto_pitch.append({'position': calcval(point['tick']-points[0]['tick']), 'value': point['pitchBend']})
            arr_bendvals.append(point['pitchBend'])
            arr_volvals.append(point['volume'])

        maxvol = max(arr_volvals)

        for point in points:
            if maxvol != 0:
                t_auto_gain.append({'position': calcval(point['tick']-points[0]['tick']), 'value': (point['volume']*(1/maxvol))})

        t_vol = maxvol/100

        cvpj_notemod = {}
        cvpj_notemod['auto'] = {}

        if all(element == arr_volvals[0] for element in arr_volvals) == False:
            cvpj_notemod['auto']['gain'] = t_auto_gain

        if all(element == arr_bendvals[0] for element in arr_bendvals) == False:
            cvpj_notemod['auto']['pitch'] = t_auto_pitch

            if len(pitches) == 1:
                cvpj_notemod['slide'] = []
                for pinu in range(len(t_auto_pitch)-1):
                    slide_dur = t_auto_pitch[pinu+1]['position'] - t_auto_pitch[pinu]['position']

                    if t_auto_pitch[pinu+1]['value'] != t_auto_pitch[pinu]['value']:
                        cvpj_notemod['slide'].append({
                            'position': t_auto_pitch[pinu]['position'], 
                            'duration': slide_dur, 
                            'key': t_auto_pitch[pinu+1]['value']})

        for pitch in pitches:
            t_key = pitch-48 + jummbox_key
            for bb_instrument in bb_instruments:
                t_instrument = 'bb_ch'+str(channum)+'_inst'+str(bb_instrument)
                cvpj_note = note_data.mx_makenote(t_instrument, t_position, t_duration, t_key, t_vol, None)
                cvpj_note['notemod'] = cvpj_notemod
                cvpj_notelist.append(cvpj_note)
    return cvpj_notelist


def parse_channel(channeldata, channum):
    global jummbox_notesize
    global jummbox_beatsPerBar
    global jummbox_ticksPerBeat

    bbcvpj_placementnames[channum] = []
    bb_color = None
    bb_type = channeldata['type']
    bb_instruments = channeldata['instruments']
    bb_patterns = channeldata['patterns']
    bb_sequence = channeldata['sequence']

    if bb_type == 'pitch' or bb_type == 'drum':
        if bb_type == 'pitch': bb_color = getcolor_p()
        if bb_type == 'drum': bb_color = getcolor_d()

        t_instnum = 1
        for bb_instrument in bb_instruments:
            parse_instrument(channum, t_instnum, bb_instrument, bb_type, bb_color)
            cvpj_instid = 'bb_ch'+str(channum)+'_inst'+str(t_instnum)

            if 'panning' in bb_instrument['effects']: tracks.m_param_inst(cvpj_l, cvpj_instid, 'pan', bb_instrument['pan']/50)
            #if 'pitch shift' in bb_instrument['effects']: tracks.m_param_instdata(cvpj_l, cvpj_instid, 'pitch', (bb_instrument['pitchShiftSemitones']-12)*100 )
            if 'detune' in bb_instrument['effects']: tracks.m_param_instdata(cvpj_l, cvpj_instid, 'pitch', bb_instrument['detuneCents'] )

            tracks.m_playlist_pl(cvpj_l, str(channum), None, bb_color, None)
            t_instnum += 1

        patterncount = 0
        for bb_pattern in bb_patterns:
            nid_name = str(patterncount+1)
            cvpj_patid = 'bb_ch'+str(channum)+'_pat'+str(patterncount)
            bb_notes = bb_pattern['notes']
            if 'instruments' in bb_pattern: bb_instruments = bb_pattern['instruments']
            else: bb_instruments = [1]
            if bb_notes != []: tracks.m_add_nle(cvpj_l, cvpj_patid, parse_notes(channum, bb_notes, bb_instruments))
            patterncount += 1

        sequencecount = 0
        for bb_part in bb_sequence:
            if bb_part != 0:
                cvpj_l_placement = placement_data.makepl_n_mi(calcval(sequencecount*jummbox_notesize), calcval(jummbox_ticksPerBeat*jummbox_beatsPerBar), 'bb_ch'+str(channum)+'_pat'+str(bb_part-1))
                tracks.m_playlist_pl_add(cvpj_l, str(channum), cvpj_l_placement)
                bbcvpj_placementnames[channum].append('bb_ch'+str(channum)+'_pat'+str(bb_part-1))
            else:
                bbcvpj_placementnames[channum].append(None)
            sequencecount += 1

    if bb_type == 'mod':
        modChannels = bb_instruments[0]['modChannels']
        modInstruments = bb_instruments[0]['modInstruments']
        modSettings = bb_instruments[0]['modSettings']

        bb_def = []
        for num in range(6):
            bb_def.append([modChannels[num],modInstruments[num],modSettings[num]])

        sequencecount = 0
        for bb_part in bb_sequence:
            if bb_part != 0:
                basepos = sequencecount*jummbox_notesize
                bb_modnotes = bb_patterns[bb_part-1]['notes']
                if bb_modnotes != []:
                    for note in bb_modnotes:
                        bb_mod_points = note['points']
                        bb_mod_pos = basepos+bb_mod_points[0]['tick']
                        bb_mod_dur = bb_mod_points[-1]['tick'] - bb_mod_points[0]['tick']
                        bb_mod_target = bb_def[(note['pitches'][0]*-1)+5]

                        cvpj_autodata_points = []
                        for bb_mod_point in bb_mod_points:
                            cvpj_pointdata = {}
                            cvpj_pointdata["position"] = calcval(bb_mod_point['tick'])-calcval(bb_mod_pos)+calcval(basepos)
                            cvpj_pointdata["value"] = bb_mod_point['volume']
                            cvpj_autodata_points.append(cvpj_pointdata)

                        cvpj_autodata = auto.makepl(calcval(bb_mod_pos), calcval(bb_mod_dur), cvpj_autodata_points)

                        if bb_mod_target[0] == -1:
                            if bb_mod_target[2] == 1: 
                                cvpj_autopl = auto.multiply([cvpj_autodata], 0, 0.01)
                                tracks.a_add_auto_pl(cvpj_l, 'float', ['main', 'vol'], cvpj_autopl[0])
                            elif bb_mod_target[2] == 2: 
                                cvpj_autopl = auto.multiply([cvpj_autodata], 30, 1)
                                tracks.a_add_auto_pl(cvpj_l, 'float', ['main', 'bpm'], cvpj_autopl[0])
                            elif bb_mod_target[2] == 17: 
                                cvpj_autopl = auto.multiply([cvpj_autodata], -250, 0.01)
                                tracks.a_add_auto_pl(cvpj_l, 'float', ['main', 'pitch'], cvpj_autopl[0])

                        else:
                            auto_instnum = 1
                            auto_trackid = 'bb_ch'+str(bb_mod_target[0]+1)+'_inst'+str(bb_mod_target[1]+1)

                            if bb_mod_target[2] == 6: 
                                cvpj_autopl = auto.multiply([cvpj_autodata], -50, 0.02)
                                tracks.a_add_auto_pl(cvpj_l, 'float', ['track', auto_trackid, 'pan'], cvpj_autopl[0])
                            elif bb_mod_target[2] == 15: 
                                cvpj_autopl = auto.multiply([cvpj_autodata], -200, 1)
                                tracks.a_add_auto_pl(cvpj_l, 'float', ['track', auto_trackid, 'pitch'], cvpj_autodata)
                            elif bb_mod_target[2] == 36: 
                                cvpj_autopl = auto.multiply([cvpj_autodata], 0, 0.04)
                                tracks.a_add_auto_pl(cvpj_l, 'float', ['track', auto_trackid, 'vol'], cvpj_autopl[0])



            sequencecount += 1


class input_jummbox(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'jummbox'
    def getname(self): return 'jummbox'
    def gettype(self): return 'mi'
    def getdawcapabilities(self): 
        return {
        'fxrack': False,
        'track_lanes': True,
        'placement_cut': False,
        'placement_loop': False,
        'auto_nopl': False,
        'track_nopl': False
        }
    def supported_autodetect(self): return False
    def parse(self, input_file, extra_param):
        global cvpj_l

        global idvals_inst_beepbox

        global jummbox_beatsPerBar
        global jummbox_ticksPerBeat
        global jummbox_key

        global bbcvpj_placementsize
        global bbcvpj_placementnames

        cvpj_l = {}

        idvals_inst_beepbox = idvals.parse_idvalscsv('data_idvals/beepbox_inst.csv')

        bbcvpj_placementsize = []
        bbcvpj_placementnames = {}

        bytestream = open(input_file, 'r', encoding='utf8')
        jummbox_json = json.load(bytestream)

        cvpj_l_track_data = {}
        cvpj_l_track_order = []
        cvpj_l_track_placements = {}

        if 'name' in jummbox_json: song.add_info(cvpj_l, 'title', jummbox_json['name'])
        
        jummbox_key = noteoffset[jummbox_json['key']]
        jummbox_channels = jummbox_json['channels']
        jummbox_beatsPerBar = jummbox_json['beatsPerBar']
        jummbox_ticksPerBeat = jummbox_json['ticksPerBeat']
        jummbox_beatsPerMinute = jummbox_json['beatsPerMinute']
        jummbox_channels = jummbox_json['channels']

        if 'introBars' in jummbox_json and 'loopBars' in jummbox_json:
            introbars = jummbox_json['introBars']*32
            loopbars = jummbox_json['loopBars']*32 + introbars
            song.add_timemarker_looparea(cvpj_l, 'Loop', introbars, loopbars)

        global jummbox_notesize
        jummbox_notesize = jummbox_beatsPerBar*jummbox_ticksPerBeat

        chancount = 1
        for jummbox_channel in jummbox_channels:
            parse_channel(jummbox_channel, chancount)
            chancount += 1

        cvpj_l['do_addloop'] = True

        cvpj_l['bpm'] = jummbox_beatsPerMinute

        return json.dumps(cvpj_l)
