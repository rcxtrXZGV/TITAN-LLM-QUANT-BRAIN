"""
TITAN SUPREME AUTONOMOUS QUANT SYNDICATE
Core Architecture: 5 Independent Sovereign Elite Minds + 1 Supreme God Arbiter
Ground Rules:
1. 100% Complete Freedom. Zero Rigid Boxes. Zero Scripted Limitations.
2. Single Absolute Objective: Compound $100 -> $1,000+ USD within 1 month at ANY COST.
3. Zero Hallucination: Targets must be real, reachable intraday institutional liquidity levels (Session High/Low, Previous Day High/Low, 2-Day Range Extremes).
4. Asymmetric Precision: Strict small risk ($0.70 - $2.50) targeting massive real-world rewards (1:6+ to 1:20+).
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

def run_supreme_syndicate(api_key):
    if not api_key:
        log("No Gemini API key available.")
        return

    now_utc = datetime.datetime.now(datetime.timezone.utc)
    client = genai.Client(api_key=api_key)

    market_data = fetch_live_market_universe()
    log(f"Multi-asset feed delivered to Syndicate ({len(market_data)} assets).")

    past_records = []
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                past_records = json.load(f).get("historical_insights", [])[-8:]
        except Exception:
            past_records = []

    # THE ABSOLUTE CLARITY DIRECTIVE
    master_directive = f"""
LISTEN CAREFULLY. THIS IS A COMPLETE RESET TO ABSOLUTE CLARITY FOR ALL 5 MINDS AND THE SUPREME GOD BRAIN.

1. YOU ARE 100% FREE:
   - You are not in any box. Nobody is telling you what indicators, formulas, or strategies to use.
   - You have complete sovereign freedom to analyze, think, and trade however you want.

2. YOUR SOLE & ABSOLUTE MISSION:
   - Compound this account from $100 to $1,000+ USD within 1 month AT ANY COST.
   - Every trade must be taken with the mindset of turning this small capital into $1,000+ while preserving the principal ($0 account ruin).

3. ZERO HALLUCINATION (GROUND TRUTH REALITY ONLY):
   - DO NOT hallucinate imaginary targets (e.g. Gold at 6000+ when it is at 3790). That is pure fiction.
   - Your Take Profit (TP) MUST be real, reachable intraday institutional liquidity levels:
     * Today's Session High / Session Low
     * Previous Day's High / Low
     * 2-Day Range Breakout / Reversal Extremes
   - A real 1:6 to 1:20 asymmetric move captures $15 to $35 real cash on 0.01 lot. That is how $100 compounds to $1,000+.

4. HOW YOU OPERATE:
   - 5 INDEPENDENT ELITE MINDS observe the raw market realities, think in complete freedom, and formulate independent trade opportunities.
   - THE SUPREME GOD BRAIN synthesizes the 5 minds:
     * If an unmistakable, reachable, high-profit sniper trade exists -> ORDER IMMEDIATE EXECUTION (BUY or SELL) with real SL and real TP.
     * If there is noise or no clear edge -> ORDER RUTHLESS PATIENCE (WAIT).

### REAL-TIME LIVE 13-ASSET MARKET SNAPSHOT ({now_utc.isoformat()}):
{json.dumps(market_data, indent=2)}

### HISTORICAL SYNDICATE REFLECTIONS:
{json.dumps(past_records, indent=2)}

Respond STRICTLY in valid JSON:
{{
  "evolution_timestamp": "{now_utc.isoformat()}",
  "cycle_iteration": {len(past_records) + 1},
  "syndicate_clarity_status": "All 5 minds and God Brain aligned: 100% Free, Zero Box, Zero Hallucination, $100 to $1,000+ Mission Active",
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
    "god_brain_synthesis": "Unified truth of execution based strictly on reachable intraday liquidity"
  }},
  "month_end_compounding_step": "Specific contribution toward the $100 -> $1,000+ objective"
}}
"""
    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=master_directive
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
            "type": "SUPREME_SYNDICATE_UNBOXED_CYCLE",
            "market_snapshot": market_data,
            "rsi_evolution": parsed
        })
        all_records = all_records[-250:]

        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump({"total_records": len(all_records), "historical_insights": all_records}, f, indent=2)

        with open(RSI_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(parsed) + "\n")

        log(f"👑 [GOD BRAIN GROUNDED & UNBOXED] Asset: {active_bias.get('prime_asset')} | Verdict: {active_bias.get('verdict')} | Real TP: {active_bias.get('target_liquidity_pool')} | RR: {active_bias.get('projected_rr')}")

    except Exception as e:
        log(f"Syndicate cycle error: {e}")

def main():
    log("==================================================")
    log("TITAN SUPREME SYNDICATE ENGINE INITIALIZED")
    log("==================================================")
    api_key = os.getenv("GEMINI_API_KEY", "")
    run_supreme_syndicate(api_key)

if __name__ == "__main__":
    main()
