# SPDX-FileCopyrightText: 2022 Colby Ray
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import argparse
import _func_song

parser = argparse.ArgumentParser()
parser.add_argument("cvpjm")
parser.add_argument("cvpj")

args = parser.parse_args()

def find_instrument_id(idnum, cvpjm_instrument_json):
    instrumentoutput = None
    for instrument in cvpjm_instrument_json:
        if instrument["id"] == idnum:
            instrumentoutput = instrument
    return instrumentoutput

def add_to_seperated_object(seperated_object_table, objectdata, instrument):
    instrumentfound = 0
    if seperated_object_table == []:
        seperated_object_table.append([instrument,[objectdata]])
    else:
        for prognote in seperated_object_table:
            if prognote[0] == instrument:
                instrumentfound = 1
                prognote[1].append(objectdata)
        if instrumentfound == 0:
            seperated_object_table.append([instrument,[objectdata]])

def seperate_instrument_placement_notelist(placement):
    seperated_notelist_table = []
    for note in placement['notelist']:
        copy_note = note.copy()
        instrument = copy_note['instrument']
        del copy_note['instrument']
        add_to_seperated_object(seperated_notelist_table, copy_note, instrument)
    return seperated_notelist_table

def seperate_instrument_placements(placement):
    global seperated_placement_table
    prognotetable = seperate_instrument_placement_notelist(placement)
    for prognote in prognotetable:
        instrument = prognote[0]
        notelist = prognote[1]
        placement_foroutput = placement.copy()
        del placement_foroutput['notelist']
        placement_foroutput['notelist'] = notelist
        add_to_seperated_object(seperated_placement_table, placement_foroutput, instrument)

def seperate_instrument_placements_get():
    return seperated_placement_table

def seperate_instrument_placements_init():
    global seperated_placement_table
    seperated_placement_table = []

def seperate_track_from_instruments(track, cvpjm_instrument_json):
    instrumentnumberslist = []
    seperate_instrument_placements_init()
    placements = track['placements']
    for placement in placements:
        seperate_instrument_placements(placement)
    seperated_placement_table = seperate_instrument_placements_get()
    out_tracks = []
    for seperated_placement in seperated_placement_table:
        out_track = track.copy()
        out_track['placements'] = seperated_placement[1]
        out_track['type'] = 'instrument'
        out_track['frominstrumentid'] = seperated_placement[0]
        out_tracks.append(out_track)
    return out_tracks

with open(args.cvpjm + '.cvpjm', 'r') as cvpjm:
    cvpjm_json = json.loads(cvpjm.read())

cvpjm_tracks_json = cvpjm_json['tracks']
cvpjm_instrument_json = cvpjm_json['instruments']

output_tracks = []
for cvpjm_track_json in cvpjm_tracks_json:
    seperatedtracks = seperate_track_from_instruments(cvpjm_track_json, cvpjm_instrument_json)
    for seperatedtrack in seperatedtracks:
        output_tracks.append(seperatedtrack)

#add instrument-placement
all_instrument_placements_table = []
for output_track in output_tracks:
    instrumentid = output_track['frominstrumentid']
    print(instrumentid, end=": ")
    for trackplacement in output_track['placements']:
        add_to_seperated_object(all_instrument_placements_table, trackplacement, instrumentid)
        print('P', end=" ")
    print()

#view combine instrument-placement
print('\noutput:')
for instrument_placement in all_instrument_placements_table:
    print(instrument_placement[0], end=": ")
    for placement in instrument_placement[1]:
        print('P', end=" ")
    print()

optimized_tracks = []
#add instrument for each instrument
for instrument_placement in all_instrument_placements_table:
    print('\ninst:', instrument_placement[0])
    singleinst_placements_table = []
    for placement in instrument_placement[1]:
        position = placement['position']
        add_to_seperated_object(singleinst_placements_table,placement,position)
    singleinst_tracksplacements = []
    print('\npos-num output:')
    for singleinst_placement in singleinst_placements_table:
        print(singleinst_placement[0], len(singleinst_placement[1]))
        for number in range(len(singleinst_placement[1])):
            add_to_seperated_object(singleinst_tracksplacements,singleinst_placement[1][number],number)
    print('\npos-placement output:')
    for singleinst_tracksplacement in singleinst_tracksplacements:
        print(singleinst_tracksplacement[0], len(singleinst_tracksplacement[1]))
        out_track = {}
        instdata = find_instrument_id(instrument_placement[0], cvpjm_instrument_json)
        if instdata != None:
            if instdata['name'] == '':
                out_track['name'] = str(instrument_placement[0])
            else:
                out_track['name'] = instdata['name']
            out_track['instrumentdata'] = instdata['instrumentdata']
            out_track['placements'] = singleinst_tracksplacement[1]
            out_track['type'] = 'instrument'
            out_track['vol'] = instdata['volume']
            out_track['fxrack_channel'] = instdata['fxrack_channel']
            out_track['frominstrumentid'] = singleinst_tracksplacement[0]
            optimized_tracks.append(out_track)

cvpj_json_out = cvpjm_json.copy()
del cvpj_json_out['tracks']
del cvpj_json_out['instruments']

cvpj_json_out['tracks'] = optimized_tracks

with open(args.cvpj + '.cvpj', 'w') as outfile:
        outfile.write(json.dumps(cvpj_json_out, indent=2))
