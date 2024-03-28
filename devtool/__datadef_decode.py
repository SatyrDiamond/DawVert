import argparse
import json
import sys
sys.path.append('../')

from objects import dv_datadef

aparser = argparse.ArgumentParser()
aparser.add_argument("-d", default=None)
aparser.add_argument("-f", default=None)
aparser.add_argument("-s", default='main')

argsd = vars(aparser.parse_args())

datadef = dv_datadef.datadef(None)

if argsd['d'] != None:
    df_file = argsd['d']
    datadef.load_file(df_file)
    
if argsd['f'] != None:
    dat_file = argsd['f']
    databytes_str = open(dat_file, "rb")
    databytes = databytes_str.read()

if argsd['s'] != None: 
    structname = argsd['s']

datadef = dv_datadef.datadef(df_file)

datadef.parse(structname,databytes)

if datadef.errored:
    print('[error] '+datadef.errormeg)
else:
    with open('out.json', "w") as fileout:
        json.dump(datadef.output, fileout, indent=4, sort_keys=True)
