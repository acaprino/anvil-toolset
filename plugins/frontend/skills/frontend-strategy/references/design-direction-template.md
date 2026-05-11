# Design Direction

## Color Palette

| Role | Hex | Usage | Psychology note |
|------|-----|-------|-----------------|
| Primary | #[hex] | [main brand color - buttons, links, key accents] | [emotional association] |
| Secondary | #[hex] | [supporting brand color - headers, highlights] | [emotional association] |
| Accent | #[hex] | [attention-drawing elements - CTAs, badges, alerts] | [emotional association] |
| Neutral - Dark | #[hex] | [body text, headings] | |
| Neutral - Mid | #[hex] | [secondary text, borders, dividers] | |
| Neutral - Light | #[hex] | [backgrounds, cards, subtle fills] | |
| Background | #[hex] | [page background] | |
| Success | #[hex] | [positive feedback, confirmations] | |
| Error | #[hex] | [error states, destructive actions] | |

**Contrast check:** All text/background combinations must meet WCAG AA minimum (4.5:1 for body, 3:1 for large text).

---

## Typography

| Role | Font Family | Weight | Size | Line Height | Usage |
|------|-------------|--------|------|-------------|-------|
| Display | [font name] | [weight] | [size] | [line height] | Hero headlines, feature titles |
| Heading | [font name] | [weight] | [size scale] | [line height] | H1-H4 |
| Body | [font name] | [weight] | [size] | [line height] | Paragraphs, lists, general content |
| UI | [font name] | [weight] | [size] | [line height] | Buttons, labels, navigation, forms |
| Mono | [font name] | [weight] | [size] | [line height] | Code, technical content (if needed) |

**Cognitive Fluency note:** Body font must prioritize readability over style. Display font expresses brand personality. Never sacrifice legibility for aesthetics.

---

## Visual Moodboard

### Adjective Grid

| Attribute | This site IS | This site is NOT |
|-----------|-------------|-----------------|
| Tone | [e.g. warm, approachable] | [e.g. cold, corporate] |
| Density | [e.g. spacious, breathing] | [e.g. cramped, cluttered] |
| Energy | [e.g. calm, confident] | [e.g. frantic, urgent] |
| Style | [e.g. refined, editorial] | [e.g. generic, templated] |

### Inspiration References

| Reference | URL | What to take | What to leave |
|-----------|-----|-------------|---------------|
| [Brand/site] | [URL] | [specific element: "their hero layout", "their button style"] | [what doesn't fit: "their color scheme", "their density"] |
| [Brand/site] | [URL] | [specific element] | [what doesn't fit] |
| [Brand/site] | [URL] | [specific element] | [what doesn't fit] |

---

## Spacing System

| Token | Value | Usage |
|-------|-------|-------|
| --space-xs | [e.g. 4px] | Tight gaps, icon padding |
| --space-sm | [e.g. 8px] | Inline spacing, small gaps |
| --space-md | [e.g. 16px] | Default component padding |
| --space-lg | [e.g. 24px] | Section inner padding, card padding |
| --space-xl | [e.g. 48px] | Section spacing |
| --space-2xl | [e.g. 80px] | Major section dividers |
| --space-3xl | [e.g. 120px] | Hero padding, dramatic breathing room |

**White space principle:** Premium websites use space generously. When in doubt, add more space, not less. White space signals confidence and exclusivity.

---

## Component Style Direction

Describe the visual treatment for key components (no code - visual direction only):

### Buttons
- **Primary:** [shape, fill, hover behavior, size]
- **Secondary:** [outline vs ghost, contrast approach]
- **Micro-interaction:** [hover/click animation description]

### Cards
- **Style:** [shadow vs border, corner radius, padding]
- **Hover state:** [elevation change, scale, overlay]

### Forms
- **Input style:** [border, focus state, label behavior]
- **Validation:** [inline, color, icon, animation]
- **Success feedback:** [confirmation approach - peak moment]

### Navigation
- **Desktop:** [sticky vs static, transparency, scroll behavior]
- **Mobile:** [hamburger vs tab bar, animation style]
- **Active state:** [indicator style]
