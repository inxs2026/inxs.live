# Skills Development Guide

**Purpose:** Guidelines for creating and maintaining high-quality AgentSkills

---

## Required Components

Every SKILL.md must have:

### 1. Front Matter
```yaml
---
name: skill-name
description: One-line summary. Use when [specific use case].
metadata: {"clawdbot":{"emoji":"🔤","requires":{}}}
---
```

### 2. Use When / Don't Use When Section ⚠️ **CRITICAL**

```markdown
## ✅ Use When

- **Specific scenario 1:** Brief explanation
- **Specific scenario 2:** Brief explanation
- **Specific scenario 3:** Brief explanation

## ❌ Don't Use When

- **Wrong scenario 1:** Why not + what to use instead
- **Wrong scenario 2:** Why not + what to use instead
- **Wrong scenario 3:** Why not + what to use instead

**Rule of thumb:** One-sentence decision criteria
```

**Why this matters:** Prevents wrong skill selection ~20% of the time. Be specific, not generic.

### 3. Examples and Patterns

Show, don't just tell:
- Code examples with comments
- Command-line usage
- Real-world scenarios
- Edge cases and gotchas

### 4. Language-Specific Sections (if applicable)

Organize by language/tool:
- JavaScript
- Python
- Go
- Bash/CLI
- etc.

---

## Skill Categories

### Data/API Skills
- External integrations
- API wrappers
- Data fetchers

**Example:** weather, trackdata.live, email checking

### Tool/Utility Skills
- Development tools
- Text processing
- File manipulation

**Example:** regex-patterns, coding-agent, healthcheck

### Analysis Skills
- Data analysis
- Report generation
- Monitoring

**Example:** racing analytics, performance tracking

---

## Anti-Patterns to Avoid

### ❌ Vague "Use When" Sections
**Bad:**
```markdown
## Use When
- You need to work with text
- You want to process data
```

**Good:**
```markdown
## ✅ Use When
- **Validating email addresses:** Quick format check before sending
- **Extracting phone numbers:** Pull all phone numbers from customer data
- **Cleaning log files:** Remove ANSI codes, timestamps, or debug lines
```

### ❌ Missing "Don't Use When"
Always include this! It's as important as "Use When."

### ❌ No Examples
Show working code. Don't just describe the concept.

### ❌ Too Much or Too Little
- **Too much:** 5000-line reference manual (link to external docs instead)
- **Too little:** "Use this for regex" with no patterns

**Sweet spot:** 200-1000 lines with practical examples

---

## Skill Testing Checklist

Before marking a skill complete:

- [ ] Front matter has accurate description
- [ ] "Use When" section has 3+ specific scenarios
- [ ] "Don't Use When" section exists with alternatives
- [ ] At least 3 working code examples
- [ ] Covers edge cases and common mistakes
- [ ] Tested in actual use (not just theory)
- [ ] README.md exists if there are scripts/tools

---

## When to Create a New Skill vs. Update Existing

**Create new skill when:**
- Completely different domain/tool
- Would make existing skill too large (>1500 lines)
- Needs different dependencies/requirements

**Update existing skill when:**
- Related patterns or use cases
- Same tool/domain, different scenarios
- Adding language-specific variants

---

## Skill Maintenance

### Regular Review
- Update examples when language/tool versions change
- Add new patterns as you discover them
- Remove obsolete/deprecated approaches

### Document in lessons.md
When you learn something new while using a skill:
1. Update the skill's SKILL.md with the new pattern
2. Add entry to `memory/lessons.md` noting what you learned
3. Update "Common Mistakes" section if applicable

---

## Example: Good Skill Structure

```markdown
---
name: example-skill
description: Does X when you need Y. Use when validating Z, parsing A, or extracting B.
---

# Skill Name

One-paragraph overview.

## ✅ Use When
- Specific scenario 1
- Specific scenario 2
- Specific scenario 3

## ❌ Don't Use When
- Wrong scenario + alternative
- Wrong scenario + alternative

## Quick Reference
[Table or list of most common patterns]

## Language-Specific Usage

### JavaScript
[Examples]

### Python
[Examples]

## Common Patterns
[Cookbook-style solutions]

## Gotchas and Edge Cases
[Things that trip people up]

## Tips
[Best practices, performance notes]
```

---

**Remember:** Skills are architecture, not prompts. Structure creates clarity, clarity creates correct usage.
