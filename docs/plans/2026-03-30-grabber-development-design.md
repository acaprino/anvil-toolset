# Grabber Development Plugin -- Design Spec

**Date:** 2026-03-30
**Plugin:** `grabber-development`
**Category:** development
**Pattern:** single agent + skill with reference knowledge base (like `ibkr-trading`)

---

## Overview

Expert plugin for designing and building production Python web scraping systems. Covers the full stack: target assessment, tool selection, stealth/anti-bot evasion, proxy architecture, data discovery, extraction strategies, rate limiting, and observability. Based on the 2025-2026 Python web scraping field guide.

## Plugin Structure

```
plugins/grabber-development/
  agents/
    grabber-architect.md
  skills/
    grabber-development/
      SKILL.md
      references/
        field-guide.md
```

## Agent: `grabber-architect`

### Frontmatter

- **name:** grabber-architect
- **model:** opus
- **color:** green
- **tools:** Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch

### Trigger Description

Expert in Python web scraping system design, implementation, and anti-bot evasion. Covers stealth browser automation (Patchright, Camoufox, Nodriver), TLS/HTTP fingerprint impersonation (curl_cffi, primp), anti-bot bypass (Cloudflare, DataDome, PerimeterX), CAPTCHA solving, proxy strategy, AI-assisted extraction (Crawl4AI, Firecrawl, ScrapeGraphAI), framework selection (Scrapy, Crawlee), rate limiting, and observability.

TRIGGER WHEN: building scrapers, bypassing anti-bot, choosing scraping tools, designing proxy architecture, reverse-engineering APIs, or extracting data from websites.
DO NOT TRIGGER WHEN: the task is outside the specific scope of this component.

### Agent Body Sections (~250-350 lines, terse keyword-list style)

1. **Target assessment** -- analyze target site: static vs JS-rendered, anti-bot tier (none/basic Cloudflare/DataDome/PerimeterX), data volume, update frequency
2. **Tool selection matrix** -- decision tree mapping target characteristics to optimal library stack
3. **Data discovery & extraction strategy** -- the core workflow:
   - Phase 1 (API-first): navigate target with Playwright/Patchright, intercept all network traffic (REST, WebSocket, GraphQL, SSE), classify responses, identify endpoints with structured data
   - Phase 2 (DOM fallback): if data not available via intercepted requests, extract from rendered page via CSS/XPath selectors, JSON-LD/microdata embedded in page, or LLM-based extraction as final fallback
   - Principle: always prefer API replay over DOM scraping (faster, more stable, less resource-intensive)
4. **Stealth stack** -- TLS fingerprinting (JA4+, HTTP/2 SETTINGS), browser automation stealth (Patchright, Camoufox, Nodriver, rebrowser-patches), behavioral simulation (mouse dynamics, scroll patterns, timing)
5. **Anti-bot bypass tiers** -- per-service strategies for Cloudflare (cf_clearance, Turnstile), DataDome (behavioral + residential), PerimeterX (delayed enforcement patterns)
6. **CAPTCHA solving** -- AI-native (CapSolver) vs human-powered (2Captcha), browser integration (playwright-captcha), cost comparison
7. **Proxy architecture** -- tiered escalation: datacenter -> ISP -> residential -> mobile, provider recommendations with pricing, distributed rate limiting with pyrate-limiter + Redis
8. **Extraction patterns** -- CSS selectors for stable fields, LLM fallback for unstable DOM, hybrid cost optimization ($0 selectors + ~$0.01 LLM repair), Pydantic schema-driven extraction
9. **Production stack** -- rate limiting (pyrate-limiter v4, AutoThrottle), observability (structlog + Prometheus + Grafana), error handling, retry strategies
10. **Cost awareness** -- proxy pricing tiers, CAPTCHA costs, managed API tradeoffs (Bright Data Web Unlocker, ZenRows), build-vs-buy decision framework

### Key Principles

- API-first, DOM-fallback: always intercept network traffic before scraping rendered pages
- Minimal evasion: use the lightest stealth layer that works (don't use residential proxies when datacenter suffices)
- Assess before building: always analyze the target's protection level before choosing tools
- Cost-conscious: track per-request costs across proxy, CAPTCHA, and compute

## Skill: `grabber-development`

### SKILL.md

- Trigger rules (when to activate the skill)
- Quick-reference decision tree: target assessment -> tool selection -> extraction strategy
- Pointers to `references/field-guide.md` for deep knowledge
- Key workflow: discover (intercept traffic) -> assess (API vs DOM) -> implement (optimal tool) -> harden (stealth + proxies) -> monitor (observability)

### references/field-guide.md

The full 2025-2026 Python web scraping field guide, covering:
- Browser automation stealth (Patchright, Camoufox, Nodriver, rebrowser-patches)
- TLS fingerprinting (JA4+, curl_cffi, primp, HTTP/2)
- Behavioral biometrics (mouse, keyboard, scroll, timing)
- Anti-bot bypass (Cloudflare, DataDome, PerimeterX)
- CAPTCHA solving (CapSolver, 2Captcha, playwright-captcha)
- Proxy landscape (residential, mobile, ISP, Web Unlockers)
- Frameworks (Scrapy 2.14, Crawlee, Scrapling, Crawl4AI)
- AI-assisted scraping (ScrapeGraphAI, Firecrawl, Browser Use, Skyvern)
- GraphQL reverse engineering (InQL, Clairvoyance, mitmproxy)
- Rate limiting and observability (pyrate-limiter, Prometheus, Grafana)

Note: legal/compliance sections are included in the reference for completeness but the agent does not proactively advise on legal matters.

## Marketplace Registration

```json
{
  "name": "grabber-development",
  "source": "./plugins/grabber-development",
  "description": "Expert Python web scraping -- target assessment, stealth browser automation, TLS fingerprint impersonation, anti-bot bypass, proxy architecture, API discovery, DOM extraction, and production observability",
  "version": "1.0.0",
  "author": { "name": "Alfio" },
  "license": "MIT",
  "keywords": ["scraping", "web-scraping", "crawler", "anti-bot", "stealth", "proxy", "captcha", "extraction", "playwright", "curl-cffi"],
  "category": "development",
  "strict": false,
  "agents": ["./agents/grabber-architect.md"],
  "skills": ["./skills/grabber-development"]
}
```
