# Events, conversions, audiences

> Source: GA4 official event documentation, GTM trigger and tag reference, and the GA4 Key Events / Google Ads Conversion Actions integration as of 2025-2026.

This reference covers the measurement layer: which events to track, how to configure them in GTM, how to register custom dimensions, how to mark Key Events, how to create remarketing audiences, and how to link to Google Ads.

## Enhanced Measurement: what GA4 tracks automatically

When the data stream is created with Enhanced Measurement enabled (default), GA4 automatically tracks the following events without any custom configuration:

| Event | Trigger | Notes |
|---|---|---|
| `page_view` | Every page load | Includes SPA virtual page views if the GTM Initialization trigger is set up correctly |
| `session_start` | First page of a session | Auto |
| `first_visit` | First-ever visit by a user | Auto |
| `user_engagement` | After 10 seconds on page or interaction | Auto |
| `scroll` | At 90% page scroll | Toggle individually in stream settings |
| `click` (outbound) | Click on a link to a different domain | Toggle individually |
| `view_search_results` | URL contains a search query parameter | Toggle individually, customizable parameter |
| `video_start`, `video_progress`, `video_complete` | Embedded YouTube videos | Toggle individually, requires JS API enabled iframe |
| `file_download` | Click on a link with a known file extension | Toggle individually |

These cover the basics. For actionable conversion data, layer custom events on top.

## Custom events via GTM

Custom events are configured by creating a GTM **trigger** that fires on a specific user action and a GTM **tag** of type "Google Analytics: GA4 Event" that pushes the event to GA4 with parameters.

### Pattern 1: click on a button (e.g. "Book", "Reserve")

**Trigger**: Click - All Elements
- Trigger type: Click - All Elements
- This trigger fires on: Some Clicks
- Condition: `Click Text` contains `Prenota` (or `Book`, `Reserve`, depending on the language)
- Optional: also match on `Click Classes` if the button has a unique CSS class

**Tag**: GA4 Event
- Tag type: Google Analytics: GA4 Event
- Configuration tag: select the existing GA4 Google Tag (or measurement ID directly)
- Event name: `book_now_click`
- Event parameters:
  - `button_text` = `{{Click Text}}`
  - `page_path` = `{{Page Path}}` (optional)

### Pattern 2: WhatsApp link click

**Trigger**: Click - Just Links
- Trigger type: Click - Just Links
- Wait for tags: yes (recommended)
- This trigger fires on: Some Link Clicks
- Condition: `Click URL` contains `wa.me`

**Tag**: GA4 Event
- Event name: `whatsapp_click`
- Parameters: `link_url` = `{{Click URL}}`

### Pattern 3: phone number click (`tel:`)

**Trigger**: Click - Just Links
- Condition: `Click URL` starts with `tel:`

**Tag**: GA4 Event
- Event name: `phone_click`
- Parameters: `phone_number` = `{{Click URL}}` (optional, will include `tel:` prefix)

### Pattern 4: email click (`mailto:`)

**Trigger**: Click - Just Links
- Condition: `Click URL` starts with `mailto:`

**Tag**: GA4 Event
- Event name: `email_click`

### Pattern 5: form submission (contact form)

Two reliable approaches depending on the form:

**Approach A: native HTML form with thank-you page redirect**

**Trigger**: Page View
- Condition: `Page Path` equals `/grazie` (or `/thank-you`)

**Tag**: GA4 Event
- Event name: `generate_lead`
- Parameters: `method` = `contact_form`

**Approach B: AJAX form without redirect**

The form library must push to the dataLayer on success:

```javascript
// In the form success callback
dataLayer.push({
  event: 'form_submit_success',
  form_name: 'contact'
});
```

**Trigger**: Custom Event
- Event name: `form_submit_success`

**Tag**: GA4 Event
- Event name: `generate_lead`
- Parameters: `method` = `contact_form`, `form_name` = `{{DLV - form_name}}` (a Data Layer Variable)

### Pattern 6: external OTA / booking platform click

**Trigger**: Click - Just Links
- Condition: `Click URL` contains `booking.com` OR `Click URL` contains `airbnb`

**Tag**: GA4 Event
- Event name: `booking_platform_click`
- Parameters: `platform` = a Custom JavaScript Variable that returns `'booking'` or `'airbnb'` based on the URL

## Custom dimensions

Custom event parameters do **not** appear automatically in GA4 reports. Each parameter that should appear as a dimension in reports must be registered manually:

1. GA4 > Admin > Data Display > Custom Definitions
2. Click "Create custom dimension"
3. Dimension name: human-readable name shown in reports (e.g. "Button Text")
4. Scope: **Event** (for event parameters; User scope is for user properties)
5. Description: short note about what the parameter captures
6. Event parameter: the **exact** parameter name used in the GTM tag (e.g. `button_text`) - case-sensitive

After registration it takes up to 24 hours for the dimension to appear in reports. Existing event data with that parameter is **not** retroactively populated - the dimension only sees values collected after registration.

GA4 has a hard limit of **50 event-scoped custom dimensions** and **25 user-scoped** per property. Plan accordingly: not every parameter needs to be a registered dimension. Use registration only for parameters you need to filter, group, or break down by in reports.

## Key Events (formerly Conversions)

In March 2024 Google renamed "Conversions" to **"Key Events"** in GA4. The term "Conversion" is now reserved exclusively for Google Ads. Functionally they are the same: a flag on an event that tells GA4 to count it as a primary success metric.

To mark an event as a Key Event:

1. GA4 > Admin > Data Display > Events
2. Find the event in the list (it appears only after firing at least once)
3. Toggle "Mark as key event" on

Once marked, the event count appears in the Key Events column of Acquisition reports, and the event becomes importable as a Conversion Action in linked Google Ads accounts.

**Suggested Key Events for a service or hospitality business**:

- `generate_lead` (contact form submission) - primary
- `book_now_click` (click on the booking button) - primary
- `whatsapp_click` - primary
- `email_click`, `phone_click` - primary
- `booking_platform_click` - secondary (micro-conversion - the user left to a third-party platform)

For ecommerce, the standard primary Key Event is `purchase`. Secondary Key Events: `begin_checkout`, `add_payment_info`, `add_to_cart`.

## GA4 recommended events for ecommerce

GA4 has a fixed list of "recommended events" that map to standard reports. Using these names instead of inventing custom ones unlocks the built-in Monetization and Funnel reports.

| Event | When to fire | Required parameters |
|---|---|---|
| `view_item_list` | User views a product list / category | `item_list_id`, `item_list_name`, `items[]` |
| `select_item` | User clicks a product in a list | `item_list_id`, `item_list_name`, `items[]` |
| `view_item` | User views a product detail page | `currency`, `value`, `items[]` |
| `add_to_cart` | User adds product to cart | `currency`, `value`, `items[]` |
| `view_cart` | User views the cart | `currency`, `value`, `items[]` |
| `remove_from_cart` | User removes from cart | `currency`, `value`, `items[]` |
| `begin_checkout` | User starts checkout | `currency`, `value`, `items[]`, `coupon` |
| `add_payment_info` | User submits payment info | `currency`, `value`, `payment_type`, `items[]` |
| `add_shipping_info` | User submits shipping info | `currency`, `value`, `shipping_tier`, `items[]` |
| `purchase` | Order completed | `currency`, `value`, `transaction_id`, `items[]`, `tax`, `shipping`, `coupon` |
| `refund` | Order refunded | `currency`, `value`, `transaction_id`, `items[]` |

The `items[]` array structure:

```javascript
dataLayer.push({
  event: 'purchase',
  ecommerce: {
    transaction_id: 'T-12345',
    value: 199.99,
    currency: 'EUR',
    tax: 35.99,
    shipping: 9.99,
    items: [
      {
        item_id: 'SKU-001',
        item_name: 'Product Name',
        item_brand: 'Brand',
        item_category: 'Category',
        item_variant: 'Red',
        price: 99.99,
        quantity: 2
      }
    ]
  }
});
```

In GTM, configure a tag of type "GA4 Event" with event name `purchase`, then in More Settings > Ecommerce, enable "Send Ecommerce data" and set the data source to "Data Layer". GTM will pick up the `ecommerce` object automatically.

For non-ecommerce sites, the recommended events `login`, `sign_up`, `search`, `share` are also worth using when they apply.

## Audiences for remarketing

Audiences in GA4 populate **only from the date of creation forward**. They are not retroactive. Create them as soon as the property is set up so data accumulates before Google Ads campaigns launch.

**Standard audience set** to create on day one:

| Audience | Definition | Membership duration |
|---|---|---|
| All visitors 30 days | `session_start` event triggered | 30 days |
| All visitors 180 days | `session_start` event triggered | 180 days |
| Engaged visitors | session duration > 60s AND pageviews > 2 | 90 days |
| Visitors to booking page | `page_location` contains `/prenota` or `/book` | 30 days |
| Visitors to gallery | `page_location` contains `/gallery` or `/foto` | 30 days |
| High-intent no-conversion | fired `book_now_click` OR `whatsapp_click` but NOT `generate_lead` | 30 days |
| Cart abandoners (ecommerce) | fired `begin_checkout` but NOT `purchase` | 30 days |
| Past purchasers (ecommerce) | fired `purchase` | 540 days (max) |

To create an audience:

1. GA4 > Admin > Data Display > Audiences
2. Click "New Audience" > "Create a custom audience"
3. Set the conditions, the membership duration, and the audience name
4. Optionally create an audience trigger (a custom event that fires when a user joins the audience)

Once GA4 is linked to Google Ads, audiences automatically export to the Google Ads Audience Manager and become available for campaign targeting.

## Google Ads link

Even before launching campaigns, link GA4 to Google Ads so the integration is ready:

1. GA4 > Admin > Product Links > Google Ads Links > Link
2. Choose the Google Ads account (the linker must have admin on both sides)
3. Enable "Personalized advertising"
4. Submit

Once linked:
- GA4 sees Google Ads cost data in Acquisition reports
- Audiences auto-export to Google Ads Audience Manager
- Key Events become importable as Conversion Actions in Google Ads

To import Key Events as Conversion Actions: Google Ads > Goals > Conversions > New conversion action > Import > Google Analytics 4 properties > Web. Select the events to import. Each becomes a Conversion Action available for Smart Bidding.

## Enhanced Conversions

Enhanced Conversions improve attribution by matching first-party hashed user data (email, phone) submitted in forms or checkouts with Google's user data. To enable:

1. GA4 > Admin > Data Streams > select the stream > Configure tag settings > Show all > Allow user-provided data capabilities > **toggle ON**
2. In GTM, on the GA4 Google Tag or on the conversion event tag, configure user-provided data with selectors or variables that point to the email and phone fields

This becomes particularly valuable when running Google Ads campaigns with form-based conversions, as it materially improves measured conversion rates and Smart Bidding signal quality.

## Attribution and reporting settings

In GA4 > Admin > Data Display > Attribution Settings:

- **Attribution model**: data-driven (default). With low traffic, GA4 falls back to last-click. Don't change this manually.
- **Conversion lookback window**: 30 days for fast-cycle ecommerce, 90 days for travel/hospitality, B2B SaaS, or any business with a long decision cycle
- **Engagement lookback window**: 30 days

In GA4 > Admin > Reporting Identity:

- **Blended** (default): combines User-ID, Google Signals, Device-ID, and modeling - best for accuracy when Google Signals is enabled
- **Observed**: User-ID, Google Signals, Device-ID without modeling
- **Device-based**: only Device-ID - useful for low-traffic sites where data thresholding is a problem because modeling and Google Signals data trigger thresholding more aggressively

For an EU site with Google Signals disabled, **Device-based** often gives the most useful low-traffic reports without sacrificing real measurement.

## Internal traffic exclusion

Own visits to the site pollute the data. Exclude them:

1. GA4 > Admin > Data Streams > select the stream > Configure tag settings > Show all > Define internal traffic > Create
2. Rule name: "Owner IP" or similar
3. Traffic type value: leave as `internal`
4. Match type: "IP address equals" (or "begins with" / "in range")
5. Find the IP at [whatismyip.com](https://www.whatismyip.com) or by Googling "what is my IP"
6. Save

Then activate the filter:

1. GA4 > Admin > Data Settings > Data Filters
2. Find the "Internal Traffic" filter
3. Change the state from **Testing** to **Active**

Once active, filtered traffic is permanently excluded from all reports. Note: filtered traffic also disappears from DebugView, so disable temporarily for debug sessions or use a different device.

For dynamic IPs (most home connections), the filter must be updated periodically. For office IPs or static residential IPs, set it once and forget.
