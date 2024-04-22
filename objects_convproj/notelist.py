# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import xtramath
from objects_convproj import autopoints

def calc_tracker_pitch(pitch, speed):
    return (pitch/5)*((speed/6)*1.3)

class pitchmod:
    def __init__(self, c_note):
        self.current_pitch = 0
        self.start_note = c_note
        self.porta_target = c_note
        self.pitch_change = 1
        self.slide_data = {}

    def slide_tracker_porta_targ(self, note):
        self.porta_target = note

    def slide_tracker_porta(self, pos, pitch, speed):
        if pitch != 0: self.pitch_change = pitch*1.5
        pitch_change = calc_tracker_pitch(self.pitch_change, speed)
        self.slide_data[pos] = [1.0, 'porta', pitch_change, self.porta_target]

    def slide_tracker_up(self, pos, pitch, speed):
        if pitch != 0: self.pitch_change = pitch
        pitch_change = calc_tracker_pitch(self.pitch_change, speed)
        self.slide_data[pos] = [1.0, 'slide_c', pitch_change, self.porta_target]

    def slide_tracker_down(self, pos, pitch, speed):
        if pitch != 0: self.pitch_change = pitch
        pitch_change = calc_tracker_pitch(self.pitch_change, speed)
        self.slide_data[pos] = [1.0, 'slide_c', -pitch_change, self.porta_target]

    def slide_note(self, pos, pitch, dur):
        self.slide_data[pos] = [dur, 'slide_n', dur, pitch]

    def to_pointdata(self):
        outslide = []

        prevpos = -10000
        slide_list = []
        for slidepart in self.slide_data:
            slide_list.append([slidepart]+self.slide_data[slidepart])

        for index, slidepart in enumerate(slide_list):
            if index != 0:
                slidepart_prev = slide_list[index-1]
                minval = min(slidepart[0]-slidepart_prev[0], slidepart_prev[1])
                mulval = minval/slidepart_prev[1] if slidepart_prev[1] != 0 else 1
                slidepart_prev[1] = minval
                if slidepart_prev[2] != 'slide_n': 
                    slidepart_prev[3] = slidepart_prev[3]*mulval

        out_blocks = []

        cur_pitch = self.start_note

        for slidepart in slide_list:

            output_blk = False

            if slidepart[2] == 'slide_c': 
                cur_pitch += slidepart[3]
                output_blk = True

            if slidepart[2] == 'slide_n': 
                partslide = slidepart[1]/slidepart[3] if slidepart[3] != 0 else 1
                cur_pitch += (slidepart[4]-cur_pitch)*partslide
                output_blk = True
                
            if slidepart[2] == 'porta': 
                max_dur = min(abs(cur_pitch-slidepart[4]), slidepart[3])
                if cur_pitch > slidepart[4]: 
                    cur_pitch -= max_dur
                    output_blk = True
                if cur_pitch < slidepart[4]: 
                    cur_pitch += max_dur
                    output_blk = True
                slidepart[1] *= max_dur/slidepart[3]

            if output_blk: out_blocks.append([slidepart[0], slidepart[1], cur_pitch-self.start_note])

        islinked = False
        prevpos = -10000
        prevval = 0

        out_pointdata = []

        for slidepart in out_blocks:
            islinked = slidepart[0]-prevpos == slidepart[1]
            if not islinked: out_pointdata.append([slidepart[0], prevval])
            out_pointdata.append([slidepart[0]+slidepart[1], slidepart[2]])
            prevval = slidepart[2]
            prevpos = slidepart[0]

        return out_pointdata

    def to_points(self, notelist_obj):
        pointdata = self.to_pointdata()
        for spoint in pointdata:
            autopoints_obj = notelist_obj.last_add_auto('pitch')
            autopoints_obj.pos = spoint[0]
            autopoints_obj.value = spoint[1]

class cvpj_notelist:
    __slots__ = ['nl','time_ppq','time_float','used_inst']

    def __init__(self, time_ppq, time_float):
        self.nl = []
        self.time_ppq = time_ppq
        self.time_float = time_float
        self.used_inst = []

    def __eq__(self, nlo):
        nl_same = self.nl == nlo.nl
        time_ppq_same = self.time_ppq == nlo.time_ppq
        time_float_same = self.time_float == nlo.time_float
        return nl_same and time_ppq_same and time_float_same

    def clear(self):
        self.nl = []
        self.used_inst = []

    def inst_split(self):
        out_nl_inst = {}
        for t_pos, t_dur, t_key, t_vol, t_inst, t_extra, t_auto, t_slide in self.nl:
            if t_inst != None:
                if t_inst not in out_nl_inst: 
                    notelist_obj = cvpj_notelist(self.time_ppq, self.time_float)
                    notelist_obj.used_inst = [t_inst]
                    out_nl_inst[t_inst] = notelist_obj
                out_nl_inst[t_inst].nl.append([t_pos, t_dur, t_key, t_vol, None, t_extra, t_auto, t_slide])
        return out_nl_inst

    def change_timings(self, time_ppq, time_float):
        for cn in self.nl:
            cn[0] = xtramath.change_timing(self.time_ppq, time_ppq, time_float, cn[0])
            cn[1] = xtramath.change_timing(self.time_ppq, time_ppq, time_float, cn[1])
            if cn[6] != None:
                for t in cn[6]:
                    cn[6][t].change_timings(time_ppq, time_float)
            if cn[7] != None:
                for sn in cn[7]:
                    sn[0] = xtramath.change_timing(self.time_ppq, time_ppq, time_float, sn[0])
                    sn[1] = xtramath.change_timing(self.time_ppq, time_ppq, time_float, sn[1])

        self.time_ppq = time_ppq
        self.time_float = time_float

    def add_r(self, t_pos, t_dur, t_key, t_vol, t_extra):
        self.nl.append([t_pos, t_dur, [t_key], t_vol, None, t_extra, None, None])

    def add_r_multi(self, t_pos, t_dur, m_keys, t_vol, t_extra):
        self.nl.append([t_pos, t_dur, m_keys, t_vol, None, t_extra, None, None])

    def add_m(self, t_inst, t_pos, t_dur, t_key, t_vol, t_extra):
        self.nl.append([t_pos, t_dur, [t_key], t_vol, t_inst, t_extra, None, None])
        if t_inst != None: 
            if t_inst not in self.used_inst: self.used_inst.append(t_inst)

    def add_m_multi(self, t_inst, t_pos, t_dur, m_keys, t_vol, t_extra):
        self.nl.append([t_pos, t_dur, m_keys, t_vol, t_inst, t_extra, None, None])
        if t_inst != None: 
            if t_inst not in self.used_inst: self.used_inst.append(t_inst)

    def last_add_auto(self, a_type):
        if self.nl != []:
            notedata = self.nl[-1]
            if notedata[6] == None: notedata[6] = {}
            if a_type not in notedata[6]: notedata[6][a_type] = autopoints.cvpj_autopoints(self.time_ppq, self.time_float, 'float')
            return notedata[6][a_type].add_point()

    def last_add_slide(self, t_pos, t_dur, t_key, t_vol, t_extra):
        if self.nl != []:
            notedata = self.nl[-1]
            if t_vol == None: t_vol = notedata[3]
            if notedata[7] == None: notedata[7] = []
            notedata[7].append([t_pos, t_dur, t_key, t_vol, t_extra])

    def last_add_vol(self, i_val):
        if self.nl != []:
            self.nl[-1][3] = i_val

    def last_add_extra(self, i_name, i_val):
        if self.nl != []:
            if self.nl[-1][5] == None: self.nl[-1][5] = {}
            self.nl[-1][5][i_name] = i_val

    def last_extend_pos(self, endpos):
        if self.nl != []: self.nl[-1][1] = endpos-self.nl[-1][0]

    def last_extend(self, dur):
        if self.nl != []: self.nl[-1][1] += dur

    def auto_add_slide(self, t_inst, t_pos, t_dur, t_key, t_vol, t_extra):
        if self.nl != []:
            notedata = self.nl[-1]
            for c, nn in enumerate(self.nl):
                nn_pos = nn[0]
                nn_dur = nn[1]
                nn_key = nn[2]
                nn_inst = nn[4]
                if nn_pos <= t_pos < nn_pos+nn_dur and t_inst == nn_inst:
                    sn_pos = t_pos - nn_pos 
                    sn_key = t_key
                    if nn[7] == None: nn[7] = []
                    nn[7].append([sn_pos, t_dur, sn_key, t_vol, t_extra])

    def notesfound(self):
        return self.nl != []

    def get_dur(self):
        duration_final = 0
        for note in self.nl:
            noteendpos = note[0]+note[1]
            if duration_final < noteendpos: duration_final = noteendpos
        return duration_final

    def get_start_end(self):
        duration_final = 0
        position_final = 100000000000000
        for note in self.nl:
            notestartpos = note[0]
            noteendpos = note[0]+note[1]
            if duration_final < noteendpos: duration_final = noteendpos
            if note[0] < position_final: position_final = note[0]
        return position_final, duration_final

    def edit_move(self, pos):
        new_nl = []
        for new_n in self.nl.copy():
            new_n[0] += pos
            if new_n[0] >= 0: new_nl.append(new_n)
        self.nl = new_nl

    def edit_move_minus(self, pos):
        for n in self.nl: n[0] += pos

    def edit_trim(self, pos):
        new_nl = []
        for new_n in self.nl.copy():
            if new_n[0] < pos: new_nl.append(new_n)
        self.nl = new_nl

    def edit_trimmove(self, startat, endat):
        if endat != None: self.edit_trim(endat)
        if startat != None: self.edit_move(-startat)

    def sort(self):
        t_nl_bsort = {}
        t_nl_sorted = {}
        new_nl = []
        for n in self.nl:
            if n[0] not in t_nl_bsort: t_nl_bsort[n[0]] = []
            t_nl_bsort[n[0]].append(n)
        t_nl_sorted = dict(sorted(t_nl_bsort.items(), key=lambda item: item[0]))
        for p in t_nl_sorted:
            for note in t_nl_sorted[p]: new_nl.append(note)
        self.nl = new_nl

    def notemod_conv(self):
        old_nl = self.nl

        for index, note in enumerate(self.nl):
            noteautopitch_exists = note[6] != None
            noteslide_exists = note[7] != None

            if noteslide_exists == True and noteautopitch_exists == False:
                pointsdata = pitchmod(note[2][0])
                for slidenote in note[7]:
                    pointsdata.slide_note(slidenote[0], slidenote[2], slidenote[1])
                nmp = pointsdata.to_pointdata()

                self.nl[index][6] = {}
                self.nl[index][6]['pitch'] = autopoints.cvpj_autopoints(self.time_ppq, self.time_float, 'float')
                for nmps in nmp:
                    autopoint = self.nl[index][6]['pitch'].add_point()
                    autopoint.pos = nmps[0]
                    autopoint.value = nmps[1]

            if noteslide_exists == False and noteautopitch_exists == True:
                if 'pitch' in note[6]:
                    pitchauto = note[6]['pitch']
                    pitchauto.remove_instant()
                    pitchblocks = pitchauto.blocks()
                    if not note[7]: note[7] = []
                    maxnote = max(note[2])
                    for pb in pitchblocks:
                        note[7].append([pb[0], pb[1], pb[2]+maxnote, note[3], {}])

    def last_arpeggio(self, notes):
        if self.nl != []:
            notedata = self.nl[-1]
            key = notedata[2]
            outnotes = []
            for n in notes:
                if not outnotes: outnotes.append(n)
                elif outnotes[-1] != n: outnotes.append(n)
            counts = {}
            for i in outnotes: counts[i] = counts.get(i, 0) + 1
            isduped = max([x for v, x in counts.items()])>1
            if not isduped:
                key = notedata[2][0]
                notedata[2] = [x+notedata[2][0] for x in outnotes]

    def add_instpos(self, instlocs):
        if len(instlocs) == 0: 
            pass
        if len(instlocs) == 1: 
            inst = instlocs[0][1]
            for x in self.nl: x[4] = inst
        elif len(instlocs) == 2: 
            p_inst, a_pos, a_inst = instlocs[0][1], instlocs[1][0], instlocs[1][1]
            for x in self.nl: x[4] = a_inst if a_pos >= x[0] else p_inst
        else: 
            rangelist = [x[0] for x in instlocs.copy()]+[self.get_dur()]
            instlist = [x[1] for x in instlocs]
            rangenum = 0
            for x in self.nl:
                while x[0] >= rangelist[rangenum+1]: rangenum += 1
                x[4] = instlist[rangenum]



    def iter(self):
        for note in self.nl:
            t_pos, t_dur, t_keys, t_vol, t_inst, t_extra, t_auto, t_slide = note
            yield t_pos, t_dur, t_keys, t_vol, t_inst, t_extra, t_auto, t_slide

    def to_cvpj(self):
        self.sort()
        cvpj_out = []
        for note in self.nl:

            for keynum in note[2]:
                note_data = {}
                note_data['position'] = (note[0]/self.time_ppq)*4
                note_data['duration'] = (note[1]/self.time_ppq)*4
                note_data['key'] = keynum
                if note[3] != None: note_data['vol'] = note[3]
                if note[4] != None: note_data['instrument'] = note[4]
                if note[5] != None: 
                    for key, value in note[5].items(): note_data[key] = value
                if note[6] != None: 
                    if 'notemod' not in note_data: note_data['notemod'] = {}
                    if 'auto' not in note_data['notemod']: note_data['notemod']['auto'] = {}
                    for key, value in note[6].items():
                        note_data['notemod']['auto'][key] = value.to_cvpj()
                if note[7] != None: 
                    if 'notemod' not in note_data: note_data['notemod'] = {}
                    if 'slide' not in note_data['notemod']: note_data['notemod']['slide'] = []
                    note_data['notemod']['slide'] = []
                    for snb in note[7]:
                        slidenote = {}
                        slidenote['position'] = (snb[0]/self.time_ppq)*4
                        slidenote['duration'] = (snb[1]/self.time_ppq)*4
                        slidenote['key'] = snb[2]
                        if snb[3] != None: slidenote['vol'] = snb[3]
                        if snb[4] != None:
                            for key, value in snb[4].items(): slidenote[key] = value
                        note_data['notemod']['slide'].append(slidenote)
                cvpj_out.append(note_data)
        return cvpj_out
