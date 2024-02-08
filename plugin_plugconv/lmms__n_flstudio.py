# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

threeosc_shapes = {
    0: 0,
    1: 1,
    2: 3,
    3: 2,
    4: 5,
    5: 6,
    6: 7}

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['native-flstudio', None, 'flp'], ['native-lmms', None, 'lmms'], True, False
    def convert(self, convproj_obj, plugin_obj, pluginid, extra_json):

        if plugin_obj.plugin_subtype.lower() == 'fruity balance':  
            print('[plug-conv] FL Studio to LMMS: Fruity Balance > Amplifier:',pluginid)
            bal_pan = plugin_obj.params.get('pan', 0).value
            bal_vol = plugin_obj.params.get('vol', 0).value
            plugin_obj.replace('native-lmms', 'amplifier')
            plugin_obj.params.add('pan', (bal_pan/128)*100, 'int')
            plugin_obj.params.add('right', 100, 'int')
            plugin_obj.params.add('volume', (bal_vol/256)*100, 'int')
            plugin_obj.params.add('left', 100, 'int')
            return 0

        if plugin_obj.plugin_subtype.lower() == 'fruity stereo shaper':
            print('[plug-conv] FL Studio to LMMS: Stereo Shaper > Stereo Matrix:',pluginid)
            fl_shape_r2l = plugin_obj.params.get('r2l', 0).value/12800
            fl_shape_l2l = plugin_obj.params.get('l2l', 0).value/12800
            fl_shape_r2r = plugin_obj.params.get('r2r', 0).value/12800
            fl_shape_l2r = plugin_obj.params.get('l2r', 0).value/12800
            plugin_obj.replace('native-lmms', 'stereomatrix')
            plugin_obj.params.add('l-r', fl_shape_l2r, 'float')  
            plugin_obj.params.add('r-l', fl_shape_r2l, 'float')  
            plugin_obj.params.add('r-r', fl_shape_r2r, 'float')  
            plugin_obj.params.add('l-l', fl_shape_l2l, 'float')  
            return 0

        if plugin_obj.plugin_subtype.lower() == '3x osc':   
            print('[plug-conv] FL Studio to LMMS: 3xOsc > TripleOscillator:',pluginid)
            fl_osc1_coarse = plugin_obj.params.get('osc1_coarse', 0).value
            fl_osc1_detune = plugin_obj.params.get('osc1_detune', 0).value
            fl_osc1_fine = plugin_obj.params.get('osc1_fine', 0).value
            fl_osc1_invert = plugin_obj.params.get('osc1_invert', 0).value
            fl_osc1_mixlevel = plugin_obj.params.get('osc1_mixlevel', 0).value/128
            fl_osc1_ofs = plugin_obj.params.get('osc1_ofs', 0).value/64   
            fl_osc1_pan = plugin_obj.params.get('osc1_pan', 0).value/64   
            fl_osc1_shape = plugin_obj.params.get('osc1_shape', 0).value

            fl_osc2_coarse = plugin_obj.params.get('osc2_coarse', 0).value
            fl_osc2_detune = plugin_obj.params.get('osc2_detune', 0).value
            fl_osc2_fine = plugin_obj.params.get('osc2_fine', 0).value
            fl_osc2_invert = plugin_obj.params.get('osc2_invert', 0).value
            fl_osc2_mixlevel = plugin_obj.params.get('osc2_mixlevel', 0).value/128
            fl_osc2_ofs = plugin_obj.params.get('osc2_ofs', 0).value/64   
            fl_osc2_pan = plugin_obj.params.get('osc2_pan', 0).value/64   
            fl_osc2_shape = plugin_obj.params.get('osc2_shape', 0).value

            fl_osc3_coarse = plugin_obj.params.get('osc3_coarse', 0).value
            fl_osc3_detune = plugin_obj.params.get('osc3_detune', 0).value
            fl_osc3_fine = plugin_obj.params.get('osc3_fine', 0).value
            fl_osc3_invert = plugin_obj.params.get('osc3_invert', 0).value
            fl_osc3_ofs = plugin_obj.params.get('osc3_ofs', 0).value/64   
            fl_osc3_pan = plugin_obj.params.get('osc3_pan', 0).value/64   
            fl_osc3_shape = plugin_obj.params.get('osc3_shape', 0).value

            fl_osc3_am = plugin_obj.params.get('osc3_am', 0).value
            fl_phase_rand = plugin_obj.params.get('phase_rand', 0).value

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

            samplerefid = plugin_obj.samplerefs['audiofile'] if 'audiofile' in plugin_obj.samplerefs else None

            fileref_exists, filedata = plugin_obj.get_fileref('audiofile', convproj_obj)

            plugin_obj.replace('native-lmms', 'tripleoscillator')

            plugin_obj.params.add('coarse0', lmms_coarse0, 'int')
            plugin_obj.params.add('coarse1', lmms_coarse1, 'int')
            plugin_obj.params.add('coarse2', lmms_coarse2, 'int')

            plugin_obj.params.add('finel0', lmms_finel0, 'int')  
            plugin_obj.params.add('finel1', lmms_finel1, 'int')  
            plugin_obj.params.add('finel2', lmms_finel2, 'int')  
            plugin_obj.params.add('finer0', lmms_finer0, 'int')  
            plugin_obj.params.add('finer1', lmms_finer1, 'int')  
            plugin_obj.params.add('finer2', lmms_finer2, 'int')

            plugin_obj.params.add('modalgo1', lmms_modalgo1, 'int')  
            plugin_obj.params.add('modalgo2', lmms_modalgo2, 'int')  
            plugin_obj.params.add('modalgo3', lmms_modalgo3, 'int')

            plugin_obj.params.add('pan0', lmms_pan0, 'int')  
            plugin_obj.params.add('pan1', lmms_pan1, 'int')  
            plugin_obj.params.add('pan2', lmms_pan2, 'int')

            plugin_obj.params.add('phoffset0', lmms_phoffset0, 'int')
            plugin_obj.params.add('phoffset1', lmms_phoffset1, 'int')
            plugin_obj.params.add('phoffset2', lmms_phoffset2, 'int')

            plugin_obj.params.add('stphdetun0', lmms_stphdetun0, 'int')  
            plugin_obj.params.add('stphdetun1', lmms_stphdetun1, 'int')  
            plugin_obj.params.add('stphdetun2', lmms_stphdetun2, 'int')

            plugin_obj.params.add('vol0', lmms_vol0*33, 'int')   
            plugin_obj.params.add('vol1', lmms_vol1*33, 'int')   
            plugin_obj.params.add('vol2', lmms_vol2*33, 'int')

            plugin_obj.params.add('wavetype0', lmms_wavetype0, 'int')
            plugin_obj.params.add('wavetype1', lmms_wavetype1, 'int')
            plugin_obj.params.add('wavetype2', lmms_wavetype2, 'int')

            if samplerefid:
                for oscnum in range(1, 4):
                    out_str = 'userwavefile'+str(oscnum)
                    plugin_obj.samplerefs[out_str] = samplerefid
                    plugin_obj.samplerefs[out_str] = samplerefid
                    plugin_obj.samplerefs[out_str] = samplerefid
            return 0
            
        return 2