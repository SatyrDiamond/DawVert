# SPDX-FileCopyrightText: 2022 Colby Ray
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import xml.etree.ElementTree as ET 
import argparse
import _func_song

parser = argparse.ArgumentParser()
parser.add_argument("cvpj")
parser.add_argument("mpp")

args = parser.parse_args()

def onetime2lmmstime(input):
	return int(round(float(input * 48)))

def oneto100(input):
	return round(float(input) * 100)

def lmms_encode_notelist(xmltag, json_notelist):
	print('\t\tNotes:', end=' ')
	printcountpat = 0
	for json_note in json_notelist:
		xml_pattern = ET.SubElement(xmltag, "note")
		key = json_note['key'] + 60
		position = int(round(float(json_note['position']) * 48))
		pan = oneto100(json_note['pan'])
		duration = int(round(float(json_note['duration']) * 48))
		vol = oneto100(json_note['vol'])
		xml_pattern.set('key', str(key))
		xml_pattern.set('pos', str(int(round(position))))
		xml_pattern.set('pan', str(pan))
		xml_pattern.set('len', str(int(round(duration))))
		xml_pattern.set('vol', str(vol))
		printcountpat += 1
		print(str(printcountpat), end=' ')
	print(' ')

def lmms_encode_plugin(xmltag, json_singletrack):
	pluginname = json_singletrack['instrumentdata']['plugin']
	xml_instrumentpreplugin = ET.SubElement(xmltag, "instrument")
	if pluginname == 'soundfont2':
		xml_instrumentpreplugin.set('name', "sf2player")
		xml_sf2 = ET.SubElement(xml_instrumentpreplugin, "sf2player")
		xml_sf2.set('bank', str(json_singletrack['instrumentdata']['plugindata']['bank']))
		xml_sf2.set('gain', str(json_singletrack['instrumentdata']['plugindata']['gain']))
		xml_sf2.set('patch', str(json_singletrack['instrumentdata']['plugindata']['patch']))
		xml_sf2.set('src', str(json_singletrack['instrumentdata']['plugindata']['file']))
		xml_sf2.set('reverbDamping', str(json_singletrack['instrumentdata']['plugindata']['reverb']['damping']))
		xml_sf2.set('reverbLevel', str(json_singletrack['instrumentdata']['plugindata']['reverb']['level']))
		xml_sf2.set('reverbOn', str(json_singletrack['instrumentdata']['plugindata']['reverb']['enabled']))
		xml_sf2.set('reverbRoomSize', str(json_singletrack['instrumentdata']['plugindata']['reverb']['roomsize']))
		xml_sf2.set('reverbWidth', str(json_singletrack['instrumentdata']['plugindata']['reverb']['width']))
		xml_sf2.set('chorusDepth', str(json_singletrack['instrumentdata']['plugindata']['chorus']['depth']))
		xml_sf2.set('chorusLevel', str(json_singletrack['instrumentdata']['plugindata']['chorus']['level']))
		xml_sf2.set('chorusNum', str(json_singletrack['instrumentdata']['plugindata']['chorus']['lines']))
		xml_sf2.set('chorusOn', str(json_singletrack['instrumentdata']['plugindata']['chorus']['enabled']))
		xml_sf2.set('chorusSpeed', str(json_singletrack['instrumentdata']['plugindata']['chorus']['speed']))
	if pluginname == 'sampler':
		xml_instrumentpreplugin.set('name', "audiofileprocessor")
		xml_sampler = ET.SubElement(xml_instrumentpreplugin, "audiofileprocessor")
		if 'reversed' in json_singletrack['instrumentdata']['plugindata']:
			xml_sampler.set('reversed', str(json_singletrack['instrumentdata']['plugindata']['reverse']))
		if 'amp' in json_singletrack['instrumentdata']['plugindata']:
			xml_sampler.set('amp', str(oneto100(json_singletrack['instrumentdata']['plugindata']['amp'])))
		if 'continueacrossnotes' in json_singletrack['instrumentdata']['plugindata']:
			xml_sampler.set('stutter', str(json_singletrack['instrumentdata']['plugindata']['continueacrossnotes']))
		if 'file' in json_singletrack['instrumentdata']['plugindata']:
			xml_sampler.set('src', str(json_singletrack['instrumentdata']['plugindata']['file']))
		loopenabled = 0
		loopmode = "normal"
		if 'points' in json_singletrack['instrumentdata']['plugindata']:
			xml_sampler.set('eframe', str(json_singletrack['instrumentdata']['plugindata']['points']['end']))
			xml_sampler.set('lframe', str(json_singletrack['instrumentdata']['plugindata']['points']['loop']))
			xml_sampler.set('sframe', str(json_singletrack['instrumentdata']['plugindata']['points']['start']))
			loopenabled = json_singletrack['instrumentdata']['plugindata']['points']['loopenabled']
			loopmode = json_singletrack['instrumentdata']['plugindata']['points']['loopmode']
		if loopenabled == 0:
			xml_sampler.set('looped', '0')
		if loopenabled == 1:
			if loopmode == "normal":
				xml_sampler.set('looped', '1')
			if loopmode == "pingpong":
				xml_sampler.set('looped', '2')
		interpolation = "none"
		if 'interpolation' in json_singletrack['instrumentdata']['plugindata']:
			interpolation = json_singletrack['instrumentdata']['plugindata']['interpolation']
		if interpolation == "none":
			xml_sampler.set('interp', '0')
		if interpolation == "linear":
			xml_sampler.set('interp', '1')
		if interpolation == "sinc":
			xml_sampler.set('interp', '2')
	else:
		xml_instrumentpreplugin.set('name', "audiofileprocessor")


def asdflfo(jsondata, xmlobj, type, xmltype):
	if 'mod.' + type in jsondata:
		xml_elmod = ET.SubElement(xmlobj, 'el' + xmltype)
		json_elmod = jsondata['mod.' + type]
		xml_elmod.set('amt', str(json_elmod['envelope']['amount']))
		xml_elmod.set('pdel', str(json_elmod['envelope']['predelay']))
		xml_elmod.set('att', str(json_elmod['envelope']['attack']))
		xml_elmod.set('hold', str(json_elmod['envelope']['hold']))
		xml_elmod.set('dec', str(json_elmod['envelope']['decay']))
		xml_elmod.set('sustain', str(json_elmod['envelope']['sustain']))
		xml_elmod.set('rel', str(json_elmod['envelope']['release']))
		xml_elmod.set('lpdel', str(json_elmod['lfo']['predelay']))
		xml_elmod.set('latt', str(json_elmod['lfo']['attack']))
		xml_elmod.set('x100', '0')
		lfospeed = float(json_elmod['lfo']['speed']) / 20000
		if lfospeed > 1:
			xml_elmod.set('x100', '1')
			lfospeed = lfospeed / 100
		xml_elmod.set('lspd', str(lfospeed))
		xml_elmod.set('lamt', str(json_elmod['lfo']['amount']))

def lmms_encode_inst_track(xmltag, json_singletrack):
	xmltag.set('solo', "0")
	xmltag.set('name', "untitled")
	xmltag.set('type', "0")
	xmltag.set('muted', "0")
	if 'muted' in json_singletrack:
		xmltag.set('muted', str(json_singletrack['muted']))
	if 'name' in json_singletrack:
		xmltag.set('name', json_singletrack['name'])
	#instrumenttrack
	json_instrumentdata = json_singletrack['instrumentdata']
	xml_instrumenttrack = ET.SubElement(xmltag, "instrumenttrack")
	xml_instrumenttrack.set('usemasterpitch', "1")
	if 'usemasterpitch'in json_instrumentdata:
		xml_instrumenttrack.set('usemasterpitch', str(json_instrumentdata['usemasterpitch']))
	xml_instrumenttrack.set('pitch', "0")
	if 'pitch' in json_instrumentdata:
		xml_instrumenttrack.set('pitch', str(json_instrumentdata['pitch']))
	xml_instrumenttrack.set('basenote', "57")
	basenote = 60
	if 'basenote' in json_instrumentdata:
		basenote = json_instrumentdata['basenote']
	if json_instrumentdata['plugin'] != 'sampler':
		basenote += -3
	xml_instrumenttrack.set('basenote', str(basenote))
	if 'fxrack_channel' in json_singletrack:
		xml_instrumenttrack.set('fxch', str(json_singletrack['fxrack_channel']))
	else:
		xml_instrumenttrack.set('fxch', '0')
	xml_instrumenttrack.set('pan', "0")
	xml_instrumenttrack.set('pitchrange', "12")
	xml_instrumenttrack.set('vol', "100")
	if 'pan' in json_singletrack:
		xml_instrumenttrack.set('pan', str(oneto100(json_singletrack['pan'])))
	if 'vol' in json_singletrack:
		xml_instrumenttrack.set('vol', str(oneto100(json_singletrack['vol'])))

	xml_eldata = ET.SubElement(xml_instrumenttrack, "eldata")
	if 'filter' in json_instrumentdata:
		json_filter = json_instrumentdata['filter']
		xml_eldata.set('fcut', str(json_filter['cutoff']))
		xml_eldata.set('fwet', str(json_filter['wet']))
		xml_eldata.set('ftype', str(json_filter['type']))
		xml_eldata.set('fres', str(json_filter['reso']))

	asdflfo(json_instrumentdata, xml_eldata, 'volume', 'vol')
	asdflfo(json_instrumentdata, xml_eldata, 'cutoff', 'cut')
	asdflfo(json_instrumentdata, xml_eldata, 'reso', 'res')

	if 'arpeggiator' in json_instrumentdata:
		xml_arpeggiator = ET.SubElement(xml_instrumenttrack, "arpeggiator")
		json_arpeggiator = json_instrumentdata['arpeggiator']
		xml_arpeggiator.set('arpgate', str(json_arpeggiator['gate']))
		xml_arpeggiator.set('arprange', str(json_arpeggiator['arprange']))
		xml_arpeggiator.set('arp-enabled', str(json_arpeggiator['enabled']))
		xml_arpeggiator.set('arpmode', str(json_arpeggiator['mode']))
		xml_arpeggiator.set('arpdir', str(json_arpeggiator['direction']))
		xml_arpeggiator.set('arpskip', str(json_arpeggiator['skiprate']))
		xml_arpeggiator.set('arptime', str(json_arpeggiator['time']))
		xml_arpeggiator.set('arpmiss', str(json_arpeggiator['missrate']))
		xml_arpeggiator.set('arpcycle', str(json_arpeggiator['cyclenotes']))
		xml_arpeggiator.set('arp', str(json_arpeggiator['chord']))

	if 'chordcreator' in json_instrumentdata:
		xml_chordcreator = ET.SubElement(xml_instrumenttrack, "chordcreator")
		json_chordcreator = json_instrumentdata['chordcreator']
		xml_chordcreator.set('chord-enabled', str(json_chordcreator['enabled']))
		xml_chordcreator.set('chordrange', str(json_chordcreator['chordrange']))
		xml_chordcreator.set('chord', str(json_chordcreator['chord']))

	lmms_encode_plugin(xml_instrumenttrack, json_singletrack)
	print('Instrument Track Name: ' + json_singletrack['name'])

	#placements
	json_placementlist = json_singletrack['placements']
	tracksnum = 0
	printcountplace = 1
	while tracksnum <= len(json_placementlist)-1:
		global patternscount_forprinting
		patternscount_forprinting += 1
		print('\tPlacement ' + str(printcountplace) + ': ')
		printcountplace += 1
		json_placement = json_placementlist[tracksnum-1]
		json_notelist = json_placement['notelist']
		xml_pattern = ET.SubElement(xmltag, "pattern")
		xml_pattern.set('pos', str(int(json_placement['position'] * 48)))
		xml_pattern.set('muted', "0")
		xml_pattern.set('steps', "16")
		xml_pattern.set('name', "")
		xml_pattern.set('type', "1")
		lmms_encode_notelist(xml_pattern, json_notelist)
		tracksnum += 1


def lmms_encode_audio_track(xmltag, json_singletrack):
	xmltag.set('solo', "0")
	xmltag.set('name', "untitled")
	xmltag.set('type', "2")
	xmltag.set('muted', "0")
	tracksnum = 0
	xml_sampletrack = ET.SubElement(xmltag, "sampletrack")
	xml_sampletrack.set('pan', "0")
	xml_sampletrack.set('vol', "100")
	if json_singletrack['pan'] is not None:
		xml_sampletrack.set('pan', str(oneto100(json_singletrack['pan'])))
	if json_singletrack['vol'] is not None:
		xml_sampletrack.set('vol', str(oneto100(json_singletrack['vol'])))
	xmltag.set('name', json_singletrack['name'])
	xmltag.set('muted', str(json_singletrack['muted']))
	print('Audio Track Name: ' + json_singletrack['name'])

	#placements
	printcountplace = 0
	print('\tPlacements:', end=' ')
	json_placementlist = json_singletrack['placements']
	while tracksnum <= len(json_placementlist)-1:
		printcountplace += 1
		print(str(printcountplace), end=' ')
		json_placement = json_placementlist[tracksnum-1]
		xml_pattern = ET.SubElement(xmltag, "sampletco")
		xml_pattern.set('pos', str(int(round(json_placement['position'] * 48))))
		xml_pattern.set('len', str(int(round((json_placement['duration']*bpm)*0.8))))
		xml_pattern.set('src', str(json_placement['file']))
		tracksnum += 1
	print('')

def lmms_encode_tracks(xmltag, json_tracks):
	for json_singletrack in json_tracks:
		xml_track = ET.SubElement(xmltag, "track")
		if json_singletrack['type'] == "instrument":
			lmms_encode_inst_track(xml_track, json_singletrack)
		if json_singletrack['type'] == "audio":
			lmms_encode_audio_track(xml_track, json_singletrack)

def lmms_encode_fxrack(xmltag, json_fxrack):
	for json_fxchannel in json_fxrack:
		xml_fxchannel = ET.SubElement(xmltag, "fxchannel")
		xml_fxchannel.set('soloed', "0")
		xml_fxchannel.set('num', str(json_fxchannel['num']))
		num = json_fxchannel['num']

		if 'name' in json_fxchannel:
			name = json_fxchannel['name']
		else:
			name = 'FX ' + str(num)

		if 'vol' in json_fxchannel:
			volume = json_fxchannel['vol']
		else:
			volume = 1

		if 'muted' in json_fxchannel:
			muted = json_fxchannel['muted']
		else:
			muted = 0

		xml_fxchannel.set('name', name)
		xml_fxchannel.set('volume', str(volume))
		xml_fxchannel.set('muted', str(muted))
		if 'sends' in json_fxchannel:
			json_sends = json_fxchannel['sends']
			for json_send in json_sends:
				xml_send = ET.SubElement(xml_fxchannel, "send")
				xml_send.set('channel', json_send['channel'])
				xml_send.set('amount', json_send['amount'])
		else:
			xml_send = ET.SubElement(xml_fxchannel, "send")
			xml_send.set('channel', '0')
			xml_send.set('amount', '1')

with open(args.cvpj + '.cvpj', 'r') as projfile:
		json_proj = json.loads(projfile.read())

patternscount_forprinting = 0

_func_song.removewarping(json_proj)

json_tracks = json_proj['tracks']
xml_proj = ET.Element("lmms-project")
xml_proj.set('type', "song")
xml_head = ET.SubElement(xml_proj, "head")
xml_head.set('masterpitch', "0")
xml_head.set('mastervol', "100")
xml_head.set('timesig_numerator', "4")
xml_head.set('timesig_denominator', "4")
xml_head.set('bpm', "140")
bpm = 140
if json_proj['tracks'] is not None:
	xml_head.set('mastervol', str(oneto100(json_proj['mastervol'])))
if json_proj['tracks'] is not None:
	xml_head.set('timesig_numerator', str(json_proj['timesig_numerator']))
if json_proj['tracks'] is not None:
	xml_head.set('timesig_denominator', str(json_proj['timesig_denominator']))
if json_proj['tracks'] is not None:
	xml_head.set('bpm', str(json_proj['bpm']))
	bpm = json_proj['bpm']

xml_song = ET.SubElement(xml_proj, "song")
xml_trackcontainer = ET.SubElement(xml_song, "trackcontainer")

if 'fxrack' in json_proj:
	xml_fxmixer = ET.SubElement(xml_song, "fxmixer")
	json_fxrack = json_proj['fxrack']
	lmms_encode_fxrack(xml_fxmixer, json_fxrack)

lmms_encode_tracks(xml_trackcontainer, json_tracks)

print("Number of Patterns: " + str(patternscount_forprinting))

if 'loop' in json_proj:
	xml_timeline = ET.SubElement(xml_song, "timeline")
	xml_timeline.set('lpstate', str(json_proj['loop']['enabled']))
	xml_timeline.set('lp0pos', str(round(json_proj['loop']['start']*192)))
	xml_timeline.set('lp1pos', str(round(json_proj['loop']['end']*192)))

json_tracks = json_proj['tracks']

outfile = ET.ElementTree(xml_proj)

ET.indent(outfile)
outfile.write(args.mpp, encoding='unicode')
