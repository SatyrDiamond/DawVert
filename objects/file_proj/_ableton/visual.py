# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.file_proj._ableton.func import *

import xml.etree.ElementTree as ET

class ableton_ClipEnvelopeChooserViewState:
	__slots__ = ['SelectedDevice','SelectedEnvelope','PreferModulationVisible']
	def __init__(self, xmltag):
		if xmltag:
			x_Name = xmltag.findall('ClipEnvelopeChooserViewState')[0]
			self.SelectedDevice = get_value(x_Name, 'SelectedDevice', 0)
			self.SelectedEnvelope = get_value(x_Name, 'SelectedEnvelope', 0)
			self.PreferModulationVisible = get_bool(x_Name, 'PreferModulationVisible', False)
		else:
			self.SelectedDevice = 0
			self.SelectedEnvelope = 0
			self.PreferModulationVisible = False

	def write(self, xmltag):
		x_Name = ET.SubElement(xmltag, "ClipEnvelopeChooserViewState")
		add_value(x_Name, 'SelectedDevice', self.SelectedDevice)
		add_value(x_Name, 'SelectedEnvelope', self.SelectedEnvelope)
		add_bool(x_Name, 'PreferModulationVisible', self.PreferModulationVisible)
