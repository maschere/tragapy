#%% imports and defs
import json
import requests


def format_float(val)->float:
    if type(val) is str:
        val = float(val.replace(".", "").replace(",", "."))
    return val

def format_int(val)->int:
    if type(val) is str:
        val = int(val.replace(".", "").replace(",", "."))
    return val

def traga_quote(isin: str) -> dict:
    raw_dat = json.loads(
        requests.get("https://www.tradegate.de/refresh.php?isin=" + isin).content
    )
    bid_price = format_float(raw_dat["bid"])
    ask_price = format_float(raw_dat["ask"])
    last_price = format_float(raw_dat["last"])
    daily_high_price = format_float(raw_dat["high"])
    daily_low_price = format_float(raw_dat["low"])
    daily_open_price = round(last_price/(1+format_float(raw_dat["delta"].replace("%",""))/100),2)
    daily_avg_price = format_float(raw_dat["avg"])

    bid_volume = format_int(raw_dat["bidsize"])
    ask_volume = format_int(raw_dat["asksize"])
    daily_volume = format_int(raw_dat["stueck"])

    return dict(
        last_price=last_price,
        bid_price=bid_price,
        ask_price=ask_price,
        daily_high_price=daily_high_price,
        daily_low_price=daily_low_price,
        daily_open_price=daily_open_price,
        daily_avg_price=daily_avg_price,
        daily_volume=daily_volume,
        bid_volume=bid_volume,
        ask_volume=ask_volume
    )


def traga_top() -> dict:
    return {}


def traga_ticks(isin: str, from_id: int) -> dict:
    return {}


# %%
bla = traga_quote("US36467W1099")
bla
# %%
