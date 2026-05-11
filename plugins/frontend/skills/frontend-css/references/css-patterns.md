# CSS Patterns and Detailed Examples

## Container Query Patterns

```css
.card {
  container: --my-card / inline-size;
}

@container --my-card (width < 40ch) {
  /* Component-based responsive design */
}

@container (20ch < width < 50ch) {
  /* Range syntax */
}
```

**Container units:** `cqi`, `cqb`, `cqw`, `cqh` - size relative to container dimensions

**Anchored container queries:** Style positioned elements based on anchor fallback state
```css
.tooltip {
  container-type: anchored;
}

@container anchored(top) {
  /* Styles when positioned at top */
}
```

## Color Manipulation Patterns

```css
/* color-mix() */
.lighten {
  background: color-mix(in oklab, var(--brand), white);
}

/* Relative color syntax */
.lighter {
  background: oklch(from blue calc(l + .25) c h);
  background: oklch(from blue 75% c h); /* Set to specific lightness */
}

.semi-transparent {
  background: oklch(from var(--color) l c h / 50%);
}

.complementary {
  background: hsl(from blue calc(h + 180) s l);
}
```

## SASS Migration Patterns

Native CSS now covers most SASS use cases (custom properties, nesting, `@layer`). Use SASS when you need:

```scss
// Maps: iterate design tokens
$spacing: (
  'sm': 0.5rem,
  'md': 1rem,
  'lg': 1.5rem,
);

@each $name, $value in $spacing {
  .p-#{$name} { padding: $value; }
  .m-#{$name} { margin: $value; }
}

// Mixins: reusable style blocks with arguments
@mixin visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

.sr-only { @include visually-hidden; }

// @use and @forward (modern SASS module system - NOT @import)
// _tokens.scss
$brand: oklch(60% 0.2 230);

// main.scss
@use 'tokens' as t;
.button { background: t.$brand; }
```

**When to skip SASS:** If the project uses native CSS custom properties, `@layer`, and native nesting, SASS adds complexity without benefit. Prefer native CSS for new projects.

## BEM Naming Convention

Block-Element-Modifier: predictable, collision-free class names for component-scoped CSS without tooling.

```css
/* Block: standalone component */
.card { }

/* Element: part of the block, never standalone */
.card__title { }
.card__image { }
.card__body { }

/* Modifier: variant or state of a block or element */
.card--featured { }
.card--dark { }
.card__title--truncated { }
```

Rules:
- Elements never depend on other elements: `.card__title`, not `.card__header__title`
- Modifiers never appear alone - always with their block/element class
- Avoid deep nesting in selectors; BEM trades class verbosity for zero specificity wars
- One block = one file in a component-driven project

## CSS Modules (React/Vite)

Scoped styles via build-time hash - zero runtime overhead, zero global leakage.

```css
/* Button.module.css */
.button {
  padding: var(--space-3) var(--space-6);
  border-radius: var(--radius-md);
}

.button--primary {
  background: var(--brand);
  color: white;
}

.button--ghost {
  background: transparent;
  border: 1px solid currentColor;
}
```

```tsx
// Button.tsx
import styles from './Button.module.css';

export function Button({ variant = 'primary', children }) {
  return (
    <button className={`${styles.button} ${styles[`button--${variant}`]}`}>
      {children}
    </button>
  );
}
```

**Composing classes:**
```css
.error-button {
  composes: button from './Button.module.css';
  background: var(--danger);
}
```

**When to use BEM vs CSS Modules:**
- **BEM**: Plain HTML projects, design systems shipped as CSS, teams preferring no build step
- **CSS Modules**: React/Vue/Svelte component projects - scoping is automatic and co-location is clean
- **Tailwind**: Utility-first, good for rapid iteration; pair with `@apply` sparingly for repeated patterns

## Accessibility Patterns

### Focus Management
```css
/* :focus-visible - only show ring for keyboard, not mouse */
:focus-visible {
  outline: 2px solid var(--brand);
  outline-offset: 2px;
}

/* Remove default focus ring only if providing a custom one */
:focus:not(:focus-visible) {
  outline: none;
}
```

### Visually Hidden (Screen Reader Only)
```css
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

/* Unhide on focus (e.g. skip links) */
.sr-only:focus {
  position: static;
  width: auto;
  height: auto;
  overflow: visible;
  clip: auto;
  white-space: normal;
}
```

### Skip Link Pattern
```html
<a class="skip-link" href="#main-content">Skip to main content</a>
<main id="main-content">...</main>
```
```css
.skip-link {
  position: absolute;
  top: -100%;
  left: 1rem;
  padding: 0.5rem 1rem;
  background: var(--brand);
  color: white;
  border-radius: var(--radius-sm);
  z-index: 9999;
}
.skip-link:focus { top: 1rem; }
```

### Forced Colors / High Contrast Mode
```css
/* Respect Windows High Contrast / Forced Colors mode */
@media (forced-colors: active) {
  .button {
    border: 2px solid ButtonText;
    forced-color-adjust: none; /* Only when you need to preserve specific colors */
  }
}

/* Never convey information by color alone */
.error {
  color: var(--danger);
  border-left: 3px solid var(--danger); /* Also a shape cue */
}
.error::before {
  content: "! "; /* Also a text cue */
}
```

**WCAG contrast minimums:**
- Normal text: 4.5:1 (AA), 7:1 (AAA)
- Large text (18px+/14px+ bold): 3:1 (AA), 4.5:1 (AAA)
- UI components and focus rings: 3:1 (AA)
- Use `oklch()` - its uniform lightness makes contrast estimation intuitive

## Cross-Browser Compatibility

### Feature Detection with @supports
```css
@supports (animation-timeline: view()) {
  .fade-in {
    animation: fade linear both;
    animation-timeline: view();
  }
}

@supports (container-type: inline-size) {
  .responsive-card {
    container-type: inline-size;
  }
}

/* Negative - apply styles only when NOT supported */
@supports not (display: grid) {
  .layout { display: flex; flex-wrap: wrap; }
}
```

### Vendor Prefixes
Modern browsers require very few vendor prefixes (Autoprefixer handles the rest). The few remaining cases:

```css
/* -webkit- still needed for some properties */
.gradient {
  background: -webkit-linear-gradient(top, #000, #fff);
  background: linear-gradient(to bottom, #000, #fff);
}

/* Always write the unprefixed version last */
```

**Use Autoprefixer in your build tool** (PostCSS plugin) - don't write vendor prefixes manually. Configure `browserslist` in `package.json` to target the browsers you support:

```json
{
  "browserslist": "> 0.5%, last 2 versions, not dead"
}
```

### Respect User Preferences
```css
@media (prefers-reduced-motion: no-preference) {
  .animated {
    animation: slide 1s ease;
  }
}

@media (prefers-color-scheme: dark) {
  :root {
    --surface: #222;
  }
}

@media (prefers-contrast: more) {
  .text {
    font-weight: 600;
  }
}
```

## Responsive Images

```html
<!-- srcset + sizes: browser picks the right resolution -->
<img
  src="hero-800.jpg"
  srcset="hero-400.jpg 400w, hero-800.jpg 800w, hero-1600.jpg 1600w"
  sizes="(max-width: 600px) 100vw, (max-width: 1200px) 50vw, 800px"
  alt="Description"
  loading="lazy"
  decoding="async"
>

<!-- picture: art direction (different crops at different sizes) -->
<picture>
  <source
    media="(min-width: 800px)"
    srcset="hero-wide.webp"
    type="image/webp"
  >
  <source
    media="(max-width: 799px)"
    srcset="hero-square.webp"
    type="image/webp"
  >
  <img src="hero-wide.jpg" alt="Description">
</picture>
```

**CSS aspect ratio (prevents layout shift):**
```css
img {
  aspect-ratio: 16 / 9;
  width: 100%;
  height: auto;
  object-fit: cover;
}

/* Reserve space before image loads */
.image-container {
  aspect-ratio: 16 / 9;
  overflow: hidden;
}
```

**Performance rules:**
- Always set `width` and `height` attributes on `<img>` - browser reserves space before load
- Use `loading="lazy"` for below-fold images; never on LCP image
- Prefer `webp` with jpg/png fallback via `<picture>`
- Use `fetchpriority="high"` on the LCP image

## Real-World Example: Modern Card Component

```css
/* Cascade layer for organization */
@layer components.card {

  /* Custom properties with @property */
  @property --card-hue {
    syntax: "<number>";
    inherits: false;
    initial-value: 200;
  }

  .card {
    /* Container for responsive design */
    container: card / inline-size;

    /* Logical properties */
    inline-size: 100%;
    padding-inline: var(--space-md);
    padding-block: var(--space-lg);

    /* Modern color system */
    background: light-dark(
      oklch(98% 0.02 var(--card-hue)),
      oklch(20% 0.02 var(--card-hue))
    );

    /* Border with relative color */
    border: 1px solid oklch(from var(--surface) calc(l * 0.9) c h);

    /* Smooth corners */
    border-radius: var(--radius-md);

    /* View transition */
    view-transition-name: --card;

    /* Scroll-driven animation */
    animation: fade-in linear both;
    animation-timeline: view();
    animation-range: entry 0% cover 30%;

    /* Anchor for tooltips */
    anchor-name: --card-anchor;

    /* Transition custom property */
    transition: --card-hue 0.5s var(--ease-spring-3);

    &:hover {
      --card-hue: 280;
    }

    /* Responsive typography in container */
    @container card (width > 30ch) {
      .card__title {
        font-size: clamp(1.5rem, 3cqi, 2.5rem);
        text-wrap: balance;
      }
    }

    @container card (width < 30ch) {
      .card__image {
        aspect-ratio: 16 / 9;
        object-fit: cover;
      }
    }
  }

  .card__title {
    /* Text box trim for optical alignment */
    text-box: trim-both cap alphabetic;
    text-wrap: balance;

    /* Logical margin */
    margin-block-end: var(--space-sm);
  }

  .card__body {
    text-wrap: pretty;
    max-inline-size: 65ch;
  }

  .card__cta {
    /* Inherit font */
    font: inherit;

    /* Accent color */
    accent-color: var(--brand);

    /* Field sizing */
    field-sizing: content;

    /* Logical properties */
    padding-inline: var(--space-md);
    padding-block: var(--space-sm);

    /* Modern color with relative syntax */
    background: oklch(from var(--brand) l c h);
    color: oklch(from var(--brand) 95% 0.05 h);

    &:hover {
      background: oklch(from var(--brand) calc(l * 1.1) c h);
    }

    &:user-invalid {
      outline: 2px solid light-dark(red, #ff6b6b);
    }
  }

  /* Popover tooltip anchored to card */
  .card__tooltip[popover] {
    position-anchor: --card-anchor;
    position-area: block-start;
    position-try-fallbacks: flip-block;

    /* Entry animation */
    @starting-style {
      opacity: 0;
      scale: 0.9;
    }

    transition:
      opacity 0.2s,
      scale 0.2s,
      display 0.2s allow-discrete,
      overlay 0.2s allow-discrete;
  }

  /* Scroll state container queries */
  @supports (container-type: scroll-state) {
    .card__sticky-header {
      container-type: scroll-state;
      position: sticky;
      inset-block-start: 0;

      @container scroll-state(stuck: top) {
        box-shadow: 0 2px 8px oklch(0% 0 0 / 0.1);
      }
    }
  }

  /* Respect user preferences */
  @media (prefers-reduced-motion: reduce) {
    .card {
      animation: none;
      transition: none;
    }
  }

  @media (prefers-contrast: more) {
    .card {
      border-width: 2px;
    }
  }
}

/* Keyframes for scroll animation */
@keyframes fade-in {
  from {
    opacity: 0;
    scale: 0.95;
  }
  to {
    opacity: 1;
    scale: 1;
  }
}
```

### HTML for the Card Example

```html
<article class="card">
  <img
    class="card__image"
    src="image.jpg"
    alt="Description"
    loading="lazy"
  >

  <h2 class="card__title">Card Title</h2>

  <p class="card__body">
    Card description with pretty text wrapping that avoids orphans.
  </p>

  <button
    class="card__cta"
    popovertarget="card-tooltip"
  >
    Learn More
  </button>

  <div
    class="card__tooltip"
    popover="hint"
    id="card-tooltip"
  >
    Additional information appears here
  </div>
</article>
```
