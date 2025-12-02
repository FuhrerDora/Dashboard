import numpy as np
import pandas as pd
import scipy.interpolate as interp
from scipy.integrate import cumulative_trapezoid
import matplotlib.pyplot as plt
from .signal import Signal

class PostProcess:
    def __init__(self, sim_info=None):
        self.signals=[]
        self.signal_map={}
        self.abfp=sim_info['abf_path']
        self.roadp=sim_info['road_path']
        self.speed=sim_info['speed']/3.6  #m/s
        self.wheelbase=sim_info['wheelbase']
        self.front_offset=sim_info['Road_origin_FWC_offset']
        self.step_size=sim_info['time_step']
        self.trim=sim_info.get('trim', None)

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

        FWC_time_offset=-self.front_offset/(self.speed*1000)
        FWC_rows_offset=int(FWC_time_offset/self.step_size)
        RWC_time_offset=-(self.front_offset - self.wheelbase)/(self.speed*1000)
        RWC_rows_offset=int(RWC_time_offset/self.step_size)

        road=pd.DataFrame({'Time':vel_signal.time, 'Z':road_z})
        road['FWC']=road['Z'].shift(FWC_rows_offset, fill_value=road['Z'].iloc[0])
        road['RWC']=road['Z'].shift(RWC_rows_offset, fill_value=road['Z'].iloc[0])
        if isinstance(self.trim, (int, float)):
            road=road[road['Time']<self.trim]
        elif isinstance(self.trim, tuple):
            road=road[(road['Time']>self.trim[0]) & (road['Time']<self.trim[1])]
        else:
            print("Invalid trim parameter")

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
        for (name, dtype, zones), curve in zip(curve_details, curves_pp):
            #print(f"Loading signal: {name}")
            if not self.trim:
                print("No trim")
                self.add_signal(name, curve['Time'], curve['Y'], dtype, zones)
                num+=1
            else:    
                if isinstance(self.trim, (int, float)):
                    curve=curve[curve['Time']<self.trim]
                elif isinstance(self.trim, tuple):
                    curve=curve[(curve['Time']>self.trim[0]) & (curve['Time']<self.trim[1])]
                    self.add_signal(name, curve['Time'], curve['Y'], dtype, zones)
                    num+=1
                else:
                    print("Check_trim_inputs")
        print(f"Loaded {num} signals.")

    def plot(self, names=None, want_zones=True):
        if names is None:
            selected=self.signals
        else:
            selected=[s for s in self.signals if s.name in names]
            if not selected:
                print("No matching signals found.")
                return

        dtype_groups={}
        for sig in selected:
            dtype_groups.setdefault(sig.dtype, []).append(sig)

        n=0
        for dtype, sigs in dtype_groups.items():
            if dtype=='D':
                n+=len(sigs)
            else: 
                n+=1

        fig, axes=plt.subplots(n, 1, figsize=(12, 4*n), sharex=False)

        if n==1:
            axes=[axes]
        
        ax_index=0
        for dtype, sigs in dtype_groups.items():
            if dtype=='D':
                for sig in sigs:
                    ax=axes[ax_index]
                    sig.splot(ax=ax, want_zones=want_zones)
                    if sig.name=='Front_travel':
                        if self.roadp is not None:
                            self.RF.splot(ax=ax)
                    else: 
                        if self.roadp is not None:
                            self.RR.splot(ax=ax)
                    ax.legend()
                    ax_index+=1
            elif dtype in ['F', 'M', 'A']:
                continue
            elif dtype=='I':
                ax=axes[ax_index]
                for sig in sigs:
                    sig.splot(ax=ax, want_zones=want_zones)
                    
                ax.grid(True)
                ax.legend()
                ax_index+=1
        plt.tight_layout()
        plt.show()