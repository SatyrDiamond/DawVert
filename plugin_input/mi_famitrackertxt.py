# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from functions import song_tracker
from functions import note_data
from functions import tracks
import plugin_input
import json

def hextoint(value):
    return int(value, 16)

def setmacro(cvpj_plugdata, macro_list, listname, macronum, famitrkr_instdata_macro_id):
    if famitrkr_instdata_macro_id in macro_list[macronum]:
        cvpj_plugdata[listname] = macro_list[macronum][famitrkr_instdata_macro_id]

def parsecell(celldata):
    cellsplit = celldata.split(' ')

    cellsplit_key = cellsplit[0]
    cellsplit_inst = cellsplit[1]
    cellsplit_vol = cellsplit[2]

    cellsplit_key_note = cellsplit_key[0]
    cellsplit_key_sharp = cellsplit_key[1]
    cellsplit_key_oct = cellsplit_key[2]

    out_cell = [{},[None, None, {}, {}]]

    if cellsplit_key in ['---', '===']: out_cell[1][0] = 'Off'
    elif cellsplit_key != '...':
        out_note = 0
        if cellsplit_key_oct != '#':
            out_note = note_data.keyletter_to_note(cellsplit_key_note, int(cellsplit_key_oct)-3)
            if cellsplit_key_sharp == '#': out_note += 1
            out_cell[1][0] = out_note

    if cellsplit_inst != '..': out_cell[1][1] = hextoint(cellsplit_inst)

    if cellsplit_vol != '.': out_cell[1][2]['vol'] = hextoint(cellsplit_vol)/15

    return(out_cell)

retroinst_names = ['Square1','Square2','Triangle','Noise','VRC6Square','VRC6Saw']

retroinst_names_vrc6 = ['VRC6Square','VRC6Saw']

class input_famitrkr_txt(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'famitrkr_txt'
    def getname(self): return 'famitrkr_txt'
    def gettype(self): return 'mi'
    def getdawcapabilities(self): 
        return {
        'fxrack': False,
        'track_lanes': True,
        'placement_cut': False,
        'placement_loop': False,
        'auto_nopl': False,
        'track_nopl': False
        }
    def supported_autodetect(self): return False
    def parse(self, input_file, extra_param):
        f_smp = open(input_file, 'r')
        lines_smp = f_smp.readlines()

        if 'songnum' in extra_param: selectedsong = int(extra_param['songnum'])
        else: selectedsong = 1

        songnum = 1

        mt_pat = {}
        mt_ord = {}
        mt_ch_insttype = ['Square1','Square2','Triangle','Noise','DPCM']
        mt_ch_names = ['Square1','Square2','Triangle','Noise','DPCM']

        cur_pattern = 1

        i_trackactive = False
        ft_info_main_title = ''
        ft_info_title = ''
        ft_info_author = ''
        ft_info_copyright = ''
        t_patterndata = {}

        song_tempo = 150
        song_speed = 3
        song_rows = 64

        macro_nes = [{},{},{},{},{}]
        macro_nes_vrc6 = [{},{},{},{},{}]

        famitrkr_instdata = {}
        famitrkr_instdata_vrc6 = {}

        inst_name = {}

        mt_ch_insttype = ['Square1','Square2','Triangle','Noise','DPCM']
        mt_ch_names = ['Square1','Square2','Triangle','Noise','DPCM']

        for line in lines_smp:
            ft_cmd_data = line.strip().split(' ', 1)

            #print(ft_cmd_data)
            if ft_cmd_data[0] == 'TITLE':
                ft_info_main_title = ft_cmd_data[1].split('"')[1::2][0]
                print('[input-famitracker_txt] Title: ' + ft_info_main_title)

            if ft_cmd_data[0] == 'MACRO':
                macrodata = ft_cmd_data[1].split(' : ')
                if len(macrodata) > 1:
                    macrotxt, macroseq = macrodata
                    macroseq = [int(i) for i in macroseq.split()]
                    macrovals = macrotxt.strip().split()
                    microtype, macroid, macroloop, macrorelease, macrounk = [int(i) for i in macrovals]
                    env_data = {'values': macroseq}
                    if macrorelease != -1: env_data['release'] = macrorelease
                    if macroloop != -1: env_data['loop'] = macroloop
                    macro_nes[microtype][macroid] = env_data

            if ft_cmd_data[0] == 'MACROVRC6':
                macrodata = ft_cmd_data[1].split(' : ')
                if len(macrodata) > 1:
                    macrotxt, macroseq = macrodata
                    macroseq = [int(i) for i in macroseq.split()]
                    macrovals = macrotxt.strip().split()
                    microtype, macroid, macroloop, macrorelease, macrounk = [int(i) for i in macrovals]
                    env_data = {'values': macroseq}
                    if macrorelease != -1: env_data['release'] = macrorelease
                    if macroloop != -1: env_data['loop'] = macroloop
                    macro_nes_vrc6[microtype][macroid] = env_data

            if ft_cmd_data[0] == 'AUTHOR':
                ft_info_author = ft_cmd_data[1].split('"')[1::2][0]
                print('[input-famitracker_txt] Author: ' + ft_info_author)

            if ft_cmd_data[0] == 'COPYRIGHT':
                ft_info_copyright = ft_cmd_data[1].split('"')[1::2][0]
                print('[input-famitracker_txt] Copyright: ' + ft_info_copyright)

            if ft_cmd_data[0] == 'EXPANSION':
                ft_info_expansion = int(ft_cmd_data[1].split()[0])
                print('[input-famitracker_txt] Expansion: ' + str(ft_info_expansion))

                #1=VRC6, 2=VRC7, 4=FDS, 8=MMC5, 16=N163, 32=S5B 

                if bool(ft_info_expansion & 0b1):
                    mt_ch_insttype.append('VRC6Square1')
                    mt_ch_names.append('VRC6Square1')
                    mt_ch_insttype.append('VRC6Square2')
                    mt_ch_names.append('VRC6Square2')
                    mt_ch_insttype.append('VRC6Saw')
                    mt_ch_names.append('VRC6Saw')
                if bool(ft_info_expansion & 0b10):
                    for _ in range(6):
                        mt_ch_insttype.append('VRC7FM')
                        mt_ch_names.append('VRC7FM')
                if bool(ft_info_expansion & 0b100):
                    mt_ch_insttype.append('FDS')
                    mt_ch_names.append('FDS')
                if bool(ft_info_expansion & 0b1000):
                    for _ in range(2):
                        mt_ch_insttype.append('MMC5Square')
                        mt_ch_names.append('MMC5Square')
                if bool(ft_info_expansion & 0b10000):
                    for _ in range(8):
                        mt_ch_insttype.append('N163')
                        mt_ch_names.append('N163')
                if bool(ft_info_expansion & 0b100000):
                    for _ in range(3):
                        mt_ch_insttype.append('S5B')
                        mt_ch_names.append('S5B')

                for chnum in range(len(mt_ch_insttype)):
                    mt_ord[chnum] = []
                    mt_pat[chnum] = {}

                print(mt_ch_names, len(mt_ch_names))

            if ft_cmd_data[0] == 'INST2A03':
                t_instdata = ft_cmd_data[1].split('"')[:2]
                t_instdata_nums = t_instdata[0].split()
                t_instdata_name = t_instdata[1]
                inst_id,inst_macro_vol,inst_macro_arp,inst_macro_pitch,inst_macro_hipitch,inst_macro_duty = [int(i) for i in t_instdata_nums]
                famitrkr_instdata[inst_id] = [t_instdata_name, inst_macro_vol, inst_macro_arp, inst_macro_pitch, inst_macro_hipitch, inst_macro_duty]
                print('[input-famitracker_txt] Inst 2A03 #' + str(inst_id) + ' (' + t_instdata_name + ')')

            if ft_cmd_data[0] == 'INSTVRC6':
                t_instdata = ft_cmd_data[1].split('"')[:2]
                t_instdata_nums = t_instdata[0].split()
                t_instdata_name = t_instdata[1]
                inst_id,inst_macro_vol,inst_macro_arp,inst_macro_pitch,inst_macro_hipitch,inst_macro_duty = [int(i) for i in t_instdata_nums]
                famitrkr_instdata_vrc6[inst_id] = [t_instdata_name, inst_macro_vol, inst_macro_arp, inst_macro_pitch, inst_macro_hipitch, inst_macro_duty]
                print('[input-famitracker_txt] Inst VRC6 #' + str(inst_id) + ' (' + t_instdata_name + ')')

            if ft_cmd_data[0] == 'TRACK':
                t_trackdata = ft_cmd_data[1].split('"')[:2]
                ft_info_title = t_trackdata[1]
                print('[input-famitracker_txt] Song #' + str(songnum) + ' (' + ft_info_title + ')')
                if selectedsong == songnum: 
                    i_trackactive = True
                    t_trackdata_nums = t_trackdata[0].split()
                    song_rows = int(t_trackdata_nums[0])
                    song_speed = int(t_trackdata_nums[1])
                    song_tempo = int(t_trackdata_nums[2])
                    print('[input-famitracker_txt]     Tempo: ' + str(song_tempo) + ' | Speed: ' + str(song_speed) + ' | Rows: ' + str(song_rows))
                else: i_trackactive = False
                songnum += 1

            if i_trackactive == True:

                if ft_cmd_data[0] == 'ORDER':
                    t_tracks_order_sep = ft_cmd_data[1].split(':')
                    t_tracks_ordernum = hextoint(t_tracks_order_sep[0])
                    t_tracks_orderdata = t_tracks_order_sep[1].split()
                    for i in range(0, len(t_tracks_orderdata)): t_tracks_orderdata[i] = hextoint(t_tracks_orderdata[i])

                    for chnum in range(len(t_tracks_orderdata)):
                        mt_ord[chnum].append(t_tracks_orderdata[chnum])

                if ft_cmd_data[0] == 'PATTERN':
                    cur_pattern = hextoint(ft_cmd_data[1])
                    print('[input-famitracker_txt]     Pattern #' + str(cur_pattern+1))
                    t_patterndata[cur_pattern] = {}

                if ft_cmd_data[0] == 'ROW':
                    row_tab = ft_cmd_data[1].split(' : ')
                    row_num = hextoint(row_tab[0])+1
                    row_data = row_tab[1:]
                    t_patterndata[cur_pattern][row_num] = row_data

        for patnum in t_patterndata:
            for chnum in range(len(mt_ch_insttype)):
                mt_pat[chnum][patnum] = []
                for _ in range(song_rows): mt_pat[chnum][patnum].append([{},[None, None, {}, {}]])

        for patnum in t_patterndata:
            s_patdata = t_patterndata[patnum]
            #print('-----', patnum)
            for rownum in range(song_rows): 
                if rownum+1 in s_patdata:
                    #print(rownum+1, s_patdata[rownum+1])
                    for chnum in range(len(s_patdata[rownum+1])):
                        mt_pat[chnum][patnum][rownum] = parsecell(s_patdata[rownum+1][chnum])

        cvpj_l = {}
        cvpj_l_instrument_data = {}
        cvpj_l_instrument_order = []

        len_table = song_tracker.multi_get_len_table(song_rows, mt_pat, mt_ord, mt_ch_insttype)

        song_tracker.multi_convert(cvpj_l, song_rows, mt_pat, mt_ord, mt_ch_insttype, len_table)

        total_used_instruments = song_tracker.get_multi_used_instruments()

        for total_used_instrument in total_used_instruments:
            insttype = total_used_instrument[0]
            instid = total_used_instrument[1]

            cvpj_instid = insttype+'_'+instid
            cvpj_inst = {}
            cvpj_instdata = {}

            if int(instid) in famitrkr_instdata:
                cvpj_instname = insttype+'-'+famitrkr_instdata[int(instid)][0]
                if insttype in retroinst_names:
                    cvpj_instdata = {"plugin": '2a03', "plugindata": {}}
                    cvpj_plugdata = cvpj_instdata["plugindata"]
                    if insttype == 'Square1' or insttype == 'Square2': cvpj_plugdata["wave"] = "square"
                    if insttype == 'Triangle': cvpj_plugdata["wave"] = "triangle"
                    if insttype == 'Noise': cvpj_plugdata["wave"] = "noise"
                    setmacro(cvpj_plugdata, macro_nes, "env_vol", 0, famitrkr_instdata[int(instid)][1]) 
                    setmacro(cvpj_plugdata, macro_nes, "env_arp", 1, famitrkr_instdata[int(instid)][2]) 
                    setmacro(cvpj_plugdata, macro_nes, "env_pitch", 2, famitrkr_instdata[int(instid)][3]*-1) 
                    setmacro(cvpj_plugdata, macro_nes, "env_hipitch", 3, famitrkr_instdata[int(instid)][4]*-1)
                    setmacro(cvpj_plugdata, macro_nes, "env_duty", 4, famitrkr_instdata[int(instid)][5]) 
                else:
                    cvpj_instdata = {"plugin": 'none', "plugindata": {}}

            elif int(instid) in famitrkr_instdata_vrc6:
                cvpj_instname = insttype+'-'+famitrkr_instdata_vrc6[int(instid)][0]
                if insttype in retroinst_names_vrc6:
                    cvpj_instdata = {"plugin": 'retro', "plugindata": {}}
                    cvpj_plugdata = cvpj_instdata["plugindata"]
                    if insttype == 'VRC6Square': cvpj_plugdata["wave"] = "square"
                    if insttype == 'VRC6Saw': cvpj_plugdata["wave"] = "square"
                    setmacro(cvpj_plugdata, macro_nes_vrc6, "env_vol", 0, famitrkr_instdata_vrc6[int(instid)][1]) 
                    setmacro(cvpj_plugdata, macro_nes_vrc6, "env_arp", 1, famitrkr_instdata_vrc6[int(instid)][2]) 
                    setmacro(cvpj_plugdata, macro_nes_vrc6, "env_pitch", 2, famitrkr_instdata_vrc6[int(instid)][3]*-1) 
                    setmacro(cvpj_plugdata, macro_nes_vrc6, "env_hipitch", 3, famitrkr_instdata_vrc6[int(instid)][4]*-1)
                    setmacro(cvpj_plugdata, macro_nes_vrc6, "env_duty", 4, famitrkr_instdata_vrc6[int(instid)][5])
                else:
                    cvpj_instdata = {"plugin": 'none', "plugindata": {}}

            else:
                cvpj_instname = insttype+'_'+instid
                cvpj_instdata = {"plugin": 'none', "plugindata": {}}

            tracks.m_create_inst(cvpj_l, cvpj_instid, cvpj_instdata)
            tracks.m_basicdata_inst(cvpj_l, cvpj_instid, cvpj_instname, None, 1.0, 0.0)

        cvpj_l['do_addloop'] = True
        cvpj_l['do_lanefit'] = True
        
        cvpj_l['use_instrack'] = False
        cvpj_l['use_fxrack'] = False

        cvpj_l['bpm'] = song_tempo
        return json.dumps(cvpj_l)
