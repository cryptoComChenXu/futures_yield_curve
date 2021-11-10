import os, sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Tuple, List, Dict
import bisect

def linear_interpolation(
    timestamp: str,
    expiration: str,
    yields: List[float],
    ttms: List[float]) -> Tuple[float, float]:

    print(f"Current time: {timestamp}")
    print(f"Expiration time: {expiration}")
    print("Yields: ", yields)
    print("TTMs: ", ttms)

    deltaT = pd.to_datetime(expiration) - pd.to_datetime(timestamp)
    ttm = (deltaT.days * SECONDS_IN_A_DAY + deltaT.seconds) / (365 * SECONDS_IN_A_DAY)

    i = bisect.bisect_left(ttms, ttm)

    return 0, 0


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
    for bar in bars[:3]:
        df_tmp = df.xs(bar)
        df_tmp.sort_values("ttm", inplace=True)

        fut_prc = (df_tmp["a1"] + df_tmp["b1"]) / 2.0
        spot_prc = (df_tmp["a1_spot"] + df_tmp["b1_spot"]) / 2.0
#        yields = list((fut_prc.div(spot_prc) - 1.0).div(df_tmp["ttm"]).values)
        yields = list((fut_prc.div(spot_prc) - 1.0).values)

        ttms = list(df_tmp["ttm"].values)

        yld, ttm = linear_interpolation(
            bar.strftime("%Y-%m-%d %H:%M:%S"),
            TEST_CONTRACT,
            yields,
            ttms)