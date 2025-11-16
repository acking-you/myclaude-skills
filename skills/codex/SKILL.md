---
name: codex
description: Execute Codex CLI for code analysis, refactoring, and automated code changes. Use when you need to delegate complex code tasks to Codex AI with file references (@syntax) and structured output.
---

# Codex CLI Integration

## Overview

Execute Codex CLI commands and parse structured JSON responses. Supports file references via `@` syntax, multiple models, and sandbox controls.

## When to Use

- Complex code analysis requiring deep understanding
- Large-scale refactoring across multiple files
- Automated code generation with safety controls
- Tasks requiring specialized reasoning models (o3, gpt-5)

## Usage

**Recommended approach** (use uv run to manage the Python environment automatically):
```bash
uv run ~/.claude/skills/codex/scripts/codex.py "<task>" [model] [working_dir]
```

**Alternative approach** (run directly or via Python):
```bash
~/.claude/skills/codex/scripts/codex.py "<task>" [model] [working_dir]
# Or
python3 ~/.claude/skills/codex/scripts/codex.py "<task>" [model] [working_dir]
```

Resume session:
```bash
uv run ~/.claude/skills/codex/scripts/codex.py resume <session_id> "<task>" [model] [working_dir]
```

## Timeout Control

- **Built-in**: Script enforces 2-hour timeout by default
- **Override**: Set `CODEX_TIMEOUT` environment variable (in milliseconds, e.g., `CODEX_TIMEOUT=3600000` for 1 hour)
- **Behavior**: On timeout, sends SIGTERM, then SIGKILL after 5s if process doesn't exit
- **Exit code**: Returns 124 on timeout (consistent with GNU timeout)
- **Bash tool**: Always set `timeout: 7200000` parameter for double protection

### Parameters

- `task` (required): Task description, supports `@file` references
  - **Important**: When task length exceeds 800 characters, the script automatically switches to stdin mode to avoid shell escaping issues
  - You will see a warning in stderr: `WARN: Task length (XXX chars) exceeds threshold, using stdin mode...`
  - This behavior is transparent and handled automatically - no manual intervention needed
- `model` (optional): Model to use (default: gpt-5.1-codex)
  - `gpt-5.1-codex`: Default, optimized for code
  - `gpt-5`: Fast general purpose
- `working_dir` (optional): Working directory (default: current)

### Return Format

Extracts `agent_message` from Codex JSON stream and appends session ID:
```
Agent response text here...

---
SESSION_ID: 019a7247-ac9d-71f3-89e2-a823dbd8fd14
```

Error format (stderr):
```
ERROR: Error message
```

### Invocation Pattern

When calling via Bash tool, always include the timeout parameter:
```
Bash tool parameters:
- command: uv run ~/.claude/skills/codex/scripts/codex.py "<task>" [model] [working_dir]
- timeout: 7200000
- description: <brief description of the task>
```

Alternatives:
```
# Direct execution (simplest)
- command: ~/.claude/skills/codex/scripts/codex.py "<task>" [model] [working_dir]

# Using python3
- command: python3 ~/.claude/skills/codex/scripts/codex.py "<task>" [model] [working_dir]
```

### Examples

**Basic code analysis:**
```bash
# Recommended: via uv run (auto-manages Python environment)
uv run ~/.claude/skills/codex/scripts/codex.py "explain @src/main.ts"
# timeout: 7200000

# Alternative: direct execution
~/.claude/skills/codex/scripts/codex.py "explain @src/main.ts"
```

**Refactoring with specific model:**
```bash
uv run ~/.claude/skills/codex/scripts/codex.py "refactor @src/utils for performance" "gpt-5"
# timeout: 7200000
```

**Multi-file analysis:**
```bash
uv run ~/.claude/skills/codex/scripts/codex.py "analyze @. and find security issues" "gpt-5-codex" "/path/to/project"
# timeout: 7200000
```

**Resume previous session:**
```bash
# First session
uv run ~/.claude/skills/codex/scripts/codex.py "add comments to @utils.js" "gpt-5-codex"
# Output includes: SESSION_ID: 019a7247-ac9d-71f3-89e2-a823dbd8fd14

# Continue the conversation
uv run ~/.claude/skills/codex/scripts/codex.py resume 019a7247-ac9d-71f3-89e2-a823dbd8fd14 "now add type hints"
# timeout: 7200000
```

**Using python3 directly (alternative):**
```bash
python3 ~/.claude/skills/codex/scripts/codex.py "your task here"
```

## Notes

- **Recommended**: Use `uv run` for automatic Python environment management (requires uv installed)
- **Alternative**: Direct execution `./codex.py` (uses system Python via shebang)
- Python implementation using standard library (zero dependencies)
- Cross-platform compatible (Windows/macOS/Linux)
- PEP 723 compliant (inline script metadata)
- Runs with `--dangerously-bypass-approvals-and-sandbox` for automation (new sessions only)
- Uses `--skip-git-repo-check` to work in any directory
- Streams progress, returns only final agent message
- Every execution returns a session ID for resuming conversations
- Requires Codex CLI installed and authenticated

### Automatic stdin Mode (800+ Character Threshold)

The wrapper automatically handles long task inputs to avoid shell argument length limits and escaping issues:

- **Threshold**: 800 characters (configurable via `STDIN_THRESHOLD` in codex.py)
- **Behavior**: When task exceeds threshold, codex.py:
  1. Writes warning to stderr: `WARN: Task length (XXX chars) exceeds threshold, using stdin mode...`
  2. Passes `-` to codex CLI (signals stdin input)
  3. Writes task content to process stdin
  4. Closes stdin pipe
- **Transparent**: No change in command syntax required - just pass long strings normally
- **Applies to**: Both new sessions and resume mode
- **Why**: Prevents issues with shell quoting, special characters, and argument length limits across different shells (bash/zsh/PowerShell)
