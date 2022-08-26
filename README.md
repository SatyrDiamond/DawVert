
## How to Use

### FLM to LMMS: 
```
python3 from_flm.py <flm project file> <output cvpj file>
python3 to_lmms.py <cvpj file> <lmms project output> 

e.g:
    python3 from_flm.py somesong.fml cvpjfile
    python3 to_lmms.py cvpjfile somesong.mmp
```

### MOD to LMMS: 
```
python3 from_trkr_mod.py <MOD Tracker Song> <output cvpjm file>
python3 cvpjm2cvpj_tracker.py <cvpjm file> <output cvpj file>
python3 to_lmms.py <cvpj file> <lmms project output> 

e.g:
    python3 from_trkr_mod.py somesong.mod cvpjmfile
    python3 cvpjm2cvpj_tracker.py cvpjmfile cvpjfile
    python3 to_lmms.py cvpjfile somesong.mmp
```

### S3M to LMMS: 
```
python3 from_trkr_s3m.py <StreamTracker3 Song> <output cvpjm file>
python3 cvpjm2cvpj_tracker.py <cvpjm file> <output cvpj file>
python3 to_lmms.py <cvpj file> <lmms project output> 

e.g:
    python3 from_trkr_s3m.py somesong.mod cvpjmfile
    python3 cvpjm2cvpj_tracker.py cvpjmfile cvpjfile
    python3 to_lmms.py cvpjfile somesong.mmp
```
