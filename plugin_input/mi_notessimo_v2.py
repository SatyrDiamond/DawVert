# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import auto
from functions import data_bytes
from functions import idvals
from functions import note_data
from functions import placement_data
from functions import song
from functions import tracks
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
        notesout[n_layer].append(note_data.mx_makenote(str(n_inst), (n_pos)*notelen, (n_len/4)*notelen, out_note+out_offset, n_vol/1.5, n_pan))
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
        'r_track_lanes': True,
        'placement_cut': False,
        'placement_loop': False,
        'no_pl_auto': False,
        'no_placements': False
        }
    def supported_autodetect(self): return False
    def parse(self, input_file, extra_param):
        global used_instruments
        used_instruments = []

        bytestream = open(input_file, 'rb')
        nv2_data = data_bytes.to_bytesio(zlib.decompress(bytestream.read()))
        text_songname = data_bytes.readstring_lenbyte(nv2_data, 2, "big", None)
        text_songauthor = data_bytes.readstring_lenbyte(nv2_data, 2, "big", None)
        text_date1 = data_bytes.readstring_lenbyte(nv2_data, 2, "big", None)
        text_date2 = data_bytes.readstring_lenbyte(nv2_data, 2, "big", None)
        print("[input-notessimo_v2] Song Name: " + str(text_songname))
        print("[input-notessimo_v2] Song Author: " + str(text_songauthor))
        len_order = int.from_bytes(nv2_data.read(2), "big")
        arr_order = struct.unpack('b'*len_order, nv2_data.read(len_order))
        print("[input-notessimo_v2] Order List: " + str(arr_order))
        tempo_table = struct.unpack('>'+'H'*100, nv2_data.read(200))

        cvpj_l = {}
        idvals_inst_notetess = idvals.parse_idvalscsv('data_idvals/notessimo_v2_inst.csv')

        tracks.fxrack_add(cvpj_l, 1, 'Drums', None, 1, 0)

        notess_sheets = {}
        for sheetnum in range(100):
            tempo, notelen = song.get_lower_tempo(tempo_table[sheetnum], 1, 200)
            notess_sheets[sheetnum] = parsenotes(nv2_data, notelen)
            sheetdata = notess_sheets[sheetnum][2]
            if len(sheetdata) != 0: 
                print("[input-notessimo_v2] Sheet "+str(sheetnum)+", Layers:",end=' ')
                for layer in sheetdata:
                    print(layer,end=' ')
                    patid = str(sheetnum)+'_'+str(layer)
                    tracks.m_add_nle(cvpj_l, patid, sheetdata[layer])
                    tracks.m_add_nle_info(cvpj_l, patid, '#'+str(sheetnum+1)+' Layer '+str(layer+1), None)
                print()

        fxnum = 2
        for used_instrument in used_instruments:
            notetess_instname = idvals.get_idval(idvals_inst_notetess, str(used_instrument), 'name')
            notetess_instcolor = idvals.get_idval(idvals_inst_notetess, str(used_instrument), 'color')
            notetess_gminst = idvals.get_idval(idvals_inst_notetess, str(used_instrument), 'gm_inst')
            notetess_isdrum = idvals.get_idval(idvals_inst_notetess, str(used_instrument), 'isdrum')

            print("[input-notessimo_v2] Instrument: " + str(notetess_instname))

            cvpj_instdata = {}
            if notetess_gminst != None: cvpj_instdata = {'plugin': 'general-midi', 'plugindata': {'bank': 0, 'inst': notetess_gminst}}

            tracks.m_create_inst(cvpj_l, str(used_instrument), cvpj_instdata)
            tracks.m_basicdata_inst(cvpj_l, str(used_instrument), notetess_instname, notetess_instcolor, 1.0, 0.0)

            if notetess_isdrum == True:
                tracks.m_param_inst(cvpj_l, str(used_instrument), 'fxrack_channel', 1)
            else:
                tracks.m_param_inst(cvpj_l, str(used_instrument), 'fxrack_channel', fxnum)
                tracks.fxrack_add(cvpj_l, fxnum, notetess_instname, notetess_instcolor, None, None)
                fxnum += 1
                
        for idnum in range(9):
            tracks.m_playlist_pl(cvpj_l, idnum, 'Layer ' + str(idnum), None, [])

        curpos = 0
        for sheetnum in arr_order:
            cursheet_data = notess_sheets[sheetnum]
            for layer in cursheet_data[2]:
                patid = str(sheetnum)+'_'+str(layer)
                cvpj_l_placement = placement_data.makepl_n_mi(curpos, cursheet_data[0]*cursheet_data[1], patid)
                tracks.m_playlist_pl_add(cvpj_l, layer+1, cvpj_l_placement)
            song.add_timemarker_timesig(cvpj_l, None, curpos, 4, 4)
            autoplacement = auto.makepl(curpos, cursheet_data[0]*cursheet_data[1], [{"position": 0, "value": tempo_table[sheetnum]*cursheet_data[1]}])
            tracks.a_add_auto_pl(cvpj_l, ['main', 'bpm'], autoplacement)
            curpos += cursheet_data[0]*cursheet_data[1]
        
        song.add_info(cvpj_l, 'title', text_songname)
        song.add_info(cvpj_l, 'author', text_songauthor)

        cvpj_l['do_addloop'] = True
        cvpj_l['do_lanefit'] = True
        
        cvpj_l['bpm'] = tempo_table[0]*notess_sheets[arr_order[0]][1]
        return json.dumps(cvpj_l)
