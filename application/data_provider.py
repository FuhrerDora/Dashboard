from pathlib import Path
from proc import PostProcess

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


# -------------------------------
# sim_info
# -------------------------------
def build_sim_info(name, abf_file):
    return {
        "name": name,
        "abf_path": DATA / abf_file,
        "speed": 40.23,
        "road_path": DATA / "bump_s400x80.rdf",
        "wheelbase": 2935,
        "Road_origin_FWC_offset": 1631.1578,
        "time_step": 0.001,
        "trim": None,
        "rolling_radius": 10,
        "nodes": {
            "HT": [1, 10, 0, 10],
            "SP": [2, 10, 0, 10],
            "RSU": [3, 10, 0, 10],
        },
        "events": {
            "bump": [(0, 0.29), (0.3, 0.5)]
        }
    }


# -------------------------------
# run postprocess
# -------------------------------
def run_postprocess(sim_info, curve_details):
    pp = PostProcess(sim_info)
    pp.read_abf(curve_details)
    pp.read_rdf()
    pp.wc_path()
    return pp


# -------------------------------
# simulations
# -------------------------------
SIMS = {
    "ADAMS": run_postprocess(
        build_sim_info("ADAMS_CS100", "Adams_CS100_bus.csv"),
        curve_details=None   # you already define this above in your file
    ),
    "MV": run_postprocess(
        build_sim_info("MV_CS100", "MV_CS100_bus.csv"),
        curve_details=None
    )
}


# -------------------------------
# dtype-based OAES
# -------------------------------
def build_dtype_oaes(simulations):

    oaes = {}

    for sim_name, pp in simulations.items():
        for dtype, signals in pp.dtype_map.items():

            if dtype not in oaes:
                oaes[dtype] = {}

            for sig in signals:

                side = "LH" if sig.lat == "L" else "RH"
                axle = "Front" if sig.lon == "F" else "Rear"

                if sig.name not in oaes[dtype]:
                    oaes[dtype][sig.name] = {
                        "Front": {"LH": {}, "RH": {}},
                        "Rear":  {"LH": {}, "RH": {}},
                    }

                oaes[dtype][sig.name][axle][side][sim_name] = sig

    return oaes


# -------------------------------
# PUBLIC OBJECT
# -------------------------------
OAES = build_dtype_oaes(SIMS)
