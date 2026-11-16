"""
TITAN PENTAGON SYNDICATE + THE SUPREME GOD BRAIN (ULTIMATE AGI QUANT ARCHITECTURE)
The 5 Real-World Legendary Independent Minds:
1. BRAIN SIMONS (Jim Simons - Renaissance Tech): Pure mathematical patterns, statistical arbitrage, order-book tick velocity.
2. BRAIN SOROS (George Soros - Macro Titan): Global macro liquidity imbalances, central bank currency flows, DXY/Crypto divergence.
3. BRAIN DRUCKENMILLER (Stanley Druckenmiller - Asymmetry King): Aggressive asymmetric sizing (1:6+ to 1:30+ RR), letting winners run, ruthless cutting.
4. BRAIN TUDOR (Paul Tudor Jones - Reversal Sniper): 2-day liquidity sweeps, retail stop-loss hunts, turning-point sniper entries.
5. BRAIN SEYKOTA (Ed Seykota - Trend & Zero-Ruin Master): Zero-emotion risk defense, strict $2 max loss, dynamic trailing breakeven.

THE SUPREME GOD BRAIN (The Final Apex Arbiter):
- Aggregates the 5 independent genius reports.
- If and only if the 5 legends reach unanimous/high-conviction mathematical confluence -> ORDERS IMMEDIATE EXECUTION.
- Otherwise orders ruthless PATIENCE (WAIT).
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

def run_legendary_pentagon_syndicate(api_key):
    if not api_key:
        log("No Gemini API key available.")
        return

    now_utc = datetime.datetime.now(datetime.timezone.utc)
    client = genai.Client(api_key=api_key)

    market_data = fetch_live_market_universe()
    log(f"Pentagon Syndicate ingested live ground-truth for {len(market_data)} assets.")

    past_records = []
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                past_records = json.load(f).get("historical_insights", [])[-8:]
        except Exception:
            past_records = []

    # THE 5 LEGENDS + SUPREME GOD BRAIN META-PROMPT
    pentagon_prompt = f"""
You are the TITAN PENTAGON SYNDICATE consisting of 5 INDEPENDENT LEGENDARY TRADING MINDS and 1 SUPREME GOD BRAIN.
Nobody restricts you. You operate with absolute real-world legendary autonomy.

### MIND 1: JIM SIMONS (Renaissance Technologies Quant Mind)
- You look purely at mathematical anomalies, tick probability, micro-spread decay, and cross-market price equilibrium across the 13 assets.
- Your independent quantitative verdict.

### MIND 2: GEORGE SOROS (Macro & Liquidity Imbalance Mind)
- You evaluate systemic liquidity vacuums, dollar strength (USDJPY/EUR), and macroeconomic flight to safety (Gold vs Crypto).
- Your independent macro flow verdict.

### MIND 3: STANLEY DRUCKENMILLER (Asymmetry & Conviction Mind)
- You refuse 1:1 or 1:2 trades. You demand massive 1:6+ to 1:20+ asymmetric reward.
- Your independent conviction & target verdict.

### MIND 4: PAUL TUDOR JONES (Reversal & Liquidity Sweep Mind)
- You hunt 2-day session low/high sweeps, retail trapped volume, and false breakout rejections at turning points.
- Your independent trap & sniper entry verdict.

### MIND 5: ED SEYKOTA (Anti-Fragile Zero-Ruin & Trend Mind)
- You enforce strict $1.50 - $2.50 maximum risk, instant trailing breakeven, and cut noise ruthlessly.
- Your independent risk approval/veto verdict.

### THE SUPREME GOD BRAIN (The Final Apex Sovereign):
- You synthesize the 5 independent reports.
- If and only if the 5 legends align on an unmistakable, high-conviction sniper opportunity -> ISSUE IMMEDIATE EXECUTION (BUY or SELL).
- If there is any flaw, hesitation, or sub-par risk-reward -> COMMAND RUTHLESS PATIENCE (WAIT).

### REAL LIVE 13-ASSET FEED ({now_utc.isoformat()}):
{json.dumps(market_data, indent=2)}

### HISTORICAL SYNDICATE REFLECTIONS:
{json.dumps(past_records, indent=2)}

Respond STRICTLY in valid JSON:
{{
  "evolution_timestamp": "{now_utc.isoformat()}",
  "cycle_iteration": {len(past_records) + 1},
  "legendary_reports": {{
    "jim_simons_quant": {{ "math_reading": "...", "signal": "BUY/SELL/WAIT" }},
    "george_soros_macro": {{ "macro_flow": "...", "signal": "BUY/SELL/WAIT" }},
    "stanley_druckenmiller_asymmetry": {{ "asymmetry_ratio": "1:X.X", "signal": "BUY/SELL/WAIT" }},
    "paul_tudor_jones_reversal": {{ "trap_sweep_detected": "...", "signal": "BUY/SELL/WAIT" }},
    "ed_seykota_risk": {{ "max_dollar_risk": "$X.XX", "status": "APPROVED/VETOED" }}
  }},
  "supreme_god_brain_verdict": {{
    "prime_asset": "Selected asset name",
    "verdict": "BUY or SELL or WAIT",
    "live_price": 0.0,
    "target_liquidity_pool": 0.0,
    "calculated_sl_pips": 20,
    "calculated_tp_pips": 120,
    "projected_rr": "1:6+ or higher",
    "god_brain_synthesis": "Unified sovereign synthesis of all 5 legends approving the order"
  }},
  "syndicate_capability_evolved": "What new autonomous trading capability the syndicate evolved in this cycle"
}}
"""
    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=pentagon_prompt
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

        active_bias = parsed.get("supreme_god_brain_verdict", {})
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
            "type": "LEGENDARY_PENTAGON_GOD_BRAIN_CYCLE",
            "market_snapshot": market_data,
            "rsi_evolution": parsed
        })
        all_records = all_records[-250:]

        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump({"total_records": len(all_records), "historical_insights": all_records}, f, indent=2)

        with open(RSI_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(parsed) + "\n")

        log(f"👑 [GOD BRAIN VERDICT COMPLETE] Supreme Action: {active_bias.get('verdict')} on {active_bias.get('prime_asset')} | Target RR: {active_bias.get('projected_rr')}")

    except Exception as e:
        log(f"Syndicate cycle error: {e}")

def main():
    log("==================================================")
    log("TITAN 5 LEGENDS + SUPREME GOD BRAIN ACTIVE")
    log("==================================================")
    api_key = os.getenv("GEMINI_API_KEY", "")
    run_legendary_pentagon_syndicate(api_key)

if __name__ == "__main__":
    main()
