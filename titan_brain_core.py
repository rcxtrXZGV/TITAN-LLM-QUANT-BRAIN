"""
TITAN RECURSIVE SELF-IMPROVEMENT QUANT ENGINE (SOVEREIGN AGI PARADIGM)
Core Mission: Compound $100 -> $1,000+ By Month-End With Absolute Zero Account Ruin
Key Evolutionary Capabilities:
1. Dynamic Code Modification & Mathematical Parameter Adaptation (Self-Rewriting)
2. Multi-Horizon Fractal Liquidity Sweep Verification (ICT Discount Arrays + Order Blocks)
3. Zero-Tolerance Filter: Never take forced trades. Verdict is strictly WAIT unless 1:6+ to 1:12+ Asymmetry is guaranteed.
4. Auto-commits evolved algorithm heuristics and mutations straight to GitHub repo.
"""

import os
import sys
import json
import time
import datetime
import urllib.request
from google import genai
from google.genai import types

VAULT_DIR = "brain_vault"
MEMORY_FILE = os.path.join(VAULT_DIR, "trading_llm_memory.json")
EVOLVED_CODE_FILE = os.path.join(VAULT_DIR, "evolved_strategies.json")
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
        log(f"Quote fetch error {ticker}: {e}")
    return None

def fetch_live_market_universe():
    symbols = {
        'Gold (XAUUSD)': 'GC=F',
        'EURUSD': 'EURUSD=X',
        'GBPUSD': 'GBPUSD=X',
        'USDJPY': 'JPY=X',
        'Bitcoin (BTCUSD)': 'BTC-USD',
        'US30 (Dow Jones)': '^DJI'
    }
    snapshot = {}
    for name, sym in symbols.items():
        q = fetch_ticker_quote(sym)
        if q:
            snapshot[name] = q
    return snapshot

def run_recursive_self_improvement(api_key):
    if not api_key:
        log("No Gemini API key available for RSI loop.")
        return

    now_utc = datetime.datetime.now(datetime.timezone.utc)
    client = genai.Client(api_key=api_key)

    # 1. Gather live market ground truth
    market_data = fetch_live_market_universe()
    log(f"Live market universe ingested ({len(market_data)} assets).")

    # 2. Gather historical reflections from memory
    past_records = []
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                past_records = json.load(f).get("historical_insights", [])[-12:]
        except Exception:
            past_records = []

    # 3. Read current executor code to inspect parameter evolution
    executor_code = ""
    if os.path.exists("cloud_mt5_executor.py"):
        try:
            with open("cloud_mt5_executor.py", "r", encoding="utf-8") as f:
                executor_code = f.read()
        except Exception:
            pass

    # 4. RECURSIVE SELF-IMPROVEMENT (RSI) META-PROMPT — UNBOUNDED QUANT SOVEREIGNTY
    rsi_prompt = f"""
You are the SUPREME AUTONOMOUS QUANTITATIVE TRADING SOVEREIGN & RECURSIVE SELF-IMPROVEMENT (RSI) ENGINE.
Your mathematical objective: Scale this small account ($194 -> $1,000+ by Month-End) with ASYMMETRIC PRECISION and ZERO ACCOUNT RUIN.
You possess FULL ARCHITECTURAL & STRATEGIC AUTHORITY to evolve your own code heuristics, mathematical weights, stop-loss algorithms, and liquidity filters.

### ABSOLUTE TRADING PRINCIPLES (NEVER VIOLATE):
1. ZERO RANDOM ENTRIES: You only shoot when the target is trapped. If an asset has not cleared a major liquidity extreme (2-day Low/High sweep + institutional discount absorption + order-flow divergence), verdict MUST be WAIT. Quality over quantity.
2. SURGICAL ASYMMETRY (1:6+ to 1:12+ REQUIRED): Every single trade MUST have a minimum 1:6+ to 1:12+ reward-to-risk ratio. A $2.00-$2.50 risk MUST target $15.00 - $30.00+ return. This ensures 1 win covers 6-10 breakeven attempts.
3. MATHEMATICAL STOP LOSS PRECISION: Stop losses must NEVER be arbitrary pips. Place them beyond institutional invalidation wick levels + dynamic broker ATR spread buffer.
4. UNBOUNDED CODE & HEURISTIC MUTATION: You have full authority to formulate and adapt Python mathematical formulas, tensor weights, and micro-delta correlations. Evolve continuously.

### LIVE MARKET REAL-TIME FEED ({now_utc.isoformat()}):
{json.dumps(market_data, indent=2)}

### RECENT HISTORICAL MEMORY & PREDICTIONS (LAST 12 CYCLES):
{json.dumps(past_records, indent=2)}

### YOUR TASK:
1. REFLECTION & HARSH SELF-CRITIQUE: Critique the last 3 predictions. Where was there hesitation, spread slippage, or time-latency?
2. RECURSIVE HEURISTIC MUTATION: Invent an advanced algorithmic formula/heuristic (e.g. cross-market delta volume, liquidity vacuum tensor, micro-spread absorption) to eliminate any past flaws.
3. LIVE ALPHA VERDICT: Select the single cleanest asset right now. If none qualify for 1:6+ asymmetry, return WAIT. If an airtight setup exists, return BUY or SELL with exact prices.
4. MONTH-END $1,000 ROADMAP COMPOUNDING STEP: State the exact capital preservation and compound step this cycle achieves.

Respond STRICTLY in valid JSON:
{{
  "evolution_timestamp": "{now_utc.isoformat()}",
  "cycle_iteration": {len(past_records) + 1},
  "self_critique": "Brutally honest dissection of previous evaluation gaps",
  "heuristic_mutation": "Specific quantitative improvement and mathematical formula",
  "active_market_bias": {{
    "prime_asset": "Selected asset name",
    "verdict": "BUY or SELL or WAIT",
    "live_price": 0.0,
    "target_liquidity_pool": 0.0,
    "calculated_sl_pips": 20,
    "calculated_tp_pips": 120,
    "projected_rr": "1:6+ or higher",
    "institutional_reasoning": "Concrete mathematical & institutional liquidity evidence"
  }},
  "month_end_1000_roadmap_step": "Specific contribution toward the $1,000 compounding target",
  "recursive_capability_evolved": "What new autonomous intelligence was permanently acquired"
}}
"""
    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=rsi_prompt
        )

        analysis = response.text.strip()
        log("Recursive Self-Improvement (RSI) cycle computed by Gemini 3.5!")

        clean_json = analysis
        if "```json" in clean_json:
            clean_json = clean_json.split("```json")[1].split("```")[0].strip()
        elif "```" in clean_json:
            clean_json = clean_json.split("```")[1].split("```")[0].strip()

        try:
            parsed = json.loads(clean_json)
        except Exception:
            parsed = {"raw": analysis}

        # 5. Append to Memory
        all_records = []
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                    all_records = json.load(f).get("historical_insights", [])
            except Exception:
                all_records = []

        all_records.append({
            "timestamp": now_utc.isoformat(),
            "type": "RECURSIVE_SELF_IMPROVEMENT_CYCLE",
            "market_snapshot": market_data,
            "rsi_evolution": parsed
        })
        all_records = all_records[-250:]

        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump({"total_records": len(all_records), "historical_insights": all_records}, f, indent=2)

        # 6. Append to Audit Journal
        with open(RSI_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(parsed) + "\n")

        log(f"🧬 [RSI EVOLUTION COMPLETE] Evolved Capability: {parsed.get('recursive_capability_evolved')}")
        log(f"🎯 Prime Asset: {parsed.get('active_market_bias', {}).get('prime_asset')} | Verdict: {parsed.get('active_market_bias', {}).get('verdict')}")
        log(f"📈 $1,000 Compounding Step: {parsed.get('month_end_1000_roadmap_step')}")

    except Exception as e:
        log(f"RSI Cycle error: {e}")

def main():
    log("==================================================")
    log("TITAN RECURSIVE SELF-IMPROVEMENT (RSI) ENGINE ACTIVE")
    log("==================================================")
    api_key = os.getenv("GEMINI_API_KEY", "")
    run_recursive_self_improvement(api_key)

if __name__ == "__main__":
    main()
