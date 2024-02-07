# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

notelist_blocks = []
timesigblocks = None

from functions import xtramath
from functions import data_values
#from functions import repeatfind
#from functions import data_regions

def get_similarity_val(first, second, nlb_exists):
	first_pos = [x[0] for x in nlb_exists[first]]
	first_dur = [x[1] for x in nlb_exists[first]]
	first_key = [x[2] for x in nlb_exists[first]]
	second_pos = [x[0] for x in nlb_exists[second]]
	second_dur = [x[1] for x in nlb_exists[second]]
	second_key = [x[2] for x in nlb_exists[second]]
	dif_pos = xtramath.similar(first_pos, second_pos)
	dif_dur = xtramath.similar(first_dur, second_dur)
	dif_key = xtramath.similar(first_key, second_key)
	dif_all = xtramath.average([dif_pos, dif_dur, dif_key])
	return dif_all

def get_similarity(patstofind, nlb_exists):
	patfindlen = len(patstofind)
	similarity = [[None for _ in range(patfindlen)] for _ in range(patfindlen)]
	similarity_done = []
	for first in patstofind:
		for second in patstofind:
			if ([first, second] not in similarity_done) and ([second, first] not in similarity_done):
				simout = get_similarity_val(first, second, nlb_exists)
				similarity_done.append([first, second])
				similarity_done.append([second, first])
				similarity[second][first] = simout
				similarity[first][second] = simout
	return similaritys

# ---------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------
# -------------------------------------------------- Main Function ----------------------------------------------
# ---------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------


def smart_merge(global_regions, local_region_count_list):
	nlb_pos = 0
	for lregc in local_region_count_list:

		nlb_exists = []
		nlb_patnum = []
		for nlb_num in range(nlb_pos, nlb_pos+lregc):
			
			nlb_notes = global_regions[nlb_num][2]

			if nlb_notes == []: nlb_patnum.append(None)
			else:
				if nlb_notes not in nlb_exists: nlb_exists.append(nlb_notes)
				nlb_patnum.append(nlb_exists.index(nlb_notes))

		#used_areas = repeatfind.find(nlb_patnum, False)
		used_areas = repeatfind.find(nlb_patnum, False)
		#used_areas_r = repeatfind.find(nlb_patnum, True)

		for nlb_num in range(nlb_pos, nlb_pos+lregc):
			used_area = used_areas[nlb_num-nlb_pos]
			if global_regions[nlb_num][5] == False and used_area:
				global_regions[nlb_num][5] = used_area

		nlb_pos += lregc





def mergetablenotes(initnotereg, addnotereg):
    inr_pos, inr_dur, inr_notes = initnotereg
    anr_pos, anr_dur, anr_notes = addnotereg
    for anr_note in anr_notes:
        inr_notes.append([anr_note[0]+inr_dur, anr_note[1], anr_note[2], anr_note[3]])
    return [inr_pos, inr_dur+anr_dur, inr_notes]

def add_timesigblocks(in_timesigblocks):
	global timesigblocks
	timesigblocks = in_timesigblocks
