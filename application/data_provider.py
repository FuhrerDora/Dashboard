"""
data_provider.py

Adapts PostProcess + rich Signal metadata
into a Dash-ready OAE structure.
"""

from pathlib import Path
from proc import PostProcess
from collections import defaultdict
import numpy as np

# -------------------------------------------------
# Paths
# -------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

# -------------------------------------------------
# Curve specification (UNCHANGED from demo)
# -------------------------------------------------
def add_force_signal(names):
    forces_temp = [
        ('_FM', 'F'), ('_FX', 'F'), ('_FY', 'F'), ('_FZ', 'F'),
        ('_MM', 'M'), ('_MX', 'M'), ('_MY', 'M'), ('_MZ', 'M')
    ]
    forces = []
    id = 1
    for name in names:
        for suffix, dtype in forces_temp:
            forces.append((name + suffix, dtype, id))
        id += 1
    return forces


curve_details = [
    ('Spring_length', 'D', 'L', 'F', None),
    ('Spring_length', 'D', 'R', 'F', None),
    ('Spring_length', 'D', 'L', 'R', None),
    ('Spring_length', 'D', 'R', 'R', None),

    ('FL_FX', 'F', 'L', 'F'),
    ('FR_FX', 'F', 'R', 'F'),
    ('RL_FX', 'F', 'L', 'R'),
    ('RR_FX', 'F', 'R', 'R'),
]

# -------------------------------------------------
# sim_info builder (Option 1 – contract preserved)
# -------------------------------------------------
def build_sim_info(name, abf_file):
    return {
        'name': name,
        'abf_path': DATA / abf_file,
        'speed': 40.23,
        'road_path': DATA / "bump_s400x80.rdf",
        'wheelbase': 2935,
        'Road_origin_FWC_offset': 1631.1578,
        'time_step': 0.001,
        'trim': None,
        'rolling_radius': 10,
        'nodes': {
            'HT': [1, 10, 0, 10],
            'SP': [2, 10, 0, 10],
            'RSU': [3, 10, 0, 10],
        },
        'events': {
            'bump': [(0, 0.29), (0.3, 0.5)]
        }
    }

# -------------------------------------------------
# Run PostProcess (unchanged logic)
# -------------------------------------------------
def run_postprocess(sim_info):
    pp = PostProcess(sim_info)
    pp.read_abf(curve_details)
    pp.read_rdf()
    pp.wc_path()
    return pp

# -------------------------------------------------
# Metrics (expand later)
# -------------------------------------------------
def compute_metrics(signal):
    return {
        "RMS": f"{np.sqrt(np.mean(signal.data**2)):.3f}",
        "Peak": f"{np.max(np.abs(signal.data)):.3f}"
    }

# -------------------------------------------------
# Core grouping logic (THIS IS THE KEY PART)
# -------------------------------------------------
def build_plots_from_signals(signals):
    """
    Groups signals into:
    plot_type → axle → LH/RH
    """

    plots = defaultdict(lambda: {
        "Front": {"LH": None, "RH": None},
        "Rear": {"LH": None, "RH": None},
        "metrics": defaultdict(dict)
    })

    for sig in signals:
        plot_name = sig.name
        side = "LH" if sig.side == "L" else "RH"
        axle = "Front" if sig.axle == "F" else "Rear"

        plots[plot_name][axle][side] = sig

        for k, v in compute_metrics(sig).items():
            plots[plot_name]["metrics"][axle][f"{side} {k}"] = v

    return plots

# -------------------------------------------------
# Build one OAE block
# -------------------------------------------------
def build_oae(name, abf_file):
    sim_info = build_sim_info(name, abf_file)
    pp = run_postprocess(sim_info)

    return {
        "summary": {
            "Name": name,
            "Speed": f"{sim_info['speed']} km/h",
            "Signals": len(pp.signals)
        },
        "plots": build_plots_from_signals(pp.signals)
    }

# -------------------------------------------------
# PUBLIC: OAES consumed by Dash
# -------------------------------------------------
OAES = {
    "Adams_CS100": build_oae("Adams_CS100", "Adams_CS100_bus.csv"),
    "MV_CS100": build_oae("MV_CS100", "MV_CS100_bus.csv"),
}
