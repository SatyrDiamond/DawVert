
from functions import data_bytes
import struct
from io import BytesIO
from functions_plugin_ext import plugin_vst2
from objects.data_bytes import dv_datadef
from objects import dv_dataset

XTPM_valid = [b'...P',b'...R',b'..BM',b'..CM',b'..EP',b'..EV',b'..MF',b'..OF',b'..PM',b'..RV',b'..SC',b'..SR',b'.[EP',b'.[EV',b'.[PP',b'.[PV',b'.EiP',b'.PiM',b'[EiP',b'[PiP',b'DWPM',b'HEVP',b'HOVP',b'LTTP',b'NREA',b'NREP',b'NREV',b'PTTF']
STPM_valid = [b'...C',b'..MT',b'..PR',b'..TD',b'.APS',b'.BPR',b'.FSM',b'.MMP',b'.MPR',b'.VGD',b'.VWC',b'AMIM',b'AUTH',b'CCOL',b'CUES',b'DTFR',b'RSMP',b'SnhC',b'SWNG',b'VTSV',b'VWSL']

def plugin__add(convproj_obj, omptp_num, omptp_type, omptp_id, omptp_name, omptp_libname, omptp_chunkdata, datadef, dataset):
	pluginid = 'FX'+str(omptp_num)
	if omptp_type == b'OMXD':
		plugin_obj = convproj_obj.plugin__add(pluginid, 'external', 'directx', omptp_libname)
		jsondecoded = datadef.parse(omptp_libname.lower(), omptp_chunkdata)
		plugin_obj.param_dict_dataset_get(jsondecoded, dataset, 'plugin', omptp_libname.lower())
	elif omptp_type == b'PtsV':
		plugin_obj = convproj_obj.plugin__add(pluginid, 'external', 'vst2', None)
		plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'win', omptp_id, 'chunk', omptp_chunkdata, 0)
	elif omptp_type == b'DBM0':
		paramdata = omptp_chunkdata[4:]
		plugin_obj = convproj_obj.plugin__add(pluginid, 'native', 'digibooster', 'pro_echo')
		plugin_obj.params.add('delay', paramdata[0], 'int')
		plugin_obj.params.add('fb', paramdata[1], 'int')
		plugin_obj.params.add('wet', paramdata[2], 'int')
		plugin_obj.params.add('cross_echo', paramdata[3], 'int')
	elif omptp_type == b'SymM':
		paramdata = omptp_chunkdata[4:]
		plugin_obj = convproj_obj.plugin__add(pluginid, 'native', 'symmod', 'echo')
		plugin_obj.params.add('type', paramdata[0], 'int')
		plugin_obj.params.add('delay', paramdata[1], 'int')
		plugin_obj.params.add('fb', paramdata[2], 'int')

def parse_start(filestream, convproj_obj):
	datadef = dv_datadef.datadef('./data_main/datadef/openmpt.ddef')
	dataset = dv_dataset.dataset('./data_main/dataset/openmpt.dset')

	patnames = None
	channames = None

	while True:
		chunk_header = filestream.read(4)
		if chunk_header == b'XTPM':
			filestream.seek(filestream.tell()-4)
			break
			
		chunk_size = int.from_bytes(filestream.read(4), "little")
		chunk_value = BytesIO(filestream.read(chunk_size))

		if chunk_header == b'PNAM':
			patnames = [data_bytes.readstring_fixedlen(chunk_value, 32, "windows-1252") for x in range(chunk_size//32) ]

		elif chunk_header == b'CNAM':
			channames = [data_bytes.readstring_fixedlen(chunk_value, 20, "windows-1252") for x in range(chunk_size//20) ]

		elif chunk_header[0:2] == b'FX':
			omptp_num = int(chunk_header[2:4].decode())+1
			omptp_type = chunk_value.read(4)
			omptp_id = int.from_bytes(chunk_value.read(4), "little")
			omptp_route = chunk_value.read(1)
			omptp_mix = chunk_value.read(1)
			omptp_gain = chunk_value.read(1)
			chunk_value.read(1)
			omptp_output_routing = chunk_value.read(4)
			chunk_value.read(16)
			omptp_name = data_bytes.readstring_fixedlen(chunk_value, 32, "windows-1252")
			omptp_libname = data_bytes.readstring_fixedlen(chunk_value, 64, "windows-1252")
			omptp_chunksize = int.from_bytes(chunk_value.read(4), "little")
			omptp_chunkdata = chunk_value.read(omptp_chunksize)
			#print('[input-it] Plugin '+str(omptp_num)+': '+omptp_type.decode()+': '+omptp_libname)
			plugin__add(convproj_obj, omptp_num, omptp_type, omptp_id, omptp_name, omptp_libname, omptp_chunkdata, datadef, dataset)

		else: break

	return patnames, channames

def parse_xtst(filestream, num_insts):

	XTPM_data = [[] for x in range(num_insts)]
	STPM_data = []

	extension_name = filestream.read(4)

	if extension_name == b'XTPM':
		while True:
			chunk_header = filestream.read(4)
			if chunk_header == b'STPM': 
				extension_name = chunk_header
				break
			chunk_size = int.from_bytes(filestream.read(2), "little")
			if chunk_header in XTPM_valid: 
				for n in range(num_insts):
					XTPM_data[n].append([chunk_header, filestream.read(chunk_size)])
			else: break

	if extension_name == b'STPM':
		while True:
			chunk_header = filestream.read(4)
			chunk_size = int.from_bytes(filestream.read(2), "little")
			chunk_value = filestream.read(chunk_size)

			if chunk_header in STPM_valid: 
				XTPM_val = chunk_value
				if chunk_header == b'CCOL':
					t_colordata = struct.unpack('I'*(len(XTPM_val)//4), XTPM_val)
					XTPM_val = []
					for n, c in enumerate(t_colordata):
						pc = struct.unpack('BBBB', struct.pack('I', c))
						XTPM_val.append([pc[0]/255, pc[1]/255, pc[2]/255])
				STPM_data.append([chunk_header, XTPM_val])
			else:
				break

	return XTPM_data, STPM_data
