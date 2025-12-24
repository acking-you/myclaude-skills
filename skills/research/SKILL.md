---
name: research
description: Use codex web search for technical research, output reports with complete citation links. Focus on key results users care about, minimize irrelevant content.
---

# Technical Research Skill

Use codex web search for online research, output structured reports with citations.

## Core Principles

1. **Codex only retrieves**: Get raw sources and links, analyze and organize yourself
2. **Focus on key results**: Only keep what users care about, trim irrelevant info
3. **Links must be complete**: All citations need clickable sources

## Research Workflow

### 1. Clarify Research Goals

Confirm with user:
- What's the core question?
- What needs comparison?
- Which aspects matter? (architecture/performance/use cases/cost)

### 2. Batch Retrieval

Use codex web search in multiple queries, each focused on one topic:

```bash
codex e -m gpt-5.1-codex -c model_reasoning_effort=high \
  --enable web_search_request \
  --dangerously-bypass-approvals-and-sandbox \
  --skip-git-repo-check \
  "Return RAW search results with URLs. Search: <specific query>"
```

**Query Tips**:
- Add year constraints: `2024 2025`
- Request raw links: `Return RAW search results with URLs`
- Focus each query on single topic, avoid overly broad searches

**Example Queries**:
```bash
# Architecture features
"Return RAW search results with URLs. Search: OpenSearch unique features architecture 2024 2025"

# Comparison
"Return RAW search results with URLs. Search: OpenSearch vs Elasticsearch key differences 2024 2025"

# Performance data
"Return RAW search results with URLs. Search: OpenSearch performance benchmark 2024 2025"

# History
"Return RAW search results with URLs. Search: OpenSearch history timeline fork Elasticsearch"
```

### 3. Extract Key Information

From codex results, extract:
- Key facts and data
- Technical details and principles
- Corresponding URLs

### 4. Analyze and Organize Yourself

**Don't let codex write the report**. Do it yourself:
- Filter valuable information
- Organize structure
- Add analysis and insights
- Unify citation format

## Output Format

### Citation Format (Clickable Links)

Inline citation:
```markdown
OpenSearch forked from Elasticsearch 7.10 in 2021 (source: [AWS OpenSearch Blog]).
```

Link definitions at end:
```markdown
[AWS OpenSearch Blog]: https://aws.amazon.com/blogs/opensource/...
```

### Report Structure

```markdown
# [Topic] Research Report

## 1. Overview
What it is, what problem it solves

## 2. Core Features/Architecture
Key technical points with citations

## 3. Comparison (if applicable)
Table comparison, each item with source

## 4. Recommendations
Conclusions based on research

## References
[Link Name 1]: URL1
[Link Name 2]: URL2
...
```

## Guidelines

- **Don't fabricate data**: No performance numbers without sources
- **Trim sections**: Only keep what users care about
- **Valid links**: Prefer official docs, reputable tech blogs
- **Declarative titles**: Don't use questions as headings

## Example Research Task

User: Research differences between OpenSearch and Elasticsearch

Steps:
1. Search OpenSearch unique features
2. Search architecture differences
3. Search licensing and governance differences
4. Search performance comparisons (with sources)
5. Organize into report, add links to all citations
