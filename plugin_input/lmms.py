import plugin_input
import xml.etree.ElementTree as ET
import json


def hundredto1(input):
    return float(input) * 0.01

def lmms_getvalue(defualt, jsonvar, xmltag, xmlname, json_name):
    jsonvar[json_name] = defualt
    if xmltag.get(xmlname) != None:
        jsonvar[json_name] = float(xmltag.get(xmlname))
    if xmltag.findall(xmlname):
        realvalue = xmltag.findall(xmlname)[0]
        jsonvar[json_name] = realvalue.get('value')

def lmms_decode_pattern(notesxml):
    notelist = []
    print('Notes:', end=' ')
    printcountpat = 0
    for notexml in notesxml:
        notejson = {}
        notejson['key'] = int(notexml.get('key')) - 60
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
        print('Input-LMMS | ┗━━━━ Placement ' + str(printcountplace+1) + ': ', end='')
        printcountplace += 1
        placementjson = {}
        placementjson["position"] = float(patternxml.get('pos')) / 48
        notesxml = patternxml.findall('note')
        jsonnotelist = lmms_decode_pattern(notesxml)
        placementjson["notelist"] = jsonnotelist
        placementjson["duration"] = note_list_getduration(jsonnotelist)
        nlplacements.append(placementjson)
    return nlplacements

def note_list_getduration(notelistjsontable):
    notelistdurationfinal = 0
    for x in notelistjsontable:
        notelistduration = x['position'] + x['duration']
        if notelistduration > notelistdurationfinal:
            notelistdurationfinal = notelistduration
    return notelistdurationfinal

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
    speedx100 = float(xmlobj.get('x100')) * 100
    trackjson['mod.' + type]['lfo'] = {}
    trackjson['mod.' + type]['lfo']['predelay'] = float(xmlobj.get('lpdel'))
    trackjson['mod.' + type]['lfo']['attack'] = float(xmlobj.get('latt'))
    trackjson['mod.' + type]['lfo']['speed'] = float((float(xmlobj.get('lspd')) * 20000) * speedx100)
    trackjson['mod.' + type]['lfo']['amount'] = float(xmlobj.get('lamt'))

def lmms_decodeplugin(trackxml_insttr, jsonplugindata, instrumentdata_json):
    instrumentdata_json['plugin'] = "none"
    trackxml_instrument = trackxml_insttr.findall('instrument')[0]
    pluginname = trackxml_instrument.get('name')
    trackxml_plugindata = trackxml_instrument.findall(pluginname)[0]
    if pluginname == "sf2player":
        instrumentdata_json['plugin'] = "soundfont2"
        jsonplugindata['bank'] = int(trackxml_plugindata.get('bank'))
        jsonplugindata['patch'] = int(trackxml_plugindata.get('patch'))
        jsonplugindata['file'] = trackxml_plugindata.get('src')
        jsonplugindata['gain'] = float(trackxml_plugindata.get('gain'))
        jsonplugindata['reverb'] = {}
        jsonplugindata['chorus'] = {}
        jsonplugindata['chorus']['depth'] = float(trackxml_plugindata.get('chorusDepth'))
        jsonplugindata['chorus']['level'] = float(trackxml_plugindata.get('chorusLevel'))
        jsonplugindata['chorus']['lines'] = int(trackxml_plugindata.get('chorusNum'))
        jsonplugindata['chorus']['enabled'] = float(trackxml_plugindata.get('chorusOn'))
        jsonplugindata['chorus']['speed'] = float(trackxml_plugindata.get('chorusSpeed'))
        jsonplugindata['reverb']['damping'] = float(trackxml_plugindata.get('reverbDamping'))
        jsonplugindata['reverb']['level'] = float(trackxml_plugindata.get('reverbLevel'))
        jsonplugindata['reverb']['enabled'] = float(trackxml_plugindata.get('reverbOn'))
        jsonplugindata['reverb']['roomsize'] = float(trackxml_plugindata.get('reverbRoomSize'))
        jsonplugindata['reverb']['width'] = float(trackxml_plugindata.get('reverbWidth'))

    if pluginname == "audiofileprocessor":
        instrumentdata_json['plugin'] = "sampler"
        jsonplugindata['reverse'] = int(trackxml_plugindata.get('reversed'))
        jsonplugindata['amp'] = hundredto1(float(trackxml_plugindata.get('amp')))
        jsonplugindata['continueacrossnotes'] = int(trackxml_plugindata.get('stutter'))
        jsonplugindata['file'] = trackxml_plugindata.get('src')
        jsonplugindata['points'] = {}
        jsonplugindata['points']['end'] = float(trackxml_plugindata.get('eframe'))
        jsonplugindata['points']['loop'] = float(trackxml_plugindata.get('lframe'))
        jsonplugindata['points']['start'] = float(trackxml_plugindata.get('sframe'))
        looped = int(trackxml_plugindata.get('looped'))
        if looped == 0:
            jsonplugindata['points']['loopenabled'] = 0
        if looped == 1:
            jsonplugindata['points']['loopenabled'] = 1
            jsonplugindata['points']['loopmode'] = "normal"
        if looped == 2:
            jsonplugindata['points']['loopenabled'] = 1
            jsonplugindata['points']['loopmode'] = "pingpong"
        interpolation = int(trackxml_plugindata.get('interp'))
        if interpolation == 0:
            jsonplugindata['interpolation'] = "none"
        if interpolation == 1:
            jsonplugindata['interpolation'] = "linear"
        if interpolation == 2:
            jsonplugindata['interpolation'] = "sinc"


def lmms_decode_inst_track(trackxml):
    trackjson = {}
    trackjson['type'] = "instrument"
    instrumentdata_json = {}
    plugindata_json = {}
    trackjson['instrumentdata'] = instrumentdata_json
    trackjson['placements'] = {}
    trackjson['name'] = trackxml.get('name')
    print('Input-LMMS | Instrument Track Name: ' + trackjson['name'])
    trackjson['muted'] = int(trackxml.get('muted'))
    trackjson_instdata = trackjson['instrumentdata']
    trackjson_instdata['plugindata'] = plugindata_json
    trackxml_insttr = trackxml.findall('instrumenttrack')[0]
    trackjson['fxrack_channel'] = int(trackxml_insttr.get('fxch'))
    trackxml_insttr_eldata = trackxml_insttr.findall('eldata')[0]
    if trackxml_insttr_eldata.findall('elvol'):
        realvalue = trackxml_insttr_eldata.findall('elvol')[0]
        asdflfo(trackjson_instdata, realvalue, 'volume')
    if trackxml_insttr_eldata.findall('elcut'):
        realvalue = trackxml_insttr_eldata.findall('elcut')[0]
        asdflfo(trackjson_instdata, realvalue, 'cutoff')
    if trackxml_insttr_eldata.findall('elres'):
        realvalue = trackxml_insttr_eldata.findall('elres')[0]
        asdflfo(trackjson_instdata, realvalue, 'reso')
    trackjson_instdata['filter'] = {}
    trackjson_instdata['filter']['cutoff'] = float(trackxml_insttr_eldata.get('fcut'))
    trackjson_instdata['filter']['wet'] = float(trackxml_insttr_eldata.get('fwet'))
    trackjson_instdata['filter']['type'] = float(trackxml_insttr_eldata.get('ftype'))
    trackjson_instdata['filter']['reso'] = float(trackxml_insttr_eldata.get('fres'))
    trackjson['pan'] = hundredto1(trackxml_insttr.get('pan'))
    trackjson['vol'] = hundredto1(trackxml_insttr.get('vol'))
    trackjson_instdata['usemasterpitch'] = int(trackxml_insttr.get('usemasterpitch'))
    
    trackjson_instdata['pitch'] = 0
    if trackxml_insttr.get('pitch') != None:
        trackjson_instdata['pitch'] = float(trackxml_insttr.get('pitch'))
    basenote = int(trackxml_insttr.get('basenote'))
    trackjson_instdata['basenote'] = int(basenote)
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
    trackjson_plugindata = trackjson_instdata['plugindata']
    lmms_decodeplugin(trackxml_insttr, trackjson_plugindata, instrumentdata_json)
    return trackjson

def lmms_decode_audioplacements(trackxml):
    audioplacements = []
    patternsxml = trackxml.findall('sampletco')
    printcountplace = 0
    print('Input-LMMS | ┗━━━━ Placements:', end=' ')
    for patternxml in patternsxml:
        printcountplace += 1
        print(str(printcountplace), end=' ')
        audioplacementsjson = {}
        audioplacementsjson['position'] = float(patternxml.get('pos')) / 48
        audioplacementsjson['duration'] = (int(patternxml.get('len'))/bpm)*(1.25)
        audioplacementsjson['file'] = patternxml.get('src')
        audioplacements.append(audioplacementsjson)
    print('')
    return audioplacements

def lmms_decode_audio_track(trackxml):
    trackjson = {}
    trackjson['type'] = "audio"
    trackjson['name'] = trackxml.get('name')
    print('Input-LMMS | Audio Track Name: ' + trackjson['name'])
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

def lmms_decode_fx(fxchannelxml):
    fxchain = []
    fxchainxml = fxchannelxml.get('fxchain')
    
    
    output = {}
    return output

def lmms_decode_fxmixer(fxxml):
    fxlist = []
    for fxchannelxml in fxxml:
        fxchanneljson = {}
        fxchanneljson['name'] = fxchannelxml.get('name')
        fxchanneljson['muted'] = int(fxchannelxml.get('muted'))
        fxchanneljson['num'] = int(fxchannelxml.get('num'))
        fxchanneljson['vol'] = float(fxchannelxml.get('volume'))
        fxchanneljson['fxchain'] = lmms_decode_fx(fxchannelxml)
        sendlist = []
        sendsxml = fxchannelxml.findall('send')
        for sendxml in sendsxml:
            sendentryjson = {}
            sendentryjson['channel'] = sendxml.get('channel')
            sendentryjson['amount'] = sendxml.get('amount')
            sendlist.append(sendentryjson)
        fxchanneljson['sends'] = sendlist
        fxlist.append(fxchanneljson)
    return fxlist


class input_lmms(plugin_input.base):
    def __init__(self):
        pass

    def getname(self):
        return 'LMMS'

    def detect(self, input_file):
        output = False
        try:
            tree = ET.parse(input_file)
            root = tree.getroot()
            if root.tag == "lmms-project":
                output = True
        except ET.ParseError:
            output = False
        return output

    def parse(self, input_file):
        tree = ET.parse(input_file).getroot()
        headxml = tree.findall('head')[0]
        tracksxml = tree.findall('song/trackcontainer/track')
        fxxml = tree.findall('song/fxmixer/fxchannel')
        timelinexml = tree.find('song/timeline')
        
        bpm = 140
        if headxml.get('bpm') != None:
            bpm = int(headxml.get('bpm'))
        
        loop = {}
        loop['enabled'] = int(timelinexml.get('lpstate'))
        loop['start'] = int(timelinexml.get('lp0pos'))/192
        loop['end'] = int(timelinexml.get('lp1pos'))/192
        
        json_root = {}
        json_root['mastervol'] = float(hundredto1(headxml.get('mastervol')))
        json_root['masterpitch'] = float(hundredto1(headxml.get('masterpitch')))
        lmms_getvalue(4, json_root, headxml, 'timesig_numerator', 'timesig_numerator')
        lmms_getvalue(4, json_root, headxml, 'timesig_denominator', 'timesig_denominator')
        lmms_getvalue(140, json_root, headxml, 'bpm', 'bpm')
        json_root['loop'] = loop
        json_root['tracks'] = lmms_decode_tracks(tracksxml)
        json_root['fxrack'] = lmms_decode_fxmixer(fxxml)
        json_root['convprojtype'] = 'single'
        return json.dumps(json_root, indent=2)


