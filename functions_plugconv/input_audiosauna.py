# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import struct
import math
from functions import data_bytes
from functions import params_vst
from functions import plugin_vst2

def convert_inst(instdata):
	pluginname = instdata['plugin']
	plugindata = instdata['plugindata']
	if pluginname == 'native-audiosauna':
		as_type = plugindata['type']
		as_data = plugindata['data']
		as_asdrlfo = plugindata['asdrlfo']
		#print(as_type)
		#print(as_data)
		#print(as_asdrlfo)

		if as_type == 0:
			instdata['plugin'] = 'fm'

			masterrelease = as_asdrlfo['volume']['envelope']['release']

			new_plugindata = {}

			new_plugindata['asdrlfo'] = {}
			new_plugindata['asdrlfo']['cutoff'] = as_asdrlfo['cutoff']
			new_plugindata['asdrlfo']['pitch'] = as_asdrlfo['pitch']

			new_plugindata['max_mod'] = 13

			new_plugindata['num_ops'] = 4
			new_plugindata['ops'] = [{},{},{},{}]

			new_plugindata['ops'][0]['ratio'] = float(as_data['frq1']) + float(as_data['fine1'])
			new_plugindata['ops'][0]['shape'] = 'sine'
			new_plugindata['ops'][0]['vol'] = int(as_data['opAmp1'])/100
			new_plugindata['ops'][0]['env'] = {}
			new_plugindata['ops'][0]['env']['attack'] = float(as_data['aOp2'])
			new_plugindata['ops'][0]['env']['decay'] = float(as_data['dOp2'])
			new_plugindata['ops'][0]['env']['sustain'] = float(as_data['sOp1'])/100
			new_plugindata['ops'][0]['env']['release'] = masterrelease

			new_plugindata['ops'][1]['ratio'] = float(as_data['frq2']) + float(as_data['fine2'])
			new_plugindata['ops'][1]['shape'] = 'sine'
			new_plugindata['ops'][1]['vol'] = int(as_data['opAmp2'])/100
			new_plugindata['ops'][1]['env'] = {}
			new_plugindata['ops'][1]['env']['attack'] = float(as_data['aOp2'])
			new_plugindata['ops'][1]['env']['decay'] = float(as_data['dOp2'])
			new_plugindata['ops'][1]['env']['sustain'] = float(as_data['sOp2'])/100
			new_plugindata['ops'][1]['env']['release'] = masterrelease
			new_plugindata['ops'][1]['targets'] = []

			new_plugindata['ops'][2]['ratio'] = float(as_data['frq3']) + float(as_data['fine3'])
			new_plugindata['ops'][2]['shape'] = 'sine'
			new_plugindata['ops'][2]['vol'] = int(as_data['opAmp3'])/100
			new_plugindata['ops'][2]['env'] = {}
			new_plugindata['ops'][2]['env']['attack'] = float(as_data['aOp3'])
			new_plugindata['ops'][2]['env']['decay'] = float(as_data['dOp3'])
			new_plugindata['ops'][2]['env']['sustain'] = float(as_data['sOp3'])/100
			new_plugindata['ops'][2]['env']['release'] = masterrelease
			new_plugindata['ops'][2]['targets'] = []

			new_plugindata['ops'][3]['ratio'] = float(as_data['frq4']) + float(as_data['fine4'])
			new_plugindata['ops'][3]['shape'] = 'sine'
			new_plugindata['ops'][3]['vol'] = int(as_data['opAmp4'])/100
			new_plugindata['ops'][3]['env'] = {}
			new_plugindata['ops'][3]['env']['attack'] = float(as_data['aOp4'])
			new_plugindata['ops'][3]['env']['decay'] = float(as_data['dOp4'])
			new_plugindata['ops'][3]['env']['sustain'] = float(as_data['sOp4'])/100
			new_plugindata['ops'][3]['env']['release'] = masterrelease
			new_plugindata['ops'][3]['targets'] = []

			fmAlgorithm = int(as_data['fmAlgorithm'])

			if fmAlgorithm == 1:
				new_plugindata['ops'][0]['targets'] = [-1]
				new_plugindata['ops'][1]['targets'] = [0]
				new_plugindata['ops'][2]['targets'] = [1]
				new_plugindata['ops'][3]['targets'] = [2]
			if fmAlgorithm == 2:
				new_plugindata['ops'][0]['targets'] = [-1]
				new_plugindata['ops'][1]['targets'] = [0]
				new_plugindata['ops'][2]['targets'] = [1]
				new_plugindata['ops'][3]['targets'] = [1]
			if fmAlgorithm == 3:
				new_plugindata['ops'][0]['targets'] = [-1]
				new_plugindata['ops'][1]['targets'] = [0]
				new_plugindata['ops'][2]['targets'] = [1]
				new_plugindata['ops'][3]['targets'] = [0]
			if fmAlgorithm == 4:
				new_plugindata['ops'][0]['targets'] = [-1]
				new_plugindata['ops'][1]['targets'] = [0]
				new_plugindata['ops'][2]['targets'] = [0]
				new_plugindata['ops'][3]['targets'] = [2]
			if fmAlgorithm == 5:
				new_plugindata['ops'][0]['targets'] = [-1]
				new_plugindata['ops'][1]['targets'] = [0]
				new_plugindata['ops'][2]['targets'] = [-1]
				new_plugindata['ops'][3]['targets'] = [2]
			if fmAlgorithm == 6:
				new_plugindata['ops'][0]['targets'] = [-1]
				new_plugindata['ops'][1]['targets'] = [-1]
				new_plugindata['ops'][2]['targets'] = [-1]
				new_plugindata['ops'][3]['targets'] = [0,1,2]
			if fmAlgorithm == 7:
				new_plugindata['ops'][0]['targets'] = [-1]
				new_plugindata['ops'][1]['targets'] = [-1]
				new_plugindata['ops'][2]['targets'] = [-1]
				new_plugindata['ops'][3]['targets'] = [2]
			if fmAlgorithm == 8:
				new_plugindata['ops'][0]['targets'] = [-1]
				new_plugindata['ops'][1]['targets'] = [-1]
				new_plugindata['ops'][2]['targets'] = [-1]
				new_plugindata['ops'][3]['targets'] = [-1]
			
			instdata['plugindata'] = new_plugindata

def convert_fx(fxdata):
	pluginname = fxdata['plugin']
	plugindata = fxdata['plugindata']
	as_type = plugindata['name']
	as_data = plugindata['data']

