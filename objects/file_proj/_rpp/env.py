from objects.file_proj._rpp import func as reaper_func
from objects.file_proj._rpp import item as rpp_item
from objects.file_proj._rpp import fxchain as rpp_fxchain

rvd = reaper_func.rpp_value
ts = reaper_func.to_string
rvs = reaper_func.rpp_value.single_var
robj = reaper_func.rpp_obj

class rpp_env:
	def __init__(self):
		self.used = False
		self.points = []
		self.eguid = rvs(0, str, False)
		self.act = rvd([0,-1], ['bypass', 'unknown'], None, True)
		self.vis = rvd([1,1,1], None, None, True)
		self.laneheight = rvd([0,0], None, None, True)
		self.arm = rvs(0, float, False)
		self.defshape = rvd([0,-1,-1], None, None, True)

		self.is_param = False
		self.param_id = 0
		self.param_name = None
		self.param_min = 0
		self.param_max = 1
		self.param_mid = 0.5
		self.visname = ''


	def read(self, rpp_data, in_values):
		trackid = ''
		self.used = True
		for name, is_dir, values, inside_dat in reaper_func.iter_rpp(rpp_data):
			if name == 'EGUID': self.eguid.set(values[0])
			if name == 'ARM': self.arm.set(values[0])
			if name == 'ACT': self.act.read(values)
			if name == 'VIS': self.vis.read(values)
			if name == 'LANEHEIGHT': self.laneheight.read(values)
			if name == 'DEFSHAPE': self.defshape.read(values)
			if name == 'PT': self.points.append([float(x) for x in values])

		if in_values:
			self.is_param = True
			for n, v in enumerate(in_values):
				if n == 0: 
					splitname = v.split(':', 1)
					self.param_id = int(splitname[0])
					if len(splitname)>1: self.param_name = splitname[1]
				if n == 1: self.param_min = float(v)
				if n == 2: self.param_max = float(v)
				if n == 3: self.param_mid = float(v)
				if n == 4: self.visname = v

	def write(self, name, rpp_data):
		if self.used:
			values = [str(self.param_id)+(':'+self.param_name if self.param_name else ''),ts(float, self.param_min),ts(float, self.param_max),ts(float, self.param_mid),self.visname] if self.is_param else []
			rpp_tempdata = robj(name,values)
			self.eguid.write('EGUID',rpp_tempdata)
			self.act.write('ACT',rpp_tempdata)
			self.vis.write('VIS',rpp_tempdata)
			self.laneheight.write('LANEHEIGHT',rpp_tempdata)
			self.arm.write('ARM',rpp_tempdata)
			self.defshape.write('DEFSHAPE',rpp_tempdata)
			for p in self.points:
				rpp_tempdata.children.append(['PT']+[ts(float, x) for x in p])
			rpp_data.children.append(rpp_tempdata)

