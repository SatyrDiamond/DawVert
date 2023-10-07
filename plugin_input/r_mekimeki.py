# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import placement_data
from functions import note_data
from functions import song
from functions_tracks import tracks_r
from functions_tracks import tracks_master
import plugin_input
import json

def getvalue(tag, name, fallbackval):
    if name in tag: return tag[name]['Value']
    else: return fallbackval

maincolor = [0.42, 0.59, 0.24]

scaletable = [[0,0,0,0,0,0,0], [0,0,-1,0,0,-1,-1], [0,1,1,1,0,1,0], [0,-1,-1,-1,-1,-1,-1]]

class input_cvpj_f(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'mekimekichip'
    def getname(self): return 'メキメキチップ (MekiMeki Chip)'
    def gettype(self): return 'r'
    def getdawcapabilities(self): 
        return {
        'auto_nopl': True,
        'track_nopl': True
        }
    def supported_autodetect(self): return False
    def parse(self, input_file, extra_param):
        bytestream = open(input_file, 'r')
        file_data = bytestream.read()
        mmc_main = json.loads(file_data)

        with open(input_file+'_pritty', "w") as fileout:
            json.dump(mmc_main, fileout, indent=4, sort_keys=True)

        mmc_tracks = mmc_main["Tracks"]
        mmc_bpm = getvalue(mmc_main, 'Bpm', 120)
        mmc_mastervolume = getvalue(mmc_main, 'MasterVolume', 0.5)
        mmc_key = getvalue(mmc_main, 'Key', 0)
        mmc_scale = scaletable[getvalue(mmc_main, 'Scale', 0)]
        mmc_melooffset = getvalue(mmc_main, 'MelodyOffset', 0)
        if mmc_mastervolume == None: mmc_mastervolume = 1

        cvpj_l = {}

        mmc_bpm, notelen = song.get_lower_tempo(mmc_bpm, 1, 200)

        tracks_master.create(cvpj_l, mmc_mastervolume*1.5)
        tracks_master.visual(cvpj_l, name='MAS', color=maincolor)

        tracknum = 0
        for mmc_track in mmc_tracks:
            cvpj_instid = 'CH'+str(tracknum)

            cvpj_notelist = []

            mmc_notes = mmc_track["Notes"]
            for mmc_note in mmc_notes:
                mmc_wv = mmc_note['WaveVolume']

                cvpj_notedata = {}

                n_key = getvalue(mmc_note, 'Melody', 0) + mmc_melooffset
                out_offset = getvalue(mmc_note, 'Add', 0)
                out_oct = int(n_key/7)
                out_key = n_key - out_oct*7

                notedur = getvalue(mmc_note, 'Length', 1)*notelen
                notekey = note_data.keynum_to_note(out_key, out_oct-3) + out_offset + mmc_key + mmc_scale[out_key]
                notepos = getvalue(mmc_note, 'BeatOffset', 0)*notelen
                notevol = getvalue(mmc_wv, 'Volume', 1)*1.5
                notepan = getvalue(mmc_wv, 'Pan', 0)
                if notepan == None: notepan = 0
                notepan = notepan*-1

                cvpj_notedata = note_data.rx_makenote(notepos, notedur, notekey, notevol, notepan)
                cvpj_notelist.append(cvpj_notedata)

            tracks_r.track_create(cvpj_l, cvpj_instid, 'instrument')
            tracks_r.track_visual(cvpj_l, cvpj_instid, name=cvpj_instid, color=maincolor)
            tracks_r.track_param_add(cvpj_l, cvpj_instid, 'enabled', int(not getvalue(mmc_track, 'Mute', False)), 'bool')
            tracks_r.track_param_add(cvpj_l, cvpj_instid, 'solo', int(getvalue(mmc_track, 'Solo', False)), 'bool')
            tracks_r.add_pl(cvpj_l, cvpj_instid, 'notes', placement_data.nl2pl(cvpj_notelist))

            tracknum += 1

        cvpj_l['do_addloop'] = True
        cvpj_l['do_singlenotelistcut'] = True
        
        cvpj_l['use_instrack'] = False
        cvpj_l['use_fxrack'] = False
        cvpj_l['timesig'] = [4, 4]

        song.add_param(cvpj_l, 'bpm', mmc_bpm)
        return json.dumps(cvpj_l)

