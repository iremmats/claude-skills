# Claude Skills

A collection of Claude Code skills and plugins by [iremmats](https://github.com/iremmats). Compatible with Claude Code and OpenClaw.

## Skills

| Plugin | Description |
|--------|-------------|
| **schoolsoft** | Read news from [SchoolSoft](https://www.schoolsoft.se/) as a guardian (vardnadshavare) |

## Installation

### Claude Code (via marketplace)

```bash
# Add the marketplace
/plugin marketplace add iremmats/claude-skills

# Install a plugin
/plugin install schoolsoft@iremmats-skills
```

### OpenClaw

```bash
git clone https://github.com/iremmats/claude-skills.git
cp -r claude-skills/schoolsoft/skills/schoolsoft-news ~/.openclaw/skills/
```

### Manual (Claude Code)

Clone this repo and point Claude Code at the plugin directory:

```bash
git clone https://github.com/iremmats/claude-skills.git
claude --plugin-dir ./claude-skills/schoolsoft
```

## SchoolSoft Plugin

Fetches and displays news from SchoolSoft for your children's school. Logs in as guardian (vardnadshavare) via SchoolSoft's mobile app API.

### Prerequisites

- Python 3 with `requests` and `beautifulsoup4`:
  ```bash
  pip install requests beautifulsoup4
  ```
- A SchoolSoft account with mobile login enabled
- Your school must support login type 4 (check the [school list](https://sms.schoolsoft.se/rest/app/schoollist/prod))

### Configuration

Set the following environment variables. For Claude Code, add them in `~/.claude/settings.json` under `env`. For OpenClaw, set them in your shell profile or workspace config:

| Variable | Description | Example |
|----------|-------------|---------|
| `SCHOOLSOFT_USERNAME` | Your login username | `johndoe0101` |
| `SCHOOLSOFT_SCHOOL` | School URL name (from `sms.schoolsoft.se/<school>/`) | `myschool` |
| `SCHOOLSOFT_PASSWORD` | Your password | |

### Usage

Once installed, just ask Claude:

> "Show me the latest news from school"

The skill activates automatically when you ask about school news.

## License

MIT
