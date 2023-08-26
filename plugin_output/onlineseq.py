# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_output
import json
import struct
import blackboxprotobuf
from functions import data_values
from functions import params
from functions import idvals
from functions import plugins

def float2int(value): return struct.unpack("<I", struct.pack("<f", value))[0]

def create_markers(cvpj_auto, inst_id, instparam):
    if len(cvpj_auto['placements']) != 0:
        mainauto = cvpj_auto['placements'][0]
        basepos = mainauto['position']
        points = mainauto['points']

        for point in points:
            markerdata = {}
            posdata = point['position']+basepos
            markerdata[1] = float2int(point['position']+basepos)
            markerdata[2] = instparam
            markerdata[3] = inst_id
            markerdata[4] = float2int(point['value'])
            pointtype = data_values.get_value(point, 'type', 'normal')
            if pointtype == 'normal': markerdata[5] = 1
            if posdata not in glob_markerdata: glob_markerdata[posdata] = []
            glob_markerdata[posdata].append(markerdata)

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
        'track_nopl': True
        }
    def getsupportedplugins(self): return ['midi']
    def parse(self, convproj_json, output_file):
        global glob_markerdata
        projJ = json.loads(convproj_json)

        tempo = int(params.get(projJ, [], 'bpm', 120)[0])

        onlineseqdata = {}
        onlineseqdata[1] = {1: tempo, 3: []}
        onlineseqdata[2] = []
        onlineseqdata[3] = []

        idvals_onlineseq_inst = idvals.parse_idvalscsv('data_idvals/onlineseq_map_midi.csv')

        repeatedolinst = {}

        cvpjid_onlineseqid = {}

        glob_markerdata = {}

        if 'track_data' in projJ and 'track_order' in projJ:
            #print('[output-midi] Trk# | Ch# | Bnk | Prog | Key | Name')

            for trackid in projJ['track_order']:
                if trackid in projJ['track_data']:
                    trackdata = projJ['track_data'][trackid]

                    if trackid in projJ['track_placements']:
                        if 'notes' in projJ['track_placements'][trackid]:

                            onlineseqinst = 43
                            trackname = data_values.get_value(trackdata, 'name', 'noname')
                            trackvol = params.get(trackdata, [], 'vol', 1.0)[0]

                            if 'instdata' in trackdata:
                                pluginid = data_values.get_value(trackdata['instdata'], 'pluginid', 1.0)
                                plugintype = plugins.get_plug_type(projJ, pluginid)
                                if plugintype[0] == 'midi':
                                    cvpj_plugindata = plugins.get_plug_data(projJ, pluginid)
                                    if cvpj_plugindata['bank'] != 128:
                                        olinst = idvals.get_idval(idvals_onlineseq_inst, str(cvpj_plugindata['inst']), 'outid')
                                        if olinst != 'null': onlineseqinst = int(olinst)
                                    else:
                                        onlineseqinst = 2

                            #print(str(onlineseqinst).rjust(10), trackid)

                            if onlineseqinst not in repeatedolinst: repeatedolinst[onlineseqinst] = 0
                            else: repeatedolinst[onlineseqinst] += 1 

                            track_pls = projJ['track_placements'][trackid]['notes']

                            onlineseqnum = onlineseqinst + repeatedolinst[onlineseqinst]*10000

                            onlseqinst = {1: onlineseqnum, 2: {1: float2int(trackvol), 10: 1, 15: trackname}}
                            onlineseqdata[1][3].append(onlseqinst)

                            for track_pl in track_pls:
                                basepos = track_pl['position']
                                notelist = track_pl['notelist']
                                for cvpj_note in notelist:
                                    onlineseq_note = {
                                        "1": int(cvpj_note['key']+60),
                                        "2": float2int(cvpj_note['position']+basepos),
                                        "3": float2int(cvpj_note['duration']),
                                        "4": onlineseqnum,
                                        "5": float2int(data_values.get_value(cvpj_note, 'vol', 1.0))
                                        }
                                    onlineseqdata[2].append(onlineseq_note)

                            cvpjid_onlineseqid[trackid] = onlineseqnum

        if 'automation' in projJ:
            cvpj_autodata = projJ['automation']
            for autogroup in cvpj_autodata:
                autogroupdata = cvpj_autodata[autogroup]
                for autoname in autogroupdata:
                    s_autodata = autogroupdata[autoname]
                    if [autogroup, autoname] == ['main', 'bpm']: create_markers(s_autodata, 0, 0)
                    if [autogroup, autoname] == ['main', 'vol']: create_markers(s_autodata, 0, 8)
                    if autogroup == 'track': 
                        for trackautodata in s_autodata:
                            s_trackautodata = s_autodata[trackautodata]
                            if autoname in cvpjid_onlineseqid:
                                onlineseqid = cvpjid_onlineseqid[autoname]
                                if trackautodata == 'vol': create_markers(s_trackautodata, onlineseqid, 1)
                                if trackautodata == 'pan': create_markers(s_trackautodata, onlineseqid, 2)

        protobuf_typedef = {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '3': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'message', 'message_typedef': {'1': {'type': 'fixed32', 'name': ''}, '10': {'type': 'int', 'name': ''}, '15': {'type': 'bytes', 'name': ''}}, 'name': ''}}, 'name': ''}}, 'name': ''}, '2': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '3': {'type': 'fixed32', 'name': ''}, '4': {'type': 'int', 'name': ''}, '5': {'type': 'fixed32', 'name': ''}, '2': {'type': 'fixed32', 'name': ''}}, 'name': ''}, '3': {'type': 'message', 'message_typedef': {'1': {'type': 'fixed32', 'name': ''}, '4': {'type': 'fixed32', 'name': ''}, '5': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}, '3': {'type': 'int', 'name': ''}}, 'name': ''}}

        for num in sorted(glob_markerdata):
            for markdata in glob_markerdata[num]:
                onlineseqdata[3].append(markdata)

        with open(output_file, "wb") as fileout:
            fileout.write(blackboxprotobuf.encode_message(onlineseqdata,protobuf_typedef))