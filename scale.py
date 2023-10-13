import time
import requests
import hmac
import json
from hashlib import sha256
import pandas as pd
import json
from datetime import datetime


APIURL = "https://open-api.bingx.com"
APIKEY = "BINGX_KEY"
SECRETKEY = "BINGX_SECRET"

def calculate_quantity(price, usd):
    return usd / price

def get_current_leverage(symbol):
    payload = {}
    path = '/openApi/swap/v2/trade/leverage'
    method = "GET"
    paramsMap = {
        "symbol": symbol,
        "recvWindow": 0
    }
    paramsStr = praseParam(paramsMap)
    response = send_request(method, path, paramsStr, payload)
    data = json.loads(response)
    return data.get('leverage', None)

def set_leverage(symbol, side, leverage):
    payload = {}
    path = '/openApi/swap/v2/trade/leverage'
    method = "POST"
    paramsMap = {
        "symbol": symbol,
        "side": side,
        "leverage": leverage,
        "recvWindow": 0
    }
    paramsStr = praseParam(paramsMap)
    send_request(method, path, paramsStr, payload)

def create_bulk_orders(symbol, base_price, spread_percent, total_orders, total_usd, position_side):
    orders = []
    single_order_usd = total_usd / total_orders
    single_order_spread = spread_percent / (total_orders - 1)
    
    for i in range(total_orders):
        price_multiplier = 1 + (i * single_order_spread / 100) if position_side == "SHORT" else 1 - (i * single_order_spread / 100)
        price = base_price * price_multiplier
        quantity = calculate_quantity(price, single_order_usd)
        
        order = {
            "symbol": symbol,
            "type": "LIMIT",
            "side": "BUY" if position_side == "LONG" else "SELL",
            "positionSide": position_side,
            "price": price,
            "quantity": quantity
        }
        orders.append(order)
    return json.dumps(orders)

def get_sign(api_secret, payload):
    signature = hmac.new(api_secret.encode("utf-8"), payload.encode("utf-8"), digestmod=sha256).hexdigest()
    return signature

def send_request(method, path, urlpa, payload):
    url = f"{APIURL}{path}?{urlpa}&signature={get_sign(SECRETKEY, urlpa)}"
    headers = {
        'X-BX-APIKEY': APIKEY,
    }
    response = requests.request(method, url, headers=headers, data=payload)
    return response.text

def praseParam(paramsMap):
    sortedKeys = sorted(paramsMap)
    paramsStr = "&".join([f"{x}={paramsMap[x]}" for x in sortedKeys])
    return f"{paramsStr}&timestamp={int(time.time() * 1000)}"

def PnLInfo():
    payload = {}
    path = '/openApi/swap/v2/user/income'
    method = "GET"
    paramsMap = {
    "incomeType": "REALIZED_PNL",
    "startTime": 0,
    "endTime": 0,
    "limit": 0,
    "recvWindow": 0
}
    paramsStr = praseParam(paramsMap)
    result = send_request(method, path, paramsStr, payload)
    data_dict = json.loads(result)
    data_list = data_dict.get('data', [])
    df = pd.DataFrame(data_list)
    df['income'] = df['income'].astype(float)
    total_income = df['income'].sum()
    print(df)
    print(f'Total Income: {total_income} {df["asset"].iloc[0] if not df.empty else ""}')

    # Export to CSV
    now = datetime.now()
    date_time_str = now.strftime('%Y%m%d_%H%M%S')

    df.to_csv(f'{date_time_str}.csv', index=False)

def accountInfo():
    payload = {}
    path = '/openApi/swap/v2/user/balance'
    method = "GET"
    paramsMap = {
    "recvWindow": 0
}
    paramsStr = praseParam(paramsMap)
    result = send_request(method, path, paramsStr, payload)
    result_dict = json.loads(result)

    balance_data = result_dict['data']['balance']
    formatted_str = (
        f"User ID: {balance_data['userId']}\n"
        f"Asset: {balance_data['asset']}\n"
        f"Balance: {balance_data['balance']}\n"
        f"Equity: {balance_data['equity']}\n"
        f"Unrealized Profit: {balance_data['unrealizedProfit']}\n"
        f"Available Margin: {balance_data['availableMargin']}\n"
        f"Used Margin: {balance_data['usedMargin']}"
    )
    print(formatted_str)
def Balance():
    payload = {}
    path = '/openApi/swap/v2/user/balance'
    method = "GET"
    paramsMap = {
    "recvWindow": 0
}
    paramsStr = praseParam(paramsMap)
    result = send_request(method, path, paramsStr, payload)
    result_dict = json.loads(result)

    balance_data = result_dict['data']['balance']
    formatted_str = (
        
        f"Available Margin: {balance_data['availableMargin']}\n"

    )
    print(formatted_str)
def scale():
    Balance()
    symbol = input("Enter the trading pair symbol (e.g., BTC-USDT): ")
    total_usd = float(input("Enter your total USD amount: "))
    base_price = float(input("Enter your base price: "))
    spread_percent = float(input("Enter your total spread percentage: "))
    total_orders = int(input("Enter total number of orders: "))
    if total_orders > 15:
        print('15 is the max. Changed to 15')
        total_orders = 15
    position_side = input("Enter position side (LONG or SHORT): ").upper()
    leverage = int(input("Enter your desired leverage: "))
    
    if position_side not in ["LONG", "SHORT"]:
        print("Invalid position side. Please enter either LONG or SHORT.")
        return
    
    current_leverage = get_current_leverage(symbol)
    if current_leverage != leverage:
        set_leverage(symbol, position_side, leverage)
    
    bulk_orders = create_bulk_orders(symbol, base_price, spread_percent, total_orders, total_usd, position_side)
    
    if not bulk_orders:
        print("No orders to place.")
        return

    paramsMap = {
        "batchOrders": str(bulk_orders)
    }
    
    path = '/openApi/swap/v2/trade/batchOrders'
    method = "POST"
    paramsStr = praseParam(paramsMap)
    result = send_request(method, path, paramsStr, {})
    print(f"API response: {result}")

def menu():
    option = input("CHOOSE AN OPTION: 1 = TRADE | 2 = PnL | 3 = ACCOUNT: ")
    if option == '1':
        scale()
    if option == '2':
        PnLInfo()
    if option == '3':
        accountInfo()
if __name__ == '__main__':
    menu()
