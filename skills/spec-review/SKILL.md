---
name: spec-review
description: Validate, critique, and iterate on generated specifications. Use for "review this spec", "critique the FRD/FRS", "is this spec ready to build?", or folding user feedback into a spec produced by spec-plan before execution begins.
---

# Spec Review: Critique & Iterate

Validate generated specifications, provide critical analysis, and collect user feedback.

## Purpose

This skill provides the **human feedback loop** for feature specifications:
1. Validate spec completeness (automated)
2. Critique quality (automated)
3. Present findings to user
4. Iterate based on feedback

## Workflow

### Phase 1: Validate Structure

Run automated validation to catch errors early:

```bash
Bash: python skills/spec/scripts/validate_spec.py /path/to/job-queue/feature-{name}
```

**Checks performed:**
- ✅ All required files exist (FRD, FRS, GS, TR, task-list)
- ✅ Files not empty (> 100 bytes)
- ✅ Gherkin syntax valid
- ✅ Task list has actionable items
- ✅ .gitignore includes /job-queue
- ✅ Cross-references consistent

**Output:** JSON with errors, warnings, completeness score

### Phase 2: Critique Quality

Run automated critique for quality analysis:

```bash
Bash: python skills/spec/scripts/critique_plan.py /path/to/job-queue/feature-{name}
```

**Analysis performed:**
- **Requirement Quality:**
  - Are requirements specific or vague?
  - Are acceptance criteria measurable?
  - Are edge cases covered?

- **Task Breakdown:**
  - Are tasks atomic and actionable?
  - Is sequencing logical?
  - Are dependencies identified?

- **Technical Design:**
  - Are APIs well-defined?
  - Are data models complete?
  - Are error scenarios handled?
  - Are security concerns addressed?

- **Testability:**
  - Can Gherkin scenarios be automated?
  - Are test data requirements clear?

**Output:** JSON with critique score, critical issues, warnings, recommendations

### Phase 3: Present Findings

Summarize validation and critique results for user:

#### If Validation FAILED (errors found):

```
⚠️ Spec Validation Failed

Critical Errors:
- [List errors from validation tool]

Warnings:
- [List warnings]

Completeness Score: [X%]

Action Required:
These issues must be fixed before proceeding. Would you like me to:
1. Fix these issues automatically
2. Re-run spec-writer agent with corrections
3. Guide you to fix them manually
```

#### If Validation PASSED but Critique Found Issues:

```
✅ Spec Structure Valid

Quality Analysis (Score: [X%]):

Critical Issues:
- [File] - [Issue] → Suggestion: [fix]

Warnings:
- [File] - [Issue] → Suggestion: [improvement]

Recommendations:
- [List recommendations]

---

The specs are structurally valid but have quality concerns.
Would you like me to iterate on these issues?
```

#### If Everything PASSED:

```
✅ Spec Validation Passed
✅ Quality Critique Passed (Score: [X%])

Generated Specifications:
📁 /job-queue/feature-{name}/docs/
  ├── FRD.md - Business requirements ✅
  ├── FRS.md - Functional specs ✅
  ├── GS.md - Gherkin scenarios ✅
  ├── TR.md - Technical requirements ✅
  └── task-list.md - Development tasks ✅

Completeness: [X%]
Quality Score: [X%]

Minor Recommendations:
- [Optional improvements]

Ready to proceed with development?
```

### Phase 4: Collect User Feedback

Ask the user for their assessment:

**Questions:**
1. Are these specifications acceptable?
2. Any changes or clarifications needed?
3. Should I iterate on any specific areas?

**User Options:**

**A) Approve Specs**
→ Mark as complete, ready for development

**B) Request Changes**
→ Collect specific feedback, re-run spec-writer agent with updates

**C) Manual Edits**
→ User will edit files directly, re-run validation after

**D) Focus on Specific Area**
→ Re-run critique with `--focus` on specific concerns

### Phase 5: Iterate if Needed

If user requests changes:

1. **Collect specific feedback:**
   - Which documents need changes?
   - What's missing or incorrect?
   - Any new requirements?

2. **Re-run spec-writer agent:**
   ```bash
   Task tool with subagent_type="spec-writer"

   Prompt: "Update feature specifications based on feedback:

   **Previous Specs:** /job-queue/feature-{name}/docs/

   **User Feedback:**
   [List specific changes requested]

   **Focus Areas:**
   [Which documents to update]

   Please update the specifications addressing this feedback."
   ```

3. **Re-run validation and critique:**
   - Validate structure again
   - Critique quality again
   - Present updated findings

4. **Repeat until approved**

## Tools Used

### Python Scripts

1. **validate_spec.py** - Structural validation
   - File existence and completeness
   - Gherkin syntax
   - Cross-references

2. **critique_plan.py** - Quality critique
   - Requirement clarity
   - Task quality
   - Technical completeness
   - Testability

## Decision Tree

```
Start → Run Validation
  ├─ Errors? → Present errors → User fixes → Re-validate
  └─ Valid → Run Critique
      ├─ Critical Issues? → Present issues → User decides
      │   ├─ Iterate → Re-run agent → Re-validate
      │   └─ Accept → Done
      └─ No Critical Issues → Present summary → User approves → Done
```

## Expected Outcomes

After this skill completes:

1. ✅ Specs validated for structure
2. ✅ Specs critiqued for quality
3. ✅ Findings presented to user
4. ✅ User feedback collected
5. ✅ Specs iterated if needed
6. ✅ Final specs approved by user

## Next Steps

Once specs are approved:

1. **Update Memory Bank:**
   ```bash
   /memorybank sync
   ```

2. **Begin Development:**
   - Follow task-list.md
   - Reference TR.md for technical details
   - Use GS.md for test scenarios

## Important Notes

- **Human-in-loop:** User approval required before proceeding
- **Automated validation:** No manual checklists
- **Critical analysis:** Quality gate before development
- **Iteration support:** Easy to refine based on feedback

---

**Estimated time:** 2-5 minutes for validation + user review
**Token usage:** ~600 tokens (focused on validation and feedback)
