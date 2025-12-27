---
description: Scan codebase and interview for product inventory
allowed-tools: Read, Glob, Grep, Write, AskUserQuestion
---

# Product Analysis

Perform comprehensive product analysis to understand current state.

## Process

1. **Scan Codebase Structure**
   - Use Glob to find routes/pages (user-facing features)
   - Identify components (UI capabilities)
   - Find API endpoints (backend functionality)
   - Locate database models (data entities)

2. **Interview User** for business context using AskUserQuestion:
   - "What's your core value proposition?"
   - "Who are your target users?"
   - "What's your pricing model?"
   - "What do users love most? Complain about most?"

3. **Generate Product Inventory**
   - List all features with metadata
   - Identify technical moats (hard to replicate)
   - Flag technical debt areas
   - Note architectural constraints

4. **Save Results**
   - Create `.pm/` directory if not exists
   - Save to `.pm/product/inventory.md`
   - Save to `.pm/product/architecture.md`
   - Update `.pm/cache/last-updated.json`

## Output Format

```markdown
# Product Inventory - [Date]

## Core Value Proposition
[User-provided]

## Features
| Feature | Type | Technical Moat | Debt Level |
|---------|------|----------------|------------|

## Architecture Constraints
- [Constraint 1]
```

Reference the product-management skill for detailed guidance.
