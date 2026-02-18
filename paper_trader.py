#!/usr/bin/env python3
import requests, json, datetime, os
BALANCE_FILE = "paper_balance.json"
HISTORY_FILE = "trade_history.json"
STATS_FILE = "strategy_stats.json"
FEE_RATE = 0.02

def load_data():
    balance, history, stats = 100.0, [], {}
    try:
        with open(BALANCE_FILE, "r") as f: balance = float(json.load(f).get("balance", 100.0))
    except: pass
    try:
        with open(HISTORY_FILE, "r") as f: history = json.load(f) or []
    except: pass
    try:
        with open(STATS_FILE, "r") as f: stats = json.load(f) or {}
    except: pass
    return balance, history, stats

def save_data(balance, history, stats):
    try:
        json.dump({"balance": round(balance, 2)}, open(BALANCE_FILE + ".tmp", "w"))
        json.dump(history, open(HISTORY_FILE + ".tmp", "w"))
        json.dump(stats, open(STATS_FILE + ".tmp", "w"))
        os.replace(BALANCE_FILE + ".tmp", BALANCE_FILE)
        os.replace(HISTORY_FILE + ".tmp", HISTORY_FILE)
        os.replace(STATS_FILE + ".tmp", STATS_FILE)
    except Exception as e: print(f"Save error: {e}")

def get_best_strategy(price, volume, stats):
    candidates = []
    if price < 0.40:
        wr = stats.get("Mean Reversion", {}).get("win_rate", 0.5)
        conf = (10 if price < 0.30 else 7 if price < 0.35 else 5) * wr
        candidates.append(("Mean Reversion", conf))
    if price > 0.70:
        wr = stats.get("Contrarian", {}).get("win_rate", 0.5)
        conf = (10 if price > 0.80 else 7 if price > 0.75 else 5) * wr
        candidates.append(("Contrarian", conf))
    if price < 0.45 and volume > 50000:
        wr = stats.get("Momentum", {}).get("win_rate", 0.5)
        candidates.append(("Momentum", 6 * wr))
    if volume > 500000 and price < 0.50:
        wr = stats.get("Smart Money", {}).get("win_rate", 0.5)
        candidates.append(("Smart Money", 8 * wr))
    if candidates:
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[0][0]
    return None

def update_stats(stats, strategy, profit):
    if strategy not in stats: stats[strategy] = {"wins": 0, "losses": 0, "total_profit": 0}
    if profit > 0: stats[strategy]["wins"] += 1
    else: stats[strategy]["losses"] += 1
    stats[strategy]["total_profit"] += profit
    total = stats[strategy]["wins"] + stats[strategy]["losses"]
    stats[strategy]["win_rate"] = stats[strategy]["wins"] / total if total > 0 else 0.5
    return stats

def check_circuit_breaker(history):
    recent = [t for t in history[-10:] if t.get("outcome") == "closed"]
    return len(recent) >= 3 and all(t.get("profit", 0) < 0 for t in recent[-3:])

def fetch_markets():
    try:
        r = requests.get("https://gamma-api.polymarket.com/markets?closed=false&limit=200", timeout=10)
        r.raise_for_status()
        markets = r.json()
    except Exception as e: print(f"API error: {e}"); return []
    results = []
    for m in markets:
        try:
            if not all(k in m for k in ["id","question","outcomePrices","liquidityNum","volumeNum"]): continue
            q = m["question"].lower()
            liq = float(m["liquidityNum"])
            vol = float(m["volumeNum"])
            if any(k in q for k in ["bitcoin","ethereum","solana"]) and liq > 10000:
                if any(w in q for w in ["above","up","increase","higher"]):
                    m["volumeNum"] = vol; results.append(m)
        except: continue
    return results[:3]

def create_trade(strategy, price, stake, mid, q):
    return {"timestamp": datetime.datetime.now().isoformat(), "strategy": strategy,
            "contract": q, "odds": price, "stake": stake, "outcome": "open",
            "entry_price": price, "market_id": mid, "payout": None,
            "exit_price": None, "profit": None, "fees": stake * FEE_RATE}

def main():
    balance, history, stats = load_data()
    if check_circuit_breaker(history):
        print("Circuit breaker active"); save_data(balance, history, stats); return
    markets = fetch_markets()
    if not markets: print("No markets"); save_data(balance, history, stats); return
    for m in markets:
        try:
            mid, q = m["id"], m["question"]
            price = float(m["outcomePrices"][0])
            vol = float(m["volumeNum"])
            strategy = get_best_strategy(price, vol, stats)
            if not strategy: continue
            max_stake = 5.0 if vol < 100000 else 10.0
            stake = min(max_stake, balance)
            if balance >= stake:
                trade = create_trade(strategy, price, stake, mid, q)
                history.append(trade); balance -= stake
                print(f"{strategy}: Entry {price}, stake ${stake}")
        except Exception as e: print(f"Error: {e}"); continue
    save_data(balance, history, stats)
    print(f"Balance: ${balance:.2f}")

if __name__ == '__main__': main()

def process_exits(history, balance, stats):
    now = datetime.datetime.now()
    for t in history:
        if t.get("outcome") != "open": continue
        try:
            entry_time = datetime.datetime.fromisoformat(t["timestamp"])
            hold_secs = (now - entry_time).total_seconds()
            entry = t["entry_price"]
            stake = t["stake"]
            # Fetch current price (simplified - assumes 0.55 for demo)
            current = 0.55 # In real: fetch from API
            if current > 0.60 or hold_secs > 3600:
                payout = stake / entry if current > 0.60 else 0
                profit = payout - stake - t["fees"]
                t["outcome"] = "closed"
                t["exit_price"] = current
                t["payout"] = payout
                t["profit"] = profit
                balance += payout
                stats = update_stats(stats, t["strategy"], profit)
                print(f"Closed {t["strategy"]}: profit ${profit:.2f}")
        except Exception as e: print(f"Exit error: {e}"); continue
    return history, balance, stats
