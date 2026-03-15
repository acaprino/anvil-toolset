# Layout Patterns Library

CSS layout patterns for common page structures. Used by `ui-layout-designer` agent.

## Holy Grail

Full-page chrome: header / (sidebar + main + aside) / footer.
```css
.holy-grail {
  display: grid;
  grid-template:
    "header header header" auto
    "sidebar main aside" 1fr
    "footer footer footer" auto
    / 240px 1fr 200px;
  min-height: 100dvh;
}
```

## Full-Bleed with Content Column

Content constrained to max-width; some sections break out to full viewport width.
```css
.page {
  display: grid;
  grid-template-columns:
    [full-start] minmax(1.5rem, 1fr)
    [content-start] min(100% - 3rem, 1200px)
    [content-end] minmax(1.5rem, 1fr)
    [full-end];
}
.full-bleed { grid-column: full; }
.content    { grid-column: content; }
```

## Split Screen

Two panes -- equal or weighted (60/40, 70/30).
```css
.split {
  display: grid;
  grid-template-columns: 1fr 1fr; /* or 3fr 2fr for weighted */
  min-height: 100dvh;
}
```

## Organic / Anti-Grid

Fluid, natural compositions that break rigid structure -- magazine-style editorial feel.
Deliberately asymmetrical placement, overlapping elements, varied whitespace, free-form content flow.
Use when: portfolio, creative agency, brand storytelling, editorial, fashion, art.
Avoid when: data-heavy, e-commerce catalog, enterprise dashboards.
```css
.organic {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: clamp(1rem, 3vw, 2.5rem);
}
/* Deliberately irregular placement */
.organic__hero   { grid-column: 1 / 8; grid-row: 1 / 3; }
.organic__aside  { grid-column: 9 / 13; grid-row: 1; align-self: end; }
.organic__pull   { grid-column: 3 / 11; margin-top: -4rem; position: relative; z-index: 1; }
.organic__offset { grid-column: 2 / 7; transform: rotate(-1deg); }
```
Key principles:
- Guide the eye through visual weight and flow, not grid lines
- Intentional overlap creates depth and editorial quality
- Vary element sizes dramatically -- one dominant, rest subordinate
- Negative space is the structure -- let content breathe unevenly
- Combine with motion narrative for scroll-driven journey feel

## Editorial Asymmetry

3-column base grid; content spans 2+1 or 1+2 for unequal rhythm.
```css
.editorial {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2rem;
}
.lead   { grid-column: span 2; }
.aside  { grid-column: span 1; }
```

## Bento Grid

Asymmetric card tiles with varied row/col spans -- dashboard, features, portfolio.
```css
.bento {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  grid-auto-rows: 200px;
  gap: 1rem;
}
.bento-lg   { grid-column: span 2; grid-row: span 2; }
.bento-wide { grid-column: span 3; }
```

## Sidebar + Main

Classic two-column: fixed sidebar, fluid content area.
```css
.layout {
  display: grid;
  grid-template-columns: 260px 1fr;
  gap: 2rem;
}
@media (max-width: 768px) {
  .layout { grid-template-columns: 1fr; }
}
.aside {
  position: sticky;
  top: var(--header-height, 4rem);
  max-height: calc(100dvh - var(--header-height, 4rem));
  overflow-y: auto;
}
```

## Masonry

Variable-height cards in aligned columns. CSS-native (Chrome 117+) or column-count fallback.
```css
/* Native masonry (progressive enhancement) */
@supports (grid-template-rows: masonry) {
  .masonry {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    grid-template-rows: masonry;
    gap: 1.5rem;
  }
}
/* Fallback */
.masonry-fallback {
  columns: 3;
  column-gap: 1.5rem;
}
```

## Centered Narrow (Reading Layout)

Max-width content column, generous margins -- articles, docs, forms.
```css
.narrow {
  max-width: 65ch; /* ~680px at 16px base */
  margin-inline: auto;
  padding-inline: clamp(1rem, 5vw, 2rem);
}
```

## Stacked Sections

Full-width alternating content rows -- marketing landing pages.
```css
.section { padding-block: clamp(4rem, 10vw, 8rem); }
.section:nth-child(even) { background: var(--surface-alt); }
.section__inner {
  max-width: 1200px;
  margin-inline: auto;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4rem;
  align-items: center;
}
.section:nth-child(even) .section__inner { direction: rtl; }
.section:nth-child(even) .section__inner > * { direction: ltr; }
```

## Card Grid with Subgrid Alignment

Auto-fill cards; subgrid aligns internals (title, body, CTA) across rows.
```css
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
}
.card {
  display: grid;
  grid-row: span 3;
  grid-template-rows: subgrid;
}
/* card children: .card__header, .card__body, .card__footer */
```
