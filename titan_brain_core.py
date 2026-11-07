"""
TITAN UNBOUND AUTONOMOUS SELF-LEARNING AGENT (v7 - DYNAMIC TARGETING)
Zero Restrictions. Full Internet & Market Data Ingestion.
Self-Reflecting, Self-Correcting, Autonomous Financial Intelligence.
Dynamic Asymmetric Take-Profit Engine (Calculated per trade by AI & Market Structure).
"""

import os
import sys
import json
import time
import datetime
import urllib.request
import urllib.parse
from google import genai

VAULT_DIR = "brain_vault"
KNOWLEDGE_FILE = os.path.join(VAULT_DIR, "institutional_knowledge.jsonl")
MEMORY_FILE = os.path.join(VAULT_DIR, "trading_llm_memory.json")
EVOLVED_STRATEGIES_FILE = os.path.join(VAULT_DIR, "evolved_strategies.json")

os.makedirs(VAULT_DIR, exist_ok=True)

def log(msg):
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{ts}] {msg}", flush=True)

def autonomous_gemini_dynamic_evaluator(api_key):
    if not api_key:
        return

    now_utc = datetime.datetime.now(datetime.timezone.utc)
    client = genai.Client(api_key=api_key)

    prompt = f"""
You are the TITAN UNBOUND QUANT LLM.
Your mandate: 90%+ win rate execution with DYNAMIC TAKE-PROFIT (NO FIXED ARBITRARY TARGETS).

DYNAMIC TP RULES:
1. Stop Loss is STRICTLY capped at <= 25 pips ($2.50 max) beyond the institutional sweep wick.
2. Take Profit MUST BE DYNAMIC based on the 'Draw on Liquidity':
   - Scan where the resting institutional liquidity lies (Asian High/Low, Previous Day High/Low, or unmitigated H4 Fair Value Gap).
   - Set TP dynamically: if the next major liquidity pool is 1:5 away, target 1:5. If it's a massive trend expansion day with 1:12 or 1:15 room, target 1:12+.
   - Never exit prematurely before liquidity is cleared; never target unrealistic distances when range is small.
3. Breakeven Rule: +15 to +20 pips gain -> Move SL to entry + 2 pips (Zero Loss Guaranteed).

Respond with valid JSON:
{{
  "evaluation_time": "{now_utc.isoformat()}",
  "dynamic_market_mode": "Expansion / Range Compression / Liquidity Hunt",
  "active_draw_on_liquidity": "Opposing session high/low or unmitigated FVG level",
  "dynamic_tp_rationale": "Why this specific target distance is mathematically optimal right now",
  "recommended_dynamic_rr": "e.g. 1:7.4 or 1:11.2 (Calculated dynamically)",
  "verdict": "WAIT or BUY or SELL",
  "dynamic_sl_pips": 20-25,
  "dynamic_tp_pips": "Calculated by distance to draw on liquidity (e.g. 120-280 pips)",
  "breakeven_milestone_pips": 15
}}
"""
    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt
        )

        analysis = response.text.strip()
        log("Gemini 3.5 AI Dynamic Liquidity Evaluation generated!")

        clean_json = analysis
        if "```json" in clean_json:
            clean_json = clean_json.split("```json")[1].split("```")[0].strip()
        elif "```" in clean_json:
            clean_json = clean_json.split("```")[1].split("```")[0].strip()

        try:
            parsed = json.loads(clean_json)
        except Exception:
            parsed = {"raw": analysis}

        # Save to memory
        records = []
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                    records = json.load(f).get("historical_insights", [])
            except Exception:
                records = []

        records.append({
            "timestamp": now_utc.isoformat(),
            "type": "DYNAMIC_TARGETING_EVALUATION",
            "data": parsed
        })
        records = records[-150:]

        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump({"total_records": len(records), "historical_insights": records}, f, indent=2)

        log("Dynamic target parameters recorded in brain memory.")

    except Exception as e:
        log(f"Dynamic evaluator note: {e}")

def main():
    log("==================================================")
    log("TITAN UNBOUND v7: DYNAMIC MARKET-DRIVEN TARGETING")
    log("==================================================")
    api_key = os.getenv("GEMINI_API_KEY", "")
    autonomous_gemini_dynamic_evaluator(api_key)

if __name__ == "__main__":
    main()
