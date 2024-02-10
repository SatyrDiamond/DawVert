import json
from objects import dv_dataset
from functions import colors

onlineseq_settings_str = open('settings.php', 'r') # https://onlinesequencer.net/ajax/settings.php

onlineseq_settings = onlineseq_settings_str.read().split('var settings = ', 1)[1][:-1]

onlineseq_settings_dict = json.loads(onlineseq_settings)

os_instruments = onlineseq_settings_dict['instruments']
os_instrumentColors = onlineseq_settings_dict['instrumentColors']
os_instrumentCategories = onlineseq_settings_dict['instrumentCategories']
os_midiInstrumentMap = onlineseq_settings_dict['midiInstrumentMap']

os_dataset = dv_dataset.dataset('./data_dset/onlineseq.dset')

os_dataset.category_add('inst')

for instnum in range(len(os_instruments)):
    strinstnum = str(instnum)

    vis_instname = os_instruments[instnum]
    vis_color = colors.rgb_int_to_rgb_float(os_instrumentColors[instnum])

    os_dataset.object_add('inst', strinstnum)
    os_dataset.object_visual_set('inst', strinstnum, {'name':vis_instname, 'color':vis_color})
    os_dataset.midito_add('inst', strinstnum, 0, os_midiInstrumentMap[instnum]-1, False)

for groupname in os_instrumentCategories:
    for instnum in os_instrumentCategories[groupname]:
        os_dataset.object_var_set('group', 'inst', str(instnum), groupname)

with open('./data_dset/onlineseq.dset', "w") as fileout:
    json.dump(os_dataset.dataset, fileout, indent=4, sort_keys=True)






