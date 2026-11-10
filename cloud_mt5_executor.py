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

def find_best_active_symbol(candidates):
    """
    Scans a multi-asset universe (Gold, BTC, ETH, EURUSD, US30)
    and selects the symbol with the cleanest trending momentum & liquidity.
    """
    best_symbol = None
    best_score = -1.0
    best_sinfo = None
    best_tick = None

    for sym in candidates:
        if not mt5.symbol_select(sym, True):
            continue
        sinfo = mt5.symbol_info(sym)
        tick = mt5.symbol_info_tick(sym)
        if not sinfo or not tick or tick.bid <= 0 or sinfo.trade_mode != mt5.SYMBOL_TRADE_MODE_FULL:
            continue

        # Fetch recent M15 volatility & spread health
        rates = mt5.copy_rates_from_pos(sym, mt5.TIMEFRAME_M15, 0, 16)
        if rates is None or len(rates) < 10:
            continue

        spread = tick.ask - tick.bid
        high_low_range = max([r['high'] for r in rates]) - min([r['low'] for r in rates])
        
        # Volatility to spread ratio (higher is better for clean moves)
        if spread > 0:
            quality_score = high_low_range / spread
            if quality_score > best_score:
                best_score = quality_score
                best_symbol = sym
                best_sinfo = sinfo
                best_tick = tick

    return best_symbol, best_sinfo, best_tick

def main():
    log("==================================================")
    log("TITAN CLOUD EXECUTOR - MULTI-ASSET OPPORTUNITY HUNTER")
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
    log(f"AUTHENTICATED: {acc.name} | Balance: ${acc.balance:.2f} | Server: {acc.server}")

    # MULTI-ASSET UNIVERSE: Gold, Crypto, Major FX & Indices
    candidates = [
        "XAUUSD", "BTCUSD", "ETHUSD", "EURUSD", "GBPUSD", "USDJPY", "US30", "NAS100"
    ]
    
    target_symbol, sinfo, tick = find_best_active_symbol(candidates)
    if not target_symbol:
        log("No eligible liquid symbol available right now.")
        mt5.shutdown()
        return

    log(f"Selected Prime Opportunity Asset: {target_symbol} | Bid={tick.bid} | Ask={tick.ask}")

    # Trailing Breakeven Shield Management on all open positions
    open_positions = mt5.positions_get() or []
    log(f"Total open positions across all assets: {len(open_positions)}")

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

    mt5.shutdown()
    log("Multi-asset dynamic execution cycle completed safely.")

if __name__ == "__main__":
    main()
