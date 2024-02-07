# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_values
from objects import convproj_placements
from objects import convproj
from objects import counter

class convproj2autoid:
    def __init__(self, time_ppq, time_float):
        self.in_data = {}
        self.time_ppq = time_ppq
        self.time_float = time_float

    def define(self, i_id, i_loc, i_type, i_addmul):
        i_loc = convproj.autopath_encode(i_loc)
        #print('[auto id] Define - '+str(i_id)+' - '+i_loc)
        if i_id not in self.in_data: 
            self.in_data[i_id] = [i_loc, i_type, i_addmul, convproj_placements.cvpj_placements_auto(self.time_ppq, self.time_float, 'float')]
        else:
            self.in_data[i_id][0] = i_loc
            self.in_data[i_id][1] = i_type
            self.in_data[i_id][2] = i_addmul

    def add_pl(self, i_id, val_type):
        #print('in_add_pl', i_id, len(i_autopl))
        if i_id not in self.in_data: self.in_data[i_id] = [None, None, None, convproj_placements.cvpj_placements_auto(self.time_ppq, self.time_float, val_type)]
        return self.in_data[i_id][3].add(val_type)

    def output(self, convproj_obj):
        for i_id in self.in_data:
            out_auto_loc = self.in_data[i_id][0]
            out_auto_type = self.in_data[i_id][1]
            out_auto_addmul = self.in_data[i_id][2]
            out_auto_data = self.in_data[i_id][3]
            out_auto_data.val_type = out_auto_type
            #print(i_id, self.in_data[i_id][0:3], out_auto_data)
            if self.in_data[i_id][0:4] != [None, None, None] and out_auto_data.data != []:
                if out_auto_addmul != None: out_auto_data.addmul(out_auto_addmul[0], out_auto_addmul[1])
                convproj_obj.automation[out_auto_loc] = out_auto_data

# ------------------------ cvpjauto to autoid ------------------------

class autoid2convproj:
    def __init__(self, convproj_obj):
        self.out_data = {}
        auto_num = counter.counter(200000, 'auto_')
        for ap in convproj_obj.automation: self.out_data[ap] = auto_num.get()

    def get(self, i_loc, convproj_obj):
        i_loc = convproj.autopath_encode(i_loc)
        if i_loc in self.out_data: 
            return True, self.out_data[i_loc], convproj_obj.automation[i_loc]
        else: 
            return False, None, None