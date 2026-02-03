# AI Usage Monitor

A lightweight bash CLI tool to monitor usage of various AI services including Claude (Anthropic), OpenAI (Codex/Copilot), Synthetic, and more. Track sessions and usage statistics across all your AI services.

## Features

- 🔍 Monitor multiple AI services from a single CLI
- 📊 Track sessions and usage statistics for Claude, OpenAI Codex, and more
- 💾 Persistent storage of session and usage data
- 🔑 Load API keys from environment variables or `.env` file
- 📈 Beautiful terminal output with status indicators
- ⚡ Quick status check of all configured services
- 🪶 Pure bash - no dependencies required!
- 🌐 Real-time API quota checking for Synthetic

## Supported Services

- **Claude (Anthropic)** - Advanced AI assistant with session and usage tracking
- **OpenAI Codex** - Code generation and completion with usage tracking
- **OpenAI** - GPT models and Copilot with usage tracking
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

## Usage

The tool now supports multiple commands for tracking sessions and usage:

### Check Service Status

Check the configuration status of all AI services:

```bash
./ai-monitor
# or
./ai-monitor status
```

### Track Sessions

Start a new session for a service:

```bash
./ai-monitor start claude
./ai-monitor start openai
./ai-monitor start codex
```

End an active session:

```bash
./ai-monitor end <session_id>
```

View all tracked sessions:

```bash
./ai-monitor sessions
```

### Track Usage

Log usage for a service:

```bash
./ai-monitor log claude 1500 0.02    # 1500 tokens, $0.02 cost
./ai-monitor log openai 2000 0.04    # 2000 tokens, $0.04 cost
./ai-monitor log codex 500 0.01      # 500 tokens, $0.01 cost
```

View usage statistics:

```bash
./ai-monitor usage
```

### Other Commands

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

### Output Example

The tool displays beautiful tables showing:
- Service configuration status with color-coded indicators
- Active and completed sessions with timestamps
- Usage statistics with token counts and costs
- Links to usage dashboards

## Environment Variables

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key for Claude |
| `OPENAI_API_KEY` | Your OpenAI API key for Codex/Copilot/GPT |
| `SYNTHETIC_API_KEY` | Your Synthetic API key (uses api.synthetic.new/v2/quotas) |

## Development

To add support for additional AI services:

1. Add a new function in the script (e.g., `check_new_service()`)
2. Call the function in the main display section
3. Add any required API keys to `.env.example`

## Requirements

- Bash 4.0 or higher
- `curl` for API requests (standard on most systems)
- `jq` (optional) - for prettier quota display from Synthetic API

## License

MIT License - feel free to use and modify as needed!