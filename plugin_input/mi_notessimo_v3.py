# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from functions import note_mod
from functions import colors
from functions import idvals
from functions import notelist_data
from functions import placement_data
from functions import note_data
from functions import auto
from functions import plugins
from functions import song
from functions_tracks import auto_data
from functions_tracks import tracks_mi
from functions_tracks import fxrack
from functions_tracks import fxslot
import plugin_input
import json
import zipfile
import math
import xml.etree.ElementTree as ET

idvals_inst_notetess = idvals.parse_idvalscsv('data_idvals/notessimo_v3_inst.csv')

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
            if 'color' in inst_vars: lists_data[1][inst]['color'] = colors.moregray(inst_vars['color'])
        elif inst in idvals_inst_notetess:
        	print("[input-notessimo_v3] Instrument: " + inst + " BUI")
        else:
            print("[input-notessimo_v3] Instrument: " + inst + " UNK")

# ----------------------------------- Sheets -----------------------------------

def parse_sheets(notess_sheets): 
    institems = {}
    items = notess_sheets.findall('items')[0]
    parse_items(items, 0)

    for sheet in lists_data[0]:
        sheet_name = lists_data[0][sheet]['name']
        print("[input-notessimo_v3] Sheet: " + lists_data[0][sheet]['name'])
        notelist = []

        notess_s_sheet = ET.fromstring(zip_data.read('sheets/'+sheet+'.xml'))
        layers = notess_s_sheet.findall('layers')[0]

        sheet_note_signature = [0,[[0,0,0,0,0,0,0],[0,0,0,0,0,0,0]]]

        sheet_color = None
        sheet_vars = get_vars(notess_s_sheet)
        if 'color' in sheet_vars: 
            sheet_color = colors.moregray(sheet_vars['color'])
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

                notelist.append( note_data.mx_makenote(notess_n_id, notess_n_pos*2, note_dur, notess_no_note, None, None) )
                if notess_n_id not in used_inst: used_inst.append(notess_n_id)

        print("[input-notessimo_v3]")

        tracks_mi.notelistindex_add(cvpj_l, sheet, notelist_data.sort(notelist))
        tracks_mi.notelistindex_visual(cvpj_l, sheet, name=sheet_name, color=sheet_color)

# ----------------------------------- Song -----------------------------------

def parse_song(songid):
    global bpm
    global song_length

    notess_x_song = ET.fromstring(zip_data.read('songs/'+songid+'.xml'))
    notess_l_songlayers = notess_x_song.findall('layers')[0]

    objects = notess_l_songlayers.findall('objects')[0]
    items = notess_l_songlayers.findall('items')[0]

    # ---------------- items ----------------
    for s_item in items:
        item_name = s_item.get('name')
        item_order = int(s_item.get('order'))+1
        tracks_mi.playlist_add(cvpj_l, item_order)
        tracks_mi.playlist_visual(cvpj_l, item_order, name=item_name)

    # ---------------- vars ----------------
    bpm = None
    song_vars = get_vars(notess_x_song)

    timesig_Numerator = 4
    timesig_Denominator = 4

    if 'author' in song_vars:
        song.add_info(cvpj_l, 'author', song_vars['author'])
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

    song.add_timesig(cvpj_l, timesig_Numerator, timesig_Denominator)
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
                cvpj_placement = placement_data.makepl_n_mi(cvpj_p_totalpos*8, tlslen/(120/tls[3])*8, tls[4])
                tracks_mi.add_pl(cvpj_l, tlsnum+1, 'notes', cvpj_placement)
                if tlsnum == 0:
                    autoplacement = auto.makepl(cvpj_p_totalpos*8, tlslen/(120/tls[3])*8, [{"position": 0, "value": tls[3]}])
                    auto_data.add_pl(cvpj_l, 'float', ['main', 'bpm'], autoplacement)
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
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'notessimo_v3'
    def getname(self): return 'Notessimo V3'
    def gettype(self): return 'mi'
    def getdawcapabilities(self): 
        return {
        'fxrack': True,
        'track_lanes': True
        }
    def supported_autodetect(self): return False
    def parse(self, input_file, extra_param):
        global zip_data
        global cvpj_l

        zip_data = zipfile.ZipFile(input_file, 'r')
        cvpj_l = {}

        fxrack.add(cvpj_l, 1, 1, 0, name='Drums')

        if 'instruments.xml' in zip_data.namelist():
            notess_instruments = ET.fromstring(zip_data.read('instruments.xml'))
            parse_instruments(notess_instruments)

        #if 'samples.xml' in zip_data.namelist():
        #    notess_samples = ET.fromstring(zip_data.read('instruments.xml'))
        #    parse_samples(notess_samples)

        notess_sheets = ET.fromstring(zip_data.read('sheets.xml'))
        parse_sheets(notess_sheets)

        notess_songs = ET.fromstring(zip_data.read('songs.xml'))
        parse_songs(notess_songs)

        fxnum = 2
        for inst in used_inst:
            isbuiltindrum = 0
            midiinst = None

            if inst in idvals_inst_notetess:
                isbuiltindrum = idvals.get_idval(idvals_inst_notetess, str(inst), 'isdrum')
                midiinst = idvals.get_idval(idvals_inst_notetess, str(inst), 'gm_inst')
                inst_name = idvals.get_idval(idvals_inst_notetess, str(inst), 'name')
                inst_color = idvals.get_idval(idvals_inst_notetess, str(inst), 'color')
            elif inst in lists_data[1]: 
                t_instdata = lists_data[1][inst]
                if 'name' in t_instdata: inst_name = t_instdata['name']
                if 'color' in t_instdata: inst_color = t_instdata['color']
            else:
                inst_name = 'noname ('+inst+')'
                inst_color = [0.3,0.3,0.3]

            inst_color = colors.moregray(inst_color)

            pluginid = plugins.get_id()

            if midiinst != None: 
                plugins.add_plug_gm_midi(cvpj_l, pluginid, 0, midiinst)
                cvpj_instdata = {'pluginid': pluginid}

            cvpj_instid = str(inst)

            tracks_mi.inst_create(cvpj_l, cvpj_instid)
            tracks_mi.inst_visual(cvpj_l, cvpj_instid, name=inst_name, color=inst_color)

            if midiinst != None: 
                plugins.add_plug_gm_midi(cvpj_l, pluginid, 0, midiinst)
                tracks_mi.inst_pluginid(cvpj_l, cvpj_instid, pluginid)
                tracks_mi.inst_dataval_add(cvpj_l, cvpj_instid, 'midi', 'output', {'program': midiinst})

            if isbuiltindrum == 1: 
                tracks_mi.inst_fxrackchan_add(cvpj_l, cvpj_instid, 1)
            else:
                tracks_mi.inst_fxrackchan_add(cvpj_l, cvpj_instid, 1)
                fxrack.add(cvpj_l, fxnum, 1, 0, name=inst_name, color=inst_color)
                fxnum += 1

        song.add_param(cvpj_l, 'bpm', 120)

        return json.dumps(cvpj_l)


