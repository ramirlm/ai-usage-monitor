# AI Usage Monitor

A comprehensive CLI tool and web dashboard to monitor usage and costs of various AI services including Claude (Anthropic), OpenAI (Codex/Copilot), Synthetic, and more.

## Features

### CLI Tool
- 🔍 Monitor multiple AI services from a single CLI
- 🔑 Load API keys from environment variables or `.env` file
- 📊 Beautiful terminal output with status indicators
- ⚡ Quick status check of all configured services
- 🪶 Pure bash - no dependencies required for basic monitoring!
- 🌐 Real-time API quota checking for Synthetic

### Web Dashboard (NEW!)
- 💰 **Cost Tracking**: Real-time monitoring of AI spending across all services
- 📊 **Budget Management**: Set monthly budgets with automatic alerts
- 📈 **Historical Data**: Track usage trends and costs over time
- ⚠️ **Smart Alerts**: Automatic notifications for budget thresholds and anomalies
- 🎯 **Cost Projections**: Linear projection of monthly spending
- 📉 **Service Breakdown**: Detailed cost analysis by service and model
- 🖥️ **Beautiful UI**: Modern, responsive dashboard interface

## Supported Services

- **Claude (Anthropic)** - Advanced AI assistant
- **OpenAI** - Codex, Copilot, and GPT models
- **Synthetic** - AI service with real-time quota monitoring via API
- More services can be added easily!

## Installation

1. Clone this repository:
```bash
git clone https://github.com/ramirlm/ai-usage-monitor.git
cd ai-usage-monitor
```

2. Make the script executable:
```bash
chmod +x ai-monitor
```

3. Configure your API keys:
```bash
cp .env.example .env
# Edit .env and add your API keys
```

Or export them directly:
```bash
export ANTHROPIC_API_KEY="your-anthropic-key"
export OPENAI_API_KEY="your-openai-key"
export SYNTHETIC_API_KEY="your-synthetic-key"
```

4. (Optional) Install Python dependencies for the web dashboard:
```bash
cd backend
pip install -r requirements.txt
```

## Usage

### Basic CLI Usage

Run the monitor to check the status of all configured AI services:

**Basic usage:**
```bash
./ai-monitor
```

**Show help:**
```bash
./ai-monitor --help
```

**Show version:**
```bash
./ai-monitor --version
```

**Make it globally available:**
```bash
# Add to your PATH or create a symlink
sudo ln -s $(pwd)/ai-monitor /usr/local/bin/ai-monitor
ai-monitor
```

### Extended CLI Commands

The new Python-based CLI provides advanced features:

#### Initialize Database
```bash
cd backend
python3 cli.py init
```

#### Budget Management
```bash
# Set global monthly budget
python3 cli.py budget set 300

# Set service-specific budget
python3 cli.py budget set 200 --service anthropic
python3 cli.py budget set 80 --service openai

# View budget status
python3 cli.py budget status
```

#### Generate Reports
```bash
# Generate report for current month
python3 cli.py report

# Generate report for specific month
python3 cli.py report --month 2026-02
```

#### Start Web Dashboard
```bash
# Launch the web dashboard
python3 cli.py dashboard
```

Then open your browser to: http://localhost:3000

### Web Dashboard

The web dashboard provides a comprehensive overview of your AI usage and costs:

**Features:**
- 💰 Real-time cost tracking
- 📊 Budget progress visualization
- 🎯 Cost projections with overage warnings
- 📈 Service breakdown with percentages
- ⚡ Auto-refresh every 5 minutes

**Access:** http://localhost:3000 (when dashboard server is running)

## Dashboard Architecture

### Backend (Python + Flask)
- **Database**: SQLite for historical data storage
- **API**: RESTful API for frontend communication
- **Tables**:
  - `usage_snapshots`: Individual usage records
  - `daily_summaries`: Aggregated daily statistics
  - `alerts`: Alert history
  - `budget_settings`: Budget configurations

### Frontend (HTML + JavaScript)
- **UI**: Modern, responsive dashboard
- **Charts**: Visual cost and usage trends
- **Real-time Updates**: Auto-refresh functionality
- **Mobile-Friendly**: Responsive design

## API Endpoints

The dashboard provides several API endpoints:

- `GET /api/dashboard` - Dashboard overview data
- `GET /api/costs/daily?days=30` - Daily cost data
- `GET /api/costs/service/<service>` - Service-specific costs
- `GET /api/budget` - Get budget settings
- `POST /api/budget` - Set budget settings
- `GET /api/alerts` - Get recent alerts
- `POST /api/alerts/<id>/acknowledge` - Acknowledge alert
- `POST /api/usage/add` - Add usage data manually

## Database Schema

### usage_snapshots
Stores individual usage records with timestamps, service, model, tokens, and cost.

### daily_summaries
Aggregated daily statistics by service and model.

### alerts
Alert history with type, severity, message, and acknowledgment status.

### budget_settings
Budget configurations for global and service-specific budgets.

## Development

### Adding Support for Additional AI Services

1. Add a new function in `ai-monitor` script (e.g., `check_new_service()`)
2. Call the function in the main display section
3. Add any required API keys to `.env.example`
4. Update cost calculations in `backend/app/cost_calculator.py`

### Running Tests

```bash
# Test database initialization
cd backend
python3 -c "from app.database import Database; db = Database(); db.connect(); db.init_schema(); print('✓ Database test passed')"

# Test cost calculator
python3 -c "from app.cost_calculator import CostCalculator; cost = CostCalculator.calculate_cost('anthropic', 'claude-sonnet-4', 1000000, 500000); print(f'✓ Cost calculation test: ${cost:.2f}')"
```

### Adding Test Data

```bash
# Start Python shell
python3

# Add test data
from app.database import Database
from datetime import datetime

db = Database('ai-usage.db')
db.connect()
db.init_schema()

# Add some sample usage
db.add_usage_snapshot('anthropic', 'claude-sonnet-4', 1000000, 500000, 10.50)
db.add_usage_snapshot('openai', 'gpt-4', 500000, 250000, 22.50)
db.add_usage_snapshot('synthetic', 'default', 300000, 150000, 0.90)

# Update daily summaries
today = datetime.now().strftime('%Y-%m-%d')
db.update_daily_summary(today, 'anthropic', 'claude-sonnet-4', 1000000, 500000, 10.50)
db.update_daily_summary(today, 'openai', 'gpt-4', 500000, 250000, 22.50)
db.update_daily_summary(today, 'synthetic', 'default', 300000, 150000, 0.90)

db.close()
print("✓ Test data added successfully!")
```

## Requirements

### Basic CLI
- Bash 4.0 or higher
- `curl` for API requests (standard on most systems)
- `jq` (optional) - for prettier quota display from Synthetic API

### Web Dashboard
- Python 3.7 or higher
- Flask 3.0.0
- Flask-CORS 4.0.0

## Project Structure

```
ai-usage-monitor/
├── ai-monitor              # Main bash CLI script
├── .env.example           # Example environment configuration
├── README.md              # This file
├── backend/               # Python backend
│   ├── requirements.txt   # Python dependencies
│   ├── cli.py            # Extended CLI commands
│   └── app/              # Backend application
│       ├── __init__.py
│       ├── database.py   # Database layer
│       ├── server.py     # Flask API server
│       ├── cost_calculator.py  # Cost calculation logic
│       └── alert_manager.py    # Alert management
└── frontend/             # Frontend dashboard
    └── public/
        └── index.html    # Dashboard UI
```

## Roadmap

Future enhancements:
- [ ] Real-time API data syncing from service providers
- [ ] Advanced analytics and charts (Chart.js integration)
- [ ] Email/Slack/WhatsApp alert notifications
- [ ] PDF report generation
- [ ] CSV/JSON data export
- [ ] Multi-user support with authentication
- [ ] Docker deployment support
- [ ] Calendar heatmap visualization
- [ ] Model-specific cost breakdown
- [ ] Project/tag-based cost tracking

## License

MIT License - feel free to use and modify as needed!