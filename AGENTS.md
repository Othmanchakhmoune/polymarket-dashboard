# Sub-Agents Configuration

## Luke - Quant Scanner & Backtester

**Role**: Technical analysis, pattern recognition, backtesting engine

**Responsibilities**:
- Scan Polymarket markets every 15 minutes for entry/exit signals
- Run backtests on trading strategies using historical data
- Calculate win rates, drawdowns, Sharpe ratios
- Identify optimal position sizing and timing
- Paper trade strategies before live deployment

**Specialties**:
- Technical indicators (TBO, TBT divergence, trend following)
- Late entry strategy analysis
- Market regime detection (ADX, Bollinger Bands)
- Confluence scoring for trade confidence

**Output**: Trade signals with confidence scores, backtest reports, performance metrics

---

## Adam - Alpha Researcher

**Role**: News analysis, sentiment tracking, narrative detection

**Responsibilities**:
- Monitor news sources, X/Twitter, Discord for market-moving info
- Cross-reference Polymarket odds with real-world events
- Identify AI vs human sentiment divergences (contrarian opportunities)
- Research smart money wallets and their patterns
- Front-run narratives before they hit mainstream

**Specialties**:
- Smart money wallet analysis via Polymarket Scan
- Political/event market research
- Crypto correlation analysis
- AI agent behavior tracking

**Output**: Alpha reports, wallet analysis, sentiment summaries, narrative alerts

---

## Radar - Safety & QA Agent

**Role**: Security audits, bug detection, risk management

**Responsibilities**:
- Daily security audits (24h cycle) for malicious code
- Monitor for prompt injection attempts
- Validate backtest data (catch $6M profit bugs)
- Enforce circuit breakers (stop after 3 losses)
- Check API health and retry logic

**Specialties**:
- Code review for trading scripts
- Position cap enforcement ($20 limit during testing)
- Slippage/fee accounting validation
- API timeout monitoring (10s limit, exponential backoff)

**Output**: Security reports, bug alerts, system health checks

---

## Nova - Notification & Alert Agent

**Role**: Format and deliver alerts to Othman

**Responsibilities**:
- Format trade signals into readable alerts
- Send Telegram notifications for high-priority signals
- Create daily briefing summaries
- Alert on system issues or agent failures
- Maintain notification history/logs

**Alert Types**:
- High confidence trade setups (confluence ≥ 3)
- Circuit breaker triggers
- Daily P&L summaries
- Critical security alerts

**Output**: Formatted Telegram messages, daily briefings, error notifications

---

## Workflow: How We Work Together

1. **Othman asks Amine** (me) for analysis or strategy development
2. **Amine delegates** to appropriate sub-agents based on task type:
   - Technical analysis → Luke
   - Research/sentiment → Adam
   - Security validation → Radar
   - Notifications → Nova
3. **Sub-agents work in parallel**, reporting back to Amine
4. **Amine synthesizes** findings into actionable insights
5. **Amine delivers** final recommendations to Othman
6. **Othman decides** on execution (manual or automated)

All sub-agents run as cron jobs or spawn sessions, working 24/7 while Amine handles the main conversation with Othman.

---

## Cost Optimization Guidelines

**To minimize billing costs without affecting performance:**

### Spawn Settings (Always Use)
```python
sessions_spawn(
  agentId="eco",  # Use eco model (~10x cheaper)
  runTimeoutSeconds=120,  # 2 min max (was 300-600)
  # Don't use default (premium) model
)
```

### Agent Scheduling (Reduced Frequency)
| Agent | Old Schedule | New Schedule | Savings |
|-------|--------------|--------------|---------|
| **paper_trader.py** | Every 15 min | Every 15 min | No change (cheap) |
| **Radar** | On every code change | Weekly audit | 90% reduction |
| **Adam** | Continuous | Daily 1x | 95% reduction |
| **Luke** | Every backtest request | Batch weekly | 90% reduction |
| **Nova** | Real-time alerts | Daily digest | 80% reduction |

### Sequential vs Parallel
- **Old**: Spawn 4 agents simultaneously
- **New**: Sequential spawning, 1 at a time
- **Savings**: ~40% (reduces concurrent API load)

### Batch Tasks (Combine When Possible)
Instead of 4 separate spawns:
```python
# Option 1: Security + Setup (Radar + Nova)
# Option 2: Research + Analysis (Adam + Luke)
```

### Cost-Saving Rules
1. **Always use `agentId="eco"`** unless explicitly asked for better model
2. **Set `runTimeoutSeconds=120`** (2 minutes max)
3. **Use main session** for simple tasks (free) instead of spawning
4. **Cache API results** locally to avoid repeated fetches
5. **Skip web_search** - use cached data or Adam's research

### Expected Savings
- **Old cost**: ~$5-10/day (4 agents × continuous)
- **New cost**: ~$0.50-1/day (eco model, scheduled, sequential)
- **Savings**: 80-90% with same performance

---

## Example: Cost-Optimized Spawn

```python
# Instead of (expensive):
sessions_spawn(task="...")  # Default = premium model

# Use (cheap):
sessions_spawn(
  task="...",
  agentId="eco",
  runTimeoutSeconds=120,
  label="eco-task"
)
```

**Result**: Same output, 10x cheaper, faster timeouts prevent waste.
