# tragapy
unofficial python API to get real-time stock trading quotes from German exchange [Tradegate](https://www.tradegate.de/) using their json API. Please note that this project is not affiliated with Tradegate in any way and you are responsible for how you use the data you obtain.

## install
- install from pypi (stable): *unavailable*

- directly from github (unstable): **pip install git+https://github.com/maschere/tragapy -U**

## usage
- get a real-time quote (during market hours) by supplying one ISIN number, e.g.:
  
```python
from tragapy import tragapy
q = tragapy.quote("US36467W1099")
print(q)

{'isin': 'US36467W1099',
 'last_price': 126.0,
 'bid_price': 125.3,
 'ask_price': 126.0,
 'daily_high_price': 139.35,
 'daily_low_price': 124.55,
 'daily_open_price': 132.9,
 'daily_avg_price': 131.4424,
 'daily_volume': 25709,
 'bid_volume': 640,
 'ask_volume': 640}
```

- get today's trade data (until now if market is still open) by supplying one ISIN number
  
```python
from tragapy import tragapy
t = tragapy.tick_all("US36467W1099")
print(t)

                        volume	price	isin
dt			
2021-04-12 08:02:39.089	30.0	131.50	US36467W1099
2021-04-12 08:03:11.004	110.0	131.30	US36467W1099
2021-04-12 08:03:56.563	150.0	131.30	US36467W1099
2021-04-12 08:04:36.649	4.0	132.80	US36467W1099
2021-04-12 08:04:42.436	9.0	132.50	US36467W1099
...	...	...	...
2021-04-12 15:56:12.804	50.0	123.50	US36467W1099
2021-04-12 15:56:20.622	15.0	123.45	US36467W1099
2021-04-12 15:56:43.523	10.0	122.60	US36467W1099
2021-04-12 15:56:44.298	5.0	122.60	US36467W1099
2021-04-12 15:56:46.394	29.0	122.05	US36467W1099
674 rows × 3 columns
```
