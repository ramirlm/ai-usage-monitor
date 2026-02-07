# AI Usage Monitor Dashboard - Setup Guide

## Quick Start (5 minutes)

### 1. Clone and Setup
```bash
git clone https://github.com/ramirlm/ai-usage-monitor.git
cd ai-usage-monitor
```

### 2. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 3. Initialize Database
```bash
python3 cli.py init
```

### 4. Generate Sample Data (Optional)
```bash
python3 generate_sample_data.py
```

### 5. Start Dashboard
```bash
python3 cli.py dashboard
```

Open your browser to: **http://localhost:3000**

## Alternative: Use Quick Start Script
```bash
./start-dashboard.sh
```

## CLI Commands Reference

### Database Initialization
```bash
cd backend
python3 cli.py init
```

### Budget Management
```bash
# Set global monthly budget
python3 cli.py budget set 300

# Set budget with custom alert threshold (80% = 0.8)
python3 cli.py budget set 300 --threshold 0.8

# Set service-specific budget
python3 cli.py budget set 200 --service anthropic
python3 cli.py budget set 80 --service openai
python3 cli.py budget set 20 --service synthetic

# View current budget status
python3 cli.py budget status
```

Output example:
```
============================================================
  Budget Status - February 2026
============================================================

  Global Budget:      $300.00
  Current Spend:      $247.52 (82.5%)
  Projected:          $310.00
  Remaining:          $52.48
  ⚠ Warning: Projected to exceed budget by $10.00

  Service Breakdown:
  --------------------------------------------------------
  anthropic            $  142.30  ( 57.5%)
  openai               $   89.12  ( 36.0%)
  synthetic            $   16.10  (  6.5%)

============================================================
```

### Reports
```bash
# Generate report for current month
python3 cli.py report

# Generate report for specific month
python3 cli.py report --month 2026-02
```

Output example:
```
======================================================================
  AI Usage Report - 2026-02
======================================================================

  Total Monthly Cost: $247.52

  Cost by Service:
  ------------------------------------------------------------------
  anthropic            $  142.30  ( 57.5%)  12,400,000 tokens
  openai               $   89.12  ( 36.0%)  4,200,000 tokens
  synthetic            $   16.10  (  6.5%)  8,050,000 tokens

======================================================================
```

### Data Sync (Framework)
```bash
# Sync usage data from AI service APIs
python3 cli.py sync
```

*Note: This currently requires implementation of service-specific API integrations.*

### Export (Framework)
```bash
# Export data to CSV
python3 cli.py export --start 2026-02-01 --end 2026-02-28 --format csv

# Export data to JSON
python3 cli.py export --start 2026-02-01 --end 2026-02-28 --format json
```

*Note: This currently requires implementation.*

## API Endpoints

### Dashboard Overview
```bash
curl http://localhost:3000/api/dashboard | jq
```

Response:
```json
{
  "monthly_cost": 247.52,
  "budget": 300.00,
  "budget_used": 82.5,
  "projected_cost": 310.00,
  "over_budget": true,
  "service_breakdown": [
    {
      "service": "anthropic",
      "total_cost": 142.30,
      "total_tokens": 12400000,
      "input_tokens": 9920000,
      "output_tokens": 2480000
    }
  ],
  "alerts": [],
  "last_updated": "2026-02-07T23:00:00"
}
```

### Daily Costs
```bash
curl "http://localhost:3000/api/costs/daily?days=30" | jq
```

### Service-Specific Costs
```bash
curl http://localhost:3000/api/costs/service/anthropic | jq
```

### Budget Settings
```bash
# Get budget
curl http://localhost:3000/api/budget | jq

# Set budget
curl -X POST http://localhost:3000/api/budget \
  -H "Content-Type: application/json" \
  -d '{"monthly_budget": 300, "alert_threshold": 0.8}'
```

### Alerts
```bash
# Get all alerts
curl http://localhost:3000/api/alerts | jq

# Get unacknowledged alerts only
curl "http://localhost:3000/api/alerts?unacknowledged=true" | jq

# Acknowledge an alert
curl -X POST http://localhost:3000/api/alerts/1/acknowledge
```

### Add Usage Data (Manual)
```bash
curl -X POST http://localhost:3000/api/usage/add \
  -H "Content-Type: application/json" \
  -d '{
    "service": "anthropic",
    "model": "claude-sonnet-4",
    "input_tokens": 1000000,
    "output_tokens": 500000,
    "cost": 10.50
  }'
```

## Database Schema

### Tables

#### usage_snapshots
Individual usage records:
- `id`: Primary key
- `timestamp`: When the usage occurred
- `service`: Service name (anthropic, openai, synthetic)
- `model`: Model name
- `input_tokens`: Number of input tokens
- `output_tokens`: Number of output tokens
- `total_tokens`: Total tokens (input + output)
- `cost`: Cost in dollars
- `metadata`: Optional JSON metadata

#### daily_summaries
Aggregated daily statistics:
- `id`: Primary key
- `date`: Date (YYYY-MM-DD)
- `service`: Service name
- `model`: Model name
- `total_input_tokens`: Aggregated input tokens
- `total_output_tokens`: Aggregated output tokens
- `total_tokens`: Total tokens
- `total_cost`: Total cost

#### alerts
Alert history:
- `id`: Primary key
- `timestamp`: When the alert was created
- `type`: Alert type (budget_threshold, anomaly_detection, etc.)
- `severity`: Severity level (info, warning, error, critical)
- `message`: Alert message
- `details`: Additional details
- `acknowledged`: Whether the alert has been acknowledged
- `acknowledged_at`: When it was acknowledged

#### budget_settings
Budget configurations:
- `id`: Primary key
- `service`: Service name (NULL for global budget)
- `monthly_budget`: Monthly budget amount
- `alert_threshold`: Threshold percentage for alerts (0.0-1.0)
- `updated_at`: Last update timestamp

## Cost Calculations

### Pricing (per million tokens)

**Anthropic (Claude):**
- claude-sonnet-4: $3.00 input, $15.00 output
- claude-opus-4: $15.00 input, $75.00 output
- claude-haiku: $0.80 input, $4.00 output

**OpenAI:**
- gpt-4: $30.00 input, $60.00 output
- gpt-4-turbo: $10.00 input, $30.00 output
- gpt-3.5-turbo: $0.50 input, $1.50 output

**Synthetic:**
- default: $1.00 input, $2.00 output

### Example Cost Calculation
```python
from app.cost_calculator import CostCalculator

# Calculate cost for Claude Sonnet
cost = CostCalculator.calculate_cost(
    service='anthropic',
    model='claude-sonnet-4',
    input_tokens=1000000,   # 1M input tokens
    output_tokens=500000    # 500K output tokens
)
print(f"Cost: ${cost:.2f}")  # Cost: $10.50
```

## Troubleshooting

### Database Locked Error
If you get a "database is locked" error:
```bash
# Stop any running dashboard instances
pkill -f "python3.*server.py"

# Remove the lock file
rm backend/ai-usage.db-journal
```

### Port Already in Use
If port 3000 is already in use:
```bash
# Find and kill the process using port 3000
lsof -ti:3000 | xargs kill -9

# Or modify the port in backend/app/server.py (last line)
```

### Dependencies Not Installing
```bash
# Update pip
pip3 install --upgrade pip

# Install dependencies with verbose output
pip3 install -v -r backend/requirements.txt
```

## Development

### Running in Development Mode
```bash
cd backend
python3 app/server.py
```

The Flask server will start with debug mode enabled, providing:
- Auto-reload on code changes
- Detailed error messages
- Interactive debugger

### Direct Database Access
```bash
# Open SQLite shell
sqlite3 backend/ai-usage.db

# View tables
.tables

# Query data
SELECT * FROM usage_snapshots ORDER BY timestamp DESC LIMIT 10;
SELECT * FROM daily_summaries;
SELECT * FROM budget_settings;
SELECT * FROM alerts WHERE acknowledged = 0;

# Exit
.quit
```

### Testing API Endpoints
```bash
# Test all endpoints
cd backend

# Dashboard
curl -s http://localhost:3000/api/dashboard | jq

# Daily costs
curl -s "http://localhost:3000/api/costs/daily?days=7" | jq

# Budget
curl -s http://localhost:3000/api/budget | jq

# Alerts
curl -s http://localhost:3000/api/alerts | jq
```

## Production Deployment

### Using systemd (Linux)
Create `/etc/systemd/system/ai-monitor-dashboard.service`:
```ini
[Unit]
Description=AI Usage Monitor Dashboard
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/ai-usage-monitor/backend
ExecStart=/usr/bin/python3 cli.py dashboard
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable ai-monitor-dashboard
sudo systemctl start ai-monitor-dashboard
sudo systemctl status ai-monitor-dashboard
```

### Using Docker (Future)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ .
EXPOSE 3000
CMD ["python3", "cli.py", "dashboard"]
```

### Nginx Reverse Proxy
```nginx
server {
    listen 80;
    server_name ai-monitor.example.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Support

For issues or questions:
1. Check the main README.md
2. Review this SETUP.md guide
3. Open an issue on GitHub
4. Review the code documentation in backend/app/

## License

MIT License - See LICENSE file for details
