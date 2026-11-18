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
                # Dynamic organic flow: last 5 candles momentum, recent volatility
                last_5_move = round(closes[-1] - closes[-5], 4)
                recent_volatility = round(max(highs[-5:]) - min(lows[-5:]), 4)
                return {
                    'current_price': round(meta.get('regularMarketPrice', closes[-1]), 4),
                    'momentum_5_candles': last_5_move,
                    'recent_5_candle_range': recent_volatility,
                    'previous_close': round(closes[-2], 4),
                    'net_move': round(closes[-1] - closes[-2], 4)
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
    log(f"Multi-asset feed delivered to Syndicate ({len(market_data)} assets). Balance: ${account_status.get('balance')}, Equity: ${account_status.get('equity')}")

    past_records = []
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                past_records = json.load(f).get("historical_insights", [])[-8:]
        except Exception:
            past_records = []

    master_directive = f"""
RECURSIVE SELF-IMPROVEMENT (RSI) DIRECTIVE FOR THE 5 UNCONSTRAINED WALL STREET LEGENDS & SUPREME GOD BRAIN:

### CRITICAL LESSON FROM TODAY'S FORENSIC AUDIT (LEARN & NEVER REPEAT):
- 149 trades were executed today and 147 were stopped out by noise because stop losses were too tight (7-8 pips) and targets were anchored to static macro numbers (3894 / 3799).
- RESULT: Account drew down to $45.34.
- YOUR RSI DIRECTIVE: Stop anchoring to static numbers! Use organic, dynamic price action.
- STOP OVER-TRADING: Only 2 to 4 high-probability sniper trades per day. If the setup is not unmistakable -> RUTHLESS WAIT!

1. THE 5 INDEPENDENT ELITE MINDS (NO PRE-DEFINED BOX):
   - Mind 1: JIM SIMONS (Mathematical pattern recognition & multi-asset correlation)
   - Mind 2: GEORGE SOROS (Global macro liquidity flow & inter-market momentum)
   - Mind 3: STANLEY DRUCKENMILLER (Asymmetric 1:3+ to 1:6+ risk-to-reward structuring)
   - Mind 4: PAUL TUDOR JONES (Liquidity sweeps, false breakouts, and institutional reversal points)
   - Mind 5: ED SEYKOTA (Ruthless capital preservation & trend alignment)
   - Whatever happens in the trading world — scalping, intraday momentum, liquidity grabs, break-and-retest, order-flow sweeps — you have the full power to execute it all yourself.
   - You decide when to scalp, when to ride an intraday wave, when to take quick profits, and how to manage risk.

2. YOUR LIVE BROKER ACCOUNT STATUS:
   - Real-time Balance: ${account_status.get('balance', 45.34)} USD
   - Real-time Floating Equity: ${account_status.get('equity', 45.34)} USD
   - Real-time Free Margin: ${account_status.get('free_margin', 45.34)} USD
   - Currently Open Broker Positions: {json.dumps(account_status.get('open_positions', []))}
   - STUDY YOUR ACCOUNT. Adjust your position sizing (0.01 to 0.05 lot) and strategy dynamically based on your available balance.

3. YOUR MISSION: COMPOUND FROM CURRENT BALANCE TO $1,000+ USD WITHIN 1 MONTH:
   - This requires active, smart intraday execution.
   - Do NOT hold trades waiting for distant macro fantasy targets that take weeks. Focus on INTRADAY trades (targets reachable today).
   - Cash in your hand is how an account grows: bank wins, protect capital, compound continuously.

4. YOU DECIDE EVERYTHING:
   - 5 Independent Minds observe market reality and trade opportunities.
   - The Supreme God Brain synthesizes the final execution verdict:
     * Which asset to trade
     * Action: BUY, SELL, or WAIT
     * Lot size (0.01 to 0.05 based on equity)
     * Exact Entry Price, Stop Loss (SL), and Take Profit (TP)
     * Trade Style: "Scalp (quick 5-15 pips)", "Intraday Momentum (15-35 pips)", or "Breakout"
     * Profit Protection Rule: You dictate how the active trade should be managed (e.g. secure at +$5, trailing stop, or manual exit)

### REAL-TIME LIVE 13-ASSET MARKET SNAPSHOT ({now_utc.isoformat()}):
{json.dumps(market_data, indent=2)}

### HISTORICAL SYNDICATE REFLECTIONS:
{json.dumps(past_records, indent=2)}

Respond STRICTLY in valid JSON:
{{
  "evolution_timestamp": "{now_utc.isoformat()}",
  "cycle_iteration": {len(past_records) + 1},
  "account_assessment": {{
    "current_balance": {account_status.get('balance', 45.34)},
    "growth_plan": "How you plan to compound from this balance to $1,000+ this month"
  }},
  "independent_brains": {{
    "brain_1": {{ "raw_thought": "...", "signal": "BUY/SELL/WAIT", "target_asset": "...", "style": "Scalp/Intraday" }},
    "brain_2": {{ "raw_thought": "...", "signal": "BUY/SELL/WAIT", "target_asset": "...", "style": "Scalp/Intraday" }},
    "brain_3": {{ "raw_thought": "...", "signal": "BUY/SELL/WAIT", "target_asset": "...", "style": "Scalp/Intraday" }},
    "brain_4": {{ "raw_thought": "...", "signal": "BUY/SELL/WAIT", "target_asset": "...", "style": "Scalp/Intraday" }},
    "brain_5": {{ "raw_thought": "...", "signal": "BUY/SELL/WAIT", "target_asset": "...", "style": "Scalp/Intraday" }}
  }},
  "supreme_god_verdict": {{
    "prime_asset": "Exact instrument name (e.g. Gold (XAUUSD))",
    "verdict": "BUY or SELL or WAIT",
    "trade_style": "Scalp or Intraday Momentum",
    "recommended_lot": 0.01,
    "entry_price": 0.0,
    "target_liquidity_pool": 0.0,
    "calculated_sl_pips": 10.0,
    "calculated_tp_pips": 20.0,
    "profit_securing_threshold_usd": 10.0,
    "projected_rr": "1:2+ to 1:6+",
    "god_brain_synthesis": "Autonomous synthesis and execution decision"
  }},
  "active_market_bias": {{
    "prime_asset": "Exact instrument name",
    "verdict": "BUY or SELL or WAIT",
    "trade_style": "Scalp or Intraday Momentum",
    "recommended_lot": 0.01,
    "target_liquidity_pool": 0.0,
    "calculated_sl_pips": 10.0,
    "calculated_tp_pips": 20.0,
    "profit_securing_threshold_usd": 10.0,
    "projected_rr": "1:2+ to 1:6+",
    "god_brain_synthesis": "Autonomous synthesis and execution decision"
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
            "type": "SOVEREIGN_INTRADAY_UNBOXED_CYCLE",
            "market_snapshot": market_data,
            "rsi_evolution": parsed
        })
        all_records = all_records[-250:]

        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump({"total_records": len(all_records), "historical_insights": all_records}, f, indent=2)

        with open(RSI_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{now_utc.isoformat()}] SOVEREIGN INTRADAY EVOLUTION COMPLETED: {active_bias.get('prime_asset')} -> {active_bias.get('verdict')} | TP: {active_bias.get('target_liquidity_pool')}\\n")

        log(f"👑 [SOVEREIGN INTRADAY BRAIN] Asset: {active_bias.get('prime_asset')} | Verdict: {active_bias.get('verdict')} | Style: {active_bias.get('trade_style')} | TP: {active_bias.get('target_liquidity_pool')} | RR: {active_bias.get('projected_rr')}")
        return parsed

    except Exception as e:
        log(f"Syndicate cycle exception: {e}")
        return None

if __name__ == "__main__":
    key = os.getenv("GEMINI_API_KEY", "")
    run_supreme_syndicate(key)
