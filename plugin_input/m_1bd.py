# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from functions import data_values
from functions import note_data
from functions import placement_data
from functions import plugins
from functions import song
from functions_tracks import tracks_m
from functions_tracks import tracks_master
import plugin_input
import base64
import json
import zlib

onebd_colors = [
[0.14, 1.00, 0.60],
[1.00, 0.87, 0.18],
[0.76, 0.41, 1.00],
[0.97, 0.51, 0.00],

[0.76, 0.76, 0.76],
[0.76, 0.58, 0.38],
[0.47, 0.49, 0.88],
[0.59, 0.73, 0.23],
[0.88, 0.35, 0.53]
]

def tnotedata_to_cvpj_nl(cvpj_notelist, instid, in_notedata, note):
    for tnote in in_notedata:
        duration = 1
        if 'duration' in tnote[1]: duration = tnote[1]['duration']
        cvpj_notelist.append(
            note_data.mx_makenote(instid, tnote[0], duration, note, tnote[1]['velocity'], 0)
            )

    return cvpj_notelist

def get_instids(instdata):
    outdata = []
    for instnum in range(len(instdata)):
        si = instdata[instnum]
        instid = str(int(si['on']))+'_'+str(si['audioClipId'])+'_'+str(si['volume'])
        used_instrument_data[instid] = si
        outdata.append(instid)
    return outdata

def decodeblock(cvpj_l, input_block, position):
    pl_dur = 128
    repeatdur = 0

    columns = input_block['columns']
    notesdata = input_block['notes']
    instdata = input_block['instruments']
    drumsdata = input_block['drums']

    for repeatnum in range(8):
        if columns[repeatnum]['repeat'] == True:
            repeatdur += 16
            pl_dur = repeatdur
        else:
            break

    blockinsts = get_instids(instdata)

    blockdrums = get_instids(drumsdata)

    t_notedata_drums = [[] for x in range(5)]
    t_notedata_inst = [[[] for x in range(16)] for x in range(4)]

    datafirst = data_values.list_chunks(notesdata, 9*128)

    for firstnum in range(len(datafirst)):
        datasecond = datafirst[firstnum]
        datathird = data_values.list_chunks(datasecond, 9)
        for thirdnum in range(128):
            stepnum = ((thirdnum&0b0000111)<<4)+((thirdnum&0b1111000)>>3)
            forthdata = datathird[thirdnum]
            for notevirt in range(9):
                notevirt_t = -notevirt+8 + firstnum*9
                if forthdata[notevirt]['velocity'] != 0.0:
                    tnotedata = [stepnum, forthdata[notevirt]]
                    if notevirt_t < 5: t_notedata_drums[notevirt_t].append(tnotedata)
                    else:
                        instnumber = notevirt_t-5
                        notenumber = instnumber//9
                        instnumber -= (instnumber//9)*9
                        t_notedata_inst[instnumber][notenumber].append(tnotedata)

    for instnum in range(4):
        instnuminv = -instnum+3
        notelist = []
        for notekey in range(16):
            notelist = tnotedata_to_cvpj_nl(notelist, blockinsts[instnum], t_notedata_inst[instnuminv][notekey], cvpj_scale[notekey])
        if notelist != []: 
            blockinstid = blockinsts[instnum]
            if blockinstid not in used_instruments[instnum]:  used_instruments[instnum].append(blockinstid)
            placementdata = placement_data.makepl_n(position, pl_dur, notelist)
            placementdata['name'] = instdata[instnum]['preset']
            placementdata['color'] = onebd_colors[instnum]

            longpldata = placement_data.longpl_split(placementdata)
            for longpls in longpldata:
                tracks_m.add_pl(cvpj_l, instnum+1, 'notes', longpls)

    for drumnum in range(5):
        drumnumminv = -drumnum+4
        notelist = tnotedata_to_cvpj_nl([], blockdrums[drumnum], t_notedata_drums[drumnum], 0)
        if notelist != []: 
            blockdrumid = blockdrums[drumnum]
            if blockdrumid not in used_instruments[drumnumminv+4]: used_instruments[drumnumminv+4].append(blockdrumid)
            placementdata = placement_data.makepl_n(position, pl_dur, notelist)
            placementdata['name'] = drumsdata[drumnum]['preset']
            placementdata['color'] = onebd_colors[drumnumminv+4]
            longpldata = placement_data.longpl_split(placementdata)
            for longpls in longpldata:
                tracks_m.add_pl(cvpj_l, drumnumminv+5, 'notes', longpls)

    return pl_dur


class input_1bitdragon(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return '1bitdragon'
    def getname(self): return '1bitdragon'
    def gettype(self): return 'm'
    def supported_autodetect(self): return False
    def getdawcapabilities(self): 
        return {
        'track_lanes': True
        }
    def parse(self, input_file, extra_param):
        global used_instruments
        global used_instrument_data
        global cvpj_scale

        song_file = open(input_file, 'r')
        basebase64stream = base64.b64decode(song_file.read())
        bio_base64stream = data_bytes.to_bytesio(basebase64stream)
        bio_base64stream.seek(4)
        decompdata = json.loads(zlib.decompress(bio_base64stream.read(), 16+zlib.MAX_WBITS))

        cvpj_l = {}
        used_instruments = [[] for x in range(9)]
        used_instrument_data = {}

        onebitd_bpm = decompdata['bpm']
        onebitd_reverb = decompdata['reverb']
        onebitd_scaleId = decompdata['scaleId']
        onebitd_volume = decompdata['volume']

        onebitd_scaletype = (onebitd_scaleId//12)
        onebitd_scalekey = onebitd_scaleId-(onebitd_scaletype*12)

        if onebitd_scaletype == 0: cvpj_scale = [[0 ,2 ,4 ,7 ,9 ,12,14,16,19,21,24,26,28,31,33,36] ,-24]
        if onebitd_scaletype == 1: cvpj_scale = [[0 ,3 ,5 ,7 ,10,12,15,17,19,22,24,27,29,31,34,36] ,-24]
        if onebitd_scaletype == 2: cvpj_scale = [[0 ,2 ,4 ,5 ,7 ,9 ,11,12,14,16,17,19,21,23,24,26] ,-24]
        if onebitd_scaletype == 3: cvpj_scale = [[0 ,2 ,3 ,4 ,7 ,8 ,10,12,14,15,16,19,20,22,24,26] ,-24]
        if onebitd_scaletype == 4: cvpj_scale = [[0 ,2 ,3 ,5 ,7 ,9 ,10,12,14,15,17,19,21,22,24,26] ,-24]
        if onebitd_scaletype == 5: cvpj_scale = [[0 ,1 ,4 ,5 ,6 ,9 ,10,12,13,16,17,18,21,22,24,25] ,-24]
        if onebitd_scaletype == 6: cvpj_scale = [range(16),-12]

        cvpj_scale = [x+cvpj_scale[1]+onebitd_scalekey for x in cvpj_scale[0]]

        for plnum in range(9):
            tracks_m.playlist_add(cvpj_l, plnum+1)
            tracks_m.playlist_visual(cvpj_l, plnum+1, color=onebd_colors[plnum])

        curpos = 0
        for blocknum in range(len(decompdata['blocks'])):
            nextpos = decodeblock(cvpj_l, decompdata['blocks'][blocknum], curpos)
            curpos += nextpos

        for instnum in range(9):
            part_used_instruments = used_instruments[instnum]
            for part_used_instrument in part_used_instruments:
                usedinstdata = used_instrument_data[part_used_instrument]
                instname = usedinstdata['preset']
                tracks_m.inst_create(cvpj_l, part_used_instrument)
                tracks_m.inst_visual(cvpj_l, part_used_instrument, name=instname, color=onebd_colors[instnum])

                tracks_m.inst_param_add(cvpj_l, part_used_instrument, 'vol', usedinstdata['volume'], 'float')
                tracks_m.inst_param_add(cvpj_l, part_used_instrument, 'enabled', usedinstdata['on'], 'bool')

        cvpj_l['timesig'] = [4, 4]
        song.add_param(cvpj_l, 'bpm', onebitd_bpm)

        tracks_master.create(cvpj_l, onebitd_volume)
        tracks_master.visual(cvpj_l, name='Master')

        return json.dumps(cvpj_l)
