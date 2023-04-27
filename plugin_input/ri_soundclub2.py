# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from functions import tracks
from functions import note_data
from functions import audio_wav
from functions import folder_samples
from functions import note_mod
from functions import notelist_data
from functions import placement_data
from functions import idvals
from functions import song
from functions import auto
import plugin_input
import struct
import json
import os

def sc2_read(sc2bytebuffer, offset):
    return data_bytes.customchunk_read(sc2bytebuffer, offset, 3, 4, "little", False)

class input_soundclub2(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'soundclub2'
    def getname(self): return 'Sound Club 2'
    def gettype(self): return 'ri'
    def getdawcapabilities(self): 
        return {
        'r_track_lanes': True,
        'no_pl_auto': True
        }
    def supported_autodetect(self): return True
    def detect(self, input_file):
        bytestream = open(input_file, 'rb')
        bytestream.seek(0)
        bytesdata = bytestream.read(3)
        if bytesdata == b'SN2': return True
        else: return False
    def parse(self, input_file, extra_param):
        bytestream = open(input_file, 'rb')
        bytestream.seek(7)
        sc2_headerdata = struct.unpack("iiiiii", bytestream.read(24))
        sc2_globaltempo = (1/((sc2_headerdata[3]/40)/2+0.5))*120

        print('[input-soundclub2] Tempo', sc2_globaltempo)

        file_name = os.path.splitext(os.path.basename(input_file))[0]
        samplefolder = folder_samples.samplefolder(extra_param, file_name)
        idvals_inst_soundclub2 = idvals.parse_idvalscsv('data_idvals/soundclub2_inst.csv')

        cvpj_l = {}

        cur_patnum = 0
        cur_instnum = 1

        pat_cvpj_notelist = {}
        pat_tempopoints = {}

        t_patnames = {}
        t_laneddata = {}

        sc2objects = sc2_read(bytestream, 31)
        for sc2object in sc2objects:
            sc2_datatype = sc2object[0]

            if sc2_datatype == b'NAM':  sc2_songdisc = sc2object[1].decode('ascii')

            elif sc2_datatype == b'PAT': 
                sc2_patdata = sc2object[1]
                t_patid = 'sc2_'+str(cur_patnum)
                print('[input-soundclub2] Pattern')
                sc2_patobjs = sc2_read(sc2_patdata, 4)
                pat_cvpj_notelist[cur_patnum] = [0, {}]
                pat_duration = 0
                for sc2_patobj in sc2_patobjs:
                    if sc2_patobj[0] == b'pna': 
                        print('[input-soundclub2]      Name: '+sc2_patobj[1].decode('ascii'))
                        t_patnames[cur_patnum] = sc2_patobj[1].decode('ascii')
                    elif sc2_patobj[0] == b'tem':
                        print('[input-soundclub2]      Tempo Points: '+str(len(sc2_patobj[1])//8))
                        pat_tempopoints[cur_patnum] = []
                        for datapos in range(len(sc2_patobj[1])//8):
                            muldatapos = datapos*8
                            tp_chunk = struct.unpack("IBBBB", sc2_patobj[1][muldatapos:muldatapos+8])
                            tp_pos = tp_chunk[0]
                            tp_sc2temp = tp_chunk[1]
                            tp_sc2temp_out = ((((tp_sc2temp-30)*-6)+60)/120)*sc2_globaltempo
                            pat_tempopoints[cur_patnum].append({"type": 'instant', "position": tp_pos, "value": tp_sc2temp_out})
                    elif sc2_patobj[0] == b'voi': 
                        cvpj_notelist = []
                        t_instid = int.from_bytes(sc2_patobj[1][:4], "little")+1
                        print('[input-soundclub2]      Events for Inst '+str(t_instid)+': '+str(len(sc2_patobj[1][5:])//3))
                        sc2_notedata = sc2_patobj[1][4:]
                        bio_sc2_notedata = data_bytes.to_bytesio(sc2_patobj[1][4:])
                        t_active_notes = [None for x in range(84)]
                        curpos = 0
                        n_curvol = 31
                        n_curpan = 15
                        while bio_sc2_notedata.tell() < len(sc2_notedata) :
                            n_len = bio_sc2_notedata.read(1)[0]
                            if n_len == 255:
                                n_len = int.from_bytes(bio_sc2_notedata.read(4), 'little')
                                bio_sc2_notedata.read(4)

                            n_type, n_note = struct.unpack("BB", bio_sc2_notedata.read(2)) 
                            curpos += n_len

                            if n_type == 0: t_active_notes[n_note] = [n_note,curpos,n_curvol,n_curpan,[]]
                            if n_type == 17: t_active_notes[n_note] = [n_note,curpos,n_curvol,n_curpan,[]]
                            if n_type == 19: #off
                                if t_active_notes[n_note] != None:
                                    t_notedata = t_active_notes[n_note]
                                    cvpj_notedata = note_data.rx_makenote(t_notedata[1], curpos-t_notedata[1], t_notedata[0]-36, n_curvol/31, (n_curpan-15)/-15)
                                    note_mod.pitchmod2point_init()
                                    for autopoint in t_notedata[4]: note_mod.pitchmod2point(cvpj_notedata, autopoint[0], 2, curpos-t_notedata[1], autopoint[1], autopoint[2])
                                    cvpj_notelist.append(cvpj_notedata)
                            if n_type == 20: n_curvol = n_note
                            if n_type == 21: n_curpan = n_note
                            if n_type == 54: #porta
                                n_p_k, n_p_l = bio_sc2_notedata.read(2)
                                t_active_notes[n_p_k] = t_active_notes[n_note]
                                t_active_notes[n_p_k][4].append([curpos-t_active_notes[n_note][1], n_p_l, n_p_k-t_active_notes[n_note][0]])
                                t_active_notes[n_note] = None

                        detectlen = notelist_data.getduration(cvpj_notelist)
                        if pat_duration < detectlen: pat_duration = detectlen
                        if t_instid not in pat_cvpj_notelist[cur_patnum][1]: pat_cvpj_notelist[cur_patnum][1][t_instid] = []
                        if cvpj_notelist != []: pat_cvpj_notelist[cur_patnum][1][t_instid].append(cvpj_notelist)

                pat_cvpj_notelist[cur_patnum][0] = pat_duration
                cur_patnum += 1

            elif sc2_datatype == b'SEQ': 
                sc2_seqdata = sc2object[1]
                sc2_seqdata = struct.unpack("I"*(len(sc2_seqdata)//4), sc2_seqdata)
                print('[input-soundclub2] Sequence', sc2_seqdata)

            elif sc2_datatype == b'INS': 
                sc2_insdata = sc2object[1]
                print('[input-soundclub2] Instrument: ', end='')
                cvpj_instid = 'sc2_'+str(cur_instnum)
                t_laneddata[cur_instnum] = {}
                if sc2_insdata[0] == 1:
                    t_instname = sc2_insdata[1:].decode('ascii')
                    print(t_instname)
                    sc2idvinst_instname = idvals.get_idval(idvals_inst_soundclub2, t_instname, 'name')
                    sc2idvinst_gminst = idvals.get_idval(idvals_inst_soundclub2, t_instname, 'gm_inst')
                    cvpj_instdata = {}
                    if sc2idvinst_gminst != None: cvpj_instdata = {'plugin': 'general-midi', 'plugindata': {'bank': 0, 'inst': sc2idvinst_gminst}}
                    tracks.r_create_inst(cvpj_l, cvpj_instid, cvpj_instdata)
                    tracks.r_basicdata(cvpj_l, cvpj_instid, sc2_insdata[1:].decode('ascii'), None, None, None)
                elif sc2_insdata[0] == 0:
                    bio_sc2_insdata = data_bytes.to_bytesio(sc2_insdata)
                    bio_sc2_insdata.seek(1)
                    insextype = bio_sc2_insdata.read(3)
                    if insextype == b'SMP':
                        cvpj_instname = data_bytes.readstring(bio_sc2_insdata)
                        print(cvpj_instname)
                        sc2_i_unk1 = bio_sc2_insdata.read(2)
                        sc2_i_samplesize, sc2_i_loopstart, sc2_i_unk3, sc2_i_unk4, sc2_i_freq = struct.unpack("IIIHH", bio_sc2_insdata.read(16))
                        cvpj_wavdata = bio_sc2_insdata.read()

                        wave_path = samplefolder + 'sc2_'+file_name+'_'+str(cur_instnum)+'.wav'

                        loopdata = None
                        cvpj_instdata = {}
                        cvpj_instdata['plugin'] = 'sampler'
                        cvpj_instdata['plugindata'] = {'file': wave_path}
                        cvpj_instdata['plugindata']['point_value_type'] = "samples"
                        if sc2_i_loopstart != 4294967295:
                            loopdata = {'loop':[sc2_i_loopstart, sc2_i_samplesize]}
                            cvpj_instdata['plugindata']['loop'] = {'enabled': 1, 'mode': "normal", 'points': [sc2_i_loopstart, sc2_i_samplesize]}
                        else: cvpj_instdata['plugindata']['loop'] = {'enabled': 0}
                        audio_wav.generate(wave_path, cvpj_wavdata, 1, sc2_i_freq, 8, loopdata)

                        tracks.ri_create_inst(cvpj_l, cvpj_instid, None, cvpj_instdata)
                        tracks.r_basicdata(cvpj_l, cvpj_instid, cvpj_instname, None, 0.3, None)
                tracks.r_pl_notes(cvpj_l, cvpj_instid, [])
                cur_instnum += 1
            else:  print('UNK', sc2object[0])

        for patnum in pat_cvpj_notelist:
            nlpd = pat_cvpj_notelist[patnum]
            dupeinst = {}
            for instnum in nlpd[1]:
                for nldata in nlpd[1][instnum]:
                    if instnum not in dupeinst: dupeinst[instnum] = 1
                    else: dupeinst[instnum] = 1 + dupeinst[instnum]
                    tracks.ri_nle_add(cvpj_l, 'sc2_'+str(instnum), str(instnum)+'_'+str(patnum)+'_'+str(dupeinst[instnum]), nldata, t_patnames[patnum])

        song_curpos = 0

        for patnum in sc2_seqdata:
            nlpd = pat_cvpj_notelist[patnum]
            songpartdur = nlpd[0]
            dupeinst = {}
            for instnum in nlpd[1]:
                for nldata in nlpd[1][instnum]:
                    if instnum not in dupeinst: dupeinst[instnum] = 1
                    else: dupeinst[instnum] = 1 + dupeinst[instnum]
                    if dupeinst[instnum] not in t_laneddata[instnum]: t_laneddata[instnum][dupeinst[instnum]] = []
                    pl_placement = placement_data.makepl_n_mi(song_curpos, songpartdur, str(instnum)+'_'+str(patnum)+'_'+str(dupeinst[instnum]))
                    t_laneddata[instnum][dupeinst[instnum]].append(pl_placement)
            song.add_timemarker_timesig(cvpj_l, t_patnames[patnum], song_curpos, sc2_headerdata[4], sc2_headerdata[5])
            tracks.a_add_auto_pl(cvpj_l, ['main', 'bpm'], auto.makepl(song_curpos, songpartdur, pat_tempopoints[patnum]))
            song_curpos += songpartdur

        for s_laneddata in t_laneddata:
            for s_laned in t_laneddata[s_laneddata]:
                tracks.r_pl_notes_laned(cvpj_l, 'sc2_'+str(s_laneddata), str(s_laned), t_laneddata[s_laneddata][s_laned])

        cvpj_l['do_addloop'] = True
        song.add_info_msg(cvpj_l, 'text', sc2_songdisc)
        cvpj_l['timesig_denominator'] = sc2_headerdata[4]
        cvpj_l['timesig_numerator'] = sc2_headerdata[5]
        cvpj_l['bpm'] = sc2_globaltempo
        return json.dumps(cvpj_l)