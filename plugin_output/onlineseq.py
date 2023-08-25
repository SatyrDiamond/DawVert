# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_output
import json
import struct
import blackboxprotobuf
from functions import data_values
from functions import params

def float2int(value): return struct.unpack("<I", struct.pack("<f", value))[0]

class output_onlineseq(plugin_output.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'output'
    def getname(self): return 'Online Sequencer'
    def getshortname(self): return 'onlineseq'
    def gettype(self): return 'r'
    def plugin_archs(self): return None
    def getdawcapabilities(self): 
        return {
        'fxrack': False,
        'track_lanes': False,
        'placement_cut': False,
        'placement_loop': False,
        'auto_nopl': True,
        'track_nopl': False
        }
    def getsupportedplugins(self): return []
    def parse(self, convproj_json, output_file):
        projJ = json.loads(convproj_json)

        tempo = int(params.get(projJ, [], 'bpm', 120)[0])

        onlineseqdata = {}
        onlineseqdata[1] = {1: tempo, 3: []}
        onlineseqdata[2] = []

        if 'track_data' in projJ and 'track_order' in projJ:
            #print('[output-midi] Trk# | Ch# | Bnk | Prog | Key | Name')
            tracknum = 0

            for trackid in projJ['track_order']:
                if trackid in projJ['track_data']:
                    trackdata = projJ['track_data'][trackid]

                    if trackid in projJ['track_placements']:
                        if 'notes' in projJ['track_placements'][trackid]:

                            track_pls = projJ['track_placements'][trackid]['notes']

                            onlineseqnum = 43 + tracknum*10000

                            trackname = data_values.get_value(trackdata, 'name', 'noname')
                            trackvol = params.get(trackdata, [], 'vol', 1.0)[0]
                    
                            onlseqinst = {1: onlineseqnum, 2: {1: float2int(trackvol), 10: 1, 15: trackname}}
                            onlineseqdata[1][3].append(onlseqinst)

                            for track_pl in track_pls:
                                basepos = track_pl['position']
                                notelist = track_pl['notelist']
                                for cvpj_note in notelist:
                                    onlineseq_note = {
                                        "1": cvpj_note['key']+60,
                                        "2": float2int(cvpj_note['position']+basepos),
                                        "3": float2int(cvpj_note['duration']),
                                        "4": onlineseqnum,
                                        "5": float2int(data_values.get_value(cvpj_note, 'vol', 1.0))
                                        }
                                    onlineseqdata[2].append(onlineseq_note)

                            tracknum += 1

        protobuf_typedef = {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '3': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'message', 'message_typedef': {'1': {'type': 'fixed32', 'name': ''}, '10': {'type': 'int', 'name': ''}, '15': {'type': 'bytes', 'name': ''}}, 'name': ''}}, 'name': ''}}, 'name': ''}, '2': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '3': {'type': 'fixed32', 'name': ''}, '4': {'type': 'int', 'name': ''}, '5': {'type': 'fixed32', 'name': ''}, '2': {'type': 'fixed32', 'name': ''}}, 'name': ''}}

        with open(output_file, "wb") as fileout:
            fileout.write(blackboxprotobuf.encode_message(onlineseqdata,protobuf_typedef))