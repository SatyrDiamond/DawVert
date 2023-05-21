# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from functions import auto
from functions import idvals
from functions import tracks
from functions import note_data
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

def parse_instrument(channum, instnum, bb_instrument, bb_type, bb_color):
    global idvals_inst_beepbox
    bb_effects = bb_instrument['effects']
    bb_type = bb_instrument['type']
    bb_volume = bb_instrument['volume']

    if 'preset' in bb_instrument: bb_preset = str(bb_instrument['preset'])
    else: bb_preset = None

    trackid = 'bb_ch'+str(channum)+'_inst'+str(instnum)

    instslot = {}
    cvpj_volume = (bb_volume/50)+0.5

    gm_inst = None
    if bb_preset in idvals_inst_beepbox:
        gm_inst = idvals.get_idval(idvals_inst_beepbox, bb_preset, 'gm_inst')

    cvpj_instdata = {}
    if gm_inst == None:
        cvpj_instdata['plugin'] = 'native-jummbox'
        cvpj_instdata['plugindata'] = {'type':bb_type, 'data':bb_instrument}
        cvpj_instname = inst_names[bb_type]
    else:
        cvpj_instdata['plugin'] = 'general-midi'
        cvpj_instdata['plugindata'] = {'bank':0, 'inst':gm_inst}
        cvpj_instname = idvals.get_idval(idvals_inst_beepbox, bb_preset, 'name')

    tracks.m_create_inst(cvpj_l, trackid, cvpj_instdata)
    tracks.m_basicdata_inst(cvpj_l, trackid, cvpj_instname, bb_color, None, None)

def parse_notes(channum, bb_notes, bb_instruments):
    cvpj_notelist = []
    for note in bb_notes:
        points = note['points']
        pitches = note['pitches']
        cvpj_note_pos = (points[-1]['tick'] - points[0]['tick'])

        t_duration = calcval(cvpj_note_pos)
        t_position = calcval(points[0]['tick'])
        t_vol = points[0]['volume']/100
        t_auto_pitch = []

        arr_bendvals = []
        arr_volvals = []
        for point in points:
            t_auto_pitch.append({'position': calcval(point['tick']-points[0]['tick']), 'value': point['pitchBend']})
            arr_bendvals.append(point['pitchBend'])
            arr_volvals.append(point['volume'])

        cvpj_notemod = {}
        cvpj_notemod['auto'] = {}
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

            #print(bb_instrument['effects'])

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
            bb_def.append([modChannels[num],modSettings[num]])

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
                        #print(bb_mod_pos, bb_mod_dur, bb_mod_target)
                        cvpj_autodata_points = []
                        for bb_mod_point in bb_mod_points:
                            cvpj_pointdata = {}
                            cvpj_pointdata["position"] = calcval(bb_mod_point['tick'])-calcval(bb_mod_pos)+calcval(basepos)
                            cvpj_pointdata["value"] = bb_mod_point['volume']
                            cvpj_autodata_points.append(cvpj_pointdata)

                        cvpj_autodata = auto.makepl(calcval(bb_mod_pos), calcval(bb_mod_dur), cvpj_autodata_points)


                        if bb_mod_target[0] == -1:
                            if bb_mod_target[1] == 1: 
                                cvpj_autopl = auto.multiply([cvpj_autodata], 0, 0.01)
                                tracks.a_add_auto_pl(cvpj_l, ['main', 'vol'], cvpj_autopl[0])
                            if bb_mod_target[1] == 2: 
                                cvpj_autopl = auto.multiply([cvpj_autodata], 30, 1)
                                tracks.a_add_auto_pl(cvpj_l, ['main', 'bpm'], cvpj_autopl[0])
                            if bb_mod_target[1] == 17: 
                                cvpj_autopl = auto.multiply([cvpj_autodata], -250, 4)
                                tracks.a_add_auto_pl(cvpj_l, ['main', 'pitch'], cvpj_autopl[0])
                        else:
                            auto_instnum = 1
                            auto_trackid = 'bb_ch'+str(bb_mod_target[0]+1)+'_inst'+str(auto_instnum)

                            if bb_mod_target[1] == 6: 
                                cvpj_autopl = auto.multiply([cvpj_autodata], -50, 0.02)
                                tracks.a_add_auto_pl(cvpj_l, ['track', auto_trackid, 'pan'], cvpj_autopl[0])
                            if bb_mod_target[1] == 15: 
                                cvpj_autopl = auto.multiply([cvpj_autodata], -200, 1)
                                tracks.a_add_auto_pl(cvpj_l, ['track', auto_trackid, 'pitch'], cvpj_autodata)
                            #if bb_mod_target[1] == 34: 
                            #    cvpj_autopl = auto.multiply([cvpj_autodata], -12, 100)
                            #    tracks.a_add_auto_pl(cvpj_l, ['track', 'bb_ch'+str(bb_mod_target[0]+1)+'_inst1', 'pitch'], cvpj_autopl[0])

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
        'r_track_lanes': True,
        'placement_cut': False,
        'placement_loop': False,
        'no_pl_auto': False,
        'no_placements': False
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

        cvpj_l['use_instrack'] = False
        cvpj_l['use_fxrack'] = False
        cvpj_l['use_placements_notes'] = True

        cvpj_l['bpm'] = jummbox_beatsPerMinute

        return json.dumps(cvpj_l)
