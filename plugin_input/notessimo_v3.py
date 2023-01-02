# SPDX-FileCopyrightText: 2022 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later
from functions import data_bytes
from functions import note_mod
from functions import colors
import plugin_input
import json
import zipfile
import math
import xml.etree.ElementTree as ET

keytable = [0,2,4,5,7,9,11,12]

t_noteoffset = {}
t_noteoffset["(#) A / F#"] = []
t_noteoffset["(#) B / G#"] = []
t_noteoffset["(#) C# / A#"] = []
t_noteoffset["(#) D / B"] = [] 
t_noteoffset["(#) E / C#"] = []
t_noteoffset["(#) F# / D#"] = []
t_noteoffset["(#) G / E"] = [] 
t_noteoffset["(b) Ab / F"] = []
t_noteoffset["(b) Bb / G"] = []
t_noteoffset["(b) Cb / Ab"] = []
t_noteoffset["(b) Db / Bb"] = []
t_noteoffset["(b) Eb / C"] = []
t_noteoffset["(b) F / D"] = [] 
t_noteoffset["(b) Gb / Eb"] = []
t_noteoffset["C / A"] = []

# ------------- Normal -------------
t_noteoffset["C / A"].append(        [[ 0, 0, 0, 0, 0, 0, 0],[ 0, 0, 0, 0, 0, 0, 0]])
t_noteoffset["C / A"].append(        [[ 1, 1, 0, 1, 1, 1, 0],[ 1, 1, 1, 1, 1, 1, 1]])
t_noteoffset["C / A"].append(        [[-1,-1,-1,-1,-1,-1,-1],[-1,-1,-1, 0,-1,-1,-1]])

t_noteoffset["(#) G / E"].append(    [[ 0, 0, 0, 0, 1, 0, 0],[ 0, 0, 0, 1, 0, 0, 0]])
t_noteoffset["(#) G / E"].append(    [[ 1, 1, 0, 1, 0, 1, 0],[ 1, 1, 1, 0, 1, 1, 1]])
t_noteoffset["(#) G / E"].append(    [[-1,-1,-1,-1, 0,-1,-1],[-1,-1,-1, 0,-1,-1,-1]])

t_noteoffset["(#) D / B"].append(    [[ 1, 0, 1, 0, 1, 0, 0],[ 1, 0, 0, 1, 0, 0, 1]])
t_noteoffset["(#) D / B"].append(    [[ 0, 1, 1, 1, 0, 1, 0],[ 0, 1, 1, 0, 1, 1, 0]])
t_noteoffset["(#) D / B"].append(    [[ 0,-1, 0,-1, 0,-1,-1],[ 0,-1,-1, 0,-1,-1, 0]])

t_noteoffset["(#) A / F#"].append(   [[ 1, 0, 0, 1, 1, 0, 0],[ 1, 0, 1, 1, 0, 0, 1]])
t_noteoffset["(#) A / F#"].append(   [[ 0, 1, 0, 0, 0, 1, 0],[ 0, 1, 0, 0, 1, 1, 0]])
t_noteoffset["(#) A / F#"].append(   [[ 0,-1,-1, 0, 0,-1,-1],[ 0,-1, 0, 0,-1,-1, 0]])

t_noteoffset["(#) E / C#"].append(   [[ 1, 0, 1, 1, 1, 0, 0],[ 1, 0, 1, 1, 0, 1, 1]])
t_noteoffset["(#) E / C#"].append(   [[ 0, 1, 1, 0, 0, 1, 0],[ 0, 1, 0, 0, 1, 0, 0]])
t_noteoffset["(#) E / C#"].append(   [[ 0,-1, 0, 0, 0,-1, 0],[ 0,-1, 0, 0,-1, 0, 0]])

t_noteoffset["(#) B / G#"].append(   [[ 1, 0, 0, 1, 1, 0, 0],[ 1, 1, 1, 1, 0, 1, 1]])
t_noteoffset["(#) B / G#"].append(   [[ 0, 1, 0, 0, 0, 1, 0],[ 0, 0, 0, 0, 1, 0, 0]])
t_noteoffset["(#) B / G#"].append(   [[ 0,-1, 0, 0, 0,-1, 0],[ 0, 0, 0, 0,-1, 0, 0]])

t_noteoffset["(#) F# / D#"].append(  [[ 1, 0, 0, 1, 1, 1, 0],[ 1, 1, 1, 1, 1, 1, 1]])
t_noteoffset["(#) F# / D#"].append(  [[ 0, 1, 0, 0, 0, 0, 0],[ 0, 0, 0, 0, 0, 0, 0]])
t_noteoffset["(#) F# / D#"].append(  [[ 0,-1, 0, 0, 0, 0, 0],[ 0, 0, 0, 0, 0, 0, 0]])

t_noteoffset["(#) C# / A#"].append(  [[ 1, 1, 0, 1, 1, 1, 0],[ 1, 1, 1, 1, 1, 1, 1]])
t_noteoffset["(#) C# / A#"].append(  [[ 0, 0, 0, 0, 0, 0, 0],[ 0, 0, 0, 0, 0, 0, 0]])
t_noteoffset["(#) C# / A#"].append(  [[ 0, 0, 0, 0, 0, 0, 0],[ 0, 0, 0, 0, 0, 0, 0]])

t_noteoffset["(b) F / D"].append(    [[ 0,-1, 0, 0, 0, 0, 0],[ 0, 0, 0, 0, 0, 0, 0]])
t_noteoffset["(b) F / D"].append(    [[ 1, 0, 0, 1, 1, 1, 0],[ 1, 1, 1, 1, 1, 1, 0]])
t_noteoffset["(b) F / D"].append(    [[-1, 0,-1,-1,-1,-1,-1],[-1,-1,-1, 0,-1,-1,-1]])

t_noteoffset["(b) Bb / G"].append(   [[ 0,-1, 0, 0, 0,-1, 0],[ 0, 0, 0, 0,-1, 0, 0]])
t_noteoffset["(b) Bb / G"].append(   [[ 1, 0, 0, 1, 1, 0, 0],[ 1, 1, 1, 1, 0, 1, 1]])
t_noteoffset["(b) Bb / G"].append(   [[-1, 0,-1,-1,-1, 0,-1],[-1,-1,-1,-1, 0,-1,-1]])

t_noteoffset["(b) Eb / C"].append(   [[ 0,-1,-1, 0, 0,-1, 0],[ 0,-1, 0, 0,-1, 0, 0]])
t_noteoffset["(b) Eb / C"].append(   [[ 1, 0, 0, 1, 1, 0, 0],[ 1, 0, 1, 1, 0, 1, 1]])
t_noteoffset["(b) Eb / C"].append(   [[-1, 0, 0,-1,-1, 0,-1],[-1, 0,-1, 0, 0,-1,-1]])

t_noteoffset["(b) Ab / F"].append(   [[ 0,-1,-1, 0, 0,-1,-1],[ 0,-1, 0, 0,-1,-1, 0]])
t_noteoffset["(b) Ab / F"].append(   [[ 1, 0, 0, 1, 1, 0, 0],[ 1, 0, 1, 1, 0, 0, 1]])
t_noteoffset["(b) Ab / F"].append(   [[-1, 0, 0,-1,-1, 0, 0],[-1, 0,-1, 0, 0, 0,-1]])

t_noteoffset["(b) Db / Bb"].append(  [[ 0,-1,-1,-1, 0,-1,-1],[ 0,-1,-1, 0,-1,-1, 0]])
t_noteoffset["(b) Db / Bb"].append(  [[ 1, 0, 0, 0, 1, 0, 0],[ 1, 0, 0, 1, 0, 0, 1]])
t_noteoffset["(b) Db / Bb"].append(  [[-1, 0, 0, 0,-1, 0, 0],[-1, 0, 0, 0, 0, 0,-1]])

t_noteoffset["(b) Gb / Eb"].append(  [[-1,-1,-1,-1, 0,-1,-1],[-1,-1,-1, 0,-1,-1,-1]])
t_noteoffset["(b) Gb / Eb"].append(  [[ 0, 0, 0, 0, 1, 0, 0],[ 0, 0, 0, 1, 0, 0, 0]])
t_noteoffset["(b) Gb / Eb"].append(  [[ 0, 0, 0, 0,-1, 0, 0],[ 0, 0, 0, 0, 0, 0, 0]])

t_noteoffset["(b) Cb / Ab"].append(  [[-1,-1,-1,-1,-1,-1,-1],[-1,-1,-1, 0,-1,-1,-1]])
t_noteoffset["(b) Cb / Ab"].append(  [[ 0, 0, 0, 0, 0, 0, 0],[ 0, 0, 0, 0, 0, 0, 0]])
t_noteoffset["(b) Cb / Ab"].append(  [[ 0, 0, 0, 0, 0, 0, 0],[ 0, 0, 0, 0, 0, 0, 0]])



global lists_data
global used_inst
global sheets_width
global sheets_tempo
global cvpj_auto_tempo

lists_data = [{},{},{}]
used_inst = []
sheets_width = {}
sheets_tempo = {}
cvpj_auto_tempo = []

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

# ----------------------------------- Instruments and Plugins -----------------------------------

def parse_instruments(notess_instruments): 
    institems = {}
    items = notess_instruments.findall('items')[0]
    parse_items(items, 1)

# ----------------------------------- Sheets -----------------------------------

def parse_sheets(notess_sheets): 
    institems = {}
    items = notess_sheets.findall('items')[0]
    parse_items(items, 0)

    for sheet in lists_data[0]:
        cvpj_l_notelistindex[sheet] = {}
        cvpj_l_notelistindex[sheet]['name'] = lists_data[0][sheet]['name']
        notelist = []

        notess_s_sheet = ET.fromstring(zip_data.read('sheets/'+sheet+'.xml'))
        layers = notess_s_sheet.findall('layers')[0]

        sheet_note_signature = [0,[[0,0,0,0,0,0,0],[0,0,0,0,0,0,0]]]

        sheet_vars = get_vars(notess_s_sheet)
        if 'color' in sheet_vars: cvpj_l_notelistindex[sheet]['color'] = colors.moregray(sheet_vars['color'])
        if 'signature' in sheet_vars:
            if sheet_vars['signature'] in t_noteoffset: sheet_note_signature = t_noteoffset[sheet_vars['signature']]
        if 'width' in sheet_vars: sheets_width[sheet] = sheet_vars['width']
        if 'tempo' in sheet_vars: sheets_tempo[sheet] = sheet_vars['tempo']

        objects = layers.findall('objects')[0]
        for s_object in objects:
            objs = s_object.findall('obj')
            for s_obj in objs:
                notess_n_pos = float(s_obj.get('x'))*2
                notess_n_note = int(s_obj.get('y'))
                notess_n_isSharp = s_obj.get('isSharp')
                notess_n_isFlat = s_obj.get('isFlat')
                notess_n_id = s_obj.get('id')

                notess_t_oct = int(roundseven(notess_n_note)/7)*-1
                notess_t_r_note = notess_n_note*-1 - notess_t_oct*7
                notess_t_note = keytable[notess_t_r_note]

                notess_o_note = notess_t_note + (notess_t_oct*12)

                notetype = 0
                if notess_n_isSharp == 'true': notetype = 1
                if notess_n_isFlat == 'true': notetype = 2

                if notess_t_oct >= 0: sharpkey = sheet_note_signature[notetype][1][notess_t_r_note]
                else: sharpkey = sheet_note_signature[notetype][0][notess_t_r_note]

                notess_o_note += sharpkey

                note = {}
                note['position'] = notess_n_pos*2
                note['duration'] = 1
                note['key'] = notess_o_note
                note['instrument'] = notess_n_id
                notelist.append(note)
                if notess_n_id not in used_inst: used_inst.append(notess_n_id)

        cvpj_l_notelistindex[sheet]['notelist'] = note_mod.sortnotes(notelist)

# ----------------------------------- Song -----------------------------------

def parse_song(songid):
    global bpm
    global song_length

    notess_s_song = ET.fromstring(zip_data.read('songs/'+songid+'.xml'))
    song_layers = notess_s_song.findall('layers')[0]

    objects = song_layers.findall('objects')[0]
    items = song_layers.findall('items')[0]

    # ---------------- items ----------------
    for s_item in items:
        item_name = s_item.get('name')
        item_order = int(s_item.get('order'))+1
        cvpj_l_playlist[item_order]['name'] = item_name

    # ---------------- vars ----------------
    bpm = None
    song_vars = get_vars(notess_s_song)

    if 'author' in song_vars: cvpj_l['author'] = song_vars['author']
    if 'width' in song_vars: song_length = song_vars['width']*60
    if 'video_time' in song_vars: cvpj_l['timesig_numerator'] = song_vars['video_time']
    if 'video_beat' in song_vars: cvpj_l['timesig_denominator'] = song_vars['video_beat']

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
                placement = {}
                placement['type'] = "instruments"
                placement['position'] = cvpj_p_totalpos*8
                placement['duration'] = tlslen/(120/tls[3])
                placement['fromindex'] = tls[4]
                cvpj_l_playlist[tlsnum+1]['placements'].append(placement)
                if tlsnum == 0:
                    autoplacement = {}
                    autoplacement['position'] = cvpj_p_totalpos*8
                    autoplacement['duration'] = tlslen/(120/tls[3])*8
                    autoplacement['points'] = [{"position": 0, "value": tls[3]}]
                    cvpj_auto_tempo.append(autoplacement)
                cvpj_p_totalpos += tlslen/(120/tls[3])
            else: 
                cvpj_p_totalpos += tlslen


def parse_songs(notess_songs):
    songlist = []
    items = notess_songs.findall('items')[0]
    for item in items:
        itemid = item.get('id')
        itemname = item.get('name')
        songlist.append([itemid, itemname])
    selected_song = songlist[0]
    parse_song(selected_song[0])

# ----------------------------------- Main -----------------------------------
 
class input_notessimo_v3(plugin_input.base):
    def __init__(self): pass
    def getshortname(self): return 'notessimo_v3'
    def getname(self): return 'Notessimo V3'
    def gettype(self): return 'mi'
    def supported_autodetect(self): return False
    def parse(self, input_file, extra_param):
        global zip_data
        zip_data = zipfile.ZipFile(input_file, 'r')

        global cvpj_l
        global cvpj_l_notelistindex
        global cvpj_l_playlist
        cvpj_l = {}
        cvpj_l_instruments = {}
        cvpj_l_instrumentsorder = []
        cvpj_l_notelistindex = {}
        cvpj_l_playlist = {}
        for plnum in range(20):
            cvpj_l_playlist[plnum] = {}
            cvpj_l_playlist[plnum]['placements'] = []

        if 'instruments.xml' in zip_data.namelist():
            notess_instruments = ET.fromstring(zip_data.read('instruments.xml'))
            parse_instruments(notess_instruments)

        notess_sheets = ET.fromstring(zip_data.read('sheets.xml'))
        parse_sheets(notess_sheets)

        notess_songs = ET.fromstring(zip_data.read('songs.xml'))
        parse_songs(notess_songs)

        for inst in used_inst:
            if inst in lists_data[1]: 
                if 'name' in lists_data[1][inst]: 
                    instname = lists_data[1][inst]['name']
                else: instname = 'noname ('+inst+')'
            else: instname = 'noname ('+inst+')'
            cvpj_inst = {}
            cvpj_inst["pan"] = 0.0
            cvpj_inst['name'] = instname
            cvpj_inst["vol"] = 1.0
            cvpj_inst['instdata'] = {}
            cvpj_inst['instdata']['plugin'] = 'none'

            cvpj_l_instruments[inst] = cvpj_inst
            cvpj_l_instrumentsorder.append(inst)


        placements_auto = {}
        placements_auto['bpm'] = cvpj_auto_tempo

        cvpj_l['placements_auto'] = placements_auto
        cvpj_l['notelistindex'] = cvpj_l_notelistindex
        cvpj_l['instruments'] = cvpj_l_instruments
        cvpj_l['instrumentsorder'] = cvpj_l_instrumentsorder
        cvpj_l['playlist'] = cvpj_l_playlist
        cvpj_l['bpm'] = 120

        return json.dumps(cvpj_l)


