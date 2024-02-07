# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

def process(convproj_obj, in_compat, out_compat):
    if in_compat == True and out_compat == False:
        convproj_obj.autoticks_to_autopoints()
        convproj_obj.autopoints_to_pl()
        return True
        
    if in_compat == False and out_compat == True:
        convproj_obj.autopoints_from_pl()
        return True
