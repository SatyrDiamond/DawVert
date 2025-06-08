import argparse
import json
import sys
import math
sys.path.append('../')
from imgui_bundle import hello_imgui, icons_fontawesome, imgui, immapp, imgui_fig
from imgui_bundle.demos_python import demo_utils
from typing import List

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt






def widgit_list_manip(i_text, i_list, i_numname, i_vlist):
    imgui.push_item_width(200)
    c_listdata, w_listdata = imgui.list_box('##wlistm', i_numname[0], i_list if i_vlist == None else i_vlist)
    if c_listdata: 
        i_numname[0] = w_listdata
        i_numname[1] = i_list[i_numname[0]]
        i_text = i_numname[1]
    return i_text, i_numname, c_listdata, w_listdata

def widgit_txt_manip(a_text, b_text):
    imgui.push_item_width(100)
    wc_atxtfield, wi_atxtfield = imgui.input_text('##a_', a_text)
    imgui.same_line()
    wc_btxtfield, wi_btxtfield = imgui.input_text('##b_', b_text)
    if wc_atxtfield: a_text = wi_atxtfield
    if wc_btxtfield: b_text = wi_btxtfield
    btn_add = False
    btn_del = False
    if a_text and b_text:
        imgui.same_line()
        btn_add = imgui.button("Add")
        imgui.same_line()
        btn_del = imgui.button("Del")
    return btn_add, btn_del, a_text, b_text

p_numname = [0, None]
a_text, b_text, l_text = '', '', ''
wc_i, codetxt = '', ''

prevnum = 0

def widgits___main():
    global a_text
    global b_text
    global l_text
    global wc_i
    global codetxt
    global p_numname
    global poslist
    global prevnum

    imgui.text('Input:')
    imgui.push_item_width(300)
    wc_i, codetxt = imgui.input_text_multiline('in_code', codetxt)


    imgui.separator()
    imgui.text('Pos List:')
    btn_add, btn_del, a_text, b_text = widgit_txt_manip(a_text, b_text)

    if btn_add: 
        try: 
            out = [float(a_text), float(b_text)]
            if out not in poslist: poslist.append(out)
        except: pass

    if btn_del: 
        try: 
            out = [float(a_text), float(b_text)]
            if out in poslist: poslist.remove(out)
        except: pass

    l_text, p_numname, c_listdata, ismodded = widgit_list_manip(l_text, poslist, p_numname, [str(x[0])+'  ,  '+str(x[1]) for x in poslist])
    if prevnum != ismodded: a_text, b_text = str(p_numname[1][0]), str(p_numname[1][1])
    prevnum = ismodded

def window___main():
    window_data = hello_imgui.DockableWindow()
    window_data.label = "Input"
    window_data.dock_space_name = "MainDockSpace"
    window_data.gui_function = widgits___main
    return window_data



def widgits___out():
    global codetxt
    global poslist

    imgui.text('Graph')
    static_fig, static_ax = plt.subplots()
    plt.plot([float(x[0]) for x in poslist], color='g')
    plt.plot([float(x[1]) for x in poslist], color='b')

    outvals = []
    try:
        for x in [float(d[0]) for d in poslist]:
            outvals.append( eval(codetxt) )
        plt.plot(outvals, color='r')
    except:
        pass


    imgui_fig.fig("OutPlot", static_fig, refresh_image=True)



def window___out():
    window_data = hello_imgui.DockableWindow()
    window_data.label = "Output"
    window_data.dock_space_name = "LeftSpace"
    window_data.gui_function = widgits___out
    return window_data














def create_default_docking_splits() -> List[hello_imgui.DockingSplit]:
    split_w_main = hello_imgui.DockingSplit()
    split_w_main.initial_dock = "MainDockSpace"
    split_w_main.new_dock = "LeftSpace"
    split_w_main.direction = imgui.Dir_.right
    split_w_main.ratio = 0.6

    split_w_outdata = hello_imgui.DockingSplit()
    split_w_outdata.initial_dock = "LeftSpace"
    split_w_outdata.new_dock = "OutputData"
    split_w_outdata.direction = imgui.Dir_.right
    split_w_outdata.ratio = 0.1

    splits = [
        split_w_main,
        split_w_outdata
        ]
    return splits

def create_dockable_windows() -> List[hello_imgui.DockableWindow]:
    return [
        window___main(),
        window___out()
        ]

def create_default_layout() -> hello_imgui.DockingParams:
    docking_params = hello_imgui.DockingParams()
    docking_params.docking_splits = create_default_docking_splits()
    docking_params.dockable_windows = create_dockable_windows()
    return docking_params

def main():
    global poslist


    poslist = []

    aparser = argparse.ArgumentParser()
    aparser.add_argument("-i", default=None)

    argsd = vars(aparser.parse_args())

    if argsd['i'] != None:
        inputfile = argsd['i']
        databytes_str = open(inputfile, "rb")
        for linedata in databytes_str.readlines():
            vardata = linedata.decode().strip().split(',')
            poslist.append([vardata[0],vardata[1]])
            print()
    

    hello_imgui.set_assets_folder(demo_utils.demos_assets_folder())
    runner_params = hello_imgui.RunnerParams()

    runner_params.app_window_params.restore_previous_geometry = True
    runner_params.app_window_params.window_geometry.size = (1000, 600)
    runner_params.app_window_params.window_title = "Log Figure-out-inator"

    runner_params.docking_params = create_default_layout()

    runner_params.imgui_window_params.default_imgui_window_type = hello_imgui.DefaultImGuiWindowType.provide_full_screen_dock_space
    runner_params.imgui_window_params.enable_viewports = True
    runner_params.imgui_window_params.menu_app_title = "Log Figure-out-inator"
    runner_params.imgui_window_params.show_menu_bar = True  
    runner_params.imgui_window_params.show_status_bar = True

    hello_imgui.run(runner_params)

if __name__ == "__main__":
    main()