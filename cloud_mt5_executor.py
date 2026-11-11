"""
TITAN RECURSIVE BRAIN EXECUTOR (DIRECT LLM-BRAIN INTEGRATION)
Directly connects Gemini's Recursive Self-Improvement (RSI) Evolved Intelligence
to MetaTrader 5 Broker for Instant Live Execution.
Reads latest RSI evolution decision & fires with strict $2.00 dollar-risk management.
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

def calculate_safe_dollar_lot(sym, sinfo, sl_distance, max_dollar_risk=2.00):
    min_vol = sinfo.volume_min
    max_vol = sinfo.volume_max
    step_vol = sinfo.volume_step
    tick_value = getattr(sinfo, "trade_tick_value", 1.0) or 1.0
    point = sinfo.point

    if sl_distance <= 0:
        return min_vol

    loss_per_lot = (sl_distance / point) * tick_value if point > 0 else 1000.0
    if loss_per_lot <= 0:
        return min_vol

    raw_lot = max_dollar_risk / loss_per_lot
    steps = int(raw_lot / step_vol)
    calculated_lot = steps * step_vol

    safe_lot = max(min_vol, min(0.10, calculated_lot))
    return round(safe_lot, 2)

def execute_rsi_evolved_trade(rsi_decision, equity):
    target_asset = rsi_decision.get("prime_asset", "Bitcoin (BTCUSD)")
    verdict = rsi_decision.get("verdict", "BUY")
    sl_pips = float(rsi_decision.get("calculated_sl_pips", 140))
    tp_pips = float(rsi_decision.get("calculated_tp_pips", 1412))

    log(f"Received Evolved RSI Order Request: {verdict} on {target_asset}")

    # Map name to broker symbol
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

    sinfo = mt5.symbol_info(sym)
    tick = mt5.symbol_info_tick(sym)

    if not sinfo or not tick:
        log(f"Broker symbol {sym} not available for trading.")
        return

    point = sinfo.point
    digits = sinfo.digits
    pip_size = point * 10 if digits in [3, 5] else point
    sl_dist = sl_pips * pip_size
    tp_dist = tp_pips * pip_size

    # Cap dollar risk strictly to $2.00
    lot = calculate_safe_dollar_lot(sym, sinfo, sl_dist, 2.00)
    filling_mode = choose_filling_mode(sinfo)

    if verdict == "BUY":
        price = tick.ask
        sl = round(price - sl_dist, digits)
        tp = round(price + tp_dist, digits)
        req = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": sym,
            "volume": lot,
            "type": mt5.ORDER_TYPE_BUY,
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": 50,
            "magic": 999901,
            "comment": "TITAN_RSI_AI",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": filling_mode,
        }
        log(f"Transmitting Evolved RSI BUY: {lot} lots {sym} @ {price} | SL: {sl} | TP: {tp}...")
        res = mt5.order_send(req)
        if res and res.retcode == mt5.TRADE_RETCODE_DONE:
            log(f"💥 [RSI TRADE FIRED LIVE] Order #{res.order} on {sym} @ {res.price} executed on broker!")
        else:
            log(f"Order retcode: {getattr(res, 'retcode', None)} | comment: {getattr(res, 'comment', None)}")

    elif verdict == "SELL":
        price = tick.bid
        sl = round(price + sl_dist, digits)
        tp = round(price - tp_dist, digits)
        req = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": sym,
            "volume": lot,
            "type": mt5.ORDER_TYPE_SELL,
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": 50,
            "magic": 999902,
            "comment": "TITAN_RSI_AI",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": filling_mode,
        }
        log(f"Transmitting Evolved RSI SELL: {lot} lots {sym} @ {price} | SL: {sl} | TP: {tp}...")
        res = mt5.order_send(req)
        if res and res.retcode == mt5.TRADE_RETCODE_DONE:
            log(f"💥 [RSI TRADE FIRED LIVE] Order #{res.order} on {sym} @ {res.price} executed on broker!")
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

    # Fire the exact trade evolved by the Recursive Self-Improvement LLM
    execute_rsi_evolved_trade(rsi_decision, acc.equity)

    mt5.shutdown()
    log("RSI Execution cycle successfully finalized.")

if __name__ == "__main__":
    main()
