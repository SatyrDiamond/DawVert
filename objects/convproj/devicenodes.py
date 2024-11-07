# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.convproj import visual

class cvpj_devnode_device:
	def __init__(self):
		self.type = ''
		self.subtype = ''
		self.data = {}
		self.data_internal = {}
		self.visual = visual.cvpj_visual()
		self.window = visual.cvpj_window_data()

class cvpj_devnode_cable:
	def __init__(self):
		self.id = ''
		self.input_device = ''
		self.input_id = ''
		self.output_device = ''
		self.output_id = ''
		self.color = None

class cvpj_devnode_semisep:
	def __init__(self):
		self.tracks = {}
		self.cables = []

	def track__add(self, i_track):
		self.tracks[i_track] = {}

	def add_device(self, i_track, i_id):
		device_obj = cvpj_devnode_device()
		self.tracks[i_track][i_id] = device_obj
		return device_obj

	def add_cable(self):
		cable_obj = cvpj_devnode_cable()
		self.cables.append(cable_obj)
		return cable_obj

	def add_cable_data(self, input_device, input_id, output_device, output_id):
		cable_obj = cvpj_devnode_cable()
		cable_obj.input_device = input_device
		cable_obj.input_id = input_id
		cable_obj.output_device = output_device
		cable_obj.output_id = output_id
		self.cables.append(cable_obj)
		return cable_obj

class cvpj_devnode:
	def __init__(self):
		self.devices = []
		self.cables = []

	def add_device(self, i_id):
		device_obj = cvpj_devnode_device()
		self.devices[i_id].append(device_obj)
		return device_obj

	def add_cable(self):
		cable_obj = cvpj_devnode_cable()
		self.cables.append(cable_obj)
		return cable_obj

	def add_cable_data(self, input_device, input_id, output_device, output_id):
		cable_obj = cvpj_devnode_cable()
		cable_obj.input_device = input_device
		cable_obj.input_id = input_id
		cable_obj.output_device = output_device
		cable_obj.output_id = output_id
		self.cables.append(cable_obj)
		return cable_obj