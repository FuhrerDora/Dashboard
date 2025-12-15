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
        self.zone_colors=['green', 'yellow', 'red']
    
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
                fig.add_trace(go.Scatter(x=self.sims[0].Front_travel.time, y=self.sims[0].Front_travel.data, mode='lines', name=self.sims[0].FWC_path.name), row=1, col=1)
                fig.add_trace(go.Scatter(x=self.sims[0].RR.time, y=self.sims[0].RR.data, mode='lines', name=self.sims[0].RR.name), row=1, col=2)
                fig.add_trace(go.Scatter(x=self.sims[0].Rear_travel.time, y=self.sims[0].Rear_travel.data, mode='lines', name=self.sims[0].RWC_path.name), row=1, col=2)
                y0=0
                for i in range(3):
                    fig.add_shape(type='rect', xref='x', yref='y',
                                    x0=0, x1=self.sims[0].Front_travel.time.iloc[-1],
                                    y0=y0, y1=y0+1,
                                    fillcolor=self.zone_colors[i], opacity=0.15, layer='below')
                    
                    fig.add_shape(type='rect', xref='x2', yref='y2',
                                    x0=0, x1=self.sims[0].Front_travel.time.iloc[-1],
                                    y0=y0, y1=y0+1,
                                    fillcolor=self.zone_colors[i], opacity=0.15, layer='below')
                    y0+=1

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
        fig.update_layout(height=600*len(self.sims), width=2000, title_text="Displacement_Only")
        fig.show()

    def plot(self, signals=None, dtypes=None):   #unstable
        exclude_dtypes=['IP']
        if signals is None and dtypes is None:
            print('No signals provided, plotting by dtype')
            max_num_dtypes=-1
            for sim in self.sims:
                max_num_dtypes=max(max_num_dtypes, len(list(sim.dtype_map.keys()))-len(exclude_dtypes))
            fig=make_subplots(rows=max_num_dtypes, cols=2, subplot_titles=['Inputs', 'Moments', 'Displacement', 'Accelerations', 'Road', 'Forces'])
            for sim in self.sims:
                dtype_idx=1
                for dt, sigs in sim.dtype_map.items():
                    if dtype_idx>3:
                        dtype_idx=1
                    if dt in exclude_dtypes:
                        dtype_idx-=1
                    else:
                        if dt in ['D', 'I', 'R']:
                            col_idx=1
                        else: col_idx=2
                        for sig in sigs:
                            fig.add_trace(go.Scatter(x=sig.time, y=sig.data, mode='lines', name=sim.name+'_'+sig.name), row=dtype_idx, col=col_idx)
                    dtype_idx+=1
            fig.update_layout(height=300*max_num_dtypes, width=1800, title_text="Signals by Dtype")
            fig.show()
            return
        elif signals and dtypes is None:
            fig=make_subplots(rows=len(signals), cols=1)
            sig_idx=1   #plotly is 1 indexed
            for name in signals:
                for sim in self.sims:
                    cur=next(sig for sig in sim.signal_map.values() if sig.name==name)
                    fig.add_trace(go.Scatter(x=cur.time, y=cur.data, mode='lines', name=sim.name+'_'+cur.name), row=sig_idx, col=1)
                sig_idx+=1
            fig.show()
        elif dtypes and signals is None:
            fig=make_subplots(rows=len(dtypes), cols=1)
            dtype_idx=1   #plotly is 1 indexed
            for dt in dtypes:
                for sim in self.sims:
                    cur_sigs=sim.dtype_map.get(dt, [])
                    for cur in cur_sigs:
                        fig.add_trace(go.Scatter(x=cur.time, y=cur.data, mode='lines', name=sim.name+'_'+cur.name), row=dtype_idx, col=1)
                dtype_idx+=1
            fig.show()
        else:
            raise ValueError("Provide either signals or dtypes, not both.")
        
    def viz2(self, moments=False, ignore_y_component=True):
        if ignore_y_component:
            rows=3
        else: rows=4
        if moments:
            fig=make_subplots(rows=rows, cols=2, subplot_titles=['FM', 'MM', 'FX', 'MX', 'FZ', 'MZ', 'FY', 'MY'])
            fig.update_layout(height=1200, width=1000, title_text="Forces and Moments")
        else:
            fig=make_subplots(rows=rows, cols=1, subplot_titles=['FM', 'FX', 'FZ', 'FY']) 
            fig.update_layout(height=900, width=1600, title_text="Forces")
        for sim in self.sims:
            for sig in sim.dtype_map.get('F'):
                if sig.name.endswith('_FM'): 
                    fig.add_trace(go.Scatter(x=sig.time, y=sig.data, mode='lines', name=sim.name+'_'+sig.name), row=1, col=1)
                elif sig.name.endswith('_FX'):
                    fig.add_trace(go.Scatter(x=sig.time, y=sig.data, mode='lines', name=sim.name+'_'+sig.name), row=2, col=1)
                elif sig.name.endswith('_FY') and not ignore_y_component:
                    fig.add_trace(go.Scatter(x=sig.time, y=sig.data, mode='lines', name=sim.name+'_'+sig.name), row=4, col=1)
                elif sig.name.endswith('_FZ'):
                    fig.add_trace(go.Scatter(x=sig.time, y=sig.data, mode='lines', name=sim.name+'_'+sig.name), row=3, col=1)
            if moments:
                for sig in sim.dtype_map.get('M'):
                    if sig.name.endswith('_MM'): 
                        fig.add_trace(go.Scatter(x=sig.time, y=sig.data, mode='lines', name=sim.name+'_'+sig.name), row=1, col=2)
                    elif sig.name.endswith('_MX'):
                        fig.add_trace(go.Scatter(x=sig.time, y=sig.data, mode='lines', name=sim.name+'_'+sig.name), row=2, col=2)
                    elif sig.name.endswith('_MY') and not ignore_y_component:
                        fig.add_trace(go.Scatter(x=sig.time, y=sig.data, mode='lines', name=sim.name+'_'+sig.name), row=4, col=2)
                    elif sig.name.endswith('_MZ'):
                        fig.add_trace(go.Scatter(x=sig.time, y=sig.data, mode='lines', name=sim.name+'_'+sig.name), row=3, col=2)
                    row_idx+=1
        fig.show()              

    def viz3(self, overlay=False):
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
                fig.add_trace(go.Scatter(x=self.sims[0].FWC_path.time, y=self.sims[0].FWC_path.data, mode='lines', name=self.sims[0].FWC_path.name), row=1, col=1)
                fig.add_trace(go.Scatter(x=self.sims[0].RR.time, y=self.sims[0].RR.data, mode='lines', name=self.sims[0].RR.name), row=1, col=2)
                fig.add_trace(go.Scatter(x=self.sims[0].RWC_path.time, y=self.sims[0].RWC_path.data, mode='lines', name=self.sims[0].RWC_path.name), row=1, col=2)
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
        fig.update_layout(height=600*len(self.sims), width=2000, title_text="Displacement_Only")
        fig.show()
    

