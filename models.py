import os, sys
import numpy as np
import pandas as pd
from typing import Tuple, List, Dict, Type

def linear_interpolation(
    timestamp: str,
    expiration: str,
    yields: List[float],
    ttm: List[float]) -> Tuple(float, float):
    pass


if __name__ == "__main__":
    print("Testing models.")

    df_con = pd.read_csv("contracts.csv", parse_dates=["expiry", "creation"])
    df = pd.read_csv("con_data.csv", parse_dates=["bar"])
    df_spot = pd.read_csv("spot_data.csv", parse_dates=["bar"])

    df = pd.merge(df, df_con[["sym", "expiry"]], left_on=["symbol"], right_on=["sym"], how="left")
    df = pd.merge(df, df_spot, on=["bar"], suffixes=["", "_spot"], how="left")

    df["days"] = (df["expiry"] - df["bar"]).dt.days
    df["seconds"] = (df["expiry"] - df["bar"]).dt.seconds

    seconds_in_a_day = 24 * 3600
    df["ttm"] = (df["days"] * seconds_in_a_day + df["seconds"]) / (365 * seconds_in_a_day)

    df.set_index(["bar", "symbol"], inplace=True)

    bars = sorted(df.index.get_level_values(0).unique())
    for bar in bars:
        df_tmp = df.xs(bar)
        df_tmp.sort_values("ttm", inplace=True)
        print(df_tmp)