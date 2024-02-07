# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from functions import note_data
from functions import xtramath
from objects import convproj
from objects import dv_dataset
import json
import plugin_input
import struct
import zlib

def parsenotes(bio_data, notelen): 
    patsize, numnotes = struct.unpack('>II', bio_data.read(8))
    notesout = {}
    for _ in range(numnotes):
        notedata = bio_data.read(20)
        n_pos,n_note,n_layer,n_inst,n_sharp,n_vol,n_pan,n_len = struct.unpack('>Ibbhbffh', notedata[:19])
        n_key = (n_note-41)*-1
        out_oct = int(n_key/7)
        out_key = n_key - out_oct*7
        out_offset = 0
        if n_layer not in notesout: notesout[n_layer] = []
        if n_inst not in used_instruments: used_instruments.append(n_inst)
        if n_sharp == 2: out_offset = 1
        if n_sharp == 1: out_offset = -1
        out_note = note_data.keynum_to_note(out_key, out_oct-3)
        notesout[n_layer].append([n_inst, (n_pos)*notelen, (n_len/4)*notelen, out_note+out_offset, n_vol/1.5, n_pan])
        #notesout[n_layer].add_m(str(n_inst), (n_pos)*notelen, (n_len/4)*notelen, out_note+out_offset, n_vol/1.5, {'pan': n_pan})
    return patsize-32, notelen, notesout

class input_notessimo_v2(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'notessimo_v2'
    def getname(self): return 'Notessimo V2'
    def gettype(self): return 'mi'
    def getdawcapabilities(self): 
        return {
        'fxrack': True,
        'track_lanes': True
        }
    def supported_autodetect(self): return False
    def parse(self, convproj_obj, input_file, extra_param):
        global used_instruments
        used_instruments = []

        # ---------- CVPJ Start ----------
        convproj_obj.type = 'mi'
        convproj_obj.set_timings(4, True)

        # ---------- File ----------
        bytestream = open(input_file, 'rb')
        nv2_data = data_bytes.to_bytesio(zlib.decompress(bytestream.read()))
        text_songname = data_bytes.readstring_lenbyte(nv2_data, 2, "big", None)
        print("[input-notessimo_v2] Song Name: " + str(text_songname))
        text_songauthor = data_bytes.readstring_lenbyte(nv2_data, 2, "big", None)
        print("[input-notessimo_v2] Song Author: " + str(text_songauthor))
        text_date1 = data_bytes.readstring_lenbyte(nv2_data, 2, "big", None)
        text_date2 = data_bytes.readstring_lenbyte(nv2_data, 2, "big", None)

        try:
            t_date, t_time = text_date1.split(', ')
            t_month, t_day, t_year = t_date.split('/')
            t_hours, t_min = t_time.split(':')
            convproj_obj.metadata.t_hours = int(t_hours)
            convproj_obj.metadata.t_minutes = int(t_min)
            convproj_obj.metadata.t_day = int(t_day)
            convproj_obj.metadata.t_month = int(t_month)
            convproj_obj.metadata.t_year = int(t_year)
        except: pass

        len_order = int.from_bytes(nv2_data.read(2), "big")
        arr_order = struct.unpack('b'*len_order, nv2_data.read(len_order))
        print("[input-notessimo_v2] Order List: " + str(arr_order))
        tempo_table = struct.unpack('>'+'H'*100, nv2_data.read(200))

        dataset = dv_dataset.dataset('./data_dset/notessimo_v2.dset')
        dataset_midi = dv_dataset.dataset('./data_dset/midi.dset')
        
        fxchan_data = convproj_obj.add_fxchan(1)
        fxchan_data.visual.name = 'Drums'

        notess_sheets = {}
        for sheetnum in range(100):
            tempo, notelen = xtramath.get_lower_tempo(tempo_table[sheetnum], 1, 200)
            notess_sheets[sheetnum] = parsenotes(nv2_data, notelen)
            sheetdata = notess_sheets[sheetnum][2]
            if len(sheetdata) != 0: 
                print("[input-notessimo_v2] Sheet "+str(sheetnum)+", Layers: "+', '.join([str(x) for x in sheetdata]))
                for layer in sheetdata:
                    nle_obj = convproj_obj.add_notelistindex(str(sheetnum)+'_'+str(layer))
                    for nn in sheetdata[layer]:
                        nle_obj.notelist.add_m(str(nn[0]), nn[1], nn[2], nn[3], nn[4], {'pan': nn[5]})
                    nle_obj.visual.name = '#'+str(sheetnum+1)+' Layer '+str(layer+1)

        fxnum = 2
        for used_instrument in used_instruments:
            cvpj_instid = str(used_instrument)

            inst_obj, plugin_obj = convproj_obj.add_instrument_from_dset(cvpj_instid, cvpj_instid, dataset, dataset_midi, cvpj_instid, None, None)

            print("[input-notessimo_v2] Instrument: " + str(inst_obj.visual.name))

            if inst_obj.midi.drum_mode: 
                inst_obj.fxrack_channel = 1
            else:
                inst_obj.fxrack_channel = fxnum
                fxchan_data = convproj_obj.add_fxchan(fxnum)
                fxchan_data.visual.name = inst_obj.visual.name
                fxchan_data.visual.color = inst_obj.visual.color
                fxnum += 1
                
        for idnum in range(9):
            playlist_obj = convproj_obj.add_playlist(idnum, 1, True)
            playlist_obj.visual.name = 'Layer '+str(idnum+1)


        curpos = 0
        for sheetnum in arr_order:
            cursheet_data = notess_sheets[sheetnum]
            for layer in cursheet_data[2]:
                placement_obj = convproj_obj.playlist[layer].placements.add_notes()
                placement_obj.position = curpos
                placement_obj.duration = cursheet_data[0]*cursheet_data[1]
                placement_obj.fromindex = str(sheetnum)+'_'+str(layer)
            convproj_obj.timesig_auto.add_point(curpos, [4,4])

            autopl_obj = convproj_obj.add_automation_pl('main/bpm', 'float')
            autopl_obj.position = curpos
            autopl_obj.duration = cursheet_data[0]*cursheet_data[1]
            autopoint_obj = autopl_obj.data.add_point()
            autopoint_obj.value = tempo_table[sheetnum]*cursheet_data[1]
            curpos += cursheet_data[0]*cursheet_data[1]
        
        convproj_obj.metadata.name = text_songname
        convproj_obj.metadata.author = text_songauthor

        convproj_obj.do_actions.append('do_addloop')
        convproj_obj.do_actions.append('do_lanefit')
        convproj_obj.params.add('bpm', tempo_table[0]*notess_sheets[arr_order[0]][1], 'float')