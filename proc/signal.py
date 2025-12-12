import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class Signal:
    def __init__(self, name, time, data, dtype, zones=None, node_id=None):
        self.name=name
        self.time=time
        self.data=data
        self.dtype=dtype
        self.zones=zones
        self.step_size=self.time.iloc[1]-self.time.iloc[0]
        self.node_id=node_id
    
    def peak(self, t=None):
        if not t:
            val=self.data.abs().max()
            time_idx=self.data.abs().idxmax()
            return val, self.time.iloc[time_idx]
        trimmed=self.data[int(t[0]*1/self.step_size):int(t[1]*(1/self.step_size))]
        val=trimmed.abs.max()
        time_idx=trimmed.abs().idxmax()
        return val, self.time.iloc[time_idx]
    
    def rms(self):
        return np.sqrt(np.mean(self.data**2))

    def splot(self, ax=None, want_zones=False, alone=False, **kwargs):
        if ax==None:
            fig, ax=plt.subplots()
        
        ax.plot(self.time, self.data, label=self.name, **kwargs)

        if not want_zones or self.zones is None:
            ax.legend()
            ax.grid(True)
            return ax
        
        z=self.zones
        colors=['red', 'green', 'blue', 'orange']
        zone_labels=['K1', 'K2', 'Bump_Stop', 'Metal']

        for i in range(len(z)-1):
            ax.axhspan(z[i], z[i+1], color=colors[i], alpha=0.1,
                       label=zone_labels[i] if i<len(zone_labels) else None)

        ax.set_xlabel('Time (s)')
        ax.legend()
        ax.grid(True)
        if alone:
            plt.show()
            return 
        return ax