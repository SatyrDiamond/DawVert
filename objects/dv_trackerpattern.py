# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from objects_convproj import notelist

t_retg_alg = [['mul', 1], ['minus', 1], ['minus', 2], ['minus', 4], ['minus', 8], ['minus', 16], ['mul', 2/3], ['mul', 1/2], ['mul', 1], ['plus', 1], ['plus', 2], ['plus', 4], ['plus', 8], ['plus', 16], ['mul', 3/2], ['mul', 2]]


def splitparams(value, firstname, secondname):
    dualparams = {}
    dualparams[firstname], dualparams[secondname] = data_bytes.splitbyte(value)
    return dualparams

def getfineval(value):
    volslidesplit = data_bytes.splitbyte(value)
    volslideout = 0
    if volslidesplit[0] == 0 and volslidesplit[1] == 0: volslideout = 0
    elif volslidesplit[0] == 15 and volslidesplit[1] == 15: volslideout = volslidesplit[0]/16
    elif volslidesplit[0] == 0 and volslidesplit[1] == 15: volslideout = -15
    elif volslidesplit[0] == 0 and volslidesplit[1] != 0: volslideout = volslidesplit[1]*-1
    elif volslidesplit[0] != 0 and volslidesplit[1] == 0: volslideout = volslidesplit[0]
    elif volslidesplit[0] == 15 and volslidesplit[1] != 15: volslideout = (volslidesplit[0]*-1)/16
    elif volslidesplit[0] != 15 and volslidesplit[1] == 15: volslideout = volslidesplit[0]/16
    return volslideout

class tracker_speed:
    def __init__(self, bpm, speed):
        self.tempo = bpm
        self.speed = speed if speed != 0 else 3

    def speed(self, val):
        if val != 0: self.speed = val

    def tempo(self, val): 
        self.tempo = val

    def get(self): 
        return self.tempo*(3/self.speed)

class autostream:
    def __init__(self):
        self.placements = []
        self.pl_pos = 0
        self.cur_pos = 0
        self.active = False

    def next(self):
        self.cur_pos += 1
        if self.placements: self.placements[-1][2] = self.cur_pos

    def do_point(self, point):
        if not self.active:
            self.active = True
            self.placements.append([self.pl_pos, [], 0])
        self.placements[-1][1].append([self.cur_pos, point])

    def add_pl(self):
        self.active = False
        self.pl_pos += self.cur_pos
        self.cur_pos = 0

    def to_cvpj(self, convproj_obj, autoloc):
        for tpl in self.placements:
            autopl_obj = convproj_obj.add_automation_pl(autoloc, 'float')
            autopl_obj.position = (tpl[0])
            autopl_obj.duration = tpl[2]
            for tap in tpl[1]:
                autopoint_obj = autopl_obj.data.add_point()
                autopoint_obj.pos = tap[0]
                autopoint_obj.value = tap[1]
                autopoint_obj.type = 'instant'

class notestream:
    def __init__(self, text_inst_start):
        self.placements = []
        self.used_inst = []
        self.cur_inst = None
        self.note_active = False
        self.text_inst_start = text_inst_start
        self.cur_pos = 0
        self.note_pos = 0
        self.slide_speed = 0

    def note_on(self, c_note, c_fx):
        self.note_active = True
        last_nl = self.placements[-1][1]
        self.note_pos = 0
        init_vol = c_fx['vol'] if 'vol' in c_fx else 1
        init_pan = c_fx['pan'] if 'pan' in c_fx else 0
        last_nl.add_m(self.text_inst_start+str(self.cur_inst), self.cur_pos, 0, c_note, init_vol, {'pan': init_pan})
        self.slide_pitch = notelist.pitchmod(c_note)

    def note_off(self):
        if self.note_active: 
            self.slide_pitch.to_points(self.placements[-1][1])
            self.note_active = False

    def do_cell(self, c_note, c_inst, c_fx, s_speed):
        if c_inst != None: 
            self.cur_inst = c_inst
            if c_inst not in self.used_inst: self.used_inst.append(c_inst)

        if c_note != None:
            if c_note not in ['off', 'cut']:
                new_note = True
                if 'slide_to_note' in c_fx and self.note_active: new_note = False
                if new_note:
                    self.note_off()
                    self.note_on(c_note, c_fx)
                elif self.note_active: self.slide_pitch.slide_tracker_porta_targ(c_note)
            else: self.note_off()

        self.cur_pos += 1
        self.placements[-1][0] += 1
        if self.note_active: 
            if c_fx:
                if 'slide_to_note' in c_fx:
                    if c_fx['slide_to_note'] != 0: self.slide_speed = c_fx['slide_to_note']
                    self.slide_pitch.slide_tracker_porta(self.note_pos, self.slide_speed, s_speed)

                if 'slide_up' in c_fx:
                    if c_fx['slide_up'] != 0: self.slide_speed = c_fx['slide_up']
                    self.slide_pitch.slide_tracker_up(self.note_pos, self.slide_speed, s_speed)

                if 'slide_down' in c_fx:
                    if c_fx['slide_down'] != 0: self.slide_speed = c_fx['slide_down']
                    self.slide_pitch.slide_tracker_down(self.note_pos, self.slide_speed, s_speed)

            self.note_pos += 1
            self.placements[-1][1].last_extend(1)

    def add_pl(self, patnum):
        if self.note_active: self.slide_pitch.to_points(self.placements[-1][1])
        self.placements.append([0, notelist.cvpj_notelist(4, True), patnum, self.used_inst])
        self.cur_pos = 0
        self.note_pos = 0
        self.note_active = False



def addminusval(i_val):
    pos, neg = data_bytes.splitbyte(i_val)
    return (neg*-1) + pos

class multipatterndata:
    def __init__(self, inst_types, dataset, rowsize):
        self.dataset = dataset
        self.mul_types = inst_types
        self.rowsize = rowsize
        self.mul_pd = []
        self.mul_names = []
        self.mul_colors = []
        self.used_inst = []
        for insttype in self.mul_types:
            inst_name, inst_color = dataset.object_get_name_color('chip', insttype)
            self.mul_names.append(inst_name if inst_name != None else insttype)
            self.mul_colors.append(inst_color)
            self.mul_pd.append(patterndata(1, insttype+'_', inst_color))

    def to_cvpj(self, convproj_obj, order_list, s_bpm, s_speed):
        convproj_obj.type = 'm'
        convproj_obj.set_timings(4, True)

        notepl = [notestream(x+"_") for x in self.mul_types]
        numchan = len(self.mul_types)
        patnums = [order_list[x] for x in range(numchan)]
        patdatas = []
        l_patnums = []
        for y in range(len(order_list[0])):
            l_patnums.append([order_list[x][y] for x in range(numchan)])

        notepl = [notestream(x+"_") for x in self.mul_types]

        cur_tempo = s_bpm
        cur_speed = s_speed
        bpm_changed = False

        for s_patnums in l_patnums:
            patdatas = []

            active_part = True

            for chnum in range(numchan):
                s_patnum = s_patnums[chnum]
                if s_patnum in self.mul_pd[chnum].patterndata: 
                    patdatas.append(self.mul_pd[chnum].patterndata[s_patnum])
                else: 
                    patdatas.append([[{}, [[None, None, {}]]] for _ in range(self.rowsize)])

            for ch_num in range(numchan):
                notepl[ch_num].add_pl(0)

            par_rows = []

            #print(s_patnums)

            for rownum in range(self.rowsize):
                global_d = {}
                row_data = []

                for chnum in range(numchan):
                    global_p, cell_p = patdatas[chnum][rownum]
                    row_data.append(cell_p[0])
                    global_d |= global_p

                par_rows.append([global_d, row_data])

                if 'skip_pattern' in global_d: break
                if 'pattern_jump' in global_d: break

            for par_row in par_rows:
                global_r, cell_r = par_row

                for chnum in range(numchan):
                    ch_row_data = cell_r[chnum]
                    notepl[chnum].do_cell(ch_row_data[0], ch_row_data[1], ch_row_data[2], cur_speed)

        for ch_num in range(numchan):
            idnum = str(ch_num+1)
            track_obj = convproj_obj.add_track(idnum, 'instruments', True, False)
            track_obj.visual.name = self.mul_names[ch_num]
            track_obj.visual.color = self.mul_colors[ch_num]

            cur_pl_pos = 0
            for tpl in notepl[ch_num].placements:
                if tpl[0]:
                    for ui in tpl[3]:
                        t_instnamenum = [self.mul_types[ch_num], ui]
                        if t_instnamenum not in self.used_inst: self.used_inst.append(t_instnamenum)

                placement_obj = track_obj.placements.add_notes()
                placement_obj.position = cur_pl_pos
                placement_obj.duration = tpl[0]
                placement_obj.visual.name = 'Pattern '+str(tpl[2]+1)
                placement_obj.notelist = tpl[1]
                cur_pl_pos += tpl[0]

#notepl

class patterndata:
    def __init__(self, number_of_channels, text_inst_start, maincolor):
        self.patterndata = {}
        self.num_chans = number_of_channels
        self.cur_pat = 0

    def to_cvpj(self, convproj_obj, order_list, text_inst_start, s_bpm, s_speed, maincolor):
        convproj_obj.type = 'm'
        convproj_obj.set_timings(4, True)

        notepl = [notestream(text_inst_start) for _ in range(self.num_chans)]
        tempo_autopl = autostream()

        cur_tempo = s_bpm
        cur_speed = s_speed
        bpm_changed = False

        for patnum in order_list:

            if patnum in self.patterndata:
                cur_patdata = self.patterndata[patnum]
                tempo_autopl.add_pl()

                for ch_num in range(self.num_chans): notepl[ch_num].add_pl(patnum)

                for rowdata in cur_patdata:
                    for ch_num in range(self.num_chans):
                        celld = rowdata[1][ch_num]
                        notepl[ch_num].do_cell(celld[0], celld[1], celld[2], cur_speed)

                    if 'break_to_row' in rowdata[0]: break
                    if 'speed' in rowdata[0]: 
                        cur_speed = rowdata[0]['speed']
                        bpm_changed = True
                    if 'tempo' in rowdata[0]: 
                        cur_tempo = rowdata[0]['tempo']
                        bpm_changed = True
                    if 'pattern_jump' in rowdata[0]: break

                    if bpm_changed:
                        tempo_autopl.do_point(cur_tempo*(6/cur_speed))

                    tempo_autopl.next()
                    bpm_changed = False



        #print(tempo_autopl.placements)

        tempo_autopl.to_cvpj(convproj_obj, ['main','bpm'])
        #exit()

        for ch_num in range(self.num_chans):
            notepl[ch_num].add_pl(-1)

        used_inst = []

        for ch_num in range(self.num_chans):
            playlist_obj = convproj_obj.add_playlist(ch_num, True, False)
            playlist_obj.visual.name = "Channel "+str(ch_num)
            playlist_obj.visual.color = maincolor

            cur_pl_pos = 0
            for tpl in notepl[ch_num].placements:
                if tpl[0]:
                    for ui in tpl[3]:
                        if ui not in used_inst: used_inst.append(ui)

                    if tpl[1].notesfound():
                        tpl[1].notemod_conv()
                        placement_obj = playlist_obj.placements.add_notes()
                        placement_obj.position = cur_pl_pos
                        placement_obj.duration = tpl[0]
                        placement_obj.notelist = tpl[1]
                        placement_obj.visual.name = 'Pattern '+str(tpl[2]+1)
                cur_pl_pos += tpl[0]

        patlentable = [x[0] for x in notepl[0].placements]
        convproj_obj.patlenlist_to_timemarker(patlentable[:-1], -1)

        return used_inst

    def veryfirstrow(self, firstpat):
        return self.patterndata[firstpat][0][0]

    def pattern_add(self, num, rows):
        s_patdata = []
        for _ in range(rows): s_patdata.append([{}, [[None, None, {}] for _ in range(self.num_chans)]])
        self.patterndata[num] = s_patdata
        self.cur_pat = num
        self.cur_row = 0

    def pattern_set_cur(self, num):
        self.cur_pat = num
        self.cur_row = 0

    def row_set_cur(self, num):
        self.cur_row = num

    def row_next(self):
        self.cur_row += 1

    def cell_note(self, n_chan, c_note, c_inst):
        if n_chan < self.num_chans:
            patdata = self.patterndata[self.cur_pat][self.cur_row][1][n_chan]
            if c_note != None: patdata[0] = c_note
            if c_inst != None: patdata[1] = c_inst

    def cell_param(self, n_chan, c_partype, c_parval):
        if n_chan < self.num_chans:
            patdata = self.patterndata[self.cur_pat][self.cur_row][1][n_chan]
            if c_partype != None: patdata[2][c_partype] = c_parval

    def cell_g_param(self, c_partype, c_parval):
        self.patterndata[self.cur_pat][self.cur_row][0][c_partype] = c_parval


    def cell_fx_mod(self, n_chan, fx_type, fx_value):
        if fx_type == 1: self.cell_param(n_chan, 'slide_up', fx_value)
        if fx_type == 2: self.cell_param(n_chan, 'slide_down', fx_value)
        if fx_type == 3: self.cell_param(n_chan, 'slide_to_note', fx_value)
        if fx_type == 4: self.cell_param(n_chan, 'vibrato', splitparams(fx_value, 'speed', 'depth'))
        if fx_type == 6: self.cell_param(n_chan, 'vol_slide', addminusval(fx_value))
        if fx_type == 7: self.cell_param(n_chan, 'tremolo', splitparams(fx_value, 'speed', 'depth'))
        if fx_type == 8: self.cell_param(n_chan, 'pan', (fx_value-128)/128)
        if fx_type == 9: self.cell_param(n_chan, 'sample_offset', fx_value*256)
        if fx_type == 10: self.cell_param(n_chan, 'vol_slide', addminusval(fx_value))

        if fx_type == 0 and fx_value != 0:
            arpeggio_first, arpeggio_second = data_bytes.splitbyte(fx_value)
            self.cell_param(n_chan, 'arp', [arpeggio_first, arpeggio_second])

        if fx_type == 5:
            valueout = addminusval(fx_value) 
            self.cell_param(n_chan, 'vol_slide', valueout)
            self.cell_param(n_chan, 'slide_to_note', valueout)

        if fx_type == 14: 
            ext_type, ext_value = data_bytes.splitbyte(fx_value)
            if ext_type == 0: self.cell_param(n_chan, 'filter_amiga_led', ext_value)
            if ext_type == 1: self.cell_param(n_chan, 'fine_slide_up', ext_value)
            if ext_type == 2: self.cell_param(n_chan, 'fine_slide_down', ext_value)
            if ext_type == 3: self.cell_param(n_chan, 'glissando_control', ext_value)
            if ext_type == 4: self.cell_param(n_chan, 'vibrato_waveform', ext_value)
            if ext_type == 5: self.cell_param(n_chan, 'set_finetune', ext_value)
            if ext_type == 6: self.cell_param(n_chan, 'pattern_loop', ext_value)
            if ext_type == 7: self.cell_param(n_chan, 'tremolo_waveform', ext_value)
            if ext_type == 8: self.cell_param(n_chan, 'set_pan', ext_value)
            if ext_type == 9: self.cell_param(n_chan, 'retrigger_note', ext_value)
            if ext_type == 10: self.cell_param(n_chan, 'fine_vol_slide_up', ext_value)
            if ext_type == 11: self.cell_param(n_chan, 'fine_vol_slide_down', ext_value)
            if ext_type == 12: self.cell_param(n_chan, 'note_cut', ext_value)
            if ext_type == 13: self.cell_param(n_chan, 'note_delay', ext_value)
            if ext_type == 14: self.cell_param(n_chan, 'pattern_delay', ext_value)
            if ext_type == 15: self.cell_param(n_chan, 'invert_loop', ext_value)

    def cell_fx_s3m(self, n_chan, fx_type, fx_value):
        if fx_type == 1: self.cell_g_param('speed', fx_value)
        if fx_type == 2: self.cell_g_param('pattern_jump', fx_value)
        if fx_type == 3: self.cell_g_param('break_to_row', fx_value)
        if fx_type == 4: self.cell_param(n_chan, 'vol_slide', getfineval(fx_value))
        if fx_type == 5: self.cell_param(n_chan, 'slide_down', fx_value)
        if fx_type == 6: self.cell_param(n_chan, 'slide_up', fx_value)
        if fx_type == 7: self.cell_param(n_chan, 'slide_to_note', fx_value)
        if fx_type == 8: self.cell_param(n_chan, 'vibrato', splitparams(fx_value, 'speed', 'depth'))
        if fx_type == 9: self.cell_param(n_chan, 'tremor', splitparams(fx_value, 'ontime', 'offtime'))
        if fx_type == 11: self.cell_param(n_chan, 'vol_slide', getfineval(fx_value))
        if fx_type == 13: self.cell_param(n_chan, 'channel_vol', fx_value/64)
        if fx_type == 14: self.cell_param(n_chan, 'channel_vol_slide', getfineval(fx_value))
        if fx_type == 15: self.cell_param(n_chan, 'sample_offset', fx_value*256)
        if fx_type == 16: self.cell_param(n_chan, 'pan_slide', getfineval(fx_value)*-1)
        if fx_type == 18: self.cell_param(n_chan, 'tremolo', splitparams(fx_value, 'speed', 'depth'))
        if fx_type == 22: self.cell_g_param('global_volume', fx_value/64)
        if fx_type == 23: self.cell_g_param('global_volume_slide', getfineval(fx_value))
        if fx_type == 24: self.cell_param(n_chan, 'set_pan', fx_value/255)
        if fx_type == 25: self.cell_param(n_chan, 'panbrello', splitparams(fx_value, 'speed', 'depth'))

        if fx_type == 10:
            arpeggio_first, arpeggio_second = data_bytes.splitbyte(fx_value)
            self.cell_param(n_chan, 'arp', [arpeggio_first, arpeggio_second])

        if fx_type == 12:
            self.cell_param(n_chan, 'vol_slide', getfineval(fx_value))
            self.cell_param(n_chan, 'slide_to_note', getfineval(fx_value))

        if fx_type == 17:
            retrigger_params = {}
            retrigger_alg, retrigger_params['speed'] = data_bytes.splitbyte(fx_value)
            retrigger_params['alg'], retrigger_params['val'] = t_retg_alg[retrigger_alg]
            self.cell_param(n_chan, 'retrigger', retrigger_params)
    
        if fx_type == 19: 
            ext_type, ext_value = data_bytes.splitbyte(fx_value)
            if ext_type == 1: self.cell_param(n_chan, 'glissando_control', ext_value)
            if ext_type == 3: self.cell_param(n_chan, 'vibrato_waveform', ext_value)
            if ext_type == 4: self.cell_param(n_chan, 'tremolo_waveform', ext_value)
            if ext_type == 5: self.cell_param(n_chan, 'panbrello_waveform', ext_value)
            if ext_type == 6: self.cell_param(n_chan, 'fine_pattern_delay', ext_value)
            if ext_type == 7: self.cell_param(n_chan, 'it_inst_control', ext_value)
            if ext_type == 8: self.cell_param(n_chan, 'set_pan', ext_value/16)
            if ext_type == 9: self.cell_param(n_chan, 'it_sound_control', ext_value)
            if ext_type == 10: self.cell_param(n_chan, 'sample_offset_high', ext_value*65536)
            if ext_type == 11: self.cell_param(n_chan, 'loop_start', ext_value)
            if ext_type == 12: self.cell_param(n_chan, 'note_cut', ext_value)
            if ext_type == 13: self.cell_param(n_chan, 'note_delay', ext_value)
            if ext_type == 14: self.cell_param(n_chan, 'pattern_delay', ext_value)
            if ext_type == 15: self.cell_param(n_chan, 'it_active_macro', ext_value)
