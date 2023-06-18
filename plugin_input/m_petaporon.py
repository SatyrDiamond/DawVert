# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from functions import tracks
from functions import notedata
from functions import placement_data
import plugin_input
import io
import struct
import json

peta_colors = [
[0.22, 0.52, 0.35],
[0.51, 0.88, 0.30],
[1.00, 0.95, 0.46],
[1.00, 0.75, 0.21],
[0.81, 0.47, 0.34],
[0.88, 0.25, 0.25],
[1.00, 0.50, 0.67],
[0.75, 0.25, 0.70],
[0.22, 0.60, 1.00],
[0.43, 0.93, 1.00]]

def getval(i_val):
    if i_val == 91: i_val = 11
    elif i_val == 11: i_val = 91
    elif i_val == -3: i_val = 92
    elif i_val == -2: i_val = 93
    return i_val

class input_soundation(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'petaporon'
    def getname(self): return 'Petaporon'
    def gettype(self): return 'm'
    def supported_autodetect(self): return False
    def getdawcapabilities(self): 
        return {
        'track_lanes': True,
        'track_nopl': True
        }
    def parse(self, input_file, extra_param):
        bytestream = open(input_file, 'r')
        sndstat_data = json.load(bytestream)
        cvpj_l = {}
        peta_notedata = sndstat_data['n'].encode('ascii')
        peta_noteints = struct.unpack("B"*len(peta_notedata), peta_notedata)
        bio_peta_notebytes = data_bytes.to_bytesio(bytes(peta_noteints))

        cvpj_notelist = notedata.NoteList('steps')

        for instnum in range(10):
            instid = 'petaporon'+str(instnum)
            tracks.m_create_inst(cvpj_l, instid, {})
            tracks.m_basicdata_inst(cvpj_l, instid, 'Inst #'+str(instnum+1), peta_colors[instnum], 1.0, 0.0)

        for _ in range(len(peta_noteints)//5):
            partdata = bio_peta_notebytes.read(5)
            peta_note = getval(partdata[0]-35)
            peta_inst = getval(partdata[1]-35)
            peta_len = getval(partdata[2]-35)
            peta_poshigh = getval(partdata[3]-35)
            peta_poslow = getval(partdata[4]-35)
            peta_pos = peta_poslow+(peta_poshigh*94)

            cvpj_notelist.add(
                peta_pos, 
                peta_len, 
                peta_note-12, 
                instrument='petaporon'+str(peta_inst))   

        placementdata = placement_data.nl2pl(cvpj_notelist.get())
        tracks.m_playlist_pl(cvpj_l, 1, None, None, placementdata)

        cvpj_l['do_singlenotelistcut'] = True

        cvpj_l['timesig_numerator'] = sndstat_data['c']
        cvpj_l['timesig_denominator'] = 4
        cvpj_l['bpm'] = sndstat_data['t']

        return json.dumps(cvpj_l)
