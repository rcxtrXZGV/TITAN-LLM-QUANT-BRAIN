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

def main():
    log("==================================================")
    log("TITAN CLOUD DEAL FIRE ENGINE - CERTIFIED TIER-C")
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

    # IC Markets Crypto symbols: BTCUSD, ETHUSD, LTCUSD, BCHUSD, XRPUSD
    # Let's inspect crypto group symbols
    crypto_symbols = ["BTCUSD", "ETHUSD", "LTCUSD", "XRPUSD", "BTCUSD.", "ETHUSD."]
    
    target_symbol = None
    target_tick = None
    target_info = None

    for sym in crypto_symbols:
        if mt5.symbol_select(sym, True):
            sinfo = mt5.symbol_info(sym)
            tick = mt5.symbol_info_tick(sym)
            log(f"Checking {sym}: trade_mode={sinfo.trade_mode}, session_deals={sinfo.session_deals}, tick={tick}")
            if tick and tick.bid > 0 and sinfo.trade_mode == mt5.SYMBOL_TRADE_MODE_FULL:
                target_symbol = sym
                target_tick = tick
                target_info = sinfo
                break

    if not target_symbol:
        # Check all symbols in Crypto category
        all_syms = mt5.symbols_get() or []
        for s in all_syms:
            if "Crypto" in getattr(s, "path", "") or s.name in ["BTCUSD", "ETHUSD"]:
                mt5.symbol_select(s.name, True)
                tick = mt5.symbol_info_tick(s.name)
                if tick and tick.bid > 0 and s.trade_mode == mt5.SYMBOL_TRADE_MODE_FULL:
                    target_symbol = s.name
                    target_tick = tick
                    target_info = s
                    log(f"Found active crypto in path {s.path}: {target_symbol}")
                    break

    if not target_symbol:
        log("No open crypto symbol for Saturday trading found on broker!")
        mt5.shutdown()
        sys.exit(1)

    price = target_tick.ask
    lot = target_info.volume_min
    filling_mode = choose_filling_mode(target_info)
    digits = target_info.digits
    point = target_info.point

    sl = price - (5000 * point if point > 0.01 else 50.0)
    tp = price + (15000 * point if point > 0.01 else 150.0)

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": target_symbol,
        "volume": lot,
        "type": mt5.ORDER_TYPE_BUY,
        "price": price,
        "sl": round(sl, digits),
        "tp": round(tp, digits),
        "deviation": 50,
        "magic": 999111,
        "comment": "CLOUD_BTC_SAT_TEST",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": filling_mode,
    }

    log(f"Executing BUY Order: {lot} lots on {target_symbol} @ {price}...")
    res = mt5.order_send(request)
    if res and res.retcode == mt5.TRADE_RETCODE_DONE:
        log("==================================================")
        log("SUCCESS! CLOUD ORDER EXECUTED LIVE ON BROKER!")
        log(f"Symbol       : {target_symbol}")
        log(f"Order Ticket : {res.order}")
        log(f"Deal Ticket  : {res.deal}")
        log(f"Executed At  : {res.price}")
        log("==================================================")
    else:
        log(f"Order retcode: {getattr(res, 'retcode', None)} | comment: {getattr(res, 'comment', None)}")

    mt5.shutdown()

if __name__ == "__main__":
    main()
