# MyClaude Skills

A collection of reusable Claude-based workflows for code automation, git operations, and creative front-end design.

## Overview

- **Unified workflow**: `prompts/CLAUDE.md` enforces strict engineering standards across all skills
- **Translation guide**: `prompts/TRANSLATE.md` ensures technical content translation accuracy
- **Modular skills**: Independent Claude skills in `skills/` for CLI, API, or CI/CD integration
- **Multi-domain coverage**: Code automation, git workflow automation, and creative UI design

## Structure

```
.
├── prompts/
│   ├── CLAUDE.md          # Global workflow configuration
│   └── TRANSLATE.md       # Translation guidelines for technical content
└── skills/
    ├── codex/             # Codex CLI integration
    ├── frontend-design/   # Front-end design skill
    ├── gen-commit-msg/    # Auto-generate commit messages
    └── git-squash-commits/# Squash commits with auto-generated messages
```

## Components

### prompts/CLAUDE.md
Repository-wide English workflow config defining strict engineering processes, session management, patch review, and test coverage thresholds (≥90%).

### prompts/TRANSLATE.md
Technical content translation guidelines enforcing natural phrasing over literal translation. Defines rules for untranslatable terms (APIs, frameworks, emerging concepts) and preserves code structure while translating prose.

### skills/codex/
Codex CLI wrapper for code analysis, refactoring, and automated task execution. Supports large-scale migrations, automated fixes, and conversational IDE workflows.

### skills/frontend-design/
Generate distinctive, high-quality front-end interfaces with unique aesthetics. Includes color systems, layout suggestions, and component hierarchies.

### skills/gen-commit-msg/
Generate concise commit messages from conversation context or git diff. Prioritizes context-aware generation, falls back to diff analysis, follows conventional commit format with type prefixes (feat, fix, refactor, etc.).

### skills/git-squash-commits/
Squash multiple commits into a single commit with comprehensive auto-generated message. Analyzes commit history, verifies builds before committing, saves operation summaries to `ai_docs/` for audit trail.

## Usage

1. **Setup**: Configure `CLAUDE_API_KEY` or Codex CLI credentials
2. **Load skills**: Point Codex CLI or Claude Code to relevant skills in `skills/`
3. **Git workflows**: Invoke `gen-commit-msg` or `git-squash-commits` directly via Claude Code skills
4. **Customize**: Copy and adapt `prompts/CLAUDE.md` or `prompts/TRANSLATE.md` for new workflows

## Core Scenarios

- **Code review automation**: Combine `prompts/CLAUDE.md` + `skills/codex/` for PR reviews
- **Batch refactoring**: Use Codex CLI with `skills/codex/` for large-scale code changes
- **UI ideation**: Embed `skills/frontend-design/` in Figma plugins for rapid prototyping
- **Smart commits**: Use `skills/gen-commit-msg/` to auto-generate context-aware commit messages
- **History cleanup**: Use `skills/git-squash-commits/` to consolidate messy commit history with comprehensive messages
- **Translation tasks**: Apply `prompts/TRANSLATE.md` for technical documentation or code comment translation

## Contributing

Fork, create feature branches, document new skills, and verify changes locally before submitting PRs.
