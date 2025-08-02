# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.file_proj_past._sequel import func
from objects.file_proj_past._sequel import classobj
import xml.etree.ElementTree as ET

class sequel_project:
	def __init__(self):
		self.root_objects = {}
		self.objects = []

		self.obj_version = None
		self.obj_project = None
		self.obj_devices = None
		self.obj_guistate = None

	def load_from_file(self, filename):
		x_root = ET.parse(filename).getroot()
		func.globalids = {}
		self.root_objects = {}
		for x in x_root:
			if x.tag == 'rootObjects':
				for i in x:
					self.root_objects[i.get('name')] = int(i.get('ID'))
			else:
				self.objects.append(func.sequel_object(x))

		globalids = func.globalids
		if 'Version' in self.root_objects:
			self.obj_version = classobj.get_object(func.globalids[self.root_objects['Version']])
		if 'Project' in self.root_objects:
			self.obj_project = classobj.get_object(func.globalids[self.root_objects['Project']])
		if 'Devices' in self.root_objects:
			self.obj_devices = classobj.get_object(func.globalids[self.root_objects['Devices']])
		if 'GuiState' in self.root_objects:
			self.obj_guistate = classobj.get_object(func.globalids[self.root_objects['GuiState']])

		return True
		#for track in self.obj_project['Data Root']['Node']['Tracks']:
		#	print(track)

#input_file = "G:\\RandomMusicFiles\\old\\sequel 3\\"
#main_obj = sequel_project()
#main_obj.load_from_file(
#	input_file+'Sequel 3 Demo - Third Generation\\Sequel 3 Demo - Third Generation.steinberg-project'
#	)
