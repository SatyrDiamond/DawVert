# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_output
import json
import struct
import blackboxprotobuf
from objects_file import proj_onlineseq
from functions import data_values
from objects import idvals

def create_auto(project_obj, convproj_obj, os_target, os_param, autoloc, mul):
    auto_found, auto_points = convproj_obj.automation.get_autopoints(autoloc)

    if auto_found:
        for auto_point in auto_points.iter():
            os_marker = proj_onlineseq.onlineseq_marker(None)
            os_marker.pos = auto_point.pos
            os_marker.value = auto_point.value*mul
            os_marker.type = 0 if auto_point.type == 'instant' else 1
            os_marker.id = os_target
            os_marker.param = os_param
            project_obj.markers.append(os_marker)

class output_onlineseq(plugin_output.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'output'
    def getshortname(self): return 'onlineseq'
    def gettype(self): return 'r'
    def plugin_archs(self): return None
    def getdawinfo(self, dawinfo_obj): 
        dawinfo_obj.name = 'Online Sequencer'
        dawinfo_obj.file_ext = 'sequence'
        dawinfo_obj.auto_types = ['nopl_points']
        dawinfo_obj.track_nopl = True
        dawinfo_obj.plugin_included = ['midi','native-onlineseq','universal:synth-osc']
    def parse(self, convproj_obj, output_file):

        convproj_obj.change_timings(4, True)

        project_obj = proj_onlineseq.onlineseq_project()
        project_obj.tempo = convproj_obj.params.get('bpm', 120).value

        idvals_onlineseq_inst = idvals.idvals('data_idvals/onlineseq_map_midi.csv')
        repeatedolinst = {}

        for trackid, track_obj in convproj_obj.iter_track():
            onlineseqinst = 43
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
            onlineseqnum = int(onlineseqinst + repeatedolinst[onlineseqinst]*10000)

            iparams = proj_onlineseq.onlineseq_inst_param(None)
            iparams.vol = track_obj.params.get('vol', 1).value
            iparams.pan = track_obj.params.get('pan', 1).value

            if track_obj.visual.name: iparams.name = track_obj.visual.name

            for t_pos, t_dur, t_keys, t_vol, t_inst, t_extra, t_auto, t_slide in track_obj.placements.notelist.nl:
                for t_key in t_keys:
                    onlineseq_note = [int(t_key+60),t_pos,t_dur,onlineseqnum,t_vol]
                    project_obj.notes.append(onlineseq_note)

            project_obj.params[onlineseqnum] = iparams

            create_auto(project_obj, convproj_obj, onlineseqnum, 1, ['track', trackid, 'vol'], 1)
            create_auto(project_obj, convproj_obj, onlineseqnum, 2, ['track', trackid, 'pan'], 1)
            create_auto(project_obj, convproj_obj, onlineseqnum, 11, ['track', trackid, 'pitch'], 100)

        create_auto(project_obj, convproj_obj, 0, 0, ['main', 'bpm'], 1)
        create_auto(project_obj, convproj_obj, 0, 8, ['master', 'vol'], 1)

        project_obj.save_to_file(output_file)