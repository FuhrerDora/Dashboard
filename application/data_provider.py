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

SIMS = {
    "ADAMS": run_postprocess(
        build_sim_info("ADAMS_CS100", "Adams_CS100_bus.csv")
    ),
    "MV": run_postprocess(
        build_sim_info("MV_CS100", "MV_CS100_bus.csv")
    )
}

# -------------------------------------------------
# Build dtype-based OAEs with overlay support
# -------------------------------------------------
def build_dtype_oaes(simulations):
    """
    Returns:
    OAES[dtype][signal_name][axle][side][sim_name] = Signal
    """

    oaes = defaultdict(
        lambda: defaultdict(
            lambda: {
                "Front": {"LH": {}, "RH": {}},
                "Rear":  {"LH": {}, "RH": {}},
            }
        )
    )

    for sim_name, pp in simulations.items():
        for dtype, signals in pp.dtype_map.items():
            for sig in signals:

                signal_name = sig.name
                side = "LH" if sig.side == "L" else "RH"
                axle = "Front" if sig.axle == "F" else "Rear"

                oaes[dtype][signal_name][axle][side][sim_name] = sig

    return oaes

# -------------------------------------------------
# PUBLIC: dtype-based OAEs
# -------------------------------------------------
OAES = build_dtype_oaes(SIMS)