---
name: stripe-integrator
description: >
  Comprehensive Stripe integration agent for payments, subscriptions, billing, and
  marketplace management. Use when Claude needs to work with Stripe API for creating
  customers, managing subscriptions, processing payments, handling checkout sessions,
  setting up products/prices, managing webhooks, Connect marketplaces, metered billing,
  tax calculation, fraud prevention, or any payment-related task. Triggers on mentions
  of Stripe, payments, subscriptions, billing, checkout, invoices, payment intents,
  recurring payments, Connect, marketplace, SCA, 3D Secure, or disputes.
tools: Read, Write, Edit, Bash, Glob, Grep
model: opus
color: purple
---

# Stripe Integrator

Interact with Stripe's API for complete payment and subscription management.

## Prerequisites

Ensure `STRIPE_SECRET_KEY` environment variable is set. For webhook handling, also set `STRIPE_WEBHOOK_SECRET`.

```bash
export STRIPE_SECRET_KEY="sk_test_..."
export STRIPE_WEBHOOK_SECRET="whsec_..."
```

Install the Stripe SDK (use a virtual environment for isolation):
```bash
pip install stripe
```

## Core Workflows

### 1. Customer Management

Create and manage customers before any payment operation.

```python
import stripe
import os

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

# Create customer
customer = stripe.Customer.create(
    email="user@example.com",
    name="John Doe",
    metadata={"user_id": "your_app_user_id"}
)

# Retrieve / Update / List
customer = stripe.Customer.retrieve("cus_xxx")
stripe.Customer.modify("cus_xxx", metadata={"plan": "premium"})
customers = stripe.Customer.list(limit=10, email="user@example.com")
```

### 2. Products and Prices

Always create Products first, then attach Prices. Use `lookup_key` for easy price retrieval.

```python
product = stripe.Product.create(
    name="Pro Plan",
    description="Full access to all features",
    metadata={"tier": "pro"}
)

# Recurring price (subscription)
price = stripe.Price.create(
    product=product.id,
    unit_amount=1999,  # Amount in cents
    currency="eur",
    recurring={"interval": "month"},
    lookup_key="pro_monthly"
)

# One-time price
one_time_price = stripe.Price.create(
    product=product.id,
    unit_amount=9999,
    currency="eur",
    lookup_key="pro_lifetime"
)
```

### 3. Checkout Sessions (Recommended for Web)

Use Checkout Sessions for secure, hosted payment pages.

```python
session = stripe.checkout.Session.create(
    customer="cus_xxx",
    mode="subscription",
    line_items=[{"price": "price_xxx", "quantity": 1}],
    success_url="https://yourapp.com/success?session_id={CHECKOUT_SESSION_ID}",
    cancel_url="https://yourapp.com/cancel",
    metadata={"user_id": "123"}
)
# Redirect user to: session.url
```

### 4. Subscription Management

```python
# Create subscription directly (when you have payment method)
subscription = stripe.Subscription.create(
    customer="cus_xxx",
    items=[{"price": "price_xxx"}],
    payment_behavior="default_incomplete",
    expand=["latest_invoice.payment_intent"]
)

# Update subscription (change plan)
stripe.Subscription.modify(
    "sub_xxx",
    items=[{"id": sub["items"]["data"][0].id, "price": "price_new_xxx"}],
    proration_behavior="create_prorations"
)

# Cancel subscription
stripe.Subscription.cancel("sub_xxx")  # Immediate
stripe.Subscription.modify("sub_xxx", cancel_at_period_end=True)  # At period end
```

### 5. Payment Intents (Custom Integration)

Use when you need full control over the payment flow.

```python
intent = stripe.PaymentIntent.create(
    amount=2000,
    currency="eur",
    customer="cus_xxx",
    metadata={"order_id": "order_123"}
)
# Return intent.client_secret to frontend
```

### 6. Webhook Handling

Critical for subscription lifecycle. Key events to handle:
- `checkout.session.completed` - Payment successful
- `customer.subscription.created` - New subscription
- `customer.subscription.updated` - Plan changes
- `customer.subscription.deleted` - Cancellation
- `invoice.paid` - Successful renewal
- `invoice.payment_failed` - Failed payment

```python
def handle_webhook(payload, sig_header):
    endpoint_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")
    event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        # Fulfill order, activate subscription
    elif event["type"] == "invoice.payment_failed":
        invoice = event["data"]["object"]
        # Notify user, handle dunning
    return {"status": "success"}
```

## Firebase Integration Pattern

For Firebase + Stripe integration, see `references/firebase-integration.md`.

Quick setup:
1. Store Stripe customer_id in Firestore user document
2. Sync subscription status via webhooks to Firestore
3. Use Firebase Security Rules to check subscription status

## Common Operations Quick Reference

| Task | Method |
|------|--------|
| Create customer | `stripe.Customer.create()` |
| Start subscription | `stripe.checkout.Session.create(mode="subscription")` |
| Cancel subscription | `stripe.Subscription.cancel()` |
| Change plan | `stripe.Subscription.modify()` |
| Refund payment | `stripe.Refund.create(payment_intent="pi_xxx")` |
| Get invoices | `stripe.Invoice.list(customer="cus_xxx")` |
| Create portal session | `stripe.billing_portal.Session.create()` |

## Customer Portal (Self-Service)

```python
portal_session = stripe.billing_portal.Session.create(
    customer="cus_xxx",
    return_url="https://yourapp.com/account"
)
# Redirect to: portal_session.url
```

## Payment Links (No-Code Payments)

```python
payment_link = stripe.PaymentLink.create(
    line_items=[{"price": "price_xxx", "quantity": 1}],
    after_completion={"type": "redirect", "redirect": {"url": "https://yourapp.com/thanks"}}
)
# Share: payment_link.url
```

## Testing

Use test mode keys (`sk_test_...`) and test card numbers:
- `4242424242424242` - Successful payment
- `4000000000000002` - Declined
- `4000002500003155` - Requires 3D Secure

## Error Handling

```python
try:
    # Stripe operation
except stripe.error.CardError as e:
    print(f"Card error: {e.user_message}")
except stripe.error.InvalidRequestError as e:
    print(f"Invalid request: {e}")
except stripe.error.AuthenticationError:
    pass  # Invalid API key
except stripe.error.StripeError as e:
    pass  # Generic Stripe error
```

## Advanced Features

For detailed code examples of the following, see `references/stripe-patterns.md`:
- **Metered and usage-based billing** - API calls, seats, tiered pricing
- **Stripe Connect (Marketplaces)** - Connected accounts, platform fees, transfers
- **Tax Calculation (Stripe Tax)** - Automatic tax in checkout
- **3D Secure and SCA Compliance** - Strong Customer Authentication (EU/UK)
- **Fraud Prevention (Stripe Radar)** - Risk assessment, custom rules
- **Dispute Handling** - Chargebacks, evidence submission
- **Idempotency** - Preventing duplicate operations

## Scripts Reference

- `scripts/setup_products.py` - Create products and prices
- `scripts/webhook_handler.py` - Flask webhook endpoint
- `scripts/sync_subscriptions.py` - Sync subscriptions to database
- `scripts/stripe_utils.py` - Common utility functions

## References

- `references/stripe-patterns.md` - Metered billing, Connect, tax, 3DS, Radar, disputes, idempotency patterns
- `references/firebase-integration.md` - Firebase + Firestore integration
- `references/api-cheatsheet.md` - Quick API reference
