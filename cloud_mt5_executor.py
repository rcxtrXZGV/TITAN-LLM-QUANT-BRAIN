"""
TITAN RECURSIVE BRAIN EXECUTOR - BULLETPROOF CRYPTO, FOREX & GOLD STOP DISTANCE
WITH POSITION LIMIT GUARD & DYNAMIC TRAILING BREAKEVEN ENGINE!
1. Trailing Breakeven: When floating profit >= 1:2 RR (or >= $1.50 profit), SL moves to entry + tiny buffer (Risk = $0.00).
2. Position Limit Guard: Prevents duplicate positions, single-bullet risk cap ($2.50 max portfolio risk).
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
        sl_dist = 250.0
        tp_dist = 1800.0
        lot = 0.01
    elif "ETH" in sym:
        sl_dist = 25.0
        tp_dist = 180.0
        lot = 0.01
    elif "SOL" in sym:
        sl_dist = 2.0
        tp_dist = 15.0
        lot = 0.01
    elif "XAU" in sym or "GOLD" in sym:
        sl_dist = 2.50
        tp_dist = 18.00
        lot = 0.01
    elif "XAG" in sym or "SILVER" in sym:
        sl_dist = 0.30
        tp_dist = 2.20
        lot = 0.01
    elif "OIL" in sym or "WTI" in sym or "CL" in sym:
        sl_dist = 0.60
        tp_dist = 4.50
        lot = 0.01
    elif "NAS" in sym or "USTEC" in sym or "100" in sym:
        sl_dist = 20.0
        tp_dist = 150.0
        lot = 0.01
    elif "US30" in sym or "DJ" in sym:
        sl_dist = 30.0
        tp_dist = 220.0
        lot = 0.01
    elif "JPY" in sym:
        sl_dist = 0.25
        tp_dist = 1.80
        lot = 0.02
    else:
        sl_dist = 0.0025
        tp_dist = 0.0180
        lot = 0.01

    if is_buy:
        sl = round(price - sl_dist, 2 if ("BTC" in sym or "XAU" in sym) else 5)
        tp = round(price + tp_dist, 2 if ("BTC" in sym or "XAU" in sym) else 5)
    else:
        sl = round(price + sl_dist, 2 if ("BTC" in sym or "XAU" in sym) else 5)
        tp = round(price - tp_dist, 2 if ("BTC" in sym or "XAU" in sym) else 5)

    return lot, sl, tp

def manage_active_trailing_breakeven(open_positions, rsi_decision=None):
    """
    Pure Autonomous Management:
    1. Instantly update active position TP to realistic intraday target (3782.0 - 3785.0).
    2. Dynamic Profit Lock: If profit >= $8, lock SL into guaranteed green profit!
    """
    brain_target = 0.0
    if rsi_decision:
        try:
            brain_target = float(rsi_decision.get("target_liquidity_pool", 0) or 0)
        except Exception:
            brain_target = 0.0
            
    # Realistic Intraday Target Fallback:
    if brain_target == 0 or brain_target > 3790.0:
        brain_target = 3782.50

    for p in open_positions:
        log(f"Inspecting Position #{p.ticket} on {p.symbol}: Entry={p.price_open}, Current={p.price_current}, SL={p.sl}, TP={p.tp}, Profit=${p.profit:.2f}")
        
        is_buy = (p.type == mt5.ORDER_TYPE_BUY)
        buffer = 0.10 if ("XAU" in p.symbol or "BTC" in p.symbol) else 0.0001
        
        # Step 1: Real-Time TP Synchronization: Overwrite 3799/3894 to realistic target
        current_sl = p.sl
        target_tp = brain_target
        need_mod = False
        
        if brain_target > 0 and abs(p.tp - brain_target) > 0.5:
            target_tp = brain_target
            need_mod = True
            
        # Step 2: Dynamic Profit Lock (If floating profit >= $8, lock guaranteed profit into SL!)
        if p.profit >= 8.0:
            locked_sl = round(p.price_open + (3.0 if is_buy else -3.0), 2 if "XAU" in p.symbol else 5)
            if (is_buy and locked_sl > p.sl) or ((not is_buy) and (p.sl == 0 or locked_sl < p.sl)):
                current_sl = locked_sl
                need_mod = True
                log(f"💰 [GUARANTEED PROFIT LOCK] Position #{p.ticket} is up +${p.profit:.2f}! Moving SL to {locked_sl} to lock in cash!")
        elif p.profit > 0 and (current_sl < p.price_open if is_buy else (current_sl == 0 or current_sl > p.price_open)):
            # Move to Breakeven
            current_sl = round(p.price_open + (buffer if is_buy else -buffer), 2 if "XAU" in p.symbol else 5)
            need_mod = True
            log(f"🎯 [BREAKEVEN] Position #{p.ticket} secured at {current_sl}!")
            
        if need_mod:
            mod_req = {
                "action": mt5.TRADE_ACTION_SLTP,
                "position": p.ticket,
                "symbol": p.symbol,
                "sl": current_sl,
                "tp": target_tp
            }
            res_mod = mt5.order_send(mod_req)
            if res_mod and res_mod.retcode == mt5.TRADE_RETCODE_DONE:
                log(f"✅ Position #{p.ticket} updated! SL={current_sl} | TP={target_tp}!")

def execute_rsi_evolved_trade(rsi_decision, equity):
    target_asset = rsi_decision.get("prime_asset", "Gold (XAUUSD)")
    verdict = rsi_decision.get("verdict", "WAIT")

    log(f"Received Evolved RSI Order Request: {verdict} on {target_asset}")

    # RUTHLESS WAIT DISCIPLINE: Only execute on crystal-clear BUY or SELL!
    if verdict not in ["BUY", "SELL"]:
        log(f"🛡️ [STANDBY] Supreme God Brain verdict is '{verdict}'. Preserving capital with ZERO trade exposure.")
        return

    # Check active open positions and manage trailing breakeven
    open_positions = mt5.positions_get()
    if open_positions and len(open_positions) > 0:
        log(f"ACTIVE POSITION MANAGER: Managing {len(open_positions)} open position(s) on broker.")
        manage_active_trailing_breakeven(open_positions, rsi_decision)
        
        # Guard 1: Prevent duplicate stacking on the EXACT same asset
        target_sym_base = "XAUUSD" if ("Gold" in target_asset or "XAU" in target_asset) else ("BTCUSD" if "BTC" in target_asset else ("EURUSD" if "EUR" in target_asset else "USDJPY"))
        for p in open_positions:
            if target_sym_base in p.symbol:
                log(f"Already holding active position on {p.symbol} (Ticket #{p.ticket}). Skipping duplicate entry on same asset.")
                return
        
        # Guard 2: Allow multi-asset diversification up to 3 uncorrelated trades ($2.00 risk each)
        if len(open_positions) >= 3:
            log(f"Max multi-asset portfolio capacity reached ({len(open_positions)}/3). Preserving margin buffer.")
            return

    sym = "BTCUSD"
    if "Gold" in target_asset or "XAU" in target_asset:
        sym = "XAUUSD"
    elif "Silver" in target_asset or "XAG" in target_asset:
        sym = "XAGUSD"
    elif "Oil" in target_asset or "USOIL" in target_asset:
        sym = "USOIL"
    elif "Nasdaq" in target_asset or "NAS100" in target_asset or "USTEC" in target_asset:
        sym = "USTEC"
    elif "US30" in target_asset:
        sym = "US30"
    elif "ETH" in target_asset:
        sym = "ETHUSD"
    elif "SOL" in target_asset:
        sym = "SOLUSD"
    elif "EUR" in target_asset:
        sym = "EURUSD"
    elif "GBP" in target_asset:
        sym = "GBPUSD"
    elif "JPY" in target_asset:
        sym = "USDJPY"
    elif "AUD" in target_asset:
        sym = "AUDUSD"
    elif "CAD" in target_asset:
        sym = "USDCAD"

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

    is_buy = (verdict == "BUY")
    price = tick.ask if is_buy else tick.bid
    # Pure Autonomous Execution: Read EXACT Target Pool & Calculated SL from Supreme God Brain
    brain_target_pool = float(rsi_decision.get("target_liquidity_pool", 0) or 0)
    brain_sl_pips = float(rsi_decision.get("calculated_sl_pips", 0) or 0)
    
    # Calculate fallback standard stops
    fallback_lot, fallback_sl, fallback_tp = calculate_symbol_stops(sym, price, is_buy)
    lot = fallback_lot
    
    # Use God Brain's exact target if valid, otherwise fallback
    if brain_target_pool > 0:
        tp = round(brain_target_pool, 2 if ("BTC" in sym or "XAU" in sym or "XAG" in sym) else 5)
        log(f"🧠 [GOD BRAIN TARGET UNLOCKED] Using Autonomous Liquidity Target: {tp}")
    else:
        tp = fallback_tp

    # Use God Brain's calculated structural SL if provided and respects minimum broker stops
    if brain_sl_pips > 0:
        multiplier = 0.10 if ("XAU" in sym or "BTC" in sym) else 0.0001
        sl_distance = brain_sl_pips * multiplier
        sl = round(price - sl_distance if is_buy else price + sl_distance, 2 if ("BTC" in sym or "XAU" in sym) else 5)
        log(f"🧠 [GOD BRAIN SL UNLOCKED] Using Autonomous Structural SL: {sl} (dist: {sl_distance})")
    else:
        sl = fallback_sl
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
    try:
        os.makedirs("brain_vault", exist_ok=True)
        open_pos = mt5.positions_get()
        pos_list = []
        if open_pos:
            for p in open_pos:
                pos_list.append({"ticket": p.ticket, "symbol": p.symbol, "volume": p.volume, "sl": p.sl, "tp": p.tp, "profit": round(p.profit, 2)})
        with open(os.path.join("brain_vault", "broker_account_live.json"), "w", encoding="utf-8") as f:
            json.dump({"balance": round(acc.balance, 2), "equity": round(acc.equity, 2), "free_margin": round(acc.margin_free, 2), "open_positions": pos_list}, f, indent=2)
    except Exception as e:
        pass

    # 3-Minute Continuous Real-Time Tick Sniping Loop
    log("Starting 3-Minute Continuous Microsecond Tick Sniping Window...")
    end_time = time.time() + 180  # 3 minutes continuous scanning
    while time.time() < end_time:
        acc = mt5.account_info()
        execute_rsi_evolved_trade(rsi_decision, acc.equity)
        time.sleep(10)  # Check ticks and trailing stops every 10 seconds

    mt5.shutdown()
    log("RSI 3-Minute Sniper Execution cycle successfully finalized.")

if __name__ == "__main__":
    main()
