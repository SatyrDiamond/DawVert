# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import notelist_data
from functions import data_values

def process(cvpj_l, cvpj_type, in_compat, out_compat):

    if cvpj_type in ['ri','r']:
        if in_compat == out_compat: return False
        #elif in_compat != []:
        #    remainingparams = [x for x in in_compat if x not in out_compat]
        else:
            fxrackdata = cvpj_l['fxrack']
            trackdata = cvpj_l['track_data']

            datatomove = {}
            for fxnum in fxrackdata:
                datatomove[fxnum] = {}
                s_fxrackdata = fxrackdata[fxnum]
                if 'params' in s_fxrackdata:
                    paramsdata = s_fxrackdata['params'].copy()
                    for paramname in out_compat:
                        if paramname in paramsdata: del paramsdata[paramname]
                    for paramname in paramsdata:
                        fxnumstr = str(fxnum)
                        autodata = data_values.nested_dict_get_value(cvpj_l, ['automation', 'fxmixer', fxnumstr, paramname])
                        paramdata = s_fxrackdata['params'][paramname]
                        datatomove[fxnum][paramname] = [paramdata, autodata]

            for track in trackdata:
                s_trackdata = trackdata[track]
                if 'fxrack_channel' in s_trackdata:
                    #print(track, s_trackdata['fxrack_channel'])
                    fxnum = s_trackdata['fxrack_channel']
                    s_datatomove = datatomove[str(fxnum)]
                    if 'params' not in s_trackdata: s_trackdata['params'] = {}
                    for paramname in s_datatomove:
                        ptmd = s_datatomove[paramname]
                        s_trackdata['params'][paramname] = ptmd[0]
                        if ptmd[1] != None:
                            data_values.nested_dict_add_value(cvpj_l, ['automation', 'track', track, paramname], ptmd[1])
        
            return True
            
    else: return False
