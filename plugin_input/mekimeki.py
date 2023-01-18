# SPDX-FileCopyrightText: 2022 Colby Ray
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from functions import note_mod
import plugin_input
import json

def getvalue(tag, name):
    return tag[name]['Value']

keytable = [0,2,4,5,7,9,11,12]
maincolor = [0.42, 0.59, 0.24]

class input_cvpj_f(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'mekimekichip'
    def getname(self): return 'メキメキチップ (MekiMeki Chip)'
    def gettype(self): return 'r'
    def supported_autodetect(self): return False
    def parse(self, input_file, extra_param):
        bytestream = open(input_file, 'r')
        file_data = bytestream.read()
        mmc_main = json.loads(file_data)

        cvpj_l_trackdata = {}
        cvpj_l_trackordering = []
        cvpj_l_track_master = {}

        mmc_bpm = getvalue(mmc_main, 'Bpm')
        mmc_mastervolume = getvalue(mmc_main, 'MasterVolume')
        cvpj_l_track_master['name'] = 'MAS'
        cvpj_l_track_master['vol'] = mmc_mastervolume*1.5
        cvpj_l_track_master['color'] = maincolor

        mmc_tracks = mmc_main["Tracks"]

        tracknum = 0
        for mmc_track in mmc_tracks:
            trackdata = {}
            trackdata['color'] = maincolor
            trackdata['name'] = 'CH'+str(tracknum)
            trackdata['type'] = 'instrument'
            trackdata["instdata"] = {}
            trackdata["instdata"]['plugin'] = 'none'
            cvpj_l_trackdata[str('CH'+str(tracknum))] = trackdata
            cvpj_l_trackordering.append('CH'+str(tracknum))

            cvpj_notelist = []

            mmc_notes = mmc_track["Notes"]
            for mmc_note in mmc_notes:
                #print(mmc_note)
                mmc_wv = mmc_note['WaveVolume']

                notedata = {}
                notedata["duration"] = getvalue(mmc_note, 'Length')

                n_key = getvalue(mmc_note, 'Melody')
                out_offset = getvalue(mmc_note, 'Add')
                out_oct = int(n_key/7)
                out_key = n_key - out_oct*7

                notedata["key"] = keytable[out_key] + (out_oct-3)*12 + out_offset
                notedata["position"] = getvalue(mmc_note, 'BeatOffset')
                notedata["vol"] = getvalue(mmc_wv, 'Volume')*1.5
                notedata["pan"] = getvalue(mmc_wv, 'Pan')*-1
                cvpj_notelist.append(notedata)

            trackdata['placements'] = []

            if cvpj_notelist != []:
                placement_pl = {}
                placement_pl['position'] = 0
                placement_pl['duration'] = note_mod.getduration(cvpj_notelist)
                placement_pl['notelist'] = cvpj_notelist
                trackdata['placements'].append(placement_pl)

            tracknum += 1

        cvpj_l = {}
        cvpj_l['use_fxrack'] = False
        cvpj_l['bpm'] = mmc_bpm
        cvpj_l['trackdata'] = cvpj_l_trackdata
        cvpj_l['trackordering'] = cvpj_l_trackordering
        cvpj_l['track_master'] = cvpj_l_track_master
        return json.dumps(cvpj_l)

