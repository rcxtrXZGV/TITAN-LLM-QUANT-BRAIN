"""
TITAN CLOUD MT5 AUTONOMOUS EXECUTOR (XAUUSD)
Runs directly on GitHub Actions (windows-latest virtual environment).
1. Connects to MetaTrader 5 on the cloud VM.
2. Logs in to IC Markets Demo account (53084231).
3. Fetches live Gold ticks & evaluates A+ Predator Institutional Structure.
4. Executes 0.02 Lot orders with tight SL <= 25 pips & Asymmetric 1:6 to 1:10 TP.
5. Manages Break-Even dynamic armor.
"""
import os
import sys
import time
import datetime
import json
import MetaTrader5 as mt5

SYMBOL = "XAUUSD"
MAGIC_NUMBER = 777111
LOT_SIZE = 0.02
MAX_SL_PIPS = 25.0
TARGET_PIPS = 120.0

LOGIN = int(os.environ.get("MT5_LOGIN", "53084231"))
PASSWORD = os.environ.get("MT5_PASSWORD", "7!sOgsaOlLnT2M")
SERVER = os.environ.get("MT5_SERVER", "ICMarketsSC-Demo")

def log(msg):
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{now}] {msg}", flush=True)

def connect_cloud_mt5():
    log("Initializing MetaTrader 5 on Cloud Windows VM...")
    if not mt5.initialize():
        log(f"MT5 Init Error: {mt5.last_error()}")
        return False

    logged_in = mt5.login(LOGIN, password=PASSWORD, server=SERVER)
    if not logged_in:
        log(f"Login failed: {mt5.last_error()}")
        return False

    acc = mt5.account_info()
    if not acc:
        log("No account info found.")
        return False

    log("=" * 65)
    log(f"  CLOUD MT5 CONNECTED TO IC MARKETS DEMO!")
    log(f"  Login: {acc.login} | Server: {acc.server}")
    log(f"  Balance: ${acc.balance:.2f} | Equity: ${acc.equity:.2f} | Trade Allowed: {acc.trade_allowed}")
    log("=" * 65)
    mt5.symbol_select(SYMBOL, True)
    return True

def manage_positions():
    positions = mt5.positions_get(symbol=SYMBOL)
    if not positions:
        return

    for p in positions:
        if p.magic != MAGIC_NUMBER:
            continue
        # Breakeven armor at +15 pips
        if p.type == mt5.ORDER_TYPE_BUY:
            profit_pips = (p.price_current - p.price_open) * 10
            if profit_pips >= 15.0 and p.sl < p.price_open:
                new_sl = round(p.price_open + 0.30, 2)
                req = {
                    "action": mt5.TRADE_ACTION_SLTP,
                    "position": p.ticket,
                    "symbol": SYMBOL,
                    "sl": new_sl,
                    "tp": p.tp
                }
                mt5.order_send(req)
                log(f"[SHIELD] Breakeven locked for BUY #{p.ticket} @ {new_sl}!")
        elif p.type == mt5.ORDER_TYPE_SELL:
            profit_pips = (p.price_open - p.price_current) * 10
            if profit_pips >= 15.0 and (p.sl == 0.0 or p.sl > p.price_open):
                new_sl = round(p.price_open - 0.30, 2)
                req = {
                    "action": mt5.TRADE_ACTION_SLTP,
                    "position": p.ticket,
                    "symbol": SYMBOL,
                    "sl": new_sl,
                    "tp": p.tp
                }
                mt5.order_send(req)
                log(f"[SHIELD] Breakeven locked for SELL #{p.ticket} @ {new_sl}!")

def evaluate_and_trade():
    rates = mt5.copy_rates_from_pos(SYMBOL, mt5.TIMEFRAME_M5, 0, 20)
    if rates is None or len(rates) < 10:
        return

    tick = mt5.symbol_info_tick(SYMBOL)
    last_bar = rates[-2]
    c_open = last_bar['open']
    c_high = last_bar['high']
    c_low = last_bar['low']
    c_close = last_bar['close']
    rng = c_high - c_low

    if rng < 1.0:
        log("Market in tight chop (< $1 range). Sitting on hands.")
        return

    wick_up = c_high - max(c_open, c_close)
    wick_down = min(c_open, c_close) - c_low

    direction = None
    sl_price = 0.0
    tp_price = 0.0

    if wick_up >= 0.50 * rng and c_close < c_open:
        inval = (c_high + 0.30) - tick.bid
        if 0.80 <= inval <= 2.50:
            direction = "SELL"
            sl_price = round(c_high + 0.30, 2)
            tp_price = round(tick.bid - (TARGET_PIPS / 10), 2)
    elif wick_down >= 0.50 * rng and c_close > c_open:
        inval = tick.ask - (c_low - 0.30)
        if 0.80 <= inval <= 2.50:
            direction = "BUY"
            sl_price = round(c_low - 0.30, 2)
            tp_price = round(tick.ask + (TARGET_PIPS / 10), 2)

    if direction and sl_price > 0:
        # Check if already in trade
        open_pos = mt5.positions_get(symbol=SYMBOL)
        if open_pos and any(p.magic == MAGIC_NUMBER for p in open_pos):
            log("Active position already open. Monitoring runner.")
            return

        order_type = mt5.ORDER_TYPE_BUY if direction == "BUY" else mt5.ORDER_TYPE_SELL
        entry_price = tick.ask if direction == "BUY" else tick.bid
        
        req = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": SYMBOL,
            "volume": LOT_SIZE,
            "type": order_type,
            "price": float(entry_price),
            "sl": float(sl_price),
            "tp": float(tp_price),
            "deviation": 20,
            "magic": MAGIC_NUMBER,
            "comment": "TITAN_PREDATOR",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        res = mt5.order_send(req)
        if res and res.retcode == mt5.TRADE_RETCODE_DONE:
            log(f"[TRADE EXECUTED] {direction} {SYMBOL} #{res.order} @ {res.price} | SL: {sl_price} | TP: {tp_price}")
        else:
            log(f"[!] Order rejected: {res.comment if res else mt5.last_error()}")

def main():
    if not connect_cloud_mt5():
        return
    manage_positions()
    evaluate_and_trade()
    mt5.shutdown()

if __name__ == "__main__":
    main()
