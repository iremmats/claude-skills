---
name: schoolsoft-news
description: Use when the user asks about school news, SchoolSoft updates, nyheter from school, or wants to read messages from their children's school
allowed-tools: Bash(python3 *fetch_news.py*)
---

# SchoolSoft News

Fetch and display news from SchoolSoft for the user's children as a guardian (vardnadshavare).

## Prerequisites

- Python 3 with `requests` and `beautifulsoup4` installed
- A SchoolSoft account with mobile login enabled
- Your school must support login type 4 (mobile app login)

## Required Environment Variables

Set these in `~/.claude/settings.json` under `env`, or in your shell profile:

- `SCHOOLSOFT_USERNAME` — your SchoolSoft login username
- `SCHOOLSOFT_SCHOOL` — your school's URL name (the part after `sms.schoolsoft.se/` in the login URL)
- `SCHOOLSOFT_PASSWORD` — your SchoolSoft password

## How to Use

Run the fetch script:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/schoolsoft-news/fetch_news.py
```

The script outputs formatted news articles to stdout. Present the output directly to the user — it is already cleanly formatted with Swedish characters handled correctly.

If the script fails with missing environment variables, tell the user which variables need to be set.
