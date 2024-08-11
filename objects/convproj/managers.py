# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

class manager_plugts:
	def __init__(self):
		self.storedts = {}

	def transform(self, filepath, ts_name, convproj_obj, plugin_obj, pluginid, extra_json):
		if filepath not in self.storedts: 
			self.storedts[filepath] = plugtransform()
			self.storedts[filepath].load_file(filepath)
		self.current_ts = self.storedts[filepath]
		self.current_ts.transform(ts_name, convproj_obj, plugin_obj, pluginid, extra_json)

	def get_storedval(self, name):
		return self.current_ts.get_storedval(name)