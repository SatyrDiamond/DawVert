
from objects.data_bytes import bytereader
import os
from lxml import etree as ET
import zlib
import gzip
import zipfile
import fnmatch
import re

class file_detector_bytesheader:
	def __init__(self):
		self.offset = 0
		self.data = b''

	def detect(self, data):
		endpart = self.offset+len(self.data)
		if len(data)>=endpart:
			if data[self.offset:endpart]==self.data:
				return True
		return False


class file_detector_def:
	def __init__(self):
		self.is_folder = False

		self.file__type = None
		self.file__ext = []
		self.file__format = None

		self.xml__root_name = None

		self.plug__set = None
		self.plug__name = None

		self.folder__fileext = None
		self.folder__files = []

		self.bytesheaders = []

		self.compressed__type = None
		self.compressed__required = False
		self.compressed__offset = 0

		self.archived__type = None
		self.archived__required = False
		self.archived__infiles = []

	def from_xml(self, xml_data):
		self.plug__set = xml_data.get('pluginset')
		self.plug__name = xml_data.get('name')
		for x_part in xml_data:
			attrib = x_part.attrib
			if x_part.tag == 'file':
				self.is_folder = False
				if 'fileext' in attrib: self.file__ext = attrib['fileext'].split(';')

			if x_part.tag == 'folder':
				self.is_folder = True
				if 'fileext' in attrib: self.folder__fileext = attrib['fileext'].split(';')
				if 'files' in attrib: self.folder__files = attrib['files'].split(';')

			if x_part.tag == 'xml':
				self.file__type = 'text'
				self.file__format = 'xml'
				if 'root_name' in attrib: self.xml__root_name = attrib['root_name']

			if x_part.tag == 'bytes_header':
				self.file__type = 'bytes'
				bytesheader = file_detector_bytesheader()
				if 'pos' in attrib: bytesheader.offset = int(attrib['pos'])
				if 'data' in attrib: bytesheader.data = bytes.fromhex(attrib['data'])
				self.bytesheaders.append(bytesheader)

			if x_part.tag == 'compressed':
				self.compressed__required = True
				if 'type' in attrib: self.compressed__type = attrib['type']
				if 'optional' in attrib: self.compressed__required = not attrib['optional']=='1'
				if 'offset' in attrib: self.compressed__offset = int(attrib['offset'])

			if x_part.tag == 'archived':
				self.archived__required = True
				if 'type' in attrib: self.archived__type = attrib['type']
				if 'optional' in attrib: self.archived__required = not attrib['optional']=='1'
				if self.archived__type == 'zip':
					if 'file' in attrib: self.archived__infiles = attrib['file'].split(';')

def comp__detect(offset, proj_file, comptype): 
	proj_file.seek(offset)
	if comptype == 'zlib': return proj_file.raw(2) in [b'\x78\x08', b'\x78\x5E', b'\x78\x9C', b'\x78\xDA']
	if comptype == 'gzip': return proj_file.raw(3) == b'\x1f\x8b\x08'

def comp__startdata(offset, proj_file, comptype):
	proj_file.seek(offset)
	try:
		if comptype == 'zlib':
			decomp_obj = zlib.decompressobj(wbits=zlib.MAX_WBITS)
			data = decomp_obj.decompress(proj_file.raw(1024), max_length=512)
			return True, data
		if comptype == 'gzip':
			decomp_obj = gzip.GzipFile(fileobj=proj_file)
			data = f.read(512)
			return True, data
	except: return False, b''

DEBUGTXT = False

class file_detector:
	def __init__(self):
		self.formats = []
		self.q_filenames = {}
		self.q_file = []
		self.q_folder = []

		self.q_archived__type = {}
		self.q_nonarchived_none = []
		self.q_nonarchived_xml = [[],[]]
		self.q_filenames = {}

	def load_def(self, filename):
		parser = ET.XMLParser()
		xml_data = ET.parse(filename, parser)
		xml_defs = xml_data.getroot()
		for x_part in xml_defs:
			def_file = file_detector_def()
			def_file.from_xml(x_part)
			if not def_file.is_folder: self.q_file.append(def_file)
			else: self.q_folder.append(def_file)

			if def_file.file__ext:
				for fileext in def_file.file__ext:
					self.q_filenames[fileext] = def_file

			q_archived__type = def_file.archived__type
			if q_archived__type: 
				if q_archived__type not in self.q_archived__type: 
					self.q_archived__type[q_archived__type] = []
				self.q_archived__type[q_archived__type].append(def_file)
				if not def_file.archived__required: self.q_nonarchived_none.append(def_file)
			else:
				if def_file.file__format==None: self.q_nonarchived_none.append(def_file)
				if def_file.file__format=='xml': 
					self.q_nonarchived_xml[int(bool(def_file.compressed__type))].append(def_file)
		

	def detect_file(self, filename):
		if os.path.exists(filename):
			f_name, f_ext = os.path.splitext(filename) 
			f_ext = f_ext.lower()

			if os.path.isdir(filename):
				if DEBUGTXT: print('TRY: folder')
				listfiles = os.listdir(filename)
				for det_obj in self.q_folder:
					infiles = det_obj.folder__files
					cond_files = (True in [(x in infiles) for x in listfiles]) if listfiles else True
					cond_ext = (True in [(x in f_ext) for x in det_obj.file__ext]) if det_obj.file__ext else True
					if cond_files and cond_ext: return det_obj.plug__set, det_obj.plug__name
	
			else:
				proj_file = bytereader.bytereader()
				proj_file.load_file(filename)
	
				archived_type = None
	
				proj_file.seek(0)
				if proj_file.raw(4) == b'PK\x03\x04': archived_type = 'zip'
				proj_file.seek(0)

				if archived_type:
					if archived_type in self.q_archived__type:
						if archived_type == 'zip':

							if DEBUGTXT: print('TRY: zip_data')
							zip_data = zipfile.ZipFile(filename, 'r')
							namelist = zip_data.namelist()
							for det_obj in self.q_archived__type[archived_type]:
								infiles = det_obj.archived__infiles

								outcheck = []
								for zipname in namelist:
									for infile in infiles:
										if fnmatch.fnmatch(zipname, infile):
											outcheck.append(zipname)

								if outcheck: return det_obj.plug__set, det_obj.plug__name
				else:
					for det_obj in self.q_nonarchived_none:
						if DEBUGTXT: print('TRY: data')
						compressed__type = det_obj.compressed__type

						data = b''

						comp_valid = False
						if compressed__type:
							if DEBUGTXT: print('TRY: data: compressed')
							if comp__detect(det_obj.compressed__offset, proj_file, compressed__type):
								comp_valid, decomp_data = comp__startdata(det_obj.compressed__offset, proj_file, compressed__type)
								if comp_valid: data = decomp_data

						if len(data)==0:
							proj_file.seek(0)
							data = proj_file.read(256)

						arequired = False
						brequired = False
						if det_obj.compressed__type: arequired = det_obj.compressed__required
						elif det_obj.archived__type: brequired = det_obj.archived__required

						if data and (False in [arequired, brequired]):
							for bytesheader in det_obj.bytesheaders:
								if bytesheader.detect(data): 
									return det_obj.plug__set, det_obj.plug__name

					if f_ext in self.q_filenames:
						det_obj = self.q_filenames[f_ext]
						return det_obj.plug__set, det_obj.plug__name

					try:
						if DEBUGTXT: print('TRY: xml')
						parser = ET.XMLParser()
						xml_data = ET.parse(filename, parser)
						xml_root = xml_data.getroot()
						for det_obj in self.q_nonarchived_xml[0]:
							if det_obj.xml__root_name == xml_root.tag:
								return det_obj.plug__set, det_obj.plug__name
					except: pass

					for det_obj in self.q_nonarchived_xml[1]:
						if DEBUGTXT: print('TRY: compressed xml')
						compressed__type = det_obj.compressed__type
						if comp__detect(det_obj.compressed__offset, proj_file, compressed__type):
							comp_valid, decomp_data = comp__startdata(det_obj.compressed__offset, proj_file, compressed__type)
							if comp_valid:
								try:
									textstring = decomp_data.decode()
									if comp_valid: 
										for x in re.findall(r'\<(.*?)\>',textstring):
											if x:
												firstletter = x[0]
												if firstletter not in ['?', '!', ' ']:
													splitstr = x.split(' ', 1)
													if splitstr: return det_obj.plug__set, det_obj.plug__name
													else: break
								except:
									pass
