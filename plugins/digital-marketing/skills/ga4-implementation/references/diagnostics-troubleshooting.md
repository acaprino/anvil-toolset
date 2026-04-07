# Diagnostics and troubleshooting

> Source: GA4 reports documentation, Microsoft Clarity and Google Search Console integration guides, and field-tested patterns for low-traffic sites as of 2025-2026.

This reference covers two related concerns: how to diagnose **why** a site does not generate the expected results (the "I have GA4 installed but no bookings come in" question), and how to fix **common errors** in the installation itself. It also covers complementary tools (Microsoft Clarity, Google Search Console) that fill GA4's blind spots.

## The fundamental diagnostic question: traffic or conversion?

After GA4 has been collecting for at least **2-4 weeks** (minimum 100 sessions for any pattern to be statistically meaningful), the first diagnostic step is to distinguish between two completely different scenarios.

### Scenario A: nobody visits the site (traffic problem)

Reports > Acquisition > Traffic Acquisition - check Users and Sessions over the last 30 days. If they are near zero, the problem is upstream of GA4: the site is not findable.

**What to do**:
- Check Google Search Console: is the site indexed? Search `site:example.com` on Google. Are pages crawled and shown in impressions?
- Check that Search Console is verified for the property and linked to GA4
- Check organic CTR and average position - if impressions exist but clicks don't, the title and meta description are not compelling enough
- Check Google Business Profile (for local businesses) - is it claimed, complete, with photos and reviews?
- Check inbound link sources - any references from OTAs (Booking.com, Airbnb, Tripadvisor for hospitality), industry directories, social profiles?

**Hand off to**: `seo-specialist` agent (in this same plugin) for a full SEO audit. Traffic problems are SEO problems and require their own tooling.

### Scenario B: people visit but don't convert (conversion problem)

Reports > Engagement > Events - confirm sessions exist (>100/month) but Key Events count is zero or very low.

**What to do**:
- Build a Funnel Exploration: Explore > Funnel Exploration. Map the path: Homepage → Detail/Photos → Contact/Booking page → Form Submission. Look for the drop-off step.
- Compare mobile vs desktop bounce rate (Reports > Tech > Tech Details, or build a comparison segment). If mobile bounce is 20+ points higher than desktop, the mobile UX is the problem.
- Check Reports > Engagement > Pages and Screens - do visitors ever reach the contact/booking page, or do they bounce from the homepage?
- Check Reports > Engagement > Landing Page - which pages are entry points? Is traffic landing on the wrong pages (blog posts, gallery) instead of the conversion pages?
- Install **Microsoft Clarity** (see below) - heatmaps and session recordings reveal **why** users don't convert in a way GA4 alone cannot.

**Hand off to**: `content-marketer` agent (for landing page copy and CTA) and/or the `premium-web-consultant` skill in the `frontend` plugin (for UX issues).

## Acquisition reports: traffic source interpretation

Reports > Acquisition > Traffic Acquisition shows where users come from. Common patterns and what they mean:

| Pattern | Likely meaning | Action |
|---|---|---|
| Almost all "Direct / (none)" | Site has no organic visibility; visits come from people who already know the URL | SEO audit, Search Console check, Google Business Profile work |
| Mostly "Organic Search" | Site ranks for some queries; check which queries in Search Console | Build on what works, identify content gaps |
| Mostly "Referral" | Most traffic comes from external links | Identify the referrers (which sites? are they relevant?) and double down |
| Mostly "Paid Search" with low conversion | Ads bring traffic but the landing page does not convert | Audit ad-to-landing-page message match, CRO work |
| Mostly "Social" | Traffic comes from Instagram/Facebook/etc. | Check social engagement quality - social traffic often has lower intent than organic |
| Even split, low volume | Decent variety but not enough total volume | Scale what works rather than diversifying further |

## Funnel Exploration

Build the funnel manually in GA4 > Explore > Funnel Exploration:

**Standard hospitality funnel**:
1. Step 1: page_view where `page_location` matches homepage
2. Step 2: page_view where `page_location` contains `/gallery` or `/foto` or `/details`
3. Step 3: page_view where `page_location` contains `/contact` or `/prenota`
4. Step 4: `generate_lead` event (form submission)

**Standard ecommerce funnel**:
1. `view_item_list`
2. `view_item`
3. `add_to_cart`
4. `begin_checkout`
5. `purchase`

**Standard SaaS funnel**:
1. Homepage page_view
2. Pricing page_view
3. Sign up page_view
4. `sign_up` event

For each step, GA4 shows the count, the drop-off rate, and the abandonment time. The **biggest drop-off step is the priority for optimization**. If 80% of users land on the homepage but only 20% reach the gallery, the homepage CTA or value proposition is the problem. If 80% reach the contact form but only 5% submit it, the form is the problem (too long, broken, asking for too much).

## Industry benchmarks

| Metric | Healthy range (hospitality/travel) | Red flag |
|---|---|---|
| Engagement rate | 50-60% | <40% |
| Average engagement time per session | 1-3 minutes | <30 seconds |
| Views per session | 2-4 | ~1 (single-page bounce) |
| Mobile/desktop bounce delta | <10 points | >20 points |

For ecommerce, the benchmarks differ:

| Metric | Healthy range (ecommerce) | Red flag |
|---|---|---|
| Engagement rate | 55-65% | <45% |
| Avg engagement time | 2-5 minutes | <60 seconds |
| Cart-to-purchase conversion rate | 1-3% (varies by vertical) | <0.5% |
| Add-to-cart-to-checkout rate | 30-50% | <15% |

These are rough guidelines - benchmark against historical data for the same site rather than against generic numbers when possible.

## Data thresholding for low-traffic sites

GA4 automatically hides report rows when user counts are too low to protect privacy. This is signaled by an **orange triangle** at the top of the report. Thresholding gets aggressive when:

- **Google Signals is enabled** (this is the biggest single factor)
- Demographic dimensions are used in the report
- Date ranges are narrow (last 7 days vs last 90 days)
- Segments fragment data into very small groups (typically <50 users)

**Workarounds for low-traffic sites**:

1. **Disable Google Signals** in Admin > Data Settings > Data Collection (recommended for EEA properties anyway for GDPR reasons)
2. **Use 30+ day windows** in reports
3. **Avoid demographic dimensions** (Age, Gender) in reports - they trigger thresholding
4. **Switch Reporting Identity to Device-based** in Admin > Reporting Identity (sacrifices some attribution accuracy for less thresholding)
5. **Avoid very narrow segments** - prefer fewer, broader segments

For sites under 1,000 sessions/month, thresholding is a constant concern. Below 100 sessions/month, GA4 reports are generally too sparse to be actionable - focus on Realtime, DebugView, and Microsoft Clarity instead.

## Microsoft Clarity: see what users actually do

Microsoft Clarity ([clarity.microsoft.com](https://clarity.microsoft.com)) is **completely free** with no traffic limits. It provides heatmaps (click and scroll) and session recordings. Where GA4 says "70% of users abandon the contact page", Clarity shows the **why**: rage clicks on broken buttons, users not finding the form because it's below the fold on mobile, hesitation on specific fields.

### Installation

1. Sign up at clarity.microsoft.com with a Microsoft account
2. Create a project for the site
3. Copy the embed snippet
4. Paste it in the `<head>` of every page (same way as GA4)
5. Optional: enable the Google Analytics integration (Clarity > Settings > Setup > Google Analytics) to link recordings to GA4 segments

Clarity and GA4 coexist without conflicts.

### GDPR consent

Clarity sets non-essential cookies (`_clck`, `_clsk`, `CLID`, `MUID`) and **requires consent** in Italy/EU just like GA4. From 31 October 2025, Microsoft applies consent signal requirements for EEA users on Clarity. Place Clarity in the same "Analytics" category in the CMP and ensure it is blocked until consent is given.

If using iubenda or Cookiebot autoblocking, this is automatic. With Orestbida, mark the Clarity script tag with `type="text/plain" data-category="analytics"`.

### What to look for in Clarity

- **Rage clicks**: rapid clicks in the same spot - usually a broken button or expected interactivity that doesn't exist
- **Dead clicks**: clicks on elements that don't respond - misleading visual cues (something looks clickable but isn't)
- **Excessive scrolling**: users scrolling up and down repeatedly - they can't find what they're looking for
- **Quick backs**: users navigating into a page and immediately back - the page didn't match their expectation
- **JavaScript errors**: Clarity logs JS errors in the recordings - useful for catching production bugs

## Google Search Console: the missing piece

Google Search Console measures what happens **before** the user arrives on the site: how many times pages appear in search results (impressions), the click-through rate (CTR), the average position, and crucially the **search queries** users typed (which GA4 cannot see). It also shows indexing status, crawling errors, Core Web Vitals, and mobile usability issues.

For a site that doesn't receive bookings, Search Console is the **first** tool to check whether the problem is that **Google doesn't find or doesn't show the site**.

### Verification

For a static HTML site, the simplest verification methods:

- **HTML file**: download the verification file from Search Console and upload it to the site root
- **Meta tag**: add `<meta name="google-site-verification" content="CODE">` to the homepage `<head>`
- **DNS TXT record**: add a TXT record to the domain's DNS (verifies the entire domain)
- **Google Tag**: if GA4 is already installed via the same Google account, Search Console can verify automatically

### Linking to GA4

1. GA4 > Admin > Product Links > Search Console Links > Link
2. Choose the Search Console property
3. Associate it with the web data stream
4. Confirm
5. Reports > Library > find the "Search Console" collection > publish it to make Search Console reports visible in GA4

After publishing, Reports > Search Console > Queries shows the queries users searched to find the site, with impressions, clicks, CTR, and average position. This is the only place to see search queries in GA4.

## Common installation errors checklist

In order of frequency, these are the errors that break GA4 installations:

### 1. Snippet on only one page (most common static-site error)

**Symptom**: Reports > Engagement > Pages and Screens shows only one page (typically the homepage). Tag Coverage report shows missing pages.

**Cause**: snippet pasted in `index.html` but not in other HTML files.

**Fix**: paste the snippet in every page, or centralize via a layout/include.

### 2. Double tracking (silent and insidious)

**Symptom**: every metric appears doubled. Pageviews are 2x what real traffic should be. Hard to detect because there are no errors - the data just looks "good" until you compare with another source.

**Cause**: both gtag.js and GTM injecting the same Measurement ID, or the same snippet pasted twice in the source.

**Detection**:
- Open DevTools > Network > filter `collect`. Each page_view should produce **one** request, not two.
- Search the page source (view-source:) for occurrences of `G-XXXXXXXXXX` and `GTM-XXXXXXX` - there should be exactly one of each.
- Use Tag Assistant - it warns about duplicate tags.

**Fix**: remove one of the two installations. Historical data corrupted by double tracking is **not recoverable**. Mark the recovery date and treat older data as suspect.

### 3. Snippet in the wrong position

**Symptom**: missing early page interactions, especially `session_start` and the first `page_view`.

**Cause**: snippet placed inside a `<div>`, after `</head>`, in `<body>` instead of `<head>`, or buried under many other scripts.

**Fix**: move the snippet to the very first script in `<head>`. The GTM noscript iframe goes immediately after `<body>`, never inside `<head>`.

### 4. Wrong Measurement ID

**Symptom**: data goes to the wrong property or to no property. Realtime is empty.

**Cause**: typo in the ID, extra spaces, or smart quotes (`"` and `"`) copied from a word processor instead of straight quotes (`"`).

**Fix**: always copy-paste the Measurement ID directly from GA4 > Admin > Data Streams. Verify the source byte-for-byte. A typed ID is a recipe for mistakes.

### 5. Internal traffic not excluded

**Symptom**: numbers look bigger than they should, especially for the homepage. Owner visits skew the data.

**Fix**: see "Internal traffic exclusion" in [`events-and-conversions.md`](events-and-conversions.md).

### 6. CMP loads after GTM

**Symptom**: tags fire before consent state is updated, Consent Mode v2 reports show all-denied even after acceptance.

**Cause**: the Consent Mode default block runs after the GTM snippet, or the CMP loader runs after GTM.

**Fix**: enforce the order in `<head>`:
1. Consent Mode v2 default block
2. CMP loader
3. GTM snippet

### 7. WordPress caching plugin stripping the snippet

**Symptom**: snippet works in admin / preview but not on the live front-end.

**Cause**: caching plugin (W3 Total Cache, WP Rocket, LiteSpeed, WP Super Cache) minifies or delays the GTM script away.

**Fix**: flush the cache. Add `googletagmanager.com` and `gtm.js` to the "do not minify" or "exclude from delay" list.

### 8. Hydration mismatch (Next.js, React)

**Symptom**: console warnings about hydration mismatch, inconsistent behavior between SSR and client.

**Cause**: GTM script injected via `dangerouslySetInnerHTML` in a server component without a unique `id` attribute.

**Fix**: use `next/script` or `@next/third-parties/google` `<GoogleTagManager>` instead.

### 9. Ad blockers blocking GA4

**Symptom**: missing data for some users (estimates: 10-30% of users in Italy block trackers).

**Cause**: uBlock Origin, Ghostery, Brave Shields, Firefox tracking protection, etc.

**Fix**: not directly fixable. Server-side GTM (sGTM) is the workaround for production-grade deployments. For most sites, accept the loss and focus on the data you can collect.

### 10. Wrong trigger type for the GA4 Google Tag

**Symptom**: tags fire in the wrong order, especially with Consent Mode.

**Cause**: trigger set to "All Pages" instead of "Initialization - All Pages".

**Fix**: in GTM, edit the GA4 Google Tag, change the trigger to **Initialization - All Pages** (under "Other" trigger types). Republish.

## Verification routine after every change

Whenever the GA4 or GTM configuration changes (new event, new tag, new variable), run this routine before considering the change live:

1. **Preview mode** in GTM - test the change with Tag Assistant before publishing
2. **Publish** the GTM container with a meaningful version name and description
3. **Realtime report** in GA4 - verify the new event appears within minutes
4. **DebugView** - verify the parameters are populated correctly
5. **Wait 24-48 hours** for standard reports to populate
6. **Standard reports** - verify the event count looks reasonable
7. **Test on mobile** - many issues only appear on mobile (touch targets, viewport, responsive layout)
8. **Test in incognito with no ad blocker** - the cleanest test environment
