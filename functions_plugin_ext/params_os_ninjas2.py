# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions_plugin_ext import plugin_vst2
from functions_plugin_ext import data_nullbytegroup

def create_blank_prog():
	progout = ''
	progtext = '0 0 0 0.001000 0.001000 1.000000 0.001000 '
	progout += '1 '
	for _ in range(128): progout += progtext
	return progout

class ninjas2_data:
	def __init__(self):
		self.data_main = {}
		self.data_progs = {}

		self.data_main['number_of_slices'] = '0.000000'
		self.data_main['sliceSensitivity'] = '0.500000'
		self.data_main['attack'] = '0.001000'
		self.data_main['decay'] = '0.001000'
		self.data_main['sustain'] = '1.000000'
		self.data_main['release'] = '0.001000'
		self.data_main['load'] = '0.000000'
		self.data_main['slicemode'] = '1.000000'
		self.data_main['programGrid'] = '1.000000'
		self.data_main['playmode'] = '0.000000'
		self.data_main['pitchbendDepth'] = '12.000000'
		self.data_main['OneShotForward'] = '0.000000'
		self.data_main['OneShotReverse'] = '0.000000'
		self.data_main['LoopForward'] = '0.000000'
		self.data_main['LoopReverse'] = '0.000000'

		self.data_progs['slices'] = 'empty'
		self.data_progs['filepathFromUI'] = ''
		self.data_progs['program00'] = create_blank_prog()
		self.data_progs['program01'] = create_blank_prog()
		self.data_progs['program02'] = create_blank_prog()
		self.data_progs['program03'] = create_blank_prog()
		self.data_progs['program04'] = create_blank_prog()
		self.data_progs['program05'] = create_blank_prog()
		self.data_progs['program06'] = create_blank_prog()
		self.data_progs['program07'] = create_blank_prog()
		self.data_progs['program08'] = create_blank_prog()
		self.data_progs['program09'] = create_blank_prog()
		self.data_progs['program10'] = create_blank_prog()
		self.data_progs['program11'] = create_blank_prog()
		self.data_progs['program12'] = create_blank_prog()
		self.data_progs['program13'] = create_blank_prog()
		self.data_progs['program14'] = create_blank_prog()
		self.data_progs['program15'] = create_blank_prog()

	def to_cvpj_vst2(self, convproj_obj, plugin_obj):
		plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'any', 1315524146, 'chunk', data_nullbytegroup.make([self.data_progs, self.data_main]), None)
