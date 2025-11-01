# U2 Poker Agent

**Ultra-Nimble Adaptive Gaming Intelligence (Standalone Version)**

## Overview

U2 is a fully autonomous tournament poker agent optimized for the specific 30-hand, 5-max format. It combines solid mathematical analysis with adaptive tournament strategy to maximize chip accumulation. **This is a standalone version with all dependencies self-contained within the `agents/u2/` directory.**

## Strategy Philosophy

### Core Principles

1. **Math-First Foundation**
   - Equity calculations (Monte Carlo simulation)
   - Pot odds analysis
   - SPR-based decision making
   - Position-aware ranges

2. **Tournament-Aware Adaptation**
   - Early phase (1-10): Stack building
   - Middle phase (11-20): Exploitation
   - Late phase (21-30): Aggressive maximization

3. **Risk Profile Dynamics**
   - `balanced`: Standard GTO play
   - `aggressive`: Short stack or late game
   - `ultra_aggressive`: Critical push/fold situations
   - `cautious`: Protect chip lead

## Architecture

```
u2/
├── __init__.py           # Export root_agent
├── agent.py              # Main LLM agent + strategy tool
├── brains/
│   ├── __init__.py
│   └── math_brain.py     # Mathematical analysis engine
├── tools/
│   ├── __init__.py
│   └── equity_calculator.py  # Monte Carlo equity calculations
└── config/
    ├── __init__.py
    ├── constants.py      # Tournament settings & thresholds
    └── ranges.py         # Preflop hand ranges
```

**Note:** All modules are self-contained within the `u2` directory. No dependencies on `agents/unagi/` or other agents.

### Decision Flow

```
Game State
    ↓
unagi_strategy_tool()
    ↓
Math Brain Analysis
    ↓
- Calculate equity
- Determine position
- Assess tournament phase
- Select risk profile
- Generate recommendation
    ↓
LLM Decision Fusion
    ↓
JSON Action Output
```

## Key Features

### 1. Tournament Phase Awareness
- **Early (hands 1-10)**: Tight-aggressive, gather intel
- **Middle (hands 11-20)**: Exploit opponent weaknesses
- **Late (hands 21-30)**: Maximum aggression, chip accumulation

### 2. Adaptive Risk Profiles
Automatically adjusts aggression based on:
- Stack size (in BB)
- Hand number
- Chip leader status
- Critical situations (hands 25-30)

### 3. Position Exploitation
- Tight ranges from UTG
- Wide stealing from BTN/CO
- Aggressive blind defense
- Position-based 3-betting

### 4. Fast Equity Calculations
- Monte Carlo simulation (800-1000 iterations)
- Preflop lookup tables for speed
- Efficient caching for repeated situations

## Competitive Advantages vs Baseline

| Feature | team_codex_agent | U2 |
|---------|------------------|-----|
| Math Foundation | ✅ Strong | ✅ Strong (similar) |
| Tournament Awareness | ✅ Good | ✅ Enhanced (30-hand specific) |
| Risk Adaptation | ⚠️ Static profiles | ✅ Dynamic (hand-by-hand) |
| Late Game Aggression | ⚠️ Moderate | ✅ Maximized |
| Time Efficiency | ✅ Good | ✅ Optimized |
| Dependencies | ✅ Self-contained | ✅ **Fully autonomous** |

## Testing

### Quick Test (10 hands)
```bash
uv run python main.py --cli --agent-only --agents "u2:1,beginner_agent:4" --max-hands 10
```

### Standard Test (30 hands)
```bash
uv run python main.py --cli --agent-only --agents "u2:1,beginner_agent:4" --max-hands 30
```

### Benchmark vs Baseline
```bash
uv run python main.py --cli --agent-only \
  --agents "u2:1,team_codex_agent:1,beginner_agent:3" \
  --max-hands 30
```

### Arena Tests
```bash
make quick BOT=u2        # 10 games
make medium BOT=u2       # 50 games
make full BOT=u2         # 100 games
```

## Performance Expectations

**Target Metrics:**
- Win rate vs beginner_agent: >70%
- Win rate vs team_codex_agent: >50%
- Average time per decision: <15 seconds
- No timeouts (all decisions <40s)

**Win Conditions:**
1. Solid early game (avoid big losses)
2. Exploit middle game (build chip lead)
3. Aggressive late game (hands 25-30 critical)

## Configuration

Key parameters in `config/constants.py`:

- `TOURNAMENT_PHASES`: Hand ranges for phases
- `STACK_THRESHOLDS`: When to change risk profiles
- `RISK_PROFILES`: Aggression multipliers
- `EQUITY_THRESHOLDS`: Decision thresholds

## Development Notes

### Time Budget
- Math calculations: ~5 seconds
- LLM decision: ~8 seconds
- Safety buffer: 24+ seconds
- Total: <40 seconds guaranteed

### Error Handling
- Fallback to safe play (check/fold) on errors
- No crashes or forfeits
- Graceful degradation

### Future Enhancements
1. Opponent modeling (track VPIP/PFR)
2. Hand history analysis
3. Exploitative adjustments
4. Multi-brain fusion (if time permits)

## Usage Example

```python
# The agent is automatically loaded by ADK
from agents.u2 import root_agent

print(f"Agent: {root_agent.name}")  # Output: u2_poker_agent

# It will be called with game_state JSON
# and return action JSON:
{
  "action": "raise",
  "amount": 60,
  "reasoning": "Open-raise from BTN with A9s (equity 58%)"
}
```

## Differences from UNAGI

U2 is a **fully autonomous version** of UNAGI:
- ✅ All imports reference `agents.u2.*` instead of `agents.unagi.*`
- ✅ All modules copied into the `u2` directory
- ✅ No dependencies on `agents/unagi/`
- ✅ Can operate independently without other agents
- ✅ Agent name changed to `u2_poker_agent`

## Credits

Built with inspiration from:
- `team_codex_agent` - Math foundation
- `octopus_agent` - Multi-agent architecture ideas
- `codex_bot` - Strategy engine patterns

## License

Part of ADK Poker hackathon project.

---

**U2 - Fully autonomous, like U2 the band, we rock independently!**
