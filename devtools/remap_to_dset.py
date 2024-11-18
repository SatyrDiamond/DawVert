import os 
import sys

import func__paramremap
dpath_befr = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
relpath = os.path.abspath(dpath_befr)
sys.path.append(relpath)
from objects.datastorage import dataset

dn = 'kickmess'

infile = "..\\data_ext\\remap\\%s.csv" % dn

out_dset = dataset.dataset(None)
dataset_cat = out_dset.category_add('plugin')

def create_object(infile, objname):
	pmap_obj = func__paramremap.paramremap(infile)
	dataset_object = dataset_cat.objects.create(objname)
	
	for n, x in enumerate(pmap_obj.cvpj):
		param_obj = dataset_object.params.adddef(x['paramid'])
		param_obj.type = 'float'
		param_obj.defv = x['def']
		param_obj.min = x['min']
		param_obj.max = x['max']
		param_obj.name = x['visname']
		param_obj.extplug_paramid = x['extid']

		param_obj.math_zeroone.type = x['mathtype']
		param_obj.math_zeroone.val = x['mathval']
		
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