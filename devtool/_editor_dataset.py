from enum import Enum
from imgui_bundle import hello_imgui, icons_fontawesome, imgui, immapp
from imgui_bundle.demos_python import demo_utils
from typing import List
import argparse
import json

import sys
sys.path.append('../')

from functions import xtramath
from objects import dv_dataset

table_flags = (
    imgui.TableFlags_.row_bg
    | imgui.TableFlags_.borders
    | imgui.TableFlags_.resizable
    | imgui.TableFlags_.sizing_stretch_same
)

def clamp(n, minn, maxn): return max(min(maxn, n), minn)

# --------------------------------------------------------------------------------- Widgits

def widgit_txt_manip(i_text):
    wc_txtfield, wi_txtfield = imgui.input_text('##', i_text)
    if wc_txtfield: i_text = wi_txtfield
    btn_add = False
    btn_del = False
    if i_text != '':
        imgui.same_line()
        btn_add = imgui.button("Add")
        imgui.same_line()
        btn_del = imgui.button("Del")
    return btn_add, btn_del, i_text

def widgit_color_manip(i_color):
    wc_color, wi_color = imgui.color_edit3('##colorin', i_color)
    if wc_color: i_color = wi_color
    btn_add = False
    btn_del = False
    if i_color != '':
        imgui.same_line()
        btn_add = imgui.button("Add")
        imgui.same_line()
        btn_del = imgui.button("Del")
    return btn_add, btn_del, i_color

def widgit_list_manip(i_text, i_list, i_numname, i_vlist):
    imgui.separator()
    imgui.push_item_width(400)
    c_listdata, w_listdata = imgui.list_box('##wlistm', i_numname[0], i_list if i_vlist == None else i_vlist)
    if c_listdata: 
        i_numname[0] = w_listdata
        i_numname[1] = i_list[i_numname[0]]
        i_text = i_numname[1]
        
    return i_text, i_numname, c_listdata, w_listdata

def widgit_txt_but(i_text, i_list, i_numname, i_vlist):
    btn_add, btn_del, i_text = widgit_txt_manip(i_text)
    i_text, i_numname, c_listdata, w_listdata = widgit_list_manip(i_text, i_list, i_numname, i_vlist)
    return btn_add, btn_del, i_text, i_numname, w_listdata

def widgit_color_but(i_text, i_list, i_numname, i_vlist):
    btn_add, btn_del, i_text = widgit_txt_manip(i_text)
    i_text, i_numname, c_listdata, w_listdata = widgit_list_manip(i_text, i_list, i_numname, i_vlist)
    return btn_add, btn_del, i_text, i_numname, w_listdata

def widgit_dict_txt(dict_data, dict_name, ctrl_txt, ctrl_type):
    paramfound = False
    ismodded = False

    ctrl_data = ''
    if dict_data != None:
        if dict_name in dict_data: 
            ctrl_data = dict_data[dict_name]
            paramfound = True

    if paramfound:
        if ctrl_type == 0: ismodded, ctrl_data = imgui.input_text(ctrl_txt, ctrl_data)
        if ctrl_type == 1: ismodded, ctrl_data = imgui.input_int(ctrl_txt, ctrl_data)
        if ctrl_type == 2: ismodded, ctrl_data = imgui.input_float(ctrl_txt, ctrl_data)
        if ismodded:
            if dict_data == None: dict_data = {}
            dict_data[dict_name] = ctrl_data
    else:
        if imgui.button('Create '+ctrl_txt): 
            ismodded = True
            if dict_data == None: dict_data = {}
            dict_data[dict_name] = ''

    return ismodded, dict_data

def widgit_visualmod(visual_data):
    ismodded = False
    obj_color = None
    if visual_data:
        if 'color' in visual_data: obj_color = visual_data['color']

    name_modded, visual_data = widgit_dict_txt(visual_data, 'name', 'Name', 0)
    if name_modded: ismodded = True

    if obj_color != None:
        c_color, v_color = imgui.color_edit3('Color', obj_color)
        if c_color:
            ismodded = True
            visual_data['color'] = v_color
    else:
        if visual_data == None: visual_data = {}
        if imgui.button('Create Color'): visual_data['color'] = [0,0,0]

    return ismodded, visual_data

def current_txt(i_text, i_type):
    imgui.text("Current "+i_type+": "+i_text if i_text else "No "+i_type+" Selected")

def visual_txt(i_text, visual_data):
    vispart = i_text
    if visual_data: vispart += ' - '+visual_data['name'] if 'name' in visual_data else ''
    return vispart

# --------------------------------------------------------------------------------- Vars

g_current_object = [0, None]
g_current_cat = [0, None]
g_current_param = [0, None]
g_current_map = [0, None]
g_current_group = [0, None]
g_current_drumset = [0, None]
g_current_colorset = [0, None]

# ####################################################################################################
# ####################################################################################################
# --- Category List
# ####################################################################################################
# ####################################################################################################

txtbox_cat_name = ''

def window___category_list():
    window_data = hello_imgui.DockableWindow()
    window_data.label = "Category List"
    window_data.dock_space_name = "LeftSpace"
    window_data.gui_function = widgits___category_list
    return window_data

def widgits___category_list():
    global txtbox_cat_name
    global main_dataset
    global g_current_cat
    current_txt(g_current_cat[1], 'Category')
    imgui.separator()
    btn_add, btn_del, txtbox_cat_name, g_current_cat, ismodded = widgit_txt_but(txtbox_cat_name, main_dataset.category_list, g_current_cat, None)
    if btn_add: 
        main_dataset.category_add(txtbox_cat_name)
        g_current_cat = [0, main_dataset.category_list[g_current_cat[0]]]
    if btn_del: 
        if main_dataset.category_del(txtbox_cat_name): g_current_cat[0] = 0

# ####################################################################################################
# ####################################################################################################
# --- Object Visual Window
# ####################################################################################################
# ####################################################################################################

def window___object_vis_editor():
    window_data = hello_imgui.DockableWindow()
    window_data.label = "Object Editor"
    window_data.dock_space_name = "objvisSpace"
    window_data.gui_function = widgits___object_vis_editor
    return window_data

def widgits___object_vis_editor():
    global main_dataset
    global g_current_cat
    global g_current_object

    for nameval in [['group','Group'],['datadef','DataDef'],['datadef_struct','DataDef Struct']]:
        group_isobjfound, group_data = main_dataset.object_var_get(nameval[0], g_current_cat[1], g_current_object[1])
        if group_isobjfound:
            if group_data == None: group_data = ''
            c_pard_group, v_pard_group = imgui.input_text(nameval[1], group_data)
            if c_pard_group: main_dataset.object_var_set(nameval[0], g_current_cat[1], g_current_object[1], v_pard_group)

# ####################################################################################################
# ####################################################################################################
# --- Object List Window
# ####################################################################################################
# ####################################################################################################

txtbox_object_name = ''

def window___object_list():
    window_data = hello_imgui.DockableWindow()
    window_data.label = "Object List"
    window_data.dock_space_name = "LeftSpaceObj"
    window_data.gui_function = widgits___object_list
    return window_data

def widgits___object_list():
    global txtbox_object_name
    global main_dataset
    global g_current_object

    if main_dataset.category_list:
        catobj_list = main_dataset.object_list(g_current_cat[1])
        if catobj_list != None:

            catobj_list_vis = []
            for catobjn in catobj_list:
                isobjfound, visual_data = main_dataset.object_visual_get(g_current_cat[1], catobjn)
                catobj_list_vis.append(visual_txt(catobjn, visual_data))

            obj_id = main_dataset.category_list[g_current_cat[0]]
            current_txt(g_current_object[1], 'Object')
            imgui.separator()
            btn_add, btn_del, txtbox_object_name, g_current_object, ismodded = widgit_txt_but(txtbox_object_name, catobj_list, g_current_object, catobj_list_vis)
            if btn_add: 
                main_dataset.object_add(g_current_cat[1], txtbox_object_name)
            if btn_del: 
                if main_dataset.object_del(g_current_cat[1], txtbox_object_name): g_current_object[0] = 0

# ####################################################################################################
# ####################################################################################################
# --- Param List Window
# ####################################################################################################
# ####################################################################################################

txtbox_param_name = ''
g_current_param_num = 0

def window___param_list():
    window_data = hello_imgui.DockableWindow()
    window_data.label = "Param List"
    window_data.dock_space_name = "ParamListSpace"
    window_data.gui_function = widgits___param_list_selector
    return window_data

def widgits___param_list_selector():
    global g_current_object
    global g_current_cat
    global g_current_param
    global txtbox_param_name

    if g_current_cat[1] and g_current_object[1]:
        paramlist = main_dataset.params_list(g_current_cat[1], g_current_object[1])
        if paramlist == None:
            if imgui.button('Create Params'): main_dataset.params_create(g_current_cat[1], g_current_object[1])
        else: 
            btn_add, btn_del, txtbox_param_name, g_current_param, ismodded = widgit_txt_but(txtbox_param_name, paramlist, g_current_param, None)
            if btn_add: main_dataset.params_i_add(g_current_cat[1], g_current_object[1], txtbox_param_name)
            if btn_del: main_dataset.params_i_del(g_current_cat[1], g_current_object[1], txtbox_param_name)

# ####################################################################################################
# ####################################################################################################
# --- Visual Editor Window
# ####################################################################################################
# ####################################################################################################

visedit_mode = 'object'

def window___visual_editor():
    window_data = hello_imgui.DockableWindow()
    window_data.label = "Visual Editor"
    window_data.dock_space_name = "VisualEditor"
    window_data.gui_function = widgits___visual_editor
    return window_data

def widgits___visual_editor():
    global visedit_mode
    global main_dataset
    global g_current_cat
    global g_current_object
    global g_current_group
    global g_current_drumset

    imgui.text('Mode: '+visedit_mode)
    if imgui.button('Object'): visedit_mode = 'object'
    imgui.same_line()
    if imgui.button('Group'): visedit_mode = 'group'
    imgui.same_line()
    if imgui.button('Drum'): visedit_mode = 'drum'
    imgui.separator()

    if visedit_mode == 'object':
        visual_isobjfound, visual_data = main_dataset.object_visual_get(g_current_cat[1], g_current_object[1])
        if visual_isobjfound:
            vismodded, visual_data = widgit_visualmod(visual_data)
            if vismodded and visual_data: main_dataset.object_visual_set(g_current_cat[1], g_current_object[1], visual_data)
        
    if visedit_mode == 'group':
        grouplist = main_dataset.groups_list(g_current_cat[1])
        if g_current_group[1] and grouplist:
            isobjfound, visual_data = main_dataset.groups_visual_get(g_current_cat[1], g_current_group[1])
            vismodded, visual_data = widgit_visualmod(visual_data)
            if vismodded and visual_data: main_dataset.groups_visual_set(g_current_cat[1], g_current_group[1], visual_data)

    if visedit_mode == 'drum':
        drumsetlist = main_dataset.drumset_list(g_current_cat[1], g_current_object[1])
        if g_current_cat[1] and g_current_object[1] and g_current_drumset[1] and drumsetlist:
            isobjfound, visual_data = main_dataset.drumset_visual_get(g_current_cat[1], g_current_object[1], g_current_drumset[1])
            vismodded, visual_data = widgit_visualmod(visual_data)
            if vismodded and visual_data: main_dataset.drumset_visual_set(g_current_cat[1], g_current_object[1], g_current_drumset[1], visual_data)

# ####################################################################################################
# ####################################################################################################
# --- Data Editor Window
# ####################################################################################################
# ####################################################################################################

paramvaltype = ['none', 'int', 'float', 'bool', 'string']

def window___param_editor():
    window_data = hello_imgui.DockableWindow()
    window_data.label = "Param Editor"
    window_data.dock_space_name = "DataEditorSpace"
    window_data.gui_function = widgits___param_editor
    return window_data

def widgits___param_editor():
    global g_current_object
    global g_current_cat
    global g_current_param
    global main_dataset

    if main_dataset.params_list(g_current_cat[1], g_current_object[1]) != None and g_current_param[1]:
        paramname = g_current_param[1]

        paramdata = main_dataset.params_i_get(g_current_cat[1], g_current_object[1], paramname)
        if paramdata != None:
            if paramname: imgui.text( 'Param: '+ paramname )
            imgui.separator()
            ismodded = False

            c_prd_name, v_prd_name = imgui.input_text('Name', paramdata[5])

            for valtypetable in [['Bool','bool'],['Int','int'],['Float','float'],['String','string']]:
                if imgui.button(valtypetable[0]): 
                    paramdata[1] = valtypetable[1]
                    ismodded = True
                imgui.same_line()

            imgui.text('Type:'+paramdata[1])

            c_prd_noauto, v_prd_noauto = imgui.checkbox('Is Data', paramdata[0])

            if c_prd_name: 
                ismodded = True
                paramdata[5] = v_prd_name
            if c_prd_noauto: 
                ismodded = True
                paramdata[0] = v_prd_noauto

            imgui.separator()

            if paramdata[1] in ['int', 'float', 'bool']:
                if isinstance(paramdata[2], str): paramdata[2] = 0
                if isinstance(paramdata[3], str): paramdata[3] = 0
                if isinstance(paramdata[4], str): paramdata[4] = 0

            if paramdata[1] == 'int':
                paramdata[2] = int(paramdata[2])
                paramdata[3] = int(paramdata[3]) if paramdata[3] != None else 0
                paramdata[4] = int(paramdata[4]) if paramdata[4] != None else 0

                c_prd_def, v_prd_def = imgui.input_int('Defualt', paramdata[2])
                c_prd_minmax, v_prd_min, v_prd_max = imgui.drag_int_range2('Min-Max', paramdata[3], paramdata[4])

                if c_prd_def: 
                    ismodded = True
                    paramdata[2] = int(v_prd_def)
                if c_prd_minmax: 
                    ismodded = True
                    paramdata[3] = int(v_prd_min)
                    paramdata[4] = int(v_prd_max)
        
            if paramdata[1] == 'float':
                paramdata[2] = float(paramdata[2])
                paramdata[3] = float(paramdata[3]) if paramdata[3] != None else 0
                paramdata[4] = float(paramdata[4]) if paramdata[4] != None else 0

                c_prd_def, v_prd_def = imgui.input_float('Defualt', paramdata[2])
                c_prd_minmax, v_prd_min, v_prd_max = imgui.drag_float_range2('Min-Max', paramdata[3], paramdata[4])

                if c_prd_def: 
                    ismodded = True
                    paramdata[2] = v_prd_def
                if c_prd_minmax: 
                    ismodded = True
                    paramdata[3] = v_prd_min
                    paramdata[4] = v_prd_max

            if paramdata[1] == 'string':
                paramdata[2] = str(paramdata[2])
                paramdata[3] = None
                paramdata[4] = None

                c_prd_def, v_prd_def = imgui.input_text('Defualt', paramdata[2])

                if c_prd_def: 
                    ismodded = True
                    paramdata[2] = v_prd_def

            if paramdata[1] == 'bool':
                paramdata[2] = int(paramdata[2])
                paramdata[3] = None
                paramdata[4] = None

                c_prd_def, v_prd_def = imgui.checkbox('Defualt', bool(paramdata[2]))

                if c_prd_def: 
                    ismodded = True
                    paramdata[2] = v_prd_def

            if ismodded: 
                main_dataset.params_i_set(g_current_cat[1], g_current_object[1], paramname, paramdata)

# ####################################################################################################
# ####################################################################################################
# --- Extra Editor
# ####################################################################################################
# ####################################################################################################

txtbox_midito_name = ''
int_midito_bank = 0
int_midito_patch = 0
int_midito_isdrum = False

def window___gm_map():
    window_data = hello_imgui.DockableWindow()
    window_data.label = "MIDI To"
    window_data.dock_space_name = "ExEditorSpace"
    window_data.gui_function = widgits___gm_map
    return window_data

def widgits___gm_map():
    global txtbox_midito_name
    global int_midito_bank
    global int_midito_patch
    global int_midito_isdrum
    global g_current_map
    if g_current_cat[1]:
        maplist = main_dataset.midito_list(g_current_cat[1])
        if maplist != None:
            btn_add, btn_del, txtbox_midito_name = widgit_txt_manip(txtbox_midito_name)
            _, int_midito_bank = imgui.input_int('bank', clamp(int_midito_bank, 0, 127))
            _, int_midito_patch = imgui.input_int('patch', clamp(int_midito_patch, 0, 127))
            _, int_midito_isdrum = imgui.checkbox('is drum', int_midito_isdrum)
            maplist_vis = []
            for x in maplist:
                value_b,value_p,value_d = main_dataset.midito_get(g_current_cat[1], x)
                vispart = ('D' if value_d == True else 'I ')+'   '+str(value_b)+'   '+str(value_p)+'   '+x
                visual_isobjfound, visual_data = main_dataset.object_visual_get(g_current_cat[1], x)
                maplist_vis.append(visual_txt(vispart, visual_data))
            txtbox_midito_name, g_current_map, c_listdata, w_listdata = widgit_list_manip(txtbox_midito_name, maplist, g_current_map, maplist_vis)
            if c_listdata and g_current_map[1]:
                value_b,value_p,value_d = main_dataset.midito_get(g_current_cat[1], g_current_map[1])
                int_midito_bank = value_b
                int_midito_patch = value_p
                int_midito_isdrum = value_d
            if btn_add: main_dataset.midito_add(g_current_cat[1], txtbox_midito_name, int_midito_bank, int_midito_patch, int_midito_isdrum)
            if btn_del: main_dataset.midito_del(g_current_cat[1], txtbox_midito_name)
        else: 
            if imgui.button('Create MIDI Map'): main_dataset.midito_create(g_current_cat[1])

# ####################################################################################################

txtbox_group_name = ''
txtbox_group_data = ''

def window___group_list():
    window_data = hello_imgui.DockableWindow()
    window_data.label = "Groups"
    window_data.dock_space_name = "ExEditorSpace"
    window_data.gui_function = widgits___group_list
    return window_data

def widgits___group_list():
    global txtbox_group_name
    global txtbox_group_data
    global g_current_group
    global g_current_cat
    if g_current_cat[1]:
        grouplist = main_dataset.groups_list(g_current_cat[1])
        if grouplist != None:
            btn_add, btn_del, txtbox_group_name, g_current_group, ismodded = widgit_txt_but(txtbox_group_name, grouplist, g_current_group, None)
            if btn_add: main_dataset.groups_add(g_current_cat[1], txtbox_group_name)
            if btn_del: main_dataset.groups_del(g_current_cat[1], txtbox_group_name)
        else: 
            if imgui.button('Create GroupList'): main_dataset.groups_create(g_current_cat[1])

# ####################################################################################################

txtbox_drumset_name = ''

def window___drumset_editor():
    window_data = hello_imgui.DockableWindow()
    window_data.label = "Drumset"
    window_data.dock_space_name = "ExEditorSpace"
    window_data.gui_function = widgits___drumset_editor
    return window_data

def widgits___drumset_editor():
    global g_current_cat
    global g_current_object
    global g_current_drumset
    global txtbox_drumset_name
    if g_current_cat[1] and g_current_object[1]:
        drumsetlist = main_dataset.drumset_list(g_current_cat[1], g_current_object[1])
        if drumsetlist != None:
            drumsetlist_vis = []
            for drumid in drumsetlist:
                visualtxt = None
                isfound, visuald = main_dataset.drumset_visual_get(g_current_cat[1], g_current_object[1], drumid)
                if isfound and visuald: visualtxt = visuald['name'] if 'name' in visuald else None
                drumsetlist_vis.append(visual_txt(drumid, visualtxt))
            btn_add, btn_del, txtbox_drumset_name, g_current_drumset, ismodded = widgit_txt_but(txtbox_drumset_name, drumsetlist, g_current_drumset, drumsetlist_vis)
            if btn_add: main_dataset.drumset_i_set(g_current_cat[1], g_current_object[1], txtbox_drumset_name)
            if btn_del: main_dataset.drumset_i_del(g_current_cat[1], g_current_object[1], txtbox_drumset_name)
        else: 
            if imgui.button('Create Drumset'): main_dataset.drumset_create(g_current_cat[1], g_current_object[1])

# ####################################################################################################

txtbox_colorset_name = ''
colorbox_colorset_color = [0,0,0]

def window___colorset_list():
    window_data = hello_imgui.DockableWindow()
    window_data.label = "Colorset List"
    window_data.dock_space_name = "VisualEditor"
    window_data.gui_function = widgits___colorset_list
    return window_data

def widgits___colorset_list():
    global g_current_cat
    global g_current_colorset
    global txtbox_colorset_name
    global colorbox_colorset_color
    if g_current_cat[1]:
        colorsetlist = main_dataset.colorset_list(g_current_cat[1])
        if colorsetlist != None:
            #colorset = main_dataset.colorset_e_list(g_current_cat[1], g_current_colorset[1])
            #c_btn_add, c_btn_del, colorbox_colorset_color = widgit_color_manip(colorbox_colorset_color)
            #if colorset != None:
            #    for color in colorset:
            #        imgui.color_edit3('##', color)
            #imgui.separator()
            btn_add, btn_del, txtbox_colorset_name, g_current_colorset, w_listdata = widgit_txt_but(txtbox_colorset_name, colorsetlist, g_current_colorset, None)
            if btn_add: 
                print(txtbox_colorset_name)
                main_dataset.colorset_add(g_current_cat[1], txtbox_colorset_name)
        else: 
            if imgui.button('Create Colorset'): main_dataset.colorset_create(g_current_cat[1])

def window___colorset_editor():
    window_data = hello_imgui.DockableWindow()
    window_data.label = "Colorset Editor"
    window_data.dock_space_name = "ExEditorSpace"
    window_data.gui_function = widgits___colorset_editor
    return window_data

def widgits___colorset_editor():
    global g_current_cat
    global g_current_colorset
    global txtbox_colorset_name
    global colorbox_colorset_color
    if g_current_cat[1]:
        colorsetlist = main_dataset.colorset_list(g_current_cat[1])
        if colorsetlist != None:
            colorset = main_dataset.colorset_e_list(g_current_cat[1], g_current_colorset[1])
            c_btn_add, c_btn_del, colorbox_colorset_color = widgit_color_manip(colorbox_colorset_color)
            if c_btn_add: main_dataset.colorset_e_add(g_current_cat[1], g_current_colorset[1], colorbox_colorset_color)
            imgui.separator()
            if colorset != None:
                for color in colorset: imgui.color_edit3('##', color)

# ####################################################################################################
# ####################################################################################################
# --- Param Viewer Window
# ####################################################################################################
# ####################################################################################################

def window___param_viewer():
    window_data = hello_imgui.DockableWindow()
    window_data.label = "Param Viewer"
    window_data.dock_space_name = "ParamViewerSpace"
    window_data.gui_function = widgits___param_viewer
    return window_data

def widgits___param_viewer():
    global g_current_object
    global g_current_cat
    global g_current_param
    global main_dataset

    table_flags = (
        imgui.TableFlags_.row_bg
        | imgui.TableFlags_.borders
        | imgui.TableFlags_.sizing_stretch_same
    )
    imgui.begin_child("TableChild", hello_imgui.em_to_vec2(0, 0))
    if imgui.begin_table("Apps", 8, table_flags):

        imgui.table_setup_column("ID", 0, 0.4)
        imgui.table_setup_column("NoAuto", 0, 0.15)
        imgui.table_setup_column("Type", 0, 0.2)
        imgui.table_setup_column("Defualt", 0, 0.3)
        imgui.table_setup_column("Min", 0, 0.3)
        imgui.table_setup_column("Max", 0, 0.3)
        imgui.table_setup_column("Name", 0, 0.4)
        imgui.table_setup_column("Name", 0, 0.4)

        imgui.table_next_column()

        for textdata in ['ID','NoAuto','Type','Defualt','Min','Max','Name']:
            imgui.text(textdata)
            imgui.table_next_column()

        # [pv_noauto,pv_type,pv_def,pv_min,pv_max,pv_name]

        if g_current_cat[1] and g_current_object[1]:
            paramlist = main_dataset.params_list(g_current_cat[1], g_current_object[1])
            if paramlist:
                for paramname in paramlist:
                    imgui.table_next_row()
                    imgui.table_next_column()
                    imgui.text(paramname)
                    paramdata = main_dataset.params_i_get(g_current_cat[1], g_current_object[1], paramname)

                    imgui.table_next_column()
                    imgui.text(str(paramdata[0]) if paramdata != None else '')
                    imgui.table_next_column()
                    imgui.text(str(paramdata[1]) if paramdata != None else '')
                    imgui.table_next_column()

                    pi_def = False
                    pi_min = False
                    pi_max = False


                    if paramdata[1] == 'float':
                        imgui.push_item_width(100)
                        pi_def, paramdata[2] = imgui.input_float('##def_'+paramname, paramdata[2])
                        imgui.table_next_column()
                        imgui.push_item_width(100)
                        pi_min, paramdata[3] = imgui.input_float('##min_'+paramname, paramdata[3])
                        imgui.table_next_column()
                        imgui.push_item_width(100)
                        pi_max, paramdata[4] = imgui.input_float('##max_'+paramname, paramdata[4])

                    if paramdata[1] == 'int':
                        imgui.push_item_width(100)
                        pi_def, paramdata[2] = imgui.input_int('##def_'+paramname, int(paramdata[2]))
                        imgui.table_next_column()
                        imgui.push_item_width(100)
                        pi_min, paramdata[3] = imgui.input_int('##min_'+paramname, int(paramdata[3]))
                        imgui.table_next_column()
                        imgui.push_item_width(100)
                        pi_max, paramdata[4] = imgui.input_int('##max_'+paramname, int(paramdata[4]))

                    if paramdata[1] == 'string':
                        imgui.push_item_width(100)
                        pi_def, paramdata[2] = imgui.input_text('##def_'+paramname, str(paramdata[2]))
                        imgui.table_next_column()
                        imgui.text('')
                        imgui.table_next_column()
                        imgui.text('')

                    if paramdata[1] == 'bool':
                        imgui.push_item_width(100)
                        pi_def, paramdata[2] = imgui.checkbox('##def_'+paramname, paramdata[2])
                        imgui.table_next_column()
                        imgui.text('')
                        imgui.table_next_column()
                        imgui.text('')

                    imgui.table_next_column()
                    imgui.push_item_width(200)
                    pi_name, paramdata[5] = imgui.input_text('##name_'+paramname, paramdata[5])

                    if paramdata[1] == 'float':
                        imgui.table_next_column()
                        imgui.text( str(xtramath.between_to_one(paramdata[3], paramdata[4], paramdata[2])) )

                    if True in [pi_name, pi_def, pi_min, pi_max]: 
                        main_dataset.params_i_set(g_current_cat[1], g_current_object[1], paramname, paramdata)

        imgui.end_table()
    imgui.end_child()


# ####################################################################################################
# ####################################################################################################
# --- Docking Data
# ####################################################################################################
# ####################################################################################################

def create_default_docking_splits() -> List[hello_imgui.DockingSplit]:
    split_w_cat = hello_imgui.DockingSplit()
    split_w_cat.initial_dock = "MainDockSpace"
    split_w_cat.new_dock = "LeftSpace"
    split_w_cat.direction = imgui.Dir_.left
    split_w_cat.ratio = 0.3

    split_w_objvis = hello_imgui.DockingSplit()
    split_w_objvis.initial_dock = "LeftSpace"
    split_w_objvis.new_dock = "objvisSpace"
    split_w_objvis.direction = imgui.Dir_.up
    split_w_objvis.ratio = 0.2

    split_w_objl = hello_imgui.DockingSplit()
    split_w_objl.initial_dock = "LeftSpace"
    split_w_objl.new_dock = "LeftSpaceObj"
    split_w_objl.direction = imgui.Dir_.up
    split_w_objl.ratio = 0.65

    split_w_param_list = hello_imgui.DockingSplit()
    split_w_param_list.initial_dock = "MainDockSpace"
    split_w_param_list.new_dock = "ParamListSpace"
    split_w_param_list.direction = imgui.Dir_.left
    split_w_param_list.ratio = 0.4

    split_w_param_editor = hello_imgui.DockingSplit()
    split_w_param_editor.initial_dock = "ParamListSpace"
    split_w_param_editor.new_dock = "DataEditorSpace"
    split_w_param_editor.direction = imgui.Dir_.up
    split_w_param_editor.ratio = 0.3

    split_w_extra_editor = hello_imgui.DockingSplit()
    split_w_extra_editor.initial_dock = "MainDockSpace"
    split_w_extra_editor.new_dock = "ExEditorSpace"
    split_w_extra_editor.direction = imgui.Dir_.left
    split_w_extra_editor.ratio = 0.3

    split_w_visual = hello_imgui.DockingSplit()
    split_w_visual.initial_dock = "ExEditorSpace"
    split_w_visual.new_dock = "VisualEditor"
    split_w_visual.direction = imgui.Dir_.up
    split_w_visual.ratio = 0.3

    split_w_param_viewer = hello_imgui.DockingSplit()
    split_w_param_viewer.initial_dock = "MainDockSpace"
    split_w_param_viewer.new_dock = "ParamViewerSpace"
    split_w_param_viewer.direction = imgui.Dir_.left
    split_w_param_viewer.ratio = 1

    splits = [
        split_w_cat, 
        split_w_objvis, 
        split_w_objl,
        split_w_extra_editor, 
        split_w_visual,
        split_w_param_list,
        split_w_param_editor, 
        split_w_param_viewer, 
        ]
    return splits

def create_dockable_windows() -> List[hello_imgui.DockableWindow]:
    return [
        window___category_list(), 
        window___object_list(),
        window___object_vis_editor(), 
        window___param_list(),
        window___visual_editor(),
        #window___mode(),
        window___gm_map(),
        window___group_list(),
        window___drumset_editor(),
        window___colorset_list(),
        window___colorset_editor(),
        window___param_editor(),
        window___param_viewer(),
        ]

def create_default_layout() -> hello_imgui.DockingParams:
    docking_params = hello_imgui.DockingParams()
    docking_params.docking_splits = create_default_docking_splits()
    docking_params.dockable_windows = create_dockable_windows()
    return docking_params

# ####################################################################################################
# ####################################################################################################
# --- Main
# ####################################################################################################
# ####################################################################################################

g_dataset = {}



____debug____ = False


def main():
    global main_dataset

    aparser = argparse.ArgumentParser()
    aparser.add_argument("inp", default=None, nargs='?')
    args = aparser.parse_args()
    in_file = args.inp
    print(in_file)

    main_dataset = dv_dataset.dataset(in_file)

    if ____debug____:
        main_dataset.category_add('test1')
        main_dataset.object_add('test1', 'insideobj')
        main_dataset.params_create('test1', 'insideobj')
        main_dataset.params_i_add('test1', 'insideobj', 'yh54vbwh4')
        main_dataset.params_i_add('test1', 'insideobj', '3h5qchq64')
        main_dataset.params_i_add('test1', 'insideobj', '3qvh53q')
        main_dataset.category_add('test2')
        main_dataset.category_add('test3')

    hello_imgui.set_assets_folder(demo_utils.demos_assets_folder())
    runner_params = hello_imgui.RunnerParams()

    runner_params.app_window_params.restore_previous_geometry = True
    runner_params.app_window_params.window_geometry.size = (1000, 600)
    runner_params.app_window_params.window_title = "DawVert DataSet Editor"

    runner_params.docking_params = create_default_layout()

    runner_params.imgui_window_params.default_imgui_window_type = hello_imgui.DefaultImGuiWindowType.provide_full_screen_dock_space
    runner_params.imgui_window_params.enable_viewports = True
    runner_params.imgui_window_params.menu_app_title = "DawVert DataSet Editor"
    runner_params.imgui_window_params.show_menu_bar = True  
    runner_params.imgui_window_params.show_status_bar = True

    hello_imgui.run(runner_params)

    if in_file != None:
        with open(in_file, "w") as fileout:
            json.dump(main_dataset.dataset, fileout, indent=4, sort_keys=True)

if __name__ == "__main__":
    main()