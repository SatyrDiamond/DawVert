
def decode(sysex_obj, bstream):
	devicename = 'universal'

	if sysex_obj.vendor.id == 126: 
		if sysex_obj.device == 127:
			sysex_obj.known = True
			sysex_obj.category = 'system'
			sysex_obj.param = 'gm_reset'

	if sysex_obj.vendor.id == 127: 
		if sysex_obj.model_id == 3:
			sysex_obj.known = True
			sysex_obj.category = 'notation'
			if sysex_obj.command == 1: sysex_obj.param = 'bar_number'
			if sysex_obj.command == 2: sysex_obj.param = 'time_signature_immediate'
			if sysex_obj.command == 66: sysex_obj.param = 'time_signature_delayed'
			sysex_obj.value = bstream.read()

		if sysex_obj.model_id == 4:
			sysex_obj.known = True
			sysex_obj.category = 'device'
			sysex_obj.value = bstream.read()
			if sysex_obj.command == 1: 
				sysex_obj.param = 'master_volume'
				sysex_obj.value = int.from_bytes(sysex_obj.value[0:2], 'big')
			if sysex_obj.command == 2: sysex_obj.param = 'master_pan'
			if sysex_obj.command == 3: sysex_obj.param = 'master_fune_tune'
			if sysex_obj.command == 4: sysex_obj.param = 'master_coarse_tuning'
			if sysex_obj.command == 5: sysex_obj.param = 'global_param_control'