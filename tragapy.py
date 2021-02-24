#%% imports and defs
import json
from typing import Any, Tuple
import requests
import pandas as pd
import time
from datetime import datetime, timedelta
import pytz

# custom_headers = {'user-agent': 'https://github.com/maschere/tragapy'}


def format_float(val) -> float:
    if type(val) is str:
        val = float(val.replace(" ", "").replace(",", "."))
    return val


def format_int(val) -> int:
    if type(val) is str:
        val = int(val.replace(" ", "").replace(",", "."))
    return val



class tragapy:
    """static class that wraps all tradegate json API calls
    """
    last_warn = datetime.now() - timedelta(seconds=10)

    @staticmethod
    def __get__(url: str, pause=0.0) -> dict:
        raw_dat = {}
        tz = pytz.timezone("Europe/Berlin")
        berlin_now = datetime.now(tz)
        if berlin_now.hour < 8 or berlin_now.hour >= 22:
            if (datetime.now() - tragapy.last_warn).total_seconds() > 10.0:
                print("WARNING: Market is closed right now, returning yesterday's data")
                tragapy.last_warn = datetime.now()
        try:
            if pause > 0:
                time.sleep(pause)
            txt_dat = requests.get(url).content
            raw_dat = json.loads(txt_dat)
        except:
            pass
        return raw_dat

    @staticmethod
    def quote(isin: str) -> dict:
        """queries the latest quote of the supplied ISIN from tradegate

        Args:
            isin (str): ISIN number

        Returns:
            dict: real-time quote data
        """
        raw_dat = tragapy.__get__("https://www.tradegate.de/refresh.php?isin=" + isin)
        # fix numbers, sometimes , instead of .
        if raw_dat["avg"] == "./.":
            return {}
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

    @staticmethod
    def top() -> pd.DataFrame:
        all_top = []
        for i in range(1,5):
            top_dict = tragapy.__get__("https://www.tradegate.de/json/tradegate{id:g}.json".format(id=i),0.05)
            all_top.append(pd.DataFrame(top_dict["top5umsatz"]))
        return pd.concat(all_top, ignore_index=True)


    @staticmethod
    def ticks(isin: str, from_id=0) -> Tuple[pd.DataFrame, int]:
        """queries todays trading ticks of the supplied ISIN from tradegate

        Args:
            isin (str): ISIN number
            from_id (int): transaction ID. starts at 0 on market open and increases until market close

        Returns:
            Tuple[pd.DataFrame,int,dict]: dataframe of tick data and the next tick ID to continue querying from
        """
        raw_dat = tragapy.__get__(
            "https://www.tradegate.de/umsaetze.php?isin={isin:s}&id={id:g}".format(
                isin=isin, id=from_id
            ), pause=0.05
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
            ["id", "sortierung", "date", "time", "umsatz"], inplace=True, axis="columns", errors="ignore"
        )
        dat["isin"] = isin
        # dat.reset_index(drop=True, inplace=True)
        dat.set_index("dt", inplace=True)
        return dat, next_id

    @staticmethod
    def ticks_all(isin: str) -> pd.DataFrame:
        """retrieves all of todays ticks up until now for the supplied ISIN. please use this responsibly as it queries a lot from tradegate

        Args:
            isin (str): ISIN number

        Returns:
            pd.DataFrame: dataframe of tick data up until now
        """
        dats = []
        nextid = 0
        while nextid != -1:
            dat, nextid = tragapy.ticks(isin, nextid)
            if dat is not None:
                dats.append(dat)
        if len(dats) > 0:
            dats = pd.concat(dats)
        else:
            dats = pd.DataFrame()
        return dats

