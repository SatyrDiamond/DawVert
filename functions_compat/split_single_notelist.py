# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

notelist_blocks = []
timesigblocks = None

from functions import xtramath

def mergetablenotes(initnotereg, addnotereg):
    inr_pos, inr_dur, inr_notes = initnotereg
    anr_pos, anr_dur, anr_notes = addnotereg
    for anr_note in anr_notes:
        inr_notes.append([anr_note[0]+inr_dur, anr_note[1], anr_note[2]])
    return [inr_pos, inr_dur+anr_dur, inr_notes]

def add_timesigblocks(in_timesigblocks):
	global timesigblocks
	timesigblocks = in_timesigblocks

def add_notelist(inid, notelist):
	global timesigblocks

	notelist_regions = []
	for _ in range(len(timesigblocks)):
		notelist_regions.append([])

	for note in notelist:
		note_start = note['position']
		note_end = note['duration']
		del note['position']
		del note['duration']
		for tsbnum in range(len(timesigblocks)):
			tsbdat = timesigblocks[tsbnum]
			if tsbdat[0] <= note_start < tsbdat[1]:
				notelist_regions[tsbnum].append([note_start-tsbdat[0], note_end, note])
				break

	global_regions = []
	local_region_count_list = []

	#notelist to g_regions
	for reigionnum in range(len(timesigblocks)):
		area_start, area_end, splitdur = timesigblocks[reigionnum]
		area_notelist = notelist_regions[reigionnum]

		local_region = []
		curpos = area_start
		local_region_count = 0
		for steplen in xtramath.gen_float_blocks((area_end-area_start), splitdur):
			local_region.append([curpos, splitdur, [], False, splitdur, False])
			local_region_count += 1
			curpos += steplen
		local_region_count_list.append(local_region_count)

		for area_note in area_notelist:
			noteregionnnum = int(area_note[0]//splitdur)
			area_note[0] -= noteregionnnum*splitdur
			local_region[noteregionnnum][2].append(area_note)
			local_region[noteregionnnum][3] = True
			if local_region[noteregionnnum][4] < area_note[0]+area_note[1]:
				local_region[noteregionnnum][4] = area_note[0]+area_note[1]

		for local_region_part in local_region:
			local_region_part[4] -= local_region_part[1] 

		global_regions += local_region

	#g_regions merge overlap
	for greg_num in range(len(global_regions)):
		greg_pos, greg_dur, greg_notes, greg_used, greg_of, greg_ofmarked = global_regions[greg_num]
		greg_lanum = greg_num

		while greg_of > 0:
			global_regions[greg_lanum][5] = True
			global_regions[greg_lanum+1][3] = True
			greg_of -= global_regions[greg_lanum][1]
			greg_lanum += 1

	notelist_blocks.append([inid, global_regions])

def get_notelist():
	global notelist_blocks
	for notelist_block in notelist_blocks:

		curreg = None
		preoutput_regs = []
		out_placements = []

		inid, global_regions = notelist_block
		for global_region in global_regions:
			greg_pos, greg_dur, greg_notes, greg_used, greg_of, greg_ofmarked = global_region

			if greg_used == True:
				if greg_ofmarked == False: 
					if curreg == None: curreg = global_region[0:3]
					else: curreg = mergetablenotes(curreg, global_region[0:3])
					preoutput_regs.append(curreg)
					curreg = None
				else:
					if curreg == None: curreg = global_region[0:3]
					else: curreg = mergetablenotes(curreg, global_region[0:3])
			else:
				if curreg != None: preoutput_regs.append(global_region[0:3])
				curreg = None

		for preoutput_reg in preoutput_regs:
			pop_pos, pop_dur, pop_notes = preoutput_reg
			cur_placement = {'notelist': [], 'position': pop_pos, 'duration': pop_dur}
			for rn_pos, rn_dur, rn_extra in pop_notes:
				out_note = rn_extra
				out_note['position'] = rn_pos
				out_note['duration'] = rn_dur
				cur_placement['notelist'].append(out_note)
			out_placements.append(cur_placement)

		yield inid, out_placements