import xml.etree.ElementTree as ET
import _func_instrument
import _func_audio
import json

print('--- LMMS to ConvJson OTMN ---')

def hundredto1(input):
	return float(input) * 0.01

def lmms_decode_pattern(notesxml):
	notelist = []
	print('\t\tNotes:', end=' ')
	printcountpat = 0
	for notexml in notesxml:
		notejson = {}
		notejson['key'] = int(notexml.get('key'))
		notejson['position'] = float(notexml.get('pos')) / 48
		notejson['pan'] = hundredto1(notexml.get('pan'))
		notejson['duration'] = float(notexml.get('len')) / 48
		notejson['vol'] = hundredto1(notexml.get('vol'))
		printcountpat += 1
		print(str(printcountpat), end=' ')
		notelist.append(notejson)
	print(' ')
	return notelist

def lmms_decode_nlplacements(trackxml):
	nlplacements = []
	patternsxml = trackxml.findall('pattern')
	printcountplace = 0
	for patternxml in patternsxml:
		print('\tPlacement ' + str(printcountplace) + ': ')
		printcountplace += 1
		placementjson = {}
		placementjson["position"] = float(patternxml.get('pos')) / 48
		notesxml = patternxml.findall('note')
		placementjson["notelist"] = lmms_decode_pattern(notesxml)
		nlplacements.append(placementjson)
	return nlplacements

def asdflfo(trackjson, xmlobj, type):
	trackjson['mod.' + type] = {}
	trackjson['mod.' + type]['envelope'] = {}
	trackjson['mod.' + type]['envelope']['predelay'] = float(xmlobj.get('pdel'))
	trackjson['mod.' + type]['envelope']['attack'] = float(xmlobj.get('att'))
	trackjson['mod.' + type]['envelope']['hold'] = float(xmlobj.get('hold'))
	trackjson['mod.' + type]['envelope']['decay'] = float(xmlobj.get('dec'))
	trackjson['mod.' + type]['envelope']['sustain'] = float(xmlobj.get('sustain'))
	trackjson['mod.' + type]['envelope']['release'] = float(xmlobj.get('rel'))
	trackjson['mod.' + type]['envelope']['amount'] = float(xmlobj.get('amt'))
	if xmlobj.get('x100') is not None:
		speedx100 = float(xmlobj.get('x100')) * 100
		if speedx100 == 0:
			speedx100 = 1
	trackjson['mod.' + type]['lfo'] = {}
	trackjson['mod.' + type]['lfo']['predelay'] = float(xmlobj.get('lpdel'))
	trackjson['mod.' + type]['lfo']['attack'] = float(xmlobj.get('latt'))
	trackjson['mod.' + type]['lfo']['speed'] = float(xmlobj.get('lspd')) * speedx100
	trackjson['mod.' + type]['lfo']['amount'] = float(xmlobj.get('lamt'))


def lmms_decode_inst_track(trackxml):
	trackjson = _func_instrument.init_instrument_trackdataCONVPROJ()
	trackjson['name'] = trackxml.get('name')
	print('Instrument Track Name: ' + trackjson['name'])
	trackjson['muted'] = int(trackxml.get('muted'))
	trackjson_instdata = trackjson['instrumentdata']
	trackxml_insttr = trackxml.findall('instrumenttrack')[0]
	trackxml_insttr_eldata = trackxml_insttr.findall('eldata')[0]
	trackjson['pan'] = hundredto1(trackxml_insttr.get('pan'))
	trackjson['vol'] = hundredto1(trackxml_insttr.get('vol'))
	trackjson_instdata['usemasterpitch'] = int(trackxml_insttr.get('usemasterpitch'))
	trackjson_instdata['pitch'] = 0
	if trackxml_insttr.get('pitch') != None:
		trackjson_instdata['pitch'] = float(trackxml_insttr.get('pitch'))
	trackjson_instdata['basenote'] = int(trackxml_insttr.get('basenote')) + 3
	trackxml_chordcreator = trackxml_insttr.findall('chordcreator')[0]
	trackjson_instdata['chordcreator'] = {}
	trackjson_instdata['chordcreator']['enabled'] = int(trackxml_chordcreator.get('chord-enabled'))
	trackjson_instdata['chordcreator']['chordrange'] = int(trackxml_chordcreator.get('chordrange'))
	trackjson_instdata['chordcreator']['chord'] = int(trackxml_chordcreator.get('chord'))
	trackxml_arpeggiator = trackxml_insttr.findall('arpeggiator')[0]
	trackjson_instdata['arpeggiator'] = {}
	trackjson_instdata['arpeggiator']['gate'] = int(trackxml_arpeggiator.get('arpgate'))
	trackjson_instdata['arpeggiator']['arprange'] = int(trackxml_arpeggiator.get('arprange'))
	trackjson_instdata['arpeggiator']['enabled'] = int(trackxml_arpeggiator.get('arp-enabled'))
	trackjson_instdata['arpeggiator']['mode'] = int(trackxml_arpeggiator.get('arpmode'))
	trackjson_instdata['arpeggiator']['direction'] = int(trackxml_arpeggiator.get('arpdir'))
	trackjson_instdata['arpeggiator']['skiprate'] = int(trackxml_arpeggiator.get('arpskip')) #percent
	trackjson_instdata['arpeggiator']['time'] = int(trackxml_arpeggiator.get('arptime')) #ms
	trackjson_instdata['arpeggiator']['missrate'] = int(trackxml_arpeggiator.get('arpmiss')) #percent
	trackjson_instdata['arpeggiator']['cyclenotes'] = int(trackxml_arpeggiator.get('arpcycle'))
	trackjson_instdata['arpeggiator']['chord'] = int(trackxml_arpeggiator.get('arp'))
	trackjson['placements'] = lmms_decode_nlplacements(trackxml)
	return trackjson

def lmms_decode_audioplacements(trackxml):
	audioplacements = []
	patternsxml = trackxml.findall('sampletco')
	printcountplace = 0
	print('\tPlacements:', end=' ')
	for patternxml in patternsxml:
		printcountplace += 1
		print(str(printcountplace), end=' ')
		audioplacementsjson = {}
		audioplacementsjson['position'] = float(patternxml.get('pos')) / 48
		audioplacementsjson['duration'] = float(patternxml.get('len')) / 48
		audioplacementsjson['file'] = patternxml.get('src')
		audioplacements.append(audioplacementsjson)
	print('')
	return audioplacements

def lmms_decode_audio_track(trackxml):
	trackjson = _func_audio.init_audio_trackdataCONVPROJ()
	trackjson['name'] = trackxml.get('name')
	print('Audio Track Name: ' + trackjson['name'])
	trackjson['muted'] = int(trackxml.get('muted'))
	trackxml_insttr = trackxml.findall('sampletrack')[0]
	trackjson['pan'] = hundredto1(trackxml_insttr.get('pan'))
	trackjson['vol'] = hundredto1(trackxml_insttr.get('vol'))
	trackjson['placements'] = lmms_decode_audioplacements(trackxml)
	return trackjson

def lmms_decode_tracks(tracksxml):
	tracklist = []
	for trackxml in tracksxml:
		tracktype = trackxml.get('type')
		if tracktype == "0":
			tracklist.append(lmms_decode_inst_track(trackxml))
		if tracktype == "2":
			tracklist.append(lmms_decode_audio_track(trackxml))
	return tracklist

tree = ET.parse('test.mmp').getroot()
headxml = tree.findall('head')[0]
tracksxml = tree.findall('song/trackcontainer/track')

json_root = {}
json_root['datatype'] = 'otmn'
json_root['mastervol'] = float(hundredto1(headxml.get('mastervol')))
json_root['timesig_numerator'] = int(headxml.get('timesig_numerator'))
json_root['timesig_denominator'] = int(headxml.get('timesig_denominator'))
json_root['bpm'] = int(headxml.get('bpm'))
json_root['tracks'] = lmms_decode_tracks(tracksxml)

with open('proj.conv_otmn', 'w') as outfile:
        outfile.write(json.dumps(json_root, indent=2))
