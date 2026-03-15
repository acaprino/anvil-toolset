# Flow & Onboarding Layout Patterns

Spatial structure for guided, sequential, and focused-attention UIs. Used by `ui-layout-designer` agent.

## Step Indicator / Progress Bar

Sticky at top, always visible throughout the flow -- users must see the finish line.
```css
.wizard__progress {
  position: sticky;
  top: 0;
  z-index: var(--z-header, 100);
  background: var(--surface);
  padding: var(--space-4) var(--space-6);
  display: flex;
  gap: var(--space-2);
  align-items: center;
  border-bottom: 1px solid var(--border);
}
.step { flex: 1; height: 4px; border-radius: 2px; background: var(--border); }
.step--done    { background: var(--brand); }
.step--current { background: var(--brand); opacity: 0.5; }
```

## Single-Step / Quiz Layout

One question, one action -- nothing else competes for attention.
```css
.quiz-step {
  display: grid;
  grid-template-rows: auto 1fr auto; /* progress / question+options / next */
  min-height: 100dvh;
}
.quiz-step__body {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: var(--space-6);
  padding: var(--space-12) var(--space-6);
  max-width: 560px;
  margin-inline: auto;
  width: 100%;
}
.quiz-step__options {
  display: grid;
  gap: var(--space-3);
}
.quiz-step__actions {
  position: sticky;
  bottom: 0;
  background: var(--surface);
  padding: var(--space-4) var(--space-6);
  border-top: 1px solid var(--border);
}
```

## Coachmark / Tooltip Overlay

Floating callout anchored to a target element; backdrop dims everything else.
```css
/* Backdrop */
.coach-overlay {
  position: fixed;
  inset: 0;
  z-index: var(--z-coach, 400);
  pointer-events: none; /* let target element through via clip-path cutout */
}
/* Tooltip */
.coachmark {
  position: absolute;
  z-index: calc(var(--z-coach, 400) + 1);
  background: var(--surface-inverse);
  color: var(--text-inverse);
  border-radius: var(--radius-md);
  padding: var(--space-4) var(--space-6);
  max-width: 280px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.3);
}
/* Arrow pointer -- placed with data-side attribute */
.coachmark[data-side="bottom"]::before {
  content: "";
  position: absolute;
  top: -6px; left: 50%; transform: translateX(-50%);
  border: 6px solid transparent;
  border-bottom-color: var(--surface-inverse);
  border-top: none;
}
```
**Positioning rules:** arrow points at target; tooltip stays within viewport (`clamp()` on `left`); max 3-4 coachmarks per flow -- never launch on return visits.

## Notification Positioning

```css
/* Toast stack -- bottom-right, stacks upward */
.toast-region {
  position: fixed;
  bottom: var(--space-6);
  right: var(--space-6);
  display: flex;
  flex-direction: column-reverse;
  gap: var(--space-3);
  z-index: var(--z-toast, 500);
  max-width: 360px;
  width: calc(100vw - var(--space-12));
}
/* Badge on icon -- top-right corner */
.badge {
  position: absolute;
  top: -4px; right: -4px;
  min-width: 18px; height: 18px;
  border-radius: 9999px;
  background: var(--danger);
  color: #fff;
  font-size: 11px;
  font-variant-numeric: tabular-nums;
  display: grid; place-items: center;
  padding-inline: 4px;
}
/* Banner -- full-width below header */
.notification-banner {
  position: sticky;
  top: var(--header-height, 56px);
  z-index: calc(var(--z-header, 100) - 1);
  padding: var(--space-3) var(--space-6);
  text-align: center;
}
```

## Paywall / Content Gate Layout

```css
/* Content blur gate */
.paywall-wrapper { position: relative; overflow: hidden; }
.paywall-wrapper .content--gated {
  filter: blur(4px);
  user-select: none;
  pointer-events: none;
  max-height: 200px; /* cut off gradually */
  mask-image: linear-gradient(to bottom, black 40%, transparent 100%);
}
.paywall-cta {
  position: absolute;
  bottom: 0; left: 0; right: 0;
  padding: var(--space-8);
  background: linear-gradient(to bottom, transparent, var(--surface) 40%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-4);
  text-align: center;
}
```
**Taxometer model:** show the full first N items, gate from N+1 -- never reveal partial sentences.

## Completeness Meter Layout

Inline bar in sidebar or settings page -- always paired with "next step" link.
```css
.completeness {
  display: grid;
  gap: var(--space-2);
}
.completeness__bar {
  height: 6px;
  border-radius: 3px;
  background: var(--border);
  overflow: hidden;
}
.completeness__fill {
  height: 100%;
  border-radius: inherit;
  background: var(--brand);
  transition: width 0.4s ease;
  width: var(--progress, 0%); /* set via inline style */
}
.completeness__label {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: var(--text-secondary);
}
```

## Lazy Registration Gate Layout

CTA appears after user has invested effort (filled form, built cart) -- not before.
- Position: inline at the natural "save / proceed" moment -- not as an interstitial blocking entry
- Never a full-screen blocker at page load -- let users build investment first
- "Save your work" framing > "Create an account" framing -- loss aversion over friction
