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
    def gettype(self): return 'f'
    def supported_autodetect(self): return False
    def parse(self, input_file, extra_param):
        bytestream = open(input_file, 'r')
        file_data = bytestream.read()
        mmc_main = json.loads(file_data)

        cvpj_l_trackdata = {}
        cvpj_l_trackordering = []
        cvpj_l_fxrack = {}
        cvpj_l_fxrack['0'] = {'name': 'MAS'}

        mmc_bpm = getvalue(mmc_main, 'Bpm')
        mmc_mastervolume = getvalue(mmc_main, 'MasterVolume')
        cvpj_l_fxrack['0']['vol'] = mmc_mastervolume*1.5
        cvpj_l_fxrack['0']['color'] = maincolor

        mmc_tracks = mmc_main["Tracks"]

        tracknum = 0
        for mmc_track in mmc_tracks:
            trackdata = {}
            trackdata['color'] = maincolor
            trackdata['name'] = 'CH'+str(tracknum)
            trackdata['type'] = 'instrument'
            trackdata['fxrack_channel'] = tracknum+1
            trackdata["instdata"] = {}
            trackdata["instdata"]['plugin'] = 'none'
            cvpj_l_fxrack[str(tracknum+1)] = {'name': 'CH'+str(tracknum)}
            cvpj_l_fxrack[str(tracknum+1)]['color'] = maincolor
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

            trackdata['placements'] = [{}]
            trackdata['placements'][0]['position'] = 0
            trackdata['placements'][0]['duration'] = note_mod.getduration(cvpj_notelist)
            trackdata['placements'][0]['notelist'] = cvpj_notelist

            tracknum += 1

        rootJ = {}
        rootJ['bpm'] = mmc_bpm
        rootJ['trackdata'] = cvpj_l_trackdata
        rootJ['trackordering'] = cvpj_l_trackordering
        rootJ['fxrack'] = cvpj_l_fxrack
        return json.dumps(rootJ)

