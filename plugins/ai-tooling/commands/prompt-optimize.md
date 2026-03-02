---
description: "Analyze, evaluate, and optimize prompts for LLMs — improve clarity, reduce token usage, add structure, and test variations"
argument-hint: "<prompt text or file path> [--model claude|gpt|gemini] [--optimize-for clarity|tokens|reliability] [--compare]"
---

# Prompt Optimization

## CRITICAL RULES

1. **Read the prompt first.** If `$ARGUMENTS` is a file path, read the file. If inline text, use it directly.
2. **Never modify the user's original prompt** until they approve the optimization.
3. **Show before/after.** Always present the original alongside the optimized version.
4. **Never enter plan mode.** Execute immediately.

## Step 1: Analyze the Current Prompt

Use the `prompt-engineer` agent to analyze the prompt:

```
Task:
  subagent_type: "prompt-engineer"
  description: "Analyze and score the current prompt"
  prompt: |
    Analyze this prompt for effectiveness with LLMs.

    ## Prompt to Analyze
    [Insert the prompt from $ARGUMENTS]

    ## Instructions
    Evaluate across these dimensions (score each 1-10):

    1. **Clarity**: Is the task unambiguous? Could the LLM misinterpret?
    2. **Specificity**: Are constraints, format, and scope clearly defined?
    3. **Structure**: Is information logically organized? Good use of sections/lists?
    4. **Token efficiency**: Any redundancy, filler, or verbose phrasing?
    5. **Robustness**: Will it work consistently, or is it fragile to phrasing?
    6. **Output control**: Does it specify the desired output format?

    For each dimension:
    - Current score (1-10)
    - Specific weakness found
    - Concrete improvement suggestion

    Also identify:
    - Missing context the LLM would need
    - Ambiguous instructions that could be interpreted multiple ways
    - Prompt injection vulnerabilities (if applicable)

    Present a scorecard and detailed analysis.
```

Present the analysis to the user:

```
## Prompt Analysis

| Dimension | Score | Key Issue |
|-----------|-------|-----------|
| Clarity | X/10 | [issue] |
| Specificity | X/10 | [issue] |
| Structure | X/10 | [issue] |
| Token Efficiency | X/10 | [issue] |
| Robustness | X/10 | [issue] |
| Output Control | X/10 | [issue] |
| **Overall** | **X/10** | |

Top 3 improvements:
1. [most impactful improvement]
2. [second improvement]
3. [third improvement]
```

## Step 2: Generate Optimized Version

```
Task:
  subagent_type: "prompt-engineer"
  description: "Generate optimized prompt"
  prompt: |
    Optimize this prompt based on the analysis.

    ## Original Prompt
    [Insert the original prompt]

    ## Analysis Findings
    [Insert findings from Step 1]

    ## Optimization Target
    [--optimize-for flag value, or "balanced" if not specified]

    ## Target Model
    [--model flag value, or "claude" if not specified]

    ## Instructions
    Rewrite the prompt to address all identified weaknesses:
    - Fix ambiguities
    - Add missing structure (sections, numbered lists, constraints)
    - Specify output format if missing
    - Remove redundancy and filler
    - Add examples if the task is complex
    - Add guard rails for edge cases

    If --optimize-for is:
    - "clarity": Prioritize unambiguous language, even if longer
    - "tokens": Minimize token count while preserving meaning
    - "reliability": Add constraints, examples, and output format for consistent results

    Present the optimized prompt as a complete, ready-to-use text.
```

## Step 3: Present Results

Show side-by-side comparison:

```
## Optimization Results

### Score Comparison
| Dimension | Before | After | Change |
|-----------|--------|-------|--------|
| Clarity | X/10 | Y/10 | +Z |
| ... | ... | ... | ... |
| **Overall** | **X/10** | **Y/10** | **+Z** |

### Token Count
- Original: [X] tokens (estimated)
- Optimized: [Y] tokens (estimated)
- Savings: [Z]% [if applicable]

### Optimized Prompt
[The complete optimized prompt in a code block]

### Key Changes Made
1. [change and rationale]
2. [change and rationale]
3. [change and rationale]
```

If `--compare` flag is set, generate 2-3 variations optimized for different goals (clarity vs tokens vs reliability) and present all for comparison.

## Quick Examples

- `/prompt-optimize "Summarize this document"` — Analyze and improve a simple prompt
- `/prompt-optimize prompts/system.md --optimize-for tokens` — Reduce token count of a system prompt
- `/prompt-optimize prompts/agent.md --model gpt --compare` — Optimize for GPT with variations
