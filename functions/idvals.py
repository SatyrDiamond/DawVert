import csv
import os

def parse_idvalscsv(filename):
	if os.path.exists(filename) == True:
		with open('G:\\git\\DawVert\\idvals\\notessimo_v2_inst.csv') as csvfile:
			spamreader = csv.reader(csvfile, delimiter=';', quotechar='|')
			count = 0
			typecount = 0
			l_params = {}
			tid_id = None
			tid_params = {}
			for row in spamreader:
				if count == 0:
					for valtype in row:
						if valtype == 'id': tid_id = typecount
						else: tid_params[valtype] = typecount
						typecount += 1
				else:
					l_params[row[tid_id]] = {}
					for tid_param in tid_params:
						out_value = row[tid_params[tid_param]]
						if tid_param == 'color_r': l_params[row[tid_id]][tid_param] = float(out_value)
						elif tid_param == 'color_g': l_params[row[tid_id]][tid_param] = float(out_value)
						elif tid_param == 'color_b': l_params[row[tid_id]][tid_param] = float(out_value)
						elif tid_param == 'isdrum': l_params[row[tid_id]][tid_param] = bool(out_value)
						elif tid_param == 'gm_inst':
							if out_value == 'null': l_params[row[tid_id]][tid_param] = None
							else: l_params[row[tid_id]][tid_param] = int(out_value)
						else: l_params[row[tid_id]][tid_param] = out_value
				count += 1
		return l_params
	else:
		return {}

def get_idval(valdata, i_id, i_param):
	if i_param == 'name':
		outval = 'noname'
		if i_id in valdata:
			if 'name' in valdata[i_id]: outval = valdata[i_id]['name']
	if i_param == 'color':
		outval = None
		if i_id in valdata:
			valdata_f = valdata[i_id]
			if 'color_r' in valdata_f: 
				if 'color_g' in valdata_f: 
					if 'color_b' in valdata_f: 
						outval = [valdata_f['color_r'], valdata_f['color_g'], valdata_f['color_b']]
	if i_param == 'isdrum':
		outval = False
		if i_id in valdata:
			if 'isdrum' in valdata[i_id]: outval = valdata[i_id]['isdrum']
	if i_param == 'gm_inst':
		outval = None
		if i_id in valdata:
			if 'gm_inst' in valdata[i_id]: outval = valdata[i_id]['gm_inst']

	return outval

#parse_idvalscsv('notessimo_v2_inst.csv')
#get_idval(valsdata, id_fine, 'name')







