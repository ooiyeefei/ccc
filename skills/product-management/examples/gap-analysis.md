# Gap Analysis - 2025-12-26

**Example output from `/pm gaps` command**

---

## Summary

- **Product data from:** 2025-12-20 (6 days old) ✅
- **Competitor data from:** 2025-12-15 (11 days old) ✅
- **Total gaps identified:** 8
- **Recommended to FILE:** 3 (score ≥40)
- **Recommended to WAIT:** 3 (score 25-39)
- **Recommended to SKIP:** 2 (score <25)

---

## Gaps (Sorted by WINNING Score)

### 1. Dark Mode Support

**WINNING Score: 47/60** → Recommended: **FILE**

| Criterion | Score | Notes |
|-----------|-------|-------|
| Pain Intensity | 9/10 | 47 G2 reviews mention eye strain/dark mode |
| Market Timing | 8/10 | All major competitors have shipped this |
| Execution Capability | 9/10 | CSS variables ready, 3-5 day effort |
| Strategic Fit | 8/10 | Developer audience expects this |
| Revenue Potential | 6/10 | Won't drive upgrades, but reduces churn |
| Competitive Moat | 7/10 | Our theme system allows custom themes |

**Competitor Evidence:**
- **Notion:** Full dark mode with system auto-detect. Users love it.
- **Linear:** Dark-first design. "Finally an app that doesn't blind me" - Reddit
- **Slack:** Per-workspace setting. Some user confusion.

**User Evidence:**
- "Please add dark mode, I code at night" - Support ticket #2341
- "The bright UI gives me headaches" - G2 review

**Decision:** [x] FILE  [ ] WAIT  [ ] SKIP

---

### 2. API Webhooks

**WINNING Score: 44/60** → Recommended: **FILE**

| Criterion | Score | Notes |
|-----------|-------|-------|
| Pain Intensity | 8/10 | 23 support tickets requesting webhooks |
| Market Timing | 7/10 | Searches up 40% YoY, competitors launching |
| Execution Capability | 7/10 | Event system exists, 3-4 week effort |
| Strategic Fit | 9/10 | Core to "developer-first" positioning |
| Revenue Potential | 8/10 | Enterprise deal-closer |
| Competitive Moat | 5/10 | Table stakes, everyone will have it |

**Competitor Evidence:**
- **Notion:** Comprehensive webhook system with retry logic
- **Linear:** Webhooks launched Q3, heavily adopted
- **Zapier:** Generic integration, but users want native

**User Evidence:**
- "We can't integrate without webhooks" - Enterprise prospect call
- "Polling is killing our server" - Support ticket #1892

**Decision:** [x] FILE  [ ] WAIT  [ ] SKIP

---

### 3. Team Sharing & Permissions

**WINNING Score: 41/60** → Recommended: **FILE**

| Criterion | Score | Notes |
|-----------|-------|-------|
| Pain Intensity | 7/10 | Teams sharing via screen share (!!) |
| Market Timing | 7/10 | Standard for B2B SaaS |
| Execution Capability | 6/10 | Requires auth refactor, 6-8 weeks |
| Strategic Fit | 8/10 | Enterprise expansion requires this |
| Revenue Potential | 9/10 | Enables team plan pricing tier |
| Competitive Moat | 4/10 | Commodity feature |

**Competitor Evidence:**
- **All competitors:** Have team features
- **Differentiation opportunity:** Real-time collaboration (like Figma)

**User Evidence:**
- "When can we add team members?" - Asked in 5 sales calls

**Decision:** [x] FILE  [ ] WAIT  [ ] SKIP

---

### 4. Export to PDF

**WINNING Score: 38/60** → Recommended: **WAIT**

| Criterion | Score | Notes |
|-----------|-------|-------|
| Pain Intensity | 6/10 | Some users print/share reports |
| Market Timing | 5/10 | Stable demand, not trending |
| Execution Capability | 8/10 | Libraries available, 1-2 weeks |
| Strategic Fit | 6/10 | Useful but not core |
| Revenue Potential | 5/10 | Won't drive decisions |
| Competitive Moat | 3/10 | Every tool has this |

**Competitor Evidence:**
- **Most competitors:** Basic PDF export
- **No differentiation** in this space

**Decision:** [ ] FILE  [x] WAIT  [ ] SKIP
**Notes:** Revisit if enterprise requests increase

---

### 5. Mobile App

**WINNING Score: 36/60** → Recommended: **WAIT**

| Criterion | Score | Notes |
|-----------|-------|-------|
| Pain Intensity | 7/10 | Users want to check on mobile |
| Market Timing | 6/10 | Mobile-first declining for B2B tools |
| Execution Capability | 4/10 | Would need React Native, 3+ months |
| Strategic Fit | 6/10 | Desktop-first product |
| Revenue Potential | 6/10 | Might help retention |
| Competitive Moat | 3/10 | Expensive to maintain |

**Competitor Evidence:**
- **Notion:** Good mobile app, but users primarily use desktop
- **Linear:** Minimal mobile, focus on desktop

**Decision:** [ ] FILE  [x] WAIT  [ ] SKIP
**Notes:** PWA might be lighter-weight alternative

---

### 6. AI Assistant

**WINNING Score: 32/60** → Recommended: **WAIT**

| Criterion | Score | Notes |
|-----------|-------|-------|
| Pain Intensity | 5/10 | Users curious, not demanding |
| Market Timing | 8/10 | AI everything is hot right now |
| Execution Capability | 5/10 | Would need LLM integration, unclear scope |
| Strategic Fit | 6/10 | Depends on use case |
| Revenue Potential | 5/10 | Could be premium feature |
| Competitive Moat | 3/10 | Everyone adding AI |

**Competitor Evidence:**
- **Notion AI:** Popular but mixed reviews on usefulness
- **Linear:** No AI features yet

**Decision:** [ ] FILE  [x] WAIT  [ ] SKIP
**Notes:** Need clearer use case. "AI" is too vague.

---

### 7. Offline Mode

**WINNING Score: 22/60** → Recommended: **SKIP**

| Criterion | Score | Notes |
|-----------|-------|-------|
| Pain Intensity | 3/10 | Rarely requested |
| Market Timing | 3/10 | Not trending, always-online assumed |
| Execution Capability | 3/10 | Major architecture change |
| Strategic Fit | 4/10 | Not core to value prop |
| Revenue Potential | 3/10 | Niche use case |
| Competitive Moat | 6/10 | Hard to do well |

**Competitor Evidence:**
- **Few competitors:** Have offline, those that do report low usage

**Decision:** [ ] FILE  [ ] WAIT  [x] SKIP

---

### 8. Blockchain Integration

**WINNING Score: 12/60** → Recommended: **SKIP**

| Criterion | Score | Notes |
|-----------|-------|-------|
| Pain Intensity | 1/10 | No users asking |
| Market Timing | 2/10 | Web3 hype declining |
| Execution Capability | 2/10 | Team has no blockchain experience |
| Strategic Fit | 2/10 | Doesn't fit product vision |
| Revenue Potential | 2/10 | Unclear monetization |
| Competitive Moat | 3/10 | If anyone can do it, not a moat |

**Decision:** [ ] FILE  [ ] WAIT  [x] SKIP
**Notes:** Not relevant to our market

---

## Decision Summary

| # | Gap | Score | Decision | Priority |
|---|-----|-------|----------|----------|
| 1 | Dark Mode Support | 47/60 | **FILE** | Now |
| 2 | API Webhooks | 44/60 | **FILE** | Now |
| 3 | Team Sharing | 41/60 | **FILE** | Next |
| 4 | Export to PDF | 38/60 | WAIT | - |
| 5 | Mobile App | 36/60 | WAIT | - |
| 6 | AI Assistant | 32/60 | WAIT | - |
| 7 | Offline Mode | 22/60 | SKIP | - |
| 8 | Blockchain | 12/60 | SKIP | - |

---

## Next Steps

1. Run `/pm review` to confirm/adjust decisions
2. Run `/pm file` to create GitHub Issues for FILE items (3 issues)
3. Run `/pm roadmap` to organize priorities

---

*Generated by PM Skill | Ready for `/pm file`*
