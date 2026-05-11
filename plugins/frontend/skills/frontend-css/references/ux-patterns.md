# UX Pattern Decision Guide

Sourced from ui-patterns.com -- when to use each pattern, what makes it work, and what kills it. Used by `frontend-design` agent.

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

---

<!-- Section below derived from pbakaus/impeccable (Apache-2.0), snapshot 2026-05-11. -->

# UX Writing

The patterns above describe WHICH UX move to use; the rules below describe HOW the words in those moves should be written.

## The Button Label Problem

**Never use "OK", "Submit", or "Yes/No".** These are lazy and ambiguous. Use specific verb + object patterns:

| Bad | Good | Why |
|-----|------|-----|
| OK | Save changes | Says what will happen |
| Submit | Create account | Outcome-focused |
| Yes | Delete message | Confirms the action |
| Cancel | Keep editing | Clarifies what "cancel" means |
| Click here | Download PDF | Describes the destination |

**For destructive actions**, name the destruction:
- "Delete" not "Remove" (delete is permanent, remove implies recoverable)
- "Delete 5 items" not "Delete selected" (show the count)

## Error Messages: The Formula

Every error message should answer: (1) What happened? (2) Why? (3) How to fix it? Example: "Email address isn't valid. Please include an @ symbol." not "Invalid input".

### Error Message Templates

| Situation | Template |
|-----------|----------|
| **Format error** | "[Field] needs to be [format]. Example: [example]" |
| **Missing required** | "Please enter [what's missing]" |
| **Permission denied** | "You don't have access to [thing]. [What to do instead]" |
| **Network error** | "We couldn't reach [thing]. Check your connection and [action]." |
| **Server error** | "Something went wrong on our end. We're looking into it. [Alternative action]" |

### Don't Blame the User

Reframe errors: "Please enter a date in MM/DD/YYYY format" not "You entered an invalid date".

## Empty States Are Opportunities

Empty states are onboarding moments: (1) Acknowledge briefly, (2) Explain the value of filling it, (3) Provide a clear action. "No projects yet. Create your first one to get started." not just "No items".

## Voice vs Tone

**Voice** is your brand's personality, consistent everywhere.
**Tone** adapts to the moment.

| Moment | Tone Shift |
|--------|------------|
| Success | Celebratory, brief: "Done! Your changes are live." |
| Error | Empathetic, helpful: "That didn't work. Here's what to try..." |
| Loading | Reassuring: "Saving your work..." |
| Destructive confirm | Serious, clear: "Delete this project? This can't be undone." |

**Never use humor for errors.** Users are already frustrated. Be helpful, not cute.

## Writing for Accessibility

**Link text** must have standalone meaning: "View pricing plans" not "Click here". **Alt text** describes information, not the image: "Revenue increased 40% in Q4" not "Chart". Use `alt=""` for decorative images. **Icon buttons** need `aria-label` for screen reader context.

## Writing for Translation

### Plan for Expansion

German text is ~30% longer than English. Allocate space:

| Language | Expansion |
|----------|-----------|
| German | +30% |
| French | +20% |
| Finnish | +30-40% |
| Chinese | -30% (fewer chars, but same width) |

### Translation-Friendly Patterns

Keep numbers separate ("New messages: 3" not "You have 3 new messages"). Use full sentences as single strings (word order varies by language). Avoid abbreviations ("5 minutes ago" not "5 mins ago"). Give translators context about where strings appear.

## Consistency: The Terminology Problem

Pick one term and stick with it:

| Inconsistent | Consistent |
|--------------|------------|
| Delete / Remove / Trash | Delete |
| Settings / Preferences / Options | Settings |
| Sign in / Log in / Enter | Sign in |
| Create / Add / New | Create |

Build a terminology glossary and enforce it. Variety creates confusion.

## Avoid Redundant Copy

If the heading explains it, the intro is redundant. If the button is clear, don't explain it again. Say it once, say it well.

## Loading States

Be specific: "Saving your draft..." not "Loading...". For long waits, set expectations ("This usually takes 30 seconds") or show progress.

## Confirmation Dialogs: Use Sparingly

Most confirmation dialogs are design failures; consider undo instead. When you must confirm: name the action, explain consequences, use specific button labels ("Delete project" / "Keep project", not "Yes" / "No").

## Form Instructions

Show format with placeholders, not instructions. For non-obvious fields, explain why you're asking.

---

**Avoid**: Jargon without explanation. Blaming users ("You made an error" then prefer "This field is required"). Vague errors ("Something went wrong"). Varying terminology for variety. Humor for errors.
