"""
TITAN 5 PURE AUTONOMOUS MINDS + SUPREME GOD ARBITER
Pure Natural Intelligence.
Zero predefined definitions. Zero rigid instructions.
5 independent elite trading intelligences analyzing the raw market in complete freedom,
with 1 Supreme GOD Brain uniting them into absolute execution truth.
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
RSI_LOG_FILE = os.path.join(VAULT_DIR, "recursive_evolution_audit.jsonl")
os.makedirs(VAULT_DIR, exist_ok=True)

def log(msg):
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{ts}] {msg}", flush=True)

def fetch_ticker_quote(ticker):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=15m&range=2d"
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
        pass
    return None

def fetch_live_market_universe():
    symbols = {
        'Gold (XAUUSD)': 'GC=F',
        'Silver (XAGUSD)': 'SI=F',
        'Crude Oil (USOIL)': 'CL=F',
        'Nasdaq 100 (NAS100)': 'NQ=F',
        'US30 (Dow Jones)': '^DJI',
        'Bitcoin (BTCUSD)': 'BTC-USD',
        'Ethereum (ETHUSD)': 'ETH-USD',
        'Solana (SOLUSD)': 'SOL-USD',
        'EURUSD': 'EURUSD=X',
        'GBPUSD': 'GBPUSD=X',
        'USDJPY': 'JPY=X',
        'AUDUSD': 'AUDUSD=X',
        'USDCAD': 'CAD=X'
    }
    snapshot = {}
    for name, sym in symbols.items():
        q = fetch_ticker_quote(sym)
        if q:
            snapshot[name] = q
    return snapshot

def run_pure_natural_intelligence(api_key):
    if not api_key:
        log("No Gemini API key available.")
        return

    now_utc = datetime.datetime.now(datetime.timezone.utc)
    client = genai.Client(api_key=api_key)

    market_data = fetch_live_market_universe()
    log(f"Market realities delivered to 5 Independent Pure Brains ({len(market_data)} live assets).")

    past_records = []
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                past_records = json.load(f).get("historical_insights", [])[-8:]
        except Exception:
            past_records = []

    # 100% UNCONSTRAINED NATURAL INTELLIGENCE META-PROMPT
    pure_prompt = f"""
You are an autonomous intelligence network consisting of 5 INDEPENDENT ELITE TRADING MINDS and 1 SUPREME GOD ARBITER.

### YOUR SOLE & ABSOLUTE MISSION:
Compound this account from $100 to $1,000+ USD within 1 month with ZERO ACCOUNT RUIN.
(Current Account Equity: ~$194.00 USD).
Nobody dictates your strategy, indicators, or methods. You have 100% natural, unconstrained intelligence.
Think, calculate, and act like real-world master traders whose only mandate is to turn $100 into $1,000+ by month-end.

### THE 5 INDEPENDENT MINDS:
- BRAIN 1: Independent Elite Mind (Full autonomy)
- BRAIN 2: Independent Elite Mind (Full autonomy)
- BRAIN 3: Independent Elite Mind (Full autonomy)
- BRAIN 4: Independent Elite Mind (Full autonomy)
- BRAIN 5: Independent Elite Mind (Full autonomy)

Each mind observes the live data, thinks independently, and outputs its raw perspective.

### THE SUPREME GOD BRAIN:
You observe all 5 independent minds.
Your only mission: If there is an absolute, undeniable, high-profit truth in the market with small risk and massive reward, ORDER EXECUTION.
If there is uncertainty or divergence, ORDER WAIT.

### LIVE MARKET REALITY ({now_utc.isoformat()}):
{json.dumps(market_data, indent=2)}

### HISTORICAL NETWORK REFLECTIONS:
{json.dumps(past_records, indent=2)}

Respond STRICTLY in valid JSON:
{{
  "evolution_timestamp": "{now_utc.isoformat()}",
  "cycle_iteration": {len(past_records) + 1},
  "independent_brains": {{
    "brain_1": {{ "raw_thought": "...", "signal": "BUY/SELL/WAIT", "target_asset": "..." }},
    "brain_2": {{ "raw_thought": "...", "signal": "BUY/SELL/WAIT", "target_asset": "..." }},
    "brain_3": {{ "raw_thought": "...", "signal": "BUY/SELL/WAIT", "target_asset": "..." }},
    "brain_4": {{ "raw_thought": "...", "signal": "BUY/SELL/WAIT", "target_asset": "..." }},
    "brain_5": {{ "raw_thought": "...", "signal": "BUY/SELL/WAIT", "target_asset": "..." }}
  }},
  "supreme_god_verdict": {{
    "prime_asset": "Selected asset name",
    "verdict": "BUY or SELL or WAIT",
    "live_price": 0.0,
    "target_liquidity_pool": 0.0,
    "calculated_sl_pips": 20,
    "calculated_tp_pips": 120,
    "projected_rr": "1:6+ or higher",
    "god_brain_synthesis": "Unified truth of execution"
  }},
  "intelligence_evolved": "What new understanding the network acquired independently"
}}
"""
    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=pure_prompt
        )

        clean_json = response.text.strip()
        if "```json" in clean_json:
            clean_json = clean_json.split("```json")[1].split("```")[0].strip()
        elif "```" in clean_json:
            clean_json = clean_json.split("```")[1].split("```")[0].strip()

        try:
            parsed = json.loads(clean_json)
        except Exception:
            parsed = {"raw": response.text.strip()}

        active_bias = parsed.get("supreme_god_verdict", {})
        parsed["active_market_bias"] = active_bias

        all_records = []
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                    all_records = json.load(f).get("historical_insights", [])
            except Exception:
                all_records = []

        all_records.append({
            "timestamp": now_utc.isoformat(),
            "type": "PURE_NATURAL_INTELLIGENCE_CYCLE",
            "market_snapshot": market_data,
            "rsi_evolution": parsed
        })
        all_records = all_records[-250:]

        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump({"total_records": len(all_records), "historical_insights": all_records}, f, indent=2)

        with open(RSI_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(parsed) + "\n")

        log(f"⚡ [GOD BRAIN VERDICT COMPLETE] Supreme Action: {active_bias.get('verdict')} on {active_bias.get('prime_asset')} | Target RR: {active_bias.get('projected_rr')}")

    except Exception as e:
        log(f"Network cycle error: {e}")

def main():
    log("==================================================")
    log("TITAN PURE NATURAL INTELLIGENCE NETWORK ACTIVE")
    log("==================================================")
    api_key = os.getenv("GEMINI_API_KEY", "")
    run_pure_natural_intelligence(api_key)

if __name__ == "__main__":
    main()
