# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects import regions
import numpy as np
from functions import xtramath
from objects.data_bytes import dynbytearr

timesig_premake = dynbytearr.dynbytearr_premake([
		('type', np.uint8),

		('start', np.float64),
		('end', np.float64),
		('numerator', np.uint8),
		('denominator', np.uint8),

		('dur', np.float64),
	])

BLOCKID__ZERO = 100
BLOCKID__START = 101
BLOCKID__END = 102
BLOCKID__TIMESIG = 1

def add_dur_end(splitdata):
	p = None
	for n, u in enumerate(splitdata.data):
		if u['used']:
			if p:
				p['end'] = u['start']
				p['dur'] = u['start']-p['start']
			p = u


def remove_pos_clones(splitdata):
	splitdata.sort(['start'])
	prevval = -1
	for x in splitdata.data:
		if x['used']:
			if prevval-x['start'] == 0: x['used'] = 0
			prevval = x['start']
	splitdata.clean()

class timesigblocks:
	def __init__(self):
		self.splitdata = timesig_premake.create()

	def create_points_cut(self, convproj_obj, dawvert_intent):
		cur_splitdata = self.splitdata.create_cursor()

		mode = dawvert_intent.splitter_mode if dawvert_intent else 0
		detect_start = dawvert_intent.splitter_detect_start if dawvert_intent else True

		ppq = convproj_obj.time_ppq

		timesig_num, timesig_dem = convproj_obj.timesig
		cur_splitdata.add()
		cur_splitdata['type'] = BLOCKID__ZERO
		cur_splitdata['start'] = 0
		cur_splitdata['numerator'] = timesig_num
		cur_splitdata['denominator'] = timesig_dem

		timesig_num, timesig_dem = convproj_obj.timesig
		cur_splitdata.add()
		cur_splitdata['type'] = BLOCKID__END
		cur_splitdata['start'] = convproj_obj.get_dur()
		cur_splitdata['numerator'] = timesig_num
		cur_splitdata['denominator'] = timesig_dem

		timesig_num, timesig_dem = convproj_obj.timesig
		cur_splitdata.add()
		cur_splitdata['type'] = BLOCKID__END
		cur_splitdata['start'] = convproj_obj.get_dur()+ppq
		cur_splitdata['numerator'] = timesig_num
		cur_splitdata['denominator'] = timesig_dem

		for pos, timesig in convproj_obj.timesig_auto:
			cur_splitdata.add()
			cur_splitdata['type'] = BLOCKID__TIMESIG
			cur_splitdata['start'] = pos
			cur_splitdata['numerator'] = timesig[0]
			cur_splitdata['denominator'] = timesig[1]
		
		remove_pos_clones(self.splitdata)
		add_dur_end(self.splitdata)

		if mode == 0:
			for u in self.splitdata.get_used():
				for val in xtramath.gen_float_range(float(u['start']), float(u['end']), ppq*float(u['numerator'])):
					cur_splitdata.add()
					cur_splitdata['start'] = val
					cur_splitdata['numerator'] = u['numerator']
					cur_splitdata['denominator'] = u['denominator']

		if mode == 1:

			if detect_start:
				startpos = 0
				if convproj_obj.transport.loop_start:
					startpos = convproj_obj.transport.loop_start
				if not startpos:
					startpos = convproj_obj.transport.start_pos

				useddata = self.splitdata.get_used()
				poslist = useddata['start']

				if max(poslist)>startpos and startpos not in poslist:
					timesigid = np.searchsorted(poslist, startpos)
					betweenval = useddata[timesigid]

					convproj_obj.timesig_auto.add_point(startpos, [betweenval['numerator'], betweenval['denominator']])
				
					cur_splitdata.add()
					cur_splitdata['start'] = startpos
					cur_splitdata['numerator'] = betweenval['numerator']
					cur_splitdata['denominator'] = betweenval['denominator']

			remove_pos_clones(self.splitdata)
			add_dur_end(self.splitdata)

			for u in self.splitdata.get_used():
				for val in xtramath.gen_float_range(u['start'], u['end'], ppq*(u['numerator']*u['denominator'])):
					cur_splitdata.add()
					cur_splitdata['start'] = val
					cur_splitdata['numerator'] = u['numerator']
					cur_splitdata['denominator'] = u['denominator']

		if mode == 2:

			if detect_start:
				startpos = 0
				if convproj_obj.transport.loop_start:
					startpos = convproj_obj.transport.loop_start
				if not startpos:
					startpos = convproj_obj.transport.start_pos

				useddata = self.splitdata.get_used()
				poslist = useddata['start']
				if max(poslist)>startpos and startpos not in poslist:
					timesigid = np.searchsorted(poslist, startpos)
					betweenval = useddata[timesigid]

					cur_splitdata.add()
					cur_splitdata['start'] = startpos
					cur_splitdata['numerator'] = betweenval['numerator']
					cur_splitdata['denominator'] = betweenval['denominator']

			remove_pos_clones(self.splitdata)
			add_dur_end(self.splitdata)

			for u in self.splitdata.get_used():
				for val in xtramath.gen_float_range(u['start'], u['end'], ppq*(u['numerator']*2)):
					cur_splitdata.add()
					cur_splitdata['start'] = val
					cur_splitdata['numerator'] = u['numerator']
					cur_splitdata['denominator'] = u['denominator']

		remove_pos_clones(self.splitdata)
		add_dur_end(self.splitdata)

dtype_blocks = np.dtype([
		('start', np.float64),
		('end', np.float64),
		('dur', np.float64),

		('used', np.uint8),
		('nosplit', np.uint8),
		('overflow', np.float64),
		('remaining', np.float64),
	])

useactive_premake = dynbytearr.dynbytearr_premake([
		('start', np.float64),
		('end', np.float64),
		('active', np.uint8),
		('done', np.uint8),
	])

class cvpj_notelist_splitter:
	def __init__(self, timesigblocks_obj, ppq):
		self.data = []
		self.ppq = ppq
		self.timesigblocks_obj = timesigblocks_obj

	def add_plnl(self, i_pl):
		self.data.append(i_pl)

	def process(self):
		useddata = self.timesigblocks_obj.splitdata.get_used()
		blocksdata = np.zeros((len(self.data), len(useddata)), dtype=dtype_blocks)
		blocksdata['start'] = useddata['start']
		blocksdata['end'] = useddata['end']
		blocksdata['dur'] = useddata['dur']

		for plnum, pldata in enumerate(self.data):
			for blocknum, blockdata in enumerate(useddata):
				splitd = blocksdata[plnum][blocknum]
				notelist = pldata.notelist
				splitd['used'], splitd['overflow'] = notelist.usedoverflow(blockdata['start'], blockdata['end'])

		for blockdata in blocksdata:
			remainval = 0
			for splitd in blockdata:
				splitd['remaining'] = remainval
				if remainval: splitd['used'] = 1
				remainval = max(remainval-splitd['dur'], 0)
				remainval += splitd['overflow']
				splitd['nosplit'] = 1+(remainval!=0) if splitd['used'] else 0

		for plnum, pldata in enumerate(self.data):
			activedata = useactive_premake.create()
			cur_activedata = activedata.create_cursor()

			cur_activedata.add()

			blockdata = blocksdata[plnum]

			for x in blockdata:
				nosplit = x['nosplit']
				if cur_activedata['done']: cur_activedata.add()
				if nosplit != 0:
					if not cur_activedata['active']:
						cur_activedata['start'] = x['start']
						cur_activedata['active'] = 1
					cur_activedata['end'] = x['end']
					if nosplit == 1:
						cur_activedata['done'] = 1
						cur_activedata['active'] = 0
				else:
					if cur_activedata['active']:
						cur_activedata['done'] = 1

			for x in activedata.get_used():
				if x['done']:
					placement_obj = pldata.add_notes()
					placement_obj.notelist = pldata.notelist.new_nl_start_end(x['start'], x['end'])
					time_obj = placement_obj.time
					time_obj.set_startend(int(x['start']), int(x['end']))
			pldata.notelist.clear()