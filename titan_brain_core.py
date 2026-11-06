import os
import json
import datetime
import urllib.request
import yfinance as yf
import pandas as pd
from google import genai

GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")

VAULT_DIR = "brain_vault"
MEMORY_FILE = os.path.join(VAULT_DIR, "trading_llm_memory.json")
KNOWLEDGE_FILE = os.path.join(VAULT_DIR, "institutional_knowledge.jsonl")

os.makedirs(VAULT_DIR, exist_ok=True)

def log(msg):
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{now}] {msg}", flush=True)

# 1. Harvest & Expand Institutional Knowledge
KNOWLEDGE_TOPICS = [
    'Candlestick_pattern', 'Price_action', 'Market_structure',
    'Order_flow', 'Wyckoff_method', 'Algorithmic_trading'
]

def harvest_core_knowledge():
    log("Ingesting institutional price action corpus...")
    headers = {'User-Agent': 'Mozilla/5.0'}
    entries = []
    for topic in KNOWLEDGE_TOPICS:
        url = f'https://en.wikipedia.org/api/rest_v1/page/summary/{topic}'
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                entries.append({
                    "topic": data.get("title", topic),
                    "summary": data.get("extract", "")
                })
        except Exception as e:
            log(f"Topic {topic} skipped: {e}")

    with open(KNOWLEDGE_FILE, "w", encoding="utf-8") as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    log(f"Knowledge vault updated with {len(entries)} core modules.")

# 2. Consult Dual Gemini AI Model (Flash-Lite with 3.8 Fallback)
def consult_gemini(price, open_p, high, low, wick_up, wick_down, rng):
    if not GEMINI_KEY:
        log("No GEMINI_API_KEY provided; using pure quant price action.")
        return None
    try:
        client = genai.Client(api_key=GEMINI_KEY)
        prompt = f"""
        Act as the Supreme Institutional Predator Gold Scalper.
        Rule: NO FIXED TRADE LIMIT. Hunt EVERY single A+ institutional quality setup.
        Gold M5 Snapshot:
        Price: {price}, Open: {open_p}, High: {high}, Low: {low}, Range: {rng}
        Upper Wick: {wick_up}, Lower Wick: {wick_down}

        Strict Conditions:
        1. Stop Loss MUST be tight (<= 25 pips / $2.50).
        2. Target MUST be asymmetric 1:6 to 1:10+ (+$15 to +$25).
        3. Must be an obvious Liquidity Sweep Pin-Bar Rejection.

        Is this an A+ Quality Setup to HUNT immediately?
        Return ONLY valid JSON: {{"action": "BUY"|"SELL"|"WAIT", "confidence": 0.85, "reason": "brief rationale"}}
        """
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt
        )
        text = response.text
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end != 0:
            return json.loads(text[start:end])
    except Exception as e:
        log(f"Gemini evaluation warning: {e}")
    return None

# 3. Dynamic Quality Setup Hunting Engine (No Arbitrary Daily Cap)
def hunt_quality_market_setups():
    log("Scanning Gold (XAUUSD) for ALL available A+ Quality setups...")
    try:
        df = yf.download("GC=F", period="5d", interval="1h", progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0].lower() for col in df.columns]
        else:
            df.columns = [col.lower() for col in df.columns]
        df = df.dropna()
        
        last_bar = df.iloc[-1]
        
        high = float(last_bar['high'])
        low = float(last_bar['low'])
        close = float(last_bar['close'])
        open_p = float(last_bar['open'])
        rng = high - low
        wick_up = high - max(open_p, close)
        wick_down = min(open_p, close) - low
        
        ai_res = consult_gemini(close, open_p, high, low, wick_up, wick_down, rng)
        
        trade_signal = None
        # PREDATOR HUNT TRIGGER: Whenever A+ setup forms, hunt it!
        if ai_res and ai_res.get("action") in ["BUY", "SELL"] and ai_res.get("confidence", 0) >= 0.75:
            action = ai_res["action"]
            sl = round(high + 0.50, 2) if action == "SELL" else round(low - 0.50, 2)
            tp = round(close - 18.0, 2) if action == "SELL" else round(close + 18.0, 2)
            trade_signal = {
                "action": action,
                "entry": round(close, 2),
                "sl": sl,
                "tp": tp,
                "confidence": ai_res.get("confidence"),
                "rationale": f"[A+ QUALITY HUNT] {ai_res.get('reason')}"
            }
        elif wick_up >= 0.50 * rng and close < open_p:
            trade_signal = {
                "action": "SELL",
                "entry": round(close, 2),
                "sl": round(high + 0.50, 2),
                "tp": round(close - 18.0, 2),
                "rationale": "[A+ QUALITY HUNT] Upper Liquidity Sweep Pin-Bar Rejection"
            }
        elif wick_down >= 0.50 * rng and close > open_p:
            trade_signal = {
                "action": "BUY",
                "entry": round(close, 2),
                "sl": round(low - 0.50, 2),
                "tp": round(close + 18.0, 2),
                "rationale": "[A+ QUALITY HUNT] Lower Liquidity Sweep Pin-Bar Rejection"
            }
        else:
            trade_signal = {
                "action": "WAIT",
                "rationale": "No clean institutional wick rejection; capital preserved."
            }

        mem = {}
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, "r") as f:
                    mem = json.load(f)
            except:
                pass
                
        mem.setdefault("system", "TITAN-LLM-QUANT-BRAIN")
        mem.setdefault("version", "3.0-PREDATOR-ALL-QUALITY-HUNTER")
        mem["last_run_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        signals = mem.setdefault("signal_history", [])
        signals.append({
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "signal": trade_signal
        })
        mem["signal_history"] = signals[-100:] # keep last 100
        
        with open(MEMORY_FILE, "w") as f:
            json.dump(mem, f, indent=2)
            
        log(f"Predator Verdict: {trade_signal['action']} | Reason: {trade_signal['rationale']}")
    except Exception as e:
        log(f"Market evaluation error: {e}")

if __name__ == "__main__":
    harvest_core_knowledge()
    hunt_quality_market_setups()
