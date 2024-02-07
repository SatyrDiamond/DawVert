# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_values

def process_r(convproj_obj):
    if convproj_obj.fxrack:

        if 0 in convproj_obj.fxrack:
            fxchannel_obj = convproj_obj.fxrack[0]
            convproj_obj.move_automation(['fxmixer','0','vol'], ['master', 'vol'])
            convproj_obj.move_automation(['fxmixer','0','pan'], ['master', 'pan'])
            fxchannel_obj.params.move(convproj_obj.track_master.params, 'vol')
            fxchannel_obj.params.move(convproj_obj.track_master.params, 'pan')
            convproj_obj.track_master.fxslots_audio = fxchannel_obj.fxslots_audio.copy()
            fxchannel_obj.fxslots_audio = []
            del convproj_obj.fxrack[0]

        fx_trackids = {}
        for trackid, track_obj in convproj_obj.iter_track():
            if track_obj.fxrack_channel > 0:
                if track_obj.fxrack_channel not in fx_trackids: fx_trackids[track_obj.fxrack_channel] = []
                fx_trackids[track_obj.fxrack_channel].append(trackid)
                track_obj.group = 'fxrack_'+str(track_obj.fxrack_channel)
                track_obj.fxrack_channel = -1

        #for fxnum, fxchannel_obj in convproj_obj.fxrack.items()
        for fx_num in fx_trackids:

            if fx_num in convproj_obj.fxrack:
                fxchannel_obj = convproj_obj.fxrack[fx_num]
                fxchannel_obj.sends = {}
                groupid = 'fxrack_'+str(fx_num)
                group_obj = convproj_obj.add_group(groupid)

                convproj_obj.move_automation(['fxmixer',str(fx_num),'pan'], ['group',groupid,'pan'])
                convproj_obj.move_automation(['fxmixer',str(fx_num),'vol'], ['group',groupid,'vol'])
                fxchannel_obj.params.move(group_obj.params, 'vol')
                fxchannel_obj.params.move(group_obj.params, 'pan')
                group_obj.fxslots_audio = fxchannel_obj.fxslots_audio.copy()
                fxchannel_obj.fxslots_audio = []
                group_obj.visual = fxchannel_obj.visual

            print('[compat] fxrack2trackfx: FX to Tracks '+ ', '.join(fx_trackids[fx_num]))
        convproj_obj.fxrack = {}
    return True

def process(convproj_obj, in_compat, out_compat):
    if in_compat == True and out_compat == False:
        if convproj_obj.type in ['r', 'ri']: return process_r(convproj_obj)
        else: return False
    else: return False