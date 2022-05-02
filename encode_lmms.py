import json
import xml.etree.ElementTree as ET 
import _func_instrument

def onetime2lmmstime(input):
	return int(round(float(input * 48)))

def oneto100(input):
	return round(float(input) * 100)

def lmms_encode_notelist(xmltag, table_notelist):
	for table_note in table_notelist:
		xml_pattern = ET.SubElement(xmltag, "note")
		key = table_note[2]
		position = int(round(float(table_note[0]) * 48))
		pan = oneto100(table_note[4])
		duration = int(round(float(table_note[1]) * 48))
		vol = oneto100(table_note[3])
		xml_pattern.set('key', str(key))
		xml_pattern.set('pos', str(int(round(position))))
		xml_pattern.set('pan', str(pan))
		xml_pattern.set('len', str(int(round(duration))))
		xml_pattern.set('vol', str(vol))


def lmms_encode_inst_track(xmltag, json_singletrack):
	xmltag.set('solo', "0")
	xmltag.set('name', "untitled")
	xmltag.set('type', "0")
	xmltag.set('muted', "0")
	if json_singletrack['muted'] is not None:
		xmltag.set('muted', str(json_singletrack['muted']))
	if json_singletrack['name'] is not None:
		xmltag.set('name', json_singletrack['name'])
	#instrumenttrack
	json_instrumentdata = json_singletrack['instrumentdata']
	xml_instrumenttrack = ET.SubElement(xmltag, "instrumenttrack")
	xml_instrumenttrack.set('pitch', "0")
	if json_instrumentdata['basenote'] is not None:
		xml_instrumenttrack.set('pan', str(json_instrumentdata['basenote'] - 3))
	xml_instrumenttrack.set('basenote', "57")
	xml_instrumenttrack.set('pan', "0")
	xml_instrumenttrack.set('usemasterpitch', "1")
	xml_instrumenttrack.set('pitchrange', "12")
	xml_instrumenttrack.set('vol', "100")
	if json_singletrack['pan'] is not None:
		xml_instrumenttrack.set('pan', str(oneto100(json_singletrack['pan'])))
	if json_singletrack['vol'] is not None:
		xml_instrumenttrack.set('vol', str(oneto100(json_singletrack['vol'])))
	#placements
	json_placementlist = json_singletrack['placements']
	table_placementlist = _func_instrument.nlplacementsCONVPROJ_to_nlplacementsTABLE(json_placementlist)
	tracksnum = 0
	while tracksnum <= len(table_placementlist)-1:
		table_placement = table_placementlist[tracksnum-1]
		table_notelist = table_placement[1]
		xml_pattern = ET.SubElement(xmltag, "pattern")
		xml_pattern.set('pos', str(int(table_placement[0] * 48)))
		xml_pattern.set('muted', "0")
		xml_pattern.set('steps', "16")
		xml_pattern.set('name', "untitled")
		xml_pattern.set('type', "1")
		lmms_encode_notelist(xml_pattern, table_notelist)
		tracksnum += 1

def lmms_encode_tracks(xmltag, json_tracks):
	for json_singletrack in json_tracks:
		xml_track = ET.SubElement(xml_trackcontainer, "track")
		lmms_encode_inst_track(xml_track, json_singletrack)


with open('org.json', 'r') as progfile:
		json_proj = json.loads(progfile.read())

json_tracks = json_proj['tracks']

xml_proj = ET.Element("lmms-project")
xml_proj.set('type', "song")
xml_head = ET.SubElement(xml_proj, "head")
xml_head.set('masterpitch', "0")
xml_head.set('mastervol', "100")
xml_head.set('timesig_numerator', "4")
xml_head.set('timesig_denominator', "4")
xml_head.set('bpm', "140")
if json_proj['tracks'] is not None:
	xml_head.set('mastervol', str(oneto100(json_proj['mastervol'])))
if json_proj['tracks'] is not None:
	xml_head.set('timesig_numerator', str(json_proj['timesig_numerator']))
if json_proj['tracks'] is not None:
	xml_head.set('timesig_denominator', str(json_proj['timesig_denominator']))
if json_proj['tracks'] is not None:
	xml_head.set('bpm', str(json_proj['bpm']))

xml_song = ET.SubElement(xml_proj, "song")
xml_trackcontainer = ET.SubElement(xml_song, "trackcontainer")

lmms_encode_tracks(xml_trackcontainer, json_tracks)

outfile = ET.ElementTree(xml_proj)


ET.indent(outfile)
outfile.write('out.mmp', encoding='unicode')
