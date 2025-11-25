import numpy as np
import pandas as pd
import scipy.interpolate as interp
import matplotlib.pyplot as plt

class PostProcess:
    def __init__(self, sim_info=None):
        self.signals=[]
        self.signal_map={}
        self.abfp=sim_info['abf_path']
        self.roadp=sim_info['road_path']
        self.speed=sim_info['speed']/3.6  #m/s
        self.wheelbase=sim_info['wheelbase']
        self.front_offset=sim_info['Road_origin_FWC_offset']


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
        road_signal_t=[]
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

            road_signal_t.append((x/1000)/self.speed) 
            road_signal_z.append(z)
        if not road_signal_t:
            raise ValueError("No valid road data found in RDF file.")
        
        time_domain_road=pd.DataFrame({'Time':road_signal_t, 'Z':road_signal_z})

        road_interp=interp.interp1d(time_domain_road['Time'], time_domain_road['Z'], kind='nearest', fill_value='extrapolate', bounds_error=False)
        road_f=road_interp((time_domain_road['Time'] + self.front_offset/(self.speed*1000)))
        road_r=road_interp((time_domain_road['Time'] + (self.front_offset - self.wheelbase)/(self.speed*1000)))
        self.add_signal('Road_profile_FWC', time_domain_road['Time'], road_f, 'R', None)
        self.add_signal('Road_profile_RWC', time_domain_road['Time'], road_r, 'R', None)
        self.add_signal('Road_profile', time_domain_road['Time'], time_domain_road['Z'], 'R', None)
        print('Road profiles loaded')
                
    def add_signal(self, name, time, data, dtype, zones=None):
        if dtype=='D':
            data=data*-1
        sig=Signal(name, time, data, dtype, zones)
        self.signals.append(sig)
        self.signal_map[name]=sig
    
    def __getattr__(self, item):
        if item in self.signal_map:
            return self.signal_map[item]
        raise AttributeError(f"'PostProcess' object has no attribute '{item}'")

    def read_abf(self, curve_details, trim=0.3):
        df=pd.read_csv(self.abfp, header=None, skip_blank_lines=False, names=['Time', 'Y'])
        df['curve_id']=df['Time'].isna().cumsum()
        df=df.dropna().reset_index(drop=True)
        curves_pp=[g.reset_index(drop=True) for _, g in df.groupby('curve_id')]     #curves_pp is a list of dataframes
        num=0
        for (name, dtype, zones), curve in zip(curve_details, curves_pp):
            if isinstance(trim, (int, float)):
                curve=curve[curve['Time']<trim]
            elif isinstance(trim, tuple):
                curve=curve[(curve['Time']>trim[0]) & (curve['Time']<trim[1])]
            self.add_signal(name, curve['Time'], curve['Y'], dtype, zones)
            num+=1
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
                        self.Road_profile_FWC.splot(ax=ax)
                    else: self.Road_profile_RWC.splot(ax=ax)
                    ax.legend()
                    ax_index+=1
            elif dtype=='R':
                continue
            else:
                ax=axes[ax_index]
                for sig in sigs:
                    sig.splot(ax=ax, want_zones=want_zones)
                    
                ax.grid(True)
                ax.legend()
                ax_index+=1
        plt.tight_layout()
        plt.show()