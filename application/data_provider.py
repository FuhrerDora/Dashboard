"""
data_provider.py

Bridges PostProcess → Dash
NO Dash imports here
"""

from pathlib import Path
from proc import PostProcess
import numpy as np

# -------------------------------------------------
# Paths
# -------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

# -------------------------------------------------
# Helpers from your original script
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


# -------------------------------------------------
# Curve specification (UNCHANGED LOGIC)
# -------------------------------------------------
fnames = ['HT', 'SP', 'RSU']

curve_details = [
    ('Vehicle_speed', 'I', None),
    ('Front_travel', 'D', [0, 55, 85, 97]),
    ('Rear_travel', 'D', [0, 32, 70, 82]),
]

curve_details.extend(add_force_signal(fnames))
curve_details.append(('CG_AZ', 'A', None))
curve_details.extend([
    ('FWC_X', 'IP', None),
    ('FWC_Z', 'IP', None),
    ('RWC_X', 'IP', None),
    ('RWC_Z', 'IP', None),
])

# -------------------------------------------------
# sim_info builder  ✅ OPTION 1 FIX
# -------------------------------------------------
def build_sim_info(name):
    return {
        'name': name,   # 👈 THIS FIXES YOUR ERROR
        'abf_path': DATA / "bump_s400x80_20kph_double.csv",
        'speed': 20,
        'road_path': DATA / "bump_s400x80.rdf",
        'wheelbase': 1344,
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
# Run PostProcess (old script logic wrapped)
# -------------------------------------------------
def run_postprocess(sim_info):
    pp = PostProcess(sim_info)
    pp.read_abf(curve_details)
    pp.read_rdf()
    pp.wc_path()
    return pp

# -------------------------------------------------
# Build LH / RH plot rows from dtype_map
# -------------------------------------------------
def build_plots_from_dtype_map(dtype_map):

    plots = {}

    for dtype, signals in dtype_map.items():
        for sig in signals:

            plot_name = sig.name
            side = sig.side.upper()   # LH / RH

            if plot_name not in plots:
                plots[plot_name] = {
                    "LH": None,
                    "RH": None,
                    "metrics": {}
                }

            plots[plot_name][side] = sig

            # Example metrics (expand later)
            plots[plot_name]["metrics"][f"{side} RMS"] = f"{sig.rms:.2f}"
            plots[plot_name]["metrics"][f"{side} Peak"] = f"{sig.peak:.2f}"

    return plots

# -------------------------------------------------
# Build one OAE block
# -------------------------------------------------
def build_oae(oae_name):
    sim_info = build_sim_info(oae_name)
    pp = run_postprocess(sim_info)

    return {
        "summary": {
            "Name": sim_info["name"],
            "Speed": f"{sim_info['speed']} km/h",
            "Signals": len(pp.signals)
        },
        "plots": build_plots_from_dtype_map(pp.dtype_map)
    }

# -------------------------------------------------
# PUBLIC OBJECT USED BY DASH
# -------------------------------------------------
OAES = {
    "tanu": build_oae("tanu")
}
