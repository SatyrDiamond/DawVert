# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_input
import json
from functions import xtramath
from functions import note_data

def getvalue(tag, name, fallbackval):
    if name in tag: 
        outval = tag[name]['Value']
        return outval if outval != None else fallbackval
    else: return fallbackval

maincolor = [0.42, 0.59, 0.24]

scaletable = [[0,0,0,0,0,0,0], [0,0,-1,0,0,-1,-1], [0,1,1,1,0,1,0], [0,-1,-1,-1,-1,-1,-1]]

class input_cvpj_f(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'mekimekichip'
    def gettype(self): return 'r'
    def getdawinfo(self, dawinfo_obj): 
        dawinfo_obj.name = 'メキメキチップ (MekiMeki Chip)'
        dawinfo_obj.file_ext = 'json'
        dawinfo_obj.auto_types = ['nopl_points']
        dawinfo_obj.track_nopl = True
    def supported_autodetect(self): return False
    def parse(self, convproj_obj, input_file, dv_config):
        bytestream = open(input_file, 'r')
        file_data = bytestream.read()
        mmc_main = json.loads(file_data)

        convproj_obj.type = 'r'
        convproj_obj.set_timings(4, True)

        #if 'debug' in dv_config:
        #    with open(input_file+'_pritty', "w") as fileout: json.dump(mmc_main, fileout, indent=4, sort_keys=True)

        mmc_tracks = mmc_main["Tracks"]
        mmc_bpm = getvalue(mmc_main, 'Bpm', 120)
        mmc_key = getvalue(mmc_main, 'Key', 0)
        mmc_scale = scaletable[getvalue(mmc_main, 'Scale', 0)]
        mmc_melooffset = getvalue(mmc_main, 'MelodyOffset', 0)

        mmc_bpm, notelen = xtramath.get_lower_tempo(mmc_bpm, 1, 200)

        convproj_obj.track_master.visual.name = 'MAS'
        convproj_obj.track_master.visual.color = maincolor
        convproj_obj.track_master.params.add('vol', getvalue(mmc_main, 'MasterVolume', 0.5)*1.5, 'float')
        convproj_obj.params.add('bpm', mmc_bpm, 'float')

        for tracknum, mmc_track in enumerate(mmc_tracks):
            cvpj_instid = 'CH'+str(tracknum)

            track_obj = convproj_obj.add_track(cvpj_instid, 'instrument', 0, False)

            track_obj.visual.name = cvpj_instid
            track_obj.visual.color = maincolor
            track_obj.params.add('enabled', bool(int(not getvalue(mmc_track, 'Mute', 0))), 'bool')
            track_obj.params.add('solo', bool(int(getvalue(mmc_track, 'Solo', 0))), 'bool')

            for mmc_note in mmc_track["Notes"]:
                mmc_wv = mmc_note['WaveVolume']

                n_key = getvalue(mmc_note, 'Melody', 0) + mmc_melooffset
                out_offset = getvalue(mmc_note, 'Add', 0)
                out_oct = int(n_key/7)
                out_key = n_key - out_oct*7

                notedur = getvalue(mmc_note, 'Length', 1)
                notekey = note_data.keynum_to_note(out_key, out_oct-3) + out_offset + mmc_key + mmc_scale[out_key]
                notepos = getvalue(mmc_note, 'BeatOffset', 0)
                notevol = getvalue(mmc_wv, 'Volume', 1)*1.5
                notepan = getvalue(mmc_wv, 'Pan', 0)*-1

                track_obj.placements.notelist.add_r(notepos, notedur, notekey, notevol, {'pan': notepan})

        convproj_obj.do_actions.append('do_addloop')
        convproj_obj.do_actions.append('do_singlenotelistcut')

