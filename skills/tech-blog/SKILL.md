---
name: tech-blog
description: Write technical blog posts with source code analysis. Use when user wants to explain system internals, implementation details, or technical concepts with code references.
---

# Technical Blog Writing Skill

Write technical blog posts that explain system internals and source code implementation. Focus on progressive explanation, accurate analysis, and clear structure.

## When to Use

- Explaining system internals or implementation details
- Source code analysis and walkthrough
- Technical concept explanation with code examples
- Comparing different implementations or approaches

## Core Principles

### 1. Progressive Explanation (循序渐进)

- Start with the problem, not the solution
- Build concepts layer by layer
- Each section should naturally lead to the next
- Add transition sentences between sections

**Bad**: "V2 uses permutation to restore order" (assumes reader knows context)
**Good**: "After understanding how the main branch outputs sorted results, we need to solve a new problem: how to align the lazy branch's data back to this order?"

### 2. Technical Accuracy Over Marketing

- Avoid superlatives and marketing language
- Use precise technical terms
- Back claims with data or code references
- Acknowledge limitations and trade-offs

**Bad**: "This revolutionary optimization achieves incredible performance gains"
**Good**: "V2 reduces order restoration from O(n log n) to O(n) by using inverted_permutation"

### 3. Balanced Comparison

When comparing approaches, analyze BOTH sides thoroughly:
- Don't cherry-pick advantages of one approach
- Understand the mechanisms of all approaches before comparing
- Identify what's truly different vs. what's equivalent

**Bad**: "V2 is faster because it has mark-level filtering" (if the other approach also has it)
**Good**: "Both V2 and AST rewrite support mark-level filtering. The key difference is order restoration: V2 uses O(n) permutation while AST rewrite requires O(n log n) secondary sort"

### 4. Data-Driven Conclusions

- Don't exaggerate differences
- Consider scale and context
- Identify what's the "big picture" vs. minor details

**Bad**: "V2 uses 20% more memory due to metadata overhead"
**Good**: "V2 uses ~140 MiB more memory (887 vs 747 MiB). This is mainly metadata overhead; as data volume grows, this percentage shrinks since real column data dominates memory usage"

## Document Structure

### Required Sections

```markdown
# [Topic] Deep Dive

Brief introduction: what this article covers and why it matters.

> **Code Version**: Based on [project] `vX.Y.Z` tag.

## Table of Contents
[Auto-generated or manual]

## 1. Introduction
- Problem statement with concrete example
- Why this matters (performance, usability, etc.)
- Scope of this article

## 2. Background / Prerequisites
- Concepts reader needs to understand
- Related systems or components
- Link to external resources if needed

## 3-N. Core Content
[Organized by logical flow, not by code structure]

## N+1. Comparison / Trade-offs
- Compare approaches fairly
- Use tables for structured comparison
- Explain WHY differences exist

## N+2. Debugging / Troubleshooting (optional)
- How to verify the behavior
- Common issues and solutions

## N+3. Code Index
- Key files and their purposes
- Key functions with line numbers
- Version/tag reference

## References
- Official docs, PRs, issues
- Related blog posts
```

### Section Transitions

Every section should have a natural connection to the next:

```markdown
### 1.4 Trigger Conditions

[Content about when optimization triggers]

### 1.5 Key Components

After meeting the above conditions, the optimizer uses these components to implement lazy materialization:

[Component table]
```

## Writing Guidelines

### Code Examples

- Show real code from the codebase, not pseudo-code (unless simplifying for clarity)
- Include file path and line numbers
- Explain what the code does, not just show it

```markdown
`prepareMainChunk()` extracts row indices and generates the permutation array:

​```cpp
// src/Processors/Transforms/LazilyMaterializingTransform.cpp:242-263
void prepareMainChunk()
{
    // 1. Merge main branch chunks
    auto chunk = Squashing::squash(std::move(chunks));

    // 2. Extract __global_row_index column
    auto index_col = chunk.detachColumn("__global_row_index");

    // 3. Sort by __global_row_index to generate permutation
    stableGetPermutation(index_col, permutation);
    // ...
}
​```
```

### Diagrams

- Use ASCII diagrams for simple flows (renders everywhere)
- Use Mermaid for complex diagrams (if supported)
- Every diagram needs explanation text

```markdown
​```
┌─────────────────────────────────────────────────────────────┐
│              JoinLazyColumnsStep                             │
│         ┌──────────┴──────────┐                              │
│         │                     │                              │
│      Main Branch          Lazy Branch                        │
│         │                     │                              │
│    LimitStep          LazilyReadFromMergeTree                │
└─────────────────────────────────────────────────────────────┘
​```

The diagram shows V2's dual-branch architecture: main branch handles sorting and filtering, lazy branch reads deferred columns concurrently.
```

### Tables

Use tables for:
- Feature comparisons
- Performance data
- Component summaries

```markdown
| Metric | V1 | V2 | AST Rewrite |
|--------|----|----|-------------|
| Read granularity | Row-by-row | Batch (mark) | Batch |
| Concurrency | No | Yes | Yes |
| Secondary sort | No | No | **Yes** |
```

## Common Mistakes to Avoid

1. **Abrupt transitions**: Jumping between topics without connection
2. **One-sided comparison**: Only analyzing one approach in detail
3. **Exaggerated claims**: "20% more memory" when it's actually minor overhead
4. **Missing context**: Showing code without explaining its role
5. **Redundant sections**: Repeating the same information in different places
6. **Deprecated content**: Spending too much time on obsolete implementations

## Verification Checklist

Before finalizing:

- [ ] Each section flows naturally to the next
- [ ] All comparisons analyze both sides fairly
- [ ] Data claims are accurate and contextualized
- [ ] Code examples include file paths and line numbers
- [ ] Diagrams have explanatory text
- [ ] No marketing language or exaggeration
- [ ] Deprecated features are briefly mentioned, not detailed
- [ ] Code version/tag is specified

## Output

- Location: `docs/`, `ai_docs/`, or project-specific docs folder
- Filename: `[topic-name].md` or `[topic-name]-deep-dive.md`
- Language: Match user's language preference (Chinese/English)
