# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_output
import json
import struct
import blackboxprotobuf
from functions import data_values
from objects import idvals

def float2int(value): return struct.unpack("<I", struct.pack("<f", value))[0]

def create_markers(autopoints_obj, inst_id, instparam, mul):
    for autopoint_obj in autopoints_obj.iter():
        markerdata = {}
        posdata = autopoint_obj.pos
        markerdata[1] = float2int(posdata)
        markerdata[2] = instparam
        markerdata[3] = inst_id
        markerdata[4] = float2int(autopoint_obj.value*mul)
        pointtype = autopoint_obj.value
        if autopoint_obj.type == 'normal': markerdata[5] = 1
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
        'auto_nopl': True,
        'track_nopl': True
        }
    def getsupportedplugformats(self): return []
    def getsupportedplugins(self): return ['midi']
    def getfileextension(self): return 'sequence'
    def parse(self, convproj_obj, output_file):
        global glob_markerdata

        convproj_obj.change_timings(4, True)

        tempo = convproj_obj.params.get('bpm', 120).value

        onlineseqdata = {}
        onlineseqdata[1] = {1: int(tempo), 3: []}
        onlineseqdata[2] = []
        onlineseqdata[3] = []

        idvals_onlineseq_inst = idvals.idvals('data_idvals/onlineseq_map_midi.csv')
        repeatedolinst = {}
        cvpjid_onlineseqid = {}
        glob_markerdata = {}

        for trackid, track_obj in convproj_obj.iter_track():
            onlineseqinst = 43
            trackvol = track_obj.params.get('vol', 1).value
            midiinst = None

            plugin_found, plugin_obj = convproj_obj.get_plugin(track_obj.inst_pluginid)
            if plugin_found: 

                if plugin_obj.check_wildmatch('midi', None):
                    midi_bank = plugin_obj.datavals.get('bank', 0)
                    midi_inst = plugin_obj.datavals.get('inst', 0)
                    midiinst = midi_inst if midi_bank != 128 else -1

                if plugin_obj.check_wildmatch('soundfont2', None):
                    midi_bank = plugin_obj.datavals.get('bank', 0)
                    midi_inst = plugin_obj.datavals.get('patch', 0)
                    midiinst = midi_inst if midi_bank != 128 else -1

                if plugin_obj.check_wildmatch('synth-osc', None):
                    if len(plugin_obj.oscs) == 1:
                        s_osc = plugin_obj.oscs[0]
                        if s_osc.shape == 'sine': onlineseqinst = 13
                        if s_osc.shape == 'square': onlineseqinst = 14
                        if s_osc.shape == 'triangle': onlineseqinst = 16
                        if s_osc.shape == 'saw': onlineseqinst = 15
                
                t_instid = idvals_onlineseq_inst.get_idval(str(midiinst), 'outid')
                if t_instid not in ['null', None]: onlineseqinst = int(t_instid)

                if onlineseqinst not in repeatedolinst: repeatedolinst[onlineseqinst] = 0
                else: repeatedolinst[onlineseqinst] += 1 

                onlineseqnum = onlineseqinst + repeatedolinst[onlineseqinst]*10000

                onlseqinst = {}
                onlseqinst[1] = onlineseqnum
                onlseqinst[2] = {1: float2int(trackvol), 10: 1}
                if track_obj.visual.name: onlseqinst[2][15] = track_obj.visual.name
                onlineseqdata[1][3].append(onlseqinst)

                for notespl_obj in track_obj.placements.iter_notes():
                    basepos = notespl_obj.position

                    notespl_obj.notelist.sort()
                    for t_pos, t_dur, t_keys, t_vol, t_inst, t_extra, t_auto, t_slide in notespl_obj.notelist.iter():
                        for t_key in t_keys:
                            onlineseq_note = {
                                "1": int(t_key+60),
                                "2": float2int(t_pos+basepos),
                                "3": float2int(t_dur),
                                "4": onlineseqnum,
                                "5": float2int(t_vol)
                                }
                            onlineseqdata[2].append(onlineseq_note)

                cvpjid_onlineseqid[trackid] = onlineseqnum

        protobuf_typedef = {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '3': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'message', 'message_typedef': {'1': {'type': 'fixed32', 'name': ''}, '10': {'type': 'int', 'name': ''}, '15': {'type': 'bytes', 'name': ''}}, 'name': ''}}, 'name': ''}}, 'name': ''}, '2': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '3': {'type': 'fixed32', 'name': ''}, '4': {'type': 'int', 'name': ''}, '5': {'type': 'fixed32', 'name': ''}, '2': {'type': 'fixed32', 'name': ''}}, 'name': ''}, '3': {'type': 'message', 'message_typedef': {'1': {'type': 'fixed32', 'name': ''}, '4': {'type': 'fixed32', 'name': ''}, '5': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}, '3': {'type': 'int', 'name': ''}}, 'name': ''}}

        for autopath, autopoints_obj in convproj_obj.iter_autopoints():
            if autopath == ['main', 'bpm']: create_markers(autopoints_obj, 0, 0, 1)
            if autopath == ['master', 'vol']: create_markers(autopoints_obj, 0, 8, 1)
            if autopath[0] == 'track': 
                onlineseqid = cvpjid_onlineseqid[autopath[1]]
                if autopath[2] == 'vol': create_markers(autopoints_obj, onlineseqid, 1, 1)
                if autopath[2] == 'pan': create_markers(autopoints_obj, onlineseqid, 2, 1)
                if autopath[2] == 'pitch': create_markers(autopoints_obj, onlineseqid, 11, 100)

        for num in sorted(glob_markerdata):
            for markdata in glob_markerdata[num]:
                onlineseqdata[3].append(markdata)

        with open(output_file, "wb") as fileout:
            fileout.write(blackboxprotobuf.encode_message(onlineseqdata,protobuf_typedef))