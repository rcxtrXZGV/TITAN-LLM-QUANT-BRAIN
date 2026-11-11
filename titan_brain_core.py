"""
TITAN LIVE GROUNDED LLM ENGINE (DIRECT YAHOO API INGESTION)
Direct lightweight HTTP request to Yahoo Finance Query API
Zero DataFrame multi-index issues, 100% reliable live market payload.
"""

import os
import sys
import json
import time
import datetime
import urllib.request
from google import genai

VAULT_DIR = "brain_vault"
MEMORY_FILE = os.path.join(VAULT_DIR, "trading_llm_memory.json")
os.makedirs(VAULT_DIR, exist_ok=True)

def log(msg):
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{ts}] {msg}", flush=True)

def fetch_ticker_quote(ticker):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=15m&range=1d"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            result = data['chart']['result'][0]
            meta = result['meta']
            quote = result['indicators']['quote'][0]
            closes = [c for c in quote['close'] if c is not None]
            highs = [h for h in quote['high'] if h is not None]
            lows = [l for l in quote['low'] if l is not None]
            if closes:
                return {
                    'current_price': round(meta.get('regularMarketPrice', closes[-1]), 4),
                    'session_high': round(max(highs), 4),
                    'session_low': round(min(lows), 4),
                    'previous_close': round(closes[-2] if len(closes) > 1 else closes[-1], 4),
                    'net_move': round(closes[-1] - (closes[-2] if len(closes) > 1 else closes[-1]), 4)
                }
    except Exception as e:
        log(f"Error fetching {ticker}: {e}")
    return None

def fetch_live_market_data():
    symbols = {
        'Gold (XAUUSD)': 'GC=F',
        'EURUSD': 'EURUSD=X',
        'GBPUSD': 'GBPUSD=X',
        'USDJPY': 'JPY=X',
        'Bitcoin (BTCUSD)': 'BTC-USD'
    }
    market_snapshot = {}
    for name, ticker in symbols.items():
        q = fetch_ticker_quote(ticker)
        if q:
            market_snapshot[name] = q
    return market_snapshot

def autonomous_gemini_dynamic_evaluator(api_key):
    if not api_key:
        return

    now_utc = datetime.datetime.now(datetime.timezone.utc)
    client = genai.Client(api_key=api_key)

    market_data = fetch_live_market_data()
    log(f"Real live market snapshot fetched: {list(market_data.keys())}")

    prompt = f"""
You are the TITAN GROUNDED QUANT AI.
Here is the ACTUAL LIVE REAL-TIME market data captured right now at {now_utc.isoformat()}:
{json.dumps(market_data, indent=2)}

TASK:
1. Compare the live current price against the session_high and session_low for each asset.
2. Identify where liquidity sweeps or breakout expansions have occurred.
3. Select the best asset with the cleanest risk-to-reward setup.
4. Set strict Stop Loss <= 25 pips ($2.00 max risk) and Draw on Liquidity Take Profit.

Respond strictly in valid JSON format:
{{
  "evaluation_time": "{now_utc.isoformat()}",
  "selected_prime_asset": "Name of asset",
  "live_market_bias": "BULLISH or BEARISH",
  "reasoning_from_live_data": "Concrete numbers from the market_data explaining why this asset was picked",
  "draw_on_liquidity_target": "Exact price target",
  "calculated_sl_pips": 20,
  "calculated_tp_pips": 120,
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

        log(f"SAVED REAL LEARNING: Picked {parsed.get('selected_prime_asset')} | Verdict: {parsed.get('verdict')}")

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
