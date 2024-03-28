# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import base64
import plugin_input
import zlib
import json
from functions import data_bytes
from functions import data_values
from functions import colors
from objects import dv_dataset

def filternotes(instid, in_notedata, note):
    outnotes = []
    for tnote in in_notedata:
        duration = tnote[1]['duration'] if 'duration' in tnote[1] else 1
        outnotes.append([instid, tnote[0], duration, note, tnote[1]['velocity']])
    return outnotes

def get_instids(convproj_obj, instdata):
    global dataset
    global dataset_midi
    outdata = []
    for instnum in range(len(instdata)):
        si = instdata[instnum]
        instid = str(int(si['on']))+'_'+str(si['audioClipId'])+'_'+str(si['volume'])
        if instid not in convproj_obj.instruments:
            inst_obj, plug_obj = convproj_obj.add_instrument_from_dset(instid, instid, dataset, dataset_midi, si['preset'], si['preset'], None)
            inst_obj.params.add('vol', si['volume'], 'float')
            inst_obj.params.add('enabled', bool(si['on']), 'bool')
        outdata.append(instid)
    return outdata

def decodeblock(convproj_obj, input_block, position, track_data):
    pl_dur = 128
    repeatdur = 0

    columns = input_block['columns']
    instdata = input_block['instruments']
    drumsdata = input_block['drums']

    for repeatnum in range(8):
        if columns[repeatnum]['repeat'] == True:
            repeatdur += 16
            pl_dur = repeatdur
        else:
            break

    blockinsts = get_instids(convproj_obj, instdata)

    blockdrums = get_instids(convproj_obj, drumsdata)

    notesdata = input_block['notes']
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
        outnotes = []
        for notekey in range(16):
            outnotes += filternotes(blockinsts[instnum], t_notedata_inst[instnuminv][notekey], note_scale[notekey])
        if outnotes: 
            blockinstid = blockinsts[instnum]
            placement_obj = track_data[instnum].placements.add_notes()
            placement_obj.position = position
            placement_obj.duration = pl_dur
            placement_obj.visual.name = instdata[instnum]['preset']
            placement_obj.visual.color = colordata.getcolornum(instnum)
            for n in outnotes: placement_obj.notelist.add_m(n[0], n[1], n[2], n[3], n[4], {})

    for drumnum in range(5):
        drumnumminv = -drumnum+4
        outnotes = []
        outnotes += filternotes(blockdrums[drumnum], t_notedata_drums[drumnum], 0)
        if outnotes: 
            blockdrumid = blockdrums[drumnum]
            placement_obj = track_data[drumnumminv+4].placements.add_notes()
            placement_obj.position = position
            placement_obj.duration = pl_dur
            placement_obj.visual.name = drumsdata[drumnum]['preset']
            placement_obj.visual.color = colordata.getcolornum(drumnumminv+4)
            for n in outnotes: placement_obj.notelist.add_m(n[0], n[1], n[2], n[3], n[4], {})

    return pl_dur


class input_midi(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return '1bitdragon'
    def getname(self): return '1bitdragon'
    def gettype(self): return 'rm'
    def supported_autodetect(self): return False
    def getdawinfo(self, dawinfo_obj): 
        dawinfo_obj.name = '1BITDRAGON'
        dawinfo_obj.file_ext = '1bd'
    def detect(self, input_file):
        bytestream = open(input_file, 'rb')
        bytestream.seek(0)
        bytesdata = bytestream.read(4)
        if bytesdata == b'MThd': return True
        else: return False
    def parse(self, convproj_obj, input_file, dv_config):
        global dataset
        global dataset_midi
        global note_scale
        global colordata
        convproj_obj.set_timings(4, True)
        convproj_obj.type = 'rm'

        song_file = open(input_file, 'r')
        basebase64stream = base64.b64decode(song_file.read())
        bio_base64stream = data_bytes.to_bytesio(basebase64stream)
        bio_base64stream.seek(4)
        decompdata = json.loads(zlib.decompress(bio_base64stream.read(), 16+zlib.MAX_WBITS))

        dataset = dv_dataset.dataset('./data_dset/1bitdragon.dset')
        dataset_midi = dv_dataset.dataset('./data_dset/midi.dset')
        colordata = colors.colorset(dataset.colorset_e_list('track', 'main'))

        onebitd_scaleId = decompdata['scaleId']
        onebitd_scaletype = (onebitd_scaleId//12)
        onebitd_scalekey = onebitd_scaleId-(onebitd_scaletype*12)

        if onebitd_scaletype == 0: note_scale = [[0 ,2 ,4 ,7 ,9 ,12,14,16,19,21,24,26,28,31,33,36] ,-24]
        if onebitd_scaletype == 1: note_scale = [[0 ,3 ,5 ,7 ,10,12,15,17,19,22,24,27,29,31,34,36] ,-24]
        if onebitd_scaletype == 2: note_scale = [[0 ,2 ,4 ,5 ,7 ,9 ,11,12,14,16,17,19,21,23,24,26] ,-24]
        if onebitd_scaletype == 3: note_scale = [[0 ,2 ,3 ,4 ,7 ,8 ,10,12,14,15,16,19,20,22,24,26] ,-24]
        if onebitd_scaletype == 4: note_scale = [[0 ,2 ,3 ,5 ,7 ,9 ,10,12,14,15,17,19,21,22,24,26] ,-24]
        if onebitd_scaletype == 5: note_scale = [[0 ,1 ,4 ,5 ,6 ,9 ,10,12,13,16,17,18,21,22,24,25] ,-24]
        if onebitd_scaletype == 6: note_scale = [range(16),-12]
        note_scale = [x+note_scale[1]+onebitd_scalekey for x in note_scale[0]]

        track_data = []
        for plnum in range(9):
            track_obj = convproj_obj.add_track(str(plnum), 'instruments', 1, False)
            track_obj.visual.color = colordata.getcolornum(plnum)
            track_data.append(track_obj)

        curpos = 0
        for blocknum in range(len(decompdata['blocks'])):
            nextpos = decodeblock(convproj_obj, decompdata['blocks'][blocknum], curpos, track_data)
            curpos += nextpos

        onebitd_volume = decompdata['volume']
        convproj_obj.track_master.params.add('vol', onebitd_volume, 'float')

        onebitd_bpm = decompdata['bpm']
        convproj_obj.params.add('bpm', onebitd_bpm, 'float')

        onebitd_reverb = decompdata['reverb']
        plugin_obj = convproj_obj.add_plugin('master-reverb', 'simple', 'reverb')
        plugin_obj.role = 'effect'
        plugin_obj.visual.name = 'Reverb'
        plugin_obj.fxdata_add(onebitd_reverb, 0.5)
        convproj_obj.track_master.fxslots_audio.append('master-reverb')