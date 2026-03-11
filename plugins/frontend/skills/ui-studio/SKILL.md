---
name: ui-studio
description: Orchestrate full frontend development from a product goal to shipped UI. Establishes a shared product brief (goal, audience, aesthetic tone) as the north star, then coordinates frontend-design, ui-layout-designer, ui-ux-designer, ui-polisher, and react-performance-optimizer toward a coherent result. Use when building a new UI, page, or feature from scratch.
---

# UI Studio

Orchestrating skill for new UI creation. Without a shared brief, each specialist optimizes for its own domain and produces incoherent results -- great layout, wrong tone; polished motion, wrong audience. This skill fixes that by anchoring every agent to the same product goal.

**Positioning:** Use `premium-web-consultant` first if you need strategy and planning before building. Use `/frontend-redesign` instead if improving an existing frontend codebase.

## Phase 0: Product Brief (always first)

Before any design or code, establish the shared context that all agents will receive. Elicit from the user or infer from context:

```
PRODUCT BRIEF
─────────────────────────────────────────
Goal:        [one sentence — what problem this UI solves]
Audience:    [who uses it, device preference, tech level]
Aesthetic:   [one tone + one archetype — e.g. "refined editorial", "brutalist raw", "playful toy-like"]
Stack:       [framework + CSS approach]
Perf budget: [Core Web Vitals targets or "none"]
A11y:        [WCAG AA / AAA / none]
Success:     [definition of done]
─────────────────────────────────────────
```

**This brief is the north star.** Pass it verbatim to every subsequent agent. If any agent produces output that contradicts the brief — wrong tone, wrong audience assumption — reject and redirect.

Do not proceed to Phase 1 until the brief is confirmed with the user.

---

## Phase 1: Design Direction

Skill: **frontend-design**

Pass the full product brief. The skill will:
- Commit to a bold aesthetic direction aligned with the tone from the brief
- Define typography, color palette, motion principles
- Produce a working reference component establishing the visual language

**Output:** a reference component + aesthetic definition (specific fonts, color tokens, motion tone).

This is the visual contract for all subsequent phases. Every later agent must respect it.

---

## Phase 2: Layout & Structure

Agent: **ui-layout-designer**

Pass:
- The product brief
- The aesthetic definition from Phase 1 (font scale, spatial rhythm, color tokens)

The agent will:
- Choose the layout pattern that fits the content model and audience (bento, holy grail, editorial, etc.)
- Define the spacing system and breakpoint strategy
- Produce a CSS Grid/Flexbox scaffold with named areas and responsive pivots

**Constraint:** Layout decisions must serve the audience's mental model, not just be visually interesting. When in doubt, reference the brief's goal.

---

## Phase 3: UX Patterns

Agent: **ui-ux-designer**

Pass:
- The product brief
- Layout structure from Phase 2

The agent will:
- Design interaction patterns aligned with the user goal
- Ensure all three states (loading, empty, error) are handled everywhere needed
- Validate information hierarchy — the primary action must dominate
- Flag accessibility requirements for the specified WCAG level

**Constraint:** No pattern added for completeness. Every UX decision must serve the stated goal and audience from the brief.

---

## Phase 4: Implementation

Build the actual code integrating the outputs from Phases 1–3:

- CSS custom properties from the Phase 1 aesthetic definition
- Grid scaffold from the Phase 2 layout spec
- UX patterns and interaction states from Phase 3
- Use the **css-master** skill for container queries, scroll-driven animations, View Transitions, and other modern features where appropriate

The code at this phase should feel visually coherent and structurally sound, but not yet fully polished.

---

## Phase 5: Polish

Agent: **ui-polisher**

Pass:
- The product brief — especially the aesthetic tone
- The implemented code from Phase 4

The agent will:
- Add micro-interactions that match the aesthetic tone from the brief
- Layer in page load animations and scroll reveals appropriate to the audience
- Polish hover/focus/active states for all interactive elements
- Ensure `prefers-reduced-motion` is respected

**Constraint:** Polish must amplify the aesthetic tone — not override it. "Refined editorial" means restrained, purposeful motion. "Maximalist chaos" means orchestrated, expressive motion. The brief decides.

---

## Phase 6: Performance (React projects only)

Agent: **react-performance-optimizer**

Pass:
- The product brief (performance budget)
- The implemented code

The agent will flag re-render issues, selector problems, bundle impact, and code splitting opportunities measured against the performance budget in the brief.

Skip this phase for static HTML/CSS or non-React projects.

---

## Phase 7: Final Review

Run the **review-design** command on the final output to validate:
- Visual consistency against the established aesthetic
- Layout system coherence
- CSS architecture quality
- Accessibility compliance at the WCAG level from the brief

---

## Handoff Format

When moving from one phase to the next, always pass:

```
HANDOFF
───────────────────────────────
Brief:    [paste the original product brief, unchanged]
Context:  [summary of the previous phase's key decisions]
Ask:      [the specific question or task for the next agent]
───────────────────────────────
```

This prevents each specialist from solving the wrong problem.

---

## When to Collapse Phases

**Small component:** Phases 1–3 can be merged into a single design decision. Skip Phase 6 if not React.

**Full product UI:** Run all 7 phases. Write key outputs to files (e.g., `brief.md`, `aesthetic.md`, `layout-spec.md`) to preserve context across phases.

**Existing codebase:** Use the `frontend-redesign` workflow command instead — it handles auditing and incremental improvement of existing frontends.
