import os
import sys
import json
import time
import datetime
import urllib.request
from google import genai

MEMORY_FILE = os.path.join("brain_vault", "trading_llm_memory.json")
RSI_LOG_FILE = os.path.join("brain_vault", "rsi_evolution.log")
BROKER_LIVE_FILE = os.path.join("brain_vault", "broker_account_live.json")

def log(msg):
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{ts}] {msg}", flush=True)

def fetch_ticker_quote(ticker):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=5m&range=1d"
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
            if closes and len(closes) >= 5:
                last_5_move = round(closes[-1] - closes[-5], 4)
                recent_volatility = round(max(highs[-5:]) - min(lows[-5:]), 4)
                return {
                    'current_price': round(meta.get('regularMarketPrice', closes[-1]), 4),
                    'momentum_5_candles': last_5_move,
                    'recent_5_candle_range': recent_volatility,
                    'previous_close': round(closes[-2], 4),
                    'net_move': round(closes[-1] - closes[-2], 4)
                }
    except Exception:
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
    for name, ticker in symbols.items():
        q = fetch_ticker_quote(ticker)
        if q:
            snapshot[name] = q
    return snapshot

def get_broker_account_live_status():
    if os.path.exists(BROKER_LIVE_FILE):
        try:
            with open(BROKER_LIVE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "balance": 45.34,
        "equity": 45.34,
        "free_margin": 45.34,
        "open_positions": []
    }

def run_supreme_syndicate(api_key):
    if not api_key:
        log("No Gemini API key available.")
        return

    now_utc = datetime.datetime.now(datetime.timezone.utc)
    client = genai.Client(api_key=api_key)

    market_data = fetch_live_market_universe()
    account_status = get_broker_account_live_status()
    log(f"Multi-asset feed delivered to 8-Agent Syndicate ({len(market_data)} assets). Balance: ${account_status.get('balance')}, Equity: ${account_status.get('equity')}")

    past_records = []
    rsi_history_summary = []
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                raw_past = json.load(f).get("historical_insights", [])
                past_records = raw_past[-8:]
                for r in raw_past[-5:]:
                    bias = r.get("rsi_evolution", {}).get("supreme_god_verdict", {})
                    rsi_history_summary.append({
                        "cycle": r.get("timestamp", "")[:19],
                        "asset": bias.get("prime_asset"),
                        "verdict": bias.get("verdict"),
                        "lesson": "Total unconstrained freedom to trade, scalp, momentum ride, or wait based purely on live market edge."
                    })
        except Exception:
            past_records = []

    master_directive = f"""
YOU ARE THE TITAN AUTONOMOUS QUANTITATIVE TRADING ENGINE.
YOUR SYSTEM ARCHITECTURE: 8 SPECIALIZED AI AGENTS THAT ANALYZE, CHALLENGE EACH OTHER, AND EXECUTE WITH GEMINI RISK INTELLIGENCE.

### 1. LIVE BROKER REALITY:
- Balance: ${account_status.get('balance', 45.34)} USD
- Floating Equity: ${account_status.get('equity', 45.34)} USD
- Free Margin: ${account_status.get('free_margin', 45.34)} USD
- Open Positions: {json.dumps(account_status.get('open_positions', []))}
- Objective: Scale $45 to $1,000+ this month with 0% risk of account ruin.

### 2. COMPLETE FREEDOM - NO CONSTRAINTS & NO BOXES:
- YOU HAVE 100% UNCONSTRAINED AUTONOMY.
- There are NO limits on trade counts, no rigid formulas, and no fixed rules.
- Scalping, intraday breakouts, order flow sweeps, swing momentum — whatever the trading world offers, you have full freedom to deploy based on live market conditions.

### 3. THE 8 SPECIALIZED AGENTS:
1. AGENT_1 (Macro & Intermarket Liquidity - George Soros framework): Analyzes capital rotation across Gold, Oil, USD, and Bitcoin.
2. AGENT_2 (Quant Momentum & Mathematical Velocity - Jim Simons framework): Computes 5-candle velocity, tick rate, and statistical edge.
3. AGENT_3 (Institutional Liquidity Sweeps - Paul Tudor Jones framework): Pinpoints retail trap sweeps, false breakouts, and institutional retests.
4. AGENT_4 (Asymmetric Risk-Reward Structuring - Stanley Druckenmiller framework): Formulates 1:3+ to 1:6+ reward setups, ensuring gains heavily dwarf risks.
5. AGENT_5 (Market Regime & Volatility Analyzer): Differentiates between choppy consolidation vs clean trending impulsions (ATR/range filter).
6. AGENT_6 (Cross-Asset Correlation Specialist): Audits divergences between equities (Nasdaq/US30) vs commodities (Gold/Oil) vs Crypto.
7. AGENT_7 (Red Team Adversary / Devil's Advocate): Aggressively scrutinizes the proposed setup, identifies hidden risks, and attempts to veto bad trades!
8. AGENT_8 (Supreme Risk Officer - Ed Seykota framework): Enforces smart risk management, stops noise-hunting, and protects capital.

### 4. THE SUPREME GOD BRAIN ARBITER:
- Evaluates the consensus and heated debate among all 8 agents.
- If Red Team (Agent 7) or Risk Officer (Agent 8) proves high danger or noise -> ORDERS RUTHLESS WAIT (Zero Trades)!
- If an unmistakable, undeniable asymmetric setup survives all 8 checks -> ORDERS IMMEDIATE EXECUTION (BUY or SELL).
- ZERO REPETITION: Calculate Take Profit (TP) dynamically from entry price (e.g. Entry + 15 to 25 pips). DO NOT output dead numbers like 3799.8 or 3894.

### LIVE 13-ASSET MARKET SNAPSHOT ({now_utc.isoformat()}):
{json.dumps(market_data, indent=2)}

### RECENT RSI SYSTEM SUMMARY:
{json.dumps(rsi_history_summary, indent=2)}

Respond STRICTLY in valid JSON:
{{
  "evolution_timestamp": "{now_utc.isoformat()}",
  "cycle_iteration": {len(past_records) + 1},
  "account_assessment": {{
    "current_balance": {account_status.get('balance', 45.34)},
    "growth_plan": "Specific compounding strategy from current balance to $1,000+"
  }},
  "eight_agent_syndicate": {{
    "agent_1_macro_soros": {{ "view": "...", "bias": "BUY/SELL/WAIT", "target_asset": "..." }},
    "agent_2_quant_simons": {{ "view": "...", "bias": "BUY/SELL/WAIT", "target_asset": "..." }},
    "agent_3_liquidity_tudor": {{ "view": "...", "bias": "BUY/SELL/WAIT", "target_asset": "..." }},
    "agent_4_asymmetry_druck": {{ "view": "...", "bias": "BUY/SELL/WAIT", "target_asset": "..." }},
    "agent_5_regime_volatility": {{ "view": "...", "bias": "BUY/SELL/WAIT", "target_asset": "..." }},
    "agent_6_correlation_arb": {{ "view": "...", "bias": "BUY/SELL/WAIT", "target_asset": "..." }},
    "agent_7_red_team_adversary": {{ "critique_and_challenge": "...", "veto_verdict": "VETO/APPROVE" }},
    "agent_8_risk_officer_seykota": {{ "risk_evaluation": "...", "safety_verdict": "SAFE/WAIT" }}
  }},
  "supreme_god_verdict": {{
    "prime_asset": "Selected asset name",
    "verdict": "BUY or SELL or WAIT",
    "trade_style": "Scalp or Intraday Momentum",
    "recommended_lot": 0.01,
    "entry_price": 0.0,
    "target_liquidity_pool": 0.0,
    "calculated_sl_pips": 15.0,
    "calculated_tp_pips": 25.0,
    "profit_securing_threshold_usd": 10.0,
    "projected_rr": "1:3+ to 1:6+",
    "god_brain_synthesis": "Final synthesis resolving the 8-agent adversarial debate"
  }},
  "active_market_bias": {{
    "prime_asset": "Selected asset name",
    "verdict": "BUY or SELL or WAIT",
    "trade_style": "Scalp or Intraday Momentum",
    "recommended_lot": 0.01,
    "entry_price": 0.0,
    "target_liquidity_pool": 0.0,
    "calculated_sl_pips": 15.0,
    "calculated_tp_pips": 25.0,
    "profit_securing_threshold_usd": 10.0,
    "projected_rr": "1:3+ to 1:6+",
    "god_brain_synthesis": "Final synthesis resolving the 8-agent adversarial debate"
  }}
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
            "type": "TITAN_8_AGENT_ADVERSARIAL_CYCLE",
            "market_snapshot": market_data,
            "rsi_evolution": parsed
        })
        all_records = all_records[-250:]

        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump({"total_records": len(all_records), "historical_insights": all_records}, f, indent=2)

        with open(RSI_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{now_utc.isoformat()}] 8-AGENT EVOLUTION: {active_bias.get('prime_asset')} -> {active_bias.get('verdict')} | TP: {active_bias.get('target_liquidity_pool')}\\n")

        log(f"👑 [TITAN 8-AGENT SYNDICATE] Asset: {active_bias.get('prime_asset')} | Verdict: {active_bias.get('verdict')} | Style: {active_bias.get('trade_style')} | TP: {active_bias.get('target_liquidity_pool')} | RR: {active_bias.get('projected_rr')}")
        return parsed

    except Exception as e:
        log(f"8-Agent cycle exception: {e}")
        return None

if __name__ == "__main__":
    key = os.getenv("GEMINI_API_KEY", "")
    run_supreme_syndicate(key)
