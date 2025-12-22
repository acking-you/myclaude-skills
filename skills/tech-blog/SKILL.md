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

### 2. Concept-First Principle (概念前置)
Before diving into implementation details, ensure all concepts are introduced:
- **Never use undefined terms**: If a section mentions "Text Index" or "Projection", readers must have seen their definitions first
- **Add concept introduction sections**: Create a dedicated subsection (e.g., §5.4.4.1) to introduce concepts before the detailed implementation sections
- **Use navigation hints**: Add `> ⏭️ If unfamiliar with X, see §Y first` at the start of sections that depend on prior knowledge

**Bad Structure**:
```markdown
#### 5.4.5 Text Index Merge: How it works
Text index segments are merged in Stage2...  ← Reader: "What is Text Index?"
```

**Good Structure**:
```markdown
#### 5.4.4.1 Concepts: Text Index & Projections
[Brief introduction with examples]

#### 5.4.5 Text Index Merge: How it works
> ⏭️ If unfamiliar with Text Index, see §5.4.4.1 first.
Text index segments are merged in Stage2...
```

### 3. Big Picture First (整体图景优先)
Before explaining multiple related concepts in detail, provide a unified visual overview:
- **Add comparison diagrams**: When explaining 2+ related approaches (e.g., Horizontal vs Vertical merge), start with a side-by-side diagram
- **Show the complete flow**: Include all stages/phases in one diagram, even if some are explained later
- **Highlight key differences**: Use the diagram to show WHERE the approaches diverge

**Example**:
```markdown
#### 5.4.2.1 Horizontal vs Vertical: Visual Comparison

Before diving into source code, understand the core difference:

┌─────────────────────┐  ┌─────────────────────────────────────┐
│   Horizontal Merge   │  │         Vertical Merge              │
├─────────────────────┤  ├─────────────────────────────────────┤
│  Stage 0:           │  │  Stage 0: key columns only          │
│  - Read ALL columns │  │  - Read key columns                 │
│  - Merge sort       │  │  - Merge sort → write rows_sources  │
│  - Write ALL columns│  │  - Write key columns                │
│                     │  │                                     │
│  (Stage 1 skipped)  │  │  Stage 1: per-column gather         │
│                     │  │  - For each non-key column:         │
│                     │  │    read → reorder → write           │
└─────────────────────┘  └─────────────────────────────────────┘

> 💡 **Key Difference**: Horizontal processes all columns together (memory = all columns).
> Vertical separates key columns from others (memory = single column at a time).
```

### 4. Technical Accuracy
- Avoid marketing language; use precise terms
- Back claims with data or code references
- Explore source code before writing; don't write from memory

**Bad**: "This revolutionary optimization achieves incredible gains"
**Good**: "V2 reduces order restoration from O(n log n) to O(n) by using inverted_permutation"

### 5. Balanced Comparison
- Analyze BOTH sides thoroughly; don't cherry-pick
- Identify what's truly different vs. equivalent
- **Use comparison tables** for similar concepts (e.g., Projection vs Materialized View)

**Bad**: "V2 is faster because it has mark-level filtering" (if both have it)
**Good**: "Both support mark-level filtering. The key difference is order restoration: V2 uses O(n) permutation while AST rewrite requires O(n log n) sort"

**Comparison Table Example**:
```markdown
| Feature | Projection | Materialized View |
|---------|------------|-------------------|
| Storage | Embedded in each part | Separate table |
| Consistency | Atomic with main data | Async, may lag |
| Query selection | Automatic | Explicit query |
| Use case | Same data, different views | Cross-table aggregation |
```

### 6. Design Decision Explanation
Explain WHY a design choice was made:
- What problem does it solve? What alternatives exist? What trade-offs?

**Bad**: "V2 uses __global_row_index to identify rows"
**Good**: "V2 uses __global_row_index instead of _part_index + _part_offset because: single dimension sorting, range query friendly, aligns with Mark mechanism"

### 7. Dependency Mechanism Explanation
Explain what makes a feature work:
- What underlying mechanisms does it depend on?
- What assumptions? What if violated?

**Example**: `__global_row_index` depends on StorageSnapshot (holds shared_ptr to Parts). If Parts were merged during query, indices would become invalid.

### 8. Terminology Accuracy
- Verify terms by exploring source code or official docs
- Don't assume terms are interchangeable
- Define domain-specific terms when introducing them

**Bad**: "Distributed queries send to each Replica" (if actually Shards)
**Good**: "Queries send to each Shard (data partition). Within each Shard, one Replica (data copy) is selected."

### 9. Concrete Examples with Data Flow
- Add 1-2 practical examples per major section
- Examples should trace real data flow, not abstract concepts
- Show input → process → output clearly
- For beginners: use simple, relatable scenarios
- **For abstract concepts**: Use concrete data examples to make them tangible

**Bad**: "The merge selector chooses parts based on size"
**Good**: "Given parts [1MB, 2MB, 3MB, 10MB], the selector picks [1MB, 2MB, 3MB] because their total (6MB) is closest to the largest part (10MB) without exceeding it"

**Example for Abstract Concepts (Inverted Index)**:
```markdown
**How Inverted Index Works**:

Original data (message column):
  row 0: "error in database connection"
  row 1: "user login successful"
  row 2: "database timeout error"

Inverted index (word → row list):
  "error"      → [0, 2]
  "database"   → [0, 2]
  "connection" → [0]
  "user"       → [1]
  ...

Query `WHERE message LIKE '%database%'` → directly lookup [0, 2], no full scan needed.
```

### 10. Key Point Callouts
Use callout boxes to highlight important insights:
- 💡 **Key Point**: Critical design decisions or insights
- 🤔 **Think About**: Questions that deepen understanding
- 📝 **Terminology**: Domain-specific term definitions
- ⚠️ **Gotcha**: Common mistakes or misconceptions
- ⏭️ **Navigation**: Cross-references to related sections

**Example**:
```markdown
> 💡 **Key Point**: Why sparse index instead of B+ tree?
> - Sparse index stores only first row of each granule
> - Memory footprint is tiny: 100M rows need only ~12K index entries
> - No tree maintenance on INSERT, faster writes
```

### 11. Section Organization (Summary-Detail Pattern)
- Start each major section with a brief summary
- Follow with an overview diagram (ASCII art)
- Then dive into detailed subsections
- Use data flow order, not code structure order
- Add transition sentences between sections

**Structure Pattern**:
```markdown
## N. Topic Name
Brief summary: what this section covers and why it matters.

### N.1 Overview
[ASCII diagram showing the big picture]
[1-2 sentences explaining the diagram]

### N.2 First Subtopic
[Details with code examples]
[Key point callout]

### N.3 Second Subtopic
[Details with code examples]
[Transition to next section]
```

### 12. Thorough Code Exploration
- Don't write from memory; always explore source code first
- Look for implementation variants (e.g., Wide vs Compact formats)
- Check for configurable behaviors and their settings
- Identify the "why" behind design choices by reading comments and commit history

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
| One-sided comparison | Analyze both approaches before comparing; use comparison tables |
| Exaggerated claims | Use concrete numbers with context |
| Code without context | Explain the code's role in the system |
| Too much detail in Chapter 1 | Chapter 1 is navigation only |
| Examples use unexplained concepts | Use well-known examples (FilterTransform, not LazilyMaterializingTransform) |
| Prerequisites too long | State relationship to main topic at each section's start |
| Inaccurate terminology | Explore source code; cite authoritative sources |
| Missing concrete examples | Add 1-2 examples per major section showing real data flow |
| Jumping between concepts | Use summary-detail pattern; add transition sentences |
| Missing important details | Explore code thoroughly before writing; check for variants |
| Code without thinking prompts | Add Key Point, Think About, and Terminology callouts |
| Flat section structure | Use hierarchical organization: overview → details → summary |
| Writing for experts only | Define terms; explain "why" not just "what" |
| Relying on memory | Always verify against source code; cite file:line |
| **Fabricated performance data** | **NEVER invent specific numbers (compression ratios, speeds) without actual tests or citations** |
| **Undefined concepts used** | **Add concept introduction section (§X.Y.1) before implementation details; use ⏭️ navigation hints** |
| **Missing big picture** | **Add unified visual comparison before diving into multiple related approaches** |
| **Abstract concepts without examples** | **Use concrete data examples (e.g., inverted index with actual words and row numbers)** |
| **Scattered concept definitions** | **Consolidate repeated concepts into ONE authoritative section; reference it elsewhere** |

## Concept Consolidation (DRY Principle)

When the same concept (e.g., Part, Granule, Mark) appears in multiple sections:

### Problem
- Concept defined in §2.1, re-explained in §3.2, mentioned again in §4.3, §5.3...
- Reader sees redundant explanations; maintenance becomes error-prone
- Updates require changing multiple places

### Solution
1. **Create ONE authoritative section** for each core concept
2. **Other sections reference it**: "See §3.1 for Part structure details"
3. **Only add context-specific details** in other sections

**Example Structure**:
```markdown
## 3. Storage Structure (Authoritative Section)
### 3.1 Part: The Storage Unit
[Complete definition, all details, visualizations]

### 3.2 Mark & Granule: The Index Unit
[Complete definition, all details, visualizations]

## 4. Write Flow
### 4.1 How Parts Are Created
> For Part structure details, see §3.1

[Only write-specific details here, no re-definition]
```

### When to Reorganize
- Same concept explained in 3+ sections → consolidate
- Readers need to jump around to understand one concept → consolidate
- Updating one concept requires editing multiple sections → consolidate

## Data Integrity Rules

### NEVER Fabricate Data
- **Bad**: "Compression ratio is 16:1" (without actual test)
- **Bad**: "Query speed improved by 38%" (without benchmark)
- **Good**: "LZ4 provides fast compression/decompression" (qualitative)
- **Good**: "Based on [source], compression ratio is X:Y" (with citation)

### What You CAN Do
- Explain algorithm principles without specific numbers
- Show usage examples (SQL syntax, configuration)
- Describe qualitative characteristics (faster, smaller, more efficient)
- Use conceptual examples to illustrate data flow

### What Requires Citation
- Specific compression ratios
- Performance benchmarks (speed, throughput)
- Memory usage numbers
- Any quantitative comparison

## Large Document Operations

When working with large documents (>500 lines):

### Problem
- Direct editing risks breaking existing content
- Multiple edits can cause inconsistencies
- Hard to verify completeness after major restructuring

### Solution: Draft-First Approach
1. **Create a draft file first**: `[topic]-DRAFT.md` or `[topic]-reorganized-DRAFT.md`
2. **Build the new structure** in the draft file
3. **Review with user** before replacing original
4. **Only then** merge into the original document

**Example Workflow**:
```
1. Read original document, identify sections to reorganize
2. Create: ai_docs/mergetree-section3-DRAFT.md
3. Write complete new section with all visualizations
4. User reviews and approves
5. Replace corresponding section in original document
6. Delete draft file
```

### Benefits
- Safe experimentation without breaking original
- Easy to compare old vs new structure
- User can review before committing changes
- Rollback is trivial (just delete draft)

## Verification Checklist

- [ ] Sections flow naturally; transitions are smooth
- [ ] Comparisons analyze both sides fairly; use comparison tables where appropriate
- [ ] Code examples include file paths and line numbers
- [ ] Diagrams have explanatory text
- [ ] No marketing language; claims backed by data
- [ ] Code version/tag specified
- [ ] Terminology verified against source code
- [ ] Each major section has at least one concrete example
- [ ] Sections follow summary-detail pattern with overview diagrams
- [ ] Key points are highlighted with appropriate callout boxes
- [ ] Transitions between sections are smooth and logical
- [ ] No important implementation variants are missing (e.g., Wide/Compact)
- [ ] All terminology is defined when first introduced
- [ ] Code exploration was thorough; no writing from memory
- [ ] **No fabricated performance data** (all numbers have citations or are from actual tests)
- [ ] **Core concepts defined in ONE place only** (no scattered definitions)
- [ ] **Large restructuring done via draft file first** (not direct editing)
- [ ] **Concepts introduced before use** (add §X.Y.1 concept sections; use ⏭️ navigation hints)
- [ ] **Big picture provided first** (unified visual comparison before multiple related approaches)
- [ ] **Abstract concepts have concrete examples** (e.g., inverted index with actual data)

## Output

- Location: `docs/`, `ai_docs/`, or project-specific folder
- Filename: `[topic-name].md`
- Language: Match user's preference
