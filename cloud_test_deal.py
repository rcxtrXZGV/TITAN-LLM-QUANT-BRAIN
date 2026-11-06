import os
import sys
import time
import datetime
import MetaTrader5 as mt5

def log(msg):
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{ts}] {msg}", flush=True)

def main():
    log("==========================================")
    log("TITAN CLOUD DEAL FIRE ENGINE - HEADLESS PORTABLE")
    log("==========================================")

    login_str = os.getenv("MT5_LOGIN", "")
    password = os.getenv("MT5_PASSWORD", "")
    server = os.getenv("MT5_SERVER", "ICMarketsSC-Demo")

    if not login_str or not password:
        log("ERROR: MT5 credentials missing from environment secrets!")
        sys.exit(1)

    login = int(login_str)
    
    # Check portable terminal path
    terminal_path = r"C:\MT5\terminal64.exe"
    if not os.path.exists(terminal_path):
        log(f"Custom terminal path not found at {terminal_path}, trying default...")
        terminal_path = None

    log(f"Attempting mt5.initialize(path={terminal_path}, portable=True)...")
    if terminal_path:
        init_ok = mt5.initialize(path=terminal_path, portable=True)
    else:
        init_ok = mt5.initialize()

    if not init_ok:
        err = mt5.last_error()
        log(f"mt5.initialize failed: {err}")
        # Try raw init without portable flag
        if terminal_path:
            log(f"Retrying raw init with path={terminal_path}...")
            init_ok = mt5.initialize(path=terminal_path)
            if not init_ok:
                log(f"Retry failed: {mt5.last_error()}")
                sys.exit(1)
        else:
            sys.exit(1)

    log("MetaTrader 5 terminal initialized successfully!")

    # Attempt Login
    log(f"Logging into account {login} on server '{server}'...")
    authorized = mt5.login(login=login, password=password, server=server)
    if not authorized:
        log(f"Login failed! Error: {mt5.last_error()}")
        mt5.shutdown()
        sys.exit(1)

    acc = mt5.account_info()
    if acc is None:
        log("Failed to get account info!")
        mt5.shutdown()
        sys.exit(1)

    log(f"AUTHENTICATED SUCCESSFUL: {acc.name} | Balance: ${acc.balance:.2f} | Equity: ${acc.equity:.2f} | Leverage: 1:{acc.leverage}")

    # Target Symbol: XAUUSD
    symbol = "XAUUSD"
    if not mt5.symbol_select(symbol, True):
        log(f"Symbol {symbol} select failed, checking alternatives (XAUUSD+, GOLD, etc.)...")
        for sym_cand in ["XAUUSD+", "XAUUSD.", "GOLD", "XAUUSDm"]:
            if mt5.symbol_select(sym_cand, True):
                symbol = sym_cand
                log(f"Selected alternative symbol: {symbol}")
                break

    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        log(f"Failed to fetch market tick for {symbol}. Broker market might be offline or symbol missing.")
        mt5.shutdown()
        sys.exit(1)

    log(f"Live Market Tick for {symbol}: Bid={tick.bid}, Ask={tick.ask}")

    # Asymmetric Risk Parameters: 0.01 lot test deal
    # SL = 25 pips ($2.50), TP = 150 pips ($15.00)
    lot = 0.01
    price = tick.ask
    point = mt5.symbol_info(symbol).point
    sl = price - (250 * point) # 25 pips on gold = $2.50
    tp = price + (1500 * point) # 150 pips on gold = $15.00

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": mt5.ORDER_TYPE_BUY,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 20,
        "magic": 999111,
        "comment": "CLOUD_PIPELINE_TEST",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    log(f"Sending BUY Deal Request: {lot} lots @ {price} | SL: {sl:.2f} | TP: {tp:.2f}...")
    result = mt5.order_send(request)
    
    if result is None:
        log(f"Order send returned None. Error: {mt5.last_error()}")
    elif result.retcode != mt5.TRADE_RETCODE_DONE:
        log(f"Order failed! Retcode: {result.retcode} | Comment: {result.comment}")
        # Try return code check if filling IOC failed, try FOK / RETURN
        if result.retcode in [10030, 10027]: # unsupported filling
            log("Retrying with ORDER_FILLING_RETURN...")
            request["type_filling"] = mt5.ORDER_FILLING_RETURN
            result = mt5.order_send(request)
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                log(f"ORDER EXECUTED! Deal Ticket: {result.deal}, Order Ticket: {result.order}")
            else:
                log(f"Retry failed! Retcode: {result.retcode} | {result.comment}")
    else:
        log("==================================================")
        log(f"SUCCESS! VERIFICATION TRADE EXECUTED LIVE ON BROKER!")
        log(f"Order Ticket : {result.order}")
        log(f"Deal Ticket  : {result.deal}")
        log(f"Volume       : {result.volume} Lots")
        log(f"Executed At  : {result.price}")
        log("==================================================")

    mt5.shutdown()
    log("Cloud MT5 connection shut down safely.")

if __name__ == "__main__":
    main()
