# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects import convproj_placements
from objects_convproj import fileref
from objects_convproj import params
from objects_convproj import tracks
from objects_convproj import visual
from objects_convproj import sends
from objects_convproj import notelist
from objects_convproj import stretch

import copy

class cvpj_nle:
    __slots__ = ['visual','notelist']
    def __init__(self, time_ppq, time_float):
        self.visual = visual.cvpj_visual()
        self.notelist = notelist.cvpj_notelist(time_ppq, time_float)

class cvpj_sle:
    __slots__ = ['visual','sampleref','audiomod','pan','vol','enabled','pitch','fxrack_channel','stretch']
    def __init__(self):
        self.visual = visual.cvpj_visual()
        self.sampleref = ''
        self.audiomod = {}
        self.pan = 0
        self.vol = 1
        self.enabled = True
        self.pitch = 0
        self.fxrack_channel = -1
        self.stretch = stretch.cvpj_stretch()

    def __eq__(self, sle_obj):
        s_sampleref = self.sampleref == sle_obj.sampleref
        s_audiomod = self.audiomod == sle_obj.audiomod
        s_pan = self.pan == sle_obj.pan
        s_vol = self.vol == sle_obj.vol
        s_enabled = self.enabled == sle_obj.enabled
        s_pitch = self.pitch == sle_obj.pitch
        s_fxrack_channel = self.fxrack_channel == sle_obj.fxrack_channel
        s_stretch = self.stretch == sle_obj.stretch

        return s_sampleref and s_audiomod and s_pan and s_vol and s_enabled and s_pitch and s_fxrack_channel and s_stretch

class cvpj_midiport:
    def __init__(self):
        self.in_enabled = False
        self.in_chan = -1
        self.in_fixedvelocity = -1

        self.out_enabled = False
        self.out_chan = -1
        self.out_patch = 0
        self.out_bank = 0
        self.out_fixedvelocity = -1
        self.out_fixednote = -1
        self.drum_mode = False

        self.basevelocity = 63

class cvpj_instrument:
    __slots__ = ['visual','params','datavals','midi','fxrack_channel','fxslots_notes','fxslots_audio','pluginid']
    def __init__(self):
        self.visual = visual.cvpj_visual()
        self.params = params.cvpj_paramset()
        self.datavals = params.cvpj_datavals()
        self.midi = cvpj_midiport()
        self.fxrack_channel = -1
        self.fxslots_notes = []
        self.fxslots_audio = []
        self.pluginid = ''

class cvpj_return_track:
    __slots__ = ['visual','visual_ui','params','datavals','fxslots_notes','fxslots_audio','sends']
    def __init__(self):
        self.visual = visual.cvpj_visual()
        self.visual_ui = visual.cvpj_visual_ui()
        self.params = params.cvpj_paramset()
        self.datavals = params.cvpj_datavals()
        self.fxslots_notes = []
        self.fxslots_audio = []
        self.sends = sends.cvpj_sends()

class cvpj_lane:
    def __init__(self, track_type, time_ppq, time_float, uses_placements, is_indexed):
        self.visual = visual.cvpj_visual()
        self.visual_ui = visual.cvpj_visual_ui()
        self.params = params.cvpj_paramset()
        self.datavals = params.cvpj_datavals()
        self.placements = convproj_placements.cvpj_placements(time_ppq, time_float, uses_placements, is_indexed)

class cvpj_track:
    __slots__ = ['time_ppq','time_float','uses_placements','lanes','is_indexed','type','is_laned','inst_pluginid','datavals','visual','visual_ui','params','midi','fxrack_channel','fxslots_notes','fxslots_audio','placements','sends','group','returns','notelist_index']
    def __init__(self, track_type, time_ppq, time_float, uses_placements, is_indexed):
        self.time_ppq = time_ppq
        self.time_float = time_float
        self.uses_placements = uses_placements
        self.is_indexed = is_indexed
        self.type = track_type
        self.is_laned = False
        self.lanes = {}
        self.inst_pluginid = ''
        self.visual = visual.cvpj_visual()
        self.visual_ui = visual.cvpj_visual_ui()
        self.params = params.cvpj_paramset()
        self.datavals = params.cvpj_datavals()
        self.midi = cvpj_midiport()
        self.fxrack_channel = -1
        self.fxslots_notes = []
        self.fxslots_audio = []
        self.sends = sends.cvpj_sends()
        self.placements = convproj_placements.cvpj_placements(self.time_ppq, self.time_float, self.uses_placements, self.is_indexed)
        self.group = None
        self.returns = {}
        self.notelist_index = {}

    def get_midi(self, convproj_obj):
        midi_bank = 0
        midi_inst = 0
        midi_drum = False

        is_found = False

        plugin_found, plugin_obj = convproj_obj.get_plugin(self.inst_pluginid)
        if plugin_found: 
            if plugin_obj.check_wildmatch('midi', None):
                midi_bank = plugin_obj.datavals.get('bank', 0)
                midi_inst = plugin_obj.datavals.get('patch', 0)
                if midi_bank >= 128:
                    midi_bank -= 128
                    midi_drum = True
                is_found = True

            if plugin_obj.check_wildmatch('soundfont2', None):
                midi_bank = plugin_obj.datavals.get('bank', 0)
                midi_inst = plugin_obj.datavals.get('patch', 0)
                if midi_bank >= 128:
                    midi_bank -= 128
                    midi_drum = True
                is_found = True

        if (not is_found) and self.midi.out_enabled:
            midi_bank = self.midi.out_bank
            midi_inst = self.midi.out_patch
            midi_drum = self.midi.drum_mode

        return is_found, midi_bank, midi_inst, midi_drum

    def add_return(self, returnid):
        self.returns[returnid] = cvpj_track('return', self.time_ppq, self.time_float, False, False)
        return self.returns[returnid]

    def make_base(self):
        c_obj = cvpj_track(self.type,self.time_ppq,self.time_float,self.uses_placements,self.is_indexed)
        c_obj.time_ppq = self.time_ppq
        c_obj.time_float = self.time_float
        c_obj.uses_placements = self.uses_placements
        c_obj.is_indexed = self.is_indexed
        c_obj.type = self.type
        c_obj.is_laned = False
        c_obj.lanes = {}
        c_obj.inst_pluginid = self.inst_pluginid
        c_obj.visual = copy.deepcopy(self.visual)
        c_obj.visual_ui = copy.deepcopy(self.visual_ui)
        c_obj.params = copy.deepcopy(self.params)
        c_obj.datavals = copy.deepcopy(self.datavals)
        c_obj.midi = copy.deepcopy(self.midi)
        c_obj.fxrack_channel = self.fxrack_channel
        c_obj.fxslots_notes = self.fxslots_notes
        c_obj.fxslots_audio = self.fxslots_audio
        c_obj.sends = copy.deepcopy(self.sends)
        c_obj.placements = convproj_placements.cvpj_placements(self.time_ppq, self.time_float, self.uses_placements, self.is_indexed)
        c_obj.group = self.group
        c_obj.returns = self.returns
        c_obj.notelist_index = self.notelist_index
        return c_obj

    def make_base_inst(self, inst_obj):
        track_obj = self.make_base()
        track_obj.inst_pluginid = inst_obj.pluginid
        #track_obj.visual = copy.deepcopy(inst_obj.visual)
        track_obj.params = copy.deepcopy(inst_obj.params)
        track_obj.datavals = copy.deepcopy(inst_obj.datavals)
        track_obj.midi = copy.deepcopy(inst_obj.midi)
        track_obj.fxrack_channel = inst_obj.fxrack_channel
        track_obj.fxslots_notes = inst_obj.fxslots_notes
        track_obj.fxslots_audio = inst_obj.fxslots_audio
        return track_obj

    def add_notelistindex(self, i_id):
        self.notelist_index[i_id] = cvpj_nle(self.time_ppq, self.time_float)
        return self.notelist_index[i_id]

    def add_lane(self, laneid):
        self.is_laned = True
        if laneid not in self.lanes: 
            self.lanes[laneid] = cvpj_lane(self.type, self.time_ppq, self.time_float, self.uses_placements, self.is_indexed)
        return self.lanes[laneid]

    def change_timings(self, time_ppq, time_float):
        self.placements.change_timings(time_ppq, time_float)
        for laneid, lane_obj in self.lanes.items():
            lane_obj.placements.change_timings(time_ppq, time_float)
        self.time_float = time_float
        self.time_ppq = time_ppq

    def add_return(self, returnid):
        return_obj = cvpj_return_track()
        self.returns[returnid] = return_obj
        return return_obj

    def iter_return(self):
        for returnid, return_obj in self.returns.items():
            yield returnid, return_obj
