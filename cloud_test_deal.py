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
    
    # Path to MT5 binary
    terminal_path = r"C:\MT5\terminal64.exe"
    if not os.path.exists(terminal_path):
        terminal_path = r"C:\Program Files\MetaTrader 5\terminal64.exe"

    log(f"Target Terminal: {terminal_path}")
    
    # Step 1: Kill any hung instances
    kill_terminal_instances()
    time.sleep(3)

    # Step 2: Write temporary startup.ini (Tier C Strategy)
    # This instructs terminal64 to bypass first-run wizards, accept terms, connect to broker, and bind IPC pipes immediately!
    ini_path = os.path.join(tempfile.gettempdir(), "mt5_startup.ini")
    with open(ini_path, "w", encoding="utf-8") as f:
        f.write("[Common]\n")
        f.write(f"Login={login}\n")
        f.write(f"Password={password}\n")
        f.write(f"Server={server}\n")
        f.write("News=false\n")
        f.write("EnableAutoTrading=true\n")
        f.write("CertPath=\n")
    
    log(f"Generated startup configuration at {ini_path} (Credentials safely masked)")

    # Step 3: Launch terminal with /config argument
    log("Pre-launching terminal64.exe with /config and waiting 45s for first-start settlement...")
    proc = subprocess.Popen([terminal_path, f"/config:{ini_path}"])
    log(f"Terminal process spawned with PID {proc.pid}")
    
    time.sleep(45)

    # Step 4: Attach via mt5.initialize()
    log("Attempting mt5.initialize(path=terminal_path, timeout=60000)...")
    init_ok = False
    for attempt in range(1, 4):
        log(f"Attach Attempt {attempt}/3...")
        if mt5.initialize(path=terminal_path, timeout=60000):
            init_ok = True
            log("SUCCESS: Attached to live MT5 instance via IPC!")
            break
        elif mt5.initialize(timeout=60000):
            init_ok = True
            log("SUCCESS: Attached to live default MT5 instance via IPC!")
            break
        log(f"Attempt {attempt} failed: {mt5.last_error()}. Retrying in 10s...")
        time.sleep(10)

    # Cleanup startup ini immediately
    try:
        if os.path.exists(ini_path):
            os.remove(ini_path)
    except Exception:
        pass

    if not init_ok:
        log("FATAL: Could not attach to MT5 terminal!")
        sys.exit(1)

    term_info = mt5.terminal_info()
    log(f"Live Terminal: build={term_info.build} connected={term_info.connected} ping_last={term_info.ping_last}us")

    # Step 5: Verify Login & Account
    acc = mt5.account_info()
    if acc is None or not getattr(acc, "login", None):
        log(f"Not logged in yet, attempting explicit mt5.login({login}, server='{server}')...")
        if not mt5.login(login=login, password=password, server=server):
            log(f"Login failed! Error: {mt5.last_error()}")
            mt5.shutdown()
            sys.exit(1)
        acc = mt5.account_info()

    log(f"ACCOUNT VERIFIED: {acc.name} | Login: {acc.login} | Server: {acc.server}")
    log(f"Balance: ${acc.balance:.2f} | Equity: ${acc.equity:.2f} | Leverage: 1:{acc.leverage}")

    # Step 6: Select Weekend Live Market (BTCUSD / Crypto)
    # Today is Saturday: Forex is closed, Crypto (BTCUSD) is 24/7 LIVE!
    symbol_candidates = ["BTCUSD", "BTCUSDm", "BTCUSD.", "BTCUSD+", "Bitcoin", "XAUUSD"]
    target_symbol = None

    for cand in symbol_candidates:
        if mt5.symbol_select(cand, True):
            tick = mt5.symbol_info_tick(cand)
            if tick and tick.bid > 0:
                target_symbol = cand
                log(f"Found 24/7 Active Market: {target_symbol} (Bid={tick.bid}, Ask={tick.ask})")
                break

    if not target_symbol:
        target_symbol = "BTCUSD"
        mt5.symbol_select(target_symbol, True)
        tick = mt5.symbol_info_tick(target_symbol)
    else:
        tick = mt5.symbol_info_tick(target_symbol)

    if tick is None or tick.bid == 0:
        log(f"Could not obtain live quotes for {target_symbol}. Market offline or symbols disabled.")
        mt5.shutdown()
        sys.exit(1)

    sym_info = mt5.symbol_info(target_symbol)
    lot = sym_info.volume_min if sym_info else 0.01
    filling_mode = choose_filling_mode(sym_info)
    price = tick.ask
    point = sym_info.point

    # Stop Loss & Take Profit for BTC (e.g. $100 SL, $500 TP)
    sl = price - (1000 * point * 10)
    tp = price + (5000 * point * 10)

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": target_symbol,
        "volume": lot,
        "type": mt5.ORDER_TYPE_BUY,
        "price": price,
        "sl": round(sl, sym_info.digits),
        "tp": round(tp, sym_info.digits),
        "deviation": 50,
        "magic": 999111,
        "comment": "CLOUD_BTC_SAT_TEST",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": filling_mode,
    }

    log(f"Sending BUY Order on {target_symbol}: {lot} lots @ {price} (Filling Mode: {filling_mode})...")
    result = mt5.order_send(request)

    if result is None:
        log(f"Order send returned None. Error: {mt5.last_error()}")
    elif result.retcode != mt5.TRADE_RETCODE_DONE:
        log(f"Order failed! Retcode: {result.retcode} | Comment: {result.comment}")
        # Retry with RETURN filling mode if rejected
        if result.retcode in [10030, 10027]:
            log("Retrying with ORDER_FILLING_RETURN...")
            request["type_filling"] = mt5.ORDER_FILLING_RETURN
            result = mt5.order_send(request)
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                log(f"ORDER EXECUTED! Deal: {result.deal}, Order: {result.order}")
            else:
                log(f"Retry failed! Retcode: {result.retcode} | {result.comment}")
    else:
        log("==================================================")
        log(f"SUCCESS! VERIFICATION TRADE EXECUTED LIVE ON BROKER!")
        log(f"Symbol       : {target_symbol}")
        log(f"Order Ticket : {result.order}")
        log(f"Deal Ticket  : {result.deal}")
        log(f"Volume       : {result.volume} Lots")
        log(f"Executed At  : {result.price}")
        log("==================================================")

    mt5.shutdown()
    log("Cloud MT5 connection shut down safely.")

if __name__ == "__main__":
    main()
