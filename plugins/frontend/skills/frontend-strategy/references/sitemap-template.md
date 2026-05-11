# Sitemap + User Flows

## Page Inventory

| Page | Purpose | Primary CTA | Depth |
|------|---------|-------------|-------|
| Homepage | [purpose] | [CTA] | 0 |
| About | [purpose] | [CTA] | 1 |
| [Page] | [purpose] | [CTA] | [level] |

**Cognitive Load check:** No page exceeds depth 3. Every page has exactly one primary CTA.

---

## Page Hierarchy

```
Homepage
  +-- About
  |     +-- Team
  |     +-- Story
  +-- Services
  |     +-- [Service 1]
  |     +-- [Service 2]
  +-- Portfolio / Case Studies
  |     +-- [Project 1]
  |     +-- [Project 2]
  +-- Blog
  |     +-- [Category]
  |           +-- [Post]
  +-- Contact
```

---

## Navigation Structure

### Primary Navigation (max 7 items)

| Position | Label | Links to | Dropdown |
|----------|-------|----------|----------|
| 1 | [Label] | [Page] | [yes/no - items if yes] |
| 2 | [Label] | [Page] | [yes/no] |
| ... | ... | ... | ... |

### Footer Navigation

| Column | Links |
|--------|-------|
| [Column label] | [list of links] |
| [Column label] | [list of links] |

### Utility Navigation (top bar or secondary)

[Logo | Search | Language | Login | CTA button]

---

## User Flows

### Flow: [Primary conversion journey]

```
[Entry point] --> [Page A] --> [Page B] --> [Conversion action]
                      |
                      +--> [Alternative path] --> [Recovery] --> [Conversion action]
```

**Friction points:** [identified risks at each step]
**Drop-off mitigation:** [strategy for each friction point]

### Flow: [Secondary journey]

```
[Entry point] --> [Page X] --> [Page Y] --> [Desired outcome]
```

---

## Conversion Funnels

### Funnel: [Primary goal]

| Stage | Page/Action | Expected behavior | Micro-conversion |
|-------|-------------|-------------------|-----------------|
| Awareness | [entry page] | [what they see/feel] | [scroll, click, time on page] |
| Interest | [next step] | [engagement signal] | [form start, video play] |
| Decision | [comparison/proof] | [trust building] | [pricing view, case study read] |
| Action | [conversion page] | [final step] | [form submit, purchase, signup] |

**Peak-End Rule applied:** The conversion confirmation page is a designed peak moment, not a generic "thank you."
