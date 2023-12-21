# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

from functions import plugins
from functions_tracks import auto_data

threeosc_shapes = {
    0: 0,
    1: 1,
    2: 3,
    3: 2,
    4: 5,
    5: 6,
    6: 7}


def getparam(paramname):
    global cvpj_plugindata_g
    paramval = cvpj_plugindata_g.param_get(paramname, 0)
    return paramval[0]

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['native-flstudio', None, 'flp'], ['native-lmms', None, 'lmms'], True, False
    def convert(self, cvpj_l, pluginid, cvpj_plugindata, extra_json):
        global cvpj_plugindata_g
        cvpj_plugindata_g = cvpj_plugindata

        plugintype = cvpj_plugindata.type_get()

        if plugintype[1].lower() == 'fruity balance':  
            print('[plug-conv] FL Studio to LMMS: Fruity Balance > Amplifier:',pluginid)
            auto_data.del_plugin(cvpj_l, pluginid)
            bal_pan = getparam('pan')
            bal_vol = getparam('vol')
            cvpj_plugindata.replace('native-lmms', 'amplifier')
            cvpj_plugindata.param_add('pan', (bal_pan/128)*100, 'int', "")
            cvpj_plugindata.param_add('right', 100, 'int', "")
            cvpj_plugindata.param_add('volume', (bal_vol/256)*100, 'int', "")
            cvpj_plugindata.param_add('left', 100, 'int', "")
            return 0

        if plugintype[1].lower() == 'fruity stereo shaper':
            print('[plug-conv] FL Studio to LMMS: Stereo Shaper > Stereo Matrix:',pluginid)
            auto_data.del_plugin(cvpj_l, pluginid)
            fl_shape_r2l = getparam('r2l')/12800
            fl_shape_l2l = getparam('l2l')/12800
            fl_shape_r2r = getparam('r2r')/12800
            fl_shape_l2r = getparam('l2r')/12800
            cvpj_plugindata.replace('native-lmms', 'stereomatrix')
            cvpj_plugindata.param_add('l-r', fl_shape_l2r, 'float', "")  
            cvpj_plugindata.param_add('r-l', fl_shape_r2l, 'float', "")  
            cvpj_plugindata.param_add('r-r', fl_shape_r2r, 'float', "")  
            cvpj_plugindata.param_add('l-l', fl_shape_l2l, 'float', "")  
            return 0

        if plugintype[1].lower() == '3x osc':   
            print('[plug-conv] FL Studio to LMMS: 3xOsc > TripleOscillator:',pluginid)
            auto_data.del_plugin(cvpj_l, pluginid)
            fl_osc1_coarse = getparam('osc1_coarse')
            fl_osc1_detune = getparam('osc1_detune')
            fl_osc1_fine = getparam('osc1_fine')
            fl_osc1_invert = getparam('osc1_invert')
            fl_osc1_mixlevel = getparam('osc1_mixlevel')/128
            fl_osc1_ofs = getparam('osc1_ofs')/64   
            fl_osc1_pan = getparam('osc1_pan')/64   
            fl_osc1_shape = getparam('osc1_shape')

            fl_osc2_coarse = getparam('osc2_coarse')
            fl_osc2_detune = getparam('osc2_detune')
            fl_osc2_fine = getparam('osc2_fine')
            fl_osc2_invert = getparam('osc2_invert')
            fl_osc2_mixlevel = getparam('osc2_mixlevel')/128
            fl_osc2_ofs = getparam('osc2_ofs')/64   
            fl_osc2_pan = getparam('osc2_pan')/64   
            fl_osc2_shape = getparam('osc2_shape')

            fl_osc3_coarse = getparam('osc3_coarse')
            fl_osc3_detune = getparam('osc3_detune')
            fl_osc3_fine = getparam('osc3_fine')
            fl_osc3_invert = getparam('osc3_invert')
            fl_osc3_ofs = getparam('osc3_ofs')/64   
            fl_osc3_pan = getparam('osc3_pan')/64   
            fl_osc3_shape = getparam('osc3_shape')

            fl_osc3_am = getparam('osc3_am')
            fl_phase_rand = getparam('phase_rand')

            lmms_coarse0 = fl_osc1_coarse   
            lmms_coarse1 = fl_osc2_coarse   
            lmms_coarse2 = fl_osc3_coarse   
            lmms_finel0 = fl_osc1_fine  
            lmms_finel1 = fl_osc2_fine  
            lmms_finel2 = fl_osc3_fine  
            lmms_finer0 = fl_osc1_fine+fl_osc1_detune   
            lmms_finer1 = fl_osc2_fine+fl_osc2_detune   
            lmms_finer2 = fl_osc3_fine+fl_osc3_detune   
            lmms_modalgo1 = 2   
            lmms_modalgo2 = 2   
            lmms_modalgo3 = 2   
            lmms_pan0 = int(fl_osc1_pan*100)
            lmms_pan1 = int(fl_osc2_pan*100)
            lmms_pan2 = int(fl_osc3_pan*100)
            lmms_phoffset0 = 0  
            lmms_phoffset1 = 0  
            lmms_phoffset2 = 0  
            lmms_stphdetun0 = int(fl_osc1_ofs*360)  
            if lmms_stphdetun0 < 0: lmms_stphdetun0 + 360   
            lmms_stphdetun1 = int(fl_osc2_ofs*360)  
            if lmms_stphdetun1 < 0: lmms_stphdetun1 + 360   
            lmms_stphdetun2 = int(fl_osc3_ofs*360)  
            if lmms_stphdetun2 < 0: lmms_stphdetun2 + 360   
            lmms_vol0 = 1.0*(-fl_osc1_mixlevel+1)*(-fl_osc2_mixlevel+1) 
            lmms_vol1 = fl_osc1_mixlevel*(-fl_osc2_mixlevel+1)  
            lmms_vol2 = fl_osc2_mixlevel
            lmms_wavetype0 = threeosc_shapes[fl_osc1_shape] 
            lmms_wavetype1 = threeosc_shapes[fl_osc2_shape] 
            lmms_wavetype2 = threeosc_shapes[fl_osc3_shape] 
            lmms_userwavefile0 = 0  
            lmms_userwavefile1 = 0  
            lmms_userwavefile2 = 0

            filedata = cvpj_plugindata.fileref_get('audiofile')

            cvpj_plugindata.replace('native-lmms', 'tripleoscillator')

            cvpj_plugindata.param_add('coarse0', lmms_coarse0, 'int', "")
            cvpj_plugindata.param_add('coarse1', lmms_coarse1, 'int', "")
            cvpj_plugindata.param_add('coarse2', lmms_coarse2, 'int', "")

            cvpj_plugindata.param_add('finel0', lmms_finel0, 'int', "")  
            cvpj_plugindata.param_add('finel1', lmms_finel1, 'int', "")  
            cvpj_plugindata.param_add('finel2', lmms_finel2, 'int', "")  
            cvpj_plugindata.param_add('finer0', lmms_finer0, 'int', "")  
            cvpj_plugindata.param_add('finer1', lmms_finer1, 'int', "")  
            cvpj_plugindata.param_add('finer2', lmms_finer2, 'int', "")

            cvpj_plugindata.param_add('modalgo1', lmms_modalgo1, 'int', "")  
            cvpj_plugindata.param_add('modalgo2', lmms_modalgo2, 'int', "")  
            cvpj_plugindata.param_add('modalgo3', lmms_modalgo3, 'int', "")

            cvpj_plugindata.param_add('pan0', lmms_pan0, 'int', "")  
            cvpj_plugindata.param_add('pan1', lmms_pan1, 'int', "")  
            cvpj_plugindata.param_add('pan2', lmms_pan2, 'int', "")

            cvpj_plugindata.param_add('phoffset0', lmms_phoffset0, 'int', "")
            cvpj_plugindata.param_add('phoffset1', lmms_phoffset1, 'int', "")
            cvpj_plugindata.param_add('phoffset2', lmms_phoffset2, 'int', "")

            cvpj_plugindata.param_add('stphdetun0', lmms_stphdetun0, 'int', "")  
            cvpj_plugindata.param_add('stphdetun1', lmms_stphdetun1, 'int', "")  
            cvpj_plugindata.param_add('stphdetun2', lmms_stphdetun2, 'int', "")

            cvpj_plugindata.param_add('vol0', lmms_vol0*33, 'int', "")   
            cvpj_plugindata.param_add('vol1', lmms_vol1*33, 'int', "")   
            cvpj_plugindata.param_add('vol2', lmms_vol2*33, 'int', "")

            cvpj_plugindata.param_add('wavetype0', lmms_wavetype0, 'int', "")
            cvpj_plugindata.param_add('wavetype1', lmms_wavetype1, 'int', "")
            cvpj_plugindata.param_add('wavetype2', lmms_wavetype2, 'int', "")

            if filedata != None:
                cvpj_plugindata.fileref_add('osc_1', filedata['path'])
                cvpj_plugindata.fileref_add('osc_2', filedata['path'])
                cvpj_plugindata.fileref_add('osc_3', filedata['path'])
            return 0
            
        return 2