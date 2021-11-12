import os, sys
import numpy as np
import pandas as pd
from pathlib import Path
from models import linear_interpolation, calc_prc
from models import SECONDS_IN_A_DAY

if __name__ == "__main__":
    test_options_chain_file = "btc_option_chain.csv"
    df_options = pd.read_csv(test_options_chain_file, parse_dates=["expiry", "creation"])

    res = []

    df_spot = pd.read_csv("spot_data.csv", parse_dates=["bar"])
    df_con = pd.read_csv("con_data.csv", parse_dates=["bar"])
    df_contracts = pd.read_csv("contracts.csv", parse_dates=["expiry"])

    df_spot["spot_prc"] = (df_spot["a1"] + df_spot["b1"]) / 2.0
    df = pd.merge(df_con, df_spot[["bar", "spot_prc"]], how="left", left_on=["bar"], right_on=["bar"])
    df = pd.merge(df, df_contracts[["sym", "expiry"]], how="left", left_on=["symbol"], right_on=["sym"])
    df["delta"] = df["expiry"] - df["bar"]
    df["ttm"] = (df["delta"].dt.days * SECONDS_IN_A_DAY + df["delta"].dt.seconds) / (SECONDS_IN_A_DAY * 365)
    df["yields"] = np.log((df["a1"] + df["b1"]) / df["spot_prc"] / 2.0) / df["ttm"]

    df.set_index(["bar", "symbol"], inplace=True)
    df.sort_index(inplace=True)

    bars = sorted(df.index.get_level_values(0).unique())
    for bar in bars:
        df_tmp = df.xs(bar)
        df_tmp.dropna(subset=["expiry", "ttm", "yields"], inplace=True)
        df_tmp.sort_values("ttm", inplace=True)

        for expiry in sorted(df_options.expiry.dt.strftime("%Y-%m-%d %H:%M:%S").unique()):
            print(f"\nExpiration: {expiry}")
            yld, ttm = linear_interpolation(
                bar.strftime("%Y-%m-%d %H:%M:%S"),
                expiry,
                list(df_tmp.index),
                list(df_tmp.yields.values),
                list(df_tmp.ttm.values))

            spot_prc = df_tmp.spot_prc.values[0]
            prc = calc_prc(spot_prc, yld, ttm)

            print(f"bar: {bar}, yld: {yld},  ttm: {ttm}, spot price: {spot_prc}, futures' price: {prc}")
