import numpy as np
import copy

# RSSI

def rssi_level(rssi):
    if rssi == "-":
        return "-"
    elif rssi < -120:
        return "TERRIBLE"
    elif rssi < -100:
        return "Poor"
    elif rssi < -80:
        return "Fair"
    elif rssi < -60:
        return "Good"
    elif rssi < -30:
        return "Excellent"
    else:
        return "SUPERB"
    
# SNR

def snr_level(snr):
    if snr == "-":
        return "-"
    elif snr > 10:
        return "EXCELLENT"
    elif snr > 5:
        return "Good"
    elif snr > 0:
        return "Fair"
    elif snr > -5:
        return "Weak"
    elif snr > -20:
        return "Very poor"
    else:
        return "TERRIBLE"

# Range - Uses Euclidean distance. Should adjust based on what format lat, long, height is given as. 

def range_between_nodes(lat1, lon1, alt1, lat2, lon2, alt2):
    return ((lat1-lat2) ** 2 + (lon1-lon2) ** 2 + (alt1-alt2) ** 2) ** 0.5

# Retrieve a whole dictionary except for 'raw' field

def remove_raw(dict):
    if dict.get('raw', None) != None:
        copied_dict = copy.deepcopy(dict)
        del copied_dict['raw']
        return copied_dict
    else:
        return dict
