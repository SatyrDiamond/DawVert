# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import binascii

DEBUG_COLLECT = False

globalids = {}
if DEBUG_COLLECT:
	class_collect = {}

class sequel_object:
	def __init__(self, indata):
		self.obj_class = None
		self.obj_id = -1
		self.obj_data = {}
		self.ref_obj = None
		if indata is not None: self.read(indata)

	#def __bool__(self):
	#	return bool(self.obj_data) or bool(self.obj_class)

	def __repr__(self):
		outtxt = ''
		outtxt += 'Class: "'+str(self.obj_class)+'" '
		outtxt += 'Data: '+str(list(self.obj_data))
		return '<Seq3 Obj - %s>' % outtxt

	def __getitem__(self, k):
		return self.obj_data.__getitem__(k)

	def __contains__(self, k):
		return self.obj_data.__contains__(k)

	def read(self, indata):
		attrib = indata.attrib
		if 'class' in attrib: 
			self.obj_class = attrib['class']
			if DEBUG_COLLECT:
				if self.obj_class not in class_collect: class_collect[self.obj_class] = []
				class_collect[self.obj_class].append(self)
		if 'ID' in attrib: 
			self.obj_id = int(attrib['ID'])
			if indata:
				globalids[self.obj_id] = self
		for x in iter_xdata(indata):
			if not x[0]:
				print('unknown tag in obj:', x)
			else:
				self.obj_data[x[2]] = x[3]

	def write(self, xmldata, name):
		tempxml = ET.SubElement(xmldata, 'obj')
		if self.obj_class: tempxml.set('class', str(self.obj_class))
		if name: tempxml.set('name', name)
		if self.obj_id!=-1: tempxml.set('ID', str(self.obj_id))
		write_xdata(self.obj_data, tempxml)

class sequel_member:
	def __init__(self, indata):
		self.obj_data = {}
		if indata: self.read(indata)

	def __getitem__(self, k):
		return self.obj_data.__getitem__(k)

	def __contains__(self, k):
		return self.obj_data.__contains__(k)

	def read(self, indata):
		for x in iter_xdata(indata):
			if not x[0]:
				print('unknown tag in member:', x)
			else:
				self.obj_data[x[2]] = x[3]

	def write(self, xmldata, name):
		tempxml = ET.SubElement(xmldata, 'member')
		if name: tempxml.set('name', name)
		write_xdata(self.obj_data, tempxml)

def iter_xdata(xdata):
	for x in xdata:
		if x.tag == 'int':
			yield True, 'int', x.get('name'), getval__int(x)
		elif x.tag == 'float':
			yield True, 'float', x.get('name'), getval__float(x)
		elif x.tag == 'string':
			yield True, 'string', x.get('name'), getval__string(x)
		elif x.tag == 'list':
			yield True, 'list', x.get('name'), getval__list(x)
		elif x.tag == 'obj':
			yield True, 'object', x.get('name'), sequel_object(x)
		elif x.tag == 'member':
			yield True, 'member', x.get('name'), sequel_member(x)
		elif x.tag == 'bin':
			yield True, 'binary', x.get('name'), getval__bin(x)
		else:
			yield False, x.tag, x.attrib

def write_xdata(obj_data, xmldata):
	for k, v in obj_data.items():
		if isinstance(v, sequel_object):
			v.write(xmldata, k)
		elif isinstance(v, sequel_member):
			v.write(xmldata, k)
		elif isinstance(v, int):
			tempxml = ET.SubElement(xmldata, 'int')
			tempxml.set('name', k)
			tempxml.set('value', str(v))
		elif isinstance(v, bytes):
			tempxml = ET.SubElement(xmldata, 'bin')
			tempxml.set('name', k)
			tempxml.text = binascii.hexlify(v).decode()
		elif isinstance(v, float):
			tempxml = ET.SubElement(xmldata, 'float')
			tempxml.set('name', k)
			tempxml.set('value', str(v if v%1 else int(v)))
		elif isinstance(v, str):
			tempxml = ET.SubElement(xmldata, 'string')
			tempxml.set('name', k)
			tempxml.set('value', str(v))
			tempxml.set('wide', 'true')
		elif isinstance(v, list):
			tempxml = ET.SubElement(xmldata, 'list')
			tempxml.set('name', k)
			listtypes = [type(x) for x in v]

			if listtypes:
				sametype = all(x == listtypes[0] for x in listtypes)
				if sametype:
					listtype = listtypes[0]
					if listtype == sequel_object:
						tempxml.set('type', 'obj')
						for x in v:
							x.write(tempxml, None)
					elif listtype == int:
						tempxml.set('type', 'int')
						for x in v:
							inxml = ET.SubElement(tempxml, 'item')
							inxml.set('value', str(x))
					elif listtype == float:
						tempxml.set('type', 'float')
						for x in v:
							inxml = ET.SubElement(tempxml, 'item')
							inxml.set('value', str(x))
					elif listtype == str:
						tempxml.set('type', 'string')
						for x in v:
							inxml = ET.SubElement(tempxml, 'item')
							inxml.set('value', x)
					elif listtype == dict:
						tempxml.set('type', 'list')
						for x in v:
							inxml = ET.SubElement(tempxml, 'item')
							write_xdata(x, inxml)
					else:
						print('unknown', listtype)

		else:
			print( type(v) )

def getval__int(x):
	return int(x.get('value'))

def getval__float(x):
	return float(x.get('value'))

def getval__bin(x):
	return bytes.fromhex(x.text)

def getval__string(x):
	return x.get('value')

def getval__list(x):
	listtype = x.get('type')
	listdata = []
	if listtype=='obj':
		for d in x:
			if d.tag=='obj': listdata.append(sequel_object(d))
			#else: print('list: should be obj, not', d.tag, 'in', x.attrib)
	elif listtype=='int':
		for d in x:
			if d.tag=='item': listdata.append(int(d.get('value')))
			#else: print('list: should be item, not', d.tag, 'in', x.attrib)
	elif listtype=='float':
		for d in x:
			if d.tag=='item': listdata.append(float(d.get('value')))
			#else: print('list: should be item, not', d.tag, 'in', x.attrib)
	elif listtype=='string':
		for d in x:
			if d.tag=='item': listdata.append(d.get('value'))
			#else: print('list: should be item, not', d.tag, 'in', x.attrib)
	elif listtype=='list':
		for d in x:
			if d.tag=='item':
				itemdata = {}
				for i in iter_xdata(d):
					if not i[0]:
						print('unknown tag in list/list:', i)
					else:
						itemdata[i[2]] = i[3]
				listdata.append(itemdata)
			#else: print('list: should be item, not', d.tag, 'in', x.attrib)

	else:
		exit('unknown list type %s' % str(listtype))
	return listdata
