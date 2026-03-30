# Grabber Development Plugin Implementation Plan

> **For agentic workers:** Use subagent-driven execution (if subagents available) or ai-tooling:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a `grabber-development` plugin with one expert agent (`grabber-architect`) and one skill with reference knowledge base for Python web scraping system design and implementation.

**Architecture:** Single agent + skill pattern (mirrors `ibkr-trading`). Agent body contains terse keyword-list expertise (~300 lines). Skill provides trigger rules and quick-reference decision trees. Reference doc holds the full 2025-2026 field guide.

**Tech Stack:** Markdown only (no build step, no runtime)

---

## File Structure

| File | Responsibility |
|------|---------------|
| `plugins/grabber-development/agents/grabber-architect.md` | Expert agent -- frontmatter + system prompt body |
| `plugins/grabber-development/skills/grabber-development/SKILL.md` | Skill activation -- trigger rules, decision trees, reference pointers |
| `plugins/grabber-development/skills/grabber-development/references/field-guide.md` | Full 2025-2026 Python web scraping field guide |
| `.claude-plugin/marketplace.json` | Plugin registration + version bumps |

---

### Task 1: Create the field guide reference

**Files:**
- Create: `plugins/grabber-development/skills/grabber-development/references/field-guide.md`

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p plugins/grabber-development/agents
mkdir -p plugins/grabber-development/skills/grabber-development/references
```

- [ ] **Step 2: Write field-guide.md**

Copy the full content from `C:\Users\alfio\Downloads\compass_artifact_wf-a7ee5543-f903-4bf9-93e0-c47b1f337d4f_text_markdown.md` into `plugins/grabber-development/skills/grabber-development/references/field-guide.md`.

No modifications needed -- this is the authoritative reference document.

- [ ] **Step 3: Commit**

```bash
git add plugins/grabber-development/skills/grabber-development/references/field-guide.md
git commit -m "add(grabber-development): field guide reference for 2025-2026 Python web scraping"
```

---

### Task 2: Create the SKILL.md

**Files:**
- Create: `plugins/grabber-development/skills/grabber-development/SKILL.md`

- [ ] **Step 1: Write SKILL.md**

```markdown
---
name: grabber-development
description: >
  Comprehensive Python web scraping knowledge base covering stealth browser automation (Patchright, Camoufox, Nodriver),
  TLS/HTTP fingerprint impersonation (curl_cffi, primp), anti-bot bypass (Cloudflare, DataDome, PerimeterX),
  CAPTCHA solving, proxy architecture, AI-assisted extraction (Crawl4AI, Firecrawl, ScrapeGraphAI),
  framework selection (Scrapy, Crawlee), rate limiting, and production observability.
  TRIGGER WHEN: building, optimizing, or debugging Python web scrapers.
  DO NOT TRIGGER WHEN: the task is outside the specific scope of this component.
---

# Python Web Scraping

Knowledge base for building production-grade Python web scraping systems. Covers the full stack from target assessment through production observability.

## When to Use

- Assessing a target site's protection level and choosing the right tools
- Discovering API endpoints via network traffic interception (Playwright/Patchright)
- Extracting data from rendered pages when no API is available
- Bypassing anti-bot systems (Cloudflare, DataDome, PerimeterX)
- Configuring TLS/HTTP fingerprint impersonation (curl_cffi, primp)
- Setting up stealth browser automation (Patchright, Camoufox, Nodriver)
- Designing proxy architecture with tiered escalation
- Solving CAPTCHAs programmatically (CapSolver, 2Captcha, playwright-captcha)
- Building production scraping pipelines (Scrapy, Crawlee)
- Adding rate limiting and observability to scraping systems

## Core Workflow

For every scraping task, follow this sequence:

### 1. Target Assessment
- Load the target URL in a stealth browser
- Identify: static HTML vs JS-rendered, anti-bot service (check for cf_clearance, DataDome cookies, px cookies), data volume needed, update frequency

### 2. Data Discovery (API-first)
- Navigate the site with Playwright/Patchright
- Intercept all network traffic via `page.on("request")` and `page.on("response")`
- Filter for XHR/fetch requests returning JSON, GraphQL, or structured data
- Classify: REST endpoints, WebSocket streams, GraphQL queries, SSE feeds
- If structured API found: generate curl_cffi replay code (skip browser entirely)

### 3. DOM Fallback (only if no API)
- If data exists only in rendered HTML: extract via CSS/XPath selectors
- Check for JSON-LD, microdata, or inline `<script>` JSON before parsing DOM
- For unstable DOM: use LLM-based extraction (Crawl4AI, ScrapeGraphAI) as final fallback
- Hybrid pattern: CSS selectors for stable fields ($0/extraction) + LLM for unstable fields (~$0.01/repair)

### 4. Stealth & Evasion (layer minimally)
- No protection: plain curl_cffi with `impersonate="chrome"` -- done
- Basic Cloudflare: Patchright persistent context + real Chrome channel
- Heavy Cloudflare/Turnstile: stealth browser + CAPTCHA solver + residential proxy
- DataDome: Camoufox + ghost-cursor behavioral simulation + residential proxy
- PerimeterX: organic navigation pattern + session warming + residential proxy

### 5. Production Hardening
- Rate limiting: pyrate-limiter v4 with Redis backend for distributed scraping
- Proxy rotation: tiered escalation (datacenter -> ISP -> residential -> mobile)
- Observability: structlog + Prometheus + Grafana
- Error handling: retry with backoff, proxy failover, session rotation

## Tool Selection Quick Reference

| Target Profile | HTTP Client | Browser | Framework |
|---------------|-------------|---------|-----------|
| No JS, no protection | curl_cffi | none | Scrapy / httpx |
| JS-rendered, no protection | none | Playwright | Crawlee |
| Basic Cloudflare | curl_cffi + cf_clearance | Patchright (for cookie) | Scrapy |
| Heavy Cloudflare | none | Patchright persistent | Crawlee |
| DataDome | none | Camoufox + ghost-cursor | custom |
| PerimeterX | none | Nodriver / Patchright | custom |
| AI extraction needed | none | Crawl4AI / Firecrawl | standalone |

## Proxy Tier Quick Reference

| Tier | Type | Price Range | Use When |
|------|------|-------------|----------|
| 0 | No proxy | free | Unprotected targets, development |
| 1 | Datacenter | $0.10-0.50/GB | Light protection, high volume |
| 2 | ISP (static residential) | $0.53-1.47/IP | Account management, login flows |
| 3 | Residential | $0.49-8.00/GB | Anti-bot bypass, geo-targeting |
| 4 | Mobile | $4-13/GB | Highest trust, last resort |

## Reference Materials

- `field-guide.md` -- full 2025-2026 Python web scraping field guide covering browser stealth, TLS fingerprinting, behavioral biometrics, anti-bot bypass, CAPTCHA solving, proxy landscape, frameworks, AI-assisted scraping, GraphQL reverse engineering, rate limiting, and observability
```

- [ ] **Step 2: Commit**

```bash
git add plugins/grabber-development/skills/grabber-development/SKILL.md
git commit -m "add(grabber-development): skill with trigger rules and decision trees"
```

---

### Task 3: Create the agent

**Files:**
- Create: `plugins/grabber-development/agents/grabber-architect.md`

- [ ] **Step 1: Write grabber-architect.md**

The agent body should follow the terse keyword-list style of `ibkr-architect.md`. Target ~300 lines. The body must cover these sections with concrete, actionable knowledge (not pointers to the reference -- the agent must be self-contained for common decisions):

1. **Core Knowledge header** with subsections:
   - Target Assessment (static vs JS, anti-bot tier detection, volume/frequency)
   - Data Discovery Workflow (Playwright intercept -> classify -> replay or DOM)
   - Tool Selection Matrix (decision tables like ibkr-architect)
   - Stealth Stack (TLS: JA4+, HTTP/2 SETTINGS, curl_cffi impersonation; Browser: Patchright, Camoufox, Nodriver; Behavioral: mouse, scroll, timing)
   - Anti-Bot Bypass (per-service: Cloudflare cf_clearance/Turnstile, DataDome signals/approach, PerimeterX delayed enforcement)
   - CAPTCHA Solving (CapSolver vs 2Captcha, playwright-captcha integration, cost)
   - Proxy Architecture (tiered escalation, provider picks with pricing, pyrate-limiter)
   - Extraction Patterns (CSS stable, LLM fallback, hybrid cost, Pydantic schema)
   - Production Stack (rate limiting, observability, error handling)
   - Cost Awareness (proxy $/GB, CAPTCHA $/1K, managed API tradeoffs)

2. **Decision Frameworks** section with tables (like ibkr-architect):
   - Tool Selection (target profile -> recommended stack)
   - Proxy Tier (protection level -> proxy type)
   - Extraction Strategy (data availability -> extraction method)
   - Framework Choice (use case -> Scrapy vs Crawlee vs custom)

3. **Behavioral Rules** section:
   - Always assess target before choosing tools
   - Always try API interception before DOM scraping
   - Always use minimal evasion (lightest layer that works)
   - Always impersonate a real browser TLS fingerprint (never raw httpx/requests against protected targets)
   - Track per-request cost across proxy + CAPTCHA + compute
   - Warn when user approaches DataDome/PerimeterX (no universal bypass)
   - Recommend managed Web Unlocker APIs when build cost exceeds buy cost
   - Use Pydantic models for extracted data validation
   - Default to polite scraping (respect rate limits, use delays)

4. **Common Patterns** section with code blocks:
   - Playwright network interception (request/response listeners, filtering XHR)
   - curl_cffi with TLS impersonation (basic GET, async session with proxy)
   - Patchright stealth setup (persistent context, real Chrome channel)
   - Distributed rate limiting (pyrate-limiter + Redis)

5. **Synergies** section:
   - python-development:async-python-patterns -- asyncio for async scraping
   - python-development:python-architect -- system architecture for scraping pipelines
   - opentelemetry:opentelemetry -- distributed tracing for scraping observability

Frontmatter:

```yaml
---
name: grabber-architect
description: >
  Expert in Python web scraping system design, implementation, and anti-bot evasion.
  Covers stealth browser automation (Patchright, Camoufox, Nodriver), TLS/HTTP fingerprint
  impersonation (curl_cffi, primp), anti-bot bypass (Cloudflare, DataDome, PerimeterX),
  CAPTCHA solving, proxy strategy, AI-assisted extraction (Crawl4AI, Firecrawl, ScrapeGraphAI),
  framework selection (Scrapy, Crawlee), rate limiting, and observability.
  TRIGGER WHEN: building scrapers, bypassing anti-bot, choosing scraping tools, designing proxy
  architecture, reverse-engineering APIs, or extracting data from websites
  DO NOT TRIGGER WHEN: the task is outside the specific scope of this component.
model: opus
color: green
tools: Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch
---
```

- [ ] **Step 2: Commit**

```bash
git add plugins/grabber-development/agents/grabber-architect.md
git commit -m "add(grabber-development): grabber-architect expert agent"
```

---

### Task 4: Register in marketplace.json

**Files:**
- Modify: `.claude-plugin/marketplace.json` (add plugin entry, bump metadata.version)

- [ ] **Step 1: Add plugin entry**

Add the following entry to the `plugins` array in `.claude-plugin/marketplace.json`, after the last existing plugin (docker):

```json
,
{
  "name": "grabber-development",
  "source": "./plugins/grabber-development",
  "description": "Expert Python web scraping -- target assessment, stealth browser automation, TLS fingerprint impersonation, anti-bot bypass, proxy architecture, API discovery, DOM extraction, and production observability",
  "version": "1.0.0",
  "author": {
    "name": "Alfio"
  },
  "license": "MIT",
  "keywords": [
    "scraping",
    "web-scraping",
    "crawler",
    "anti-bot",
    "stealth",
    "proxy",
    "captcha",
    "extraction",
    "playwright",
    "curl-cffi"
  ],
  "category": "development",
  "strict": false,
  "agents": [
    "./agents/grabber-architect.md"
  ],
  "skills": [
    "./skills/grabber-development"
  ]
}
```

- [ ] **Step 2: Bump metadata.version**

Change `"version": "4.5.0"` to `"version": "4.6.0"` in the `metadata` section.

- [ ] **Step 3: Commit**

```bash
git add .claude-plugin/marketplace.json
git commit -m "add(grabber-development): register plugin in marketplace v4.6.0"
```

---

### Task 5: Update CLAUDE.md plugin count

**Files:**
- Modify: `CLAUDE.md` (update plugin count from 38 to 39)

- [ ] **Step 1: Update count**

In CLAUDE.md, change `38 plugins:` to `39 plugins:` and add `grabber-development` to the list.

- [ ] **Step 2: Commit with marketplace**

```bash
git add CLAUDE.md
git commit -m "maintain(docs): add grabber-development to plugin list"
```
