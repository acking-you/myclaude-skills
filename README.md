# MyClaude Skills

A collection of reusable Claude-based workflows for code automation and creative front-end design.

## Overview

- **Unified workflow**: `prompts/CLAUDE.md` enforces strict engineering standards across all skills
- **Modular skills**: Independent Claude skills in `skills/` for CLI, API, or CI/CD integration
- **Dual coverage**: Code automation via Codex CLI + creative UI design capabilities

## Structure

```
.
├── prompts/
│   └── CLAUDE.md          # Global workflow configuration
└── skills/
    ├── codex/             # Codex CLI integration
    └── frontend-design/   # Front-end design skill
```

## Components

### prompts/CLAUDE.md
Repository-wide English workflow config defining strict engineering processes, session management, patch review, and test coverage thresholds (≥90%).

### skills/codex/
Codex CLI wrapper for code analysis, refactoring, and automated task execution. Supports large-scale migrations, automated fixes, and conversational IDE workflows.

### skills/frontend-design/
Generate distinctive, high-quality front-end interfaces with unique aesthetics. Includes color systems, layout suggestions, and component hierarchies.

## Usage

1. **Setup**: Configure `CLAUDE_API_KEY` or Codex CLI credentials
2. **Load skills**: Point Codex CLI to `skills/codex/` or reference `skills/frontend-design/` in design tools
3. **Customize**: Copy and adapt `prompts/CLAUDE.md` for new workflows

## Core Scenarios

- **Code review automation**: Combine `prompts/CLAUDE.md` + `skills/codex/` for PR reviews
- **Batch refactoring**: Use Codex CLI with `skills/codex/` for large-scale code changes
- **UI ideation**: Embed `skills/frontend-design/` in Figma plugins for rapid prototyping

## Contributing

Fork, create feature branches, document new skills, and verify changes locally before submitting PRs.
