from enum import Enum
from imgui_bundle import hello_imgui, icons_fontawesome, imgui, immapp
from imgui_bundle.demos_python import demo_utils
from typing import List
import argparse
import json
from objects import dv_datadef
import sys

table_flags = (
    imgui.TableFlags_.row_bg
    | imgui.TableFlags_.borders
    | imgui.TableFlags_.resizable
    | imgui.TableFlags_.sizing_stretch_same
)

def widgit_list_manip(i_text, i_list, i_numname, i_vlist):
    imgui.separator()
    imgui.push_item_width(400)
    c_listdata, w_listdata = imgui.list_box('##wlistm', i_numname[0], i_list if i_vlist == None else i_vlist)
    if c_listdata: 
        i_numname[0] = w_listdata
        i_numname[1] = i_list[i_numname[0]]
        i_text = i_numname[1]
    return i_text, i_numname, c_listdata, w_listdata

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

def widgit_txt_but(i_text, i_list, i_numname, i_vlist):
    btn_add, btn_del, i_text = widgit_txt_manip(i_text)
    i_text, i_numname, c_listdata, ismodded = widgit_list_manip(i_text, i_list, i_numname, i_vlist)
    return btn_add, btn_del, i_text, i_numname, ismodded

# ####################################################################################################
# ####################################################################################################
# --- Struct List
# ####################################################################################################
# ####################################################################################################

g_current_struct = [0, None]
txtbox_struct_name = ''

def window___struct_list():
    window_data = hello_imgui.DockableWindow()
    window_data.label = "Struct List"
    window_data.dock_space_name = "MainDockSpace"
    window_data.gui_function = widgits___struct_list
    return window_data

def widgits___struct_list():
    global txtbox_struct_name
    global g_current_struct
    structlist = [x for x in datadef.structs]
    btn_add, btn_del, txtbox_struct_name, g_current_struct, ismodded = widgit_txt_but(txtbox_struct_name, structlist, g_current_struct, None)

    if ismodded: datadef.parse('main',databytes)

    if btn_add and txtbox_struct_name not in datadef.structs: datadef.structs[txtbox_struct_name] = []
    if btn_del and txtbox_struct_name in datadef.structs: del datadef.structs[txtbox_struct_name]

    if btn_add or btn_del: datadef.parse('main',databytes)

# ####################################################################################################
# ####################################################################################################
# --- Struct Data
# ####################################################################################################
# ####################################################################################################


def widgits___cmd_edit(input_list, parttxt):
    for listnum in range(len(input_list)):
        listpart = input_list[listnum]
        listpartid = str(listnum)+'_'+parttxt
        imgui.push_item_width(90)

        if listpart[0] in ['raw_part', 'string_part', 'dstring_part', 'list_part']:
            imgui.text('V')
            imgui.same_line()

        c_txttype, i_txttype = imgui.input_text('##'+listpartid+'_lp', listpart[0])
        if c_txttype: 
            listpart[0] = i_txttype
            datadef.parse('main',databytes)

        if listpart[0] in ['raw', 'struct', 'string', 'dstring', 'list', 'getvar', 'skip_n']:
            imgui.same_line()
            c_txtnum, i_txtnum = imgui.input_text('##'+listpartid+'_lp_num', listpart[1])
            if c_txtnum: 
                listpart[1] = i_txtnum
                datadef.parse('main',databytes)


    imgui.same_line()
    btn_add = imgui.button("+##"+parttxt)
    if btn_add: 
        input_list.append(['byte', ''])
        datadef.parse('main',databytes)

    btn_rem = False
    if input_list:
        imgui.same_line()
        btn_rem = imgui.button("-##"+parttxt)
        if btn_rem: 
            del input_list[-1]
            datadef.parse('main',databytes)

def window___struct_edit():
    window_data = hello_imgui.DockableWindow()
    window_data.label = "Struct Editor"
    window_data.dock_space_name = "StructEditData"
    window_data.gui_function = widgits___struct_edit
    return window_data

def widgits___struct_edit():
    if g_current_struct[1] != None:
        if g_current_struct[1] in datadef.structs:
            imgui.same_line()
            btn_ptadd = imgui.button("Add")

            partdata = datadef.structs[g_current_struct[1]]

            is_changed = False

            if partdata:
                imgui.begin_child("TableChild", hello_imgui.em_to_vec2(0, 0))
                if imgui.begin_table("Apps", 5, table_flags):

                    imgui.table_setup_column("id", 0, 0.05)
                    imgui.table_setup_column("btns", 0, 0.05)
                    imgui.table_setup_column("name", 0, 0.2)
                    imgui.table_setup_column("type", 0, 0.1)
                    imgui.table_setup_column("blocks", 0, 0.8)

                    delnum = None

                    for partnum in range(len(partdata)):
                        parttxt = str(partnum)
                        imgui.table_next_column()
                        imgui.text(parttxt)
                        imgui.table_next_column()
                        btn_del = imgui.button("-##del"+parttxt)
                        if btn_del: 
                            is_changed = True
                            delnum = partnum
                        imgui.table_next_column()
                        imgui.push_item_width(120)
                        c_txtfield, i_txtfield = imgui.input_text('##'+parttxt+'_name', partdata[partnum][2])
                        if c_txtfield: 
                            is_changed = True
                            partdata[partnum][2] = i_txtfield
                        imgui.table_next_column()
                        c_txttype, i_txttype = imgui.input_text('##'+parttxt+'_type', partdata[partnum][0])
                        if c_txttype: 
                            is_changed = True
                            partdata[partnum][0] = i_txttype
                        imgui.table_next_column()
                        widgits___cmd_edit(partdata[partnum][1], parttxt)
                        imgui.table_next_row()

                    if delnum != None: del partdata[delnum]

                    imgui.end_table()
                imgui.end_child()

                if is_changed: datadef.parse('main',databytes)


            if btn_ptadd: 
                partdata.append(['part', [['byte', '']], ''])
                datadef.parse('main',databytes)






# ####################################################################################################
# ####################################################################################################
# --- Output
# ####################################################################################################
# ####################################################################################################

def window___output():
    window_data = hello_imgui.DockableWindow()
    window_data.label = "Output"
    window_data.dock_space_name = "OutputData"
    window_data.gui_function = widgits___output
    return window_data

def widgits___output():
    if datadef.errored:
        imgui.text(datadef.errormeg)
    else:

        imgui.text("leftover bytes")
        hex_txt = datadef.leftoverbytes[0:64].hex() 
        hex_sep = 2
        hex_leftovertxt = [hex_txt[i:i+hex_sep] for i in range(0, len(hex_txt), hex_sep)]
        if hex_leftovertxt: imgui.text(' '.join(hex_leftovertxt))

        imgui.begin_child("TableChild", hello_imgui.em_to_vec2(0, 0))
        if imgui.begin_table("Apps", 5, table_flags):

            delnum = None

            imgui.table_setup_column("offset", 0, 0.1)
            imgui.table_setup_column("name", 0, 0.3)
            imgui.table_setup_column("pname", 0, 0.3)
            imgui.table_setup_column("type", 0, 0.4)
            imgui.table_setup_column("value", 0, 0.8)

            for debgdata in datadef.debugoutput:
                imgui.table_next_column()
                imgui.text(debgdata[0])
                imgui.table_next_column()
                imgui.text(debgdata[1])
                imgui.table_next_column()
                imgui.text(debgdata[2])
                imgui.table_next_column()
                imgui.text(debgdata[3])
                imgui.table_next_column()
                imgui.text(debgdata[4])
                imgui.table_next_row()

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
    split_w_cat.direction = imgui.Dir_.right
    split_w_cat.ratio = 0.4

    split_w_structedit = hello_imgui.DockingSplit()
    split_w_structedit.initial_dock = "MainDockSpace"
    split_w_structedit.new_dock = "StructEditData"
    split_w_structedit.direction = imgui.Dir_.right
    split_w_structedit.ratio = 0.7

    split_w_structlist = hello_imgui.DockingSplit()
    split_w_structlist.initial_dock = "LeftSpace"
    split_w_structlist.new_dock = "OutputData"
    split_w_structlist.direction = imgui.Dir_.right
    split_w_structlist.ratio = 0.3

    splits = [
        split_w_cat, 
        split_w_structedit, 
        split_w_structlist
        ]
    return splits

def create_dockable_windows() -> List[hello_imgui.DockableWindow]:
    return [
        window___struct_list(),
        window___struct_edit(),
        window___output(),
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

def main():
    global main_dataset
    global datadef
    global databytes
    global g_current_struct
    global txtbox_struct_name

    aparser = argparse.ArgumentParser()
    aparser.add_argument("-d", default=None)
    aparser.add_argument("-f", default=None)

    argsd = vars(aparser.parse_args())

    datadef = dv_datadef.datadef(None)

    if argsd['d'] != None:
        df_file = argsd['d']
        datadef.load_file(df_file)
    
    if argsd['f'] != None:
        dat_file = argsd['f']
        databytes_str = open(dat_file, "rb")
        databytes = databytes_str.read()
    else:
        databytes = b'qwertyuiop[]asdfghjkl;zxcvbnm,./'*100

    g_current_struct = [0, 'main']
    txtbox_struct_name = 'main'

    hello_imgui.set_assets_folder(demo_utils.demos_assets_folder())
    runner_params = hello_imgui.RunnerParams()

    runner_params.app_window_params.restore_previous_geometry = True
    runner_params.app_window_params.window_geometry.size = (1000, 600)
    runner_params.app_window_params.window_title = "DawVert DataDef Editor"

    runner_params.docking_params = create_default_layout()

    runner_params.imgui_window_params.default_imgui_window_type = hello_imgui.DefaultImGuiWindowType.provide_full_screen_dock_space
    runner_params.imgui_window_params.enable_viewports = True
    runner_params.imgui_window_params.menu_app_title = "DawVert DataDef Editor"
    runner_params.imgui_window_params.show_menu_bar = True  
    runner_params.imgui_window_params.show_status_bar = True

    hello_imgui.run(runner_params)

    if argsd['f'] != None:
        datadef.save_file(df_file)

if __name__ == "__main__":
    main()