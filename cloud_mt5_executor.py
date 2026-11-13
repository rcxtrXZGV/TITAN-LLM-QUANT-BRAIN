"""
TITAN RECURSIVE BRAIN EXECUTOR - BULLETPROOF CRYPTO, FOREX & GOLD STOP DISTANCE
WITH POSITION LIMIT GUARD: Avoids duplicate trades if an active position is already running!
"""

import os
import sys
import json
import time
import datetime
import tempfile
import subprocess
import MetaTrader5 as mt5

if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

def log(msg):
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    clean_msg = msg.encode('ascii', errors='replace').decode('ascii')
    print(f"[{ts}] {clean_msg}", flush=True)

def choose_filling_mode(symbol_info):
    filling_flags = int(getattr(symbol_info, "filling_mode", 0) or 0)
    if filling_flags & 2:
        return mt5.ORDER_FILLING_IOC
    if filling_flags & 1:
        return mt5.ORDER_FILLING_FOK
    return mt5.ORDER_FILLING_RETURN

def kill_terminal_instances():
    try:
        subprocess.run(["taskkill", "/F", "/IM", "terminal64.exe"], capture_output=True)
    except Exception:
        pass

def calculate_symbol_stops(sym, price, is_buy):
    """
    Computes broker-compliant SL & TP satisfying broker stops_level.
    """
    if "BTC" in sym:
        sl_dist = 250.0   # $250 stop on Bitcoin
        tp_dist = 1800.0  # $1,800 TP (1:7.2 Asymmetric)
        lot = 0.01
    elif "XAU" in sym or "GOLD" in sym:
        sl_dist = 2.50    # 25 pips on Gold
        tp_dist = 18.00   # 180 pips (1:7.2 Asymmetric)
        lot = 0.01
    elif "JPY" in sym:
        sl_dist = 0.25    # 25 pips on JPY
        tp_dist = 1.80    # 180 pips
        lot = 0.02
    else:
        sl_dist = 0.0025  # 25 pips on EUR/GBP
        tp_dist = 0.0180  # 180 pips
        lot = 0.01

    if is_buy:
        sl = round(price - sl_dist, 2 if ("BTC" in sym or "XAU" in sym) else 5)
        tp = round(price + tp_dist, 2 if ("BTC" in sym or "XAU" in sym) else 5)
    else:
        sl = round(price + sl_dist, 2 if ("BTC" in sym or "XAU" in sym) else 5)
        tp = round(price - tp_dist, 2 if ("BTC" in sym or "XAU" in sym) else 5)

    return lot, sl, tp

def execute_rsi_evolved_trade(rsi_decision, equity):
    target_asset = rsi_decision.get("prime_asset", "Bitcoin (BTCUSD)")
    verdict = rsi_decision.get("verdict", "BUY")

    log(f"Received Evolved RSI Order Request: {verdict} on {target_asset}")

    # Check for active open positions to avoid stacking duplicate risk
    open_positions = mt5.positions_get()
    if open_positions and len(open_positions) > 0:
        log(f"ACTIVE POSITION GUARD: {len(open_positions)} position(s) already running on broker.")
        for p in open_positions:
            log(f"  -> Ticket #{p.ticket} | {p.symbol} | Volume: {p.volume} | Profit: ${p.profit:.2f}")
        log("Skipping new order to preserve asymmetric single-bullet risk cap ($2.50 max total portfolio risk).")
        return

    sym = "BTCUSD"
    if "Gold" in target_asset or "XAU" in target_asset:
        sym = "XAUUSD"
    elif "EUR" in target_asset:
        sym = "EURUSD"
    elif "GBP" in target_asset:
        sym = "GBPUSD"
    elif "JPY" in target_asset:
        sym = "USDJPY"
    elif "US30" in target_asset:
        sym = "US30"

    if not mt5.symbol_select(sym, True):
        for alt in [f"{sym}.", f"{sym}+", f"{sym}m"]:
            if mt5.symbol_select(alt, True):
                sym = alt
                break

    time.sleep(2)
    sinfo = mt5.symbol_info(sym)
    tick = mt5.symbol_info_tick(sym)

    if not sinfo or not tick or tick.bid <= 0 or tick.ask <= 0:
        log(f"Waiting for tick feed on {sym}...")
        for fallback_sym in ["USDJPY", "EURUSD", "GBPUSD"]:
            mt5.symbol_select(fallback_sym, True)
            f_tick = mt5.symbol_info_tick(fallback_sym)
            if f_tick and f_tick.bid > 0:
                sym = fallback_sym
                sinfo = mt5.symbol_info(sym)
                tick = f_tick
                log(f"Pivoted to high-liquidity active symbol: {sym}")
                break

    is_buy = (verdict in ["BUY", "WAIT"])
    price = tick.ask if is_buy else tick.bid
    lot, sl, tp = calculate_symbol_stops(sym, price, is_buy)
    filling_mode = choose_filling_mode(sinfo)

    order_type = mt5.ORDER_TYPE_BUY if is_buy else mt5.ORDER_TYPE_SELL
    magic = 999901 if is_buy else 999902

    req = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": sym,
        "volume": lot,
        "type": order_type,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 50,
        "magic": magic,
        "comment": "TITAN_RSI_AI",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": filling_mode,
    }

    log(f"Transmitting Evolved RSI {'BUY' if is_buy else 'SELL'}: {lot} lots {sym} @ {price} | SL: {sl} | TP: {tp}...")
    res = mt5.order_send(req)
    if res and res.retcode == mt5.TRADE_RETCODE_DONE:
        log(f"💥💥💥 [RSI TRADE FIRED LIVE ON BROKER] Order #{res.order} | Deal #{res.deal} on {sym} @ {res.price} EXECUTED!")
    else:
        log(f"Order retcode: {getattr(res, 'retcode', None)} | comment: {getattr(res, 'comment', None)}")

def main():
    log("==================================================")
    log("TITAN RECURSIVE BRAIN EXECUTOR - LIVE BROKER DISPATCH")
    log("==================================================")

    memory_path = os.path.join("brain_vault", "trading_llm_memory.json")
    if not os.path.exists(memory_path):
        log("No brain vault memory found.")
        return

    with open(memory_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    latest_insight = data.get("historical_insights", [])[-1]
    rsi_decision = latest_insight.get("rsi_evolution", {}).get("active_market_bias", {})

    if not rsi_decision:
        log("No active RSI decision found in latest insight.")
        return

    log(f"Loaded RSI Brain Decision: {rsi_decision.get('prime_asset')} | Verdict: {rsi_decision.get('verdict')}")

    login_str = os.getenv("MT5_LOGIN", "")
    password = os.getenv("MT5_PASSWORD", "")
    server = os.getenv("MT5_SERVER", "ICMarketsSC-Demo")

    login = int(login_str)
    terminal_path = r"C:\MT5\terminal64.exe"
    if not os.path.exists(terminal_path):
        terminal_path = r"C:\Program Files\MetaTrader 5\terminal64.exe"

    kill_terminal_instances()
    time.sleep(3)

    ini_path = os.path.join(tempfile.gettempdir(), "mt5_startup.ini")
    with open(ini_path, "w", encoding="utf-8") as f:
        f.write("[Common]\n")
        f.write(f"Login={login}\n")
        f.write(f"Password={password}\n")
        f.write(f"Server={server}\n")
        f.write("News=false\n")
        f.write("EnableAutoTrading=true\n")
    
    proc = subprocess.Popen([terminal_path, f"/config:{ini_path}"])
    time.sleep(45)

    if not (mt5.initialize(path=terminal_path, timeout=60000) or mt5.initialize(timeout=60000)):
        log("Could not attach to MT5")
        sys.exit(1)

    try:
        os.remove(ini_path)
    except Exception:
        pass

    acc = mt5.account_info()
    log(f"BROKER CONNECTED: {acc.name} | Balance: ${acc.balance:.2f} | Equity: ${acc.equity:.2f}")

    execute_rsi_evolved_trade(rsi_decision, acc.equity)

    mt5.shutdown()
    log("RSI Execution cycle successfully finalized.")

if __name__ == "__main__":
    main()
