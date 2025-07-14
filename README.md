# ICT PD Array Scanner - MES/MNQ Futures

## 🎯 Project Overview
A real-time market scanning system for CME MES and MNQ futures contracts using ICT (Inner Circle Trader) Price Delivery Array methodology. The system monitors multiple timeframes for specific price action patterns and sends intelligent alerts when predetermined criteria are met.

## 🏗️ Architecture

### Pine Script Layer (Visual Detection)
- **Purpose**: Pattern identification and visualization on TradingView charts
- **Output**: Clean pattern detection with mean threshold calculations
- **Limitation**: Visual only - no persistent state or complex logic

### Python Backend (Logic & Alerts)
- **Purpose**: Event processing, state management, and intelligent alerting
- **Components**:
  - Real-time data ingestion
  - Pattern state tracking
  - Multi-timeframe analysis
  - Alert delivery system

## 📊 Monitored Instruments
- **MES** (Micro E-mini S&P 500 Futures)
- **MNQ** (Micro E-mini NASDAQ-100 Futures)

## ⏱️ Timeframes
- 5 minute
- 15 minute  
- 30 minute
- 1 hour

## 🎯 Price Delivery Arrays (PD Arrays)

### 1. Fair Value Gap (FVG)
- **Detection**: 3-candle pattern with no overlapping wicks
- **Mean Threshold**: Midpoint between high of first candle and low of third candle
- **Alert Trigger**: Candle body closes above/below mean threshold
- **State Tracking**: Active, Respected, Breached, Filled

### 2. Inverse Fair Value Gap (iFVG)
- **Detection**: Inverse of FVG pattern
- **Logic**: Same as FVG but inverted directional bias
- **Alert Conditions**: Mirror FVG alerts

### 3. Order Block (OB)
- **Detection**: Last opposing candle before market structure shift
- **Mean Threshold**: 50% level of the order block candle
- **Alert Trigger**: Price respects or breaks mean threshold
- **Validity**: Remains active until fully mitigated

### 4. Market Structure Shift (MSS) / Break of Structure (BOS)
- **Detection**: Break of previous swing high/low
- **Alert Trigger**: Confirmation candle closes beyond structure level
- **Context**: Trend change vs. continuation identification

### 5. SMT Divergence (Smart Money Technique)
- **Detection**: Correlated assets moving in opposite directions at key levels
- **Logic**: MES sweeps level while MNQ fails to sweep corresponding level
- **Alert Trigger**: Divergence confirmed after specified time window
- **Key Levels**: Session highs/lows, previous day levels, swing points

### 6. Volume Imbalance
- **Detection**: Candle with minimal body and extended wick
- **Mean Threshold**: Midpoint of imbalance range
- **Alert Logic**: Similar to FVG threshold respect

### 7. Liquidity Void
- **Detection**: Price gaps or areas of low volume
- **Alert Trigger**: Price enters void area
- **Expectation**: Rapid price movement through void

### 8. NDOG/NWOG (New Day/Week Opening Gap)
- **Detection**: Gap between previous close and new session open
- **Alert Trigger**: Price returns to test gap levels
- **Sessions**: Asia, London, NY AM, NY Lunch, NY PM

### 9. Equal Highs/Lows
- **Detection**: Multiple touches at same price level
- **Alert Trigger**: Level break with confirmation
- **Context**: Liquidity pool identification

## 🔄 Event-Driven System Flow

```
New Candle Close → Pattern Detection → State Update → Condition Check → Alert (if triggered)
```

### Event Types
1. **Pattern Formation**: New FVG, Order Block, etc. detected
2. **Threshold Breach**: Price crosses mean threshold levels
3. **Pattern Confirmation**: Respect or invalidation of levels
4. **Structure Break**: MSS/BOS confirmations
5. **Divergence Alert**: SMT conditions met

## 📨 Alert System

### Alert Levels
- **🟢 Green**: Pattern confirmed and respected
- **🟡 Yellow**: Pattern confirmed but currently violated
- **🔴 Red**: Pattern invalidated/broken

### Alert Format Example
```
🎯 MES 15m FVG Alert
📊 Pattern: Bullish FVG Mean Threshold Breach
💹 Action: Candle closed ABOVE mean threshold
📈 Level: 4,567.25
⏰ Time: 2024-01-15 14:30:00 EST
🎨 Status: 🟢 Confirmed
```

### Delivery Channels
- Discord webhook
- Telegram bot
- Email notifications
- SMS (high priority only)

## 🗄️ State Management

### Data Persistence
- **Database**: SQLite for development, PostgreSQL for production
- **State Tracking**: Active patterns, threshold levels, alert history
- **Data Retention**: Configurable retention periods per pattern type

### State Objects
```python
{
    "pattern_id": "MES_15m_FVG_20240115_143000",
    "instrument": "MES",
    "timeframe": "15m",
    "pattern_type": "FVG",
    "direction": "bullish",
    "mean_threshold": 4567.25,
    "upper_bound": 4570.50,
    "lower_bound": 4564.00,
    "status": "active",
    "created_at": "2024-01-15T14:30:00Z",
    "last_updated": "2024-01-15T14:30:00Z"
}
```

## 🔧 Configuration

### Pattern Settings
- **Sensitivity**: Adjustable detection parameters
- **Timeframe Filters**: Enable/disable specific timeframes
- **Alert Thresholds**: Minimum conditions for alerts
- **Session Filters**: Trade only during specific market sessions

### Alert Preferences
- **Frequency Limits**: Maximum alerts per hour/day
- **Priority Levels**: Filter by alert importance
- **Quiet Hours**: Disable alerts during specified times
- **Confluence Requirements**: Multi-pattern confirmation settings

## 🚀 Setup Instructions

### Prerequisites
```bash
# Python 3.9+
pip install -r requirements.txt

# Database setup
python setup_database.py

# Configuration
cp config.template.yaml config.yaml
# Edit config.yaml with your settings
```

### Data Source Configuration
```yaml
data_source:
  provider: "interactive_brokers"  # or "tradingview", "polygon"
  credentials:
    # Provider-specific credentials
  
instruments:
  - symbol: "MES"
    contract_month: "current"
  - symbol: "MNQ" 
    contract_month: "current"
```

### Alert Configuration
```yaml
alerts:
  discord:
    webhook_url: "YOUR_DISCORD_WEBHOOK"
  telegram:
    bot_token: "YOUR_BOT_TOKEN"
    chat_id: "YOUR_CHAT_ID"
  
  preferences:
    max_alerts_per_hour: 20
    quiet_hours: ["22:00", "06:00"]
    minimum_priority: "medium"
```

## 📈 Usage Examples

### Basic Monitoring
```python
# Start the scanner
python main_scanner.py

# Monitor specific patterns
python main_scanner.py --patterns FVG,OrderBlock --timeframes 15m,30m
```

### Custom Alerts
```python
# High priority alerts only
python main_scanner.py --priority high

# Specific instrument focus
python main_scanner.py --instruments MES
```

## 🔍 Monitoring & Debugging

### Logging
- **Level**: Configurable (DEBUG, INFO, WARNING, ERROR)
- **Output**: Console and file logging
- **Pattern Logs**: Detailed pattern formation and state changes

### Performance Metrics
- **Processing Time**: Per candle analysis duration
- **Alert Latency**: Time from pattern detection to alert delivery
- **State Size**: Memory usage of active patterns

## 🛠️ Development Roadmap

### Phase 1: MVP (Current)
- [x] Basic FVG detection and mean threshold alerts
- [ ] State management system
- [ ] Simple Discord alerting
- [ ] MES/MNQ data ingestion

### Phase 2: Core Patterns
- [ ] Order Block detection
- [ ] MSS/BOS identification
- [ ] SMT divergence alerts
- [ ] Multi-timeframe coordination

### Phase 3: Advanced Features
- [ ] Machine learning pattern validation
- [ ] Backtesting capabilities
- [ ] Performance analytics
- [ ] Mobile app integration

## 🤝 Contributing

### Development Guidelines
1. Follow PEP 8 style guide
2. Add unit tests for new pattern detectors
3. Update documentation for new features
4. Test alerts before committing

### Testing
```bash
# Run unit tests
python -m pytest tests/

# Test specific pattern
python -m pytest tests/test_fvg_detector.py

# Integration tests
python -m pytest tests/integration/
```

## 📝 License
MIT License - See LICENSE file for details

## 🔗 References
- [ICT Methodology Documentation](link-to-ict-resources)
- [CME Futures Specifications](https://www.cmegroup.com/micro-e-mini.html)
- [TradingView Pine Script Documentation](https://www.tradingview.com/pine-script-docs/)

---

**⚠️ Disclaimer**: This system is for educational and research purposes. Trading futures involves substantial risk and is not suitable for all investors. Past performance does not guarantee future results. 