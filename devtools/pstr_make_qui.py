import os
import json
from lxml import etree as ET

infolder = os.path.join('data_main','plugstatets')
outfile = os.path.join('data_main','plugstatets_index.json')

outdata = {}

for f in os.listdir(infolder):
	pathd = os.path.join(infolder, f)
	for x in os.listdir(pathd):
		filepath = os.path.join(pathd, x)
		basename = os.path.splitext(os.path.basename(f))[0]
	
		parser = ET.XMLParser()
		xml_data = ET.parse(filepath, parser)
		xml_proj = xml_data.getroot()
	
		outjson = {}
	
		priority = 0
	
		outjson['file'] = filepath
	
		inplugs = xml_proj.get('plugtype')
		inplugs_s = inplugs.split(':')
		outplugs = [x.get('plugtype') for x in xml_proj.findall('.//replace')]+[x.get('plugtype') for x in xml_proj.findall('.//replace_hard')]
		outplugs_s = [x.split(':') for x in outplugs]
	
		if inplugs_s[0] == 'universal' and outplugs_s[0][0] != 'universal':
			priority = 100
		if inplugs_s[0] != 'universal' and outplugs_s[0][0] == 'universal':
			priority = -100
	
		hpriority = xml_proj.get('priority')
		if hpriority: priority = int(hpriority)
	
		daw_in = xml_proj.get('daw_in')
		if daw_in: outjson['daw_in'] = daw_in.split(';')
		daw_out = xml_proj.get('daw_out')
		if daw_out: outjson['daw_out'] = daw_out.split(';')
	
		outjson['plugtype_in'] = inplugs
		outjson['plugtype_out'] = outplugs
		outjson['priority'] = priority
	
		outdata[filepath] = outjson

f = open(outfile, 'w')
json.dump(outdata, f, indent=2)