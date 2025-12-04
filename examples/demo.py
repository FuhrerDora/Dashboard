import sys
import os
from pathlib import Path
from proc import PostProcess, Signal, Viz
from matplotlib import pyplot as plt
#& C:/Users/Karthik/AppData/Local/Programs/Python/Python313/python.exe -m examples.demo

ROOT= Path(__file__).resolve().parent.parent
data=ROOT/ 'data'

def add_force_signal(names):
    forces_temp=[('_FM', 'F', None), 
                ('_FX', 'F', None), 
                ('_FY', 'F', None),
                ('_FZ', 'F', None),
                ('_MM', 'M', None), 
                ('_MX', 'M', None), 
                ('_MY', 'M', None), 
                ('_MZ', 'M', None)]
    forces=[]
    for name in names:
        for suffix, dtype, zone in forces_temp:
            forces.append((name+suffix, dtype, zone))
    return forces

fnames=['HT', 'SP', 'RSU']
curve_details=[('Vehicle_speed', 'I', None),
               ('Front_travel', 'D', [0, 55, 85, 97]),
               ('Rear_travel', 'D', [0, 32, 70, 82])]
curve_details.extend(add_force_signal(fnames))
curve_details.append(('CG_AZ', 'A', None))
curve_details.extend([('FWC_X', 'I', None),
                      ('FWC_Z', 'I', None),
                      ('RWC_X', 'I', None),
                      ('RWC_Z', 'I', None)])

sim_info={'name': 'tanu',
          'abf_path': data/ "bump_s400x80_20kph_double.csv",
          'speed': 20, #kmph   
          'road_path': data/ "bump_s400x80.rdf",
          'wheelbase': 1344,    #mm
          'Road_origin_FWC_offset': 1631.1578,
          'time_step': 0.001,
          'trim': None}
        
tanu=PostProcess(sim_info)
tanu.read_abf(curve_details)
tanu.read_rdf()
dash1=Viz([tanu])
dash1.viz1(overlay=True)
#dash1.plot()