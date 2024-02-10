
import os
import argparse
from io import BytesIO

import vst2_funcs

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
	print(vstchunk)

	with open('vst_'+str(fourid)+'_chunk', "wb") as fileout:
		fileout.write(vstchunk)