# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.data_bytes import bytereader
from objects.data_bytes import bytewriter
import logging

def make_id(value, byw_stream):
	out = ('0'*(8-len(value)))+value
	byw_stream.raw(bytes.fromhex(out)[4::-1])

def get_id(byr_stream):
	outv = byr_stream.raw(4)[4::-1].hex()
	while outv:
		if outv[0] == '0': outv = outv[1:]
		else: break
	return outv

class tracktion_project_object:
	def __init__(self):
		self.name = ''
		self.type = ''
		self.info = ''
		self.path = ''
		self.id = ''
		self.id2 = ''

	def read(self, byr_stream):
		self.name = byr_stream.string_t()
		self.type = byr_stream.string_t()
		self.info = byr_stream.string_t()
		self.path = byr_stream.string_t()
		self.id = get_id(byr_stream)
		self.id2 = get_id(byr_stream)

	def __len__(self):
		out = 0
		out += len(self.name.encode())+1
		out += len(self.type.encode())+1
		out += len(self.info.encode())+1
		out += len(self.path.encode())+1
		return out

	def write(self, byw_stream):
		byw_stream.string_t(self.name)
		byw_stream.string_t(self.type)
		byw_stream.string_t(self.info)
		byw_stream.string_t(self.path)
		make_id(self.id, byw_stream)
		make_id(self.id2, byw_stream)

class tracktion_project:
	def __init__(self):
		self.projectId = 0
		self.props = {}
		self.objects = {}
		self.indexes = {}

	def load_from_file(self, input_file):
		byr_stream = bytereader.bytereader()
		byr_stream.load_file(input_file)
		byr_stream.magic_check(b'TP01')

		self.projectId = get_id(byr_stream)
		objectOffset = byr_stream.uint32()
		indexOffset = byr_stream.uint32()
		numprops = byr_stream.uint32()

		for _ in range(numprops):
			name = byr_stream.string_t()
			data = byr_stream.c_string__int32(False)
			self.props[name] = data

		byr_stream.seek(objectOffset)

		wobjects = []

		num = byr_stream.uint32()
		if (num < 20000):
			for _ in range(num):
				itemID = get_id(byr_stream)
				fileOffset = byr_stream.uint32()
				wobjects.append([itemID, fileOffset])

		for itemID, fileOffset in wobjects:
			byr_stream.seek(fileOffset)
			obj_obj = tracktion_project_object()
			obj_obj.read(byr_stream)
			self.objects[itemID] = obj_obj

		byr_stream.seek(indexOffset)
		for _ in range(byr_stream.uint32()):
			name = byr_stream.string_t()
			numids = byr_stream.uint16() 
			iids = [get_id(byr_stream) for x in range(numids)]
			self.indexes[name] = iids

	def write(self, byw_stream):
		byw_stream.raw(b'TP01')
		make_id(self.projectId, byw_stream)

		objectOffset = 16
		part_first = bytewriter.bytewriter()
		part_first.uint32(len(self.props))
		for k, d in self.props.items():
			part_first.string_t(k)
			part_first.c_string__int32(d)
		objectOffset += len(part_first.getvalue())

		offsets = []
		part_second = bytewriter.bytewriter()
		for k, d in self.objects.items(): 
			offsets.append(objectOffset+part_second.end)
			d.write(part_second)
		objectOffset += len(part_second.getvalue())

		part_third = bytewriter.bytewriter()
		part_third.uint32(len(self.objects))
		for n, k in enumerate(self.objects): 
			make_id(k, part_third)
			part_third.uint32(offsets[n])

		byw_stream.uint32(objectOffset)
		objectOffset += len(part_third.getvalue())

		part_fourth = bytewriter.bytewriter()
		part_fourth.uint32(len(self.indexes))
		for k, d in self.indexes.items():
			part_fourth.string_t(k)
			part_fourth.uint16(len(d)) 
			for c in d: make_id(c, part_fourth)

		byw_stream.uint32(objectOffset)

		byw_stream.raw(part_first.getvalue())
		byw_stream.raw(part_second.getvalue())
		byw_stream.raw(part_third.getvalue())
		byw_stream.raw(part_fourth.getvalue())

	def save_to_file(self, output_file):
		byw_stream = bytewriter.bytewriter()
		self.write(byw_stream)
		f = open(output_file, 'wb')
		f.write(byw_stream.getvalue())
