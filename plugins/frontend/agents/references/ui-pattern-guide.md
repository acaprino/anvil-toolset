# UI Pattern Selection Guide

Sourced from ui-patterns.com -- decision rules for choosing the right component pattern per layout context. Used by `ui-layout-designer` agent.

## Content Display: Cards vs. List vs. Table vs. Gallery vs. Thumbnail

| Pattern | Use when | Avoid when |
|---------|----------|------------|
| **Cards** | Heterogeneous content, browsing-first, mixed media | Strictly ordered lists, image-only galleries |
| **Article List** | Editorial/news, time-based or categorical content | Product listings, non-story content |
| **Table** | Homogeneous structured data, comparison, sorting needed | Narrative content, visual-first experiences |
| **Gallery** | Sequential image browsing, max viewport per image | Quick scanning of many items -- use thumbnails instead |
| **Thumbnail** | Visual preview grids, bandwidth-conscious browsing | Single hero image, when cropping destroys meaning |
| **Carousel** | Visual collections (posters, products), limited space, discovery | Text-only content, items needing explicit comparison |

**Cards layout rules:**
- One card = one concept -- never split a concept across cards
- Make the entire card clickable (Fitts's Law) -- not just the title
- Subgrid for internal alignment: title / body / CTA rows snap across columns
- Rounded corners + subtle shadow = perceived depth without decorative noise
- High-quality image as the primary visual anchor -- top of card, 16:9 or 3:2 ratio

**Article List layout rules:**
- Avoid pagination -- long scannable lists outperform page-break interruptions
- Category label sets content expectation before the headline
- Group by time (week/month) or category -- never abstract page numbers
- Teaser text: 2 lines max; headline does the luring, teaser confirms

**Carousel layout rules:**
- 3-8 items visible at once; arrows + position dots mandatory
- Horizontal scroll with `scroll-snap-type: x mandatory` -- never auto-play without pause
- Only for visual content; if items can't be identified by image alone, use a list instead
```css
.carousel {
  display: flex;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  gap: var(--space-4);
}
.carousel__item {
  scroll-snap-align: start;
  flex: 0 0 calc(33.333% - var(--space-4));
}
```

---

## Navigation Patterns: Which Component for Which Hierarchy

| Pattern | Structure | Use when |
|---------|-----------|----------|
| **Navigation Tabs** | Horizontal, top-level | 2-9 sections, flat hierarchy, full-width nav |
| **Module Tabs** | Horizontal, in-page | Multiple content panes in a single component, no page reload |
| **Accordion Menu** | Vertical, collapsible | Space-constrained nav, 2 levels of hierarchy, < 10 categories |
| **Horizontal Dropdown** | Horizontal + flyout | 2-9 sections with subsections, desktop-first |
| **Breadcrumbs** | Inline trail | Deep hierarchies, external traffic entry points |
| **Fat Footer** | Footer grid | High-traffic shortcuts, trust signals, secondary navigation |

**Navigation Tabs rules:**
- Active tab background must match (or seamlessly transition to) the content area background
- Tab selected = location indicator; if current location doesn't need emphasis -> use dropdown instead
- Secondary subsection bar below primary tabs maintains hierarchy legibility

**Breadcrumbs rules:**
- Position above page title, below primary nav
- Each label must match the actual section title exactly
- Never use as the sole navigation -- always alongside primary nav
- Don't show on homepage or top-level pages

**Fat Footer rules:**
- Curated links, not a full sitemap
- Organize into labeled columns: About / Product / Support / Legal / Social
- Ask: what is the logical next step after finishing main content? -> those links go here
- Trust builders (payment badges, certifications) live in footer for financial/sensitive services

**Accordion Menu rules:**
- Vertical orientation dominates -- horizontal accordions confuse users
- One section open at a time (closing previous) unless sections are independent
- Avoid when users frequently switch between sections -- scrolling to collapsed headers is friction

---

## Content Loading: Pagination vs. Continuous Scroll vs. Load More

| Pattern | Use when | Avoid when |
|---------|----------|------------|
| **Pagination** | Ordered/sorted data, users need specific pages, bookmarkable positions | Flow-critical browsing, mobile with slow reloads |
| **Continuous Scrolling** | Browsable unordered feeds, mobile, no need to return to exact position | Alphabetical data, content users bookmark, sites with footers |
| **Load More button** | Compromise: user-controlled loading, footers must remain accessible | -- |

**Pagination layout rules:**
- Controls below content -- user finishes reading before deciding to continue
- Current page clearly highlighted; disabled states (prev on p.1) visually grayed
- Previous/Next buttons visually separated from numbered links
```css
.pagination { display: flex; gap: var(--space-2); align-items: center; justify-content: center; }
.pagination__current { font-weight: 700; border-bottom: 2px solid currentColor; }
.pagination__disabled { opacity: 0.4; pointer-events: none; }
```

**Continuous Scrolling rules:**
- Loading indicator at bottom -- never leave users guessing if more content exists
- Fixed header recommended -- removes spatial disorientation as content grows
- Avoid on pages with footers unless footer is sticky/fixed
- Browser memory: cap loaded items and recycle DOM for very long feeds

---

## Page Archetype Layouts

**Dashboard:**
- Single unifying goal -- ruthlessly cut metrics that don't serve it
- Priority ordering: urgent/actionable -> top; monitoring/historical -> below
- Bento grid for varied widget sizes; consistent gutter, no orphaned widgets
- Group related KPIs -- proximity implies relationship
- Three dashboard types: Operational (real-time), Strategic (KPIs), Analytical (drill-down) -> each needs a different information density

**Product Page:**
- Above-fold: product title + hero image + price + add-to-cart -- never below the fold
- Image left / info right (desktop); stacked image top / info below (mobile)
- Trust indicators (reviews, guarantees, payment badges) immediately below CTA
- Variant selectors (size, color) before the CTA, never after
- Related products: below fold, separate section -- never interrupt the purchase flow
```css
.product-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: clamp(2rem, 5vw, 4rem);
  align-items: start;
}
@media (max-width: 768px) {
  .product-layout { grid-template-columns: 1fr; }
}
```

**Pricing Table:**
- 2-4 plans maximum; more -> decision paralysis
- Arrange left-to-right: expensive -> cheap (stops anchoring on cheapest)
- Middle "Goldilocks" tier: visually highlighted (scale: 1.02, ring, color) to anchor choice
- Sticky plan headers when feature list is long -- price always visible while scrolling
- Unavailable features: visual fade or strikethrough, never hidden rows
```css
.pricing-table {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}
.pricing-card--featured {
  transform: scale(1.04);
  box-shadow: 0 0 0 2px var(--brand-color);
  z-index: 1;
}
```

**Wizard (Multi-Step Form):**
- Progress indicator at top: completed / current / remaining steps always visible
- Each step above the fold -- no scrolling required per step; if overflow, break into sub-steps
- Previous/Next buttons at fixed bottom position; Finish only on last step
- Review screen before submission: summarize all choices; allow editing in place
- Step count: 3-7 steps ideal; < 3 -> use single form; > 7 -> re-examine scope
```css
.wizard {
  display: grid;
  grid-template-rows: auto 1fr auto; /* progress / content / actions */
  min-height: 100dvh;
}
.wizard__progress { position: sticky; top: 0; z-index: 10; background: var(--surface); }
.wizard__actions  { position: sticky; bottom: 0; padding: var(--space-4); background: var(--surface); }
```

**FAQ:**
- Organize with Accordion pattern -- questions collapsed, answers revealed on demand
- Category labels above accordion groups if > 8 questions
- Front-load: top 20% of questions answer 80% of user needs
- Each answer self-contained as a landing page -- optimize for direct search entry
- Search bar above the list for > 20 questions

---

## Overlay and Focus Patterns

**Modal:**
- Use only when action is critical and must block everything else
- Never for error/success/warning messages -- use toast or inline feedback instead
- Avoid on mobile (full-screen modals = confusing; use bottom sheets instead)
- Escape mechanisms: X button (top-right), Cancel button, ESC key, click outside
- Width: max 600px for forms, max 900px for content -- never full viewport width
- Dimmed overlay behind: `background: rgba(0,0,0,0.5)` -- clear spatial separation from page
```css
.modal-overlay {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.5);
  display: grid; place-items: center;
  z-index: var(--z-modal, 300);
}
.modal {
  width: min(600px, 90vw);
  background: var(--surface);
  border-radius: var(--radius-lg);
  padding: var(--space-8);
}
```

**Progressive Disclosure:**
- Show essential information first; "Show more" / expandable sections for depth
- Keep previous steps visible when users progress through multi-step flows
- Hidden content must never be part of primary task flow -- only secondary/advanced details
- Use for: advanced settings, long descriptions, secondary specs, optional filters

**Blank Slate:**
- Never leave a new user facing a bare empty screen
- Show a preview of the populated state (screenshot or illustration)
- One clear action CTA: "Create your first X" -- not a menu of options
- Supportive tone: explain what the page will look like, not what's missing
- Position guidance centrally; maintain brand trust during this vulnerable moment

---

## Feed and Stream Layout

**Activity Stream:**
- Structure per item: Avatar | Actor | Verb | Object | Timestamp
- Dedicated avatar column left (people care about WHO first)
- Aggregate similar actions: "3 people liked your post" > 3 separate items
- Consistent item height for scannability -- variable heights break rhythm
- Filtering control above stream: "All" / "Following" / "Mentions" -- always visible
```css
.activity-item {
  display: grid;
  grid-template-columns: 40px 1fr auto; /* avatar / content / time */
  gap: var(--space-3);
  align-items: start;
  padding-block: var(--space-4);
  border-bottom: 1px solid var(--border);
}
```

---

## Adaptable View (Responsive Design Control)
- Modern responsive CSS often replaces this pattern entirely -- prefer automatic adaptation
- If needed: limit user controls to font-size and interface density (not arbitrary element hiding)
- Persist preference in `localStorage` -- settings must survive page reloads
- Control must be immediately discoverable -- not buried in settings
