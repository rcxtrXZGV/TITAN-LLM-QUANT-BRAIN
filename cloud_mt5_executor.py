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

def run_trading_cycle(candidates):
    # 1. Trailing Breakeven Shield Management on all open positions
    open_positions = mt5.positions_get() or []
    for p in open_positions:
        sym = p.symbol
        pos_sinfo = mt5.symbol_info(sym)
        if not pos_sinfo:
            continue
            
        ticket = p.ticket
        pos_type = p.type
        open_price = p.price_open
        cur_price = p.price_current
        cur_sl = p.sl

        point = pos_sinfo.point
        pip_size = point * 10 if pos_sinfo.digits in [3, 5] else point

        # Trailing Breakeven at +15 pips (Risk eliminated)
        if pos_type == mt5.ORDER_TYPE_BUY and (cur_price - open_price) >= (15 * pip_size):
            be_sl = open_price + (2 * pip_size)
            if cur_sl < be_sl:
                req = {"action": mt5.TRADE_ACTION_SLTP, "position": ticket, "sl": round(be_sl, pos_sinfo.digits), "tp": p.tp}
                mt5.order_send(req)
                log(f"Position #{ticket} ({sym}) SL Trailed to Zero-Risk Breakeven ({be_sl})!")
        elif pos_type == mt5.ORDER_TYPE_SELL and (open_price - cur_price) >= (15 * pip_size):
            be_sl = open_price - (2 * pip_size)
            if cur_sl > be_sl or cur_sl == 0:
                req = {"action": mt5.TRADE_ACTION_SLTP, "position": ticket, "sl": round(be_sl, pos_sinfo.digits), "tp": p.tp}
                mt5.order_send(req)
                log(f"Position #{ticket} ({sym}) SL Trailed to Zero-Risk Breakeven ({be_sl})!")

    # 2. Evaluate and fire opportunities
    for sym in candidates:
        if not mt5.symbol_select(sym, True):
            continue
        sinfo = mt5.symbol_info(sym)
        tick = mt5.symbol_info_tick(sym)
        if not sinfo or not tick or tick.bid <= 0 or sinfo.trade_mode != mt5.SYMBOL_TRADE_MODE_FULL:
            continue

        open_pos = mt5.positions_get(symbol=sym) or []
        if len(open_pos) >= 2:
            continue

        rates = mt5.copy_rates_from_pos(sym, mt5.TIMEFRAME_M15, 0, 20)
        if rates is None or len(rates) < 15:
            continue

        last_candle = rates[-2]
        prev_candle = rates[-3]
        recent_high = max([r['high'] for r in rates[:-3]])
        recent_low = min([r['low'] for r in rates[:-3]])

        point = sinfo.point
        pip_size = point * 10 if sinfo.digits in [3, 5] else point
        filling_mode = choose_filling_mode(sinfo)
        lot = sinfo.volume_min

        # Bullish Setup: Sweep low + Close above
        if prev_candle['low'] < recent_low and last_candle['close'] > prev_candle['high']:
            sl = round(prev_candle['low'] - (5 * pip_size), sinfo.digits)
            sl_distance = tick.ask - sl
            if sl_distance <= (30 * pip_size):
                tp = round(tick.ask + (sl_distance * 8.0), sinfo.digits)
                req = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": sym,
                    "volume": lot,
                    "type": mt5.ORDER_TYPE_BUY,
                    "price": tick.ask,
                    "sl": sl,
                    "tp": tp,
                    "deviation": 30,
                    "magic": 777001,
                    "comment": f"VPS_{sym}",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": filling_mode,
                }
                res = mt5.order_send(req)
                if res and res.retcode == mt5.TRADE_RETCODE_DONE:
                    log(f"🔥 FIRED BUY on {sym} | Lot: {lot} | Price: {tick.ask} | SL: {sl} | TP: {tp} (1:8 RR)")

        # Bearish Setup: Sweep high + Close below
        elif prev_candle['high'] > recent_high and last_candle['close'] < prev_candle['low']:
            sl = round(prev_candle['high'] + (5 * pip_size), sinfo.digits)
            sl_distance = sl - tick.bid
            if sl_distance <= (30 * pip_size):
                tp = round(tick.bid - (sl_distance * 8.0), sinfo.digits)
                req = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": sym,
                    "volume": lot,
                    "type": mt5.ORDER_TYPE_SELL,
                    "price": tick.bid,
                    "sl": sl,
                    "tp": tp,
                    "deviation": 30,
                    "magic": 777002,
                    "comment": f"VPS_{sym}",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": filling_mode,
                }
                res = mt5.order_send(req)
                if res and res.retcode == mt5.TRADE_RETCODE_DONE:
                    log(f"🔥 FIRED SELL on {sym} | Lot: {lot} | Price: {tick.bid} | SL: {sl} | TP: {tp} (1:8 RR)")

def main():
    log("==================================================")
    log("TITAN CLOUD VPS-ENGINE: 5-HOUR CONTINUOUS LIVE DAEMON")
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
    log(f"VPS DAEMON ONLINE: {acc.name} | Balance: ${acc.balance:.2f} | Equity: ${acc.equity:.2f}")

    candidates = ["XAUUSD", "BTCUSD", "ETHUSD", "EURUSD", "GBPUSD", "USDJPY", "US30", "NAS100"]

    # Continuous Real-Time Loop (Runs for 5 Hours = 18,000 seconds)
    # Checks every 15 seconds like a real VPS!
    start_time = time.time()
    max_duration_seconds = 5 * 3600 - 300  # 4 hours 55 minutes

    log("Starting Continuous 15-Second High-Frequency Market Scanner...")
    loop_count = 0

    while (time.time() - start_time) < max_duration_seconds:
        try:
            run_trading_cycle(candidates)
        except Exception as e:
            log(f"Cycle scan exception: {e}")

        loop_count += 1
        if loop_count % 40 == 0:  # Log status every 10 minutes
            acc_cur = mt5.account_info()
            elapsed_min = int((time.time() - start_time) / 60)
            log(f"[VPS Alive - {elapsed_min}m elapsed] Balance: ${acc_cur.balance:.2f} | Equity: ${acc_cur.equity:.2f}")

        time.sleep(15)  # 15-second tick interval

    log("5-Hour VPS session cycle completed smoothly. Ready for relay.")
    mt5.shutdown()

if __name__ == "__main__":
    main()
