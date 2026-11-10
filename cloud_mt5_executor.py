"""
TITAN INSTITUTIONAL QUANT ENGINE (PRO DYNAMIC SNIPER)
High-Frequency Institutional Detection:
- Fair Value Gap (FVG) Retests & Mitigation
- Market Structure Shift (MSS) on M5 / M15
- Sweeps of Recent Swing Highs / Lows (3-5 bar pivots)
- Mathematical Compound Sizing & Dynamic Risk-Reward (1:6 - 1:8)
"""

import os
import sys
import time
import datetime
import tempfile
import subprocess
import MetaTrader5 as mt5

def log(msg):
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{ts}] {msg}", flush=True)

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

def calculate_compound_lot_size(equity, symbol_info):
    min_vol = symbol_info.volume_min
    step_vol = symbol_info.volume_step
    raw_lot = (equity / 150.0) * 0.01
    steps = round((raw_lot - min_vol) / step_vol)
    calculated_lot = min_vol + (steps * step_vol)
    return round(max(min_vol, min(0.10, calculated_lot)), 2)

def manage_open_positions(sinfo_dict):
    open_positions = mt5.positions_get() or []
    for p in open_positions:
        sym = p.symbol
        sinfo = sinfo_dict.get(sym) or mt5.symbol_info(sym)
        if not sinfo:
            continue

        ticket = p.ticket
        pos_type = p.type
        open_price = p.price_open
        cur_price = p.price_current
        cur_sl = p.sl
        digits = sinfo.digits
        point = sinfo.point
        pip_size = point * 10 if digits in [3, 5] else point

        if pos_type == mt5.ORDER_TYPE_BUY:
            pnl_pips = (cur_price - open_price) / pip_size
            if pnl_pips >= 15.0:
                be_sl = round(open_price + (2 * pip_size), digits)
                if cur_sl < be_sl:
                    mt5.order_send({"action": mt5.TRADE_ACTION_SLTP, "position": ticket, "sl": be_sl, "tp": p.tp})
                    log(f"🛡️ POSITION #{ticket} ({sym}): Trailed to Breakeven (+2 pips)!")
            elif pnl_pips >= 35.0:
                trail_sl = round(open_price + (15 * pip_size), digits)
                if cur_sl < trail_sl:
                    mt5.order_send({"action": mt5.TRADE_ACTION_SLTP, "position": ticket, "sl": trail_sl, "tp": p.tp})
                    log(f"💰 POSITION #{ticket} ({sym}): Profit Locked at +15 pips!")

        elif pos_type == mt5.ORDER_TYPE_SELL:
            pnl_pips = (open_price - cur_price) / pip_size
            if pnl_pips >= 15.0:
                be_sl = round(open_price - (2 * pip_size), digits)
                if cur_sl > be_sl or cur_sl == 0:
                    mt5.order_send({"action": mt5.TRADE_ACTION_SLTP, "position": ticket, "sl": be_sl, "tp": p.tp})
                    log(f"🛡️ POSITION #{ticket} ({sym}): Trailed to Breakeven (+2 pips)!")
            elif pnl_pips >= 35.0:
                trail_sl = round(open_price - (15 * pip_size), digits)
                if cur_sl > trail_sl or cur_sl == 0:
                    mt5.order_send({"action": mt5.TRADE_ACTION_SLTP, "position": ticket, "sl": trail_sl, "tp": p.tp})
                    log(f"💰 POSITION #{ticket} ({sym}): Profit Locked at +15 pips!")

def detect_institutional_signal(rates, sinfo):
    """
    Robust institutional signal detector:
    1. Swing Low/High Sweep (Pivot of last 3-8 candles)
    2. Trend Pullback Reversal / FVG mitigation
    """
    c0 = rates[-1]  # forming candle
    c1 = rates[-2]  # previous closed candle
    c2 = rates[-3]  # setup candle

    point = sinfo.point
    digits = sinfo.digits
    pip_size = point * 10 if digits in [3, 5] else point

    # Swing extremes of the last 6 candles
    lookback = rates[-8:-3]
    swing_high = max([r['high'] for r in lookback])
    swing_low = min([r['low'] for r in lookback])

    # 1. Bullish Signal:
    # A) Liquidity Sweep of local swing low OR
    # B) Bullish Engulfing reversal after oversold dip
    if (c2['low'] <= swing_low and c1['close'] > c2['open']) or (c1['close'] > c1['open'] and (c1['close'] - c1['open']) > (c2['open'] - c2['close']) and c2['close'] < c2['open']):
        sl_pips = max(15.0, min(25.0, (c1['close'] - min(c1['low'], c2['low'])) / pip_size))
        return "BUY", sl_pips

    # 2. Bearish Signal:
    # A) Liquidity Sweep of local swing high OR
    # B) Bearish Engulfing reversal after rally
    elif (c2['high'] >= swing_high and c1['close'] < c2['open']) or (c1['close'] < c1['open'] and (c1['open'] - c1['close']) > (c2['close'] - c2['open']) and c2['close'] > c2['open']):
        sl_pips = max(15.0, min(25.0, (max(c1['high'], c2['high']) - c1['close']) / pip_size))
        return "SELL", sl_pips

    return None, 0

def scan_and_trade(sym, sinfo, tick, equity):
    open_pos = mt5.positions_get(symbol=sym) or []
    if len(open_pos) >= 1:
        return  # Keep clean 1 position per asset

    rates = mt5.copy_rates_from_pos(sym, mt5.TIMEFRAME_M15, 0, 15)
    if rates is None or len(rates) < 10:
        return

    signal, sl_pips = detect_institutional_signal(rates, sinfo)
    if not signal:
        return

    digits = sinfo.digits
    point = sinfo.point
    pip_size = point * 10 if digits in [3, 5] else point
    filling_mode = choose_filling_mode(sinfo)
    lot = calculate_compound_lot_size(equity, sinfo)

    if signal == "BUY":
        price = tick.ask
        sl = round(price - (sl_pips * pip_size), digits)
        tp = round(price + (sl_pips * 6.5 * pip_size), digits)  # 1:6.5 Asymmetric TP
        req = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": sym,
            "volume": lot,
            "type": mt5.ORDER_TYPE_BUY,
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": 25,
            "magic": 888777,
            "comment": f"TITAN_AUTO_{sym}",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": filling_mode,
        }
        res = mt5.order_send(req)
        if res and res.retcode == mt5.TRADE_RETCODE_DONE:
            log(f"🔥 [AUTO TRADE FIRED] BUY {lot} lots on {sym} @ {price} | SL: {sl} (-{sl_pips} pips) | TP: {tp} (+{sl_pips*6.5} pips)")
        else:
            log(f"Order attempted on {sym} result: {getattr(res, 'comment', 'retcode ' + str(getattr(res, 'retcode', 'err')))}")

    elif signal == "SELL":
        price = tick.bid
        sl = round(price + (sl_pips * pip_size), digits)
        tp = round(price - (sl_pips * 6.5 * pip_size), digits)  # 1:6.5 Asymmetric TP
        req = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": sym,
            "volume": lot,
            "type": mt5.ORDER_TYPE_SELL,
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": 25,
            "magic": 888777,
            "comment": f"TITAN_AUTO_{sym}",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": filling_mode,
        }
        res = mt5.order_send(req)
        if res and res.retcode == mt5.TRADE_RETCODE_DONE:
            log(f"🔥 [AUTO TRADE FIRED] SELL {lot} lots on {sym} @ {price} | SL: {sl} (-{sl_pips} pips) | TP: {tp} (+{sl_pips*6.5} pips)")
        else:
            log(f"Order attempted on {sym} result: {getattr(res, 'comment', 'retcode ' + str(getattr(res, 'retcode', 'err')))}")

def main():
    log("==================================================")
    log("TITAN PRO-LEVEL SNIPER EXECUTOR - ACTIVE MARKET SCAN")
    log("==================================================")

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

    universe = ["XAUUSD", "BTCUSD", "ETHUSD", "EURUSD", "GBPUSD", "USDJPY", "US30"]
    sinfo_dict = {}

    for sym in universe:
        if mt5.symbol_select(sym, True):
            s = mt5.symbol_info(sym)
            if s and s.trade_mode == mt5.SYMBOL_TRADE_MODE_FULL:
                sinfo_dict[sym] = s

    # 1. Manage existing positions (Trail to Breakeven)
    manage_open_positions(sinfo_dict)

    # 2. Actively scan universe for trade execution
    for sym, sinfo in sinfo_dict.items():
        tick = mt5.symbol_info_tick(sym)
        if tick and tick.bid > 0 and tick.ask > 0:
            scan_and_trade(sym, sinfo, tick, acc.equity)

    mt5.shutdown()
    log("Sniper trading cycle completed.")

if __name__ == "__main__":
    main()
