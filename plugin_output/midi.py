# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_output
import difflib
import json
import mido
from functions import placements
from functions import idvals
from functions import notelist_data
from functions import xtramath

unusedchannel = 0

def getunusedchannel():
    global unusedchannel
    unusedchannel += 1
    if unusedchannel == 10: unusedchannel += 1
    if unusedchannel == 16: unusedchannel = 1
    return unusedchannel

def add_cmd(i_list, i_pos, i_cmd):
    if i_pos not in i_list: i_list[i_pos] = []
    i_list[i_pos].append(i_cmd)

class output_cvpj_f(plugin_output.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'output'
    def getname(self): return 'MIDI'
    def getshortname(self): return 'midi'
    def gettype(self): return 'r'
    def plugin_archs(self): return None
    def getdawcapabilities(self): 
        return {
        'fxrack': True,
        'track_lanes': False,
        'placement_cut': False,
        'placement_loop': False,
        'auto_nopl': True,
        'track_nopl': False
        }
    def getsupportedplugins(self): return []
    def parse(self, convproj_json, output_file):
        projJ = json.loads(convproj_json)

        idvals_names_gmmidi = idvals.parse_idvalscsv('data_idvals/names_gmmidi.csv')
        idvals_names_gmmidi_drums = idvals.parse_idvalscsv('data_idvals/names_gmmidi_drums.csv')
 
        wordlist_drums = list(idvals_names_gmmidi_drums.keys())
        wordlist = list(idvals_names_gmmidi.keys())

        midi_tracknum = 0

        guess_gmmidi = True

        midiobj = mido.MidiFile()

        multi_miditrack = []

        if 'track_data' in projJ and 'track_order' in projJ:
            #print('[output-midi] Trk# | Ch# | Bnk | Prog | Key | Name')
            print('[output-midi] Trk# | Ch# | Prog | Name')

            for _ in range(len(projJ['track_order'])+1):
                multi_miditrack.append(mido.MidiTrack())

            tracknum = 0

            midi_tempo = 555555
            midi_numerator = 4
            midi_denominator = 4

            if 'timesig_numerator' in projJ: midi_numerator = int(projJ['timesig_numerator'])
            if 'timesig_denominator' in projJ: midi_denominator = int(projJ['timesig_denominator'])
            if 'bpm' in projJ: midi_tempo = mido.bpm2tempo(projJ['bpm'])

            multi_miditrack[0].append(mido.MetaMessage('time_signature', numerator=midi_numerator, denominator=midi_denominator, clocks_per_click=24, notated_32nd_notes_per_beat=8, time=0))

            multi_miditrack[0].append(mido.MetaMessage('set_tempo', tempo=midi_tempo, time=0))

            for trackid in projJ['track_order']:
                if trackid in projJ['track_data']:
                    trackdata = projJ['track_data'][trackid]

                    midi_defined = False
                    midi_channel = None
                    midi_bank = None
                    midi_program = None
                    midi_key = None
                    midi_trackname = ''

                    if 'name' in trackdata:
                        midi_trackname = trackdata['name']

                    if guess_gmmidi == True:
                        if midi_trackname != '':
                            guessedinst = difflib.get_close_matches(midi_trackname, wordlist)
                            if guessedinst:
                                midi_defined = True
                                midi_program = idvals.get_idval(idvals_names_gmmidi, guessedinst[0], 'gm_inst')

                    if 'instdata' in trackdata:
                        trackinstdata = trackdata['instdata']
                        if 'plugin' in trackinstdata:
                            if trackinstdata['plugin'] == 'general-midi':
                                if 'plugindata' in trackinstdata:
                                    midi_defined = True
                                    if trackinstdata['plugindata']['bank'] < 128:
                                        midi_program = trackinstdata['plugindata']['inst']
                                        midi_bank = trackinstdata['plugindata']['bank']
                                    else:
                                        midi_bank = trackinstdata['plugindata']['bank']-128

                    if 'fxrack_channel' in trackdata:
                        if 16 > trackdata['fxrack_channel'] > 1:
                            midi_channel = trackdata['fxrack_channel']-1

                    #print(trackdata)

                    if midi_channel == None: midi_channel = getunusedchannel()

                    print('[output-midi]', end=" ")

                    print(str(tracknum+1).rjust(4), end=" | ")
                
                    if midi_channel == None: print('---', end=" | ")
                    else: print(str(midi_channel).rjust(3), end=" | ")

                    #if midi_bank == None: print('---', end=" | ")
                    #else: print(str(midi_bank).rjust(3), end=" | ")
    
                    if midi_program == None: print('----', end=" | ")
                    else: print(str(midi_program).rjust(4), end=" | ")
    
                    #if midi_key == None: print('---', end=" | ")
                    #else: print(str(midi_key).rjust(3), end=" | ")
                    print(midi_trackname)

                    miditrack = multi_miditrack[tracknum+1]

                    if midi_trackname != '': multi_miditrack[0].append(mido.MetaMessage('track_name', name=midi_trackname, time=0))

                    if midi_program != None: miditrack.append(mido.Message('program_change', channel=midi_channel, program=midi_program, time=0))
                    else: miditrack.append(mido.Message('program_change', channel=midi_channel, program=0, time=0))

                    i_list = {}

                    if trackid in projJ['track_placements']:
                        if 'notes' in projJ['track_placements'][trackid]:
                            for cvpj_tr_pl in projJ['track_placements'][trackid]['notes']:
                                cvpj_tr_pl_pos = cvpj_tr_pl['position']
                                cvpj_tr_pl_nl = cvpj_tr_pl['notelist']
                                cvpj_tr_pl_muted = False
                                if 'muted' in cvpj_tr_pl: cvpj_tr_pl_muted = cvpj_tr_pl['muted']
                                if cvpj_tr_pl_muted == False:
                                    for cvpj_tr_pl_n in cvpj_tr_pl_nl:
                                        #print(cvpj_tr_pl_n)
                                        cvmi_n_pos = int(cvpj_tr_pl_pos*4 + cvpj_tr_pl_n['position']*4)*30
                                        cvmi_n_dur = int(cvpj_tr_pl_n['duration']*4)*30
                                        cvmi_n_key = int(cvpj_tr_pl_n['key'])+60
                                        cvmi_n_vol = 127
                                        if 'vol' in cvpj_tr_pl_n: cvmi_n_vol = xtramath.clamp(int(cvpj_tr_pl_n['vol']*127), 0, 127)
                                        add_cmd(i_list, cvmi_n_pos, ['note_on', cvmi_n_key, cvmi_n_vol])
                                        add_cmd(i_list, cvmi_n_pos+cvmi_n_dur, ['note_off', cvmi_n_key])
                                        #print(cvmi_n_pos, cvmi_n_dur, cvmi_n_key)

                    i_list = dict(sorted(i_list.items(), key=lambda item: item[0]))

                    prevpos = 0
                    for i_list_e in i_list:
                        for midi_notedata in i_list[i_list_e]:
                            #print(i_list_e, i_list_e-prevpos, i_list[i_list_e])
                            if midi_notedata[0] == 'note_on': miditrack.append(mido.Message('note_on', channel=midi_channel, note=midi_notedata[1], velocity=midi_notedata[2], time=i_list_e-prevpos))
                            if midi_notedata[0] == 'note_off': miditrack.append(mido.Message('note_off', channel=midi_channel, note=midi_notedata[1], time=i_list_e-prevpos))
                            prevpos = i_list_e

                tracknum += 1

        for tracknum in range(len(projJ['track_order'])+1): midiobj.tracks.append(multi_miditrack[tracknum])
        midiobj.save(output_file)