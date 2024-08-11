from objects.file_proj._rpp import func as reaper_func

robj = reaper_func.rpp_obj
rvd = reaper_func.rpp_value
rvs = reaper_func.rpp_value.single_var

class rpp_source:
	def __init__(self):
		self.type = 'NONE'
		self.length = rvs('', float, False)
		self.mode = rvs(0, int, False)
		self.file = rvs('', str, False)
		self.startpos = rvs('', float, False)
		self.overlap = rvs('', float, False)
		self.hasdata = rvd([0,960,'QN'], ['hasdata', 'ppq', 'ppq_l'], [bool,int,str], False)
		self.notes = []
		self.source = None

	def load(self, rpp_data):
		for name, is_dir, values, inside_dat in reaper_func.iter_rpp(rpp_data):
			if name == 'FILE': self.file.set(values[0])
			if name == 'E': self.notes.append([True]+values)
			if name == 'e': self.notes.append([False]+values)
			if name == 'HASDATA': self.hasdata.read(values)
			if name == 'LENGTH': self.length.read(values)
			if name == 'STARTPOS': self.startpos.read(values)
			if name == 'OVERLAP': self.overlap.read(values)
			if name == 'MODE': self.mode.read(values)
			if name == 'SOURCE': 
				source_obj = rpp_source()
				source_obj.type = values[0]
				source_obj.load(inside_dat)
				self.source = source_obj

	def write(self, rpp_data):
		self.length.write('LENGTH', rpp_data)
		self.mode.write('MODE', rpp_data)
		self.file.write('FILE', rpp_data)
		self.startpos.write('STARTPOS', rpp_data)
		self.overlap.write('OVERLAP', rpp_data)
		self.hasdata.write('HASDATA', rpp_data)
		for note in self.notes:
			rpp_data.children.append(['E' if note[0] else 'e']+note[1:])
		if self.source:
			rpp_sourcedata = robj('SOURCE',[self.source.type])
			self.source.write(rpp_sourcedata)
			rpp_data.children.append(rpp_sourcedata)