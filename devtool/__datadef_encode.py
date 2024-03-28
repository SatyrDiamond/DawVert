import argparse
import json
import sys
sys.path.append('../')

from objects import dv_datadef

aparser = argparse.ArgumentParser()
aparser.add_argument("-d", default=None)
aparser.add_argument("-j", default=None)
aparser.add_argument("-s", default='main')

argsd = vars(aparser.parse_args())

datadef = dv_datadef.datadef(argsd['d'])

#if argsd['d'] != None:
#    df_file = argsd['d']
#    datadef.load_file(df_file)
    
in_data = {}
if argsd['j'] != None:
    dat_file = argsd['j']
    f = open(argsd['j'], "r")
    in_data = json.load(f)

if argsd['s'] != None: 
    structname = argsd['s']

#print(   in_data  )

datadef.create(structname, in_data)

print(   datadef.bytestream.getvalue()   )

if datadef.errored:
    print('[error] '+datadef.errormeg)
else:
    with open('out.raw', "w") as fileout:
        json.dump(datadef.output, fileout, indent=4, sort_keys=True)
