import os
import sys
import time
import datetime
import MetaTrader5 as mt5

def log(msg):
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{ts}] {msg}", flush=True)

def main():
    log("==================================================")
    log("TITAN CLOUD DEAL FIRE ENGINE - DIRECT EXECUTION")
    log("==================================================")

    login_str = os.getenv("MT5_LOGIN", "")
    password = os.getenv("MT5_PASSWORD", "")
    server = os.getenv("MT5_SERVER", "ICMarketsSC-Demo")

    if not login_str or not password:
        log("ERROR: MT5 credentials missing from environment secrets!")
        sys.exit(1)

    login = int(login_str)
    terminal_path = r"C:\MT5\terminal64.exe"

    log("Connecting to running MT5 instance with 30s timeout...")
    init_ok = False
    for attempt in range(1, 4):
        log(f"Initialize attempt {attempt}/3...")
        if mt5.initialize(path=terminal_path, timeout=30000, portable=True):
            init_ok = True
            break
        elif mt5.initialize(timeout=30000):
            init_ok = True
            break
        log(f"Attempt {attempt} failed: {mt5.last_error()}. Retrying in 3s...")
        time.sleep(3)

    if not init_ok:
        log(f"Fatal: Could not initialize MT5. Error: {mt5.last_error()}")
        sys.exit(1)

    log("MetaTrader 5 terminal initialized successfully!")

    log(f"Authenticating login {login} on {server}...")
    auth = mt5.login(login=login, password=password, server=server)
    if not auth:
        log(f"Login failed! Error: {mt5.last_error()}")
        # Check if already authenticated via pre-configured files
        acc = mt5.account_info()
        if acc is None:
            mt5.shutdown()
            sys.exit(1)
        else:
            log(f"Already authenticated as: {acc.name} ({acc.login})")
    else:
        acc = mt5.account_info()

    log(f"BROKER CONNECTED: {acc.name} | Balance: ${acc.balance:.2f} | Equity: ${acc.equity:.2f} | Leverage: 1:{acc.leverage}")

    # Select Symbol
    symbol = "XAUUSD"
    if not mt5.symbol_select(symbol, True):
        for sym_cand in ["XAUUSD+", "XAUUSD.", "GOLD", "XAUUSDm"]:
            if mt5.symbol_select(sym_cand, True):
                symbol = sym_cand
                log(f"Selected symbol: {symbol}")
                break

    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        log(f"Could not get tick for {symbol}. Market might be closed or broker weekend.")
        mt5.shutdown()
        sys.exit(1)

    log(f"Live Tick: Bid={tick.bid}, Ask={tick.ask}")

    # Asymmetric 0.01 lot test deal
    lot = 0.01
    price = tick.ask
    point = mt5.symbol_info(symbol).point
    sl = price - (250 * point) # $2.50 SL
    tp = price + (1500 * point) # $15.00 TP

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": mt5.ORDER_TYPE_BUY,
        "price": price,
        "sl": round(sl, 2),
        "tp": round(tp, 2),
        "deviation": 20,
        "magic": 999111,
        "comment": "CLOUD_PIPELINE_TEST",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    log(f"Sending BUY Deal: {lot} lots @ {price} | SL: {sl:.2f} | TP: {tp:.2f}...")
    result = mt5.order_send(request)
    
    if result is None:
        log(f"Order send returned None. Error: {mt5.last_error()}")
    elif result.retcode != mt5.TRADE_RETCODE_DONE:
        log(f"Order failed (retcode={result.retcode}): {result.comment}")
        if result.retcode in [10030, 10027]:
            log("Retrying with ORDER_FILLING_RETURN...")
            request["type_filling"] = mt5.ORDER_FILLING_RETURN
            result = mt5.order_send(request)
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                log(f"ORDER EXECUTED! Deal: {result.deal}, Order: {result.order}")
            else:
                log(f"Retry failed: {result.retcode} | {result.comment}")
    else:
        log("==================================================")
        log("SUCCESS! VERIFICATION TRADE EXECUTED LIVE ON BROKER!")
        log(f"Order Ticket : {result.order}")
        log(f"Deal Ticket  : {result.deal}")
        log(f"Price        : {result.price}")
        log(f"Balance      : ${acc.balance:.2f}")
        log("==================================================")

    mt5.shutdown()
    log("Cloud MT5 session completed.")

if __name__ == "__main__":
    main()
