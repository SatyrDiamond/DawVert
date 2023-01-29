from functions import format_flp_dec
from functions import format_flp_enc
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("input")
args = parser.parse_args()

FLP_Data = format_flp_dec.parse(args.input)

FL_Main = FLP_Data['FL_Main']
FL_Patterns = FLP_Data['FL_Patterns']
FL_Channels = FLP_Data['FL_Channels']
FL_Mixer = FLP_Data['FL_Mixer']
FL_Arrangements = FLP_Data['FL_Arrangements']
FL_TimeMarkers = FLP_Data['FL_TimeMarkers']
#FL_Tracks = FLP_Data['FL_Tracks']

#print(FL_Main)

#print('--- Patterns:')
#for FL_Pattern in FL_Patterns:
    #print(FL_Pattern, FL_Patterns[FL_Pattern])

#print('--- Channels:')
#for FL_Channel in FL_Channels:
    #print(FL_Channels[FL_Channel])
    
#print('--- Mixer:')
#for FL_FX in FL_Mixer:
    #print(FL_FX, FL_Mixer[FL_FX])

#print('--- Arrangements:')
#for FL_Arrangement in FL_Arrangements:
#    print(FL_Arrangement, FL_Arrangements[FL_Arrangement])

#print('--- Tracks:')
#for FL_Track in FL_Tracks:
#    print(FL_Track, FL_Tracks[FL_Track])

#print('--- Time Markers:')
#for FL_TimeMarker in FL_TimeMarkers:
    #print(FL_TimeMarker, FL_TimeMarkers[FL_TimeMarker])

format_flp_enc.make(FLP_Data, 'out.flp')
