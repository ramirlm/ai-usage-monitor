# AI Usage Monitor

A CLI tool to monitor usage of various AI services including Claude (Anthropic), OpenAI (Codex/Copilot), and more.

## Features

- 🔍 Monitor multiple AI services from a single CLI
- 🔑 Load API keys from environment variables
- 📊 Beautiful terminal output with status indicators
- ⚡ Quick status check of all configured services
- 🔧 Easy configuration via `.env` file

## Supported Services

- **Claude (Anthropic)** - Advanced AI assistant
- **OpenAI** - Codex, Copilot, and GPT models
- More services can be added easily!

## Installation

1. Clone this repository:
```bash
git clone https://github.com/ramirlm/ai-usage-monitor.git
cd ai-usage-monitor
```

2. Install dependencies:
```bash
pip install -r requirements.txt
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
```

## Usage

Run the monitor to check the status of all configured AI services:

**Option 1: Using the wrapper script (recommended)**
```bash
./ai-monitor
```

**Option 2: Direct Python execution**
```bash
python monitor.py
```

**Option 3: Make it globally available**
```bash
# Add to your PATH or create a symlink
sudo ln -s $(pwd)/ai-monitor /usr/local/bin/ai-monitor
ai-monitor
```

### Output Example

The tool displays a beautiful table showing:
- Service name
- Configuration status
- API key prefix (for verification)
- Links to usage dashboards

## Environment Variables

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key for Claude |
| `OPENAI_API_KEY` | Your OpenAI API key for Codex/Copilot/GPT |

## Development

To add support for additional AI services:

1. Add a new method in `AIUsageMonitor` class (e.g., `check_service_usage()`)
2. Add the service check to the `display_usage()` method
3. Add any required API keys to `.env.example`

## License

MIT License - feel free to use and modify as needed!