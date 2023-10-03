# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import xtramath
from functions import data_values

# ---------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------
# --------------------------------------------------   Print   --------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------

p_headersize = 20
p_partsize = 4

def print_usedlist(i_name, numlist):
	print((i_name).rjust(p_headersize), end=' |')
	for x in numlist:
		if x == True: x = '###'
		if x == False: x = '   '
		print(str(x).rjust(p_partsize)+'|', end='') 
	print()

def print_numlist(i_name, numlist):
	print((i_name).rjust(p_headersize), end=' |')
	[print(str(x).rjust(p_partsize)+'|', end='') for x in numlist]
	print()

def print_regions(i_length, i_name, regions):
	usedparts = [' ' for _ in range(i_length*2)]
	for region in regions:
		for num in range(region[0], region[0]+region[1]):
			usedparts[num] = '####'
		usedparts[region[0]+region[1]] = '##\\ '

	print((i_name).rjust(p_headersize), end=' |')
	[print(str(x).rjust(p_partsize)+'|', end='') for x in usedparts]
	print()

# ---------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------
# -------------------------------------------------- Find Loop --------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------

cond_values_tres = 0.05
cond_same_loc_tres = 0.5
cond_null_tres = 0.4

def subfind(lst_numberlist_in, foundlocs, patnum):
	foundlocs_cur = [x for x in foundlocs]
	highestloc = max(foundlocs)
	numlistlen = len(lst_numberlist_in)
	lst_numberlist = lst_numberlist_in.copy()
	lst_numberlist += [None for _ in range(numlistlen)]

	out_length = 0
	#print(patnum, foundlocs)

	while highestloc < numlistlen:
		foundlocs_cur = [x+1 for x in foundlocs_cur]

		precond_values = [lst_numberlist[x] for x in foundlocs_cur]
		cond_values = 1 - xtramath.average([int(x == precond_values[0]) for x in precond_values])
		cond_null = 1 - xtramath.average([int(x == None) for x in precond_values])

		precond_same_loc = [int(x in foundlocs) for x in foundlocs_cur]
		cond_same_loc = xtramath.average(precond_same_loc)

		bool_values = cond_values > cond_values_tres
		bool_same_loc = cond_same_loc > cond_same_loc_tres
		bool_cond_null = cond_null < cond_null_tres

		#print('---', out_length, '|', precond_values, cond_values, bool_values, '|', precond_same_loc, cond_same_loc, bool_same_loc)
		if bool_same_loc or bool_values or bool_cond_null: break
		else:
			highestloc += 1
			out_length += 1

	regions = [[x, out_length] for x in foundlocs]
	if out_length > 1:
		return regions
	else:
		return []

def find(lst_numberlist):
	#print('---------------- repeat find ----------------')
	lst_existing = []
	for x in lst_numberlist:
		if x != None: lst_existing.append(x)

	#print_numlist('NUMLIST', lst_numberlist)

	len_numberlist = len(lst_numberlist)

	numbdone = []

	regionsdata = []

	for patnum in lst_existing:
		foundlocs = [ind for ind, ele in enumerate(lst_numberlist) if ele == patnum]
		if patnum not in numbdone:
			if len(foundlocs) > 1:
				regions = subfind(lst_numberlist, foundlocs, patnum)
				if regions != []:
					regionsdata.append([patnum, regions])
			numbdone.append(patnum)

	used_areas = [False for _ in range(len_numberlist) ]
	d_endpoints = {}
	for s_regionsdata in regionsdata:
		#print_regions(len_numberlist, 'FOUND '+str(s_regionsdata[0]), s_regionsdata[1])
		for s_reg in s_regionsdata[1]:
			endpointval = s_reg[0]+s_reg[1]

			for num in range(s_reg[0], s_reg[0]+s_reg[1]):
				used_areas[num] = True

			if endpointval not in d_endpoints: d_endpoints[endpointval] = 0
			d_endpoints[endpointval] += 1

	for d_endpoint in d_endpoints:
		if len(regionsdata) > 4:
			if d_endpoints[d_endpoint] > 1: used_areas[d_endpoint] = False
		else:
			if d_endpoints[d_endpoint] > 0: used_areas[d_endpoint] = False

	#print_usedlist('USED', used_areas)

	return used_areas