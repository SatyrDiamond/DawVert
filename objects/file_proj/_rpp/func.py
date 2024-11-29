
from rpp import Element
from functions import data_values
import base64
import numpy as np

def iter_rpp(rpp_data):
	for rpp_var in rpp_data:
		if isinstance(rpp_var, list): yield rpp_var[0], False, rpp_var[1:], None
		else: yield rpp_var.tag, True, rpp_var.attrib, rpp_var.children

def valguesser(i_val):
	if i_val.replace('.','',1).lstrip('-+').isdigit(): 
		return float, float(i_val)
	else: 
		return str, i_val

def filldef(rppvals, defvals):
	outvals = defvals.copy()
	for n, v in enumerate(rppvals[0:len(defvals)]): 
		vartype, value = valguesser(v)
		outvals[n] = vartype(value)
	return outvals

def writestring(value):
	if isinstance(value, float): return ("%g" % value)
	else: return value

def writebin_named(rpp_data, name, bindata):
	rpp_tempd = rpp_obj(name,[])
	writebin(rpp_tempd, bindata)
	rpp_data.children.append(rpp_tempd)

def writebin(rpp_data, bindata):
	for binpart in data_values.list__chunks(bindata, 96):
		rpp_data.children.append(base64.b64encode(binpart).decode())

def getbin(rpp_data):
	return base64.b64decode(''.join(rpp_data))

def getbin_multi(rpp_data):
	bindata = [b'']
	for x in rpp_data:
		binpart = base64.b64decode(x)
		bindata[-1] += binpart
		if len(binpart) != 96: bindata += [b'']
	return bindata

def rpp_obj(i_name, i_vals): return Element(tag=i_name, attrib=i_vals, children=[])
def rpp_obj_data(i_name, i_vals, i_data): return Element(tag=i_name, attrib=i_vals, children=i_data)

def from_string(i_type, i_val): 
	if i_type == float: return float(i_val)
	if i_type == int: return int(i_val)
	if i_type == bool: return i_val=='1'
	if i_type == str: return i_val

def to_string(i_type, i_val): 
	if i_type == float: return str(int(i_val)) if float(i_val).is_integer() else np.format_float_positional(i_val)
	if i_type == int: return str(i_val)
	if i_type == bool: return '1' if i_val else '0'
	if i_type == str: return i_val

class rpp_value:
	__slots__ = ['values', 'names', 'types', 'used']
	def __init__(self, values=[], names=[], types=[], used=False):
		self.values = values
		self.names = names if names else ['unk'+str(x) for x in range(len(values))]
		self.types = types if types else [float for _ in range(len(values))]
		self.used = used

	def __setitem__(self, varname, data):
		self.values[self.names.index(varname)] = data
		
	def __getitem__(self, varname):
		return self.values[self.names.index(varname)]

	def read(self, values):
		self.used = True
		for n, v in enumerate(values[0:len(self.values)]):
			self.values[n] = from_string(self.types[n], values[n])

	def write(self, name, rppdata):
		if self.used:
			outdata = self.values.copy()
			for n, v in enumerate(outdata): outdata[n] = to_string(self.types[n], outdata[n])
			rppdata.children.append([name]+outdata)

	@classmethod
	def single_var(self, i_value, i_type, used):
		return self([i_value], ['value'], [i_type], used)

	def set(self, i_value):
		self.used = True
		valtype = self.types[0]
		if valtype == float: self.values[0] = float(i_value)
		if valtype == int: self.values[0] = int(i_value)
		if valtype == bool: self.values[0] = i_value=='1'
		if valtype == str: self.values[0] = i_value

	def get(self):
		return self.values[0]
