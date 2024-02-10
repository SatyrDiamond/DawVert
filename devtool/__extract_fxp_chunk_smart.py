
import os
import sys
import json
import argparse
from io import BytesIO

import vst2_funcs

sys.path.append('../')

from objects import dv_datadef
from objects import dv_dataset

dataset = dv_dataset.dataset('../data_dset/plugin_vst2.dset')

parser = argparse.ArgumentParser()
parser.add_argument("-i", default=None)
args = parser.parse_args()

input_file = args.i
extra_param = {}


fxpfile_file = open(input_file, 'rb')
fxpfile_file.seek(0,2)
fxpfile_filesize = fxpfile_file.tell()
fxpfile_file.seek(0)

vstdata = vst2_funcs.read_vst2_data(fxpfile_file)

if vstdata['datatype'] == 'raw':
	fourid = vstdata['plugin']['fourid']
	vstchunk = vstdata['data']

	print(fourid, vstchunk)

	with open('vst_'+str(fourid)+'_chunk', "wb") as fileout: fileout.write(vstchunk)

	isobjfound, v_datadef = dataset.object_var_get('datadef', 'plugin', str(fourid))
	isobjfound, v_struct = dataset.object_var_get('datadef_struct', 'plugin', str(fourid))
	if isobjfound:
		print('datadef found', v_struct+'@'+v_datadef)
		datadefpath = '../data_ddef/'+v_datadef
		datadef = dv_datadef.datadef(datadefpath)
		jsondecoded = datadef.parse(v_struct, vstchunk)
		for i, v in jsondecoded.items():
			print(i, v)
		with open('vst_'+str(fourid)+'_decoded.json', "w") as fileout: json.dump(jsondecoded, fileout, indent=4)


