from objects.file_proj._rpp import func as reaper_func
from objects.file_proj._rpp import item as rpp_item
from objects.file_proj._rpp import fxchain as rpp_fxchain
from objects.file_proj._rpp import env as rpp_env
import uuid

rvd = reaper_func.rpp_value
rvs = reaper_func.rpp_value.single_var
robj = reaper_func.rpp_obj

class rpp_track:
	def __init__(self):
		self.volpan = rvd([1,0,-1,-1,1], ['vol','pan','panlaw','left','right'], None, True)
		self.mutesolo = rvd([0,0,0], ['mute','solo','solo_defeat'], [bool,bool,bool], True)
		self.playoffs = rvd([0,1], None, None, True)
		self.isbus = rvd([0,0], None, None, True)
		self.buscomp = rvd([0,0,0,0,0], None, None, True)
		self.showinmix = rvd([1.0,0.6667,0.5,1.0,0.5,0.0,0.0,0.0], None, None, True)
		self.fixedlanes = rvd([9,0,0,0], None, None, False)
		self.rec = rvd([0,0,1,0,0,0,0,0], ['armed','input','monitor','record_mode','monitor_media','preserve_pdc','record_path','unk1'], None, True)
		self.trackheight = rvd([0,0,0,0,0,0,0], ['size','folder_override','unk2','unk3','unk4','unk5','unk6'], None, True)
		self.inq = rvd([0,0,0,0.5,100,0,0,100], ['q_midi','q_pos','q_noteoffs','q_fraction_beat','q_strength','swing_strength','q_range_min','q_range_max'], None, True)
		self.mainsend = rvd([1,0], ['tracknum','unk'], None, True)
		self.name = rvs("", str, True)
		self.peakcol = rvs(16576, int, True)
		self.beat = rvs(0, float, True)
		self.automode = rvs(0.0, float, True)
		self.panlawflags = rvs(0, float, False)
		self.iphase = rvs(0.0, float, True)
		self.sel = rvs(0.0, float, True)
		self.vu = rvs(0, float, False)
		self.nchan = rvs(2.0, float, True)
		self.fx = rvs(1.0, float, True)
		self.trackid = rvs("", str, True)
		self.perf = rvs(0.0, float, True)
		self.midiout  = rvs(1.0, float, True)
		self.items = []
		self.fxchain = None
		self.auxrecv = []
		self.panenv2 = rpp_env.rpp_env()
		self.volenv2 = rpp_env.rpp_env()
		self.muteenv = rpp_env.rpp_env()

	def load(self, rpp_data):
		for name, is_dir, values, inside_dat in reaper_func.iter_rpp(rpp_data):
			if name == 'NAME': self.name.set(values[0])
			if name == 'PEAKCOL': self.peakcol.set(values[0])
			if name == 'BEAT': self.beat.set(values[0])
			if name == 'AUTOMODE': self.automode.set(values[0])
			if name == 'PANLAWFLAGS': self.panlawflags.set(values[0])
			if name == 'VOLPAN': self.volpan.read(values)
			if name == 'MUTESOLO': self.mutesolo.read(values)
			if name == 'IPHASE': self.iphase.set(values[0])
			if name == 'PLAYOFFS': self.playoffs.read(values)
			if name == 'ISBUS': self.isbus.read(values)
			if name == 'BUSCOMP': self.buscomp.read(values)
			if name == 'SHOWINMIX': self.showinmix.read(values)
			if name == 'FIXEDLANES': self.fixedlanes.read(values)
			if name == 'SEL': self.sel.set(values[0])
			if name == 'REC': self.rec.read(values)
			if name == 'VU': self.vu.set(values[0])
			if name == 'TRACKHEIGHT': self.trackheight.read(values)
			if name == 'INQ': self.inq.read(values)
			if name == 'NCHAN': self.nchan.set(values[0])
			if name == 'FX': self.fx.set(values[0])
			if name == 'TRACKID': self.trackid.set(values[0])
			if name == 'PERF': self.perf.set(values[0])
			if name == 'MIDIOUT': self.midiout.set(values[0])
			if name == 'MAINSEND': self.mainsend.read(values)
			if name == 'PANENV2': self.panenv2.read(inside_dat, values)
			if name == 'VOLENV2': self.volenv2.read(inside_dat, values)
			if name == 'MUTEENV': self.muteenv.read(inside_dat, values)
			if name == 'AUXRECV': 
				auxrecv_obj = self.add_auxrecv()
				auxrecv_obj.read(values)
			if name == 'ITEM': 
				item_obj = rpp_item.rpp_item()
				item_obj.load(inside_dat)
				self.items.append(item_obj)
			if name == 'FXCHAIN': 
				fxchain_obj = rpp_fxchain.rpp_fxchain()
				fxchain_obj.load(inside_dat)
				self.fxchain = fxchain_obj

	def add_auxrecv(self):
		auxrecv_obj = rvd(
			[1,0,1,0,0,0,0,0,0,'-1:U',0,-1,''], 
			['tracknum','mode','vol','pan','mute','mono_sum','invert_phase','source_audio_chan','dest_audio_chan','panlaw','midi_chans','auto_mode','unk'], 
			[int,int,float,float,int,int,int,int,int,str,int,int,str], 
			True)
		self.auxrecv.append(auxrecv_obj)
		return auxrecv_obj

	def add_item(self):
		guid = '{'+str(uuid.uuid4())+'}'
		iguid = '{'+str(uuid.uuid4())+'}'
		item_obj = rpp_item.rpp_item()
		self.trackid.set(guid)
		self.items.append(item_obj)
		return item_obj, guid, iguid

	def write(self, rpp_data):
		self.name.write('NAME',rpp_data)
		self.peakcol.write('PEAKCOL',rpp_data)
		self.beat.write('BEAT',rpp_data)
		self.automode.write('AUTOMODE',rpp_data)
		self.panlawflags.write('PANLAWFLAGS',rpp_data)
		self.volpan.write('VOLPAN', rpp_data)
		self.mutesolo.write('MUTESOLO', rpp_data)
		self.iphase.write('IPHASE',rpp_data)
		self.playoffs.write('PLAYOFFS', rpp_data)
		self.isbus.write('ISBUS', rpp_data)
		self.buscomp.write('BUSCOMP', rpp_data)
		self.showinmix.write('SHOWINMIX', rpp_data)
		self.fixedlanes.write('FIXEDLANES', rpp_data)
		self.sel.write('SEL',rpp_data)
		self.rec.write('REC', rpp_data)
		self.vu.write('VU',rpp_data)
		self.trackheight.write('TRACKHEIGHT', rpp_data)
		self.inq.write('INQ', rpp_data)
		self.nchan.write('NCHAN',rpp_data)
		self.fx.write('FX',rpp_data)
		self.trackid.write('TRACKID',rpp_data)
		self.perf.write('PERF',rpp_data)
		for r in self.auxrecv: r.write('AUXRECV', rpp_data)
		self.midiout.write('MIDIOUT',rpp_data)
		self.mainsend.write('MAINSEND', rpp_data)
		self.panenv2.write('PANENV2', rpp_data)
		self.volenv2.write('VOLENV2', rpp_data)
		self.muteenv.write('MUTEENV', rpp_data)
		if self.fxchain != None:
			rpp_fxchaindata = robj('FXCHAIN',[])
			self.fxchain.write(rpp_fxchaindata)
			rpp_data.children.append(rpp_fxchaindata)
		for item in self.items:
			rpp_itemdata = robj('ITEM',[])
			item.write(rpp_itemdata)
			rpp_data.children.append(rpp_itemdata)
