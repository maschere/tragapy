#%% imports and defs
import json
from typing import Tuple
import requests
import pandas as pd

# custom_headers = {'user-agent': 'https://github.com/maschere/tragapy'}


def format_float(val) -> float:
    if type(val) is str:
        val = float(val.replace(",", "."))
    return val


def format_int(val) -> int:
    if type(val) is str:
        val = int(val.replace(",", "."))
    return val


def traga_quote(isin: str) -> dict:
    """queries the latest quote of the supplied ISIN from tradegate

    Args:
        isin (str): ISIN number

    Returns:
        dict: real-time quote data
    """
    raw_dat = json.loads(
        requests.get("https://www.tradegate.de/refresh.php?isin=" + isin).content
    )
    # fix numbers, sometimes , instead of .
    bid_price = format_float(raw_dat["bid"])
    ask_price = format_float(raw_dat["ask"])
    last_price = format_float(raw_dat["last"])
    daily_high_price = format_float(raw_dat["high"])
    daily_low_price = format_float(raw_dat["low"])
    daily_open_price = round(
        last_price / (1 + format_float(raw_dat["delta"].replace("%", "")) / 100), 2
    )
    daily_avg_price = format_float(raw_dat["avg"])

    bid_volume = format_int(raw_dat["bidsize"])
    ask_volume = format_int(raw_dat["asksize"])
    daily_volume = format_int(raw_dat["stueck"])
    # return dict
    return dict(
        isin=isin,
        last_price=last_price,
        bid_price=bid_price,
        ask_price=ask_price,
        daily_high_price=daily_high_price,
        daily_low_price=daily_low_price,
        daily_open_price=daily_open_price,
        daily_avg_price=daily_avg_price,
        daily_volume=daily_volume,
        bid_volume=bid_volume,
        ask_volume=ask_volume,
    )


def traga_top() -> dict:
    return {}


def traga_ticks(isin: str, from_id=0) -> Tuple[pd.DataFrame, int]:
    """queries todays trading ticks of the supplied ISIN from tradegate

    Args:
        isin (str): ISIN number
        from_id (int): transaction ID. starts at 0 on market open and increases until market close

    Returns:
        Tuple[pd.DataFrame,int]: dataframe of tick data and the next tick ID to continue querying from
    """
    raw_dat = json.loads(
        requests.get(
            "https://www.tradegate.de/umsaetze.php?isin={isin:s}&id={id:g}".format(
                isin=isin, id=from_id
            )
        ).content
    )
    # convert to df
    dat = pd.DataFrame(raw_dat)
    if len(dat) == 0:
        return None, -1
    # get next id to continue query with
    next_id = int(max(dat["id"]))
    # filter and convert
    dat["volume"] = dat["umsatz"].apply(lambda x: format_float(x))
    dat["price"] = dat["price"].apply(lambda x: format_float(x))
    dat = dat.loc[dat["volume"] >= 1]
    if len(dat) == 0:
        return None, -1
    dat["dt"] = pd.to_datetime(dat["date"] + " " + dat["time"])
    dat.drop(
        ["id", "sortierung", "date", "time", "umsatz"], inplace=True, axis="columns"
    )
    dat["isin"] = isin
    # dat.reset_index(drop=True, inplace=True)
    dat.set_index("dt", inplace=True)
    return dat, next_id


def traga_ticks_all(isin: str) -> pd.DataFrame:
    """retrieves all of todays ticks up until now for the supplied ISIN. please use this responsibly as it queries a lot from tradegate

    Args:
        isin (str): ISIN number

    Returns:
        pd.DataFrame: dataframe of tick data up until now
    """
    dats = []
    nextid = 0
    while nextid != -1:
        dat, nextid = traga_ticks(isin, nextid)
        dats.append(dat)
    return pd.concat(dats)


# %%
bla = traga_quote("US36467W1099")
bla
# %%
blub, nextid = traga_ticks("US36467W1099", 37406)
blub
# %%
all_dat = traga_ticks_all("US36467W1099")
all_dat
# %%
all_dat.to_pickle("US36467W1099_20210302.pkl")

# %%
