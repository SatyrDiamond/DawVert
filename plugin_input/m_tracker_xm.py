# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_input
import os.path
import json
import struct
from functions import data_values
from functions import data_bytes
from io import BytesIO
from objects import dv_trackerpattern

try: import xmodits
except: xmodits_exists = False
else: xmodits_exists = True

startinststr = 'XM_Inst_'
maincolor = [0.16, 0.33, 0.53]

def parse_instrument(convproj_obj, file_stream, samplecount):
    global xm_cursamplenum

    basepos = file_stream.tell()
    xm_inst_header_length = int.from_bytes(file_stream.read(4), "little")
    print("[input-xm]     Header Length: " + str(xm_inst_header_length))

    xm_inst_name = data_bytes.readstring_fixedlen(file_stream, 22, "latin1")
    print("[input-xm]     Name: " + str(xm_inst_name))
    xm_inst_type = file_stream.read(1)[0]
    print("[input-xm]     Type: " + str(xm_inst_type))
    xm_inst_num_samples = file_stream.read(1)[0]
    print("[input-xm]     # of samples: " + str(xm_inst_num_samples))

    if xm_inst_num_samples != 0:
        xm_inst_e_head_size = int.from_bytes(file_stream.read(4), "little")
        print("[input-xm]     Sample header size: " + str(xm_inst_e_head_size))
        xm_inst_e_table = struct.unpack('B'*96, file_stream.read(96))
        xm_inst_e_env_v = struct.unpack('>'+'H'*24, file_stream.read(48))
        xm_inst_e_env_p = struct.unpack('>'+'H'*24, file_stream.read(48))
        file_stream.read(1)
        xm_inst_e_number_of_volume_points = file_stream.read(1)[0]
        xm_inst_e_number_of_panning_points = file_stream.read(1)[0]
        xm_inst_e_volume_sustain_point = file_stream.read(1)[0]
        xm_inst_e_volume_loop_start_point = file_stream.read(1)[0]
        xm_inst_e_volume_loop_end_point = file_stream.read(1)[0]
        xm_inst_e_panning_sustain_point = file_stream.read(1)[0]
        xm_inst_e_panning_loop_start_point = file_stream.read(1)[0]
        xm_inst_e_panning_loop_end_point = file_stream.read(1)[0]
        xm_inst_e_volume_type = file_stream.read(1)[0]
        xm_inst_e_panning_type = file_stream.read(1)[0]
        xm_inst_e_vibrato_type = file_stream.read(1)[0]
        xm_inst_e_vibrato_sweep = file_stream.read(1)[0]
        xm_inst_e_vibrato_depth = file_stream.read(1)[0]
        xm_inst_e_vibrato_rate = file_stream.read(1)[0]
        xm_inst_e_volume_fadeout = int.from_bytes(file_stream.read(2), "little")
        xm_inst_e_reserved = int.from_bytes(file_stream.read(2), "little")

    t_sampleheaders = []
    basepos_end = file_stream.tell()

    xm_pat_extra_data = file_stream.read(xm_inst_header_length - (basepos_end-basepos))

    for _ in range(xm_inst_num_samples):
        sampheader = struct.unpack('IIIBBBBBB', file_stream.read(18))
        sampname = data_bytes.readstring_fixedlen(file_stream, 22, "windows-1252")
        t_sampleheaders.append([sampheader, sampname])

    for t_sampleheader in t_sampleheaders:
        file_stream.read(t_sampleheader[0][0])

    cvpj_instid = startinststr + str(samplecount+1)

    inst_obj = convproj_obj.add_instrument(cvpj_instid)
    inst_obj.visual.name = xm_inst_name
    inst_obj.visual.color = maincolor
    inst_obj.params.add('vol', 0.3, 'float')

    inst_used = False
    if xm_inst_num_samples == 0:
        pass
    elif xm_inst_num_samples == 1:
        inst_used = True
        inst_obj.params.add('vol', 0.3*(t_sampleheaders[0][0][3]/64), 'float')

        filename = samplefolder+str(xm_cursamplenum)+'.wav'
        plugin_obj, inst_obj.pluginid, sampleref_obj = convproj_obj.add_plugin_sampler_genid(filename)
        plugin_obj.datavals.add('point_value_type', "samples")

        sampleflags = data_bytes.to_bin(t_sampleheaders[0][0][5], 8)

        loopon = None
        xm_loop_start = t_sampleheaders[0][0][1]
        xm_loop_len = t_sampleheaders[0][0][2]

        if sampleflags[7] == 1: loopon = 'normal'
        if sampleflags[6] == 1: loopon = 'pingpong'

        if loopon == None:
            plugin_obj.datavals.add('loop', {"enabled": 0})
        else:
            plugin_obj.datavals.add('loop', {"enabled": 1, "mode": loopon, "points": [xm_loop_start,xm_loop_start+xm_loop_len]})
    else:
        inst_used = True
        inst_obj.params.add('vol', 0.3, 'float')
        sampleregions = data_values.list_to_reigons(xm_inst_e_table, 48)

        plugin_obj, inst_obj.pluginid = convproj_obj.add_plugin_genid('sampler', 'multi')
        plugin_obj.datavals.add('point_value_type', "samples")

        for sampleregion in sampleregions:
            instrumentnum = sampleregion[0]

            filename = samplefolder + str(xm_cursamplenum+instrumentnum) + '.wav'
            sampleref_obj = convproj_obj.add_sampleref(filename, filename)

            regionparams = {}
            regionparams['sampleref'] = filename
            regionparams['loop'] = {}
            if t_sampleheaders[instrumentnum][0][1:3] == (0, 0): 
                regionparams['loop']['enabled'] = 0
            else:
                regionparams['loop']['enabled'] = 1
                xm_loop_start = t_sampleheaders[instrumentnum][0][1]
                xm_loop_len = t_sampleheaders[instrumentnum][0][2]
                regionparams['loop']['points'] = [xm_loop_start,xm_loop_start+xm_loop_len]

            plugin_obj.regions.add(sampleregion[1], sampleregion[2], regionparams)

    if xm_inst_num_samples != 0:

        splitted_points_v = data_values.list_chunks(xm_inst_e_env_v[0:xm_inst_e_number_of_volume_points*2], 2)
        splitted_points_p = data_values.list_chunks(xm_inst_e_env_p[0:xm_inst_e_number_of_panning_points*2], 2)

        pointsdata = [
        ['vol', splitted_points_v, xm_inst_e_volume_sustain_point, xm_inst_e_volume_loop_start_point, xm_inst_e_volume_loop_end_point], 
        ['pan', splitted_points_p, xm_inst_e_panning_sustain_point, xm_inst_e_panning_loop_start_point, xm_inst_e_panning_loop_end_point]
        ]

        vol_envflags = data_bytes.to_bin(xm_inst_e_volume_type, 8)

        for typedata in pointsdata:
            if typedata[0] == 'vol':
                autopoints_obj = plugin_obj.env_points_add('vol', 48, False, 'float')
                if vol_envflags[6] == 1: autopoints_obj.data['sustain'] = typedata[2]+1
                if vol_envflags[5] == 1: autopoints_obj.data['loop'] = [typedata[4], typedata[3]+typedata[4]]
                if xm_inst_e_volume_fadeout != 0: autopoints_obj.data['fadeout'] = (128/xm_inst_e_volume_fadeout)*5

            if typedata[0] == 'pan':
                autopoints_obj = plugin_obj.env_points_add('pan', 48, False, 'float')

            zerofound = False
            for groupval in typedata[1]:
                if groupval[0] == 0:
                    if zerofound == True: break
                    zerofound = True

                autopoint_obj = autopoints_obj.add_point()
                autopoint_obj.pos = groupval[0]
                if typedata[0] == 'vol' and vol_envflags[7] == 1: autopoint_obj.value = groupval[1]/64
                if typedata[0] == 'pan': autopoint_obj.value = (groupval[1]-32)/32

        plugin_obj.env_asdr_from_points('vol')

    if xm_inst_num_samples != 0: xm_cursamplenum += xm_inst_num_samples

class input_xm(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'xm'
    def getname(self): return 'FastTracker 2'
    def gettype(self): return 'm'
    def getdawcapabilities(self): 
        return {
        'samples_inside': True,
        'track_lanes': True
        }
    def supported_autodetect(self): return True
    def detect(self, input_file):
        bytestream = open(input_file, 'rb')
        bytesdata = bytestream.read(17)
        if bytesdata == b'Extended Module: ': return True
        else: return False
        bytestream.seek(0)

    def parse(self, convproj_obj, input_file, extra_param):
        global samplefolder
        global xm_cursamplenum

        xm_cursamplenum = 1

        samplefolder = extra_param['samplefolder']
        
        file_stream = open(input_file, 'rb')

        xm_header = file_stream.read(17)

        xm_name = data_bytes.readstring_fixedlen(file_stream, 20, "windows-1252")
        print("[input-xm] Song Name: " + xm_name)
        xm_1a = file_stream.read(1)
        xm_trkr_name = data_bytes.readstring_fixedlen(file_stream, 20, "windows-1252")
        print("[input-xm] Tracker Name: " + xm_trkr_name)
        xm_version = file_stream.read(2)
        print("[input-xm] Version: " + str(xm_version[1]), str(xm_version[0]))

        xm_headersize = int.from_bytes(file_stream.read(4), "little")
        xm_headersize_pos = file_stream.tell()

        xm_song_length = int.from_bytes(file_stream.read(2), "little")
        print("[input-xm] Song Length: " + str(xm_song_length))
        xm_song_restart_pos = int.from_bytes(file_stream.read(2), "little")
        print("[input-xm] Song Restart Position: " + str(xm_song_restart_pos))
        xm_song_num_channels = int.from_bytes(file_stream.read(2), "little")
        print("[input-xm] Number of channels: " + str(xm_song_num_channels))
        xm_song_num_patterns = int.from_bytes(file_stream.read(2), "little")
        print("[input-xm] Number of patterns: " + str(xm_song_num_patterns))
        xm_song_num_instruments = int.from_bytes(file_stream.read(2), "little")
        print("[input-xm] Number of instruments: " + str(xm_song_num_instruments))
        xm_song_flags = int.from_bytes(file_stream.read(2), "little")
        print("[input-xm] Flags: " + str(xm_song_flags))
        xm_song_speed = int.from_bytes(file_stream.read(2), "little")
        print("[input-xm] Speed: " + str(xm_song_speed))
        xm_song_bpm = int.from_bytes(file_stream.read(2), "little")
        print("[input-xm] BPM: " + str(xm_song_bpm))

        # ------------- Orders -------------
        xm_order = file_stream.read(xm_song_length)
        t_orderlist = []
        for xm_orderentry in xm_order: t_orderlist.append(xm_orderentry)
        print("[input-xm] Order List: " + str(t_orderlist))

        # ------------- Pattern -------------
        findpat = file_stream.tell()
        calc_pos = xm_headersize+xm_headersize_pos-4

        extra_data = file_stream.read(calc_pos-findpat)
        patterndata = dv_trackerpattern.patterndata(xm_song_num_channels, startinststr, maincolor)

        for patnum in range(xm_song_num_patterns):
            basepos = file_stream.tell()
            xm_pat_header_length = int.from_bytes(file_stream.read(4), "little")
            xm_pat_pak_type = file_stream.read(1)[0]
            xm_pat_num_rows = int.from_bytes(file_stream.read(2), "little")
            xm_pat_patterndata_size = int.from_bytes(file_stream.read(2), "little")
            basepos_end = file_stream.tell()
            xm_pat_extra_data = file_stream.read(xm_pat_header_length - (basepos_end-basepos))
            bio_patdata = BytesIO(file_stream.read(xm_pat_patterndata_size))

            patterndata.pattern_add(patnum, xm_pat_num_rows)
            for rownum in range(xm_pat_num_rows):
                if xm_pat_patterndata_size != 0: 
                    for channel in range(xm_song_num_channels):
                        cell_note = None
                        output_inst = None
                        cell_vol = 64
                        cell_effect = None
                        cell_param = 0

                        packed_first = int.from_bytes(bio_patdata.read(1), "little")
                        packed_flags = bin(packed_first)[2:].zfill(8)

                        packed_note = int(packed_flags[7], 2) 
                        packed_inst = int(packed_flags[6], 2)
                        packed_vol = int(packed_flags[5], 2)
                        packed_effect = int(packed_flags[4], 2)
                        packed_param = int(packed_flags[3], 2)
                        packed_msb = int(packed_flags[0], 2)
                        if packed_msb == 1:
                            if packed_note == 1: cell_note = int.from_bytes(bio_patdata.read(1), "little")
                            if packed_inst == 1: output_inst = int.from_bytes(bio_patdata.read(1), "little")
                            if packed_vol == 1: cell_vol = int.from_bytes(bio_patdata.read(1), "little")
                            if packed_effect == 1: cell_effect = int.from_bytes(bio_patdata.read(1), "little")
                            if packed_param == 1: cell_param = int.from_bytes(bio_patdata.read(1), "little")
                        else:
                            cell_note = packed_first
                            output_inst = int.from_bytes(bio_patdata.read(1), "little")
                            cell_vol = int.from_bytes(bio_patdata.read(1), "little")
                            cell_effect = int.from_bytes(bio_patdata.read(1), "little")
                            cell_param = int.from_bytes(bio_patdata.read(1), "little")

                        output_note = cell_note
                        if cell_note != None:
                            if cell_note == 97: output_note = 'off'
                            else: output_note = cell_note - 49

                        patterndata.cell_note(channel, output_note, output_inst)
                        patterndata.cell_param(channel, 'vol', cell_vol/64)

                        patterndata.cell_fx_mod(channel, cell_effect, cell_param)

                        if cell_effect == 12: 
                            patterndata.cell_param(channel, 'vol', cell_param/64)

                        if cell_effect == 15: 
                            patterndata.cell_g_param('speed', cell_param)

                        if cell_effect == 16: 
                            patterndata.cell_param(channel, 'global_volume', cell_param/64)

                        if cell_effect == 17: 
                            patterndata.cell_param(channel, 'global_volume_slide', dv_trackerpattern.getfineval(cell_param))

                        if cell_effect == 34:
                            panbrello_params = {}
                            panbrello_params['speed'], panbrello_params['depth'] = data_bytes.splitbyte(cell_param)
                            patterndata.cell_param(n_chan, 'panbrello', panbrello_params)



                patterndata.row_next()



        # ------------- Instruments -------------
        for instnum in range(xm_song_num_instruments):
            print("[input-xm] Instrument:")
            parse_instrument(convproj_obj, file_stream, instnum)

        # ------------- Samples -------------
        if xmodits_exists == True:
            try: xmodits.dump(input_file, samplefolder, index_only=True, index_raw=True, index_padding=0)
            except: pass

        patterndata.to_cvpj(convproj_obj, t_orderlist, startinststr, xm_song_bpm, xm_song_speed, maincolor)

        convproj_obj.metadata.name = xm_name
        
        convproj_obj.do_actions.append('do_addloop')
        convproj_obj.do_actions.append('do_lanefit')

        convproj_obj.params.add('bpm', xm_song_bpm, 'float')