# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from functions import auto
from functions import idvals
from functions import plugins
from functions import note_data
from functions import data_values
from functions import placement_data
from functions import placements
from functions import xtramath
from functions import song
from functions_tracks import auto_data
from functions_tracks import fxrack
from functions_tracks import fxslot
from functions_tracks import tracks_master
from functions_tracks import tracks_mi
import plugin_input
import json
import math

global colornum_p
global colornum_d
colornum_p = 0
colornum_d = 0

colors_pitch = [[0, 0.6, 0.63], [0.63, 0.63, 0], [0.78, 0.31, 0], [0, 0.63, 0], [0.82, 0.13, 0.82], [0.47, 0.47, 0.69], [0.54, 0.63, 0], [0.87, 0, 0.1], [0, 0.63, 0.44], [0.57, 0.12, 1]]

colors_drums = [ [0.44, 0.44, 0.44], [0.6, 0.4, 0.2], [0.29, 0.43, 0.56], [0.48, 0.31, 0.6], [0.38, 0.47, 0.22]]

filtervals = [2378.41, 3363.59, 4756.83, 5656.85, 8000, 9513.66, 11313.71, 13454.34, 16000, 19027.31, None]

rawChipWaves = {}
rawChipWaves["rounded"] = {"expression": 0.94, "samples": [0,0.2,0.4,0.5,0.6,0.7,0.8,0.85,0.9,0.95,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0.95,0.9,0.85,0.8,0.7,0.6,0.5,0.4,0.2,0,-0.2,-0.4,-0.5,-0.6,-0.7,-0.8,-0.85,-0.9,-0.95,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-0.95,-0.9,-0.85,-0.8,-0.7,-0.6,-0.5,-0.4,-0.2]}
rawChipWaves["triangle"] = {"expression": 1, "samples": [1/15,0.2,5/15,7/15,0.6,11/15,13/15,1,1,13/15,11/15,0.6,7/15,5/15,0.2,1/15,-1/15,-0.2,-5/15,-7/15,-0.6,-11/15,-13/15,-1,-1,-13/15,-11/15,-0.6,-7/15,-5/15,-0.2,-1/15]}
rawChipWaves["square"] = {"expression": 0.5, "samples": [1,-1]}
rawChipWaves["1/4 pulse"] = {"expression": 0.5, "samples": [1,-1,-1,-1]}
rawChipWaves["1/8 pulse"] = {"expression": 0.5, "samples": [1,-1,-1,-1,-1,-1,-1,-1]}
rawChipWaves["sawtooth"] = {"expression": 0.65, "samples": [1/31,3/31,5/31,7/31,9/31,11/31,13/31,15/31,17/31,19/31,21/31,23/31,25/31,27/31,29/31,1,-1,-29/31,-27/31,-25/31,-23/31,-21/31,-19/31,-17/31,-15/31,-13/31,-11/31,-9/31,-7/31,-5/31,-3/31,-1/31]}
rawChipWaves["double saw"] = {"expression": 0.5, "samples": [0,-0.2,-0.4,-0.6,-0.8,-1,1,-0.8,-0.6,-0.4,-0.2,1,0.8,0.6,0.4,0.2]}
rawChipWaves["double pulse"] = {"expression": 0.4, "samples": [1,1,1,1,1,-1,-1,-1,1,1,1,1,-1,-1,-1,-1]}
rawChipWaves["spiky"] = {"expression": 0.4, "samples": [1,-1,1,-1,1,0]}
rawChipWaves["sine"] = {"expression": 0.88, "samples": [8,9,11,12,13,14,15,15,15,15,14,14,13,11,10,9,7,6,4,3,2,1,0,0,0,0,1,1,2,4,5,6]}
rawChipWaves["flute"] = {"expression": 0.8, "samples": [3,4,6,8,10,11,13,14,15,15,14,13,11,8,5,3]}
rawChipWaves["harp"] = {"expression": 0.8, "samples": [0,3,3,3,4,5,5,6,7,8,9,11,11,13,13,15,15,14,12,11,10,9,8,7,7,5,4,3,2,1,0,0]}
rawChipWaves["sharp clarinet"] = {"expression": 0.38, "samples": [0,0,0,1,1,8,8,9,9,9,8,8,8,8,8,9,9,7,9,9,10,4,0,0,0,0,0,0,0,0,0,0]}
rawChipWaves["soft clarinet"] = {"expression": 0.45, "samples": [0,1,5,8,9,9,9,9,9,9,9,11,11,12,13,12,10,9,7,6,4,3,3,3,1,1,1,1,1,1,1,1]}
rawChipWaves["alto sax"] = {"expression": 0.3, "samples": [5,5,6,4,3,6,8,7,2,1,5,6,5,4,5,7,9,11,13,14,14,14,14,13,10,8,7,7,4,3,4,2]}
rawChipWaves["bassoon"] = {"expression": 0.35, "samples": [9,9,7,6,5,4,4,4,4,5,7,8,9,10,11,13,13,11,10,9,7,6,4,2,1,1,1,2,2,5,11,14]}
rawChipWaves["trumpet"] = {"expression": 0.22, "samples": [10,11,8,6,5,5,5,6,7,7,7,7,6,6,7,7,7,7,7,6,6,6,6,6,6,6,6,7,8,9,11,14]}
rawChipWaves["electric guitar"] = {"expression": 0.2, "samples": [11,12,12,10,6,6,8,0,2,4,8,10,9,10,1,7,11,3,6,6,8,13,14,2,0,12,8,4,13,11,10,13]}
rawChipWaves["organ"] = {"expression": 0.2, "samples": [11,10,12,11,14,7,5,5,12,10,10,9,12,6,4,5,13,12,12,10,12,5,2,2,8,6,6,5,8,3,2,1]}
rawChipWaves["pan flute"] = {"expression": 0.35, "samples": [1,4,7,6,7,9,7,7,11,12,13,15,13,11,11,12,13,10,7,5,3,6,10,7,3,3,1,0,1,0,1,0]}
rawChipWaves["glitch"] = {"expression": 0.5, "samples": [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,-1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,-1,-1,1,1,1,1,1,1,1,1,1,1,1,1,1,-1,-1,-1,1,1,1,1,1,1,1,1,1,1,1,1,-1,-1,-1,-1,1,1,1,1,1,1,1,1,1,1,1,-1,-1,-1,-1,-1,1,1,1,1,1,1,1,1,1,1,-1,-1,-1,-1,-1,-1,1,1,1,1,1,1,1,1,1,-1,-1,-1,-1,-1,-1,-1,1,1,1,1,1,1,1,1,-1,-1,-1,-1,-1,-1,-1,-1,1,1,1,1,1,1,1,1,1,-1,-1,-1,-1,-1,-1,-1,1,1,1,1,1,1,1,1,1,1,-1,-1,-1,-1,-1,-1,1,1,1,1,1,1,1,1,1,1,1,-1,-1,-1,-1,-1,1,1,1,1,1,1,1,1,1,1,1,1,-1,-1,-1,-1,1,1,1,1,1,1,1,1,1,1,1,1,1,-1,-1,-1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,-1,-1]}

rawChipWaves["brucebox isolated spiky"] = {"expression": 0.5, "samples": [1.0, -1.0, 1.0, -1.0, 1.0, -1.0]}
rawChipWaves["brucebox pokey 4bit lfsr"] = {"expression": 0.5, "samples": [1.0, -1.0, -1.0, -1.0, 1.0, 1.0, 1.0, 1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0, -1.0]}
rawChipWaves["brucebox pokey 5step bass"] = {"expression": 0.5, "samples": [1.0, -1.0, 1.0, -1.0, 1.0]}
rawChipWaves["haileybox test1"] = {"expression": 0.5, "samples": [1.0, 0.5, -1.0]}
rawChipWaves["modbox 1% pulse"] = {"expression": 0.5, "samples": [1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0]}
rawChipWaves["modbox 10% pulse"] = {"expression": 0.5, "samples": [1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0]}
rawChipWaves["modbox acoustic bass"] = {"expression": 0.5, "samples": [1.0, 0.0, 0.1, -0.1, -0.2, -0.4, -0.3, -1.0]}
rawChipWaves["modbox atari bass"] = {"expression": 0.5, "samples": [1.0, 1.0, 1.0, 1.0, 0.0, 1.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0]}
rawChipWaves["modbox atari pulse"] = {"expression": 0.5, "samples": [1.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]}
rawChipWaves["modbox brass"] = {"expression": 0.45, "samples": [-1.0, -0.95, -0.975, -0.9, -0.85, -0.8, -0.775, -0.65, -0.6, -0.5, -0.475, -0.35, -0.275, -0.2, -0.125, -0.05, 0.0, 0.075, 0.125, 0.15, 0.20, 0.21, 0.225, 0.25, 0.225, 0.21, 0.20, 0.19, 0.175, 0.125, 0.10, 0.075, 0.06, 0.05, 0.04, 0.025, 0.04, 0.05, 0.10, 0.15, 0.225, 0.325, 0.425, 0.575, 0.70, 0.85, 0.95, 1.0, 0.9, 0.675, 0.375, 0.2, 0.275, 0.4, 0.5, 0.55, 0.6, 0.625, 0.65, 0.65, 0.65, 0.65, 0.64, 0.6, 0.55, 0.5, 0.4, 0.325, 0.25, 0.15, 0.05, -0.05, -0.15, -0.275, -0.35, -0.45, -0.55, -0.65, -0.7, -0.78, -0.825, -0.9, -0.925, -0.95, -0.975]}
rawChipWaves["modbox curved sawtooth"] = {"expression": 0.5, "samples": [1.0, 1.0/2.0, 1.0/3.0, 1.0/4.0]}
rawChipWaves["modbox flatline"] = {"expression": 1.0, "samples": [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]}
rawChipWaves["modbox guitar"] = {"expression": 0.5, "samples": [-0.5, 3.5, 3.0, -0.5, -0.25, -1.0]}
rawChipWaves["modbox loud pulse"] = {"expression": 0.5, "samples": [1.0, 0.7, 0.1, 0.1, 0, 0, 0, 0, 0, 0.1, 0.2, 0.15, 0.25, 0.125, 0.215, 0.345, 4.0]}
rawChipWaves["modbox lyre"] = {"expression": 0.45, "samples": [1.0, -1.0, 4.0, 2.15, 4.13, 5.15, 0.0, -0.05, 1.0]}
rawChipWaves["modbox piccolo"] = {"expression": 0.5, "samples": [1, 4, 2, 1, -0.1, -1, -0.12]}
rawChipWaves["modbox pnryshk a (u5)"] = {"expression": 0.4, "samples": [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0]}
rawChipWaves["modbox pnryshk b (riff)"] = {"expression": 0.5, "samples": [1.0, -0.9, 0.8, -0.7, 0.6, -0.5, 0.4, -0.3, 0.2, -0.1, 0.0, -0.1, 0.2, -0.3, 0.4, -0.5, 0.6, -0.7, 0.8, -0.9, 1.0]}
rawChipWaves["modbox ramp pulse"] = {"expression": 0.5, "samples": [6.1, -2.9, 1.4, -2.9]} 
rawChipWaves["modbox sax"] = {"expression": 0.5, "samples": [1.0/15.0, 3.0/15.0, 5.0/15.0, 9.0, 0.06]}
rawChipWaves["modbox sine"] = {"expression": 0.5, "samples": [0.0, 0.05, 0.125, 0.2, 0.25, 0.3, 0.425, 0.475, 0.525, 0.625, 0.675, 0.725, 0.775, 0.8, 0.825, 0.875, 0.9, 0.925, 0.95, 0.975, 0.98, 0.99, 0.995, 1, 0.995, 0.99, 0.98, 0.975, 0.95, 0.925, 0.9, 0.875, 0.825, 0.8, 0.775, 0.725, 0.675, 0.625, 0.525, 0.475, 0.425, 0.3, 0.25, 0.2, 0.125, 0.05, 0.0, -0.05, -0.125, -0.2, -0.25, -0.3, -0.425, -0.475, -0.525, -0.625, -0.675, -0.725, -0.775, -0.8, -0.825, -0.875, -0.9, -0.925, -0.95, -0.975, -0.98, -0.99, -0.995, -1, -0.995, -0.99, -0.98, -0.975, -0.95, -0.925, -0.9, -0.875, -0.825, -0.8, -0.775, -0.725, -0.675, -0.625, -0.525, -0.475, -0.425, -0.3, -0.25, -0.2, -0.125, -0.05]}
rawChipWaves["modbox squaretooth"] = {"expression": 0.5, "samples": [0.2, 1.0, 2.6, 1.0, 0.0, -2.4]}
rawChipWaves["modbox sunsoft bass"] = {"expression": 1.0, "samples": [0.0, 0.1875, 0.3125, 0.5625, 0.5, 0.75, 0.875, 1.0, 1.0, 0.6875, 0.5, 0.625, 0.625, 0.5, 0.375, 0.5625, 0.4375, 0.5625, 0.4375, 0.4375, 0.3125, 0.1875, 0.1875, 0.375, 0.5625, 0.5625, 0.5625, 0.5625, 0.5625, 0.4375, 0.25, 0.0]}
rawChipWaves["modbox viola"] = {"expression": 0.45, "samples": [-0.9, -1.0, -0.85, -0.775, -0.7, -0.6, -0.5, -0.4, -0.325, -0.225, -0.2, -0.125, -0.1, -0.11, -0.125, -0.15, -0.175, -0.18, -0.2, -0.21, -0.22, -0.21, -0.2, -0.175, -0.15, -0.1, -0.5, 0.75, 0.11, 0.175, 0.2, 0.25, 0.26, 0.275, 0.26, 0.25, 0.225, 0.2, 0.19, 0.18, 0.19, 0.2, 0.21, 0.22, 0.23, 0.24, 0.25, 0.26, 0.275, 0.28, 0.29, 0.3, 0.29, 0.28, 0.27, 0.26, 0.25, 0.225, 0.2, 0.175, 0.15, 0.1, 0.075, 0.0, -0.01, -0.025, 0.025, 0.075, 0.2, 0.3, 0.475, 0.6, 0.75, 0.85, 0.85, 1.0, 0.99, 0.95, 0.8, 0.675, 0.475, 0.275, 0.01, -0.15, -0.3, -0.475, -0.5, -0.6, -0.71, -0.81, -0.9, -1.0, -0.9]}
rawChipWaves["nerdbox unnamed 1"] = {"expression": 0.5, "samples": [0.2 , 0.8/0.2, 0.7, -0.4, -1.0, 0.5, -0.5/0.6]}
rawChipWaves["nerdbox unnamed 2"] = {"expression": 0.5, "samples": [2.0 , 5.0/55.0 , -9.0 , 6.5/6.5 , -55.0, 18.5/-26.0]}
rawChipWaves["sandbox bassoon"] = {"expression": 0.5, "samples": [1.0, -1.0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0]}
rawChipWaves["sandbox contrabass"] = {"expression": 0.5, "samples": [4.20, 6.9, 1.337, 6.66]}
rawChipWaves["sandbox deep square"] = {"expression": 1.0, "samples": [1.0, 2.25, 1.0, -1.0, -2.25, -1.0]}
rawChipWaves["sandbox double bass"] = {"expression": 0.4, "samples": [0.0, 0.1875, 0.3125, 0.5625, 0.5, 0.75, 0.875, 1.0, -1.0, -0.6875, -0.5, -0.625, -0.625, -0.5, -0.375, -0.5625, -0.4375, -0.5625, -0.4375, -0.4375, -0.3125, -0.1875, 0.1875, 0.375, 0.5625, -0.5625, 0.5625, 0.5625, 0.5625, 0.4375, 0.25, 0.0]}
rawChipWaves["sandbox double sine"] = {"expression": 1.0, "samples": [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 1.8, 1.7, 1.6, 1.5, 1.4, 1.3, 1.2, 1.1, 1.0, 0.0, -1.0, -1.1, -1.2, -1.3, -1.4, -1.5, -1.6, -1.7, -1.8, -1.9, -1.8, -1.7, -1.6, -1.5, -1.4, -1.3, -1.2, -1.1, -1.0]}
rawChipWaves["sandbox euphonium"] = {"expression": 0.3, "samples": [0, 1, 2, 1, 2, 1, 4, 2, 5, 0, -2, 1, 5, 1, 2, 1, 2, 4, 5, 1, 5, -2, 5, 10, 1]}
rawChipWaves["sandbox narrow saw"] = {"expression": 1.2, "samples": [0.1, 0.13/-0.1 ,0.13/-0.3 ,0.13/-0.5 ,0.13/-0.7 ,0.13/-0.9 ,0.13/-0.11 ,0.13/-0.31 ,0.13/-0.51 ,0.13/-0.71 ,0.13/-0.91 ,0.13/-0.12 ,0.13/-0.32 ,0.13/-0.52 ,0.13/-0.72 ,0.13/-0.92 ,0.13/-0.13 ,0.13/0.13 ,0.13/0.92 ,0.13/0.72 ,0.13/0.52 ,0.13/0.32 ,0.13/0.12 ,0.13/0.91 ,0.13/0.71 ,0.13/0.51 ,0.13/0.31 ,0.13/0.11 ,0.13/0.9 ,0.13/0.7 ,0.13/0.5 ,0.13/0.3 ,0.13]}
rawChipWaves["sandbox nes pulse"] = {"expression": 0.4, "samples": [2.1, -2.2, 1.2, 3]}
rawChipWaves["sandbox r-sawtooth"] = {"expression": 0.2, "samples": [6.1, -2.9, 1.4, -2.9]}
rawChipWaves["sandbox recorder"] = {"expression": 0.2, "samples": [5.0, -5.1, 4.0, -4.1, 3.0, -3.1, 2.0, -2.1, 1.0, -1.1, 6.0]}
rawChipWaves["sandbox ring pulse"] = {"expression": 1.0, "samples": [1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, 1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, 1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, 1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, 1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, 1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, 1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, 1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, 1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0]}
rawChipWaves["sandbox saw bass"] = {"expression": 0.25, "samples": [1, 1, 1, 1, 0, 2, 1, 2, 3, 1, -2, 1, 4, 1, 4, 2, 1, 6, -3, 4, 2, 1, 5, 1, 4, 1, 5, 6, 7, 1, 6, 1, 4, 1, 9]}
rawChipWaves["sandbox shrill bass"] = {"expression": 0.5, "samples": [0, 1, 0, 0, 1, 0, 1, 0, 0, 0]}
rawChipWaves["sandbox shrill lute"] = {"expression": 0.94, "samples": [1.0, 1.5, 1.25, 1.2, 1.3, 1.5]}
rawChipWaves["sandbox shrill pulse"] = {"expression": 0.3, "samples": [4 -2, 0, 4, 1, 4, 6, 7, 3]}
rawChipWaves["todbox 1/3 pulse"] = {"expression": 0.5, "samples": [1.0, -1.0, -1.0]}
rawChipWaves["todbox 1/5 pulse"] = {"expression": 0.5, "samples": [1.0, -1.0, -1.0, -1.0, -1.0]}
rawChipWaves["todbox accordian"] = {"expression": 0.5, "samples": [0, 1, 1, 2, 2, 1.5, 1.5, 0.8, 0, -2, -3.25, -4, -4.5, -5.5, -6, -5.75, -5.5, -5, -5, -5, -6, -6, -6, -5, -4, -3, -2, -1, 0.75, 1, 2, 3, 4, 5, 6, 6.5, 7.5, 8, 7.75, 6, 5.25, 5, 5, 5, 5, 5, 4.25, 3.75, 3.25, 2.75, 1.25, -0.75, -2, -0.75, 1.25, 1.25, 2, 2, 2, 2, 1.5, -1, -2, -1, 1.5, 2,  2.75, 2.75, 2.75, 3, 2.75, -1, -2, -2.5, -2, -1, -2.25, -2.75, -2, -3, -1.75, 1, 2, 3.5, 4, 5.25, 6, 8, 9.75, 10, 9.5, 9, 8.5, 7.5, 6.5, 5.25, 5, 4.5, 4, 4, 4, 3.25, 2.5, 2, 1, -0.5, -2, -3.5, -4, -4, -4, -3.75, -3, -2, -1]}
rawChipWaves["todbox beta banana wave"] = {"expression": 0.8, "samples": [0.0, 0.2, 0.4, 0.5, 0.6, 0.7, 0.8, 0.85, 0.9, 0.95, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.95, 0.9, 0.85, 0.8, 0.7, 0.6, 0.5, 0.4, 0.2, 0.0]}
rawChipWaves["todbox beta test wave"] = {"expression": 0.5, "samples": [56, 0, -52, 16, 3, 3, 2, -35, 20, 147, -53, 0, 0, 5, -6]}
rawChipWaves["todbox harsh wave"] = {"expression": 0.45, "samples": [1.0, -1.0, -1.0, -1.0, 0.5, 0.5, 0.5, 0.7, 0.39, 1.3, 0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0]}
rawChipWaves["todbox slap bass"] = {"expression": 0.5, "samples": [1, 0.5, 0, 0.5, 1.25, 0.5, -0.25, 0.1, -0.1, 0.1, 1.1, 2.1, 3, 3.5, 2.9, 3.3, 2.7, 2.9, 2.3, 2, 1.9, 1.8, 1, 0.7, 0.9, 0.8, 0.4, 0.1, 0.0, 0.2, 0.4, 0.6, 0.5, 0.8]}
rawChipWaves["trapezoid"] = {"expression": 1.0, "samples": [1.0/15.0, 6.0/15.0, 10.0/15.0, 14.0/15.0, 15.0/15.0, 15.0/15.0, 15.0/15.0, 15.0/15.0, 15.0/15.0, 15.0/15.0, 15.0/15.0, 15.0/15.0, 14.0/15.0, 10.0/15.0, 6.0/15.0, 1.0/15.0, -1.0/15.0, -6.0/15.0, -10.0/15.0, -14.0/15.0, -15.0/15.0, -15.0/15.0, -15.0/15.0, -15.0/15.0, -15.0/15.0, -15.0/15.0, -15.0/15.0, -15.0/15.0, -14.0/15.0, -10.0/15.0, -6.0/15.0, -1.0/15.0,]}
rawChipWaves["wackybox buzz wave"] = {"expression": 0.6, "samples": [0, 1, 1, 2, 4, 4, 4, 4, 5, 5, 6, 6, 6, 7, 8, 8, 8, 9, 9, 9, 9, 9, 9, 8, 8, 8, 11, 15, 23, 62, 61, 60, 58, 56, 56, 54, 53, 52, 50, 49, 48, 47, 47, 45, 45, 45, 44, 44, 43, 43, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 43, 43, 53]}
rawChipWaves["wackybox guitar string"] = {"expression": 0.6, "samples": [0, 63, 63, 63, 63, 19, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 11, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 27, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 34, 63, 63, 63, 63]}
rawChipWaves["wackybox intense"] = {"expression": 0.6, "samples": [36, 25, 33, 35, 18, 51, 22, 40, 27, 37, 31, 33, 25, 29, 41, 23, 31, 31, 45, 20, 37, 23, 29, 26, 42, 29, 33, 26, 31, 27, 40, 25, 40, 26, 37, 24, 41, 32, 0, 32, 33, 29, 32, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31]}
rawChipWaves["zefbox deep pulse"] = {"expression": 0.2, "samples": [1, 2, 2, -2, -2, -3, -4, -4, -5, -5, -5, -5, 0, -1, -2]}
rawChipWaves["zefbox deep sawtal"] = {"expression": 0.7, "samples": [0.75, 0.25, 0.5, -0.5, 0.5, -0.5, -0.25, -0.75]}
rawChipWaves["zefbox deep sawtooth"] = {"expression": 0.5, "samples": [0, 2, 3, 4, 4.5, 5, 5.5, 6, 6.25, 6.5, 6.75, 7, 6.75, 6.5, 6.25, 6, 5.5, 5, 4.5, 4, 3, 2, 1]}
rawChipWaves["zefbox deep square"] = {"expression": 1.0, "samples": [1.0, 2.25, 1.0, -1.0, -2.25, -1.0]}
rawChipWaves["zefbox high pulse"] = {"expression": 0.2, "samples": [1, -2, 2, -3, 3, -4, 5, -4, 3, -3, 2, -2, 1]}
rawChipWaves["zefbox pulse"] = {"expression": 0.5, "samples": [1.0, -2.0, -2.0, -1.5, -1.5, -1.25, -1.25, -1.0, -1.0]}
rawChipWaves["zefbox saw narrow"] = {"expression": 0.65, "samples": [1, 0.5, 1, 0.5, 1, 0.5, 1, 2, 1, 2 ,1]}
rawChipWaves["zefbox saw wide"] = {"expression": 0.65, "samples": [0.0, -0.4, -0.8, -1.2, -1.6 , -2.0, 0.0, -0.4, -0.8, -1.2, -1.6]}
rawChipWaves["zefbox sawtal"] = {"expression": 0.3, "samples": [1.5, 1.0, 1.25, -0.5, 1.5, -0.5, 0.0, -1.5, 1.5, 0.0, 0.5, -1.5, 0.5, 1.25, -1.0, -1.5]}
rawChipWaves["zefbox semi-square"] = {"expression": 1.0, "samples": [1.0, 1.5, 2.0, 2.5, 2.5, 2.5, 2.0, 1.5, 1.0]}
rawChipWaves["zefbox squaretal"] = {"expression": 0.7, "samples": [1.5, 1.0, 1.5, -1.5, -1.0, -1.5]}
rawChipWaves["zefbox triple pulse"] = {"expression": 0.4, "samples": [1.0, 1.0, 1.0, 1.0, 1.0, -1.0, -1.0, 1.5, 1.0, 1.0, 1.0, 1.0, -1.0, -1.0, -1.0, 1.5]}

noteoffset = {}
noteoffset['B'] = 11
noteoffset['A♯'] = 10
noteoffset['A'] = 9
noteoffset['G♯'] = 8
noteoffset['G'] = 7
noteoffset['F♯'] = 6
noteoffset['F'] = 5
noteoffset['E'] = 4
noteoffset['D♯'] = 3
noteoffset['D'] = 2
noteoffset['C♯'] = 1
noteoffset['C'] = 0

inst_names = {
"chip": "Chip Wave",
"PWM": "Pulse Width",
"harmonics": "Harmonics",
"Picked String": "Picked String",
"spectrum": "Spectrum",
"FM": "FM",
"custom chip": "Custom Chip",
"noise": "Basic Noise",
"drumset": "Drum Set"
}

def getcolor_p():
	global colornum_p
	out_color = colors_pitch[colornum_p]
	colornum_p += 1
	if colornum_p == 10: colornum_p = 0
	return out_color

def getcolor_d():
	global colornum_d
	out_color = colors_drums[colornum_d]
	colornum_d += 1
	if colornum_d == 5: colornum_d = 0
	return out_color

def calcval(value):
	global jummbox_beatsPerBar
	global jummbox_ticksPerBeat
	return (value*(jummbox_beatsPerBar/jummbox_ticksPerBeat))/2

def addfx(cvpj_instid, fxname):
	pluginid = cvpj_instid+'_'+fxname
	plugins.add_plug(cvpj_l, pluginid, 'native-jummbox', fxname)
	plugins.add_plug_fxdata(cvpj_l, pluginid, True, 1)
	fxslot.insert(cvpj_l, ['instrument', cvpj_instid], 'audio', pluginid)
	return pluginid

def addfx_universal(cvpj_instid, fxname):
	pluginid = cvpj_instid+'_'+fxname
	plugins.add_plug(cvpj_l, pluginid, 'universal', fxname)
	fxslot.insert(cvpj_l, ['instrument', cvpj_instid], 'audio', pluginid)
	return pluginid

def addfx_simple(cvpj_instid, fxname):
	pluginid = cvpj_instid+'_'+fxname
	plugins.add_plug(cvpj_l, pluginid, 'simple', fxname)
	fxslot.insert(cvpj_l, ['instrument', cvpj_instid], 'audio', pluginid)
	return pluginid

def get_harmonics(i_harmonics):
	harmonics = [i/100 for i in i_harmonics]
	harmonics.append(harmonics[-1])
	harmonics.append(harmonics[-1])
	harmonics.append(harmonics[-1])
	return harmonics

def parse_instrument(channum, instnum, bb_instrument, bb_type, bb_color, bb_inst_effects):
	global idvals_inst_beepbox
	bb_volume = bb_instrument['volume']

	if 'preset' in bb_instrument: bb_preset = str(bb_instrument['preset'])
	else: bb_preset = None

	cvpj_instid = 'bb_ch'+str(channum)+'_inst'+str(instnum)

	instslot = {}
	cvpj_volume = (bb_volume/50)+0.5

	a_decay = 3
	a_sustain = 1

	gm_inst = None
	if bb_preset in idvals_inst_beepbox:
		gm_inst = idvals.get_idval(idvals_inst_beepbox, bb_preset, 'gm_inst')

	if gm_inst != None:
		plugins.add_plug_gm_midi(cvpj_l, cvpj_instid, 0, gm_inst)
		cvpj_instname = idvals.get_idval(idvals_inst_beepbox, bb_preset, 'name')

		tracks_mi.inst_create(cvpj_l, cvpj_instid)
		tracks_mi.inst_visual(cvpj_l, cvpj_instid, name=cvpj_instname, color=bb_color)

		tracks_mi.inst_pluginid(cvpj_l, cvpj_instid, cvpj_instid)
		tracks_mi.inst_dataval_add(cvpj_l, cvpj_instid, 'midi', 'output', {'program': gm_inst})
	else:
		bb_inst_type = bb_instrument['type']
		plugins.add_plug(cvpj_l, cvpj_instid, 'native-jummbox', bb_inst_type)

		if 'unison' in bb_instrument:
			plugins.add_plug_data(cvpj_l, cvpj_instid, 'unison', bb_instrument['unison'])

		cvpj_instname = inst_names[bb_inst_type]

		if bb_inst_type == 'chip':
			bb_inst_wave = bb_instrument['wave']
			cvpj_instname = bb_inst_wave+' ('+cvpj_instname+')'
			if bb_inst_wave in rawChipWaves:
				wavesample = rawChipWaves[bb_inst_wave]['samples']
				plugins.add_wave(cvpj_l, cvpj_instid, 'chipwave', wavesample, min(wavesample), max(wavesample))

		if bb_inst_type == 'PWM':
			pulseWidth = bb_instrument['pulseWidth']
			cvpj_instname = str(pulseWidth)+'% pulse ('+cvpj_instname+')'
			plugins.add_plug_param(cvpj_l, cvpj_instid, "pulse_width", pulseWidth/100, 'float', "Pulse Width")

		if bb_inst_type == 'harmonics':
			harmonics = get_harmonics(bb_instrument['harmonics'])
			plugins.add_harmonics(cvpj_l, cvpj_instid, 'harmonics', harmonics)

		if bb_inst_type == 'Picked String':
			harmonics = get_harmonics(bb_instrument['harmonics'])
			plugins.add_harmonics(cvpj_l, cvpj_instid, 'harmonics', harmonics)
			a_sustain = bb_instrument['stringSustain']/100

		if bb_inst_type == 'spectrum':
			plugins.add_plug_data(cvpj_l, cvpj_instid, 'spectrum', bb_instrument['spectrum'])

		if bb_inst_type == 'FM':
			plugins.add_plug_data(cvpj_l, cvpj_instid, 'algorithm', bb_instrument['algorithm'])
			plugins.add_plug_data(cvpj_l, cvpj_instid, 'feedback_type', bb_instrument['feedbackType'])
			plugins.add_plug_param(cvpj_l, cvpj_instid, "feedback_amplitude", bb_instrument['feedbackAmplitude'], 'int', "Feedback Amplitude")

			for opnum in range(4):
				opdata = bb_instrument['operators'][opnum]
				opnumtext = 'op'+str(opnum+1)+'_'
				plugins.add_plug_data(cvpj_l, cvpj_instid, opnumtext+'frequency', opdata['frequency'])
				op_waveform = data_values.get_value(opdata, 'waveform', 'sine')
				plugins.add_plug_data(cvpj_l, cvpj_instid, opnumtext+'waveform', op_waveform)
				op_pulseWidth = data_values.get_value(opdata, 'waveform', 'sine')
				plugins.add_plug_data(cvpj_l, cvpj_instid, opnumtext+'pulseWidth', 5)
				plugins.add_plug_param(cvpj_l, cvpj_instid, opnumtext+"amplitude", opdata['amplitude'], 'int', "")

		if bb_inst_type == 'custom chip':
			customChipWave = bb_instrument['customChipWave']
			customChipWave = [customChipWave[str(i)] for i in range(64)]
			plugins.add_wave(cvpj_l, cvpj_instid, 'chipwave', customChipWave, -24, 24)

		tracks_mi.inst_create(cvpj_l, cvpj_instid)
		tracks_mi.inst_visual(cvpj_l, cvpj_instid, name=cvpj_instname, color=bb_color)
		tracks_mi.inst_pluginid(cvpj_l, cvpj_instid, cvpj_instid)
		tracks_mi.inst_param_add(cvpj_l, cvpj_instid, 'vol', cvpj_volume, 'float')

		if 'eqFilterType' in bb_instrument:
			if bb_instrument['eqFilterType'] == False:
				if 'eqSubFilters0' in bb_instrument:
					pluginid = addfx_universal(cvpj_instid, 'eq-bands')
					plugins.add_plug_fxvisual(cvpj_l, pluginid, 'EQ', None)
					for eqfiltdata in bb_instrument['eqSubFilters0']:
						eqgain_pass = eqfiltdata['linearGain']
						eqgain = (eqfiltdata['linearGain']-2)*6
						eqtype = eqfiltdata['type']
						if eqtype == 'low-pass':
							plugins.add_eqband(cvpj_l, pluginid, 1, eqfiltdata['cutoffHz'], 0, 'low_pass', eqgain_pass, None)
						if eqtype == 'peak':
							plugins.add_eqband(cvpj_l, pluginid, 1, eqfiltdata['cutoffHz'], eqgain, 'peak', 1, None)
						if eqtype == 'high-pass':
							plugins.add_eqband(cvpj_l, pluginid, 1, eqfiltdata['cutoffHz'], 0, 'high_pass', eqgain_pass, None)
			else:

				filter_hz = filtervals[bb_instrument['eqSimpleCut']]
				filter_peak = bb_instrument['eqSimplePeak']
				if filter_hz != None or filter_peak != 0:
					if filter_hz == None: filter_hz = 8000
					pluginid = addfx_universal(cvpj_instid, 'eq-bands')
					plugins.add_eqband(cvpj_l, pluginid, 1, filter_hz, 0, 'low_pass', filter_peak*2, None)

		elif 'eqFilter' in bb_instrument:
			bb_eqFilter = bb_instrument['eqFilter']
			if bb_eqFilter != []:
				pluginid = addfx_universal(cvpj_instid, 'eq-bands')
				plugins.add_plug_fxvisual(cvpj_l, pluginid, 'EQ', None)
				for eqfiltdata in bb_eqFilter:
					eqgain_pass = eqfiltdata['linearGain']
					eqgain = (eqfiltdata['linearGain']-2)*6
					eqtype = eqfiltdata['type']
					if eqtype == 'low-pass':
						plugins.add_eqband(cvpj_l, pluginid, 1, eqfiltdata['cutoffHz'], 0, 'low_pass', eqgain_pass, None)
					if eqtype == 'peak':
						plugins.add_eqband(cvpj_l, pluginid, 1, eqfiltdata['cutoffHz'], eqgain, 'peak', 1, None)
					if eqtype == 'high-pass':
						plugins.add_eqband(cvpj_l, pluginid, 1, eqfiltdata['cutoffHz'], 0, 'high_pass', eqgain_pass, None)

		if 'echo' in bb_inst_effects:
			pluginid = addfx_universal(cvpj_instid, 'delay-c')
			plugins.add_plug_fxvisual(cvpj_l, pluginid, 'Echo', None)
			plugins.add_plug_fxdata(cvpj_l, pluginid, 1, 0.5)

			plugins.add_plug_data(cvpj_l, pluginid, 'time_type', 'steps')
			plugins.add_plug_data(cvpj_l, pluginid, 'time', bb_instrument['echoDelayBeats']*8)
			plugins.add_plug_data(cvpj_l, pluginid, 'feedback', bb_instrument['echoSustain']/240)

		if 'distortion' in bb_inst_effects:
			pluginid = addfx_simple(cvpj_instid, 'distortion')
			plugins.add_plug_fxvisual(cvpj_l, pluginid, 'Distortion', None)
			plugins.add_plug_param(cvpj_l, pluginid, 'amount', bb_instrument['distortion']/100, 'float', 'amount')

		if 'bitcrusher' in bb_inst_effects:
			pluginid = addfx_universal(cvpj_instid, 'bitcrush')
			plugins.add_plug_fxvisual(cvpj_l, pluginid, 'Bitcrusher', None)

			t_bits_val = round(xtramath.between_from_one(7, 0, bb_instrument['bitcrusherQuantization']/100))

			bits_out = 1
			for num in range(t_bits_val):
				bits_out *= 2
			freq_out = (bb_instrument['bitcrusherOctave']+1)*523.25

			plugins.add_plug_param(cvpj_l, pluginid, 'bits', bits_out, 'float', "")
			plugins.add_plug_param(cvpj_l, pluginid, 'freq', freq_out, 'float', "")

		if 'chorus' in bb_inst_effects:
			pluginid = addfx_simple(cvpj_instid, 'chorus')
			plugins.add_plug_fxvisual(cvpj_l, pluginid, 'Chorus', None)
			plugins.add_plug_fxdata(cvpj_l, pluginid, 1, bb_instrument['chorus']/100)

		if 'reverb' in bb_inst_effects:
			pluginid = addfx_simple(cvpj_instid, 'reverb')
			plugins.add_plug_fxvisual(cvpj_l, pluginid, 'Reverb', None)
			reverblvl = data_values.get_value(bb_instrument, 'reverb', 40)
			plugins.add_plug_fxdata(cvpj_l, pluginid, 1, reverblvl/100)

		if 'vibrato' in bb_inst_effects:
			if 'vibratoSpeed' in bb_instrument and 'vibratoDelay' in bb_instrument:
				if bb_instrument['vibratoSpeed'] != 0 and bb_instrument['vibratoDelay'] != 50:
					vibrato_speed = 0.7*(1/bb_instrument['vibratoSpeed'])
					vibrato_amount = bb_instrument['vibratoDepth']
					vibrato_delay = (bb_instrument['vibratoDelay']/49)*2
					plugins.add_lfo(cvpj_l, cvpj_instid, 'pitch', 'sine', 'seconds', vibrato_speed, vibrato_delay, 0, vibrato_amount)

		a_attack = data_values.get_value(bb_instrument, 'fadeInSeconds', 0)
		a_release = abs(data_values.get_value(bb_instrument, 'fadeOutTicks', 0)/(jummbox_ticksPerBeat*32))
		plugins.add_asdr_env(cvpj_l, cvpj_instid, 'vol', 0, a_attack, 0, a_decay, a_sustain, a_release, 1)


def parse_notes(channum, bb_notes, bb_instruments):
	cvpj_notelist = []
	for note in bb_notes:
		points = note['points']
		pitches = note['pitches']

		cvpj_note_pos = (points[-1]['tick'] - points[0]['tick'])

		t_duration = calcval(cvpj_note_pos)
		t_position = calcval(points[0]['tick'])
		t_auto_pitch = []
		t_auto_gain = []

		arr_bendvals = []
		arr_volvals = []

		for point in points:
			t_auto_pitch.append({'position': calcval(point['tick']-points[0]['tick']), 'value': point['pitchBend']})
			arr_bendvals.append(point['pitchBend'])
			arr_volvals.append(point['volume'])

		maxvol = max(arr_volvals)

		for point in points:
			if maxvol != 0:
				t_auto_gain.append({'position': calcval(point['tick']-points[0]['tick']), 'value': (point['volume']*(1/maxvol))})

		t_vol = maxvol/100

		cvpj_notemod = {}
		cvpj_notemod['auto'] = {}

		if all(element == arr_volvals[0] for element in arr_volvals) == False:
			cvpj_notemod['auto']['gain'] = t_auto_gain

		if all(element == arr_bendvals[0] for element in arr_bendvals) == False:
			cvpj_notemod['auto']['pitch'] = t_auto_pitch

			if len(pitches) == 1:
				cvpj_notemod['slide'] = []
				for pinu in range(len(t_auto_pitch)-1):
					slide_dur = t_auto_pitch[pinu+1]['position'] - t_auto_pitch[pinu]['position']

					if t_auto_pitch[pinu+1]['value'] != t_auto_pitch[pinu]['value']:
						cvpj_notemod['slide'].append({
							'position': t_auto_pitch[pinu]['position'], 
							'duration': slide_dur, 
							'key': t_auto_pitch[pinu+1]['value']})

		for pitch in pitches:
			t_key = pitch-48 + jummbox_key
			for bb_instrument in bb_instruments:
				t_instrument = 'bb_ch'+str(channum)+'_inst'+str(bb_instrument)
				cvpj_note = note_data.mx_makenote(t_instrument, t_position, t_duration, t_key, t_vol, None)
				cvpj_note['notemod'] = cvpj_notemod
				cvpj_notelist.append(cvpj_note)
	return cvpj_notelist


def parse_channel(channeldata, channum, durpos):
	global jummbox_notesize
	global jummbox_beatsPerBar
	global jummbox_ticksPerBeat

	bbcvpj_placementnames[channum] = []
	bb_color = None
	bb_type = channeldata['type']
	bb_instruments = channeldata['instruments']
	bb_patterns = channeldata['patterns']
	bb_sequence = channeldata['sequence']

	if bb_type == 'pitch' or bb_type == 'drum':
		if bb_type == 'pitch': bb_color = getcolor_p()
		if bb_type == 'drum': bb_color = getcolor_d()

		t_instnum = 1
		for bb_instrument in bb_instruments:

			bb_inst_effects = data_values.get_value(bb_instrument, 'effects', [])

			parse_instrument(channum, t_instnum, bb_instrument, bb_type, bb_color, bb_inst_effects)
			cvpj_instid = 'bb_ch'+str(channum)+'_inst'+str(t_instnum)

			if 'panning' in bb_inst_effects: tracks_mi.inst_param_add(cvpj_l, cvpj_instid, 'pan', bb_instrument['pan']/50, 'float')
			if 'detune' in bb_inst_effects: tracks_mi.inst_param_add(cvpj_l, cvpj_instid, 'pitch', bb_instrument['detuneCents']/100, 'float')

			tracks_mi.playlist_add(cvpj_l, str(channum))
			tracks_mi.playlist_visual(cvpj_l, str(channum), color=bb_color)

			t_instnum += 1

		patterncount = 0
		for bb_pattern in bb_patterns:
			nid_name = str(patterncount+1)
			cvpj_patid = 'bb_ch'+str(channum)+'_pat'+str(patterncount)
			bb_notes = bb_pattern['notes']
			if 'instruments' in bb_pattern: bb_instruments = bb_pattern['instruments']
			else: bb_instruments = [1]
			if bb_notes != []: 
				tracks_mi.notelistindex_add(cvpj_l, cvpj_patid, parse_notes(channum, bb_notes, bb_instruments))
				tracks_mi.notelistindex_visual(cvpj_l, cvpj_patid, name=nid_name)
			patterncount += 1

		placement_pos = 0
		for partnum in range(len(bb_sequence)):
			bb_part = bb_sequence[partnum]
			bb_partdur = durpos[partnum]
			if bb_part != 0:
				cvpj_l_placement = placement_data.makepl_n_mi(calcval(placement_pos), calcval(bb_partdur), 'bb_ch'+str(channum)+'_pat'+str(bb_part-1))
				cvpj_l_placement['cut'] = {'type': 'cut', 'start': 0, 'end': calcval(bb_partdur)}
				tracks_mi.add_pl(cvpj_l, str(channum), 'notes', cvpj_l_placement)
				bbcvpj_placementnames[channum].append('bb_ch'+str(channum)+'_pat'+str(bb_part-1))
			else:
				bbcvpj_placementnames[channum].append(None)
			placement_pos += bb_partdur

	if bb_type == 'mod':
		modChannels = bb_instruments[0]['modChannels']
		modInstruments = bb_instruments[0]['modInstruments']
		modSettings = bb_instruments[0]['modSettings']

		bb_def = []
		for num in range(6):
			bb_def.append([modChannels[num],modInstruments[num],modSettings[num]])

		placement_pos = 0
		for partnum in range(len(bb_sequence)):
			bb_part = bb_sequence[partnum]
			bb_partdur = durpos[partnum]
			if bb_part != 0:
				bb_modnotes = bb_patterns[bb_part-1]['notes']
				if bb_modnotes != []:
					for note in bb_modnotes:
						bb_mod_points = note['points']
						bb_mod_pos = placement_pos+bb_mod_points[0]['tick']
						bb_mod_dur = bb_mod_points[-1]['tick'] - bb_mod_points[0]['tick']
						bb_mod_target = bb_def[(note['pitches'][0]*-1)+5]

						cvpj_autodata_points = []
						for bb_mod_point in bb_mod_points:
							if bb_partdur > bb_mod_point['tick']:
								cvpj_pointdata = {}
								cvpj_pointdata["position"] = calcval(bb_mod_point['tick'])-calcval(bb_mod_pos)+calcval(placement_pos)
								cvpj_pointdata["value"] = bb_mod_point['volume']
								cvpj_autodata_points.append(cvpj_pointdata)

						cvpj_autodata = auto.makepl(calcval(bb_mod_pos), calcval(bb_mod_dur), cvpj_autodata_points)

						if bb_mod_target[0] == -1:
							if bb_mod_target[2] == 1: 
								cvpj_autopl = auto.multiply([cvpj_autodata], 0, 0.01)
								auto_data.add_pl(cvpj_l, 'float', ['master', 'vol'], cvpj_autopl[0])
							elif bb_mod_target[2] == 2: 
								cvpj_autopl = auto.multiply([cvpj_autodata], 30, 1)
								auto_data.add_pl(cvpj_l, 'float', ['main', 'bpm'], cvpj_autopl[0])
							elif bb_mod_target[2] == 17: 
								cvpj_autopl = auto.multiply([cvpj_autodata], -250, 0.01)
								auto_data.add_pl(cvpj_l, 'float', ['main', 'pitch'], cvpj_autopl[0])

						else:
							auto_instnum = 1
							auto_cvpj_instid = 'bb_ch'+str(bb_mod_target[0]+1)+'_inst'+str(bb_mod_target[1]+1)

							if bb_mod_target[2] == 6: 
								cvpj_autopl = auto.multiply([cvpj_autodata], -50, 0.02)
								auto_data.add_pl(cvpj_l, 'float', ['track', auto_cvpj_instid, 'pan'], cvpj_autopl[0])
							elif bb_mod_target[2] == 15: 
								cvpj_autopl = auto.multiply([cvpj_autodata], -200, 1)
								auto_data.add_pl(cvpj_l, 'float', ['track', auto_cvpj_instid, 'pitch'], cvpj_autodata)
							elif bb_mod_target[2] == 36: 
								cvpj_autopl = auto.multiply([cvpj_autodata], 0, 0.04)
								auto_data.add_pl(cvpj_l, 'float', ['track', auto_cvpj_instid, 'vol'], cvpj_autopl[0])

			placement_pos += bb_partdur

def get_durpos(jummbox_channels):
	global jummbox_notesize
	global jummbox_beatsPerBar
	global jummbox_ticksPerBeat

	autodur = {}
	sequencelen = None

	for jummbox_channel in jummbox_channels:
		bb_type = jummbox_channel['type']
		bb_instruments = jummbox_channel['instruments']
		bb_patterns = jummbox_channel['patterns']
		bb_sequence = jummbox_channel['sequence']
		if sequencelen == None: sequencelen = [jummbox_beatsPerBar*jummbox_ticksPerBeat for _ in range(len(bb_sequence))]

		if bb_type == 'mod':
			modChannels = bb_instruments[0]['modChannels']
			modInstruments = bb_instruments[0]['modInstruments']
			modSettings = bb_instruments[0]['modSettings']

			nextbarfound = None
			for num in range(6):
				autodef = [modChannels[num],modInstruments[num],modSettings[num]]
				if autodef == [-1, 0, 4]:
					nextbarfound = num
					break

			if nextbarfound != None:
				patnum = 1
				for bb_pattern in bb_patterns:
					for autonotedata in bb_pattern['notes']:
						if autonotedata['pitches'][0] == 5-num:
							autodur[patnum] = autonotedata['points'][0]['tick']
					patnum += 1

				for seqnum in range(len(bb_sequence)):
					if bb_sequence[seqnum] in autodur:
						if sequencelen[seqnum] > autodur[bb_sequence[seqnum]]: sequencelen[seqnum] = autodur[bb_sequence[seqnum]]

	return sequencelen


class input_jummbox(plugin_input.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def getshortname(self): return 'jummbox'
	def getname(self): return 'jummbox'
	def gettype(self): return 'mi'
	def getdawcapabilities(self): 
		return {
		'track_lanes': True,
		}
	def supported_autodetect(self): return False
	def parse(self, input_file, extra_param):
		global cvpj_l

		global idvals_inst_beepbox

		global jummbox_beatsPerBar
		global jummbox_ticksPerBeat
		global jummbox_key

		global bbcvpj_placementsize
		global bbcvpj_placementnames

		cvpj_l = {}

		idvals_inst_beepbox = idvals.parse_idvalscsv('data_idvals/beepbox_inst.csv')

		bbcvpj_placementsize = []
		bbcvpj_placementnames = {}

		bytestream = open(input_file, 'r', encoding='utf8')
		jummbox_json = json.load(bytestream)

		tracks_master.create(cvpj_l, jummbox_json['masterGain'] if 'masterGain' in jummbox_json else 1)
		tracks_master.visual(cvpj_l, name='Master')

		cvpj_l_track_data = {}
		cvpj_l_track_order = []
		cvpj_l_track_placements = {}

		if 'name' in jummbox_json: song.add_info(cvpj_l, 'title', jummbox_json['name'])
		
		jummbox_key = noteoffset[jummbox_json['key']]
		jummbox_channels = jummbox_json['channels']
		jummbox_beatsPerBar = jummbox_json['beatsPerBar']
		jummbox_ticksPerBeat = jummbox_json['ticksPerBeat']
		jummbox_beatsPerMinute = jummbox_json['beatsPerMinute']

		global jummbox_notesize
		jummbox_notesize = jummbox_beatsPerBar*jummbox_ticksPerBeat

		durpos = get_durpos(jummbox_channels)
		patlentable = [calcval(x) for x in durpos]
		placements.make_timemarkers(cvpj_l, [4,8], patlentable, None)

		if 'introBars' in jummbox_json and 'loopBars' in jummbox_json:
			introbars = sum(patlentable[0:jummbox_json['introBars']])
			loopbars = (sum(patlentable[0:jummbox_json['loopBars']]) + introbars)
			song.add_timemarker_looparea(cvpj_l, 'Loop', introbars, loopbars)

		chancount = 1
		for jummbox_channel in jummbox_channels:
			parse_channel(jummbox_channel, chancount, durpos)
			chancount += 1

		cvpj_l['do_addloop'] = True

		song.add_param(cvpj_l, 'bpm', jummbox_beatsPerMinute)

		return json.dumps(cvpj_l)
