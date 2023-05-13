# SPDX-FileCopyrightText: 2023 B0ney
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import plugin_input

from typing import Optional, Dict
from functions import container_umx as umx

from plugin_input.mi_tracker_s3m import input_s3m as s3m
from plugin_input.mi_tracker_mod import input_mod as mod
from plugin_input.mi_tracker_it import input_it as it
from plugin_input.mi_tracker_xm import input_xm as xm

TRACKER_FORMATS = [
    s3m(),
    it(),
    xm(),
    # mod() # mod does not support autodetect
]

class imput_umx(plugin_input.base):
    def is_dawvert_plugin(self) -> str: 
        return 'input'
    
    def getshortname(self) -> str: 
        return 'umx'
    
    def getname(self) -> str: 
        return 'Unreal Package Container'
    
    def gettype(self) -> str: 
        return 'm'
    
    def getdawcapabilities(self) -> Dict[str, bool]: 
        return { 'r_track_lanes': True }
    
    def supported_autodetect(self) -> bool: 
        return True
    
    def detect(self, input_file: str) -> bool:
        return umx.is_umx(open(input_file, 'rb'))
    
    def parse(self, input_file: str, extra_param=None) -> Optional[str]:
        filename = os.path.splitext(os.path.basename(input_file))[0]

        # Filename of stripped umx file
        # stripped_umx = f"temp_{filename}_{random.randint(2**12, 2**32)}"
        stripped_umx = filename

        # Successfully validated and stripped umx files will return a UMXInfo class
        # which contains basic metadata about the contained tracker.
        try:
            stripped = umx.strip_umx(input_file, stripped_umx)

            if stripped is None:
                return None
            
        except Exception as error:
            print(f"[error] { error }")
            return None    
        
        # Store the parsed cvpj json, because we need to 
        # remove the temporary file before returning it
        result = None

        try:
            # Using UMXInfo.hint() can be misleading, so iterate through a list of trackers
            # and only parse with that tracker if it's a valid format. 
            for tracker in TRACKER_FORMATS:
                if tracker.detect(stripped_umx):
                    print(f"[info] Detected format: { tracker.getname() }")
                    result = tracker.parse(stripped_umx, extra_param=extra_param)
            
            # An edge case where MOD files don't have the "detect" method.
            # In this circumstance, we can assume that valid UMX files will store a valid MOD file.
            if result is None:
                result = mod().parse(stripped_umx, extra_param=extra_param)

        finally:
            # Remove the stripped umx file
            os.remove(stripped_umx)     
            
        return result
