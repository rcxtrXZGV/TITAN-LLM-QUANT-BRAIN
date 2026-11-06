import os
import json
import datetime
import urllib.request
import yfinance as yf
import pandas as pd

# Load or init brain memory
VAULT_DIR = "brain_vault"
MEMORY_FILE = os.path.join(VAULT_DIR, "trading_llm_memory.json")
KNOWLEDGE_FILE = os.path.join(VAULT_DIR, "institutional_knowledge.jsonl")

os.makedirs(VAULT_DIR, exist_ok=True)

def log(msg):
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{now}] {msg}", flush=True)

# 1. Harvest & Synthesize Institutional Knowledge (Wikipedia & Quant Books)
KNOWLEDGE_TOPICS = [
    'Candlestick_pattern', 'Price_action', 'Market_structure',
    'Order_flow', 'Wyckoff_method', 'Algorithmic_trading'
]

def harvest_core_knowledge():
    log("Ingesting institutional price action corpus...")
    headers = {'User-Agent': 'Mozilla/5.0'}
    entries = []
    for topic in KNOWLEDGE_TOPICS:
        url = f'https://en.wikipedia.org/api/rest_v1/page/summary/{topic}'
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                entries.append({
                    "topic": data.get("title", topic),
                    "summary": data.get("extract", "")
                })
        except Exception as e:
            log(f"Topic {topic} skipped: {e}")

    with open(KNOWLEDGE_FILE, "w", encoding="utf-8") as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    log(f"Knowledge vault updated with {len(entries)} core modules.")

# 2. Daily Market Evaluation & Simulation (1 Sniper Trade / Day)
def evaluate_daily_market():
    log("Pulling daily XAUUSD market structure...")
    try:
        df = yf.download("GC=F", period="5d", interval="1h", progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0].lower() for col in df.columns]
        else:
            df.columns = [col.lower() for col in df.columns]
        df = df.dropna()
        
        last_bar = df.iloc[-1]
        prev_bar = df.iloc[-2]
        
        high = float(last_bar['high'])
        low = float(last_bar['low'])
        close = float(last_bar['close'])
        open_p = float(last_bar['open'])
        rng = high - low
        wick_up = high - max(open_p, close)
        wick_down = min(open_p, close) - low
        
        # Self-Evolving Trade Logic
        trade_signal = None
        if wick_up >= 0.50 * rng and close < open_p:
            trade_signal = {
                "action": "SELL",
                "entry": round(close, 2),
                "sl": round(high + 0.50, 2),
                "tp": round(close - 12.0, 2),
                "rationale": "Upper Liquidity Sweep Pin-Bar Rejection"
            }
        elif wick_down >= 0.50 * rng and close > open_p:
            trade_signal = {
                "action": "BUY",
                "entry": round(close, 2),
                "sl": round(low - 0.50, 2),
                "tp": round(close + 12.0, 2),
                "rationale": "Lower Liquidity Sweep Pin-Bar Rejection"
            }
        else:
            trade_signal = {
                "action": "WAIT",
                "rationale": "No clean institutional wick rejection; capital preserved."
            }

        # Update Memory
        mem = {}
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, "r") as f:
                    mem = json.load(f)
            except:
                pass
                
        mem.setdefault("system", "TITAN-LLM-QUANT-BRAIN")
        mem.setdefault("version", "1.0-SELF-EVOLVING")
        mem["last_run_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        signals = mem.setdefault("signal_history", [])
        signals.append({
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "signal": trade_signal
        })
        mem["signal_history"] = signals[-50:] # keep last 50
        
        with open(MEMORY_FILE, "w") as f:
            json.dump(mem, f, indent=2)
            
        log(f"Daily Verdict: {trade_signal['action']} | Reason: {trade_signal['rationale']}")
    except Exception as e:
        log(f"Market evaluation error: {e}")

if __name__ == "__main__":
    harvest_core_knowledge()
    evaluate_daily_market()
