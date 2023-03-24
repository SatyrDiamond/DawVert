# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from functions import tracks
from functions import note_data
from functions import audio_wav
from functions import folder_samples
from functions import note_mod
from functions import notelist_data
from functions import idvals
import plugin_input
import struct
import json
import os

def sc2_read(sc2bytebuffer, offset):
    if isinstance(sc2bytebuffer, (bytes, bytearray)) == True:
        sc2bytebuffer = data_bytes.bytearray2BytesIO(sc2bytebuffer)
    sc2objects = []
    sc2bytebuffer.seek(0,2)
    filesize = sc2bytebuffer.tell()
    sc2bytebuffer.seek(offset)
    while filesize > sc2bytebuffer.tell():
        chunkname = sc2bytebuffer.read(3)
        chunksize = int.from_bytes(sc2bytebuffer.read(4), "little")
        chunkdata = sc2bytebuffer.read(chunksize)
        sc2objects.append([chunkname, chunkdata])
    return sc2objects

class input_soundclub2(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'soundclub2'
    def getname(self): return 'Sound Club 2'
    def gettype(self): return 'ri'
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
        print('[input-soundclub2] HEADER', sc2_headerdata)

        print('[input-soundclub2] TEMPO', sc2_headerdata[3])

        #               VAL   BPM
        #TEMPO            0 = 240
        #TEMPO           40 = 120
        #TEMPO          120 = 60

        file_name = os.path.splitext(os.path.basename(input_file))[0]
        samplefolder = folder_samples.samplefolder(extra_param, file_name)

        idvals_inst_soundclub2 = idvals.parse_idvalscsv('idvals/soundclub2_inst.csv')

        cvpj_l = {}
        
        cvpj_l['playlist'] = {}

        cur_patnum = 0
        cur_instnum = 1

        pat_cvpj_notelist = {}
        pat_tempopoints = {}

        t_patnames = {}
        t_laneddata = {}

        sc2objects = sc2_read(bytestream, 31)
        for sc2object in sc2objects:
            sc2_datatype = sc2object[0]

            if sc2_datatype == b'NAM': 
                sc2_songdisc = sc2object[1].decode('ascii')

            elif sc2_datatype == b'PAT': 
                sc2_patdata = sc2object[1]
                t_patid = 'sc2_'+str(cur_patnum)
                print('[input-soundclub2] Pattern')
                sc2_patobjs = sc2_read(sc2_patdata, 4)
                pat_cvpj_notelist[cur_patnum] = [0, {}]
                t_notelist = []
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
                            tp_sc2temp_out = ((tp_sc2temp-30)*-6)+60
                            pat_tempopoints[cur_patnum].append({"type": 'instant', "position": tp_pos, "value": tp_sc2temp_out})
                    elif sc2_patobj[0] == b'voi': 
                        cvpj_notelist = []
                        t_instid = int.from_bytes(sc2_patobj[1][:4], "little")+1
                        print('[input-soundclub2]      Events for Inst '+str(t_instid)+': '+str(len(sc2_patobj[1][5:])//3))
                        sc2_notedata = sc2_patobj[1][4:]
                        bio_sc2_notedata = data_bytes.bytearray2BytesIO(sc2_patobj[1][4:])
                        t_active_notes = [None for x in range(84)]
                        curpos = 0
                        n_curvol = 31
                        n_curpan = 15
                        while bio_sc2_notedata.tell() < len(sc2_notedata) :
                            n_len, n_type, n_note = struct.unpack("BBB", bio_sc2_notedata.read(3))
                            n_p_k = None
                            n_p_l = None 
                            curpos += n_len

                            if n_len == 255: 
                                bio_sc2_notedata.read(2)

                            if n_type == 17: #on
                                t_active_notes[n_note] = [n_note,curpos,n_curvol,n_curpan,[]]
                            if n_type == 19: #off
                                if t_active_notes[n_note] != None:
                                    t_notedata = t_active_notes[n_note]
                                    cvpj_notedata = note_data.rx_makenote(t_notedata[1], curpos-t_notedata[1], t_notedata[0]-36, n_curvol/31, (n_curpan-15)/-15)
                                    note_mod.pitchmod2point_init()
                                    for autopoint in t_notedata[4]: note_mod.pitchmod2point(cvpj_notedata, autopoint[0], 2, curpos-t_notedata[1], autopoint[1], autopoint[2])
                                    cvpj_notelist.append(cvpj_notedata)
                            if n_type == 20: #vol
                                n_curvol = n_note

                            if n_type == 21: #pan
                                n_curpan = n_note

                            if n_type == 54: #porta
                                n_p_k = bio_sc2_notedata.read(1)[0]
                                n_p_l = bio_sc2_notedata.read(1)[0]
                                t_active_notes[n_p_k] = t_active_notes[n_note]
                                autoappend = [curpos-t_active_notes[n_note][1], n_p_l, n_p_k-t_active_notes[n_note][0]]
                                t_active_notes[n_p_k][4].append(autoappend)
                                t_active_notes[n_note] = None

                        detectlen = notelist_data.getduration(cvpj_notelist)
                        if pat_duration < detectlen: pat_duration = detectlen

                        if t_instid not in pat_cvpj_notelist[cur_patnum][1]: pat_cvpj_notelist[cur_patnum][1][t_instid] = []
                        if cvpj_notelist != []:
                            pat_cvpj_notelist[cur_patnum][1][t_instid].append(cvpj_notelist)

                pat_cvpj_notelist[cur_patnum][0] = pat_duration

                cur_patnum += 1


            elif sc2_datatype == b'SEQ': 
                sc2_seqdata = sc2object[1]
                sc2_seqdata = struct.unpack("I"*(len(sc2_seqdata)//4), sc2_seqdata)
                print('[input-soundclub2] SEQ', sc2_seqdata)

            elif sc2_datatype == b'INS': 
                sc2_insdata = sc2object[1]
                print('[input-soundclub2] INS')
                cvpj_instid = 'sc2_'+str(cur_instnum)
                t_laneddata[cur_instnum] = {}
                if sc2_insdata[0] == 1:
                    t_instname = sc2_insdata[1:].decode('ascii')
                    sc2idvinst_instname = idvals.get_idval(idvals_inst_soundclub2, t_instname, 'name')
                    sc2idvinst_gminst = idvals.get_idval(idvals_inst_soundclub2, t_instname, 'gm_inst')
                    cvpj_instdata = {}
                    if sc2idvinst_gminst != None: cvpj_instdata = {'plugin': 'general-midi', 'plugindata': {'bank': 0, 'inst': sc2idvinst_gminst}}
                    tracks.r_addtrack_inst(cvpj_l, cvpj_instid, cvpj_instdata)
                    tracks.r_addtrack_data(cvpj_l, cvpj_instid, sc2_insdata[1:].decode('ascii'), None, None, None)
                elif sc2_insdata[0] == 0:
                    bio_sc2_insdata = data_bytes.bytearray2BytesIO(sc2_insdata)
                    bio_sc2_insdata.seek(1)
                    insextype = bio_sc2_insdata.read(3)
                    if insextype == b'SMP':
                        cvpj_instname = data_bytes.readstring(bio_sc2_insdata)
                        sc2_i_unk1 = bio_sc2_insdata.read(2)
                        cvpj_datasize = int.from_bytes(bio_sc2_insdata.read(4), "little")
                        sc2_i_loopstart, sc2_i_unk3 = struct.unpack("II", bio_sc2_insdata.read(8))
                        sc2_i_unk4, sc2_i_freq = struct.unpack("HH", bio_sc2_insdata.read(4))
                        cvpj_wavdata = bio_sc2_insdata.read()

                        loopdata = None
                        if sc2_i_loopstart != 4294967295: loopdata = {'loop':[sc2_i_loopstart, cvpj_datasize]}

                        wave_path = samplefolder + 'sc2_'+file_name+'_'+str(cur_instnum)+'.wav'
                        audio_wav.generate(wave_path, cvpj_wavdata, 1, sc2_i_freq, 8, loopdata)

                        cvpj_instdata = {}
                        cvpj_instdata['plugin'] = 'sampler'
                        cvpj_instdata['plugindata'] = {'file': wave_path}
                        cvpj_instdata['plugindata']['loop'] = {}
                        if sc2_i_loopstart != 4294967295:
                            cvpj_instdata['plugindata']['loop']['enabled'] = 1
                            cvpj_instdata['plugindata']['loop']['mode'] = "normal"
                            cvpj_instdata['plugindata']['loop']['points'] = [sc2_i_loopstart, cvpj_datasize]
                        else:
                            cvpj_instdata['plugindata']['loop']['enabled'] = 0
                        tracks.ri_addtrack_inst(cvpj_l, cvpj_instid, None, cvpj_instdata)
                        tracks.r_addtrack_data(cvpj_l, cvpj_instid, cvpj_instname, None, 0.3, None)
                tracks.r_addtrackpl(cvpj_l, cvpj_instid, [])
                cur_instnum += 1
            else:  print('UNK', sc2object[0])

        for patnum in pat_cvpj_notelist:
            nlpd = pat_cvpj_notelist[patnum]
            dupeinst = {}
            for instnum in nlpd[1]:
                for nldata in nlpd[1][instnum]:
                    if instnum not in dupeinst: dupeinst[instnum] = 1
                    else: dupeinst[instnum] = 1 + dupeinst[instnum]
                    tracks.ri_addinst_nle(cvpj_l, 'sc2_'+str(instnum), str(instnum)+'_'+str(patnum)+'_'+str(dupeinst[instnum]), nldata, t_patnames[patnum])

        song_curpos = 0

        cvpj_l['automation'] = {}
        cvpj_l['automation']['main'] = {}
        cvpj_l['automation']['main']['bpm'] = []

        for patnum in sc2_seqdata:
            nlpd = pat_cvpj_notelist[patnum]
            songpartdur = nlpd[0]
            dupeinst = {}
            for instnum in nlpd[1]:
                for nldata in nlpd[1][instnum]:
                    if instnum not in dupeinst: dupeinst[instnum] = 1
                    else: dupeinst[instnum] = 1 + dupeinst[instnum]
                    if dupeinst[instnum] not in t_laneddata[instnum]: t_laneddata[instnum][dupeinst[instnum]] = []
                    pl_placement = {}
                    pl_placement['position'] = song_curpos
                    pl_placement['duration'] = songpartdur
                    pl_placement['fromindex'] = str(instnum)+'_'+str(patnum)+'_'+str(dupeinst[instnum])
                    t_laneddata[instnum][dupeinst[instnum]].append(pl_placement)
            cvpj_l['automation']['main']['bpm'].append({'position': song_curpos, 'duration': songpartdur, 'points': pat_tempopoints[patnum]})

            song_curpos += songpartdur

        cvpj_l['track_placements'] = {}
        for s_laneddata in t_laneddata:
            cvpj_l['track_placements']['sc2_'+str(s_laneddata)] = {}
            cvpj_s_tp = cvpj_l['track_placements']['sc2_'+str(s_laneddata)] 
            cvpj_s_tp['notes_laned'] = 1
            cvpj_s_tp['notes_laneorder'] = []
            cvpj_s_tp['notes_lanedata'] = {}
            for s_laned in t_laneddata[s_laneddata]:
                cvpj_s_tp['notes_laneorder'].append(str(s_laned))
                cvpj_s_tp['notes_lanedata'][str(s_laned)] = {}
                cvpj_s_tp['notes_lanedata'][str(s_laned)]['placements'] = t_laneddata[s_laneddata][s_laned]


        cvpj_l['do_addwrap'] = True

        cvpj_l['use_instrack'] = False
        cvpj_l['use_fxrack'] = False
        
        cvpj_l['timesig_denominator'] = sc2_headerdata[4]
        cvpj_l['timesig_numerator'] = sc2_headerdata[5]

        cvpj_l['info'] = {}

        cvpj_l['info']['message'] = {}
        cvpj_l['info']['message']['type'] = 'text'
        cvpj_l['info']['message']['text'] = sc2_songdisc

        cvpj_l['bpm'] = 120
        return json.dumps(cvpj_l)