import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd

class Viz:
    def __init__(self, pp_objects=list):
        self.sims=pp_objects
        self.all_signals=[]
        for sim in self.sims:
            self.all_signals.append(list(sim.signal_map.values()))
    
    def viz1(self, overlay=False):
        if len(self.sims)==0:
            print("No simulations to visualize.")
            return
        elif len(self.sims)==1:
            if not overlay:
                fig=go.Figure()
                for signal in self.all_signals[0]:
                    if signal.dtype=='D':
                        fig.add_trace(go.Scatter(x=signal.time, y=signal.data, mode='lines', name=signal.name))
            elif overlay:
                fig=make_subplots(rows=1, cols=2)
                fig.add_trace(go.Scatter(x=self.sims[0].RF.time, y=self.sims[0].RF.data, mode='lines', name=self.sims[0].RF.name), row=1, col=1)
                fig.add_trace(go.Scatter(x=self.sims[0].Front_travel.time, y=self.sims[0].Front_travel.data, mode='lines', name=self.sims[0].Front_travel.name), row=1, col=1)
                fig.add_trace(go.Scatter(x=self.sims[0].RR.time, y=self.sims[0].RR.data, mode='lines', name=self.sims[0].RR.name), row=1, col=2)
                fig.add_trace(go.Scatter(x=self.sims[0].Rear_travel.time, y=self.sims[0].Rear_travel.data, mode='lines', name=self.sims[0].Rear_travel.name), row=1, col=2)
        else:
            fig=make_subplots(rows=len(self.sims), cols=2)
            sim_idx=1   #plotly is 1 indexed
            if not overlay:
                for sim in self.sims:
                    fig.add_trace(go.Scatter(x=sim.Front_travel.time, y=sim.Front_travel.data, mode='lines', name=sim.name+'_Front_travel'), row=sim_idx, col=1)
                    fig.add_trace(go.Scatter(x=sim.Rear_travel.time, y=sim.Rear_travel.data, mode='lines', name=sim.name+'_Rear_travel'), row=sim_idx, col=2)
                    sim_idx+=1
            elif overlay:
                for sim in self.sims:
                    fig.add_trace(go.Scatter(x=sim.RF.time, y=sim.RF.data, mode='lines', name=sim.name+'_RF'), row=sim_idx, col=1)
                    fig.add_trace(go.Scatter(x=sim.Front_travel.time, y=sim.Front_travel.data, mode='lines', name=sim.name+'_Front_travel'), row=sim_idx, col=1)
                    fig.add_trace(go.Scatter(x=sim.RR.time, y=sim.RR.data, mode='lines', name=sim.name+'_RR'), row=sim_idx, col=2)
                    fig.add_trace(go.Scatter(x=sim.Rear_travel.time, y=sim.Rear_travel.data, mode='lines', name=sim.name+'_Rear_travel'), row=sim_idx, col=2)
                    sim_idx+=1
        fig.update_layout(height=600*len(self.sims), width=1000, title_text="Displacement_Only")
        fig.show()

    def plot(self, signals=None):   #unstable
        if signals is None:
            print('No signals provided, plotting by dtype')
            max_num_dtypes=-1
            for sim in self.sims:
                max_num_dtypes=max(max_num_dtypes, len(list(sim.dtype_map.keys())))
            fig=make_subplots(rows=max_num_dtypes, cols=1)
            for sim in self.sims:
                dtype_idx=1
                for sigs in sim.dtype_map.values():
                    for sig in sigs:
                        fig.add_trace(go.Scatter(x=sig.time, y=sig.data, mode='lines', name=sim.name+'_'+sig.name), row=dtype_idx, col=1)
                    dtype_idx+=1
            fig.show()
            return
        else:
            fig=make_subplots(rows=len(signals), cols=1)
            sig_idx=1   #plotly is 1 indexed
            for name in signals:
                for sim in self.sims:
                    cur=next(sig for sig in sim.signal_map.values() if sig.name==name)
                    fig.add_trace(go.Scatter(x=cur.time, y=cur.data, mode='lines', name=sim.name+'_'+cur.name), row=sig_idx, col=1)
                sig_idx+=1
            fig.show()

