import os
import sys
import time
import subprocess
import tempfile
import json
import MetaTrader5 as mt5

login = int(os.environ.get('MT5_LOGIN', '0'))
password = os.environ.get('MT5_PASSWORD', '')
server = os.environ.get('MT5_SERVER', 'ICMarketsSC-Demo')
terminal_path = r'C:\MT5\terminal64.exe'

ini_path = os.path.join(tempfile.gettempdir(), 'mt5_check.ini')
with open(ini_path, 'w', encoding='utf-8') as f:
    f.write(f'[Common]\nLogin={login}\nPassword={password}\nServer={server}\n')

subprocess.Popen([terminal_path, f'/config:{ini_path}'])
time.sleep(45)

if not (mt5.initialize(path=terminal_path, timeout=60000) or mt5.initialize(timeout=60000)):
    print('FAILED_TO_CONNECT')
    sys.exit(1)

acc = mt5.account_info()
pos = mt5.positions_get()
pos_info = []
if pos:
    for p in pos:
        pos_info.append({
            'ticket': p.ticket,
            'symbol': p.symbol,
            'volume': p.volume,
            'open_price': p.price_open,
            'current_price': p.price_current,
            'sl': p.sl,
            'tp': p.tp,
            'profit': p.profit
        })

res = {
    'account_name': acc.name,
    'balance': acc.balance,
    'equity': acc.equity,
    'margin': acc.margin,
    'free_margin': acc.margin_free,
    'open_positions': pos_info
}

# Write directly to brain_vault/broker_account_live.json!
os.makedirs('brain_vault', exist_ok=True)
with open('brain_vault/broker_account_live.json', 'w', encoding='utf-8') as f:
    json.dump(res, f, indent=2)

print('===AUDIT_SUCCESS===')
print(json.dumps(res, indent=2))
mt5.shutdown()
