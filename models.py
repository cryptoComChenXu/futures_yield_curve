import os, sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Tuple, List, Dict
import bisect

def calc_prc(spot: float, yld: float, ttm: float) -> float:
    return np.exp(yld * ttm) * spot

def linear_interpolation(
    timestamp: str,
    expiration: str,
    contracts: List[str],
    yields: List[float],
    ttms: List[float]) -> Tuple[float, float]:

    if not len(yields) > 0 or not len(ttms) > 0 :
        print("Empty data!")
        return 0, 0

    if not len(yields) == len(ttms) == len(contracts):
        print("Wrong data!")
        return 0, 0


    # print(f"Current time: {timestamp}")
    # print(f"Expiration time: {expiration}")
    # print("Contracts: ", contracts)
    # print("TTMs: ", ttms)
    # print("Yields: ", yields)

    deltaT = pd.to_datetime(expiration) - pd.to_datetime(timestamp)
    ttm = (deltaT.days * SECONDS_IN_A_DAY + deltaT.seconds) / (365 * SECONDS_IN_A_DAY)

    i = bisect.bisect_left(ttms, ttm)
    if 0 < i < len(yields):
        print(f"Using contracts: {contracts[i - 1]} {contracts[i]}")
        x1, y1 = ttms[i - 1], yields[i - 1]
        x2, y2 = ttms[i], yields[i]
    elif i == 0:
        print(f"Using spot and contracts {contracts[i]}")
        x1, y1 = 0, 0
        x2, y2 = ttms[i], yields[i]
    elif i == len(yields):
        print(f"Using contracts: {contracts[i - 2]} {contracts[i - 1]}")
        x1, y1 = 0, 0
        if i > 1:
            x1, y1 = ttms[i - 2], yields[i - 2]
            x2, y2 = ttms[i - 1], yields[i - 1]
    else:
        print(f"Invalid futures yield curve, i = {i}")
        return 0, 0

    try:
        slope = (y2 - y1) / (x2 - x1)
        y = y1 + (ttm - x1) * slope
    except Exception as e:
        print(f"Couldn't do interpolation using x1={x1}, y1={y1}, x2={x2}, y2={y2}")
        
    print(f"y1={y1}, y={y}, y2={y2}")
    return y, ttm


TEST_CONTRACT = "2021-11-19 08:00:00"
SECONDS_IN_A_DAY = 24 * 3600

if __name__ == "__main__":
    print("Testing models.")

    df_con = pd.read_csv("contracts.csv", parse_dates=["expiry", "creation"])
    df = pd.read_csv("con_data.csv", parse_dates=["bar"])
    df_spot = pd.read_csv("spot_data.csv", parse_dates=["bar"])

    df = pd.merge(df, df_con[["sym", "expiry"]], left_on=["symbol"], right_on=["sym"], how="left")
    df = pd.merge(df, df_spot, on=["bar"], suffixes=["", "_spot"], how="left")

    df["days"] = (df["expiry"] - df["bar"]).dt.days
    df["seconds"] = (df["expiry"] - df["bar"]).dt.seconds

    df["ttm"] = (df["days"] * SECONDS_IN_A_DAY + df["seconds"]) / (365 * SECONDS_IN_A_DAY)

    df.set_index(["bar", "symbol"], inplace=True)

    bars = sorted(df.index.get_level_values(0).unique())
    for bar in bars:
        df_tmp = df.xs(bar)
        df_tmp.sort_values("ttm", inplace=True)

        fut_prc = (df_tmp["a1"] + df_tmp["b1"]) / 2.0
        spot_prc = (df_tmp["a1_spot"] + df_tmp["b1_spot"]) / 2.0
        ttm = df_tmp["ttm"]
#        yields = list((fut_prc.div(spot_prc) - 1.0).div(df_tmp["ttm"]).values)
#        yields = list((fut_prc.div(spot_prc) - 1.0).values)
#        yields = list(np.log(fut_prc / spot_prc))
        yields = list(np.log(fut_prc / spot_prc) / ttm)

        ttms = list(df_tmp["ttm"].values)

        contracts = list(df_tmp.index)

        yld, ttm = linear_interpolation(
            bar.strftime("%Y-%m-%d %H:%M:%S"),
            TEST_CONTRACT,
            contracts,
            yields,
            ttms)

        print(bar, yld, ttm)
        prc = calc_prc(spot_prc.values[0], yld, ttm)
        print(f"prc: {prc}")
