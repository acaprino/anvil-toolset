# Reply to Customer Review - Skill Design

**Date:** 2026-03-19
**Plugin:** digital-marketing
**Type:** Skill + Command

## Overview

A skill that generates professional, empathetic, on-brand responses to online customer reviews. Analyzes sentiment, detects severity, adapts tone, and provides operational suggestions. Universal by default, with sector-specific specializations for hospitality and e-commerce/app.

## File Structure

```
plugins/digital-marketing/
  skills/
    reply-to-customer-review/
      SKILL.md
      references/
        hospitality-patterns.md
        ecommerce-patterns.md
  commands/
    reply-to-customer-review.md
```

## Skill Flow

### Step 1 - Analysis

When the user pastes a review, the skill performs:

- **Language detection** -- identify the language of the review
- **Sentiment classification** -- positive / neutral / negative / mixed
- **Key points extraction** -- what topics the reviewer mentions (service, cleanliness, price, product, shipping, etc.)
- **Severity assessment** (for negative reviews):
  - Unfounded complaint -- no real issue, emotional venting
  - Minor real problem -- real issue but limited impact
  - Major real problem -- serious issue requiring immediate attention
  - Abusive/threatening -- flag for platform reporting, generate minimal professional response or recommend not responding publicly
- **Sector detection** -- hospitality, e-commerce/app, or generic (auto-detect from context, override via --sector)

### Edge Cases

- **Star-only reviews (no text):** Ask the user for the star rating and generate a brief, generic acknowledgment response appropriate to the sentiment implied by the rating.
- **Very short or ambiguous reviews (under 5 words):** Flag the ambiguity in the Analysis section. Generate a brief, neutral-positive response that invites the customer to share more details.
- **Abusive/threatening content:** Flag for potential platform reporting. Generate a minimal, professional response or recommend not responding publicly. Never mirror hostility.
- **Mixed-language reviews:** Respond in the dominant language. Note the secondary language in the Analysis section.

### Step 2 - Response Generation

- Apply user-specified tone or default (professional-empathetic)
- Use business name if provided via --brand
- Respond in the same language as the review (override via --lang)
- For negative reviews, choose approach adaptively based on severity:
  - **Unfounded/emotional complaints** -- diplomatic-defensive: acknowledge feelings, provide context, invite private contact
  - **Real problems** -- empathetic-proactive: apologize, propose concrete solution/compensation, show corrective action
- Load sector-specific reference patterns when applicable

### Step 3 - Output

Three sections:

1. **Response** -- ready-to-copy text for the review platform
2. **Analysis** -- sentiment detected, key points identified, flags (e.g., "mentions hygiene issue - may require internal follow-up")
3. **Operational Suggestions** -- internal actions recommended (e.g., "flag to cleaning team", "offer discount on next stay", "open support ticket", "check product batch")

The user can then request variants: "more formal", "shorter", "in English", etc.

## Command: /reply-to-customer-review

### Parameters (optional, inline)

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--brand` | string | none | Business name to use in the response |
| `--tone` | `formal`, `friendly`, `casual` | professional-empathetic | Override response tone |
| `--lang` | language code (en, it, fr, etc.) | same as review | Force output language |
| `--sector` | `hospitality`, `ecommerce`, `auto` | `auto` | Force sector specialization |

### Usage Examples

```
/reply-to-customer-review "Camera sporca e personale scortese. Mai piu." --brand "Villa Serena" --tone friendly

/reply-to-customer-review The app crashes every time I try to checkout. Uninstalling.

/reply-to-customer-review --lang en "Prodotto arrivato rotto, assistenza inesistente"
```

If invoked without arguments, asks the user to paste the review.

## Reference Files

### hospitality-patterns.md

- Typical vocabulary: stay, check-in, cleanliness, location, host, comfort, amenities, noise
- Recurring categories: cleanliness, listing accuracy, communication, location, value for money
- Platforms: Airbnb, Booking, Google Maps, Tripadvisor, Vrbo
- Typical operational actions: flag to cleaning team, update listing description, contact guest privately, offer discount on next stay, report maintenance issue
- Example reviews and model responses for each severity level

### ecommerce-patterns.md

- Typical vocabulary: shipping, return, product quality, customer support, bug, crash, update, refund
- Recurring categories: product quality, shipping/delivery, customer service, app functionality, price
- Platforms: Amazon, Trustpilot, App Store, Google Play, eBay
- Typical operational actions: open support ticket, report bug to dev team, initiate return procedure, verify product batch, escalate to shipping partner
- Example reviews and model responses for each severity level

## Command Frontmatter

```yaml
description: Reply to a customer review with sentiment analysis, adaptive tone, and operational suggestions
argument-hint: '"<review text>" [--brand <name>] [--tone formal|friendly|casual] [--lang <code>] [--sector hospitality|ecommerce|auto]'
```

## Trigger Description

Skill description for marketplace registration:

> "Generate professional, empathetic, on-brand responses to online customer reviews. Analyzes sentiment, detects severity, adapts tone, and provides operational suggestions. Supports hospitality (Airbnb, Booking, Tripadvisor) and e-commerce/app (Amazon, App Store, Trustpilot) with sector-specific patterns. Trigger on: review, recensione, reply to review, respond to review, risposta recensione, customer review, negative review, bad review, rispondere alla recensione, gestione recensioni, review response."

Note: Italian trigger keywords are intentionally included because the skill's core use case is multilingual -- users paste reviews in any language and may describe the task in their own language.

## Marketplace Registration

- Add skill path `./skills/reply-to-customer-review` to the digital-marketing plugin `skills` array in marketplace.json
- Add command path `./commands/reply-to-customer-review.md` to the digital-marketing plugin `commands` array
- Add keywords: `"review"`, `"review-response"`, `"reputation"`, `"customer-feedback"` to the plugin `keywords` array
- Bump digital-marketing plugin version
- Bump metadata.version
