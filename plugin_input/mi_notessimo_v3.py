# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from functions import note_data
from objects import dv_dataset
import plugin_input
import json
import zipfile
import math
import xml.etree.ElementTree as ET

global lists_data
global used_inst
global sheets_width
global sheets_tempo

lists_data = [{},{},{}]
used_inst = []
sheets_width = {}
sheets_tempo = {}

# ----------------------------------- Sharp and Flats -----------------------------------
notess_noteoffset = {}
notess_noteoffset["C / A"] = [[       [ 0, 0, 0, 0, 0, 0, 0],[ 0, 0, 0, 0, 0, 0, 0]],[[ 1, 1, 0, 1, 1, 1, 0],[ 1, 1, 1, 1, 1, 1, 1]],[[-1,-1,-1,-1,-1,-1,-1],[-1,-1,-1, 0,-1,-1,-1]]]
notess_noteoffset["(#) G / E"] = [[   [ 0, 0, 0, 0, 1, 0, 0],[ 0, 0, 0, 1, 0, 0, 0]],[[ 1, 1, 0, 1, 0, 1, 0],[ 1, 1, 1, 0, 1, 1, 1]],[[-1,-1,-1,-1, 0,-1,-1],[-1,-1,-1, 0,-1,-1,-1]]]
notess_noteoffset["(#) D / B"] = [[   [ 1, 0, 1, 0, 1, 0, 0],[ 1, 0, 0, 1, 0, 0, 1]],[[ 0, 1, 1, 1, 0, 1, 0],[ 0, 1, 1, 0, 1, 1, 0]],[[ 0,-1, 0,-1, 0,-1,-1],[ 0,-1,-1, 0,-1,-1, 0]]]
notess_noteoffset["(#) A / F#"] = [[  [ 1, 0, 0, 1, 1, 0, 0],[ 1, 0, 1, 1, 0, 0, 1]],[[ 0, 1, 0, 0, 0, 1, 0],[ 0, 1, 0, 0, 1, 1, 0]],[[ 0,-1,-1, 0, 0,-1,-1],[ 0,-1, 0, 0,-1,-1, 0]]]
notess_noteoffset["(#) E / C#"] = [[  [ 1, 0, 1, 1, 1, 0, 0],[ 1, 0, 1, 1, 0, 1, 1]],[[ 0, 1, 1, 0, 0, 1, 0],[ 0, 1, 0, 0, 1, 0, 0]],[[ 0,-1, 0, 0, 0,-1, 0],[ 0,-1, 0, 0,-1, 0, 0]]]
notess_noteoffset["(#) B / G#"] = [[  [ 1, 0, 0, 1, 1, 0, 0],[ 1, 1, 1, 1, 0, 1, 1]],[[ 0, 1, 0, 0, 0, 1, 0],[ 0, 0, 0, 0, 1, 0, 0]],[[ 0,-1, 0, 0, 0,-1, 0],[ 0, 0, 0, 0,-1, 0, 0]]]
notess_noteoffset["(#) F# / D#"] = [[ [ 1, 0, 0, 1, 1, 1, 0],[ 1, 1, 1, 1, 1, 1, 1]],[[ 0, 1, 0, 0, 0, 0, 0],[ 0, 0, 0, 0, 0, 0, 0]],[[ 0,-1, 0, 0, 0, 0, 0],[ 0, 0, 0, 0, 0, 0, 0]]]
notess_noteoffset["(#) C# / A#"] = [[ [ 1, 1, 0, 1, 1, 1, 0],[ 1, 1, 1, 1, 1, 1, 1]],[[ 0, 0, 0, 0, 0, 0, 0],[ 0, 0, 0, 0, 0, 0, 0]],[[ 0, 0, 0, 0, 0, 0, 0],[ 0, 0, 0, 0, 0, 0, 0]]]
notess_noteoffset["(b) F / D"] = [[   [ 0,-1, 0, 0, 0, 0, 0],[ 0, 0, 0, 0, 0, 0, 0]],[[ 1, 0, 0, 1, 1, 1, 0],[ 1, 1, 1, 1, 1, 1, 0]],[[-1, 0,-1,-1,-1,-1,-1],[-1,-1,-1, 0,-1,-1,-1]]]
notess_noteoffset["(b) Bb / G"] = [[  [ 0,-1, 0, 0, 0,-1, 0],[ 0, 0, 0, 0,-1, 0, 0]],[[ 1, 0, 0, 1, 1, 0, 0],[ 1, 1, 1, 1, 0, 1, 1]],[[-1, 0,-1,-1,-1, 0,-1],[-1,-1,-1,-1, 0,-1,-1]]]
notess_noteoffset["(b) Eb / C"] = [[  [ 0,-1,-1, 0, 0,-1, 0],[ 0,-1, 0, 0,-1, 0, 0]],[[ 1, 0, 0, 1, 1, 0, 0],[ 1, 0, 1, 1, 0, 1, 1]],[[-1, 0, 0,-1,-1, 0,-1],[-1, 0,-1, 0, 0,-1,-1]]]
notess_noteoffset["(b) Ab / F"] = [[  [ 0,-1,-1, 0, 0,-1,-1],[ 0,-1, 0, 0,-1,-1, 0]],[[ 1, 0, 0, 1, 1, 0, 0],[ 1, 0, 1, 1, 0, 0, 1]],[[-1, 0, 0,-1,-1, 0, 0],[-1, 0,-1, 0, 0, 0,-1]]]
notess_noteoffset["(b) Db / Bb"] = [[ [ 0,-1,-1,-1, 0,-1,-1],[ 0,-1,-1, 0,-1,-1, 0]],[[ 1, 0, 0, 0, 1, 0, 0],[ 1, 0, 0, 1, 0, 0, 1]],[[-1, 0, 0, 0,-1, 0, 0],[-1, 0, 0, 0, 0, 0,-1]]]
notess_noteoffset["(b) Gb / Eb"] = [[ [-1,-1,-1,-1, 0,-1,-1],[-1,-1,-1, 0,-1,-1,-1]],[[ 0, 0, 0, 0, 1, 0, 0],[ 0, 0, 0, 1, 0, 0, 0]],[[ 0, 0, 0, 0,-1, 0, 0],[ 0, 0, 0, 0, 0, 0, 0]]]
notess_noteoffset["(b) Cb / Ab"] = [[ [-1,-1,-1,-1,-1,-1,-1],[-1,-1,-1, 0,-1,-1,-1]],[[ 0, 0, 0, 0, 0, 0, 0],[ 0, 0, 0, 0, 0, 0, 0]],[[ 0, 0, 0, 0, 0, 0, 0],[ 0, 0, 0, 0, 0, 0, 0]]]

# ----------------------------------- functions -----------------------------------

def roundseven(x):
    return int(math.ceil(x / 7)) * 7

def timeline_addsplit(placements,forsplitdata):
    timestart = round(forsplitdata[0], 9)
    timeend = round(forsplitdata[0]+forsplitdata[1], 9)
    tempo = forsplitdata[2]
    sheetid = forsplitdata[3]

    new_placements = []
    for placement in placements:
        pltoa = timeline_addsplit_part(placement,timestart,timeend,tempo,sheetid)
        for pltoa_p in pltoa: new_placements.append(pltoa_p)

    new_placements_nozerolen = []
    for new_placement in new_placements:
        if new_placement[0] != new_placement[1]: new_placements_nozerolen.append(new_placement)
    return new_placements_nozerolen

def timeline_addsplit_part(placement,timestart,timeend,tempo,sheetid):
    split_placements = []
    if placement[0] <= timestart and timeend <= placement[1] and placement[2] == 0:
        split_placements.append([placement[0],timestart,0,placement[3], None])
        split_placements.append([timestart,timeend,1,tempo, sheetid])
        split_placements.append([timeend,placement[1],0,placement[3], None])
    else:
        split_placements.append(placement)
    return split_placements

def parse_items(xmldata, listnum):
    global lists_data
    itemdata = {}
    for item in xmldata:
        itemid = item.get('id')
        itemname = item.get('name')
        isBranch = item.get('isBranch')
        itemdata[itemid] = {}
        itemdata[itemid]['name'] = itemname
        if isBranch == 'true':
            itemdata[itemid]['group'] = True
            subitems = item.findall('item')
            itemdata[itemid]['data'] = parse_items(subitems, listnum)
        else: 
            lists_data[listnum][item.get('id')] = {}
            lists_data[listnum][item.get('id')]['name'] = item.get('name')

def get_vars(xmlvars):
    sheet_vars = xmlvars.findall('vars')[0]
    output = {}
    for s_vars in sheet_vars:
        s_name = s_vars.get('id')
        s_value = s_vars.get('value')
        s_type = s_vars.get('type')
        if s_type == 'int': output[s_name] = int(s_value)
        elif s_type == 'float': output[s_name] = float(s_value)
        elif s_type == 'color': 
            if s_value[:2] == '0x': color = int(s_value[2:], 16).to_bytes(4, "little")
            else: color = int(s_value).to_bytes(4, "little")
            output[s_name] = [color[2]/255,color[1]/255,color[0]/255]
        else: output[s_name] = s_value
    return output

# ----------------------------------- Samples -----------------------------------

def parse_samples(notess_instruments): 
    institems = {}
    items = notess_instruments.findall('items')[0]
    parse_items(items, 2)

# ----------------------------------- Instruments -----------------------------------

def parse_instruments(notess_instruments): 
    institems = {}
    items = notess_instruments.findall('items')[0]
    parse_items(items, 1)
    for inst in lists_data[1]:
        if 'instruments/'+inst+'.xml' in zip_data.namelist():
            print("[input-notessimo_v3] Instrument: " + inst + " XML ("+lists_data[1][inst]['name']+")")

            notess_s_inst = ET.fromstring(zip_data.read('instruments/'+inst+'.xml'))
            inst_vars = get_vars(notess_s_inst)
        else:
            print("[input-notessimo_v3] Instrument: " + inst)

# ----------------------------------- Sheets -----------------------------------

def parse_sheets(convproj_obj, notess_sheets): 
    institems = {}
    items = notess_sheets.findall('items')[0]
    parse_items(items, 0)

    for sheet in lists_data[0]:
        nle_obj = convproj_obj.add_notelistindex(sheet)
        nle_obj.visual.name = lists_data[0][sheet]['name']

        print("[input-notessimo_v3] Sheet: " + lists_data[0][sheet]['name'])

        notess_s_sheet = ET.fromstring(zip_data.read('sheets/'+sheet+'.xml'))
        layers = notess_s_sheet.findall('layers')[0]

        sheet_note_signature = [0,[[0,0,0,0,0,0,0],[0,0,0,0,0,0,0]]]

        sheet_vars = get_vars(notess_s_sheet)
        if 'color' in sheet_vars: 
            nle_obj.visual.color = sheet_vars['color']
        if 'signature' in sheet_vars:
            if sheet_vars['signature'] in notess_noteoffset: 
                sheet_note_signature = notess_noteoffset[sheet_vars['signature']]
                print("[input-notessimo_v3]    Signature: " + sheet_vars['signature'])
        if 'width' in sheet_vars: 
            sheets_width[sheet] = sheet_vars['width']
            print("[input-notessimo_v3]    Length: " + str(sheet_vars['width']))
        if 'tempo' in sheet_vars: 
            sheets_tempo[sheet] = sheet_vars['tempo']
            print("[input-notessimo_v3]    Tempo: " + str(sheet_vars['tempo']))

        objects = layers.findall('objects')[0]
        for s_object in objects:
            objs = s_object.findall('obj')
            for s_obj in objs:
                notess_n_pos = float(s_obj.get('x'))*2
                notess_n_note = int(s_obj.get('y'))
                notess_n_isSharp = s_obj.get('isSharp')
                notess_n_isFlat = s_obj.get('isFlat')
                notess_n_id = s_obj.get('id')
                notess_n_dur = s_obj.get('l')
                notess_nt_oct = int(roundseven(notess_n_note)/7)*-1
                notess_nt_rnote = notess_n_note*-1 - notess_nt_oct*7
                notess_no_note = note_data.keynum_to_note(notess_nt_rnote, notess_nt_oct)

                notetype = 0
                if notess_n_isSharp == 'true': notetype = 1
                if notess_n_isFlat == 'true': notetype = 2
                if notess_nt_oct >= 0: sharpkey = sheet_note_signature[notetype][1][notess_nt_rnote]
                else: sharpkey = sheet_note_signature[notetype][0][notess_nt_rnote]
                notess_no_note += sharpkey
                if notess_n_dur != None: note_dur = float(notess_n_dur)*4
                else: note_dur = 1

                nle_obj.notelist.add_m(notess_n_id, notess_n_pos*2, note_dur, notess_no_note, 1, {})
                if notess_n_id not in used_inst: used_inst.append(notess_n_id)

        print("[input-notessimo_v3]")

# ----------------------------------- Song -----------------------------------

def parse_song(convproj_obj, songid):
    global bpm
    global song_length

    notess_x_song = ET.fromstring(zip_data.read('songs/'+songid+'.xml'))
    notess_l_songlayers = notess_x_song.findall('layers')[0]

    objects = notess_l_songlayers.findall('objects')[0]
    items = notess_l_songlayers.findall('items')[0]

    # ---------------- items ----------------
    for s_item in items:
        item_order = int(s_item.get('order'))
        playlist_obj = convproj_obj.add_playlist(item_order, 1, True)
        playlist_obj.visual.name = s_item.get('name')

    # ---------------- vars ----------------
    bpm = None
    song_vars = get_vars(notess_x_song)

    timesig_Numerator = 4
    timesig_Denominator = 4

    if 'author' in song_vars:
        convproj_obj.metadata.author = song_vars['author']
        print("[input-notessimo_v3] Song Author: " + song_vars['author'])
    if 'width' in song_vars: 
        song_length = song_vars['width']*60
        print("[input-notessimo_v3] Song Length: " + str(song_vars['width']*60) + ' Seconds')
    if 'video_time' in song_vars: 
        timesig_Numerator = song_vars['video_time']
        print("[input-notessimo_v3] Song Numerator: " + str(song_vars['video_time']))
    if 'video_beat' in song_vars: 
        timesig_Denominator = song_vars['video_beat']
        print("[input-notessimo_v3] Song Denominator: " + str(song_vars['video_beat']))

    convproj_obj.timesig = [timesig_Numerator,timesig_Denominator]
    # ---------------- objects ----------------

    timeline_sheets_all = []
    for tlsnum in range(20):
        timeline_sheets_all.append([[0, song_length, 0, 120, None]])

    for s_object in objects:
        plnum = int(s_object.get('id'))
        objs = s_object.findall('obj')
        for s_obj in objs:
            notess_s_pos = float(s_obj.get('x'))*15
            notess_s_row = int(s_obj.get('y'))
            notess_s_len = float(s_obj.get('l2'))*15
            notess_s_id = s_obj.get('id')
            notess_s_tempo = sheets_tempo[notess_s_id]
            timeline_sheets_all[notess_s_row] = timeline_addsplit(timeline_sheets_all[notess_s_row],[notess_s_pos, notess_s_len, notess_s_tempo, notess_s_id])

    for tlsnum in range(20):
        timeline_sheets = timeline_sheets_all[tlsnum]
        cvpj_p_totalpos = 0
        for tls in timeline_sheets:
            tlslen = tls[1]-tls[0]
            if tls[2] == 1:
                placement_obj = convproj_obj.playlist[tlsnum].placements.add_notes_indexed()
                placement_obj.position = cvpj_p_totalpos*8
                placement_obj.duration = tlslen/(120/tls[3])*8
                placement_obj.fromindex = tls[4]
                if tlsnum == 0:
                    autopl_obj = convproj_obj.automation.add_pl_points(['main','bpm'], 'float')
                    autopl_obj.position = cvpj_p_totalpos*8
                    autopl_obj.duration = tlslen/(120/tls[3])*8
                    autopoint_obj = autopl_obj.data.add_point()
                    autopoint_obj.value = tls[3]/2
                cvpj_p_totalpos += tlslen/(120/tls[3])
            else: 
                cvpj_p_totalpos += tlslen


def parse_songs(convproj_obj, notess_songs):
    songlist = []
    items = notess_songs.findall('items')[0]
    for item in items:
        itemid = item.get('id')
        itemname = item.get('name')
        songlist.append([itemid, itemname])
    selected_song = songlist[0]
    parse_song(convproj_obj, selected_song[0])

# ----------------------------------- Main -----------------------------------
 
class input_notessimo_v3(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'notessimo_v3'
    def gettype(self): return 'mi'
    def getdawinfo(self, dawinfo_obj): 
        dawinfo_obj.name = 'Notessimo V3'
        dawinfo_obj.file_ext = 'note'
        dawinfo_obj.auto_types = ['pl_points']
        dawinfo_obj.fxrack = True
        dawinfo_obj.track_lanes = True
        dawinfo_obj.audio_filetypes = ['wav']
        dawinfo_obj.plugin_included = ['sampler:single', 'sampler:multi']
    def supported_autodetect(self): return False
    def parse(self, convproj_obj, input_file, dv_config):
        global zip_data

        # ---------- CVPJ Start ----------
        convproj_obj.type = 'mi'
        convproj_obj.set_timings(8, True)

        zip_data = zipfile.ZipFile(input_file, 'r')

        dataset = dv_dataset.dataset('./data_dset/notessimo_v3.dset')
        dataset_midi = dv_dataset.dataset('./data_dset/midi.dset')
        
        fxchan_data = convproj_obj.add_fxchan(1)
        fxchan_data.visual.name = 'Drums'

        if 'instruments.xml' in zip_data.namelist():
            notess_instruments = ET.fromstring(zip_data.read('instruments.xml'))
            parse_instruments(notess_instruments)

        #if 'samples.xml' in zip_data.namelist():
        #    notess_samples = ET.fromstring(zip_data.read('instruments.xml'))
        #    parse_samples(notess_samples)

        notess_sheets = ET.fromstring(zip_data.read('sheets.xml'))
        parse_sheets(convproj_obj, notess_sheets)

        notess_songs = ET.fromstring(zip_data.read('songs.xml'))
        parse_songs(convproj_obj, notess_songs)

        fxnum = 2
        for inst in used_inst:
            isbuiltindrum = 0
            midiinst = None

            cvpj_instid = str(inst)

            inst_obj, plugin_obj = convproj_obj.add_instrument_from_dset(cvpj_instid, cvpj_instid, dataset, dataset_midi, cvpj_instid, None, None)

            inst_found = False

            if (inst_obj.visual.name != None or inst_obj.visual.color != None):
                inst_found = True
                pass
            elif inst in lists_data[1]: 
                inst_found = True
                t_instdata = lists_data[1][inst]
                if 'name' in t_instdata: inst_obj.visual.name = t_instdata['name']
                if 'color' in t_instdata: inst_obj.visual.color = t_instdata['color']
            else: 
                inst_obj.visual.name = 'noname ('+inst+')'
                inst_obj.visual.color = [0.3,0.3,0.3]

            if inst_obj.midi.drum_mode: 
                inst_obj.fxrack_channel = 1
            else:
                inst_obj.fxrack_channel = fxnum
                fxchan_data = convproj_obj.add_fxchan(fxnum)
                fxchan_data.visual.name = inst_obj.visual.name
                fxchan_data.visual.color = inst_obj.visual.color
                fxnum += 1

        convproj_obj.params.add('bpm', 120, 'float')

