# Reply to Customer Review - Implementation Plan

> **For agentic workers:** Use subagent-driven execution (if subagents available) or ai-tooling:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a skill and command to the digital-marketing plugin that generates professional, adaptive responses to online customer reviews with sentiment analysis and operational suggestions.

**Architecture:** Single skill (`SKILL.md`) with two reference files (hospitality-patterns.md, ecommerce-patterns.md) and one slash command. All logic lives in the skill prompt -- no agents, no scripts, no build step.

**Tech Stack:** Markdown (SKILL.md + references + command), marketplace.json registration

---

## Chunk 1: Skill and Reference Files

### Task 1: Create the SKILL.md

**Files:**
- Create: `plugins/digital-marketing/skills/reply-to-customer-review/SKILL.md`

- [ ] **Step 1: Create the skill directory**

```bash
mkdir -p plugins/digital-marketing/skills/reply-to-customer-review/references
```

- [ ] **Step 2: Write SKILL.md**

Write the file `plugins/digital-marketing/skills/reply-to-customer-review/SKILL.md` with the following content:

```markdown
---
name: reply-to-customer-review
description: >
  Generate professional, empathetic, on-brand responses to online customer reviews.
  Analyzes sentiment, detects severity, adapts tone, and provides operational suggestions.
  Supports hospitality (Airbnb, Booking, Tripadvisor) and e-commerce/app (Amazon, App Store,
  Trustpilot) with sector-specific patterns. Trigger on: review, recensione, reply to review,
  respond to review, risposta recensione, customer review, negative review, bad review,
  rispondere alla recensione, gestione recensioni, review response.
---

# Reply to Customer Review

Generate a professional, empathetic response to a customer review. Analyze the review, craft an adaptive response, and provide operational suggestions.

## Input

The user pastes a customer review (or invokes via `/reply-to-customer-review`). Optional parameters:

- **--brand "Name"** -- business name to use in the response
- **--tone formal|friendly|casual** -- override tone (default: professional-empathetic)
- **--lang XX** -- force output language (default: same as review)
- **--sector hospitality|ecommerce|auto** -- force sector (default: auto-detect)

## Process

Execute all three steps inline. Do NOT spawn subagents.

### Step 1: Analysis

Analyze the review and determine:

**Language** -- identify the review language. For mixed-language reviews, identify the dominant language and note secondary languages.

**Sentiment** -- classify as one of:
- POSITIVE -- satisfied customer, praise, recommendation
- NEUTRAL -- factual, neither praise nor complaint
- NEGATIVE -- dissatisfaction, complaint, criticism
- MIXED -- contains both positive and negative elements

**Key Points** -- extract the specific topics mentioned (e.g., cleanliness, shipping speed, product quality, staff attitude, app stability, price, location).

**Severity** (negative/mixed reviews only) -- assess as one of:
- UNFOUNDED -- no real issue, emotional venting, unrealistic expectations
- MINOR -- real issue but limited impact, easy to address
- MAJOR -- serious issue requiring immediate attention, systemic problem
- ABUSIVE -- contains threats, profanity, personal attacks. Flag for platform reporting. Recommend not responding publicly or generate a minimal professional response. Never mirror hostility.

**Sector** -- auto-detect from vocabulary and context:
- HOSPITALITY -- mentions stay, check-in, room, host, property, booking, location, amenities, noise, breakfast
- ECOMMERCE -- mentions shipping, delivery, return, refund, product, app, crash, bug, update, order, package
- GENERIC -- does not clearly match either sector

Load the appropriate reference file: `references/hospitality-patterns.md` or `references/ecommerce-patterns.md`. If generic, use general best practices.

### Edge Cases

- **Star-only (no text):** Ask the user for the star rating. Generate a brief acknowledgment appropriate to the implied sentiment.
- **Very short (under 5 words):** Flag ambiguity in Analysis. Generate a brief response inviting the customer to share more details.
- **Mixed-language:** Respond in the dominant language. Note secondary language in Analysis.

### Step 2: Response Generation

Craft the response following these rules:

**Tone:** Use the user-specified tone or default to professional-empathetic. The tone scale:
- `formal` -- corporate, third-person, measured language
- `friendly` -- warm, first-person, conversational but professional (this is the professional-empathetic default)
- `casual` -- relaxed, direct, uses contractions and informal phrasing

**Language:** Respond in the same language as the review unless --lang overrides.

**Brand:** If --brand is provided, sign off with the brand name. If not, use a generic professional sign-off.

**Adaptive strategy for negative reviews:**

| Severity | Strategy | Key Elements |
|----------|----------|-------------|
| UNFOUNDED | Diplomatic-defensive | Acknowledge feelings, provide factual context, invite private contact |
| MINOR | Empathetic-proactive | Thank for feedback, acknowledge the issue, describe corrective action taken, invite return |
| MAJOR | Empathetic-proactive (urgent) | Sincere apology, take full responsibility, describe immediate corrective action, offer compensation, provide direct contact for follow-up |
| ABUSIVE | Minimal/No response | If responding: brief, professional, offer private channel. May recommend not responding and reporting to platform instead |

**For positive reviews:** Thank sincerely, reference specific points mentioned, reinforce the positive experience, invite return/continued use. Keep it genuine -- avoid sounding templated.

**For neutral reviews:** Thank for taking the time, address any suggestions, invite further engagement.

**Response length guidelines:**
- Positive reviews: 2-4 sentences
- Neutral reviews: 2-3 sentences
- Negative (minor): 3-5 sentences
- Negative (major): 4-6 sentences
- Abusive: 1-2 sentences max (if responding at all)

### Step 3: Output

Present three clearly separated sections:

**RESPONSE**

The ready-to-copy response text, formatted for the review platform. No markdown formatting -- plain text that can be pasted directly.

**ANALYSIS**

| Field | Value |
|-------|-------|
| Language | [detected language] |
| Sentiment | [POSITIVE/NEUTRAL/NEGATIVE/MIXED] |
| Severity | [UNFOUNDED/MINOR/MAJOR/ABUSIVE or N/A] |
| Sector | [HOSPITALITY/ECOMMERCE/GENERIC] |
| Key Points | [comma-separated list] |
| Flags | [any concerns requiring attention, or "None"] |

**OPERATIONAL SUGGESTIONS**

Bulleted list of recommended internal actions based on the review content. Examples:
- Flag issue to [specific team]
- Update [specific asset] to reflect current state
- Contact customer privately via [channel]
- Offer [specific compensation]
- Monitor for recurring pattern of [issue]
- No action needed -- positive reinforcement

If the review is positive with no issues, suggest ways to leverage it (e.g., "Consider featuring this review on your website", "Share with the team as positive feedback").

## Refinement

After presenting the output, the user may request adjustments:
- "more formal" / "more casual" -- regenerate with adjusted tone
- "shorter" / "longer" -- adjust response length
- "in English" / "in italiano" -- regenerate in specified language
- "don't mention X" / "add Y" -- specific content adjustments

Regenerate only the RESPONSE section when adjusting. Keep Analysis and Operational Suggestions unchanged unless the user specifically asks to revise them.
```

- [ ] **Step 3: Verify the file was created**

```bash
ls -la plugins/digital-marketing/skills/reply-to-customer-review/SKILL.md
```

- [ ] **Step 4: Commit**

```bash
git add plugins/digital-marketing/skills/reply-to-customer-review/SKILL.md
git commit -m "Add reply-to-customer-review SKILL.md for digital-marketing plugin"
```

### Task 2: Create hospitality-patterns.md

**Files:**
- Create: `plugins/digital-marketing/skills/reply-to-customer-review/references/hospitality-patterns.md`

- [ ] **Step 1: Write hospitality-patterns.md**

Write the file `plugins/digital-marketing/skills/reply-to-customer-review/references/hospitality-patterns.md` with the following content:

```markdown
# Hospitality Review Patterns

Sector-specific reference for responding to reviews in the hospitality industry (hotels, vacation rentals, B&Bs, hostels).

## Platforms

Airbnb, Booking.com, Google Maps, Tripadvisor, Vrbo, Expedia, Hotels.com, Agoda

## Vocabulary Map

Common topics in hospitality reviews and their typical phrasing:

| Category | Positive Signals | Negative Signals |
|----------|-----------------|------------------|
| Cleanliness | spotless, immaculate, clean, fresh, well-maintained | dirty, dusty, stains, hair, mold, unclean, filthy |
| Communication | responsive, helpful, quick reply, great host, welcoming | unresponsive, slow, rude, no reply, unhelpful, ghosted |
| Accuracy | as described, matched photos, better than expected | misleading, photos don't match, false advertising, smaller than expected |
| Location | great location, walkable, quiet area, central, close to | noisy area, far from, unsafe, bad neighborhood, hard to find |
| Value | great value, worth the price, fair, affordable, bargain | overpriced, not worth it, expensive for what you get, rip-off |
| Amenities | well-equipped, comfortable bed, great kitchen, nice pool | broken, missing, no hot water, weak wifi, uncomfortable, outdated |
| Check-in | smooth, easy, flexible, self check-in worked perfectly | confusing directions, late check-in, lockbox didn't work, no instructions |
| Noise | quiet, peaceful, relaxing, serene | noisy, loud neighbors, thin walls, street noise, party house next door |

## Response Templates by Severity

### Positive Review Response Pattern

Structure: Thank -> Reference specific detail -> Reinforce -> Invite return

Example (friendly tone):
> Thank you so much for your kind words, [Name]! We're thrilled you enjoyed the [specific detail they mentioned]. It's exactly the experience we want every guest to have. We'd love to welcome you back anytime -- your next stay will be just as special!

### Negative - Unfounded/Unrealistic Expectations

Structure: Acknowledge -> Provide context -> Invite private resolution

Example (friendly tone):
> Thank you for sharing your experience, [Name]. We understand expectations can vary, and we're sorry the stay didn't meet yours. Our listing clearly describes [relevant detail], but we appreciate the feedback and are always looking to improve our communication. We'd love to discuss this further -- please reach out to us directly at [contact].

### Negative - Minor Real Problem

Structure: Thank -> Acknowledge issue -> Explain corrective action -> Invite return

Example (friendly tone):
> Thank you for your honest feedback, [Name]. You're absolutely right about [issue], and we sincerely apologize for the inconvenience. We've already [specific corrective action taken]. This isn't the standard we hold ourselves to, and we've made sure it won't happen again. We hope you'll give us another chance to show you the experience we're known for.

### Negative - Major Real Problem

Structure: Apologize -> Take responsibility -> Describe immediate action -> Offer compensation -> Provide direct contact

Example (friendly tone):
> We owe you a sincere apology, [Name]. What you described with [issue] is completely unacceptable, and we take full responsibility. We've immediately [urgent corrective action], and [additional systemic change]. We'd like to make this right -- please contact us directly at [contact] so we can [specific compensation offer]. Your feedback is helping us become better, and we're grateful you brought this to our attention.

## Operational Actions by Category

| Issue Category | Suggested Internal Actions |
|---------------|---------------------------|
| Cleanliness | Flag to cleaning team, schedule deep clean, review cleaning checklist, inspect before next guest |
| Communication | Review response time metrics, set up auto-replies, assign dedicated guest contact |
| Accuracy | Update listing photos, revise description, add clarifying details |
| Location | Add detailed directions, update local area guide, mention noise levels in listing |
| Value | Review pricing strategy, compare with competitors, consider seasonal adjustments |
| Amenities | Schedule maintenance/repair, replace broken items, update amenity list |
| Check-in | Improve check-in instructions, test lockbox/smart lock, add backup access method |
| Noise | Add noise disclaimer to listing, provide earplugs, investigate soundproofing |
```

- [ ] **Step 2: Commit**

```bash
git add plugins/digital-marketing/skills/reply-to-customer-review/references/hospitality-patterns.md
git commit -m "Add hospitality review patterns reference"
```

### Task 3: Create ecommerce-patterns.md

**Files:**
- Create: `plugins/digital-marketing/skills/reply-to-customer-review/references/ecommerce-patterns.md`

- [ ] **Step 1: Write ecommerce-patterns.md**

Write the file `plugins/digital-marketing/skills/reply-to-customer-review/references/ecommerce-patterns.md` with the following content:

```markdown
# E-commerce and App Review Patterns

Sector-specific reference for responding to reviews of products, online stores, and mobile/web applications.

## Platforms

Amazon, Trustpilot, App Store (iOS), Google Play, eBay, Etsy, G2, Capterra, Product Hunt

## Vocabulary Map

Common topics in e-commerce/app reviews and their typical phrasing:

| Category | Positive Signals | Negative Signals |
|----------|-----------------|------------------|
| Product Quality | excellent quality, well-made, durable, exceeded expectations, premium | cheap, broke quickly, poor quality, defective, flimsy, not as pictured |
| Shipping/Delivery | fast shipping, well-packaged, arrived early, free shipping | late delivery, damaged in transit, wrong item, lost package, slow shipping |
| Customer Service | helpful support, quick response, resolved immediately, went above and beyond | no response, unhelpful, rude, ignored, long wait, ticket closed without resolution |
| App Stability | smooth, fast, no crashes, works perfectly, reliable | crashes, freezes, bugs, slow, laggy, won't load, error messages |
| App Features | intuitive, easy to use, love the new feature, clean design | missing features, confusing UI, hard to navigate, cluttered, feature removed |
| Price/Value | great value, worth every penny, affordable, good deal | overpriced, not worth it, hidden fees, subscription too expensive, bait and switch |
| Returns/Refunds | easy return, quick refund, hassle-free, no questions asked | difficult return process, refused refund, restocking fee, took weeks for refund |
| Packaging | beautiful packaging, eco-friendly, gift-ready, well-protected | excessive packaging, damaged box, no protection, wasteful |

## Response Templates by Severity

### Positive Review Response Pattern

Structure: Thank -> Reference specific detail -> Reinforce value -> Encourage continued use

Example (friendly tone):
> Thank you for the wonderful review, [Name]! We're so glad you're enjoying [specific feature/product they mentioned]. Our team works hard to [relevant value proposition], and it means a lot to hear it's making a difference. We have some exciting updates coming that we think you'll love!

### Negative - Unfounded/Unrealistic Expectations

Structure: Acknowledge -> Clarify product/service scope -> Offer guidance -> Invite contact

Example (friendly tone):
> Thank you for your feedback, [Name]. We understand [product/app] might not have met your expectations regarding [specific point]. Our [product/feature] is designed to [clarify actual scope], and we've clearly described this in [listing/documentation]. That said, we're always improving -- if you'd like help getting the most out of [product], our support team is happy to assist at [contact].

### Negative - Minor Real Problem

Structure: Thank -> Acknowledge -> Explain fix -> Offer remedy

Example (friendly tone):
> Thank you for letting us know, [Name]. We're sorry about the [issue] you experienced -- that's not the standard we aim for. We've [specific corrective action] to prevent this going forward. We'd love to make this right for you -- please reach out to our support team at [contact] and we'll [specific remedy].

### Negative - Major Real Problem

Structure: Apologize -> Take responsibility -> Immediate action -> Compensation -> Direct contact

Example (friendly tone):
> We sincerely apologize for your experience, [Name]. What happened with [issue] is unacceptable, and we take full responsibility. We've immediately [urgent action taken], and our team is [systemic fix being implemented]. Please contact us directly at [contact] -- we want to [specific compensation: full refund, replacement, etc.] and make sure this is fully resolved for you.

## Operational Actions by Category

| Issue Category | Suggested Internal Actions |
|---------------|---------------------------|
| Product Quality | Inspect current batch, contact supplier, update QC checklist, pull defective stock |
| Shipping/Delivery | Review carrier performance, improve packaging, update tracking notifications, switch carrier for region |
| Customer Service | Review agent interaction, retrain if needed, update response templates, escalate to supervisor |
| App Stability | Create bug ticket for dev team, check crash analytics, prioritize in next sprint, notify affected users of fix |
| App Features | Log feature request, review UX analytics, consider in product roadmap, communicate timeline if planned |
| Price/Value | Review pricing vs. competitors, clarify value proposition in listing, consider promotional offer |
| Returns/Refunds | Process refund immediately, review return policy clarity, simplify return flow |
| Packaging | Review packaging materials, improve protection for fragile items, consider eco-friendly options |
```

- [ ] **Step 2: Commit**

```bash
git add plugins/digital-marketing/skills/reply-to-customer-review/references/ecommerce-patterns.md
git commit -m "Add e-commerce review patterns reference"
```

### Task 4: Create the command file

**Files:**
- Create: `plugins/digital-marketing/commands/reply-to-customer-review.md`

- [ ] **Step 1: Write the command file**

Write the file `plugins/digital-marketing/commands/reply-to-customer-review.md` with the following content:

```markdown
---
description: "Reply to a customer review with sentiment analysis, adaptive tone, and operational suggestions"
argument-hint: "\"<review text>\" [--brand <name>] [--tone formal|friendly|casual] [--lang <code>] [--sector hospitality|ecommerce|auto]"
---

# Reply to Customer Review

## Invocation

Invoke the `reply-to-customer-review` skill and follow its full workflow.

## Arguments

- `<review text>`: The customer review to respond to (paste inline or provide after invocation)
- `--brand "Name"`: Business name to use in the response sign-off
- `--tone`: Response tone -- `formal`, `friendly`, or `casual` (default: professional-empathetic, mapped to `friendly`)

If invoked without arguments, prompts the user to paste a review.
- `--lang`: Force output language using ISO code (default: same language as the review)
- `--sector`: Force sector specialization -- `hospitality`, `ecommerce`, or `auto` for auto-detection (default: auto)

## Examples

```
/reply-to-customer-review "Camera sporca e personale scortese. Mai piu." --brand "Villa Serena" --tone friendly
/reply-to-customer-review The app crashes every time I try to checkout. Uninstalling.
/reply-to-customer-review --lang en "Prodotto arrivato rotto, assistenza inesistente"
/reply-to-customer-review "Amazing stay! The view was breathtaking and the host was incredibly welcoming." --brand "Casa Luna"
```

## What it does

1. Analyzes the review: language, sentiment, severity, key points, sector
2. Generates an adaptive response calibrated to the review's tone and content
3. Outputs the response (ready to copy), analysis summary, and operational suggestions
4. Accepts follow-up refinements: "more formal", "shorter", "in English", etc.
```

- [ ] **Step 2: Commit**

```bash
git add plugins/digital-marketing/commands/reply-to-customer-review.md
git commit -m "Add /reply-to-customer-review command"
```

## Chunk 2: Marketplace Registration

### Task 5: Update marketplace.json

**Files:**
- Modify: `.claude-plugin/marketplace.json` (digital-marketing plugin entry, lines 510-552; metadata.version at line 9)

- [ ] **Step 1: Add skill path to the digital-marketing skills array**

In `.claude-plugin/marketplace.json`, find the digital-marketing plugin's `skills` array (line 544-546) and add the new skill:

```json
"skills": [
  "./skills/brand-naming",
  "./skills/domain-hunter",
  "./skills/reply-to-customer-review"
],
```

- [ ] **Step 2: Add command path to the commands array**

Find the digital-marketing plugin's `commands` array (line 548-551) and add:

```json
"commands": [
  "./commands/seo-audit.md",
  "./commands/content-strategy.md",
  "./commands/brand-naming.md",
  "./commands/reply-to-customer-review.md"
],
```

- [ ] **Step 3: Add keywords**

Find the `keywords` array (line 518-534) and add review-related keywords:

```json
"keywords": [
  "seo",
  "content-marketing",
  "digital-marketing",
  "keyword-research",
  "content-strategy",
  "organic-traffic",
  "search-optimization",
  "brand",
  "naming",
  "branding",
  "domain-check",
  "trademark",
  "domain-hunter",
  "registrar",
  "domain-price",
  "review",
  "review-response",
  "reputation",
  "customer-feedback"
],
```

- [ ] **Step 4: Update the plugin description**

Update the digital-marketing plugin `description` (line 512) to mention review response:

```json
"description": "SEO optimization, content marketing, brand naming, domain hunting, and customer review response -- technical audits, keyword research, content strategy, brand naming, domain checks, trademark screening, and professional review reply generation with sentiment analysis",
```

- [ ] **Step 5: Bump plugin version**

Change `"version": "1.19.0"` to `"version": "1.20.0"` for the digital-marketing plugin (line 513).

- [ ] **Step 6: Bump marketplace metadata version**

Change `"version": "2.87.0"` to `"version": "2.88.0"` in the `metadata` section (line 9).

- [ ] **Step 7: Commit marketplace update**

```bash
git add .claude-plugin/marketplace.json
git commit -m "Register reply-to-customer-review skill in marketplace"
```

### Task 6: Final verification

- [ ] **Step 1: Verify all files exist**

```bash
ls -la plugins/digital-marketing/skills/reply-to-customer-review/SKILL.md
ls -la plugins/digital-marketing/skills/reply-to-customer-review/references/hospitality-patterns.md
ls -la plugins/digital-marketing/skills/reply-to-customer-review/references/ecommerce-patterns.md
ls -la plugins/digital-marketing/commands/reply-to-customer-review.md
```

- [ ] **Step 2: Verify marketplace.json is valid JSON**

```bash
python -c "import json; json.load(open('.claude-plugin/marketplace.json')); print('Valid JSON')"
```

- [ ] **Step 3: Verify the skill path exists in marketplace.json**

```bash
grep -c "reply-to-customer-review" .claude-plugin/marketplace.json
```

Expected: 3 matches (skill path, command path, description mention).
