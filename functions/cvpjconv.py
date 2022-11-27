import json
from functions import song
from functions import datastore

def find_instrument_id(idnum, cvpjm_instrument):
    instrumentoutput = None
    for instrument in cvpjm_instrument:
        if instrument['associd'] == idnum:
            instrumentoutput = instrument
    return instrumentoutput

def seperate_instrument_placement_notelist(placement):
    seperated_notelist_table = []
    for note in placement['notelist']:
        copy_note = note.copy()
        instrument = copy_note['instrument']
        del copy_note['instrument']
        datastore.add_to_seperated_object(seperated_notelist_table, copy_note, instrument)
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
        datastore.add_to_seperated_object(seperated_placement_table, placement_foroutput, instrument)

def seperate_instrument_placements_get():
    return seperated_placement_table

def seperate_instrument_placements_init():
    global seperated_placement_table
    seperated_placement_table = []

def seperate_track_from_instruments(track, cvpjm_instrument, nameordering):
    instrumentnumberslist = []
    seperate_instrument_placements_init()
    placements = track['placements']
    for placement in placements:
        seperate_instrument_placements(placement)
    seperated_placement_table = seperate_instrument_placements_get()
    out_tracks = []
    for seperated_placement in seperated_placement_table:
        out_track = track.copy()
        instdata = find_instrument_id(seperated_placement[0], cvpjm_instrument)
        if instdata != None:
            outputname = ''
            if 'name' in instdata:
                outputname = instdata['name']
            else:
                outputname = 'Inst #' + str(instdata['associd'])
            if 'name' in out_track:
                if nameordering == 'track_inst':
                    outputname = out_track['name'] + ' (' + outputname + ')' 
                else:
                    outputname = outputname + ' (' + out_track['name'] + ')' 

            out_track['name'] = outputname
            out_track['instrumentdata'] = instdata['instrumentdata']
            out_track['placements'] = seperated_placement[1]
            out_track['type'] = 'instrument'
            out_track['vol'] = instdata['vol']
            if 'color' in instdata:
                out_track['color'] = instdata['color']
            if 'fxrack_channel' in instdata:
                out_track['fxrack_channel'] = instdata['fxrack_channel']
            out_track['frominstrumentid'] = seperated_placement[0]
            out_tracks.append(out_track)
    return out_tracks

# ------- convert -------
def convert_multiple_single(cvpj_string_multiple):
    print('[func-projconv] multi2single started')
    mi2s_fixedblock = False
    cvpjm = json.loads(cvpj_string_multiple).copy()

    nameordering = 'inst_track'

    if 'mi2s_fixedblock' in cvpjm:
        if cvpjm['mi2s_fixedblock'] == 1:
            mi2s_fixedblock = True
        del cvpjm['mi2s_fixedblock']

    cvpjm_playlist = cvpjm['playlist'].copy()
    del cvpjm['playlist']

    cvpjm_instrument = cvpjm['instruments'].copy()
    del cvpjm['instruments']

    output_tracks = []
    for cvpjm_track in cvpjm_playlist:
        if 'mi2s_nameordering' in cvpjm_track:
            nameordering = cvpjm_track['mi2s_nameordering']
            del cvpjm_track['mi2s_nameordering']
        seperatedtracks = seperate_track_from_instruments(cvpjm_track, cvpjm_instrument, nameordering)
        printnumseperatedtracks = len(seperatedtracks)
        if printnumseperatedtracks != 1:
            print('[func-projconv] multi2single: InstSeperateTrack to ' + str(printnumseperatedtracks))
        for seperatedtrack in seperatedtracks:
            output_tracks.append(seperatedtrack)
    cvpj_out = cvpjm.copy()
    cvpj_out['tracks'] = output_tracks
    cvpj_out['cvpjtype'] = 'single'

    if mi2s_fixedblock == True:
        all_instrument_placements_table = []
        for output_track in output_tracks:
            instrumentid = output_track['frominstrumentid']
            for trackplacement in output_track['placements']:
                datastore.add_to_seperated_object(all_instrument_placements_table, trackplacement, instrumentid)
        
        optimized_tracks = []
        #add instrument for each instrument
        for instrument_placement in all_instrument_placements_table:
            #print('\ninst:', instrument_placement[0])
            singleinst_placements_table = []
            for placement in instrument_placement[1]:
                position = placement['position']
                datastore.add_to_seperated_object(singleinst_placements_table,placement,position)
            singleinst_tracksplacements = []
            #print('\npos-num output:')
            for singleinst_placement in singleinst_placements_table:
                #print(singleinst_placement[0], len(singleinst_placement[1]))
                for number in range(len(singleinst_placement[1])):
                    datastore.add_to_seperated_object(singleinst_tracksplacements,singleinst_placement[1][number],number)
            #print('\npos-placement output:')
            for singleinst_tracksplacement in singleinst_tracksplacements:
                #print(singleinst_tracksplacement[0], len(singleinst_tracksplacement[1]))
                out_track = {}
                instdata = find_instrument_id(instrument_placement[0], cvpjm_instrument)
                if instdata != None:
                    if 'name' in instdata:
                        out_track['name'] = instdata['name']
                    else:
                        out_track['name'] = 'Inst #' + str(instdata['associd'])
                    out_track['instrumentdata'] = instdata['instrumentdata']
                    out_track['placements'] = singleinst_tracksplacement[1]
                    out_track['type'] = 'instrument'
                    out_track['vol'] = instdata['vol']
                    if 'color' in instdata:
                        out_track['color'] = instdata['color']
                    if 'fxrack_channel' in instdata:
                        out_track['fxrack_channel'] = instdata['fxrack_channel']
                    out_track['frominstrumentid'] = singleinst_tracksplacement[0]
                    optimized_tracks.append(out_track)
        cvpj_out['tracks'] = optimized_tracks
    return json.dumps(cvpj_out)

def convert_multipleindexed_multiple(cvpj_string_multiple_indexed):
    print('[func-projconv] multiindex2multi started')
    cvpjm_out = json.loads(cvpj_string_multiple_indexed).copy()

    cvpjmi_playlist = cvpjm_out['playlist'].copy()
    del cvpjm_out['playlist']

    cvpjmi_notelistindex = cvpjm_out['notelistindex'].copy()
    del cvpjm_out['notelistindex']

    notelistindex_table = []
    for cvpjmi_notelistindex_entry in cvpjmi_notelistindex:
        #print(cvpjmi_notelistindex_entry)
        notelistindex_id = cvpjmi_notelistindex_entry['associd']
        del cvpjmi_notelistindex_entry['associd']
        notelistindex_data = cvpjmi_notelistindex_entry
        print('[func-projconv] mi2m: NoteListIndex ID, ' + str(notelistindex_id))
        datastore.add_to_seperated_object(notelistindex_table, notelistindex_data, notelistindex_id)

    cvpjm_playlist_out = []

    for track in cvpjmi_playlist.copy():
        newplacements = []
        track_placements = track['placements']
        del track['placements']
        for track_placement in track_placements:
            track_fromindex = track_placement['fromindex']
            del track_placement['fromindex']
            notelistindex_table_found = [i for i,l in enumerate(notelistindex_table) if track_fromindex in l]
            if notelistindex_table_found != []:
                track_merge = notelistindex_table[notelistindex_table_found[0]][1][0]
                track_placement = track_placement | track_merge
                if 'notelist' not in track_placement:
                   track_placement['notelist'] = []
                newplacements.append(track_placement)
        track['placements'] = newplacements
        cvpjm_playlist_out.append(track)

    cvpjm_out['playlist'] = cvpjm_playlist_out
    cvpjm_out['cvpjtype'] = 'multiple'
    return json.dumps(cvpjm_out)

def convert_trackany_single(cvpj_json_string_trackany):
    print('[func-projconv] trackany2single started')
    cvpjta = json.loads(cvpj_json_string_trackany).copy()

    cvpjta_tracks = cvpjta['tracks']
    fxcount = 1

    cvpj_tracks = []
    outputfx = []

    for cvpjta_track in cvpjta_tracks:
        fxchannel = {}
        fxchannel['name'] = cvpjta_track['name']
        fxchannel['vol'] = cvpjta_track['vol']
        del cvpjta_track['vol']
        fxchannel['pan'] = cvpjta_track['pan']
        del cvpjta_track['pan']
        if cvpjta_track['type'] == 'master':
            fxchannel['num'] = 0
        else:
            cvpjta_track['fxrack_channel'] = fxcount
            #cvpj_tracks.append(cvpjta_track)
            fxchannel['num'] = fxcount
            fxcount += 1
            cvpj_tracks.append(cvpjta_track)
        print(cvpjta_track['type'])
        outputfx.append(fxchannel)
    cvpjta['fxrack'] = outputfx
    cvpjta['tracks'] = cvpj_tracks
    return json.dumps(cvpjta)