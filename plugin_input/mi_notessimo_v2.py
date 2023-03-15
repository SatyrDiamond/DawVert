# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
import plugin_input
import json
import zlib
import struct
from functions import idvals

keytable = [0,2,4,5,7,9,11,12]

def getstring(bytesdata):
    stringlen = int.from_bytes(bytesdata.read(2), "big")
    if stringlen != 0: return bytesdata.read(stringlen).decode("utf-8")
    else: return ''

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

        note = {}
        note['position'] = (n_pos)*notelen
        note['duration'] = (n_len/4)*notelen
        note['key'] = keytable[out_key] + (out_oct-3)*12 + out_offset
        note['instrument'] = str(n_inst)
        notesout[n_layer].append(note)

    return patsize-32, notelen, notesout



class input_notessimo_v2(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'notessimo_v2'
    def getname(self): return 'Notessimo V2'
    def gettype(self): return 'mi'
    def supported_autodetect(self): return False
    def parse(self, input_file, extra_param):
        global used_instruments

        bytestream = open(input_file, 'rb')
        nv2_data = data_bytes.bytearray2BytesIO(zlib.decompress(bytestream.read()))
        text_songname = getstring(nv2_data)
        text_songauthor = getstring(nv2_data)
        text_date1 = getstring(nv2_data)
        text_date2 = getstring(nv2_data)
        print("[input-notessimo_v2] Song Name: " + str(text_songname))
        print("[input-notessimo_v2] Song Author: " + str(text_songauthor))

        len_order = int.from_bytes(nv2_data.read(2), "big")
        arr_order = struct.unpack('b'*len_order, nv2_data.read(len_order))
        print("[input-notessimo_v2] Order List: " + str(arr_order))

        idvals_inst_notetess = idvals.parse_idvalscsv('idvals/notessimo_v2_inst.csv')

        tempo_table = struct.unpack('>'+'H'*100, nv2_data.read(200))

        cvpj_l = {}
        cvpj_l_instruments = {}
        cvpj_l_instrumentsorder = []
        cvpj_l_notelistindex = {}
        cvpj_l_timemarkers = []
        cvpj_l_playlist = {}
        cvpj_l_fxrack = {}
        cvpj_auto_tempo = []
        used_instruments = []

        cvpj_l_timemarkers = []

        cvpj_l_fxrack["1"] = {}
        cvpj_l_fxrack["1"]["name"] = "Drums"

        notess_sheets = {}
        for sheetnum in range(100):
            tempo = tempo_table[sheetnum]
            notelen = 1

            if tempo > 200:
                tempo = tempo/2
                notelen = notelen/2

            notess_sheets[sheetnum] = parsenotes(nv2_data, notelen)

        for sheetnum in range(100):
            sheetdata = notess_sheets[sheetnum][2]
            if len(sheetdata) != 0: 
                print("[input-notessimo_v2] Sheet "+str(sheetnum)+", Layers:",end=' ')
                for layer in sheetdata:
                    print(layer,end=' ')
                    patid = str(sheetnum)+'_'+str(layer)
                    cvpj_l_notelistindex[patid] = {}
                    cvpj_l_notelistindex[patid]['notelist'] = sheetdata[layer]
                    cvpj_l_notelistindex[patid]['name'] = '#'+str(sheetnum+1)+' Layer '+str(layer+1)
                print()

        fxnum = 2
        for used_instrument in used_instruments:
            notetess_instname = idvals.get_idval(idvals_inst_notetess, str(used_instrument), 'name')
            notetess_instcolor = idvals.get_idval(idvals_inst_notetess, str(used_instrument), 'color')
            notetess_gminst = idvals.get_idval(idvals_inst_notetess, str(used_instrument), 'gm_inst')
            notetess_isdrum = idvals.get_idval(idvals_inst_notetess, str(used_instrument), 'isdrum')

            print("[input-notessimo_v2] Instrument: " + str(notetess_instname))

            cvpj_inst = {}
            cvpj_inst["pan"] = 0.0
            cvpj_inst['name'] = notetess_instname
            if notetess_instcolor != None: cvpj_inst['color'] = notetess_instcolor

            if notetess_isdrum == True:
                cvpj_inst['fxrack_channel'] = 1
            else:
                cvpj_inst['fxrack_channel'] = fxnum
                cvpj_l_fxrack[str(fxnum)] = {}
                cvpj_l_fxrack[str(fxnum)]["name"] = notetess_instname
                if notetess_instcolor != None: cvpj_l_fxrack[str(fxnum)]["color"] = notetess_instcolor
                fxnum += 1
                
            cvpj_inst["vol"] = 1.0
            cvpj_inst['instdata'] = {}
            if notetess_gminst == None:
                cvpj_inst['instdata']['plugin'] = 'none'
            else:
                cvpj_inst['instdata']['plugin'] = 'general-midi'
                cvpj_inst['instdata']['plugindata'] = {'bank':0, 'inst':notetess_gminst}

            cvpj_l_instruments[str(used_instrument)] = cvpj_inst
            cvpj_l_instrumentsorder.append(str(used_instrument))


        curpos = 0
        for sheetnum in arr_order:
            cursheet_data = notess_sheets[sheetnum]
            for layer in cursheet_data[2]:
                patid = str(sheetnum)+'_'+str(layer)
                cvpj_l_placement = {}
                cvpj_l_placement['type'] = "instruments"
                cvpj_l_placement['position'] = curpos
                cvpj_l_placement['duration'] = cursheet_data[0]*cursheet_data[1]
                cvpj_l_placement['fromindex'] = patid
                if str(layer+1) not in cvpj_l_playlist: 
                    cvpj_l_playlist[str(layer+1)] = {}
                    cvpj_l_playlist[str(layer+1)]['placements_notes'] = []
                cvpj_l_playlist[str(layer+1)]['placements_notes'].append(cvpj_l_placement)

            timemarker = {}
            timemarker['position'] = curpos
            timemarker['type'] = 'timesig'
            timemarker['numerator'] = 4
            timemarker['denominator'] = 4
            cvpj_l_timemarkers.append(timemarker)

            autoplacement = {}
            autoplacement['position'] = curpos
            autoplacement['duration'] = cursheet_data[0]*cursheet_data[1]
            autoplacement['points'] = [{"position": 0, "value": tempo_table[sheetnum]*cursheet_data[1]}]
            cvpj_auto_tempo.append(autoplacement)

            curpos += cursheet_data[0]*cursheet_data[1]
        
        automation = {}
        automation['main'] = {}
        automation['main']['bpm'] = cvpj_auto_tempo
        cvpj_l['automation'] = automation

        cvpj_l['info'] = {}
        cvpj_l['info']['title'] = text_songname
        cvpj_l['info']['author'] = text_songauthor

        cvpj_l['do_addwrap'] = True
        cvpj_l['do_lanefit'] = True
        
        cvpj_l['use_instrack'] = False
        cvpj_l['use_fxrack'] = True
        
        cvpj_l['fxrack'] = cvpj_l_fxrack
        cvpj_l['timemarkers'] = cvpj_l_timemarkers
        cvpj_l['notelistindex'] = cvpj_l_notelistindex
        cvpj_l['instruments_data'] = cvpj_l_instruments
        cvpj_l['instruments_order'] = cvpj_l_instrumentsorder
        cvpj_l['playlist'] = cvpj_l_playlist
        cvpj_l['bpm'] = tempo_table[0]*notess_sheets[arr_order[0]][1]
        return json.dumps(cvpj_l)
