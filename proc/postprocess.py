import numpy as np
import pandas as pd
import scipy.interpolate as interp
from scipy.integrate import cumulative_trapezoid
import matplotlib.pyplot as plt
from .signal import Signal
import os

class PostProcess:
    def __init__(self, sim_info=None):
        self.name=sim_info['name']
        self.signals=[]
        self.signal_map={}
        self.abfp=sim_info['abf_path']
        self.roadp=sim_info['road_path']
        self.speed=sim_info['speed']/3.6  #m/s
        self.wheelbase=sim_info['wheelbase']
        self.front_offset=sim_info['Road_origin_FWC_offset']
        self.step_size=sim_info['time_step']
        self.trim=sim_info.get('trim', None)
        self.rolling_radius=sim_info['rolling_radius']
        self.dtype_map={}
        self.nodes=sim_info['nodes']
        self.events=sim_info['events']

        FWC_time_offset=-self.front_offset/(self.speed*1000)
        RWC_time_offset=-(self.front_offset - self.wheelbase)/(self.speed*1000)
        self.FWC_rows_offset=int(FWC_time_offset/self.step_size)
        self.RWC_rows_offset=int(RWC_time_offset/self.step_size)

    def time_resample(self, array):  #first column of input array should be in time domain      CHECK UNSTABLE
        new=array[:, 1:]
        v=self.signal_map.get('Vehicle_speed', None)
        new_t=v.time
        c=0
        for i, t in enumerate(array[:, 0]):
            if new_t[c]>t:
                raise ValueError("Time value out of bounds in time_resample")
            while v.time[c]<t:
                new=np.vstack((new[:i+1], new[i], new[i+1:]))
                c+=1
        new.insert(0, 'Time', new_t)
        return new
                
    def wc_path(self):
        vel_signal=self.signal_map.get('Vehicle_speed', None)
        if vel_signal is None:
            raise ValueError("Vehicle_speed signal not found.")
        dist=cumulative_trapezoid(vel_signal.data, vel_signal.time, initial=0)
        dist_table=np.column_stack([vel_signal.time, dist])
        dist_df=pd.DataFrame(dist_table)
        dist_df['fdist']=dist_df[1].shift(self.FWC_rows_offset, fill_value=0)
        dist_df['rdist']=dist_df[1].shift(self.RWC_rows_offset, fill_value=0)


        dist_f=dist+self.front_offset+self.signal_map['FWC_X'].data
        dist_r=dist+self.front_offset - self.wheelbase + self.signal_map['RWC_X'].data

        fwc_xz=np.column_stack([dist_f, self.signal_map['FWC_Z'].data + self.rolling_radius])
        rwc_xz=np.column_stack([dist_r, self.signal_map['RWC_Z'].data + self.rolling_radius])

        tf=[]
        tr=[]
        for i in range(len(fwc_xz)):
            f_idx=np.abs(dist_df['fdist']-fwc_xz[i, 0]).argmin()
            r_idx=np.abs(dist_df['rdist']-rwc_xz[i, 0]).argmin()
            tf.append(self.signal_map['RF'].time[f_idx])
            tr.append(self.signal_map['RR'].time[r_idx])
        
        tf = np.array(tf).reshape(-1, 1)   # shape (N,1)
        tr = np.array(tr).reshape(-1, 1)   # shape (N,1)

        fwc_txz=np.hstack((tf, fwc_xz))
        rwc_txz=np.hstack((tr, rwc_xz))

        self.add_signal('FWC_path', fwc_txz[:, 0], fwc_txz[:, 2]-fwc_txz[0, 2]+self.rolling_radius, 'P', None)
        self.add_signal('RWC_path', rwc_txz[:, 0], rwc_txz[:, 2]-rwc_txz[0, 2]+self.rolling_radius, 'P', None)
        print('Wheel center paths loaded')


    def read_rdf(self):
        if self.roadp is None:
            return 'No road file path provided.'
        with open(self.roadp, 'r') as f:
            text=f.readlines()
            data_start=None
        for i , line in enumerate(text):
            if '(XZ_DATA)' in line:
                data_start=i+2
                break
        if data_start is None:
            raise ValueError("No XZ_DATA found in RDF file.")
        road_signal_x=[]
        road_signal_z=[]
        for line in text[data_start:]:
            parts=line.strip().split()
            if len(parts)<2:
                continue
            try:
                x=float(parts[0])
                z=float(parts[1])
            except ValueError:
                continue
            road_signal_x.append(x)
            road_signal_z.append(z)

        vel_signal=self.signal_map.get('Vehicle_speed', None)
        if vel_signal is None:
            raise ValueError("Vehicle_speed signal not found.")
        dist=cumulative_trapezoid(vel_signal.data, vel_signal.time, initial=0)
            
        
        if not road_signal_x:
            raise ValueError("No valid road data found in RDF file.")
        
        road_raw=pd.DataFrame({'X':road_signal_x, 'Z':road_signal_z})

        c = 0
        road_z=[]
        for i in range(len(vel_signal.time)):
            while c<len(road_raw['X'])-1 and road_raw['X'][c]<dist[i]:
                c+=1
            road_z.append(road_raw['Z'][c])

        road=pd.DataFrame({'Time':vel_signal.time, 'Z':road_z})
        road['FWC']=road['Z'].shift(self.FWC_rows_offset, fill_value=road['Z'].iloc[0])
        road['RWC']=road['Z'].shift(self.RWC_rows_offset, fill_value=road['Z'].iloc[0])
        if not self.trim:
            print('No road trimming')
            pass
        if isinstance(self.trim, (int, float)):
            road=road[road['Time']<self.trim]
        elif isinstance(self.trim, tuple):
            road=road[(road['Time']>self.trim[0]) & (road['Time']<self.trim[1])]

        self.add_signal('RF', road['Time'], road['FWC'], 'R', None)
        self.add_signal('RR', road['Time'], road['RWC'], 'R', None)
        self.add_signal('Road_profile', road['Time'], road['Z'], 'R', None)
        print('Road profiles loaded')
        
    def add_signal(self, name, time, data, dtype, zones=None):
        if dtype=='D':
            data=data*-1
        sig=Signal(name, time, data, dtype, zones)
        self.signals.append(sig)
        self.signal_map[name]=sig
        self.dtype_map.setdefault(sig.dtype, []).append(sig)


    def __getattr__(self, item):
        if "signal_map" in self.__dict__ and item in self.signal_map:
            return self.signal_map[item]
        raise AttributeError(f"'PostProcess' object has no attribute '{item}'")

    def read_abf(self, curve_details):
        df=pd.read_csv(self.abfp, header=None, skip_blank_lines=False, names=['Time', 'Y'])
        #print(f"Curve data types: {df.dtypes}")
        df['curve_id']=df['Time'].isna().cumsum()
        df=df.dropna().reset_index(drop=True)
        curves_pp=[g.reset_index(drop=True) for _, g in df.groupby('curve_id')]     #curves_pp is a list of dataframes
        num=0
        for (name, dtype, meta), curve in zip(curve_details, curves_pp):
            #print(f"Loading signal: {name}")
            if not self.trim:
                if dtype in ['F', 'M']:
                    self.add_signal(name, curve['Time'], curve['Y'], dtype, node_id=meta)
                else:
                    self.add_signal(name, curve['Time'], curve['Y'], dtype, zones=meta)
                num+=1
            else:    
                if isinstance(self.trim, (int, float)):
                    curve=curve[curve['Time']<self.trim]
                elif isinstance(self.trim, tuple):
                    curve=curve[(curve['Time']>self.trim[0]) & (curve['Time']<self.trim[1])]
                    num+=1
                if dtype in ['F', 'M']:
                    self.add_signal(name, curve['Time'], curve['Y'], dtype, node_id=meta)
                else:
                    self.add_signal(name, curve['Time'], curve['Y'], dtype, zones=meta)
        print(f"Loaded {num} signals.")

    def loads_extract(self, use_FM=True):
        with open('temp/load_block.txt', 'w') as f:
            if use_FM:
                loadcase=1
                for event, t_unpack in self.events.items():
                    tf, tr=t_unpack
                    where='Front'
                    for i in range(t_unpack):
                        f.write(f'$ Load Case = {event} {where}')
                        if where=='Front':
                            ref_sig=self.signal_map['HT_FM']
                        else:
                            ref_sig=self.signal_map['RS_FM']
                        time=ref_sig.peak(t=tf if where=='Front' else tr)
                        f.write(f'$ Time Step = {time}')
                        for key in self.dtype_map.keys():
                            sigs=[]
                            if key in ['F', 'M']:
                                sigs.extend(self.dtype_map[key])
                        cur_node=1
                        for sig in sigs:
                            if sig.node_id is None:
                                raise ValueError(f'node id is none for signal: {sig.name}')
                            elif sig.node_id==cur_node:
                                f.write(sig.name, sig.dtype)
                                cur_node+=1
                    

    def load_export(self, name='default'):
        loads=self.loads_extract()
        with open('data/'+name, 'w') as f:
            f.write('''$===================================================
 $GENERAL INFORMATION: 
 $    User Name = Yugal
 $    Time = Fri Dec 16 15:07:22 IST 2022
 $    MotionView Version = 2022.0.0.33
 $    MotionView Model File Name = event_pave_40kmph_2R.mdl
 $    Plot File Name = event_pave_40kmph_2R.plt
 $    Units = NEWTON/MILLIMETER/KILOGRAM/SECOND
 $===================================================
 $
 $
$=============Beginning of GRID cards===============
$
                  ''')
            
            for name, values in self.nodes.items():
                for id, x, y, z in values:
                    f.write(f'$ {name}')
                    f.write(f'GRID,       {id}, ,   {x},      {y},   {z}')
                    f.write('$')

            f.write('''$================End of GRID cards==================
$
$
$=========Beginning FORCE and MOMENT cards==========
$''')

            for event in len(self.loads.keys()):
                f.write()

        os.startfile

