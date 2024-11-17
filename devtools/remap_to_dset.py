import os 
import sys

dpath_befr = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
relpath = os.path.abspath(dpath_befr)
sys.path.append(relpath)
from objects.datastorage import dataset

import chardet
import numpy as np

dt_cvpj = np.dtype([
		('paramid', np.str_, 32),
		('extid', np.str_, 32),
		('def_one', np.float64), 
		('def', np.float64), 
		('min', np.float64), 
		('max', np.float64), 
		('mathtype', np.str_, 3),
		('mathval', np.float64), 
		('visname', np.str_, 64)
		])

dt_vst2 = np.dtype([
		('paramnum', np.short),
		('visname', np.str_, 16)
		])

dt_vst3 = np.dtype([
		('paramnum', np.short),
		('visname', np.str_, 24)
		])

class paramremap:
	def __init__(self, filename):
		self.cvpj = np.zeros(0, dtype=dt_cvpj)
		self.vst2 = np.zeros(0, dtype=dt_vst2)
		self.vst3 = np.zeros(0, dtype=dt_vst3)
		if os.path.exists(filename):
			with open(filename, 'rb') as csvfile:
				csvdata = csvfile.read()
				csvcharset = chardet.detect(csvdata)['encoding']
				csvtext = csvdata.decode(csvcharset).splitlines()

				if len(csvtext)>2:
					self.cvpj = np.zeros(len(csvtext)-2, dtype=dt_cvpj)
					self.vst2 = np.zeros(len(csvtext)-2, dtype=dt_vst2)
					self.vst3 = np.zeros(len(csvtext)-2, dtype=dt_vst3)

					self.cvpj['min'] = 0
					self.cvpj['max'] = 1
					self.cvpj['mathtype'] = 'lin'
					self.cvpj['mathval'] = 1
					self.vst2['paramnum'] = -1
					self.vst3['paramnum'] = -1

					self.usedparamnames = {'cvpj': [],'vst2': [],'vst3': []}

					for count, row_unsep in enumerate(csvtext):
						splitsep = row_unsep.split(',')
						if count == 0: 
							data_exttypes = splitsep

						elif count == 1: 
							data_typenames = splitsep
							data_len = len(data_exttypes)
							for n,v in enumerate(data_typenames):
								self.usedparamnames[data_exttypes[n]].append(v)
						else:
							numparam = count-2
							for x in range(max(data_len, len(splitsep))):
								extname = data_exttypes[x]
								dataname = data_typenames[x]
								dataval = splitsep[x]

								if dataname in ['def_one','def','min','max']: dataval = float(dataval)
								if dataname == 'paramnum': dataval = float(dataval)
								if extname == 'cvpj': self.cvpj[numparam][dataname] = dataval
								if extname == 'vst2': self.vst2[numparam][dataname] = dataval
								if extname == 'vst3': self.vst3[numparam][dataname] = dataval

					if 'def' not in self.usedparamnames['cvpj']:
						mulvals = self.cvpj['max']-self.cvpj['min']
						self.cvpj['def'] = np.asarray(self.cvpj['def_one'], dtype=np.float64)
						self.cvpj['def'] *= mulvals
						self.cvpj['def'] += self.cvpj['min']
					elif 'def_one' not in self.usedparamnames['cvpj']:
						mulvals = self.cvpj['max']-self.cvpj['min']
						self.cvpj['def_one'] = np.asarray(self.cvpj['def_one'], dtype=np.float64)
						self.cvpj['def_one'] -= self.cvpj['min']
						self.cvpj['def_one'] /= mulvals

dn = 'magical8bitplug2'

infile = "..\\data_ext\\remap\\%s.csv" % dn

out_dset = dataset.dataset(None)
dataset_cat = out_dset.category_add('plugin')

def create_object(infile, objname):
	pmap_obj = paramremap(infile)
	dataset_object = dataset_cat.objects.create(objname)
	
	for n, x in enumerate(pmap_obj.cvpj):
		param_obj = dataset_object.params.adddef(x['paramid'])
		param_obj.type = 'float'
		param_obj.defv = x['def']
		param_obj.min = x['min']
		param_obj.max = x['max']
		param_obj.name = x['visname']
		param_obj.extplug_paramid = x['extid']
		if pmap_obj.usedparamnames['vst3']:
			if not param_obj.name: param_obj.name = pmap_obj.vst3[n]['visname']
	
			paramext = param_obj.add_extplug_assoc('vst3')
			if pmap_obj.vst3[n]['visname']:
				if pmap_obj.vst3[n]['visname'] != param_obj.name:
					paramext.name = pmap_obj.vst3[n]['visname']
			paramext.num = int(pmap_obj.vst3[n]['paramnum'])
			if paramext.name and param_obj.name: 
				if paramext.name == param_obj.name[0:24]:
					paramext.name = None
	
		if pmap_obj.usedparamnames['vst2']:
			if not param_obj.name: param_obj.name = pmap_obj.vst2[n]['visname']
	
			paramext = param_obj.add_extplug_assoc('vst2')
			if pmap_obj.vst2[n]['visname']:
				if pmap_obj.vst2[n]['visname'] != param_obj.name:
					paramext.name = pmap_obj.vst2[n]['visname']
			paramext.num = int(pmap_obj.vst2[n]['paramnum'])
			if paramext.name and param_obj.name: 
				if paramext.name == param_obj.name[0:16]:
					paramext.name = None

create_object(infile, 'main')
out_dset.write('%s.dset' % dn)