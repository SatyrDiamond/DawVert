# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later
import json

from functions import data_values

class dataset:
    def __init__(self, in_dataset):
        if in_dataset != None:
            try:
                f = open(in_dataset, "r")
                self.dataset = json.load(f)
                self.category_list = [x for x in self.dataset]
                print('[dataset] Loaded '+in_dataset)
            except:
                self.dataset = {}
                self.category_list = []
        else:
            self.dataset = {}
            self.category_list = []
        self.midi_dataset = None

    def check_exists_one(self, c_name, t_name):
        if c_name in self.dataset: 
            if t_name in self.dataset[c_name]:
                return True

    def check_exists_two(self, c_name, o_name, p_name, t_name):
        if c_name in self.dataset: 
            if o_name in self.dataset[c_name][p_name]:
                if t_name in self.dataset[c_name][p_name][o_name]:
                    return True

# ####################################################################################################
# ####################################################################################################
# --- Category
# ####################################################################################################
# ####################################################################################################

    def category_add(self, c_name):
        if c_name not in self.dataset: 
            self.dataset[c_name] = {'objects': {}}
            self.category_list.append(c_name)

    def category_del(self, c_name):
        if c_name in self.dataset: 
            del self.dataset[c_name]
            self.category_list.remove(c_name)
            return True
        else:
            return False

# ####################################################################################################
# ####################################################################################################
# --- Object
# ####################################################################################################
# ####################################################################################################

    def object_list(self, c_name):
        data_out = None
        if c_name in self.dataset: data_out = [x for x in self.dataset[c_name]['objects']]
        return  data_out

    def object_add(self, c_name, o_name):
        if c_name in self.dataset: 
            if o_name not in self.dataset[c_name]['objects']:
                self.dataset[c_name]['objects'][o_name] = {}

    def object_del(self, c_name, o_name):
        if c_name in self.dataset: 
            if o_name in self.dataset[c_name]['objects']:
                del self.dataset[c_name]['objects'][o_name]
                return True

    def object_visual_get(self, c_name, o_name):
        visual_data = None
        isobjfound = False
        if c_name in self.dataset: 
            if o_name in self.dataset[c_name]['objects']:
                objdata = self.dataset[c_name]['objects'][o_name]
                isobjfound = True
                if 'visual' in objdata: visual_data = objdata['visual']
        return isobjfound, visual_data

    def object_visual_set(self, c_name, o_name, visual_data):
        if c_name in self.dataset: 
            if o_name in self.dataset[c_name]['objects']:
                objdata = self.dataset[c_name]['objects'][o_name]
                if visual_data != None: objdata['visual'] = visual_data

    def object_var_get(self, v_name, c_name, o_name):
        group_data = None
        isobjfound = False
        if c_name in self.dataset: 
            if o_name in self.dataset[c_name]['objects']:
                objdata = self.dataset[c_name]['objects'][o_name]
                isobjfound = True
                if v_name in objdata: group_data = objdata[v_name]
        return isobjfound, group_data

    def object_var_set(self, v_name, c_name, o_name, group_data):
        if c_name in self.dataset: 
            if o_name in self.dataset[c_name]['objects']:
                objdata = self.dataset[c_name]['objects'][o_name]
                if group_data != None: objdata[v_name] = group_data

    def object_get_name_color(self, c_name, o_name):
        visualdata = data_values.nested_dict_get_value(self.dataset, [c_name, 'objects', o_name, 'visual'])
        name = None
        color = None
        if visualdata != None:
            if 'name' in visualdata: name = visualdata['name']
            if 'color' in visualdata: color = visualdata['color']
        return name, color

# ####################################################################################################
# ####################################################################################################
# --- Params
# ####################################################################################################
# ####################################################################################################

    def params_list(self, c_name, o_name):
        plist = None
        if c_name in self.dataset: 
            if o_name in self.dataset[c_name]['objects']:
                if 'params' in self.dataset[c_name]['objects'][o_name]:
                    plist = [x for x in self.dataset[c_name]['objects'][o_name]['params']]
                    if all(ele.isdigit() for ele in plist):
                        plist = [int(x) for x in plist]
                        plist.sort()
                        plist = [str(x) for x in plist]

        return plist

    def params_create(self, c_name, o_name):
        if c_name in self.dataset: 
            if o_name in self.dataset[c_name]['objects']: 
                self.dataset[c_name]['objects'][o_name]['params'] = {}

    def params_exists(self, c_name, o_name):
        if c_name in self.dataset: 
            if o_name in self.dataset[c_name]['objects']: 
                existd = self.dataset[c_name]['objects'][o_name]
                return ('params' in existd)
            return False
        return False

    def params_i_add(self, c_name, o_name, p_name):
        if c_name in self.dataset: 
            if o_name in self.dataset[c_name]['objects']:
                paramdata = {}
                paramdata['noauto'] = False
                paramdata['type'] = 'none'
                paramdata['def'] = 0
                paramdata['min'] = 0
                paramdata['max'] = 0
                paramdata['name'] = ''
                self.dataset[c_name]['objects'][o_name]['params'][p_name] = paramdata

    def params_i_del(self, c_name, o_name, p_name):
        if data_values.nested_dict_get_value(self.dataset, [c_name, 'objects', o_name, 'params', p_name]) != None:
            del self.dataset[c_name]['objects'][o_name]['params'][p_name]

    def params_i_get(self, c_name, o_name, p_name):
        if data_values.nested_dict_get_value(self.dataset, [c_name, 'objects', o_name, 'params', p_name]) != None:
            paramdata = self.dataset[c_name]['objects'][o_name]['params'][p_name]
            pv_noauto = paramdata['noauto'] if 'noauto' in paramdata else False
            pv_type = paramdata['type'] if 'type' in paramdata else 'none'
            pv_def = paramdata['def'] if 'def' in paramdata else 0
            pv_min = paramdata['min'] if 'min' in paramdata else 0
            pv_max = paramdata['max'] if 'max' in paramdata else 0
            pv_name = paramdata['name'] if 'name' in paramdata else ''
            return [pv_noauto,pv_type,pv_def,pv_min,pv_max,pv_name]

    def params_i_set(self, c_name, o_name, p_name, value):
        if data_values.nested_dict_get_value(self.dataset, [c_name, 'objects', o_name, 'params', p_name]) != None:
            self.dataset[c_name]['objects'][o_name]['params'][p_name] = {'noauto': value[0], 'type': value[1], 'def': value[2], 'min': value[3], 'max': value[4], 'name': value[5]}

# ####################################################################################################
# ####################################################################################################
# --- Colorset
# ####################################################################################################
# ####################################################################################################

    def colorset_list(self, c_name):
        colorset = None
        if data_values.nested_dict_get_value(self.dataset, [c_name, 'colorset']) != None:
            colorset = [x for x in self.dataset[c_name]['colorset']]
        return colorset

    def colorset_create(self, c_name):
        if c_name in self.dataset: self.dataset[c_name]['colorset'] = {}

    def colorset_add(self, c_name, s_name):
        if data_values.nested_dict_get_value(self.dataset, [c_name, 'colorset']) != None:
            self.dataset[c_name]['colorset'][s_name] = []

    def colorset_e_list(self, c_name, s_name):
        outval = []
        if data_values.nested_dict_get_value(self.dataset, [c_name, 'colorset', s_name]) != None:
            outval = [x for x in self.dataset[c_name]['colorset'][s_name]]
        return outval

    def colorset_e_add(self, c_name, s_name, i_color):
        if data_values.nested_dict_get_value(self.dataset, [c_name, 'colorset', s_name]) != None:
            self.dataset[c_name]['colorset'][s_name].append(i_color)

    def colorset_e_del(self, c_name, s_name, num):
        if data_values.nested_dict_get_value(self.dataset, [c_name, 'colorset', s_name]) != None:
            del self.dataset[c_name]['colorset'][s_name][num]

# ####################################################################################################
# ####################################################################################################
# --- Midi Map
# ####################################################################################################
# ####################################################################################################

    def midid_to_num(self, i_bank, i_patch, i_isdrum): return i_bank*256 + i_patch + int(i_isdrum)*128
    def midid_from_num(self, value): return (value>>8), (value%128), int(bool(value&0b10000000))

    def midito_list(self, c_name):
        pmap = None
        if data_values.nested_dict_get_value(self.dataset, [c_name, 'midi_to']) != None:
            pmap = [x for x in self.dataset[c_name]['midi_to']]
        return pmap

    def midito_create(self, c_name):
        if c_name in self.dataset: self.dataset[c_name]['midi_to'] = {}

    def midito_del(self, c_name, i_name):
        if data_values.nested_dict_get_value(self.dataset, [c_name, 'midi_to']) != None:
            if i_name in self.dataset[c_name]['midi_to']: del self.dataset[c_name]['midi_to'][str(i_name)]

    def midito_add(self, c_name, i_name, i_bank, i_patch, i_isdrum):
        if data_values.nested_dict_get_value(self.dataset, [c_name, 'midi_to']) != None:
            self.dataset[c_name]['midi_to'][str(i_name)] = self.midid_to_num(i_bank, i_patch, i_isdrum)

    def midito_get(self, c_name, i_name):
        outval = None, None, None
        if data_values.nested_dict_get_value(self.dataset, [c_name, 'midi_to']) != None:
            if i_name in self.dataset[c_name]['midi_to']: 
                outval = self.midid_from_num(self.dataset[c_name]['midi_to'][str(i_name)])
        return outval

# ####################################################################################################
# ####################################################################################################
# --- Groups
# ####################################################################################################
# ####################################################################################################

    def groups_list(self, c_name):
        pmap = None
        if data_values.nested_dict_get_value(self.dataset, [c_name, 'groups']) != None:
            pmap = [x for x in self.dataset[c_name]['groups']]
        return pmap

    def groups_create(self, c_name):
        if c_name in self.dataset: self.dataset[c_name]['groups'] = {}


    def groups_add(self, c_name, g_name):
        if c_name in self.dataset: 
            if g_name not in self.dataset[c_name]['groups']:
                self.dataset[c_name]['groups'][g_name] = {}

    def groups_del(self, c_name, g_name):
        if c_name in self.dataset: 
            if g_name in self.dataset[c_name]['groups']:
                del self.dataset[c_name]['groups'][g_name]
                return True

    def groups_visual_get(self, c_name, g_name):
        visual_data = None
        isobjfound = False
        if c_name in self.dataset: 
            if 'groups' in self.dataset[c_name]:
                if g_name in self.dataset[c_name]['groups']:
                    objdata = self.dataset[c_name]['groups'][g_name]
                    isobjfound = True
                    if 'visual' in objdata: visual_data = objdata['visual']
        return isobjfound, visual_data

    def groups_visual_set(self, c_name, g_name, visual_data):
        if c_name in self.dataset: 
            if g_name in self.dataset[c_name]['groups']:
                objdata = self.dataset[c_name]['groups'][g_name]
                if visual_data != None: objdata['visual'] = visual_data

    def groups_get_name_color(self, c_name, g_name):
        isobjfound, visualdata = self.groups_visual_get(c_name, g_name)
        name = None
        color = None
        if visualdata != None:
            if 'name' in visualdata: name = visualdata['name']
            if 'color' in visualdata: color = visualdata['color']
        return name, color

# ####################################################################################################
# ####################################################################################################
# --- Drumset
# ####################################################################################################
# ####################################################################################################

    def drumset_list(self, c_name, o_name):
        plist = None
        if data_values.nested_dict_get_value(self.dataset, [c_name, 'objects', o_name, 'drumset']) != None:
            plist = [x for x in self.dataset[c_name]['objects'][o_name]['drumset']]
        return plist

    def drumset_create(self, c_name, o_name):
        if data_values.nested_dict_get_value(self.dataset, [c_name, 'objects', o_name]) != None:
            self.dataset[c_name]['objects'][o_name]['drumset'] = {}

    def drumset_i_set(self, c_name, o_name, keynum):
        if data_values.nested_dict_get_value(self.dataset, [c_name, 'objects', o_name, 'drumset']) != None:
            self.dataset[c_name]['objects'][o_name]['drumset'][keynum] = {}

    def drumset_i_del(self, c_name, o_name, keynum):
        if data_values.nested_dict_get_value(self.dataset, [c_name, 'objects', o_name, 'drumset', keynum]) != None:
            del self.dataset[c_name]['objects'][o_name]['drumset'][keynum]

    def drumset_i_get(self, c_name, o_name, keynum):
        if data_values.nested_dict_get_value(self.dataset, [c_name, 'objects', o_name, 'drumset', keynum]) != None:
            return self.dataset[c_name]['objects'][o_name]['drumset'][keynum]

    def drumset_visual_get(self, c_name, o_name, keynum):
        visual_data = None
        isobjfound = False
        if data_values.nested_dict_get_value(self.dataset, [c_name, 'objects', o_name, 'drumset', keynum]) != None:
            drumdata = self.dataset[c_name]['objects'][o_name]['drumset'][keynum]
            isobjfound = True
            if 'visual' in drumdata: visual_data = drumdata['visual']
        return isobjfound, visual_data

    def drumset_visual_set(self, c_name, o_name, keynum, visual_data):
        if data_values.nested_dict_get_value(self.dataset, [c_name, 'objects', o_name, 'drumset']) != None:
            drumdata = self.dataset[c_name]['objects'][o_name]['drumset']
            if keynum not in drumdata: drumdata[keynum] = {}
            if visual_data != None: drumdata[keynum]['visual'] = visual_data

# ####################################################################################################
# ####################################################################################################
# --- Midi to cvpj
# ####################################################################################################
# ####################################################################################################
