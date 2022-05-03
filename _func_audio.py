import json

def audioplacementsTABLE_to_audioplacementsCONVPROJ(audioplacementsTABLE):
	print('audioplacements (TABLE to CONVPROJ) started')
	printplacements = 0
	audioplacements_table2json = []
	for audioplacements_table2json_placementlist in audioplacementsTABLE:
		outputjson = {}
		outputjson['position'] = audioplacements_table2json_placementlist[0]
		outputjson['duration'] = audioplacements_table2json_placementlist[1]
		outputjson['file'] = audioplacements_table2json_placementlist[2]
		audioplacements_table2json.append(outputjson)
		printplacements += 1
	print('audioplacements (TABLE to CONVPROJ): ' + str(printplacements) + ' placements')
	return audioplacements_table2json

def audioplacementsCONVPROJ_to_audioplacementsTABLE(audioplacementsCONVPROJ):
	print('audioplacements (CONVPROJ to TABLE) started')
	printplacements = 0
	audioplacements_json2table = []
	jsonaudioplacementsinput_tmp = json.dumps(audioplacementsCONVPROJ)
	for audioplacements_json2table_placement in json.loads(jsonaudioplacementsinput_tmp):
		extravalue = audioplacements_json2table_placement
		position = audioplacements_json2table_placement["position"]
		duration = audioplacements_json2table_placement["duration"]
		file = audioplacements_json2table_placement["file"]
		del extravalue["position"]
		del extravalue["duration"]
		del extravalue["file"]
		audioplacements_json2table.append([position,duration,file,extravalue])
		printplacements += 1
	print('audioplacements (CONVPROJ to TABLE) ended: ' + str(printplacements) + ' placements')
	print('')
	return audioplacements_json2table

def init_audio_trackdataCONVPROJ():
	trackdata_json = {}
	trackdata_json['type'] = "audio"
	trackdata_json['muted'] = 0
	trackdata_json['name'] = "untitled"
	trackdata_json['pan'] = 0.0
	trackdata_json['vol'] = 1.0
	trackdata_json['placements'] = {}
	return trackdata_json