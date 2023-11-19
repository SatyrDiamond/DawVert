# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

class notelist:
    __slots__ = ['nl','ppq','used_inst']

    def __init__(self, ppq, in_notelist):
        self.nl = []
        self.ppq = ppq
        self.used_inst = []
        if in_notelist != None:
            for cn in in_notelist:
                cvpj_note = cn.copy()
                t_pos = cvpj_note['position']
                t_dur = cvpj_note['duration']
                t_key = cvpj_note['key']
                t_vol = cvpj_note['vol'] if 'vol' in cvpj_note else None
                t_inst = cvpj_note['instrument'] if 'instrument' in cvpj_note else None

                del cvpj_note['position']
                del cvpj_note['duration']
                del cvpj_note['key']
                if t_vol != None: del cvpj_note['vol']
                if t_inst != None: del cvpj_note['instrument']
                t_extra = cvpj_note
                self.add_m(t_inst, t_pos, t_dur, t_key, t_vol, t_extra)

    def add_r(self, t_pos, t_dur, t_key, t_vol, t_extra):
        self.nl.append([t_pos, t_dur, t_key, t_vol, None, t_extra, None, None])

    def add_m(self, t_inst, t_pos, t_dur, t_key, t_vol, t_extra):
        self.nl.append([t_pos, t_dur, t_key, t_vol, t_inst, t_extra, None, None])
        if t_inst != None: 
            if t_inst not in self.used_inst: self.used_inst.append(t_inst)

    def num_add_auto(self, i_num, a_type, p_pos, p_val, p_type, p_tension):
        if self.nl != []:
            notedata = self.nl[i_num]
            if notedata[6] == None: notedata[6] = {}
            if a_type not in notedata[6]: notedata[6][a_type] = []
            notedata[6][a_type].append([p_pos, p_val, p_type, p_tension])

    def last_add_auto(self, a_type, p_pos, p_val, p_type, p_tension):
        if self.nl != []:
            notedata = self.nl[-1]
            if notedata[6] == None: notedata[6] = {}
            if a_type not in notedata[6]: notedata[6][a_type] = []
            notedata[6][a_type].append([p_pos, p_val, p_type, p_tension])

    def last_add_slide(self, t_pos, t_dur, t_key, t_vol, t_extra):
        if self.nl != []:
            notedata = self.nl[-1]
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




    def get_dur(self):
        duration_final = 0
        for note in self.nl:
            noteendpos = note[0]+note[1]
            if duration_final < noteendpos: duration_final = noteendpos
        return duration_final




    def edit_move(self, pos):
        new_nl = []
        for n in self.nl.copy():
            new_n[0] += pos
            if new_n[0] >= 0: new_nl.append()
        self.nl = new_nl

    def edit_move_minus(self, pos):
        for n in self.nl: n[0] += pos

    def edit_trim(self, pos):
        new_nl = []
        for n in self.nl.copy():
            if new_n[0] < pos: new_nl.append()
        self.nl = new_nl

    def edit_trimmove(self, startat, endat):
        if endat != None: self.trim(endat)
        if startat != None: self.move(-startat)

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

    def to_cvpj(self):
        self.sort()
        cvpj_out = []
        for note in self.nl:
            note_data = {}
            note_data['position'] = (note[0]/self.ppq)*4
            note_data['duration'] = (note[1]/self.ppq)*4
            note_data['key'] = note[2]
            if note[3] != None: note_data['vol'] = note[3]
            if note[4] != None: note_data['instrument'] = note[4]
            if note[5] != None: 
                for key, value in note[5].items(): note_data[key] = value
            if note[6] != None: 
                if 'notemod' not in note_data: note_data['notemod'] = {}
                if 'auto' not in note_data['notemod']: note_data['notemod']['auto'] = {}
                for key, value in note[6].items():
                    note_data['notemod']['auto'][key] = []
                    for autod in value:
                        pointJ = {}
                        pointJ['position'] = (autod[0]/self.ppq)*4
                        pointJ['value'] = autod[1]
                        pointJ['type'] = autod[2] if autod[2] != None else 'normal'
                        if autod[3] != None: pointJ['tension'] = autod[3]
                        note_data['notemod']['auto'][key].append(pointJ)
            if note[7] != None: 
                if 'notemod' not in note_data: note_data['notemod'] = {}
                if 'slide' not in note_data['notemod']: note_data['notemod']['slide'] = []
                note_data['notemod']['slide'] = []
                for snb in note[7]:
                    slidenote = {}
                    slidenote['position'] = (snb[0]/self.ppq)*4
                    slidenote['duration'] = (snb[1]/self.ppq)*4
                    slidenote['key'] = snb[2]
                    if snb[3] != None: slidenote['vol'] = snb[3]
                    if snb[4] != None:
                        for key, value in snb[4].items(): slidenote[key] = value
                    note_data['notemod']['slide'].append(slidenote)

            cvpj_out.append(note_data)
        return cvpj_out

