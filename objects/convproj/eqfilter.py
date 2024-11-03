# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.valobjs import dualstr

class cvpj_filter:
	def __init__(self):
		self.on = False
		self.type = dualstr()
		self.freq = 44100
		self.q = 1
		self.gain = 0
		self.slope = 12
		self.filter_algo = ''

class cvpj_eq:
	def __init__(self, plugin_obj, basename):
		self.basename = basename
		self.filtnum = 0
		self.plugin_obj = plugin_obj
		self.num_bands = 0
		self.bands = []

	def __iter__(self):
		for x in self.bands:
			yield x, self.plugin_obj.named_filter[x] if x in self.plugin_obj.named_filter else cvpj_filter()

	def add(self):
		filter_id = self.basename+'_'+str(self.filtnum)
		self.bands.append(filter_id)
		self.filtnum += 1
		self.num_bands += 1

		return self.plugin_obj.named_filter_add(filter_id), filter_id

	def from_8limited(self, pluginid):
		self.bands = ['high_pass', 'low_shelf', 'peak_1', 'peak_2', 'peak_3', 'peak_4', 'high_shelf', 'low_pass']

	def to_8limited(self, convproj_obj, pluginid):
		fnames = [f for f in self.plugin_obj.named_filter]
		ftypes = [self.plugin_obj.named_filter[f].type.type for f in fnames]

		iseqlimited = False
		if ftypes.count('high_pass')<2 and ftypes.count('low_shelf')<2 and ftypes.count('peak')<5 and ftypes.count('high_shelf')<2 and ftypes.count('low_pass')<2:
			peaknum = 1
			iseqlimited = True
			for num in range(len(fnames)):
				fname = fnames[num]
				ftype = self.plugin_obj.named_filter[fname].type.type

				nameto = None
				if ftype == 'high_pass': nameto = 'high_pass'
				if ftype == 'low_shelf': nameto = 'low_shelf'
				if ftype == 'high_shelf': nameto = 'high_shelf'
				if ftype == 'low_pass': nameto = 'low_pass'
				if ftype == 'peak': 
					nameto = 'peak_'+str(peaknum)
					peaknum += 1

				if nameto: 
					self.plugin_obj.named_filter_rename(fname, nameto)
					if convproj_obj and pluginid:
						convproj_obj.automation.move(['n_filter', pluginid, fname, 'freq'], ['n_filter', pluginid, nameto, 'freq'])
						convproj_obj.automation.move(['n_filter', pluginid, fname, 'gain'], ['n_filter', pluginid, nameto, 'gain'])
						convproj_obj.automation.move(['n_filter', pluginid, fname, 'q'], ['n_filter', pluginid, nameto, 'q'])
						convproj_obj.automation.move(['n_filter', pluginid, fname, 'on'], ['n_filter', pluginid, nameto, 'on'])
		return iseqlimited
