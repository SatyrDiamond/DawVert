# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import note_data
from functions import xtramath
from objects import convproj
import math

class valuepack:
    def __init__(self, value, automation):
        self.value = value
        self.automation = automation

    def calc_div(self, i_val):
        self.value /= i_val
        if self.automation: self.automation.calc_addmul(0, 1/i_val)

    def calc_mul(self, i_val):
        self.value *= i_val
        if self.automation: self.automation.calc_addmul(0, i_val)

    def calc_add(self, i_val):
        self.value += i_val
        if self.automation: self.automation.calc_addmul(i_val, 1)

    def calc_note2freq(self):
        self.value = note_data.note_to_freq(self.value)
        if self.automation: self.automation.calc_funcval(note_data.note_to_freq)

    def calc_addmul(self, i_add, i_mul):
        self.value = (self.value+i_add)*i_mul
        if self.automation: self.automation.calc_addmul(i_add, i_mul)

    def calc_to_one(self, i_min, i_max):
        self.value = xtramath.between_to_one(i_min, i_max, self.value)
        if self.automation: self.automation.calc_to_one(i_min, i_max)

    def calc_from_one(self, i_min, i_max):
        self.value = xtramath.between_from_one(i_min, i_max, self.value)
        if self.automation: self.automation.calc_from_one(i_min, i_max)

    def calc_clamp(self, i_min, i_max):
        self.value = xtramath.clamp(self.value, i_min, i_max)

    def calc_pow(self, i_val):
        self.value = self.value**i_val
        if self.automation: self.automation.calc_pow(i_val)

    def calc_pow_r(self, i_val):
        self.value = i_val**self.value
        if self.automation: self.automation.calc_pow_r(i_val)

    def calc_log(self, i_val):
        self.value = math.log(self.value,i_val)
        if self.automation: self.automation.calc_log(i_val)

    def calc_log_r(self, i_val):
        self.value = math.log(i_val,self.value)
        if self.automation: self.automation.calc_log_r(i_val)


class transform_store:
    def __init__(self):
        self.cmds = []

        self.in_type = ''
        self.in_subtype = ''
        self.out_type = ''
        self.out_subtype = ''

        self.in_data = {}

        self.out_param = {}
        self.out_dataval = {}

        self.store_data = {}
        self.cur_params = {}

class plugtransform:
    def __init__(self):
        self.transforms = {}
        self.cur_params = {}
        self.store_data = {}
        self.filtername = ''

    def load_file(self, filepath):
        try:
            if filepath:
                f = open(filepath, "r")
                ddlines = [x.strip().split('#')[0].split('|') for x in f.readlines()]

                ts_active = False

                for ddline in ddlines:

                    if ddline == ['']: ddline = []

                    if ddline:
                        if ddline[0] == 'new':
                            ts_active = True
                            ts_store_obj = self.transforms[ddline[1]] = transform_store()

                        if ts_active: 
                            if ddline[0] == 'in_param': ts_store_obj.in_data[ddline[1]] = [ddline[2] if len(ddline) == 3 else ddline[1], False]
                            elif ddline[0] == 'in_dataval': ts_store_obj.in_data[ddline[1]] = [ddline[2] if len(ddline) == 3 else ddline[1], True]
                            elif ddline[0] == 'in_type': 
                                if ddline[1]: ts_store_obj.in_type = ddline[1]
                            elif ddline[0] == 'in_subtype': 
                                if ddline[1]: ts_store_obj.in_subtype = ddline[1]
                            elif ddline[0] == 'out_type': 
                                if ddline[1]: ts_store_obj.out_type = ddline[1]
                            elif ddline[0] == 'out_subtype': 
                                if ddline[1]: ts_store_obj.out_subtype = ddline[1]

                            #elif ddline[0] == 'out_param': ts_store_obj.out_param[ddline[1]] = [True, ddline[2], ddline[3] if len(ddline) == 4 else ddline[2]]
                            #elif ddline[0] == 'out_v_param': ts_store_obj.out_param[ddline[1]] = [False, float(ddline[2]), ddline[3] if len(ddline) == 4 else ddline[2]]
                            
                            #elif ddline[0] == 'out_dataval': ts_store_obj.out_dataval[ddline[1]] = [True, ddline[2], ddline[3]]
                            #elif ddline[0] == 'out_v_dataval': ts_store_obj.out_dataval[ddline[1]] = [False, float(ddline[2]), ddline[3]]
                            elif ddline[0] != 'new': ts_store_obj.cmds.append(ddline)
                            #print(ddline)


                print('[plugtransform] Loaded '+filepath)
        except:
            pass

    def set_filtername(self, val):
        self.filtername = val

    def store_wet(self, plugin_obj, convproj_obj, storename, pluginid):
        autopath = convproj.autopath_encode(['slot', pluginid, 'wet'])
        d_value = plugin_obj.params_slot.get('wet', 0).value
        plugin_obj.params_slot.remove('wet')
        self.cur_params[storename] = valuepack(d_value, convproj_obj.automation.data[autopath] if autopath in convproj_obj.automation.data else None)

    def store_param(self, plugin_obj, convproj_obj, paramid, storename, pluginid):
        autopath = convproj.autopath_encode(['plugin', pluginid, paramid])
        d_value = plugin_obj.params.get(paramid, 0).value
        plugin_obj.params.remove(paramid)
        self.cur_params[storename] = valuepack(d_value, convproj_obj.automation.data[autopath] if autopath in convproj_obj.automation.data else None)

    def store_dataval(self, plugin_obj, paramid, storename):
        d_value = plugin_obj.datavals.get(paramid, 0)
        plugin_obj.datavals.remove(paramid)
        self.cur_params[storename] = valuepack(d_value, None)

    def calc_div(self, storename, i_val):
        if storename in self.cur_params: self.cur_params[storename].calc_div(i_val)

    def calc_mul(self, storename, i_val):
        if storename in self.cur_params: self.cur_params[storename].calc_mul(i_val)

    def calc_add(self, storename, i_val):
        if storename in self.cur_params: self.cur_params[storename].calc_add(i_val)

    def calc_note2freq(self, storename):
        if storename in self.cur_params: self.cur_params[storename].calc_note2freq()

    def calc_addmul(self, storename, i_add, i_mul):
        if storename in self.cur_params: self.cur_params[storename].calc_addmul(i_add, i_mul)

    def calc_to_one(self, storename, i_min, i_max):
        if storename in self.cur_params: self.cur_params[storename].calc_to_one(i_min, i_max)

    def calc_from_one(self, storename, i_min, i_max):
        if storename in self.cur_params: self.cur_params[storename].calc_from_one(i_min, i_max)

    def calc_clamp(self, storename, i_min, i_max):
        if storename in self.cur_params: self.cur_params[storename].calc_clamp(i_min, i_max)

    def calc_pow(self, storename, i_val):
        if storename in self.cur_params: self.cur_params[storename].calc_pow(i_val)

    def calc_pow_r(self, storename, i_val):
        if storename in self.cur_params: self.cur_params[storename].calc_pow_r(i_val)

    def calc_log(self, storename, i_val):
        if storename in self.cur_params: self.cur_params[storename].calc_log(i_val)

    def calc_log_r(self, storename, i_val):
        if storename in self.cur_params: self.cur_params[storename].calc_log_r(i_val)

    def to_store(self, storename, outname):
        self.store_data[outname] = self.cur_params[storename].value

    def out_auto(self, convproj_obj, pluginid, storename, paramid):
        if storename in self.cur_params: 
            if self.cur_params[storename].automation: 
                autopath = convproj.autopath_encode(['plugin', pluginid, paramid])
                convproj_obj.automation.data[autopath] = self.cur_params[storename].automation

    def out(self, convproj_obj, plugin_obj, pluginid, storename, paramid, valuename):
        if storename in self.cur_params: 
            if self.cur_params[storename].automation: 
                autopath = convproj.autopath_encode(['plugin', pluginid, paramid])
                convproj_obj.automation.data[autopath] = self.cur_params[storename].automation
            param_obj = plugin_obj.params.add(paramid, self.cur_params[storename].value, 'float')
            param_obj.visual.name = valuename

    def out_wet(self, convproj_obj, plugin_obj, pluginid, storename):
        if storename in self.cur_params: 
            if self.cur_params[storename].automation: 
                autopath = convproj.autopath_encode(['slot', pluginid, 'wet'])
                convproj_obj.automation.data[autopath] = self.cur_params[storename].automation
            param_obj = plugin_obj.params_slot.add('wet', self.cur_params[storename].value, 'float')
            param_obj.visual.name = 'Wet'


    def transform(self, tsname, convproj_obj, plugin_obj, pluginid, extra_json):
        self.store_data = {}
        self.cur_params = {}

        if tsname in self.transforms:
            cur_ts = self.transforms[tsname]

            #print('[plugtransform] Transforming',cur_ts.in_type+':'+cur_ts.in_subtype,'to',cur_ts.out_type+':'+cur_ts.out_subtype)

            for in_name, in_data in cur_ts.in_data.items():
                if not in_data[1]: 
                    self.store_param(plugin_obj, convproj_obj, in_data[0], in_name, pluginid)
                else: 
                    self.store_dataval(plugin_obj, in_data[0], in_name)

            plugin_obj.params.clear()
            plugin_obj.type_set(cur_ts.out_type, cur_ts.out_subtype)

            filtername = ''
            for cmd in cur_ts.cmds:
                if cmd[0] == 'filter': filtername = cmd[1]
                elif not filtername or (filtername == self.filtername):
                    if cmd[0] == 'in_wet': self.store_wet(plugin_obj, convproj_obj, pluginid, cmd[1])
                    elif cmd[0] == 'calc':
                        if cmd[2] == 'div': self.calc_div(cmd[1], float(cmd[3]))
                        if cmd[2] == 'mul': self.calc_mul(cmd[1], float(cmd[3]))
                        if cmd[2] == 'add': self.calc_add(cmd[1], float(cmd[3]))
                        if cmd[2] == 'note2freq': self.calc_note2freq(cmd[1])
                        if cmd[2] == 'addmul': self.calc_addmul(cmd[1], float(cmd[3]), float(cmd[4]))
                        if cmd[2] == 'to_one': self.calc_to_one(cmd[1], float(cmd[3]), float(cmd[4]))
                        if cmd[2] == 'from_one': self.calc_from_one(cmd[1], float(cmd[3]), float(cmd[4]))
                        if cmd[2] == 'clamp': self.calc_clamp(cmd[1], float(cmd[3]), float(cmd[4]))
                        if cmd[2] == 'pow': self.calc_pow(cmd[1], float(cmd[3]))
                        if cmd[2] == 'pow_r': self.calc_pow_r(cmd[1], float(cmd[3]))
                        if cmd[2] == 'log': self.calc_log(cmd[1], float(cmd[3]))
                        if cmd[2] == 'log_r': self.calc_log_r(cmd[1], float(cmd[3]))
                    elif cmd[0] == 'out_store': self.to_store(cmd[2], cmd[1])
                    elif cmd[0] == 'out_auto': self.out_auto(convproj_obj, pluginid, cmd[2], cmd[1])
                    elif cmd[0] == 'out_wet': self.out_wet(convproj_obj, plugin_obj, pluginid, cmd[1])
                    elif cmd[0] == 'out_param': self.out(convproj_obj, plugin_obj, pluginid, cmd[2], cmd[1], cmd[3] if len(cmd) == 4 else cmd[2])
                    elif cmd[0] == 'out_v_param': 
                        param_obj = plugin_obj.params.add(cmd[1], float(cmd[2]), 'float')
                        param_obj.visual.name = cmd[3] if len(cmd) == 4 else cmd[2]
                    else:
                        print(cmd)

            for paramid, paramdata in cur_ts.out_param.items():
                if paramdata[0]:
                    self.out(convproj_obj, plugin_obj, pluginid, paramdata[1], paramid, paramdata[2])
                else:
                    param_obj = plugin_obj.params.add(paramid, paramdata[1], 'float')
                    param_obj.visual.name = paramdata[2]

            #for datavald in cur_ts.out_dataval.items():
            #    print(datavald)

        else:
            print('[plugtransform] '+tsname+' not defined')

    def get_storedval(self, name):
        return self.store_data[name] if name in self.store_data else 0

class storedtransform:
    def __init__(self):
        self.storedts = {}

    def transform(self, filepath, ts_name, convproj_obj, plugin_obj, pluginid, extra_json):
        if filepath not in self.storedts: 
            self.storedts[filepath] = plugtransform()
            self.storedts[filepath].load_file(filepath)
        self.current_ts = self.storedts[filepath]
        self.current_ts.transform(ts_name, convproj_obj, plugin_obj, pluginid, extra_json)

    def get_storedval(self, name):
        return self.current_ts.get_storedval(name)