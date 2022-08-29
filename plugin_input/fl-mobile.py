import plugin_input
from io import BytesIO
from functions import riff
import json
import struct

def parse_evn2_notelist(evn2bytes):
    notelistdata = BytesIO()
    notelistdata.write(evn2bytes)
    fileobject.seek(0,2)
    notelistdata_filesize = notelistdata.tell()
    notelistdata.seek(0)
    something = int.from_bytes(notelistdata.read(2), "little")
    notelist = []
    while notelistdata.tell() < notelistdata_filesize:
        notejson = {}
        notejson['position'] = int.from_bytes(notelistdata.read(4), "little")/128
        notejson['duration'] = struct.unpack('d', notelistdata.read(8))[0]
        notejson['key'] = int.from_bytes(notelistdata.read(1), "little") - 60
        notelistdata.read(1)
        notejson['vol'] = int.from_bytes(notelistdata.read(1), "little")/255
        notejson['pan'] = 0.0
        notelistdata.read(4)
        notelist.append(notejson)
    #for note in notelist:
    #   print(str(note))
    return notelist

def parse_evnt_notelist(evn2bytes):
    notelistdata = BytesIO()
    notelistdata.write(evn2bytes)
    fileobject.seek(0,2)
    notelistdata_filesize = notelistdata.tell()
    notelistdata.seek(0)
    notelist = []
    while notelistdata.tell() < notelistdata_filesize:
        notejson = {}
        notejson['position'] = int.from_bytes(notelistdata.read(4), "little")/128
        notejson['duration'] = struct.unpack('d', notelistdata.read(8))[0]
        notejson['key'] = int.from_bytes(notelistdata.read(1), "little") - 60
        notelistdata.read(1)
        notejson['vol'] = int.from_bytes(notelistdata.read(1), "little")/255
        notejson['pan'] = 0.0
        notelistdata.read(3)
        notelist.append(notejson)
    #for note in notelist:
    #   print(str(note))
    return notelist

class input_flm(plugin_input.base):
    def __init__(self):
        pass

    def getname(self):
        return 'FL Studio Mobile'

    def detect(self, input_file):
        bytestream = open(input_file, 'rb')
        bytestream.seek(0)
        bytesdata = bytestream.read(4)
        if bytesdata == b'10LF':
            return True
        else:
            return False
        bytestream.seek(0)

    def parse(self, input_file):
        global fileobject
        fileobject = open(input_file, 'rb')
        headername = fileobject.read(4)
        riffobjects = riff.readriffdata(fileobject, 4)
        tracklist = []
        flmtracks = []
        chnlcount = 0
        rackcount = 0
        for riffobject in riffobjects:
            if riffobject[0] == b'HEAD':
                headerdata = BytesIO()
                headerdata.write(riffobject[1])
                headerdata.seek(8)
                songname = headerdata.read(256).split(b'\x00')[0].decode("utf-8")
                bpm = struct.unpack('d', headerdata.read(8))[0]
        
            if riffobject[0] == b'RACK':
                rackjson = {}
                rackdata = riff.readriffdata(riffobject[1],8)
                for rackobj in rackdata:
                    if rackobj[0] == b'RPRM':
                        rackjson['vol'] = struct.unpack('f', rackobj[1][0:4])[0]
                        rackjson['pan'] = (struct.unpack('f', rackobj[1][4:8])[0]*2)-1
                flmtracks.append(rackjson)
                rackcount += 1
        
            if riffobject[0] == b'CHNL':
                chnldata = riff.readriffdata(riffobject[1],8)
                placements = []
                fxchannel_json = {}
                for chnlobj in chnldata:
                    if chnlobj[0] == b'CHHD':
                        riffobjects_chhd = chnlobj[1]
                        TrackName = riffobjects_chhd[0:256].split(b'\x00' * 1)[0].decode("utf-8")
                        flmtracks[chnlcount]['name'] = TrackName
                        flmtracks[chnlcount]['muted'] = 0
                        instrumentdata_json = {}
                        instrumentdata_json['plugin'] = "none"
                        flmtracks[chnlcount]['instrumentdata'] = instrumentdata_json
                        plugindata_json = {}
                        flmtracks[chnlcount]['plugindata'] = plugindata_json
                        
                    if chnlobj[0] == b'TRKH':
                        trkhdata = riff.readriffdata(chnlobj[1],0)
                        for trkhobj in trkhdata:
                            #print(str(trkhobj[0])+ " " + str(len(trkhobj[1])))
                            if trkhobj[0] == b'DESc':
                                TrackType = trkhobj[1][0]
                            if trkhobj[0] == b'CLIP':
                                clipobject = riff.bytearray2BytesIO(trkhobj[1])
                                clipobject.seek(0)
                                notelist_position = int.from_bytes(clipobject.read(4), "little")/128
                                riff_clip_inside = riff.readriffdata(clipobject,8)
                                placement_json = {}
                                for riff_clip_inside_part in riff_clip_inside:
                                    if TrackType == 0:
                                        if riff_clip_inside_part[0] == b'CLHd':
                                            if riff_clip_inside_part[1][0:8] != 0 and riff_clip_inside_part[1][8:16] != 0:
                                                placement_json['noteloop'] = {}
                                                placement_json['noteloop']['duration'] = struct.unpack('d', riff_clip_inside_part[1][0:8])[0]
                                                placement_json['noteloop']['endpoint'] = struct.unpack('d', riff_clip_inside_part[1][8:16])[0]
                                                placement_json['noteloop']['startpoint'] = struct.unpack('d', riff_clip_inside_part[1][16:24])[0]
                                        if riff_clip_inside_part[0] == b'EVN2':
                                            placement_json['position'] = notelist_position
                                            placement_json['notelist'] = parse_evn2_notelist(riff_clip_inside_part[1])
                                        if riff_clip_inside_part[0] == b'EVNT':
                                            placement_json['position'] = notelist_position
                                            placement_json['notelist'] = parse_evnt_notelist(riff_clip_inside_part[1])
                                if placement_json != {}:
                                    placements.append(placement_json)
                print('Input-FLMobile | Track Name: ' + TrackName, end =" | Type: ")
                print(TrackType)
                if TrackType == 0:
                    flmtracks[chnlcount]['type'] = "instrument"
                if TrackType == 2:
                    flmtracks[chnlcount]['type'] = "audio"
                flmtracks[chnlcount]['placements'] = placements
                chnlcount += 1
        
        fxrack = []
        fxcount = 0
        for flmtrack in flmtracks:
            fx_json = {}
            fx_json['vol'] = flmtrack['vol']
            fx_json['name'] = flmtrack['name']
            fx_json['num'] = fxcount
            flmtrack['fxrack_channel'] = fxcount
            if 'type' in flmtrack:
                if flmtrack['type'] == "instrument":
                    tracklist.append(flmtrack)
                if flmtrack['type'] == "audio":
                    tracklist.append(flmtrack)
            fxrack.append(fx_json)
            fxcount += 1
        json_root = {}
        json_root['mastervol'] = 1.0
        json_root['timesig_numerator'] = 4
        json_root['timesig_denominator'] = 4
        json_root['bpm'] = bpm
        json_root['title'] = songname
        json_root['tracks'] = tracklist
        json_root['fxrack'] = fxrack
        json_root['convprojtype'] = 'single'
        
        return json.dumps(json_root, indent=2)
