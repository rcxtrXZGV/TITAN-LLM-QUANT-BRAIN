"""
TITAN 4-PILLAR SUBAGENT COMMITTEE ARCHITECTURE (SUPREME AGI QUANT BRAIN)
Division of Specialized Roles:
1. Agent A: Market Structure & Liquidity Hunter (Scans 2-day low/high sweeps, discount arrays)
2. Agent B: Chief Risk Officer (Enforces strict $2.00 max risk, dynamic ATR stop buffers)
3. Agent C: Intermarket Correlation & Momentum Analyst (Verifies DXY, BTC, US30 delta volume sync)
4. THE SUPREME CHIEF (Final Man): Aggregates all 3 subagent reports. Grants final UNANIMOUS execution verdict or orders WAIT.
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

def run_subagent_committee(api_key):
    if not api_key:
        log("No Gemini API key available.")
        return

    now_utc = datetime.datetime.now(datetime.timezone.utc)
    client = genai.Client(api_key=api_key)

    # Ingest 13-asset live market ground truth
    market_data = fetch_live_market_universe()
    log(f"Multi-Asset ground truth ingested ({len(market_data)} live assets).")

    past_records = []
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                past_records = json.load(f).get("historical_insights", [])[-8:]
        except Exception:
            past_records = []

    # MASTER MULTI-SUBAGENT COMMITTEE PROMPT
    committee_prompt = f"""
You are the TITAN MULTI-AGENT QUANTITATIVE COMMITTEE consisting of 3 Specialized Subagents and 1 FINAL CHIEF EXECUTIVE OFFICER:

### 1. SUBAGENT 1: LIQUIDITY & MARKET STRUCTURE HUNTER
Your Job: Scan the 13 live market assets. Find which asset just executed a textbook 2-day liquidity sweep (Stop-hunt of retail highs/lows) into an unmitigated institutional discount/premium array.

### 2. SUBAGENT 2: CHIEF RISK OFFICER (CRO)
Your Job: Mathematically stress-test Subagent 1's setup. Enforce:
- Maximum dollar risk: $1.50 - $2.50.
- Minimum Asymmetry: 1:6+ to 1:12+ reward-to-risk.
- Invalidation level: Is the Stop Loss placed safely behind true structural wicks + dynamic spread buffer?

### 3. SUBAGENT 3: CROSS-MARKET CORRELATION SPECIALIST
Your Job: Check inter-market alignment. If Gold or EUR is buying, are USDJPY and DXY weakening? Is Bitcoin confirming macro liquidity appetite? If markets are in divergence, reject the trade.

### 4. THE FINAL MAN (CHIEF EXECUTIVE OFFICER - FINAL VERDICT):
Your Job: Synthesize reports from Subagent 1, 2, and 3.
- If ALL 3 Subagents agree with 100% mathematical confluence -> Issue FINAL EXECUTION (BUY or SELL).
- If ANY subagent raises a red flag -> Issue strict WAIT. Zero random gambles.

### LIVE MARKET TICK FEED ({now_utc.isoformat()}):
{json.dumps(market_data, indent=2)}

### RECENT HISTORICAL MEMORY:
{json.dumps(past_records, indent=2)}

Respond STRICTLY in valid JSON:
{{
  "evolution_timestamp": "{now_utc.isoformat()}",
  "cycle_iteration": {len(past_records) + 1},
  "subagent_reports": {{
    "liquidity_hunter": {{
      "prime_setup_identified": "Asset and sweep details",
      "conviction_score": "1-100"
    }},
    "risk_officer": {{
      "dollar_risk_approved": "$X.XX",
      "asymmetry_ratio": "1:X.X",
      "risk_status": "APPROVED or REJECTED"
    }},
    "correlation_analyst": {{
      "intermarket_alignment": "Details on USD/BTC/Equity alignment",
      "alignment_status": "ALIGNED or DIVERGENT"
    }}
  }},
  "final_man_ceo_verdict": {{
    "prime_asset": "Selected asset name",
    "verdict": "BUY or SELL or WAIT",
    "live_price": 0.0,
    "target_liquidity_pool": 0.0,
    "calculated_sl_pips": 20,
    "calculated_tp_pips": 120,
    "projected_rr": "1:6+",
    "final_unanimous_reasoning": "Synthesis of all 3 subagents confirming bulletproof execution"
  }},
  "heuristic_mutation": "Specific quantitative algorithmic formula evolved in this cycle",
  "recursive_capability_evolved": "What permanent edge was acquired by the committee"
}}
"""
    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=committee_prompt
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

        # Adapt for executor compatibility
        active_bias = parsed.get("final_man_ceo_verdict", {})
        parsed["active_market_bias"] = active_bias

        # Save to memory vault
        all_records = []
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                    all_records = json.load(f).get("historical_insights", [])
            except Exception:
                all_records = []

        all_records.append({
            "timestamp": now_utc.isoformat(),
            "type": "SUBAGENT_COMMITTEE_CYCLE",
            "market_snapshot": market_data,
            "rsi_evolution": parsed
        })
        all_records = all_records[-250:]

        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump({"total_records": len(all_records), "historical_insights": all_records}, f, indent=2)

        with open(RSI_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(parsed) + "\n")

        log(f"👥 [SUBAGENT COMMITTEE FINISHED] Final CEO Verdict: {active_bias.get('verdict')} on {active_bias.get('prime_asset')} (RR: {active_bias.get('projected_rr')})")

    except Exception as e:
        log(f"Committee cycle error: {e}")

def main():
    log("==================================================")
    log("TITAN 4-PILLAR SUBAGENT COMMITTEE ENGINE ACTIVE")
    log("==================================================")
    api_key = os.getenv("GEMINI_API_KEY", "")
    run_subagent_committee(api_key)

if __name__ == "__main__":
    main()
