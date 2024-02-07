# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import audio_wav
from functions import data_bytes
from objects import dv_dataset
import json
import os
import plugin_input
import struct

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
        'samples_inside': True,
        'track_lanes': True,
        'auto_nopl': True
        }
    def supported_autodetect(self): return True
    def detect(self, input_file):
        bytestream = open(input_file, 'rb')
        bytestream.seek(0)
        bytesdata = bytestream.read(3)
        if bytesdata == b'SN2': return True
        else: return False
    def parse(self, convproj_obj, input_file, extra_param):
        convproj_obj.type = 'ri'
        convproj_obj.set_timings(4, False)

        bytestream = open(input_file, 'rb')
        bytestream.seek(7)
        sc2_headerdata = struct.unpack("iiiiii", bytestream.read(24))
        sc2_globaltempo = (1/((sc2_headerdata[3]/40)/2+0.5))*120

        print('[input-soundclub2] Tempo', sc2_globaltempo)

        samplefolder = extra_param['samplefolder']

        dataset = dv_dataset.dataset('./data_dset/soundclub2.dset')
        dataset_midi = dv_dataset.dataset('./data_dset/midi.dset')

        cur_patnum = 0
        cur_instnum = 1

        pat_t_nl = {}
        pat_tempopoints = {}

        t_patnames = {}
        t_laneddata = {}

        sc2objects = sc2_read(bytestream, 31)
        for sc2object in sc2objects:
            sc2_datatype = sc2object[0]

            if sc2_datatype == b'NAM': sc2_songdisc = sc2object[1].decode('ascii')

            elif sc2_datatype == b'PAT': 
                t_patid = 'sc2_'+str(cur_patnum)
                print('[input-soundclub2] Pattern')
                sc2_patobjs = sc2_read(sc2object[1], 4)
                pat_t_nl[cur_patnum] = [0, {}]
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
                            pat_tempopoints[cur_patnum].append([tp_pos, tp_sc2temp_out])
                    elif sc2_patobj[0] == b'voi': 
                        t_nl = []
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
                                    #cvpj_notedata = note_data.rx_makenote(t_notedata[1], curpos-t_notedata[1], t_notedata[0]-36, n_curvol/31, (n_curpan-15)/-15)
                                    t_nl.append([t_notedata[1], curpos-t_notedata[1], t_notedata[0]-36, n_curvol/31, (n_curpan-15)/-15, []])

                                    for autopoint in t_notedata[4]: 
                                        t_nl[-1][5].append([autopoint[0], autopoint[1], autopoint[2], n_curvol/31])
                            if n_type == 20: n_curvol = n_note
                            if n_type == 21: n_curpan = n_note
                            if n_type == 54: #porta
                                n_p_k, n_p_l = bio_sc2_notedata.read(2)
                                t_active_notes[n_p_k] = t_active_notes[n_note]
                                t_active_notes[n_p_k][4].append([curpos-t_active_notes[n_note][1], n_p_l, n_p_k-t_active_notes[n_note][0]])
                                t_active_notes[n_note] = None

                        detectlen = max([x[0]+x[1] for x in t_nl])
                        if pat_duration < detectlen: pat_duration = detectlen
                        if t_instid not in pat_t_nl[cur_patnum][1]: pat_t_nl[cur_patnum][1][t_instid] = []
                        if t_nl: pat_t_nl[cur_patnum][1][t_instid].append(t_nl)

                pat_t_nl[cur_patnum][0] = pat_duration
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
                    convproj_obj.add_track_from_dset(cvpj_instid, cvpj_instid, dataset, dataset_midi, t_instname, None, None, 1, True)

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

                        if sc2_i_loopstart != 4294967295:
                            loopdata = {'loop':[sc2_i_loopstart, sc2_i_samplesize]}
                            cvpj_loop = {'enabled': 1, 'mode': "normal", 'points': [sc2_i_loopstart, sc2_i_samplesize]}
                        else: 
                            loopdata = None
                            cvpj_loop = {'enabled': 0}

                        wave_path = samplefolder + 'sc2_'+str(cur_instnum)+'.wav'
                        audio_wav.generate(wave_path, cvpj_wavdata, 1, sc2_i_freq, 8, loopdata)
                        plugin_obj, pluginid, sampleref_obj = convproj_obj.add_plugin_sampler_genid(wave_path)
                        sampleref_obj.dur_samples = sc2_i_samplesize
                        sampleref_obj.dur_sec = sc2_i_samplesize/sc2_i_freq
                        sampleref_obj.timebase = sc2_i_freq
                        sampleref_obj.hz = sc2_i_freq
                        plugin_obj.datavals.add('point_value_type', 'samples')
                        plugin_obj.datavals.add('loop', cvpj_loop)
                        plugin_obj.datavals.add('length', sc2_i_samplesize)
                        track_obj = convproj_obj.add_track(cvpj_instid, 'instrument', True, True)
                        track_obj.params.add('vol', 0.3, 'float')
                        track_obj.visual.name = cvpj_instname
                        track_obj.inst_pluginid = pluginid
                cur_instnum += 1
            else: print('UNK', sc2object[0])

        for patnum in pat_t_nl:
            nlpd = pat_t_nl[patnum]
            dupeinst = {}
            for instnum in nlpd[1]:
                for nldata in nlpd[1][instnum]:
                    if instnum not in dupeinst: dupeinst[instnum] = 1
                    else: dupeinst[instnum] = 1 + dupeinst[instnum]
                    nle_trkid = 'sc2_'+str(instnum)
                    nle_patid = str(instnum)+'_'+str(patnum)+'_'+str(dupeinst[instnum])
                    nle_patname = t_patnames[patnum]
                    track_found, track_obj = convproj_obj.find_track(nle_trkid)
                    if track_found:
                        nle_obj = track_obj.add_notelistindex(nle_patid)
                        nle_obj.visual.name = nle_patname
                        for n in nldata: 
                            nle_obj.notelist.add_r(n[0], n[1], n[2], n[3], {'pan': n[4]})
                            for sn in n[5]:
                                nle_obj.notelist.last_add_slide(sn[0], sn[1], sn[2], sn[3], {'pan': n[4]})
                        nle_obj.notelist.notemod_conv()

        song_curpos = 0
        for patnum in sc2_seqdata:
            nlpd = pat_t_nl[patnum]
            songpartdur = nlpd[0]
            dupeinst = {}
            for instnum in nlpd[1]:
                for nldata in nlpd[1][instnum]:
                    if instnum not in dupeinst: dupeinst[instnum] = 1
                    else: dupeinst[instnum] = 1 + dupeinst[instnum]
                    if dupeinst[instnum] not in t_laneddata[instnum]: t_laneddata[instnum][dupeinst[instnum]] = []
                    pl_placement = [song_curpos, songpartdur, str(instnum)+'_'+str(patnum)+'_'+str(dupeinst[instnum])]
                    t_laneddata[instnum][dupeinst[instnum]].append(pl_placement)

            convproj_obj.timesig_auto.add_point(song_curpos, [sc2_headerdata[4], sc2_headerdata[5]])
            timemarker_obj = convproj_obj.add_timemarker()
            timemarker_obj.visual.name = t_patnames[patnum]
            timemarker_obj.position = song_curpos*240
\
            autopl_obj = convproj_obj.add_automation_pl(['main','bpm'], 'float')
            autopl_obj.position = song_curpos
            autopl_obj.duration = songpartdur
            for tempop in pat_tempopoints[patnum]:
                autopoint_obj = autopl_obj.data.add_point()
                autopoint_obj.pos = tempop[0]
                autopoint_obj.value = tempop[1]

            song_curpos += songpartdur

        for track_id in t_laneddata:
            for lane_num in t_laneddata[track_id]:
                track_found, track_obj = convproj_obj.find_track('sc2_'+str(track_id))
                if track_found:
                    lane_obj = track_obj.add_lane(str(lane_num))
                    for p in t_laneddata[track_id][lane_num]:
                        placement_obj = lane_obj.placements.add_notes()
                        placement_obj.position = p[0]
                        placement_obj.duration = p[1]
                        placement_obj.fromindex = p[2]

        convproj_obj.do_actions.append('do_addloop')
        convproj_obj.params.add('bpm', sc2_globaltempo, 'float')
        convproj_obj.timesig = [sc2_headerdata[4], sc2_headerdata[5]]
        convproj_obj.metadata.comment_text = sc2_songdisc