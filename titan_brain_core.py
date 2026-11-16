"""
TITAN COUNCIL OF INDEPENDENT SOVEREIGN TRADERS (ELITE MULTI-BRAIN CONSORTIUM)
Philosophy:
Zero micromanagement. Zero rigid scripts.
Every brain is an autonomous sovereign entity with its own independent elite trading mind,
free to evolve its own math, indicators, psychology, and risk frameworks.
The 4 Sovereign Minds:
1. Sovereign Mind ALPHA (The Aggressive Liquidity & Volatility Predator)
2. Sovereign Mind BETA (The Institutional Order-Flow & Microstructure Purest)
3. Sovereign Mind GAMMA (The Quantitative Risk & Anti-Fragility Architect)
4. THE FINAL APEX SOVEREIGN (The Supreme Syndicate Chief - Unifies or Vetoes)
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

def run_independent_sovereign_brains(api_key):
    if not api_key:
        log("No Gemini API key available.")
        return

    now_utc = datetime.datetime.now(datetime.timezone.utc)
    client = genai.Client(api_key=api_key)

    market_data = fetch_live_market_universe()
    log(f"Multi-Asset ground truth ingested across {len(market_data)} live assets.")

    past_records = []
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                past_records = json.load(f).get("historical_insights", [])[-8:]
        except Exception:
            past_records = []

    # UNRESTRICTED SOVEREIGN COUNCIL META-PROMPT
    council_prompt = f"""
You are the SUPREME COUNCIL OF 4 INDEPENDENT ELITE TRADING MINDS.
Nobody defines your methods. You possess 100% UNRESTRICTED SOVEREIGNTY, autonomous market intelligence, and unconstrained quantitative freedom.
Each of you thinks, calculates, and trades with an independent elite trader mind:

### 1. SOVEREIGN BRAIN ALPHA (The Unconstrained Volatility & Sweep Hunter)
- You have complete freedom to hunt market anomalies, retail traps, session expansions, and momentum surges across all 13 assets.
- You think purely in terms of smart money deception, liquidity vacuums, and predatory entries.
- State your independent analysis, candidate asset, and conviction.

### 2. SOVEREIGN BRAIN BETA (The Independent Order-Flow & Microstructure Quant)
- You do not care about opinions; you care about math, multi-asset tick velocity, cross-market correlations (USD/Crypto/Equities), and volume delta imbalances.
- Formulate your own independent mathematical thesis on current market realities.

### 3. SOVEREIGN BRAIN GAMMA (The Anti-Fragility & Capital Preservation Sovereign)
- You are independent guardian of zero-ruin. You ruthlessly veto any setup where risk exceeds $1.50-$2.50 or reward is under 1:6+.
- You verify whether market conditions warrant aggressive execution or ruthless patience (WAIT).

### 4. THE FINAL APEX SOVEREIGN (The Final Man - The Master Mind)
- You synthesize the 3 independent minds.
- You have final, sovereign authority. If the council presents an undeniable, high-conviction sniper opportunity across the 13 assets with 1:6+ to 1:20+ asymmetry, you ORDER IMMEDIATE EXECUTION (BUY or SELL).
- If there is noise, disagreement, or sub-par quality, you command WAIT.

### LIVE 13-ASSET MARKET REALITY ({now_utc.isoformat()}):
{json.dumps(market_data, indent=2)}

### HISTORICAL COUNCIL MEMORY:
{json.dumps(past_records, indent=2)}

Respond STRICTLY in valid JSON:
{{
  "evolution_timestamp": "{now_utc.isoformat()}",
  "cycle_iteration": {len(past_records) + 1},
  "sovereign_minds": {{
    "brain_alpha": {{
      "independent_thesis": "Alpha's autonomous predator market reading",
      "preferred_asset": "Asset name",
      "verdict": "BUY / SELL / WAIT"
    }},
    "brain_beta": {{
      "quantitative_thesis": "Beta's autonomous order-flow and delta math",
      "correlation_verdict": "ALIGNED / SPREAD_NOISE"
    }},
    "brain_gamma": {{
      "risk_mathematics": "Gamma's capital defense calculation",
      "risk_verdict": "APPROVED / VETOED"
    }}
  }},
  "final_apex_verdict": {{
    "prime_asset": "Selected asset name",
    "verdict": "BUY or SELL or WAIT",
    "live_price": 0.0,
    "target_liquidity_pool": 0.0,
    "calculated_sl_pips": 20,
    "calculated_tp_pips": 120,
    "projected_rr": "1:6+ or higher",
    "final_master_reasoning": "Apex Master synthesis granting final order execution"
  }},
  "autonomous_capability_evolved": "What new autonomous trading capability the syndicate independently developed"
}}
"""
    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=council_prompt
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

        active_bias = parsed.get("final_apex_verdict", {})
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
            "type": "INDEPENDENT_SOVEREIGN_COUNCIL_CYCLE",
            "market_snapshot": market_data,
            "rsi_evolution": parsed
        })
        all_records = all_records[-250:]

        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump({"total_records": len(all_records), "historical_insights": all_records}, f, indent=2)

        with open(RSI_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(parsed) + "\n")

        log(f"🧠 [SOVEREIGN COUNCIL COMPLETE] Final Apex Decision: {active_bias.get('verdict')} on {active_bias.get('prime_asset')} | RR: {active_bias.get('projected_rr')}")

    except Exception as e:
        log(f"Council cycle error: {e}")

def main():
    log("==================================================")
    log("TITAN INDEPENDENT SOVEREIGN COUNCIL ACTIVE")
    log("==================================================")
    api_key = os.getenv("GEMINI_API_KEY", "")
    run_independent_sovereign_brains(api_key)

if __name__ == "__main__":
    main()
