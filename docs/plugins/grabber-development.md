# Grabber Development Plugin

> Expert Python web scraping -- target assessment, stealth browser automation, TLS fingerprint impersonation, anti-bot bypass, proxy architecture, API discovery, DOM extraction, and production observability.

## Agents

### `grabber-architect`

Expert in Python web scraping system design, implementation, and anti-bot evasion.

| | |
|---|---|
| **Model** | opus |
| **Color** | pink |
| **Tools** | Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch |
| **Use for** | Building scrapers, bypassing anti-bot, choosing scraping tools, designing proxy architecture, reverse-engineering APIs |

**Core knowledge areas:**
- **Target Assessment** - Static HTML vs JS-rendered vs anti-bot protected, volume planning
- **Data Discovery** - API-first approach: intercept network traffic before scraping DOM
- **TLS/HTTP Fingerprinting** - JA4+, HTTP/2 fingerprinting, curl_cffi/primp impersonation
- **Stealth Browsers** - Patchright (Chromium), Camoufox (Firefox), Nodriver (Chrome)
- **Anti-Bot Bypass** - Cloudflare (JS challenge, Turnstile), DataDome, PerimeterX/HUMAN
- **CAPTCHA Solving** - CapSolver, CapMonster, 2Captcha, playwright-captcha
- **Proxy Architecture** - Tiered escalation (datacenter -> ISP -> residential -> mobile)
- **Extraction** - CSS/XPath selectors, JSON-LD, LLM-based (Crawl4AI, ScrapeGraphAI, Firecrawl)
- **Frameworks** - Scrapy 2.14, Crawlee, Crawl4AI, Firecrawl, ScrapeGraphAI
- **Rate Limiting & Observability** - pyrate-limiter, Prometheus, Grafana, Spidermon

**Decision frameworks included:**
- Tool selection matrix (target profile -> HTTP client + browser + framework)
- Proxy tier selection (protection level -> tier + provider)
- Extraction strategy (data location -> method + cost + stability)
- Framework choice (use case -> framework + rationale)

---

## Skills

### `grabber-development`

Comprehensive Python web scraping knowledge base covering the full stack from target assessment through production observability.

| | |
|---|---|
| **Trigger** | Building, optimizing, or debugging Python web scrapers |

**Core workflow:**

1. **Target Assessment** - Identify protection level, data volume, update frequency
2. **Data Discovery (API-first)** - Intercept network traffic, find REST/GraphQL/WebSocket endpoints
3. **DOM Fallback** - CSS/XPath selectors, JSON-LD, LLM extraction as last resort
4. **Stealth & Evasion** - Layer minimally: plain curl_cffi -> Patchright -> Camoufox + ghost-cursor
5. **Production Hardening** - Rate limiting, proxy rotation, observability, error handling

**Quick reference tables:**

| Target Profile | HTTP Client | Browser | Framework |
|---------------|-------------|---------|-----------|
| No JS, no protection | curl_cffi | none | Scrapy / httpx |
| JS-rendered, no protection | none | Playwright | Crawlee |
| Basic Cloudflare | curl_cffi + cf_clearance | Patchright | Scrapy |
| Heavy Cloudflare | none | Patchright persistent | Crawlee |
| DataDome | none | Camoufox + ghost-cursor | custom |
| PerimeterX | none | Nodriver / Patchright | custom |

**Reference docs included:**

| Reference | Content |
|-----------|---------|
| `field-guide.md` | Full 2025-2026 Python web scraping field guide -- browser stealth, TLS fingerprinting, behavioral biometrics, anti-bot bypass, CAPTCHA solving, proxy landscape, frameworks, AI-assisted scraping, GraphQL reverse engineering |

---

**Related:** [python-development](python-development.md) (async patterns, system architecture) | [opentelemetry](opentelemetry.md) (distributed tracing for scraping observability) | [playwright-skill](playwright-skill.md) (browser automation)
