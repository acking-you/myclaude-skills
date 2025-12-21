---
name: tech-blog
description: Write technical blog posts with source code analysis. Use when user wants to explain system internals, implementation details, or technical concepts with code references.
---

# Technical Blog Writing Skill

Write technical blog posts that explain system internals and source code implementation.

## When to Use

- Explaining system internals or implementation details
- Source code analysis and walkthrough
- Comparing different implementations or approaches

## Core Principles

### 1. Progressive Explanation
- Start with the problem, not the solution
- Build concepts layer by layer; each section leads to the next
- Explain "why" not just "what"

**Bad**: "V2 uses permutation to restore order"
**Good**: "After the main branch outputs sorted results, we need to solve: how to align the lazy branch's data back to this order?"

### 2. Technical Accuracy
- Avoid marketing language; use precise terms
- Back claims with data or code references
- Explore source code before writing; don't write from memory

**Bad**: "This revolutionary optimization achieves incredible gains"
**Good**: "V2 reduces order restoration from O(n log n) to O(n) by using inverted_permutation"

### 3. Balanced Comparison
- Analyze BOTH sides thoroughly; don't cherry-pick
- Identify what's truly different vs. equivalent

**Bad**: "V2 is faster because it has mark-level filtering" (if both have it)
**Good**: "Both support mark-level filtering. The key difference is order restoration: V2 uses O(n) permutation while AST rewrite requires O(n log n) sort"

### 4. Design Decision Explanation
Explain WHY a design choice was made:
- What problem does it solve? What alternatives exist? What trade-offs?

**Bad**: "V2 uses __global_row_index to identify rows"
**Good**: "V2 uses __global_row_index instead of _part_index + _part_offset because: single dimension sorting, range query friendly, aligns with Mark mechanism"

### 5. Dependency Mechanism Explanation
Explain what makes a feature work:
- What underlying mechanisms does it depend on?
- What assumptions? What if violated?

**Example**: `__global_row_index` depends on StorageSnapshot (holds shared_ptr to Parts). If Parts were merged during query, indices would become invalid.

### 6. Terminology Accuracy
- Verify terms by exploring source code or official docs
- Don't assume terms are interchangeable
- Define domain-specific terms when introducing them

**Bad**: "Distributed queries send to each Replica" (if actually Shards)
**Good**: "Queries send to each Shard (data partition). Within each Shard, one Replica (data copy) is selected."

## Document Structure

```markdown
# [Topic] Deep Dive

Brief intro + why it matters.
> **Code Version**: Based on [project] `vX.Y.Z` tag.

## 1. Introduction (problem + scope)
## 2. Background / Prerequisites
## 3-N. Core Content (by data flow, not code structure)
## N+1. Comparison / Trade-offs
## N+2. Code Index (files, functions, line numbers)
## References
```

**Key guidelines**:
- Chapter 1 = Introduction + Navigation only, no implementation details
- Organize content by data flow, not by code components
- Add reading suggestions for sections that depend on later content:
  `> ⏭️ If reading first time, skip to §X, return here when needed.`

## Writing Guidelines

### Code Examples
- Real code with file path and line numbers
- Explain what it does, not just show it

### Diagrams
- ASCII for simple flows; every diagram needs explanation text

### Tables
- Use for comparisons, performance data, component summaries

## Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| Abrupt transitions | Add connection sentences between sections |
| One-sided comparison | Analyze both approaches before comparing |
| Exaggerated claims | Use concrete numbers with context |
| Code without context | Explain the code's role in the system |
| Too much detail in Chapter 1 | Chapter 1 is navigation only |
| Examples use unexplained concepts | Use well-known examples (FilterTransform, not LazilyMaterializingTransform) |
| Prerequisites too long | State relationship to main topic at each section's start |
| Inaccurate terminology | Explore source code; cite authoritative sources |

## Verification Checklist

- [ ] Sections flow naturally; transitions are smooth
- [ ] Comparisons analyze both sides fairly
- [ ] Code examples include file paths and line numbers
- [ ] Diagrams have explanatory text
- [ ] No marketing language; claims backed by data
- [ ] Code version/tag specified
- [ ] Terminology verified against source code

## Output

- Location: `docs/`, `ai_docs/`, or project-specific folder
- Filename: `[topic-name].md`
- Language: Match user's preference
