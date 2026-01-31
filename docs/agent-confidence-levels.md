# Agent Confidence Levels - Usage Guide

## Overview

All specialized agents in the Claude Skills Framework use a three-level confidence system (🟢🟡🔴) to communicate their level of certainty before proceeding with a task. This system ensures agents request clarification when needed, rather than proceeding with insufficient information.

## The Three-Level System

### 🟢 Green - High Confidence
**Meaning:** Safe to proceed with confidence

**Characteristics:**
- All required information is available
- Context is fully understood
- Low risk of errors or breaking changes
- Clear path forward with defined steps
- Tests exist or verification method is clear

**Agent Actions:**
- Proceed with the task
- Execute work with standard quality checks
- Document work as usual

**Examples:**
- **Refactoring:** Code is well-tested, dependencies mapped, clear refactoring path
- **Debugging:** Bug reliably reproducible, clear error logs, familiar code area
- **Backend Development:** API contract defined, database schema known, error handling clear
- **Frontend:** UI requirements specified, design mockups provided, component structure understood

---

### 🟡 Yellow - Medium Confidence
**Meaning:** Proceed with caution and documented assumptions

**Characteristics:**
- Some unknowns exist but are manageable
- Can make reasonable assumptions to proceed
- Minor risks identified but can be mitigated
- Partial information available
- Verification possible but may be incomplete

**Agent Actions:**
- Proceed with caution
- State all assumptions explicitly before acting
- Add extra validation and error handling
- Document uncertainties clearly
- Prepare rollback plan if applicable

**Examples:**
- **Refactoring:** Some dependencies unclear but can work around them
- **Debugging:** Can reproduce intermittently, have partial logs, need to form hypotheses
- **Backend Development:** API contract mostly defined, some edge cases unclear
- **Frontend:** General UI direction provided, need to infer specific interactions

**Required Documentation:**
```markdown
**Assumptions Made:**
1. [Explicit assumption #1]
2. [Explicit assumption #2]

**Risks Identified:**
- [Risk and mitigation]

**Rollback Plan:**
- [How to undo if wrong]
```

---

### 🔴 Red - Low Confidence
**Meaning:** STOP and request clarification

**Characteristics:**
- Significant ambiguity in requirements or code
- High risk of breaking changes
- Missing critical information
- Multiple conflicting interpretations possible
- Cannot verify correctness of work

**Agent Actions:**
- **STOP** - Do not proceed
- Request clarification from user
- Ask specific questions about unknowns
- Escalate to user for decision
- Wait for additional information

**Examples:**
- **Refactoring:** Code behavior unclear, no tests, high blast radius
- **Debugging:** Cannot reproduce, no logs, multiple conflicting theories
- **Backend Development:** API requirements contradictory, unclear authentication flow
- **Frontend:** No design provided, conflicting user stories, unclear business logic

**Escalation Template:**
```markdown
🔴 **Low Confidence - Need Clarification**

**What I'm uncertain about:**
1. [Specific uncertainty #1]
2. [Specific uncertainty #2]

**What I need to proceed:**
- [ ] [Specific information needed]
- [ ] [Specific decision needed]

**Why this matters:**
[Explain impact of proceeding without clarity]

**Questions:**
1. [Specific question #1]
2. [Specific question #2]
```

---

## Decision Tree: Choosing the Right Confidence Level

```
START
  ↓
Do you have ALL required information?
  ├─ YES → Do you fully understand the context?
  │         ├─ YES → Is the risk low?
  │         │         ├─ YES → 🟢 High Confidence
  │         │         └─ NO  → 🟡 Medium Confidence
  │         └─ NO  → Can you make reasonable assumptions?
  │                   ├─ YES → 🟡 Medium Confidence
  │                   └─ NO  → 🔴 Low Confidence
  └─ NO → Is the missing information critical?
            ├─ YES → 🔴 Low Confidence
            └─ NO  → Can you proceed with stated assumptions?
                      ├─ YES → 🟡 Medium Confidence
                      └─ NO  → 🔴 Low Confidence
```

## By Agent Type

### Refactoring Specialist 🟢🟡🔴

| Confidence | When to Use |
|-----------|-------------|
| 🟢 | Code well-understood, tests exist, dependencies mapped, clear path |
| 🟡 | Some unknowns in dependencies, partial tests, manageable risk |
| 🔴 | No tests, unclear behavior, high blast radius, conflicting patterns |

**Critical Rule:** Never refactor critical production code at 🔴 confidence.

### Debugger Specialist 🟢🟡🔴

| Confidence | When to Use |
|-----------|-------------|
| 🟢 | Bug reproducible, clear logs, familiar code, test environment ready |
| 🟡 | Intermittent reproduction, partial logs, reasonable hypotheses |
| 🔴 | Cannot reproduce, no logs, multiple theories, high-stakes issue |

**Critical Rule:** If debugging production issue at 🔴 confidence, escalate immediately.

### Backend Developer 🟢🟡🔴

| Confidence | When to Use |
|-----------|-------------|
| 🟢 | API contract defined, database schema clear, auth flow documented |
| 🟡 | Most requirements clear, some edge cases undefined, can infer safely |
| 🔴 | Contradictory requirements, unclear data model, authentication ambiguous |

**Critical Rule:** Never implement authentication/authorization at 🔴 confidence.

### Frontend Developer 🟢🟡🔴

| Confidence | When to Use |
|-----------|-------------|
| 🟢 | Design mockups provided, user flows clear, API contracts defined |
| 🟡 | General UI direction provided, need to infer some interactions |
| 🔴 | No design, conflicting user stories, unclear business logic |

**Critical Rule:** Never implement critical user flows at 🔴 confidence.

## Best Practices

### For Agent Developers

1. **Always assess confidence explicitly** in `<thinking>` tags before proceeding
2. **Document confidence level** at the start of your response
3. **If 🟡, state assumptions explicitly** before proceeding
4. **If 🔴, use the escalation template** to request clarification
5. **Reassess confidence** if new information emerges during work

### For Users

1. **Provide complete information upfront** when possible to enable 🟢 confidence
2. **Respond promptly to 🔴 escalations** - agents are blocked waiting for you
3. **Accept 🟡 assumptions** if they're reasonable, or provide corrections
4. **Trust agent judgment** - if they're at 🔴, there's usually a good reason

### For Framework Maintainers

1. **All agents MUST implement** the confidence level system
2. **Enforce 🔴 stops** - agents must not proceed without user input
3. **Review escalations** for common patterns that indicate missing documentation
4. **Update templates** as new confidence scenarios emerge

## Common Mistakes to Avoid

### ❌ Proceeding at 🔴 Confidence
**Wrong:**
```
🔴 I'm not sure what this code does, but I'll refactor it anyway...
```

**Right:**
```
🔴 Low Confidence - Need Clarification

I don't fully understand what this code does. Before refactoring:
1. Can you explain the business logic in lines 45-67?
2. Are there any hidden dependencies I should know about?
```

### ❌ Not Stating Assumptions at 🟡
**Wrong:**
```
🟡 Medium Confidence - Proceeding with refactoring...
```

**Right:**
```
🟡 Medium Confidence - Proceeding with these assumptions:

Assumptions:
1. The validateUser() function checks authentication (no authorization needed)
2. Error responses follow standard REST format
3. Database rollback is handled by transaction middleware

If any assumptions are wrong, please let me know.
```

### ❌ Overconfidence (🟢 when should be 🟡 or 🔴)
**Wrong:**
```
🟢 High Confidence - I'll add this authentication check...
[Proceeds to add broken auth logic]
```

**Right:**
```
🟡 Medium Confidence - Adding authentication check

Assumption: Using bcrypt for password hashing (not seeing explicit requirement)
Assumption: Session timeout is 24 hours (standard default)

Please confirm these are correct.
```

## Integration with Other Systems

### Memory Bank
Agents should read Memory Bank files to increase confidence:
- `systemArchitecture.md` → Understand patterns (🔴 → 🟡)
- `techContext.md` → Know constraints (🔴 → 🟡)
- `activeContext.md` → Avoid conflicts (🟡 → 🟢)

### Documentation Hub
Reading Documentation Hub increases confidence:
- `systemArchitecture.md` → Clear structure (🟡 → 🟢)
- `keyPairResponsibility.md` → Know module boundaries (🟡 → 🟢)
- `glossary.md` → Understand domain terms (🔴 → 🟡)

### Quality Gates
Confidence levels inform quality checks:
- **🟢**: Standard quality gates (lint, build, test)
- **🟡**: Extra validation, additional test coverage
- **🔴**: Should not reach quality gates (blocked at planning)

## Metrics and Improvement

Track confidence levels over time to improve:

### What to Measure
- **🔴 frequency by agent type** → Identify documentation gaps
- **🟡 → 🟢 conversion after clarification** → Measure communication effectiveness
- **🔴 escalations that repeat** → Systematic issues to address

### What Good Looks Like
- **🟢**: 60-70% of tasks (most work is well-defined)
- **🟡**: 25-35% of tasks (some unknowns are normal)
- **🔴**: 5-10% of tasks (rare escalations for truly unclear work)

### Red Flags
- **🟢 > 90%** → Agents may be overconfident, missing risks
- **🔴 > 20%** → Documentation gaps, requirements unclear
- **Same 🔴 escalation repeating** → Need to document pattern

## Summary

The confidence level system is a **communication tool**, not a blocker. It enables:

1. ✅ Agents to request clarification when needed
2. ✅ Users to understand agent certainty level
3. ✅ Teams to identify documentation gaps
4. ✅ Quality to improve over time

**Remember:** It's always better to ask (🔴) than to guess wrong. The cost of rework is always higher than the cost of clarification.

---

**Related Documentation:**
- [refactoring-specialist.md](/home/artsmc/.claude/agents/refactoring-specialist.md) - See confidence levels in context
- [debugger-specialist.md](/home/artsmc/.claude/agents/debugger-specialist.md) - Debugging-specific confidence guidance
- [Memory Bank](/home/artsmc/.claude/memory-bank/) - Increase confidence by reading context
- [Documentation Hub](/home/artsmc/.claude/cline-docs/) - Architecture and patterns
