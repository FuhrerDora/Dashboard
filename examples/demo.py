from MBD.postprocess import PostProcess

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
curve_details=[('Front_travel', 'D', [0, 55, 85, 97]),
               ('Rear_travel', 'D', [0, 32, 70, 82])]
curve_details.extend(add_force_signal(fnames))
curve_details.append(('CG_AZ', 'A', None))

sim_info={'abf_path': r"F:\Yugal\python\tanupost.csv",
          'speed': 20, #kmph,
          'road_path': r"F:\Yugal\python\road.rdf",
          'wheelbase': 1350,    #mmyes
          'Road_origin_FWC_offset': 0}

tanu=PostProcess(sim_info)
tanu.read_abf(curve_details)
tanu.read_rdf()
tanu.Road_profile_FWC.splot(want_zones=False, alone=True)
plt.show()