# UX Pattern Decision Guide

Sourced from ui-patterns.com -- when to use each pattern, what makes it work, and what kills it. Used by `web-designer` agent.

## Onboarding & Education Patterns

**Coachmarks** (overlay tooltips pointing at UI elements)
- Use for: novel/complex interfaces where design can't speak for itself
- Avoid: mid-task (disruptive), as a substitute for better information architecture
- Borderline anti-pattern -- treat the symptom, not the root cause
- If you must use: max 3-4 coachmarks per flow (working memory limit); always provide "Skip" escape; never launch on every visit
- Prefer Guided Tour or Inline Hints instead when possible

**Guided Tour** (just-in-time contextual hints)
- Use for: first-time feature discovery, notifying about new features, non-self-explanatory UI
- Product-guided: auto-sequences through steps; User-guided: triggers at natural interaction points (more adaptive)
- Positioning: hints appear adjacent to relevant elements; dim surrounding UI to direct attention
- Always provide escape; never force linear progression; connect hints to completion states

**Inline Hints** (embedded instructional content in normal layout flow)
- Use for: non-critical guidance that complements primary content; pairs well with Blank Slate
- Avoid: for critical instructions (users skim past inline hints); for irrelevant-to-context tips
- Blend visually with content -- same type scale, no loud styling; dismissible after action completion
- Fade out once user demonstrates competency (action completed)

**Blank Slate** (empty state with guidance)
- First user experience of an empty section -- make it feel intentional, not broken
- One clear CTA: "Create your first X" (single action, not a menu)
- Show what the populated state looks like (screenshot or illustration)
- Supportive tone: explain what will be here -- not what is missing
- Disappears as user populates content; inline hints can extend the guidance

**Lazy Registration** (try-before-commit)
- Use when: users need to evaluate before trusting; registration requires sensitive info; competitive comparison expected
- Works via loss aversion: once users invest effort (data entry, curation), registration preserves their work
- Two modes: shopping-cart (light -- accumulate before committing) vs. auto-generated anonymous account (heavy -- full session persistence)
- Avoid when: registration is already minimal; you need accountable users immediately

**Completeness Meter** (progress bar toward 100% profile/setup)
- Use for: optional goal completion (profile setup, onboarding checklist) -- not critical sequential tasks
- Psychological drivers: curiosity (what happens at 100%?), goal-gradient effect (effort increases as goal approaches)
- Suggest next step clearly alongside the meter -- don't leave users guessing what to complete
- Placement: dashboard sidebar, settings page, or dedicated onboarding section
- Examples: LinkedIn profile strength, Klaviyo onboarding checklist

**Steps Left / Progress Indicator** (multi-step process navigation)
- Show all steps; highlight current; visually distinguish completed
- Remove extra navigation and ads during multi-step flows -- reduce escape routes
- Applies to: checkout, wizard, registration, any process > 2 steps
- Optimal step count: 3-7; < 3 -> single screen; > 7 -> rethink scope
- End always visible -- users abandon when they can't see the finish line

---

## Trust & Social Proof Patterns

**Social Proof** (crowd validation signals)
- Six types: expert endorsement, celebrity association, customer logos, user testimonials, crowd metrics ("10,000+ users"), friend influence
- Placement: always adjacent to the primary CTA -- not buried in the footer
- Photos mandatory with testimonials: faces increase perceived authenticity
- Match social proof to audience: users trust people similar to themselves more than broad audience claims
- When it backfires: highlighting undesired behavior (negative social proof amplifies it); expert audience who doesn't defer to crowd

**Testimonials**
- Formats by context: short quote + photo (landing page), carousel (social proof section), video (product page), case study (B2B)
- Prominent screen real estate with contrasting background -- never small or footnoted
- Name + photo + role/company = trust; anonymous quotes = skepticism
- Pair with specific outcomes: "Reduced our churn by 40%" beats "Great product!"

**Notifications**
- Trigger only: time-sensitive, user-directed, requiring acknowledgment
- Never trigger: for info already visible on screen, for background operations, for marketing unless opt-in
- Minimize interruption: batch similar notifications; provide count badge, not individual alerts
- Dismissible with settings control -- user must be able to reduce cadence
- Cross-device sync: consumed on one device -> disappears everywhere

---

## Persuasive & Conversion Patterns

**Scarcity** (limited time, limited stock, restricted access)
- Time-based: expiring offers create urgency for immediate decision
- Stock-based: "Only 3 left" signals exclusivity and premium value
- Information-based: restricted access increases perceived value (beta access, invite-only)
- Use authentically -- fabricated scarcity detected = trust destroyed, never recovers
- Newly experienced scarcity works strongest; repeated exposure desensitizes; refresh the signal

**Paywall** (gated content access)
- Five models: hard paywall (all blocked), freemium (mixed), taxometer (N free then gate), time pass (day/week), bulk sale (corporate)
- Taxometer model converts best for content-driven products -- let users experience value before the wall hits
- Gate high-value, exclusive content -- if content is low quality, paywall accelerates churn
- Freemium: give enough that users want more; gate the features that become necessary at scale
- Don't use when: primary revenue is advertising (paywall reduces impressions)

---

## Cognitive Load Patterns

**Chunking** (grouping information into digestible units)
- Short-term memory: 3-5 items; group beyond this threshold into labeled chunks
- Tactics: group by similarity, add distinct headings between text chunks, auto-format input fields (phone: (123) 456-7890)
- Decision points: apply Hick's Law -- max 5-7 options before chunking into categories
- Don't use chunking to justify "simplicity" in general -- it specifically addresses memory/processing limits
- Application: pricing tiers, navigation categories, settings sections, form field grouping
