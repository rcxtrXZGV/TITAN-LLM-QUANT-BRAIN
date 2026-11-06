"""
TITAN CLOUD MT5 VERIFICATION TEST EXECUTION
Fires a minimal 0.01 lot test deal to physically verify cloud-to-broker execution pipeline,
then instantly confirms ticket in broker log.
"""
import os
import sys
import time
import datetime
import MetaTrader5 as mt5

SYMBOL = "XAUUSD"
MAGIC_NUMBER = 999333
LOT_SIZE = 0.01

LOGIN = int(os.environ.get("MT5_LOGIN", "53084231"))
PASSWORD = os.environ.get("MT5_PASSWORD", "7!sOgsaOlLnT2M")
SERVER = os.environ.get("MT5_SERVER", "ICMarketsSC-Demo")

def log(msg):
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{now}] {msg}", flush=True)

def main():
    log("Initializing Cloud MT5 Test Order...")
    if not mt5.initialize():
        log(f"Init failed: {mt5.last_error()}")
        return

    if not mt5.login(LOGIN, password=PASSWORD, server=SERVER):
        log(f"Login failed: {mt5.last_error()}")
        return

    acc = mt5.account_info()
    log(f"Connected to Account #{acc.login} on {acc.server} | Balance: ${acc.balance:.2f}")

    mt5.symbol_select(SYMBOL, True)
    tick = mt5.symbol_info_tick(SYMBOL)
    if not tick:
        log("No tick received.")
        return

    # Send a small verification BUY deal
    sl_price = round(tick.ask - 2.00, 2)
    tp_price = round(tick.ask + 12.00, 2)
    
    order_req = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": SYMBOL,
        "volume": LOT_SIZE,
        "type": mt5.ORDER_TYPE_BUY,
        "price": float(tick.ask),
        "sl": float(sl_price),
        "tp": float(tp_price),
        "deviation": 20,
        "magic": MAGIC_NUMBER,
        "comment": "CLOUD_PIPELINE_TEST",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    log(f"Sending Verification BUY order for {SYMBOL} @ {tick.ask}...")
    res = mt5.order_send(order_req)
    if res and res.retcode == mt5.TRADE_RETCODE_DONE:
        log(f"[SUCCESS] Order #{res.order} executed successfully on broker terminal!")
        log(f"Price: {res.price} | Volume: {res.volume} | SL: {sl_price} | TP: {tp_price}")
    else:
        log(f"[!] Order failed: {res.comment if res else mt5.last_error()}")

    mt5.shutdown()

if __name__ == "__main__":
    main()
