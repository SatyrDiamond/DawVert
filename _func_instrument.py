import json

def notelistTABLE_to_notelistCONVPROJ(notelistTABLE):
	print('notelist (TABLE to CONVPROJ) started', end=' ')
	notelist_table2json = []
	printnotes = 0
	for notelist_table2json_note in notelistTABLE:
		outputjson = {}
		outputjson['position'] = notelist_table2json_note[0]
		outputjson['duration'] = notelist_table2json_note[1]
		outputjson['key'] = notelist_table2json_note[2]
		outputjson['vol'] = notelist_table2json_note[3]
		outputjson['pan'] = notelist_table2json_note[4]
		notelist_table2json.append(outputjson)
		printnotes += 1
	print(str(printnotes) + ' notes')
	return notelist_table2json

def notelistCONVPROJ_to_notelistTABLE(notelistCONVPROJ):
	print('notelist (CONVPROJ to TABLE):', end=' ')
	printnotes = 0
	notelist_json2table = []
	json_notelistinput_tmp = json.dumps(notelistCONVPROJ)
	for notelist_json2table_note in json.loads(json_notelistinput_tmp):
		extravalue = notelist_json2table_note
		position = notelist_json2table_note["position"]
		duration = notelist_json2table_note["duration"]
		key = notelist_json2table_note["key"]
		vol = notelist_json2table_note["vol"]
		pan = notelist_json2table_note["pan"]
		del extravalue["position"]
		del extravalue["duration"]
		del extravalue["key"]
		del extravalue["vol"]
		del extravalue["pan"]
		notelist_json2table.append([position,duration,key,vol,pan,extravalue])
		printnotes += 1
	print(str(printnotes) + ' notes')
	return notelist_json2table

def nlplacementsTABLE_to_nlplacementsCONVPROJ(nlplacementsTABLE):
	print('nlplacements (TABLE to CONVPROJ) started')
	printnotes = 0
	nlplacements_table2json = []
	for nlplacements_table2json_notelist in nlplacementsTABLE:
		outputjson = {}
		outputjson['startat'] = nlplacements_table2json_notelist[0]
		outputjson['notelist'] = notelistTABLE_to_notelistCONVPROJ(nlplacements_table2json_notelist[1])
		nlplacements_table2json.append(outputjson)
		printnotes += 1
	print('nlplacements (TABLE to CONVPROJ): ' + str(printnotes) + ' placements')
	return nlplacements_table2json

def nlplacementsCONVPROJ_to_nlplacementsTABLE(nlplacementsCONVPROJ):
	print('')
	print('nlplacements (CONVPROJ to TABLE) started')
	printnotes = 0
	nlplacements_json2table = []
	jsonnlplacementsinput_tmp = json.dumps(nlplacementsCONVPROJ)
	for nlplacements_json2table_note in json.loads(jsonnlplacementsinput_tmp):
		extravalue = nlplacements_json2table_note
		startat = nlplacements_json2table_note["startat"]
		notelist = notelistCONVPROJ_to_notelistTABLE(nlplacements_json2table_note["notelist"])
		del extravalue["startat"]
		del extravalue["notelist"]
		nlplacements_json2table.append([startat,notelist,extravalue])
		printnotes += 1
	print('nlplacements (CONVPROJ to TABLE) ended: ' + str(printnotes) + ' placements')
	return nlplacements_json2table

def init_instrument_trackdataCONVPROJ():
	trackdata_json = {}
	trackdata_json['type'] = "instrument"
	trackdata_json['muted'] = 0
	trackdata_json['name'] = "untitled"
	trackdata_json['pan'] = 0.0
	trackdata_json['vol'] = 1.0
	instrumentdata_json = {}
	instrumentdata_json['basenote'] = 60
	instrumentdata_json['pitch'] = 0
	instrumentdata_json['usemasterpitch'] = 1
	instrumentdata_json['plugin'] = "none"
	plugindata_json = {}
	trackdata_json['instrumentdata'] = instrumentdata_json
	trackdata_json['plugindata'] = plugindata_json
	trackdata_json['placements'] = {}
	return trackdata_json
