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
    if filling_flags & 1:
        return mt5.ORDER_FILLING_FOK
    if filling_flags & 2:
        return mt5.ORDER_FILLING_IOC
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

    if not login_str or not password:
        log("ERROR: MT5 credentials missing from environment secrets!")
        sys.exit(1)

    login = int(login_str)
    terminal_path = r"C:\MT5\terminal64.exe"
    if not os.path.exists(terminal_path):
        terminal_path = r"C:\Program Files\MetaTrader 5\terminal64.exe"

    log(f"Target Terminal: {terminal_path}")
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
        f.write("CertPath=\n")
    
    log("Generated startup config. Spawning terminal64.exe with /config...")
    proc = subprocess.Popen([terminal_path, f"/config:{ini_path}"])
    time.sleep(45)

    log("Attaching via mt5.initialize()...")
    init_ok = False
    for attempt in range(1, 4):
        if mt5.initialize(path=terminal_path, timeout=60000) or mt5.initialize(timeout=60000):
            init_ok = True
            log("SUCCESS: Attached to live MT5 instance via IPC!")
            break
        time.sleep(10)

    try:
        if os.path.exists(ini_path):
            os.remove(ini_path)
    except Exception:
        pass

    if not init_ok:
        log("FATAL: Could not attach to MT5 terminal!")
        sys.exit(1)

    term_info = mt5.terminal_info()
    log(f"Live Terminal: build={term_info.build} connected={term_info.connected} ping={term_info.ping_last}us")

    acc = mt5.account_info()
    if acc is None or not getattr(acc, "login", None):
        mt5.login(login=login, password=password, server=server)
        acc = mt5.account_info()

    log(f"ACCOUNT VERIFIED: {acc.name} | Login: {acc.login} | Server: {acc.server}")
    log(f"Balance: ${acc.balance:.2f} | Equity: ${acc.equity:.2f} | Leverage: 1:{acc.leverage}")

    # Inspect all broker symbols to discover active crypto symbols
    all_symbols = mt5.symbols_get() or []
    log(f"Total symbols configured on broker server: {len(all_symbols)}")
    
    # Filter crypto / weekend tradeable symbols
    candidates = []
    for s in all_symbols:
        name = s.name.upper()
        if any(c in name for c in ["BTC", "ETH", "CRYPTO", "BITCOIN", "SOL"]):
            candidates.append(s.name)

    log(f"Discovered Crypto Symbol Candidates ({len(candidates)}): {candidates[:15]}")

    # Find first live tradeable symbol with active tick
    target_symbol = None
    target_tick = None

    # Check candidates
    for cand in candidates + ["BTCUSD", "BTCUSD.", "BTCUSD+", "BTCUSDT", "ETHUSD"]:
        mt5.symbol_select(cand, True)
        time.sleep(0.5)
        tick = mt5.symbol_info_tick(cand)
        if tick and tick.bid > 0 and tick.ask > 0:
            target_symbol = cand
            target_tick = tick
            log(f">>> SELECTED LIVE MARKET: {target_symbol} | Bid={tick.bid} | Ask={tick.ask} <<<")
            break

    if not target_symbol:
        log("No live crypto tick found with initial candidates, scanning all selected symbols...")
        for s in all_symbols:
            if "USD" in s.name.upper():
                mt5.symbol_select(s.name, True)
                tick = mt5.symbol_info_tick(s.name)
                if tick and tick.bid > 0:
                    target_symbol = s.name
                    target_tick = tick
                    log(f"Found active symbol: {target_symbol} | Bid={tick.bid}")
                    break

    if not target_symbol or not target_tick:
        log("ERROR: Broker currently has no live ticks streaming. Weekend maintenance may be active.")
        mt5.shutdown()
        sys.exit(1)

    sym_info = mt5.symbol_info(target_symbol)
    lot = sym_info.volume_min if sym_info else 0.01
    filling_mode = choose_filling_mode(sym_info)
    price = target_tick.ask
    point = sym_info.point
    digits = sym_info.digits

    # Conservative test bracket
    sl = price - (1000 * point if point > 0.01 else 20.0)
    tp = price + (5000 * point if point > 0.01 else 100.0)

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

    log(f"Sending BUY Deal: {lot} lots on {target_symbol} @ {price} (Filling Mode: {filling_mode})...")
    result = mt5.order_send(request)

    if result is None:
        log(f"Order send returned None. Error: {mt5.last_error()}")
    elif result.retcode != mt5.TRADE_RETCODE_DONE:
        log(f"Order retcode={result.retcode} ({result.comment}), retrying with ORDER_FILLING_RETURN...")
        request["type_filling"] = mt5.ORDER_FILLING_RETURN
        result = mt5.order_send(request)
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            log("==================================================")
            log("SUCCESS! CLOUD ORDER EXECUTED LIVE ON BROKER!")
            log(f"Symbol       : {target_symbol}")
            log(f"Order Ticket : {result.order}")
            log(f"Deal Ticket  : {result.deal}")
            log(f"Price        : {result.price}")
            log("==================================================")
        else:
            log(f"Order execution rejected: retcode={result.retcode} | {result.comment}")
    else:
        log("==================================================")
        log("SUCCESS! CLOUD ORDER EXECUTED LIVE ON BROKER!")
        log(f"Symbol       : {target_symbol}")
        log(f"Order Ticket : {result.order}")
        log(f"Deal Ticket  : {result.deal}")
        log(f"Price        : {result.price}")
        log("==================================================")

    mt5.shutdown()
    log("Cloud MT5 connection shut down safely.")

if __name__ == "__main__":
    main()
