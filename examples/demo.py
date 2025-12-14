import sys
import os
from pathlib import Path
from proc import PostProcess, Signal, Viz
from matplotlib import pyplot as plt
#& C:/Users/Karthik/AppData/Local/Programs/Python/Python313/python.exe -m examples.demo

ROOT= Path(__file__).resolve().parent.parent
data=ROOT/ 'data'

def add_force_signal(names):
    forces_temp=[('_FM', 'F'), 
                ('_FX', 'F'), 
                ('_FY', 'F'),
                ('_FZ', 'F'),
                ('_MM', 'M'), 
                ('_MX', 'M'), 
                ('_MY', 'M'), 
                ('_MZ', 'M')]
    forces=[]
    id=1
    for name in names:
        for suffix, dtype in forces_temp:
            forces.append((name+suffix, dtype, id))
        id+=1
    return forces

fnames=['HT', 'SP', 'RSU']      #Must be in ascending node_id order
curve_details=[('Vehicle_speed', 'I', None),
               ('Front_travel', 'D', [0, 55, 85, 97]),
               ('Rear_travel', 'D', [0, 32, 70, 82])]
curve_details.extend(add_force_signal(fnames))
curve_details.append(('CG_AZ', 'A', None))
curve_details.extend([('FWC_X', 'IP', None),
                      ('FWC_Z', 'IP', None),
                      ('RWC_X', 'IP', None),
                      ('RWC_Z', 'IP', None)])

sim_info={'name': 'tanu',
          'abf_path': data/ "bump_s400x80_20kph_double.csv",
          'speed': 20, #kmph   
          'road_path': data/ "bump_s400x80.rdf",
          'wheelbase': 1344,    #mm
          'Road_origin_FWC_offset': 1631.1578,
          'time_step': 0.001,
          'trim': None,
          'rolling_radius': 10,
          'nodes': {'HT': [1, 10, 0, 10],   #id, x, y, z
                   'SP': [2, 10, 0, 10],
                   'RSU':[3, 10, 0, 10]},
          'events': {'bump': [(0, 0.29), (0.3, 0.5)]}}  #start, end. f. r.
        
tanu=PostProcess(sim_info)
tanu.read_abf(curve_details)
tanu.read_rdf()
tanu.wc_path()
dash1=Viz([tanu])
#dash1.viz1(overlay=True)
#dash1.viz2()
#dash1.plot(signals=['FWC_path', 'RR', 'Road_profile'])
tanu.loads_export(name='test')
