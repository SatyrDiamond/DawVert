def add_to_seperated_object(seperated_object_table, objectdata, number):
    numberfound = 0
    if seperated_object_table == []:
        seperated_object_table.append([number,[objectdata]])
    else:
        for numberobj in seperated_object_table:
            if numberobj[0] == number:
                numberfound = 1
                numberobj[1].append(objectdata)
        if numberfound == 0:
            seperated_object_table.append([number,[objectdata]])

def add_to_id_json(seperated_object_table, jsonname, jsonvar, number):
    numberfound = 0
    jsondata = {jsonname: jsonvar}
    if seperated_object_table == []:
        seperated_object_table.append([number,jsondata])
    else:
        for numberobj in seperated_object_table:
            if numberobj[0] == number:
                numberfound = 1
                numberobj[1] = numberobj[1] | jsondata
        if numberfound == 0:
            seperated_object_table.append([number,jsondata])