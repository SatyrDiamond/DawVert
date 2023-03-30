# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from functions import note_mod
from functions import placements
from functions import tracks
from functions import note_data
import plugin_input
import json

def getvalue(tag, name):
    if name in tag:
        return tag[name]['Value']
    else:
        return None

keytable = [0,2,4,5,7,9,11,12]
maincolor = [0.42, 0.59, 0.24]

class input_cvpj_f(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'mekimekichip'
    def getname(self): return 'メキメキチップ (MekiMeki Chip)'
    def gettype(self): return 'r'
    def getdawcapabilities(self): 
        return {
        'fxrack': False,
        'r_track_lanes': False,
        'placement_cut': False,
        'placement_warp': False,
        'no_placements': True
        }
    def supported_autodetect(self): return False
    def parse(self, input_file, extra_param):
        bytestream = open(input_file, 'r')
        file_data = bytestream.read()
        mmc_main = json.loads(file_data)
        mmc_tracks = mmc_main["Tracks"]
        mmc_bpm = getvalue(mmc_main, 'Bpm')
        mmc_mastervolume = getvalue(mmc_main, 'MasterVolume')
        if mmc_mastervolume == None: mmc_mastervolume = 1

        notelen = 1

        while mmc_bpm > 200:
            mmc_bpm = mmc_bpm/2
            notelen = notelen/2

        cvpj_l_track_master = {}
        cvpj_l_track_master['name'] = 'MAS'
        cvpj_l_track_master['vol'] = mmc_mastervolume*1.5
        cvpj_l_track_master['color'] = maincolor

        cvpj_l = {}

        tracknum = 0
        for mmc_track in mmc_tracks:
            trackid = 'CH'+str(tracknum)
            tracks.r_addtrack_inst(cvpj_l, trackid, {})
            tracks.r_addtrack_data(cvpj_l, trackid, trackid, maincolor, None, None)

            cvpj_notelist = []

            mmc_notes = mmc_track["Notes"]
            for mmc_note in mmc_notes:
                mmc_wv = mmc_note['WaveVolume']

                cvpj_notedata = {}

                n_key = getvalue(mmc_note, 'Melody')
                out_offset = getvalue(mmc_note, 'Add')
                out_oct = int(n_key/7)
                out_key = n_key - out_oct*7

                notedur = getvalue(mmc_note, 'Length')*notelen
                notekey = keytable[out_key] + (out_oct-3)*12 + out_offset
                notepos = getvalue(mmc_note, 'BeatOffset')*notelen
                notevol = getvalue(mmc_wv, 'Volume')*1.5
                notepan = getvalue(mmc_wv, 'Pan')
                if notepan == None: notepan = 0
                notepan = notepan*-1

                cvpj_notedata = note_data.rx_makenote(notepos, notedur, notekey, notevol, notepan)
                cvpj_notelist.append(cvpj_notedata)

            tracks.r_addtrackpl(cvpj_l, trackid, placements.nl2pl(cvpj_notelist))

            tracknum += 1

        cvpj_l['do_addwrap'] = True
        cvpj_l['do_singlenotelistcut'] = True
        
        cvpj_l['use_instrack'] = False
        cvpj_l['use_fxrack'] = False

        cvpj_l['bpm'] = mmc_bpm
        cvpj_l['track_master'] = cvpj_l_track_master
        return json.dumps(cvpj_l)

