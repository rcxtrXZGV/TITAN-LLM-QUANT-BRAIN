import os
import sys
import time
import subprocess
import tempfile
import json
import datetime
import MetaTrader5 as mt5

login = int(os.environ.get('MT5_LOGIN', '0'))
password = os.environ.get('MT5_PASSWORD', '')
server = os.environ.get('MT5_SERVER', 'ICMarketsSC-Demo')
terminal_path = r'C:\MT5\terminal64.exe'

ini_path = os.path.join(tempfile.gettempdir(), 'mt5_hist.ini')
with open(ini_path, 'w', encoding='utf-8') as f:
    f.write(f'[Common]\nLogin={login}\nPassword={password}\nServer={server}\n')

subprocess.Popen([terminal_path, f'/config:{ini_path}'])
time.sleep(45)

if not (mt5.initialize(path=terminal_path, timeout=60000) or mt5.initialize(timeout=60000)):
    print('FAILED_TO_CONNECT')
    sys.exit(1)

# Fetch history from past 7 days to now
from_date = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=7)
to_date = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)

deals = mt5.history_deals_get(from_date, to_date)
deal_list = []
if deals:
    for d in deals:
        deal_list.append({
            'ticket': d.ticket,
            'order': d.order,
            'time': datetime.datetime.fromtimestamp(d.time, datetime.timezone.utc).isoformat(),
            'symbol': d.symbol,
            'type': 'BUY' if d.type == 0 else ('SELL' if d.type == 1 else str(d.type)),
            'entry': 'ENTRY_IN' if d.entry == 0 else ('ENTRY_OUT' if d.entry == 1 else str(d.entry)),
            'volume': d.volume,
            'price': d.price,
            'profit': d.profit,
            'comment': d.comment
        })

orders = mt5.history_orders_get(from_date, to_date)
order_list = []
if orders:
    for o in orders:
        order_list.append({
            'ticket': o.ticket,
            'time_setup': datetime.datetime.fromtimestamp(o.time_setup, datetime.timezone.utc).isoformat(),
            'time_done': datetime.datetime.fromtimestamp(o.time_done, datetime.timezone.utc).isoformat() if o.time_done else '',
            'symbol': o.symbol,
            'type': 'BUY' if o.type == 0 else ('SELL' if o.type == 1 else str(o.type)),
            'volume_initial': o.volume_initial,
            'price_open': o.price_open,
            'sl': o.sl,
            'tp': o.tp,
            'state': str(o.state),
            'comment': o.comment
        })

res = {
    'total_deals': len(deal_list),
    'deals': deal_list,
    'total_orders': len(order_list),
    'orders': order_list
}

os.makedirs('brain_vault', exist_ok=True)
with open('brain_vault/broker_deal_history.json', 'w', encoding='utf-8') as f:
    json.dump(res, f, indent=2)

print('===DEAL_HISTORY_SAVED===', len(deal_list), 'deals')
mt5.shutdown()
