# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects import convproj
from functions import xtramath
import copy

from objects_convproj import stretch
from objects_convproj import visual
from objects_convproj import autopoints
from objects_convproj import notelist

def step2sec(i_value, i_bpm): return (i_value/8)*(120/i_bpm)
def sec2step(i_value, i_bpm): return (i_value*8)/(120/i_bpm)

class cvpj_placements:
    __slots__ = ['data_notes','data_audio','data_audio_nested','time_ppq','time_float','uses_placements','is_indexed']
    def __init__(self, time_ppq, time_float, uses_placements, is_indexed):
        self.uses_placements = uses_placements
        self.is_indexed = is_indexed
        self.time_ppq = time_ppq
        self.time_float = time_float
        self.data_notes = []
        self.data_audio = []
        self.data_audio_nested = []

    def sort_notes(self):
        ta_bsort = {}
        ta_sorted = {}
        new_a = []
        for n in self.data_notes:
            if n.position not in ta_bsort: ta_bsort[n.position] = []
            ta_bsort[n.position].append(n)
        ta_sorted = dict(sorted(ta_bsort.items(), key=lambda item: item[0]))
        for p in ta_sorted:
            for note in ta_sorted[p]: new_a.append(note)
        self.data_notes = new_a

    def sort_audio(self):
        ta_bsort = {}
        ta_sorted = {}
        new_a = []
        for n in self.data_audio:
            if n.position not in ta_bsort: ta_bsort[n.position] = []
            ta_bsort[n.position].append(n)
        ta_sorted = dict(sorted(ta_bsort.items(), key=lambda item: item[0]))
        for p in ta_sorted:
            for note in ta_sorted[p]: new_a.append(note)
        self.data_audio = new_a

    def get_dur(self):
        duration_final = 0
        for pl in self.data_notes:
            if pl.duration == 0: pl.duration = pl.notelist.get_dur()
            pl_end = pl.position+pl.duration
            if duration_final < pl_end: duration_final = pl_end
        for pl in self.data_audio:
            pl_end = pl.position+pl.duration
            if duration_final < pl_end: duration_final = pl_end
        return duration_final

    def change_seconds(self, is_seconds, bpm):
        for pl in self.data_notes:
            pl.position = step2sec(pl.position, bpm) if is_seconds else sec2step(pl.position, bpm)
            pl.duration = step2sec(pl.duration, bpm) if is_seconds else sec2step(pl.duration, bpm)
            
        for pl in self.data_audio: 
            pl.position = step2sec(pl.position, bpm) if is_seconds else sec2step(pl.position, bpm)
            pl.duration = step2sec(pl.duration, bpm) if is_seconds else sec2step(pl.duration, bpm)

    def remove_cut(self):
        for x in self.data_notes: 
            if x.cut_type == 'cut':
                c_start = x.cut_data['start'] if 'start' in x.cut_data else 0
                x.notelist.edit_trimmove(c_start, x.duration)

    def remove_loops_s(self, input_pl, out__placement_loop):
        new_data_notes = []
        for notespl_obj in input_pl: 
            if notespl_obj.cut_type in ['loop', 'loop_off', 'loop_adv'] and notespl_obj.cut_type not in out__placement_loop:
                loop_start = notespl_obj.cut_data['start'] if 'start' in notespl_obj.cut_data else 0
                loop_loopstart = notespl_obj.cut_data['loopstart'] if 'loopstart' in notespl_obj.cut_data else 0
                loop_loopend = notespl_obj.cut_data['loopend'] if 'loopend' in notespl_obj.cut_data else x.duration
                for cutpoint in xtramath.cutloop(notespl_obj.position, notespl_obj.duration, loop_start, loop_loopstart, loop_loopend):
                    cutplpl_obj = copy.deepcopy(notespl_obj)
                    cutplpl_obj.position = cutpoint[0]
                    cutplpl_obj.duration = cutpoint[1]
                    cutplpl_obj.cut_type = 'cut'
                    cutplpl_obj.cut_data = {'start': cutpoint[2]}
                    new_data_notes.append(cutplpl_obj)
            else: new_data_notes.append(notespl_obj)
        return new_data_notes

    def remove_loops(self, out__placement_loop):
        self.data_notes = self.remove_loops_s(self.data_notes, out__placement_loop)
        self.data_audio = self.remove_loops_s(self.data_audio, out__placement_loop)

    def add_loops_notes(self):
        old_data_notes = copy.deepcopy(self.data_notes)
        new_data_notes = []
        prevpp = None
        for pl in old_data_notes:
            ipnl = False
            pl_data = pl.fromindex if self.is_indexed else pl.notelist
            if prevpp != None:
                if prevpp[0]==pl.position-pl.duration and prevpp[2]==pl_data and prevpp[1]==pl.duration and pl.cut_type=='none': 
                    ipnl = True
                    if pl.cut_type=='none':
                        new_data_notes[-1].cut_type = 'loop'
                        new_data_notes[-1].cut_data['loopend'] = pl.duration
                    new_data_notes[-1].duration += pl.duration
            if ipnl == False: 
                new_data_notes.append(pl)
            prevpp = [pl.position, pl.duration, pl_data] if pl.cut_type=='none' else None
        return new_data_notes

    def add_loops(self):
        self.data_notes = self.add_loops_notes()

    def iter_notes(self):
        for x in self.data_notes: yield x

    def iter_audio(self):
        for x in self.data_audio: yield x

    def add_notes(self):
        if not self.is_indexed: placement_obj = cvpj_placement_notes(self.time_ppq, self.time_float)
        else: placement_obj = cvpj_placement_index()
        if self.uses_placements:
            self.data_notes.append(placement_obj)
            return placement_obj
        else:
            if not self.data_notes: self.data_notes.append(placement_obj)
            return self.data_notes[0]

    def add_notes_timed(self, time_ppq, time_float):
        if not self.is_indexed: placement_obj = cvpj_placement_notes(time_ppq, time_float)
        else: placement_obj = cvpj_placement_index()
        if self.uses_placements:
            self.data_notes.append(placement_obj)
            return placement_obj
        else:
            if not self.data_notes: self.data_notes.append(placement_obj)
            return self.data_notes[0]

    def add_audio(self):
        if not self.is_indexed: placement_obj = cvpj_placement_audio()
        else: placement_obj = cvpj_placement_index()
        if self.uses_placements:
            self.data_audio.append(placement_obj)
            return placement_obj
        else:
            if not self.data_audio: self.data_audio.append(placement_obj)
            return self.data_audio[0]

    def changestretch(self, convproj_obj, target, tempo):
        if not self.is_indexed: 
            for x in self.data_audio: 
                pos_offset, cut_offset, finalspeed = x.stretch.changestretch(convproj_obj.samplerefs, x.sampleref, target, tempo, self.time_ppq)
                #if 'start' not in x.cut_data: x.cut_data['start'] = 0
                #x.cut_data['start'] += cut_offset
                #x.position += pos_offset
                #x.duration -= pos_offset
                #print(pos_offset, cut_offset, x.cut_type, x.cut_data, '|', end=' ')
                if x.cut_type == 'cut':
                    if 'start' in x.cut_data: x.cut_data['start'] += cut_offset
                if x.cut_type == 'loop':
                    if 'loopend' in x.cut_data: x.cut_data['loopend'] += cut_offset
                    if 'loopstart' in x.cut_data: x.cut_data['loopstart'] += cut_offset

                x.cut_data['start'] -= pos_offset

                #print(pos_offset, cut_offset, x.cut_type, x.cut_data)

    def iter_notes(self):
        for x in self.data_notes: yield x

    def iter_audio(self):
        for x in self.data_audio: yield x

    def iter_audio_nested(self):
        for x in self.data_audio_nested: yield x

    def change_timings(self, time_ppq, time_float):
        for pl in self.data_notes:
            pl.position = xtramath.change_timing(self.time_ppq, time_ppq, time_float, pl.position)
            pl.duration = xtramath.change_timing(self.time_ppq, time_ppq, time_float, pl.duration)
            if not self.is_indexed: pl.notelist.change_timings(time_ppq, time_float)
            for an in ['start', 'loopstart', 'loopend']:
                if an in pl.cut_data: pl.cut_data[an] = xtramath.change_timing(self.time_ppq, time_ppq, time_float, pl.cut_data[an])

        for pl in self.data_audio:
            pl.position = xtramath.change_timing(self.time_ppq, time_ppq, time_float, pl.position)
            pl.duration = xtramath.change_timing(self.time_ppq, time_ppq, time_float, pl.duration)
            for an in ['start', 'loopstart', 'loopend']:
                if an in pl.cut_data: pl.cut_data[an] = xtramath.change_timing(self.time_ppq, time_ppq, time_float, pl.cut_data[an])

        self.time_ppq = time_ppq
        self.time_float = time_float

    def add_inst_to_notes(self, inst):
        for x in self.data_notes:
            x.notelist.used_inst = [inst]
            for n in x.notelist.nl:
                n[4] = inst

    def used_notes(self):
        used_insts = []
        for notespl_obj in self.iter_notes(): used_insts += notespl_obj.notelist.used_inst
        return set(used_insts)

    def inst_split(self):
        splitted_pl = {}
        for notespl_obj in self.iter_notes(): notespl_obj.inst_split(splitted_pl)
        return splitted_pl

    def unindex_notes(self, notelist_index):
        new_data_notes = []
        for indexpl_obj in self.data_notes:
            new_notespl_obj = cvpj_placement_notes(self.time_ppq, self.time_float)
            new_notespl_obj.position = indexpl_obj.position
            new_notespl_obj.duration = indexpl_obj.duration
            new_notespl_obj.cut_type = indexpl_obj.cut_type
            new_notespl_obj.cut_data = indexpl_obj.cut_data
            new_notespl_obj.muted = indexpl_obj.muted

            if indexpl_obj.fromindex in notelist_index:
                nle_obj = notelist_index[indexpl_obj.fromindex]
                new_notespl_obj.notelist = nle_obj.notelist
                new_notespl_obj.visual = nle_obj.visual

            new_data_notes.append(new_notespl_obj)
        self.data_notes = new_data_notes
        self.is_indexed = False

    def unindex_audio(self, sample_index):
        new_data_audio = []
        for indexpl_obj in self.data_audio:
            apl_obj = cvpj_placement_audio()

            if indexpl_obj.fromindex in sample_index:
                sle_obj = sample_index[indexpl_obj.fromindex]
                apl_obj.position = indexpl_obj.position
                apl_obj.duration = indexpl_obj.duration
                apl_obj.cut_type = indexpl_obj.cut_type
                apl_obj.cut_data = indexpl_obj.cut_data
                apl_obj.muted = indexpl_obj.muted
                
                apl_obj.visual = sle_obj.visual
                apl_obj.sampleref = sle_obj.sampleref
                apl_obj.pan = sle_obj.pan
                apl_obj.vol = sle_obj.vol
                apl_obj.pitch = sle_obj.pitch
                apl_obj.fxrack_channel = sle_obj.fxrack_channel
                apl_obj.stretch = sle_obj.stretch
                new_data_audio.append(apl_obj)

        self.data_audio = new_data_audio
        self.is_indexed = False

    def to_indexed_notes(self, existingpatterns, pattern_number):
        self.is_indexed = True
        existingpatterns = []

        new_data_notes = []
        for notepl_obj in self.data_notes:
            nle_data = [notepl_obj.notelist, notepl_obj.visual.name, notepl_obj.visual.color]

            dupepatternfound = None
            for existingpattern in existingpatterns:
                if existingpattern[1] == nle_data: 
                    dupepatternfound = existingpattern[0]
                    break

            if dupepatternfound == None:
                patid = 'm2mi_' + str(pattern_number)
                existingpatterns.append([patid, nle_data])
                dupepatternfound = patid
                pattern_number += 1

            new_index_obj = cvpj_placement_index()
            new_index_obj.position = notepl_obj.position
            new_index_obj.duration = notepl_obj.duration
            new_index_obj.cut_type = notepl_obj.cut_type
            new_index_obj.cut_data = notepl_obj.cut_data
            new_index_obj.fromindex = dupepatternfound
            new_index_obj.muted = notepl_obj.muted
            new_data_notes.append(new_index_obj)

        self.data_notes = new_data_notes
        return existingpatterns, pattern_number

    def to_indexed_audio(self, existingsamples, sample_number):
        new_data_audio = []
        for audiopl_obj in self.data_audio:
            sle_obj = convproj.cvpj_sle()
            sle_obj.visual = audiopl_obj.visual
            sle_obj.sampleref = audiopl_obj.sampleref
            sle_obj.pan = audiopl_obj.pan
            sle_obj.vol = audiopl_obj.vol
            sle_obj.pitch = audiopl_obj.pitch
            sle_obj.fxrack_channel = audiopl_obj.fxrack_channel
            sle_obj.stretch = audiopl_obj.stretch

            dupepatternfound = None
            for existingsample in existingsamples:
                if existingsample[1] == sle_obj: 
                    dupepatternfound = existingsample[0]
                    break

            if dupepatternfound == None:
                patid = 'm2mi_audio_' + str(sample_number)
                existingsamples.append([patid, sle_obj])
                dupepatternfound = patid
                sample_number += 1

            new_index_obj = cvpj_placement_index()
            new_index_obj.position = audiopl_obj.position
            new_index_obj.duration = audiopl_obj.duration
            new_index_obj.cut_type = audiopl_obj.cut_type
            new_index_obj.cut_data = audiopl_obj.cut_data
            new_index_obj.fromindex = dupepatternfound
            new_index_obj.muted = audiopl_obj.muted
            new_data_audio.append(new_index_obj)

        self.data_audio = new_data_audio
        return existingsamples, sample_number

    def add_nested_audio(self):
        placement_obj = cvpj_placement_nested_audio()
        self.data_audio_nested.append(placement_obj)
        return placement_obj

    def remove_nested(self):
        for nestedpl_obj in self.data_audio_nested:
            main_s = nestedpl_obj.cut_data['start'] if 'start' in nestedpl_obj.cut_data else 0
            main_e = nestedpl_obj.duration+main_s
            basepos = nestedpl_obj.position

            #print('PL', end=' ')
            #for x in [main_s, main_e]:
            #    print(str(x).ljust(19), end=' ')
            #print()

            for e in nestedpl_obj.events:
                event_s, event_et = e.position, e.duration
                event_e = e.position+event_et
                event_o = e.cut_data['start'] if 'start' in e.cut_data else 0

                if main_e>=event_s and main_s<=event_e:
                    out_start = max(main_s, event_s)
                    out_end = min(main_e, event_e)

                    if False:
                        print('E ', end='| ')
                        for x in [main_s+event_o, main_e]: print(str(round(x, 4)).ljust(7), end=' ')
                        print('|', end=' ')
                        for x in [event_s, event_e]: print(str(round(x, 4)).ljust(7), end=' ')
                        print('|', end=' ')
                        for x in [out_start, out_end]: print(str(round(x, 4)).ljust(7), end=' ')
                        print('|', end=' ')
                        for x in [event_e]: print(str(round(x, 4)).ljust(7), end=' ')
                        print()

                    cutplpl_obj = copy.deepcopy(e)
                    cutplpl_obj.position = out_start+basepos
                    cutplpl_obj.duration = out_end-out_start
                    self.data_audio.append(cutplpl_obj)


class cvpj_placements_auto:
    __slots__ = ['data','type','time_ppq','time_float','val_type']
    def __init__(self, time_ppq, time_float, val_type):
        self.time_ppq = time_ppq
        self.time_float = time_float
        self.val_type = val_type
        self.data = []

    def add(self, val_type):
        placement_obj = cvpj_placement_auto(self.time_ppq, self.time_float, self.val_type)
        self.data.append(placement_obj)
        return placement_obj

    def change_timings(self, time_ppq, time_float):
        for pl in self.data:
            pl.position = xtramath.change_timing(self.time_ppq, time_ppq, time_float, pl.position)
            pl.duration = xtramath.change_timing(self.time_ppq, time_ppq, time_float, pl.duration)
            pl.data.change_timings(time_ppq, time_float)

        self.time_ppq = time_ppq
        self.time_float = time_float

    def addmul(self, addval, mulval):
        for pl in self.data: pl.data.addmul(addval, mulval)

    def to_one(self, i_min, i_max):
        for pl in self.data: pl.data.to_one(i_min, i_max)

    def from_one(self, i_min, i_max):
        for pl in self.data: pl.data.from_one(i_min, i_max)

    def funcval(self, i_function):
        for pl in self.data: pl.data.funcval(i_function)

    def iter(self):
        for x in self.data: yield x

    def check(self):
        return len(self.data) != 0



def cutloopdata(start, loopstart, loopend):
    cut_data = {}
    if start == 0 and loopstart == 0:
        cut_type = 'loop'
        cut_data['loopend'] = loopend
    elif loopstart == 0:
        cut_type = 'loop_off'
        cut_data['start'] = start
        cut_data['loopend'] = loopend
    else:
        cut_type = 'loop_adv'
        cut_data['start'] = start
        cut_data['loopstart'] = loopstart
        cut_data['loopend'] = loopend
    return cut_type, cut_data

class cvpj_placement_notes:
    __slots__ = ['position','duration','cut_type','cut_data','muted','visual','notelist','time_ppq','time_float']
    def __init__(self, time_ppq, time_float):
        self.position = 0
        self.duration = 0
        self.cut_type = 'none'
        self.cut_data = {}
        self.time_ppq = time_ppq
        self.time_float = time_float
        self.notelist = notelist.cvpj_notelist(time_ppq, time_float)
        self.muted = False
        self.visual = visual.cvpj_visual()

    def cut_loop_data(self, start, loopstart, loopend):
        self.cut_type, self.cut_data = cutloopdata(start, loopstart, loopend)

    def inst_split(self, splitted_pl):
        nl_splitted = self.notelist.inst_split()
        for inst_id, notelist_obj in nl_splitted.items():
            plb_obj = cvpj_placement_notes(self.time_ppq, self.time_float)
            plb_obj.position = self.position
            plb_obj.duration = self.duration
            plb_obj.cut_type = self.cut_type
            plb_obj.cut_data = self.cut_data
            plb_obj.time_ppq = self.time_ppq
            plb_obj.time_float = self.time_float
            plb_obj.notelist = notelist_obj
            plb_obj.muted = self.muted
            plb_obj.visual = self.visual
            if inst_id not in splitted_pl: splitted_pl[inst_id] = []
            splitted_pl[inst_id].append(plb_obj)


class cvpj_placement_audio:
    __slots__ = ['position','duration','cut_type','cut_data','muted','pan','vol','pitch','visual','sampleref','audiomod','fxrack_channel','stretch','fade_in','fade_out']

    def __init__(self):
        self.position = 0
        self.duration = 0
        self.cut_type = 'none'
        self.cut_data = {}
        self.muted = False
        self.pan = 0
        self.vol = 1
        self.pitch = 0
        self.visual = visual.cvpj_visual()
        self.sampleref = ''
        self.audiomod = {}
        self.fxrack_channel = -1
        self.stretch = stretch.cvpj_stretch()
        self.fade_in = {}
        self.fade_out = {}

    def cut_loop_data(self, start, loopstart, loopend):
        self.cut_type, self.cut_data = cutloopdata(start, loopstart, loopend)

class cvpj_placement_index:
    __slots__ = ['position','duration','cut_type','cut_data','muted','visual','fromindex']

    def __init__(self):
        self.position = 0
        self.duration = 0
        self.cut_type = 'none'
        self.cut_data = {}
        self.fromindex = ''
        self.muted = False

    def cut_loop_data(self, start, loopstart, loopend):
        self.cut_type, self.cut_data = cutloopdata(start, loopstart, loopend)

class cvpj_placement_auto:
    __slots__ = ['position','duration','cut_type','cut_data','muted','visual','data']

    def __init__(self, time_ppq, time_float, val_type):
        self.position = 0
        self.duration = 0
        self.cut_type = 'none'
        self.cut_data = {}
        self.data = autopoints.cvpj_autopoints(time_ppq, time_float, val_type)
        self.muted = False
        self.visual = visual.cvpj_visual()

    def cut_loop_data(self, start, loopstart, loopend):
        self.cut_type, self.cut_data = cutloopdata(start, loopstart, loopend)





class cvpj_placement_nested_audio:
    __slots__ = ['position','duration','cut_type','cut_data','visual','events']

    def __init__(self):
        self.position = 0
        self.duration = 0
        self.cut_type = 'none'
        self.cut_data = {}
        self.visual = visual.cvpj_visual()
        self.events = []

    def add(self):
        apl_obj = cvpj_placement_audio()
        self.events.append(apl_obj)
        return apl_obj
