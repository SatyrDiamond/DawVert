# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import lxml.etree as ET
from functions_plugin_ext import plugin_vst2
from functions_plugin_ext import data_vc2xml

class tal_filter_data:
	def __init__(self):
		self.params = {}
		self.params['programname'] = "DawVert"
		self.params['speedFactor'] = "0.3333333432674408"
		self.params['filtertype'] = "0.5555555820465088"
		self.params['volumein'] = "0.5"
		self.params['volumeout'] = "0.5"
		self.params['depth'] = "1.0"
		self.params['resonance'] = "0.0"
		self.params['offset'] = "0.5"
		self.params['legacymode'] = "0.0"
		self.params['filtertypeNew'] = "0.0"
		self.params['trigger'] = "0.0"
		self.params['stereooffset'] = "0.0"
		self.params['timespecial'] = "0.0"
		self.params['midiTrigger'] = "0.0"

		self.talc_data = ET.Element("tal")
		self.talc_data.set('curprogram', "0")
		self.talc_data.set('version', "2.0")
		self.talc_progs = ET.SubElement(self.talc_data, 'programs')
		self.talc_prog = ET.SubElement(self.talc_progs, 'program')
		self.talc_splinepoints = ET.SubElement(self.talc_prog, 'splinePoints')

	def set_param(self, name, value):
		self.params[name] = str(value)
		
	def add_point(self, pos, val, isStartPoint, isEndPoint):
		self.talc_splinepoint = ET.SubElement(self.talc_splinepoints, 'splinePoint')
		self.talc_splinepoint.set('isStartPoint', str(int(isStartPoint)))
		self.talc_splinepoint.set('isEndPoint', str(int(isEndPoint)))
		self.talc_splinepoint.set('centerPointX', str(float(pos)))
		self.talc_splinepoint.set('centerPointY', str(float(val)))
		self.talc_splinepoint.set('controlPointLeftX', str(float(pos)))
		self.talc_splinepoint.set('controlPointLeftY', str(float(val)))
		self.talc_splinepoint.set('controlPointRightX', str(float(pos)))
		self.talc_splinepoint.set('controlPointRightY', str(float(val)))

	def add_point_adv(self, centerPoint, controlPointLeft, controlPointRight, isStartPoint, isEndPoint):
		self.talc_splinepoint = ET.SubElement(self.talc_splinepoints, 'splinePoint')
		self.talc_splinepoint.set('isStartPoint', str(isStartPoint))
		self.talc_splinepoint.set('isEndPoint', str(isEndPoint))
		self.talc_splinepoint.set('centerPointX', str(centerPoint[0]))
		self.talc_splinepoint.set('centerPointY', str(centerPoint[0]))
		self.talc_splinepoint.set('controlPointLeftX', str(controlPointLeft[0]))
		self.talc_splinepoint.set('controlPointLeftY', str(controlPointLeft[1]))
		self.talc_splinepoint.set('controlPointRightX', str(controlPointRight[0]))
		self.talc_splinepoint.set('controlPointRightY', str(controlPointRight[1]))

	def to_cvpj_vst2(self, convproj_obj, plugin_obj):
		for n,v in self.params.items(): self.talc_prog.set(n, str(v))
		plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id','any', 808596837, 'chunk', data_vc2xml.make(self.talc_data), None)