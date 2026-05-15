# Moodle AI Testing POC

Automated Moodle QA testing using Anthropic Claude + Chrome MCP (Playwright).

## How it works

1. You write a test in plain English (Markdown)
2. The agent connects to a headless Chromium browser via MCP
3. Claude reads the test steps and drives the browser using semantic tools
4. Results are printed step by step with PASS/FAIL

The MCP accessibility tree keeps token usage low — the model sees a compact semantic
representation of the page rather than raw HTML.

## Setup

```bash
# 1. Install Node deps + Chromium
npm install
npx playwright install chromium

# 2. Create Python virtualenv and install deps
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env and fill in your API key and Moodle QA URL
```

## Running a test

```bash
source .venv/bin/activate
python runner.py tests/test_login.md
```

## Writing tests

Drop a `.md` file in the `tests/` folder. Plain English steps work best:

```markdown
# Test: Some Moodle Feature

## Steps
1. Navigate to the site
2. Do something
3. Check something

## Expected Results
- Something should be visible
- Something else should happen
```

## Changing the model

Edit `MODEL` in `agent/moodle_agent.py`:

| Model | Speed | Cost | Use for |
|-------|-------|------|---------|
| `claude-haiku-3-5` | Fastest | Cheapest | Simple tests |
| `claude-sonnet-4-5` | Balanced | Medium | Default |
| `claude-opus-4-5` | Slower | Higher | Complex flows |

