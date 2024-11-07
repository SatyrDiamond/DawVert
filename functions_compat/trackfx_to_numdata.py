# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

class to_numdata:
	def __init__(self):
		self.tracknum = 0
		self.output_ids = []
		self.idnum_tracks = {}
		self.idnum_return = {}
		self.idnum_group = {}


	def trackfx_to_numdata_track(self, convproj_obj, trackid, ingroupnum):
		if ingroupnum == None: self.output_ids.append([self.tracknum, 'track', trackid, [-1, 1, None], []  ])
		else: self.output_ids.append([self.tracknum, 'track', trackid, [ingroupnum, 1, None], []  ])
		self.idnum_tracks[trackid] = self.tracknum

		track_obj = convproj_obj.track_data[trackid]
		self.tracknum = self.idnum_tracks[trackid]
		for target, send_obj in track_obj.sends.iter():
			if target in self.idnum_return:
				send_amt = send_obj.params.get('amount',1).value
				self.output_ids[self.tracknum][4].append([self.idnum_return[target], send_amt, send_obj.sendautoid])
		self.tracknum += 1


	def trackfx_to_numdata(self, convproj_obj, order_mode): 
		group_trk = {}
		nogroup_trk = []
		groups_inside = {}

		for trackid, track_obj in convproj_obj.track__iter():
			if track_obj.group != None:
				if track_obj.group not in group_trk: group_trk[track_obj.group] = []
				group_trk[track_obj.group].append(trackid)
			else:
				nogroup_trk.append(trackid)

		for returnid in convproj_obj.track_master.returns:
			self.idnum_return[returnid] = self.tracknum
			self.output_ids.append([self.tracknum, 'return', returnid, [-1, 1, None], []])
			self.tracknum += 1

			

		for groupid in group_trk:
			if groupid and groupid in convproj_obj.groups:
				group_obj = convproj_obj.groups[groupid]
				parent_group = group_obj.group
				if parent_group != None: groups_inside[self.tracknum] = parent_group
				self.idnum_group[groupid] = self.tracknum
				self.output_ids.append([self.tracknum, 'group', groupid, [-1, 1, None], []  ])
				self.tracknum += 1
				if order_mode == 0:
					for trackid in group_trk[groupid]:
						self.trackfx_to_numdata_track(convproj_obj, trackid, self.idnum_group[groupid])

		if order_mode == 1:
			for groupid in group_trk:
				for trackid in group_trk[groupid]:
					self.trackfx_to_numdata_track(convproj_obj, trackid, self.idnum_group[groupid])

		groupidnum = None

		for groupidnum in groups_inside:
			self.output_ids[groupidnum][3] = [self.idnum_group[groups_inside[groupidnum]], 1, None]

		for trackid in nogroup_trk:
			self.trackfx_to_numdata_track(convproj_obj, trackid, None)

		if groupidnum:
			for groupid in group_trk:
				if groupid:
					group_obj = convproj_obj.groups[groupid]
					for sendid, send_obj in group_obj.sends.iter():
						send_amt = send_obj.params.get('amount',1).value
						self.output_ids[groupidnum][4].append([self.idnum_group[groupid], send_amt, send_obj.sendautoid])

		return self.output_ids