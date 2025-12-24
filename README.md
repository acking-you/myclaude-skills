# MyClaude Skills

Claude Code skills and prompts collection.

## Installation

```bash
./install.sh install-all    # Install all skills to ~/.claude/skills/
./install.sh prompt-update  # Update ~/.claude/CLAUDE.md
```

Run `./install.sh help` for more options.

## Structure

```
.
├── install.sh              # One-click installer
├── prompts/                # Global prompt configs
│   ├── CLAUDE.md           # Workflow configuration
│   └── TRANSLATE.md        # Translation guidelines
└── skills/                 # Claude Code skills
    ├── article-cover/      # Article cover image generation
    ├── codex/              # Codex CLI integration
    ├── excalidraw/         # Excalidraw diagram generation
    ├── frontend-design/    # Frontend UI design
    ├── gemini-image/       # Gemini image generation
    ├── gen-commit-msg/     # Auto-generate commit messages
    ├── git-squash-commits/ # Squash commits
    ├── tech-blog/          # Technical blog post generation
    └── tech-design-doc/    # Technical design doc generation
```
