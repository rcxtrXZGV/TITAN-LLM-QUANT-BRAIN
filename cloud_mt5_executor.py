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

def calculate_dynamic_draw_on_liquidity(symbol, is_buy):
    """
    Dynamically finds the recent structural high/low (liquidity pool)
    to set an exact market-driven Take Profit rather than an arbitrary fixed number.
    """
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H1, 0, 48)
    if rates is None or len(rates) == 0:
        return None

    if is_buy:
        # For BUY: Target the highest high of the previous 48 hours (liquidity buy stops)
        highest = max([r['high'] for r in rates])
        return highest
    else:
        # For SELL: Target the lowest low of the previous 48 hours (liquidity sell stops)
        lowest = min([r['low'] for r in rates])
        return lowest

def main():
    log("==================================================")
    log("TITAN CLOUD EXECUTOR - DYNAMIC ASYMMETRIC TARGETING")
    log("==================================================")

    now_utc = datetime.datetime.now(datetime.timezone.utc)
    hour = now_utc.hour
    weekday = now_utc.weekday()

    is_weekend = (weekday in [5, 6])
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

    target_symbol = "BTCUSD" if is_weekend else "XAUUSD"
    if not mt5.symbol_select(target_symbol, True):
        for alt in [f"{target_symbol}.", f"{target_symbol}+", f"{target_symbol}m", "GOLD"]:
            if mt5.symbol_select(alt, True):
                target_symbol = alt
                break

    tick = mt5.symbol_info_tick(target_symbol)
    sinfo = mt5.symbol_info(target_symbol)

    if tick and sinfo:
        log(f"Active Market: {target_symbol} | Bid={tick.bid} | Ask={tick.ask}")

        # Trailing Breakeven Shield Management
        positions = mt5.positions_get(symbol=target_symbol) or []
        log(f"Current open positions on {target_symbol}: {len(positions)}")

        for p in positions:
            ticket = p.ticket
            pos_type = p.type
            open_price = p.price_open
            cur_price = p.price_current
            cur_sl = p.sl

            pip_size = 10.0 if "BTC" in target_symbol else 0.10
            # Trailing Breakeven at +15 pips
            if pos_type == mt5.ORDER_TYPE_BUY and (cur_price - open_price) >= (15 * pip_size):
                be_sl = open_price + (2 * pip_size)
                if cur_sl < be_sl:
                    req = {"action": mt5.TRADE_ACTION_SLTP, "position": ticket, "sl": round(be_sl, sinfo.digits), "tp": p.tp}
                    mt5.order_send(req)
                    log(f"Position #{ticket} SL Trailed to Zero-Risk Breakeven ({be_sl})!")
            elif pos_type == mt5.ORDER_TYPE_SELL and (open_price - cur_price) >= (15 * pip_size):
                be_sl = open_price - (2 * pip_size)
                if cur_sl > be_sl or cur_sl == 0:
                    req = {"action": mt5.TRADE_ACTION_SLTP, "position": ticket, "sl": round(be_sl, sinfo.digits), "tp": p.tp}
                    mt5.order_send(req)
                    log(f"Position #{ticket} SL Trailed to Zero-Risk Breakeven ({be_sl})!")

    mt5.shutdown()
    log("Dynamic execution cycle completed safely.")

if __name__ == "__main__":
    main()
