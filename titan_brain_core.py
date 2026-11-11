"""
TITAN LIVE GROUNDED LLM ENGINE (REAL MARKET INGESTION)
Injects Live Price Candles & Spreads from yfinance into Gemini Prompt
Directly writes optimal institutional bias into brain memory.
"""

import os
import sys
import json
import time
import datetime
import urllib.request
import yfinance as yf
from google import genai

VAULT_DIR = "brain_vault"
MEMORY_FILE = os.path.join(VAULT_DIR, "trading_llm_memory.json")
os.makedirs(VAULT_DIR, exist_ok=True)

def log(msg):
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{ts}] {msg}", flush=True)

def fetch_live_market_data():
    symbols = {
        'Gold': 'GC=F',
        'EURUSD': 'EURUSD=X',
        'GBPUSD': 'GBPUSD=X',
        'USDJPY': 'JPY=X',
        'Bitcoin': 'BTC-USD',
        'US30': '^DJI'
    }
    market_snapshot = {}
    for name, ticker in symbols.items():
        try:
            df = yf.download(ticker, period='1d', interval='15m', progress=False)
            if len(df) >= 10:
                c_now = df.iloc[-1]
                c_prev = df.iloc[-2]
                high_range = float(df['High'].max())
                low_range = float(df['Low'].min())
                close_now = float(c_now['Close'])
                close_prev = float(c_prev['Close'])
                market_snapshot[name] = {
                    'close': round(close_now, 4),
                    'session_high': round(high_range, 4),
                    'session_low': round(low_range, 4),
                    'momentum_delta': round(close_now - close_prev, 4)
                }
        except Exception as e:
            pass
    return market_snapshot

def autonomous_gemini_dynamic_evaluator(api_key):
    if not api_key:
        return

    now_utc = datetime.datetime.now(datetime.timezone.utc)
    client = genai.Client(api_key=api_key)

    market_data = fetch_live_market_data()
    log(f"Fetched real-time live data for {len(market_data)} global assets.")

    prompt = f"""
You are the TITAN REAL QUANT BRAIN.
Analyze this ACTUAL REAL-TIME market snapshot captured at {now_utc.isoformat()}:
{json.dumps(market_data, indent=2)}

TASK:
1. Identify the single asset with the cleanest institutional imbalance or session sweep right now.
2. Formulate an exact Draw on Liquidity target based on the provided session highs/lows.
3. Keep Stop Loss strictly <= 25 pips ($2.00 max risk).

Respond with valid JSON:
{{
  "evaluation_time": "{now_utc.isoformat()}",
  "selected_prime_asset": "Name of best asset from the data",
  "live_market_bias": "BULLISH or BEARISH",
  "reasoning_from_live_data": "Exact numbers from the snapshot justifying this decision",
  "draw_on_liquidity_target": "Price level where resting orders lie",
  "calculated_sl_pips": 20,
  "calculated_tp_pips": 150,
  "verdict": "BUY or SELL or WAIT"
}}
"""
    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt
        )

        analysis = response.text.strip()
        log("Grounded Gemini 3.5 live evaluation successfully generated!")

        clean_json = analysis
        if "```json" in clean_json:
            clean_json = clean_json.split("```json")[1].split("```")[0].strip()
        elif "```" in clean_json:
            clean_json = clean_json.split("```")[1].split("```")[0].strip()

        try:
            parsed = json.loads(clean_json)
        except Exception:
            parsed = {"raw": analysis}

        records = []
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                    records = json.load(f).get("historical_insights", [])
            except Exception:
                records = []

        records.append({
            "timestamp": now_utc.isoformat(),
            "type": "REAL_GROUNDED_EVALUATION",
            "market_snapshot": market_data,
            "data": parsed
        })
        records = records[-150:]

        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump({"total_records": len(records), "historical_insights": records}, f, indent=2)

        log("Real grounded evaluation saved to brain memory.")

    except Exception as e:
        log(f"Evaluation error: {e}")

def main():
    log("==================================================")
    log("TITAN UNBOUND: REAL-TIME GROUNDED MARKET INGESTION")
    log("==================================================")
    api_key = os.getenv("GEMINI_API_KEY", "")
    autonomous_gemini_dynamic_evaluator(api_key)

if __name__ == "__main__":
    main()
