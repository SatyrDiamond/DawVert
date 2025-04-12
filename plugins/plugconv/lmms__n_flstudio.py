# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
from functions import extpluglog

threeosc_shapes = {
	0: 0,
	1: 1,
	2: 3,
	3: 2,
	4: 5,
	5: 6,
	6: 7}

pluckwave = [124, 219, 235, 222, 220, 214, 188, 161, 141, 109, 90, 74, 49, 41, 21, 0, 7, 37, 97, 139, 131, 116, 113, 111, 137, 180, 202, 194, 134, 64, 53, 72, 114, 150, 133, 130, 154, 160, 163, 171, 198, 216, 165, 109, 108, 130, 153, 161, 151, 131, 96, 68, 68, 82, 98, 106, 116, 100, 49, 42, 113, 191, 228, 227, 208, 197, 165, 134, 169, 200, 145, 60, 38, 112, 188, 158, 106, 116, 162, 199, 200, 172, 121, 78, 79, 89, 101, 149, 196, 195, 193, 199, 172, 138, 129, 113, 91, 99, 125, 126, 146, 201, 188, 107, 41, 16, 23, 56, 90, 113, 113, 101, 133, 180, 194, 197, 169, 103, 66, 75, 76, 75, 115, 169, 179, 133, 91, 106, 150, 167, 146, 141, 177, 181, 143, 144, 177, 200, 212, 213, 203, 170, 115, 101, 152, 194, 168, 115, 80, 56, 45, 60, 98, 143, 171, 181, 169, 144, 116, 84, 87, 116, 103, 63, 59, 84, 96, 78, 55, 86]

class plugconv(plugins.base):
	def is_dawvert_plugin(self):
		return 'plugconv'
	
	def get_priority(self):
		return -100
	
	def get_prop(self, in_dict):
		in_dict['in_plugins'] = [['native', 'flstudio', None]]
		in_dict['in_daws'] = ['flp']
		in_dict['out_plugins'] = [['native', 'lmms', None]]
		in_dict['out_daws'] = ['lmms']

	def convert(self, convproj_obj, plugin_obj, pluginid, dawvert_intent):
		if plugin_obj.type.check_wildmatch('native', 'flstudio', 'fruity stereo shaper'):
			extpluglog.convinternal('FL Studio', 'Stereo Shaper', 'LMMS', 'Stereo Matrix')
			plugin_obj.plugts_transform('./data_main/plugts/flstudio_lmms.pltr', 'fruity_stereo_shaper', convproj_obj, pluginid)
			return 0

		if plugin_obj.type.check_wildmatch('native', 'flstudio', 'fruity mute 2'):
			extpluglog.convinternal('FL Studio', 'Fruity Mute 2', 'LMMS', 'Amplifier')
			channel = int(plugin_obj.params.get('channel', 1024).value/341)
			mute = int(plugin_obj.params.get('mute', 0).value>512)
			left = max(1-int(channel>=1), mute)
			right = max(1-int(channel<=1), mute)
			plugin_obj.replace('native', 'lmms', 'amplifier')
			plugin_obj.params.add('pan', 0, 'int')
			plugin_obj.params.add('volume', 100, 'int')
			plugin_obj.params.add('right', 100*left, 'int')
			plugin_obj.params.add('left', 100*right, 'int')
			return 0

		if plugin_obj.type.check_wildmatch('native', 'flstudio', '3x osc'):
			extpluglog.convinternal('FL Studio', '3xOsc', 'LMMS', 'TripleOscillator')
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

			plugin_obj.samplepart_copy('userwavefile1', 'sample')
			plugin_obj.samplepart_copy('userwavefile2', 'sample')
			plugin_obj.samplepart_copy('userwavefile3', 'sample')
			
			plugin_obj.replace('native', 'lmms', 'tripleoscillator')

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

			plugin_obj.params.add('phoffset0', 0, 'int')
			plugin_obj.params.add('phoffset1', 0, 'int')
			plugin_obj.params.add('phoffset2', 0, 'int')

			plugin_obj.params.add('stphdetun0', lmms_stphdetun0, 'int')
			plugin_obj.params.add('stphdetun1', lmms_stphdetun1, 'int')
			plugin_obj.params.add('stphdetun2', lmms_stphdetun2, 'int')

			plugin_obj.params.add('vol0', lmms_vol0*33, 'int')
			plugin_obj.params.add('vol1', lmms_vol1*33, 'int')
			plugin_obj.params.add('vol2', lmms_vol2*33, 'int')

			plugin_obj.params.add('wavetype0', lmms_wavetype0, 'int')
			plugin_obj.params.add('wavetype1', lmms_wavetype1, 'int')
			plugin_obj.params.add('wavetype2', lmms_wavetype2, 'int')

			return 0
	   
		if plugin_obj.type.check_wildmatch('native', 'flstudio', 'plucked!'):
			extpluglog.convinternal('FL Studio', 'Plucked!', 'LMMS', 'Vibed')
			color = plugin_obj.params.get('color', 0).value/128
			decay = plugin_obj.params.get('decay', 0).value/256

			plugin_obj.replace('native', 'lmms', 'vibedstrings')

			plugin_obj.params.add('active0', 1, 'int')
			plugin_obj.params.add('slap0', 0.5, 'float')
			plugin_obj.params.add('stiffness0', (1-decay)*0.05, 'float')

			wave_obj = plugin_obj.wave_add('graph0')
			wave_obj.set_all_range(pluckwave, 128, 255)
			wave_obj.smooth = True
	   
		return 2