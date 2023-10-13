# bingXScripts
Custom python scripts to place orders on BingX API. 
  - Create account: https://bingx.com/invite/DYLYZZCR (2% rebate )
  - Create API key make sure withdraw is DISABLED
  - Add your API key on line 11 & 12. 

Place UP TO 15 limit orders at once (scale/ladder) into positions. 

e.g
- Enter pair: BTC-USDT
- USD amount: 1000
- Base price: 26000
- Spread Percent: 1% (This will place orders 1% above or below your price)
- Total orders: 15 (It will evenly divide $1000 into 15 orders)
- Position Side: LONG
- Leverage: 10

The above input will create 15 limit buy orders between 25,740 & 26,000 with 100$ margin and 10x leverage.

Same concept when shorting. The script will place orders ascending.

![image](https://github.com/keeganStrive12/bingXScripts/assets/135064792/669df47a-1f25-473f-9a70-6a1f7028b2ed)



You can also export your PNL in a CSV file.
