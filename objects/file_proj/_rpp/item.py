from objects.file_proj._rpp import func as reaper_func
from objects.file_proj._rpp import source as rpp_source

rvd = reaper_func.rpp_value
rvs = reaper_func.rpp_value.single_var
robj = reaper_func.rpp_obj

class rpp_item:
	def __init__(self):
		self.fadein = rvd([1,0,0,1,0,0,0], ['fade_type','fade_time','num2','num3','num4','curve','num6'], None, True)
		self.fadeout = rvd([1,0,0,1,0,0,0], ['fade_type','fade_time','num2','num3','num4','curve','num6'], None, True)
		self.mute = rvd([0,0], ['mute','num1'], None, True)
		self.volpan = rvd([1,0,1,-1], ['vol','pan','vol2','panlaw'], None, True)
		self.playrate = rvd([1,1,0,-1,0,0.0025], ['rate','preserve_pitch','pitch','stretch_mode','mode','fade_size'], None, True)
		self.position = rvs(0.0, float, True)
		self.snapoffs = rvs(0.0, float, True)
		self.length = rvs(5.0, float, True)
		self.loop = rvs(0.0, float, True)
		self.alltakes = rvs(0.0, float, True)
		self.sel = rvs(0.0, float, True)
		self.iguid = rvs("", str, True)
		self.iid = rvs(2.0, float, True)
		self.name = rvs("", str, True)
		self.soffs = rvs(0.0, float, True)
		self.chanmode = rvs(0.0, float, True)
		self.color = rvs(0, int, False)
		self.guid = rvs("", str, True)
		self.source = None
		self.beat = rvs(1, int, True)

	def load(self, rpp_data):
		for name, is_dir, values, inside_dat in reaper_func.iter_rpp(rpp_data):
			if name == 'POSITION': self.position.set(values[0])
			if name == 'SNAPOFFS': self.snapoffs.set(values[0])
			if name == 'LENGTH': self.length.set(values[0])
			if name == 'LOOP': self.loop.set(values[0])
			if name == 'ALLTAKES': self.alltakes.set(values[0])
			if name == 'FADEIN': self.fadein.read(values)
			if name == 'FADEOUT': self.fadeout.read(values)
			if name == 'MUTE': self.mute.read(values)
			if name == 'SEL': self.sel.set(values[0])
			if name == 'IGUID': self.iguid.set(values[0])
			if name == 'IID': self.iid.set(values[0])
			if name == 'NAME': self.name.set(values[0])
			if name == 'VOLPAN': self.volpan.read(values)
			if name == 'SOFFS': self.soffs.set(values[0])
			if name == 'PLAYRATE': self.playrate.read(values)
			if name == 'CHANMODE': self.chanmode.set(values[0])
			if name == 'BEAT': self.beat.set(values[0])
			if name == 'GUID': self.guid.set(values[0])
			if name == 'COLOR': self.color.set(values[0])
			if name == 'SOURCE': 
				source_obj = rpp_source.rpp_source()
				source_obj.type = values[0]
				source_obj.load(inside_dat)
				self.source = source_obj

	def write(self, rpp_data):
		self.position.write('POSITION',rpp_data)
		self.snapoffs.write('SNAPOFFS',rpp_data)
		self.length.write('LENGTH',rpp_data)
		self.loop.write('LOOP',rpp_data)
		self.alltakes.write('ALLTAKES',rpp_data)
		self.fadein.write('FADEIN', rpp_data)
		self.fadeout.write('FADEOUT', rpp_data)
		self.mute.write('MUTE', rpp_data)
		if self.beat != None: self.beat.write('BEAT',rpp_data)
		self.sel.write('SEL',rpp_data)
		self.iguid.write('IGUID',rpp_data)
		self.iid.write('IID',rpp_data)
		self.name.write('NAME',rpp_data)
		self.color.write('COLOR',rpp_data)
		self.volpan.write('VOLPAN', rpp_data)
		self.soffs.write('SOFFS',rpp_data)
		self.playrate.write('PLAYRATE', rpp_data)
		self.chanmode.write('CHANMODE',rpp_data)
		self.guid.write('GUID',rpp_data)
		if self.source != None:
			rpp_sourcedata = robj('SOURCE',[self.source.type])
			self.source.write(rpp_sourcedata)
			rpp_data.children.append(rpp_sourcedata)
