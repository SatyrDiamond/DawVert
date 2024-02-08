# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import note_data
from functions import xtramath
from objects import convproj

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

class plugtransform:
    def __init__(self):
        self.transforms = {}

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

                            elif ddline[0] == 'out_param': ts_store_obj.out_param[ddline[1]] = [True, ddline[2], ddline[3] if len(ddline) == 4 else ddline[2]]
                            elif ddline[0] == 'out_v_param': ts_store_obj.out_param[ddline[1]] = [False, float(ddline[2]), ddline[3] if len(ddline) == 4 else ddline[2]]
                            
                            elif ddline[0] == 'out_dataval': ts_store_obj.out_dataval[ddline[1]] = [True, ddline[2], ddline[3]]
                            elif ddline[0] == 'out_v_dataval': ts_store_obj.out_dataval[ddline[1]] = [False, float(ddline[2]), ddline[3]]
                            elif ddline[0] != 'new': ts_store_obj.cmds.append(ddline)
                            #print(ddline)


                print('[plugtransform] Loaded '+filepath)
        except:
            pass

    def transform(self, tsname, convproj_obj, plugin_obj, pluginid, extra_json):
        self.store_data = {}
        if tsname in self.transforms:
            cur_ts = self.transforms[tsname]

            cur_params = {}
            for in_name, in_data in cur_ts.in_data.items():
                #print(in_name, in_data)

                autopath = convproj.autopath_encode(['plugin', pluginid, in_data[0]])

                d_automation = convproj_obj.automation[autopath] if autopath in convproj_obj.automation else None
                d_autoticks = convproj_obj.autopoints[autopath] if autopath in convproj_obj.autopoints else None
                d_autopoints = convproj_obj.autoticks[autopath] if autopath in convproj_obj.autoticks else None

                if not in_data[1]:
                    d_value = plugin_obj.params.get(in_data[0], 0).value 
                    plugin_obj.params.remove(in_data[0])
                else:
                    d_value = plugin_obj.datavals.get(in_data[0], 0)
                    plugin_obj.datavals.remove(in_data[0])

                cur_params[in_name] = [d_value, d_automation, d_autoticks, d_autopoints]

            plugin_obj.params.clear()
            plugin_obj.type_set(cur_ts.out_type, cur_ts.out_subtype)

            for cmd in cur_ts.cmds:
                print(cmd)
                if cmd[0] == 'calc':
                    var_name = cmd[1]
                    var_data = cur_params[var_name]

                    if cmd[2] == 'div':
                        calcval = float(cmd[3])
                        var_data[0] /= calcval
                        if var_data[1]: var_data[1].addmul(0, 1/calcval)
                        if var_data[2]: var_data[2].addmul(0, 1/calcval)
                        if var_data[3]: var_data[3].addmul(0, 1/calcval)

                    if cmd[2] == 'mul':
                        calcval = float(cmd[3])
                        var_data[0] *= calcval
                        if var_data[1]: var_data[1].addmul(0, calcval)
                        if var_data[2]: var_data[2].addmul(0, calcval)
                        if var_data[3]: var_data[3].addmul(0, calcval)

                    if cmd[2] == 'add':
                        calcval = float(cmd[3])
                        var_data[0] += calcval
                        if var_data[1]: var_data[1].addmul(calcval, 1)
                        if var_data[2]: var_data[2].addmul(calcval, 1)
                        if var_data[3]: var_data[3].addmul(calcval, 1)

                    if cmd[2] == 'note2freq':
                        var_data[0] = note_data.note_to_freq(var_data[0])
                        if var_data[1]: var_data[1].funcval(note_data.note_to_freq)
                        if var_data[2]: var_data[2].funcval(note_data.note_to_freq)
                        if var_data[3]: var_data[3].funcval(note_data.note_to_freq)

                    if cmd[2] == 'addmul':
                        i_add = float(cmd[3])
                        i_mul = float(cmd[4])
                        var_data[0] = (var_data[0]+i_add)*i_mul
                        if var_data[1]: var_data[1].addmul(i_add, i_mul)
                        if var_data[2]: var_data[2].addmul(i_add, i_mul)
                        if var_data[3]: var_data[3].addmul(i_add, i_mul)

                    if cmd[2] == 'to_one':
                        i_min = float(cmd[3])
                        i_max = float(cmd[4])
                        var_data[0] = xtramath.between_to_one(i_min, i_max, var_data[0])
                        if var_data[1]: var_data[1].to_one(i_min, i_max)
                        if var_data[2]: var_data[2].to_one(i_min, i_max)
                        if var_data[3]: var_data[3].to_one(i_min, i_max)

                    if cmd[2] == 'from_one':
                        i_min = float(cmd[3])
                        i_max = float(cmd[4])
                        var_data[0] = xtramath.between_from_one(i_min, i_max, var_data[0])
                        if var_data[1]: var_data[1].from_one(i_min, i_max)
                        if var_data[2]: var_data[2].from_one(i_min, i_max)
                        if var_data[3]: var_data[3].from_one(i_min, i_max)

                    if cmd[2] == 'clamp':
                        i_min = float(cmd[3])
                        i_max = float(cmd[4])
                        var_data[0] = xtramath.clamp(var_data[0], i_min, i_max)

                if cmd[0] == 'out_store':
                    self.store_data[cmd[1]] = cur_params[cmd[2]][0]

                if cmd[0] == 'out_auto':
                    #print(cur_params)

                    if cmd[2] in cur_params:
                        var_data = cur_params[cmd[2]]
                        autopath = convproj.autopath_encode(['plugin', pluginid, cmd[1]])
                        if var_data[1]: convproj_obj.automation[autopath] = var_data[1]
                        if var_data[2]: convproj_obj.autopoints[autopath] = var_data[2]
                        if var_data[3]: convproj_obj.autoticks[autopath] = var_data[3]
                    else:
                        print('[plugtransform] out_auto: '+cmd[2]+' not found in stored paramdata')
                        exit()

            for paramid, paramdata in cur_ts.out_param.items():
                #print(paramid, paramdata, var_data)
                if paramdata[0]:
                    var_data = cur_params[paramdata[1]]
                    autopath = convproj.autopath_encode(['plugin', pluginid, paramid])
                    if var_data[1]: convproj_obj.automation[autopath] = var_data[1]
                    if var_data[2]: convproj_obj.autopoints[autopath] = var_data[2]
                    if var_data[3]: convproj_obj.autoticks[autopath] = var_data[3]
                    param_obj = plugin_obj.params.add(paramid, var_data[0], 'float')
                    param_obj.visual.name = paramdata[2]
                else:
                    param_obj = plugin_obj.params.add(paramid, paramdata[1], 'float')
                    param_obj.visual.name = paramdata[2]


            #for datavald in cur_ts.out_dataval.items():
            #    print(datavald)

        else:
            print('[plugtransform] '+tsname+' not defined')

    def get_storedval(self, name):
        return self.store_data[name] if name in self.store_data else 0

