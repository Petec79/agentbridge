# agents.json — Open Standard for Agentic Commerce

**Version:** 1.0.0  
**Status:** Draft Specification  
**URI:** https://github.com/Petec79/agentbridge/spec/v1  
**Authors:** AgentBridge Working Group  

---

## Abstract

This specification defines `agents.json`, a machine-readable endpoint that e-commerce stores publish to declare their product catalog, checkout flow, and commerce policies in a standardized format. AI agents — regardless of their underlying model or implementation — can read this endpoint to discover products, add items to a cart, and complete purchases without store-specific integration code.

`agents.json` is to shopping what `robots.txt` is to search: a well-known, openly published contract that any compliant agent can interpret and act upon.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Discovery Mechanism](#2-discovery-mechanism)
3. [Endpoints](#3-endpoints)
4. [Product Data Schema](#4-product-data-schema)
5. [Agent Identification and Authentication](#5-agent-identification-and-authentication)
6. [Rate Limiting and Usage Policies](#6-rate-limiting-and-usage-policies)
7. [Privacy Considerations](#7-privacy-considerations)
8. [Compliance and Policy Endpoints](#8-compliance-and-policy-endpoints)
9. [Versioning Strategy](#9-versioning-strategy)
10. [Example agents.json](#10-example-agentsjson)
11. [Implementation Notes for Common Platforms](#11-implementation-notes-for-common-platforms)

---

## 1. Overview

### 1.1 What is agents.json?

`agents.json` is a JSON document published by an e-commerce store at a well-known URL (either `/.well-known/agents.json` or `/agents.json` at the root domain). It declares:

- The store's identity and branding
- Available API endpoints for catalog access, search, cart management, and checkout
- Authentication requirements for agent-initiated sessions
- Rate limiting and usage policies
- Compliance data: return policies, refund procedures, shipping rules
- Product catalog schema and structure

### 1.2 Why It Exists

AI shopping agents today must be hard-coded to each store's unique API, payment processor, and checkout flow. A clothing store on Shopify, a electronics retailer on WooCommerce, and a boutique on Squarespace all require store-specific adapters. This fragmentation prevents AI agents from acting as general-purpose shopping assistants.

`agents.json` solves this by creating a single, open contract. Any compliant store can be shopped by any compliant agent. The agent does not need to know which platform the store runs on, which payment gateway it uses, or how its checkout is structured — all of this is declared in the standard format.

### 1.3 Who It Is For

**Store Operators** publish `agents.json` to make their store agent-accessible without integrating with each AI provider individually.

**AI Agent Developers** implement `agents.json` client logic once to gain access to the entire network of compliant stores.

**Platform Providers** (Shopify, WooCommerce, BigCommerce, etc.) can emit `agents.json` automatically for all hosted stores, bootstrapping the network effect.

### 1.4 Design Principles

1. **Open and Royalty-Free** — No license required to implement or use this specification.
2. **Self-Describing** — Every endpoint, field, and policy is declared in the document itself.
3. **Privacy-First** — Agents are not required to share user identity or behavioral data.
4. **Backward Compatible** — Versioned endpoints ensure old agents can still function as new fields are added.
5. **No Account Required** — Agents can browse and in many cases purchase as a guest, without creating a user account.

---

## 2. Discovery Mechanism

### 2.1 Well-Known URL

An agent seeking to shop at a store begins by attempting to retrieve `agents.json`. Discovery follows this priority order:

1. **`https://{store_domain}/.well-known/agents.json`** (RFC 8615 compliant)
2. **`https://{store_domain}/agents.json`** (fallback, for stores that cannot host files under `.well-known`)

The agent MUST attempt both URLs if the first returns a 404. If neither URL returns a valid `agents.json`, the store is considered non-compliant and the agent SHOULD NOT attempt proprietary API access.

### 2.2 HTTPS Requirement

All `agents.json` endpoints MUST be served over HTTPS. HTTP URLs MUST be rejected by agents.

### 2.3 Cache Behavior

The root `agents.json` document SHOULD be cached by agents for a minimum of 5 minutes and a maximum of 1 hour (configurable per-store based on update frequency declared in the document). Agents MUST re-fetch on cache expiry or when any operation returns a `410 Gone` or `403 Forbidden`.

```http
GET /.well-known/agents.json HTTP/1.1
Host: example-store.com
Accept: application/json
User-Agent: Claude-Agent/1.0 (agentic-commerce-client)

HTTP/1.1 200 OK
Content-Type: application/json
Cache-Control: max-age=300
ETag: "abc123"
```

### 2.4 Non-Compliant Stores

If neither well-known URL returns valid JSON, the agent MUST NOT fall back to store-specific APIs, crawlers, or scraping. The agent MAY inform the user that the store is not agent-accessible.

---

## 3. Endpoints

All endpoint URLs are declared inside the root `agents.json` document under the `endpoints` object. All endpoints accept and return JSON. All request and response bodies use `Content-Type: application/json` unless otherwise specified.

### 3.1 Endpoint: Store Information

**URL:** `GET {endpoints.store_info}`

Returns identity, branding, and contact information for the store.

**Response Schema:**

```json
{
  "store_id": "string (unique identifier, opaque to agents)",
  "name": "string (display name)",
  "domain": "string (canonical HTTPS domain)",
  "logo_url": "string (URL to logo image, optional)",
  "description": "string (short tagline, optional)",
  "currency": "string (ISO 4217 currency code, e.g., USD)",
  "weight_unit": "string (KG | LB | OZ | G)",
  "dimension_unit": "string (CM | IN)",
  "contact_email": "string (customer support email)",
  "terms_url": "string (URL to terms of service, optional)",
  "privacy_url": "string (URL to privacy policy, optional)",
  "supported_locales": ["string (ISO 639-1 language codes, e.g., en, fr)"],
  "created_at": "string (ISO 8601 datetime)"
}
```

### 3.2 Endpoint: Product Catalog

**URL:** `GET {endpoints.catalog}`

Returns a paginated list of all products.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `page` | integer | No | Page number (1-indexed, default: 1) |
| `per_page` | integer | No | Items per page (default: 50, max: 250) |
| `category_id` | string | No | Filter by category ID |
| `sort` | string | No | Sort field: `price_asc`, `price_desc`, `name_asc`, `newest`, `relevance` |
| `availability` | string | No | Filter: `in_stock`, `out_of_stock`, `all` (default: `in_stock`) |

**Response Schema:**

```json
{
  "products": [ /* array of Product objects — see Section 4 */ ],
  "pagination": {
    "page": 1,
    "per_page": 50,
    "total_pages": 12,
    "total_items": 589,
    "has_next": true,
    "has_prev": false
  },
  "categories": [ /* array of Category objects — see Section 4.3 */ ]
}
```

### 3.3 Endpoint: Product Detail

**URL:** `GET {endpoints.product}`

Retrieve full details for a single product.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `product_id` | string | Yes | The unique product identifier |

**Response Schema:** A single `Product` object (see Section 4).

### 3.4 Endpoint: Search

**URL:** `GET {endpoints.search}`

Full-text and filtered search across the product catalog.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `q` | string | Yes | Search query string |
| `page` | integer | No | Page number (default: 1) |
| `per_page` | integer | No | Items per page (default: 50, max: 250) |
| `category_id` | string | No | Limit to category |
| `min_price` | number | No | Minimum price (inclusive) |
| `max_price` | number | No | Maximum price (inclusive) |
| `availability` | string | No | `in_stock`, `out_of_stock`, `all` (default: `in_stock`) |
| `sort` | string | No | `relevance`, `price_asc`, `price_desc`, `name_asc`, `newest` |

**Response Schema:** Same as catalog endpoint.

### 3.5 Endpoint: Cart

The cart is a session-scoped resource. Agents interact with it via standard REST methods.

#### 3.5.1 Get Current Cart

**URL:** `GET {endpoints.cart}`

**Headers:**

```
X-Agent-Token: {agent_token}   (see Section 5)
X-Session-ID: {session_id}     (opaque session identifier, UUID recommended)
```

**Response Schema:**

```json
{
  "cart_id": "string",
  "session_id": "string",
  "items": [
    {
      "item_id": "string (line item ID)",
      "product_id": "string",
      "variant_id": "string (optional)",
      "quantity": 1,
      "unit_price": 29.99,
      "currency": "USD",
      "subtotal": 29.99,
      "product_name": "Classic T-Shirt",
      "variant_name": "Large / Navy",
      "image_url": "string (optional)"
    }
  ],
  "subtotal": 29.99,
  "tax": 2.40,
  "shipping": 5.99,
  "total": 38.38,
  "currency": "USD",
  "item_count": 1,
  "created_at": "string (ISO 8601)",
  "updated_at": "string (ISO 8601)",
  "expires_at": "string (ISO 8601, optional — cart TTL)"
}
```

#### 3.5.2 Add Item to Cart

**URL:** `POST {endpoints.cart}/items`

**Request Body:**

```json
{
  "product_id": "string (required)",
  "variant_id": "string (optional, for variant selection)",
  "quantity": 1
}
```

**Response:** Updated cart object (same as Get Cart response).

**Status Codes:** `200 OK`, `400 Bad Request` (invalid product/variant), `409 Conflict` (item already in cart — updates quantity instead), `422 Unprocessable Entity` (out of stock).

#### 3.5.3 Update Cart Item

**URL:** `PATCH {endpoints.cart}/items/{item_id}`

**Request Body:**

```json
{
  "quantity": 3
}
```

To remove an item, set `quantity` to `0`.

#### 3.5.4 Remove Cart Item

**URL:** `DELETE {endpoints.cart}/items/{item_id}`

**Response:** Updated cart object.

#### 3.5.5 Clear Cart

**URL:** `DELETE {endpoints.cart}`

Removes all items from the cart.

### 3.6 Endpoint: Checkout

#### 3.6.1 Initiate Checkout

**URL:** `POST {endpoints.checkout}/initiate`

Creates a checkout session and returns an `checkout_url` for payment completion. For guest checkouts, the store MAY return payment details inline (see below).

**Request Body (all fields optional unless `requires_shipping = true`):**

```json
{
  "cart_id": "string (required)",
  "session_id": "string (required)",
  "customer": {
    "email": "string (required for digital goods)",
    "first_name": "string",
    "last_name": "string",
    "phone": "string"
  },
  "shipping_address": {
    "address_line1": "string (required if physical goods)",
    "address_line2": "string (optional)",
    "city": "string (required if physical goods)",
    "state": "string (required if physical goods)",
    "postal_code": "string (required if physical goods)",
    "country": "string (ISO 3166-1 alpha-2 code, required if physical goods)"
  },
  "payment_method": {
    "type": "string (card | bank_transfer | store_credit | braintree | stripe | paypal)",
    "token": "string (payment processor token from hosted fields)"
  },
  "shipping_method": "string (carrier ID, from shipping_options list, optional)",
  "coupon_code": "string (optional)"
}
```

**Response:**

```json
{
  "checkout_id": "string",
  "status": "pending_payment | completed | failed",
  "order_id": "string (present if status = completed)",
  "payment_instructions": {
    "type": "string",
    "amount": 38.38,
    "currency": "USD",
    "provider": "string",
    "hosted_page_url": "string (URL to payment page, for redirect flows)",
    "inline_fields": { /* for stores that return payment fields inline */ }
  },
  "order_summary": {
    "subtotal": 29.99,
    "tax": 2.40,
    "shipping": 5.99,
    "discount": 0.00,
    "total": 38.38,
    "currency": "USD"
  },
  "redirect_url": "string (URL to redirect to after payment, optional)"
}
```

#### 3.6.2 Get Checkout Status

**URL:** `GET {endpoints.checkout}/{checkout_id}`

Poll this endpoint to check payment completion status.

#### 3.6.3 Confirm Order

**URL:** `POST {endpoints.checkout}/{checkout_id}/confirm`

Called by the agent after confirming payment was made (for redirect-based flows, called after returning from the payment provider).

**Response:**

```json
{
  "order_id": "string",
  "status": "confirmed | processing | shipped | delivered | cancelled",
  "confirmation_number": "string",
  "estimated_delivery": "string (ISO 8601 date, optional)",
  "tracking_url": "string (optional)",
  "email": "string (confirmation email sent to this address)",
  "line_items": [ /* array of purchased items */ ],
  "totals": {
    "subtotal": 29.99,
    "tax": 2.40,
    "shipping": 5.99,
    "total": 38.38,
    "currency": "USD"
  }
}
```

### 3.7 Endpoint: Order History

**URL:** `GET {endpoints.orders}`

Returns past orders for the current session/customer.

**Headers:** `X-Agent-Token`, `X-Session-ID`

**Query Parameters:** `page`, `per_page`

**Response:**

```json
{
  "orders": [
    {
      "order_id": "string",
      "confirmation_number": "string",
      "status": "confirmed | processing | shipped | delivered | cancelled | refunded",
      "placed_at": "string (ISO 8601)",
      "line_items": [ /* items */ ],
      "totals": { /* subtotal, tax, shipping, total, currency */ },
      "tracking_url": "string (optional)"
    }
  ],
  "pagination": { /* standard pagination object */ }
}
```

### 3.8 Endpoint: Customer Authentication

See Section 5 for full agent authentication details.

**URL:** `POST {endpoints.auth}/login`

```json
{
  "email": "string",
  "password": "string"
}
```

**Response:**

```json
{
  "customer_id": "string",
  "email": "string",
  "first_name": "string",
  "last_name": "string",
  "token": "string (session token to use in X-Customer-Token header)"
}
```

**URL:** `POST {endpoints.auth}/logout`

**URL:** `POST {endpoints.auth}/register`

```json
{
  "email": "string",
  "password": "string",
  "first_name": "string",
  "last_name": "string"
}
```

---

## 4. Product Data Schema

### 4.1 Product Object

```json
{
  "product_id": "string (unique identifier, URL-safe)",
  "name": "string (required)",
  "slug": "string (URL-friendly identifier)",
  "description": "string (full HTML or plain-text description — use description_plain if HTML not supported)",
  "description_plain": "string (plain-text version, required if description contains HTML)",
  "brand": "string (brand name, optional)",
  "sku": "string (stock keeping unit, optional)",
  "mpn": "string (manufacturer part number, optional)",
  "gtin": "string (Global Trade Item Number, optional — EAN, UPC, or ISBN)",
  "images": [
    {
      "url": "string (required)",
      "alt_text": "string (optional)",
      "is_primary": true,
      "width": 1200,
      "height": 800,
      "order": 1
    }
  ],
  "price": {
    "amount": 29.99,
    "currency": "USD",
    "compare_at_amount": 39.99,
    "is_on_sale": true,
    "sale_ends_at": "string (ISO 8601 datetime, optional)"
  },
  "inventory": {
    "tracked": true,
    "quantity": 142,
    "availability_status": "in_stock | low_stock | out_of_stock | preorder | backorder",
    "low_stock_threshold": 10
  },
  "categories": [
    {
      "category_id": "string",
      "name": "string",
      "path": ["Root", "Clothing", "T-Shirts"]
    }
  ],
  "variants": [
    {
      "variant_id": "string",
      "name": "Large / Navy",
      "sku": "TSHIRT-L-NVY",
      "price": {
        "amount": 29.99,
        "currency": "USD"
      },
      "inventory": {
        "quantity": 34,
        "availability_status": "in_stock"
      },
      "options": {
        "size": "Large",
        "color": "Navy"
      },
      "image_url": "string (optional, override image for this variant)"
    }
  ],
  "attributes": {
    "material": "100% Cotton",
    "care_instructions": "Machine wash cold",
    "origin": "Made in Portugal"
  },
  "tags": ["summer", "casual", "essentials"],
  "weight": {
    "value": 0.3,
    "unit": "KG"
  },
  "dimensions": {
    "length": 30,
    "width": 25,
    "height": 2,
    "unit": "CM"
  },
  "is_active": true,
  "created_at": "string (ISO 8601)",
  "updated_at": "string (ISO 8601)"
}
```

### 4.2 Field Requirements

| Field | Required | Notes |
|-------|----------|-------|
| `product_id` | Yes | Must be globally unique within this store. Stable across updates. |
| `name` | Yes | Max 500 characters. |
| `slug` | Recommended | Used for deep linking. |
| `price.amount` | Yes | Positive decimal, max 2 decimal places. |
| `price.currency` | Yes | ISO 4217 code. |
| `images` | Recommended | At least one image strongly recommended. |
| `inventory.tracked` | Yes | Must be `true` or `false`. |
| `inventory.quantity` | Conditional | Required when `tracked = true`. |
| `inventory.availability_status` | Yes | One of the defined enum values. |
| `variants` | No | Required only for products with selectable options (size/color). |
| `description` or `description_plain` | Recommended | At least one description field recommended. |

### 4.3 Category Object

```json
{
  "category_id": "string",
  "name": "T-Shirts",
  "slug": "t-shirts",
  "path": ["Clothing", "Tops", "T-Shirts"],
  "parent_id": "string (ID of parent category, null for root)",
  "product_count": 47,
  "image_url": "string (optional)"
}
```

### 4.4 Price Object

All monetary amounts are expressed as a decimal `amount` and a three-letter `currency` code. Agents MUST NOT assume a default currency if the `price.currency` field is absent. Agents MUST NOT sum monetary amounts across products with different currencies without explicit conversion.

Stores MAY express prices in any currency but MUST use the same currency for all amounts within a single cart/checkout session.

### 4.5 Inventory and Availability

The `availability_status` field MUST be one of:

- **`in_stock`** — Item is available and in stock.
- **`low_stock`** — Item is available but inventory is below the `low_stock_threshold`.
- **`out_of_stock`** — Item is not currently available. Agents SHOULD NOT add to cart.
- **`preorder`** — Item is not yet available; customers can order now for future delivery.
- **`backorder`** — Item is not currently in stock but can be ordered; will ship when available.

If `inventory.tracked = false`, agents SHOULD treat the item as `in_stock` and rely on checkout to determine actual availability.

---

## 5. Agent Identification and Authentication

### 5.1 Why Distinguish Agents from Humans?

Agents perform actions at scale and speed that differ fundamentally from human browsing. Stores need to identify requests as agent-originated to: apply appropriate rate limits, attribute purchases correctly, comply with analytics and advertising policies, and prevent credential stuffing or cart abandonment attacks.

### 5.2 Agent Identification Header

Every request made by an agent MUST include the `User-Agent` header identifying the agent and its version, following this format:

```
User-Agent: {AgentName}/{Version} (AgenticCommerce; +https://{agent-domain})
```

**Example:**

```
User-Agent: ClaudeAgent/1.0 (AgenticCommerce; +https://anthropic.com)
```

Agents MAY also include a `X-Agent-ID` header with a stable, globally unique identifier for the agent (e.g., a ULID assigned by the agent registry):

```
X-Agent-ID: clag_01HXYZ1234567890ABCDEFG
```

### 5.3 Agent Token

Agents MUST obtain an `agent_token` to interact with cart, checkout, and authenticated endpoints. Tokens are issued by the store's token endpoint.

#### 5.3.1 Token Endpoint

**URL:** `POST {endpoints.auth}/agent/token`

```json
{
  "agent_id": "string (from X-Agent-ID header or agent's registered ID)",
  "agent_name": "string",
  "agent_version": "string",
  "agent_vendor_url": "string",
  "capabilities": ["browse", "purchase", "refund_request"],
  "intended_action": "browsing | purchasing | both"
}
```

**Response:**

```json
{
  "agent_token": "string (opaque bearer token)",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "read | write | purchase",
  "rate_limits": {
    "requests_per_minute": 60,
    "requests_per_hour": 1000,
    "cart_operations_per_hour": 30,
    "checkout_attempts_per_day": 10
  }
}
```

The `agent_token` is passed in the `Authorization` header as a Bearer token, or in the `X-Agent-Token` header:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
X-Agent-Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Agents MUST treat the `agent_token` as confidential. Stores MUST expire agent tokens after the declared `expires_in` period. Agents MUST re-request a token when it expires.

### 5.4 Session ID

For stateless cart management, the agent MUST generate a stable, opaque session identifier (UUID v4 recommended) and send it in the `X-Session-ID` header on every request:

```http
X-Session-ID: 550e8400-e29b-41d4-a716-446655440000
```

The session ID persists the agent's cart across requests. Stores MAY expire sessions after 24 hours of inactivity.

### 5.5 Customer Authentication (Optional)

If the agent is purchasing on behalf of a specific customer (i.e., a human user委托 an agent to shop), the agent MAY authenticate as the customer using the customer login endpoint (Section 3.8) and include the resulting `customer_token` in the `X-Customer-Token` header:

```http
X-Customer-Token: cust_eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

This allows the checkout to be attributed to the correct customer account, loyalty program, and order history.

### 5.6 Unidentified / Guest Agents

Agents that only browse (without cart or checkout) do not need a token. The store's `endpoints.catalog` and `endpoints.search` endpoints MUST be accessible without authentication, unless the store explicitly opts into a fully private catalog (see `catalog_visibility` in the root schema).

### 5.7 Root Schema: Authentication and Token Configuration

The root `agents.json` document MUST include an `auth` configuration block:

```json
{
  "auth": {
    "agent_token_endpoint": "string (URL, required if store supports agent tokens)",
    "customer_login_required": false,
    "guest_checkout_allowed": true,
    "supported_payment_methods": [
      {
        "type": "card",
        "provider": "stripe",
        "hosted": true,
        "inline": false
      },
      {
        "type": "card",
        "provider": "braintree",
        "hosted": true,
        "inline": false
      },
      {
        "type": "paypal",
        "provider": "paypal",
        "hosted": true,
        "inline": false
      },
      {
        "type": "bank_transfer",
        "provider": "ach",
        "hosted": false,
        "inline": true
      }
    ]
  }
}
```

---

## 6. Rate Limiting and Usage Policies

### 6.1 Declaring Rate Limits

Stores declare their rate limits in the root `agents.json` document. Agents MUST respect these limits.

```json
{
  "rate_limits": {
    "catalog_requests_per_minute": 60,
    "search_requests_per_minute": 30,
    "cart_operations_per_hour": 30,
    "checkout_attempts_per_day": 10,
    "concurrent_sessions": 5,
    "burst_allowance": 10
  }
}
```

### 6.2 Rate Limit Headers

Every API response MUST include rate limit information in headers:

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1719834160
X-RateLimit-Window: 60
```

- `X-RateLimit-Limit` — Maximum requests allowed in the window.
- `X-RateLimit-Remaining` — Requests remaining in current window.
- `X-RateLimit-Reset` — Unix timestamp when the window resets.
- `X-RateLimit-Window` — Window duration in seconds.

### 6.3 Exceeded Rate Limits

When a rate limit is exceeded, the store MUST return `429 Too Many Requests`:

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 30
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1719834160
```

The `Retry-After` header (in seconds) indicates when the agent may resume requests.

### 6.4 Agent Obligations

Agents MUST:

- Track rate limit headers on every response and slow down proactively.
- Implement exponential backoff when receiving `429` responses, doubling wait time on each successive 429.
- Never attempt to circumvent rate limits by using multiple IP addresses or session IDs.
- Identify themselves honestly in the `User-Agent` and `X-Agent-ID` headers.

### 6.5 Usage Policies

Stores MAY declare additional usage policies in the root document:

```json
{
  "usage_policies": {
    "agent_purchasing_allowed": true,
    "bulk_purchasing_allowed": false,
    "resale_purchasing_allowed": false,
    "minimum_order_value": 1.00,
    "maximum_order_quantity_per_item": 10,
    "prohibited_product_categories": ["gift_cards", "digital_licenses"]
  }
}
```

Agents MUST respect these policies. A `403 Forbidden` response with `policy_violation` code indicates a violated usage policy.

---

## 7. Privacy Considerations

### 7.1 Data Minimization

Agents SHOULD only share data necessary for the current operation:

- **Browsing only:** No personal data required.
- **Guest checkout:** Email address and shipping address only (no account required).
- **Authenticated checkout:** Customer token obtained via explicit login.

Agents MUST NOT share a user's browsing history, search queries, or behavioral data with the store unless the user has explicitly opted in.

### 7.2 Required vs. Optional Fields

Stores MUST mark all customer data fields as either `required` or `optional` in their schema. Agents can display this to users so they understand what data is needed for purchase.

### 7.3 Data the Agent Should NOT Send

Unless explicitly required by the store, agents SHOULD NOT send:

- User's full name (unless needed for shipping)
- Phone number (unless required for shipping or delivery)
- Date of birth
- Gender or demographic data
- Previously visited websites
- Device identifiers or fingerprinting data

### 7.4 Session Data

The `X-Session-ID` is an opaque token. It contains no Personally Identifiable Information (PII). Agents MUST use a new session ID per user, not per agent instance. A session ID shared across users would leak cross-user browsing behavior.

### 7.5 Checkout Attribution

When an agent acts on behalf of a human user, the agent SHOULD authenticate as the customer (Section 5.5) rather than making a guest purchase, so the order appears in the customer's account history. This gives the human user full visibility and control over their purchases.

### 7.6 PII in Error Messages

Stores MUST NOT include PII in error response messages. Error messages MUST NOT reveal whether an email is registered, whether a discount code exists, or any other information that could be leveraged for enumeration attacks.

---

## 8. Compliance and Policy Endpoints

### 8.1 Returns and Refunds Policy

**URL:** `GET {endpoints.policies}/returns`

```json
{
  "returns_allowed": true,
  "return_window_days": 30,
  "return_window_start": "delivery_date | order_date",
  "return_conditions": {
    "items_must_be_unworn": true,
    "items_must_have_tags": true,
    "original_packaging_required": false,
    "proof_of_purchase_required": true
  },
  "return_shipping_covered_by": "customer | store | free",
  "refund_methods": ["original_payment_method", "store_credit"],
  "refund_processing_days": {
    "min": 3,
    "max": 10
  },
  "exceptions": {
    "final_sale_items": true,
    "customized_items": true,
    "opened_hygiene_products": true
  },
  "how_to_return": "string (URL or plain-text instructions)"
}
```

### 8.2 Shipping Policy

**URL:** `GET {endpoints.policies}/shipping`

```json
{
  "ships_domestic_only": false,
  "ships_to_countries": ["US", "CA", "GB", "AU", "DE", "FR"],
  "does_not_ship_to": ["RU", "CN"],
  "processing_time": {
    "min_days": 1,
    "max_days": 3,
    "unit": "business_days"
  },
  "estimated_delivery": {
    "domestic": {
      "min_days": 3,
      "max_days": 7,
      "unit": "business_days"
    },
    "international": {
      "min_days": 7,
      "max_days": 21,
      "unit": "business_days"
    }
  },
  "shipping_methods": [
    {
      "carrier": "string",
      "service_name": "string",
      "estimated_days": "3-7",
      "price": 5.99,
      "currency": "USD",
      "is_expedited": false,
      "is_free": false,
      "method_id": "standard_us"
    }
  ],
  "free_shipping_thresholds": [
    {
      "minimum_order_amount": 75.00,
      "currency": "USD",
      "applicable_methods": ["standard_us", "express_us"]
    }
  ],
  " Signature Required": {
    "domestic_min_order_value": 200.00,
    "currency": "USD"
  },
  "restrictions": {
    "no_po_boxes": false,
    "no_afternoon_delivery": false
  }
}
```

### 8.3 Privacy Policy Summary

**URL:** `GET {endpoints.policies}/privacy`

```json
{
  "data_collected": {
    "order_data": ["name", "email", "shipping_address", "billing_address"],
    "payment_data": "handled_by_payment_processor",
    "browsing_data": ["session_id", "pages_viewed"],
    "communication_data": ["support_tickets", "emails"]
  },
  "data_retention": {
    "order_data_years": 7,
    "browsing_data_days": 90,
    "communication_data_years": 3
  },
  "third_party_sharing": {
    "payment_processors": true,
    "shipping_carriers": true,
    "marketing_platforms": false,
    "analytics": true
  },
  "user_rights": {
    "right_to_access": true,
    "right_to_deletion": true,
    "right_to_portability": true,
    "contact_for_requests": "privacy@example-store.com"
  },
  "cookies_used": true,
  "do_not_track_honored": true,
  "privacy_policy_url": "https://example-store.com/privacy"
}
```

### 8.4 Terms of Service Summary

**URL:** `GET {endpoints.policies}/terms`

```json
{
  "acceptance_required_before_purchase": true,
  "governing_law": "State of New York, USA",
  "dispute_resolution": "binding_arbitration",
  "agent_purchasing_terms": {
    "agents_must_identify_themselves": true,
    "agent_purchases_are_binding": true,
    "store_reserves_right_to_cancel_agent_orders": false
  },
  "age_requirement": 18,
  "terms_url": "https://example-store.com/terms"
}
```

### 8.5 Payment and Security

**URL:** `GET {endpoints.policies}/payments`

```json
{
  "supported_currencies": ["USD", "CAD", "GBP"],
  "payment_gateway": "stripe",
  "pci_dss_compliant": true,
  "3d_secure_required": true,
  "fraud_detection_enabled": true,
  "supported_card_types": ["visa", "mastercard", "amex", "discover"],
  "alternative_payment_methods": ["paypal", "apple_pay", "google_pay"]
}
```

---

## 9. Versioning Strategy

### 9.1 URL Versioning

Each version of the specification has a dedicated base path:

```
https://github.com/Petec79/agentbridge/spec/v1/  (current version)
https://github.com/Petec79/agentbridge/spec/v2/  (future versions)
```

### 9.2 Media Type Versioning

All JSON payloads include a `version` field in the root response object:

```json
{
  "version": "1.0.0",
  "deprecated": false,
  "sunset_date": null
}
```

### 9.3 Capability Negotiation

Agents declare the protocol version they support when requesting an agent token:

```json
{
  "agent_id": "...",
  "protocol_version": "1.0.0",
  "minimum_supported_version": "1.0.0",
  "capabilities": ["browse", "purchase"]
}
```

### 9.4 Breaking vs. Non-Breaking Changes

**Non-breaking changes** (backward-compatible additions):
- Adding new optional fields to existing objects
- Adding new optional endpoints
- Adding new enum values to existing fields

**Breaking changes** (require major version bump):
- Removing or renaming required fields
- Changing field types
- Removing or renaming endpoints
- Changing authentication schemes

### 9.5 Deprecation

When a version is deprecated, stores MUST return:

```http
X-API-Deprecated: true
X-API-Sunset: 2025-12-31
X-API-Successor: https://github.com/Petec79/agentbridge/spec/v2/
```

Agents MUST migrate to the successor version before the `sunset` date.

---

## 10. Example agents.json

### 10.1 Root Document (agents.json)

```json
{
  "version": "1.0.0",
  "deprecated": false,
  "store": {
    "store_id": "store_a1b2c3d4e5f6",
    "name": "Nordic Thread",
    "domain": "https://nordicthread.com",
    "logo_url": "https://nordicthread.com/images/logo.png",
    "description": "Scandinavian-inspired essentials, made sustainably.",
    "currency": "USD",
    "weight_unit": "KG",
    "dimension_unit": "CM",
    "contact_email": "support@nordicthread.com",
    "terms_url": "https://nordicthread.com/terms",
    "privacy_url": "https://nordicthread.com/privacy",
    "supported_locales": ["en", "sv", "no", "da"],
    "created_at": "2023-01-15T00:00:00Z"
  },
  "endpoints": {
    "store_info": "https://nordicthread.com/api/agent/store",
    "catalog": "https://nordicthread.com/api/agent/catalog",
    "product": "https://nordicthread.com/api/agent/products",
    "search": "https://nordicthread.com/api/agent/search",
    "cart": "https://nordicthread.com/api/agent/cart",
    "checkout": "https://nordicthread.com/api/agent/checkout",
    "orders": "https://nordicthread.com/api/agent/orders",
    "auth": {
      "login": "https://nordicthread.com/api/agent/auth/login",
      "logout": "https://nordicthread.com/api/agent/auth/logout",
      "register": "https://nordicthread.com/api/agent/auth/register",
      "agent_token": "https://nordicthread.com/api/agent/auth/agent/token"
    },
    "policies": {
      "returns": "https://nordicthread.com/api/agent/policies/returns",
      "shipping": "https://nordicthread.com/api/agent/policies/shipping",
      "privacy": "https://nordicthread.com/api/agent/policies/privacy",
      "terms": "https://nordicthread.com/api/agent/policies/terms",
      "payments": "https://nordicthread.com/api/agent/policies/payments"
    }
  },
  "auth": {
    "agent_token_endpoint": "https://nordicthread.com/api/agent/auth/agent/token",
    "customer_login_required": false,
    "guest_checkout_allowed": true,
    "supported_payment_methods": [
      {
        "type": "card",
        "provider": "stripe",
        "hosted": true,
        "inline": false
      },
      {
        "type": "paypal",
        "provider": "paypal",
        "hosted": true,
        "inline": false
      },
      {
        "type": "apple_pay",
        "provider": "apple",
        "hosted": false,
        "inline": true
      }
    ]
  },
  "rate_limits": {
    "catalog_requests_per_minute": 60,
    "search_requests_per_minute": 30,
    "cart_operations_per_hour": 30,
    "checkout_attempts_per_day": 10,
    "concurrent_sessions": 5,
    "burst_allowance": 10
  },
  "usage_policies": {
    "agent_purchasing_allowed": true,
    "bulk_purchasing_allowed": false,
    "resale_purchasing_allowed": false,
    "minimum_order_value": 5.00,
    "maximum_order_quantity_per_item": 10,
    "prohibited_product_categories": ["digital_gift_cards"]
  },
  "catalog_visibility": "public",
  "agentbridge": {
    "spec_version": "1.0.0",
    "registry_url": "https://github.com/Petec79/agentbridge/registry",
    "compliance_level": "full"
  }
}
```

### 10.2 Example Product Response

```json
{
  "product_id": "prod_nt_001",
  "name": "Merino Wool Crew Neck",
  "slug": "merino-wool-crew-neck",
  "description": "<p>A lightweight, breathable merino wool sweater ideal for layering or wearing alone. Sustainably sourced from New Zealand farms.</p>",
  "description_plain": "A lightweight, breathable merino wool sweater ideal for layering or wearing alone. Sustainably sourced from New Zealand farms.",
  "brand": "Nordic Thread",
  "sku": "MW-CREW-001",
  "mpn": "MWC-2024-SS",
  "gtin": "05901234567890",
  "images": [
    {
      "url": "https://nordicthread.com/images/products/merino-crew-navy-1.jpg",
      "alt_text": "Merino Wool Crew Neck in Navy Blue, front view",
      "is_primary": true,
      "width": 1200,
      "height": 1600,
      "order": 1
    },
    {
      "url": "https://nordicthread.com/images/products/merino-crew-navy-2.jpg",
      "alt_text": "Merino Wool Crew Neck in Navy Blue, side view",
      "is_primary": false,
      "width": 1200,
      "height": 1600,
      "order": 2
    }
  ],
  "price": {
    "amount": 89.00,
    "currency": "USD",
    "compare_at_amount": null,
    "is_on_sale": false,
    "sale_ends_at": null
  },
  "inventory": {
    "tracked": true,
    "quantity": 58,
    "availability_status": "in_stock",
    "low_stock_threshold": 10
  },
  "categories": [
    {
      "category_id": "cat_clothing",
      "name": "Clothing",
      "path": ["Clothing", "Tops", "Sweaters"]
    }
  ],
  "variants": [
    {
      "variant_id": "var_nt_001_sm_nvy",
      "name": "Small / Navy",
      "sku": "MW-CREW-SM-NVY",
      "price": { "amount": 89.00, "currency": "USD" },
      "inventory": { "quantity": 12, "availability_status": "in_stock" },
      "options": { "size": "Small", "color": "Navy" },
      "image_url": null
    },
    {
      "variant_id": "var_nt_001_md_nvy",
      "name": "Medium / Navy",
      "sku": "MW-CREW-MD-NVY",
      "price": { "amount": 89.00, "currency": "USD" },
      "inventory": { "quantity": 18, "availability_status": "in_stock" },
      "options": { "size": "Medium", "color": "Navy" },
      "image_url": null
    },
    {
      "variant_id": "var_nt_001_lg_gry",
      "name": "Large / Heather Grey",
      "sku": "MW-CREW-LG-GRY",
      "price": { "amount": 89.00, "currency": "USD" },
      "inventory": { "quantity": 0, "availability_status": "out_of_stock" },
      "options": { "size": "Large", "color": "Heather Grey" },
      "image_url": null
    }
  ],
  "attributes": {
    "material": "100% Merino Wool (ZQ-certified)",
    "care_instructions": "Hand wash cold. Lay flat to dry.",
    "origin": "Made in Portugal",
    "fit": "Regular"
  },
  "tags": ["merino", "wool", "sweater", "sustainable", "essentials"],
  "weight": { "value": 0.4, "unit": "KG" },
  "dimensions": { "length": 68, "width": 52, "height": 2, "unit": "CM" },
  "is_active": true,
  "created_at": "2024-01-10T00:00:00Z",
  "updated_at": "2024-03-15T14:30:00Z"
}
```

### 10.3 Example Search Request and Response

**Request:**

```http
GET /api/agent/search?q=merino+sweater&min_price=50&max_price=100&availability=in_stock&sort=price_asc&page=1&per_page=20
Host: nordicthread.com
User-Agent: ClaudeAgent/1.0 (AgenticCommerce; +https://anthropic.com)
X-Agent-ID: clag_01HXYZ1234567890ABCDEFG
```

**Response:**

```json
{
  "version": "1.0.0",
  "results": [
    {
      "product_id": "prod_nt_001",
      "name": "Merino Wool Crew Neck",
      "slug": "merino-wool-crew-neck",
      "brand": "Nordic Thread",
      "price": { "amount": 89.00, "currency": "USD" },
      "availability_status": "in_stock",
      "image_url": "https://nordicthread.com/images/products/merino-crew-navy-1.jpg",
      "category_path": ["Clothing", "Tops", "Sweaters"],
      "relevance_score": 0.97
    },
    {
      "product_id": "prod_nt_003",
      "name": "Merino Wool Cardigan",
      "slug": "merino-wool-cardigan",
      "brand": "Nordic Thread",
      "price": { "amount": 119.00, "currency": "USD" },
      "availability_status": "in_stock",
      "image_url": "https://nordicthread.com/images/products/merino-cardigan-oat-1.jpg",
      "category_path": ["Clothing", "Tops", "Cardigans"],
      "relevance_score": 0.91
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total_pages": 1,
    "total_items": 2,
    "has_next": false,
    "has_prev": false
  },
  "facets": {
    "categories": [
      { "category_id": "cat_sweaters", "name": "Sweaters", "count": 1 },
      { "category_id": "cat_cardigans", "name": "Cardigans", "count": 1 }
    ],
    "price_ranges": [
      { "min": 50, "max": 100, "label": "$50 - $100", "count": 1 },
      { "min": 100, "max": 150, "label": "$100 - $150", "count": 1 }
    ],
    "brands": [
      { "name": "Nordic Thread", "count": 2 }
    ],
    "availability": [
      { "status": "in_stock", "count": 2 }
    ]
  }
}
```

---

## 11. Implementation Notes for Common Platforms

### 11.1 Shopify

Shopify stores can implement `agents.json` via a Shopify App (private app with API access). The storefront API (`/api/2024-01/graphql.json`) provides catalog data; the Cart API (`/cart.json`) handles cart operations.

**Discovery:** Shopify-hosted stores use `{store}.myshopify.com`. The `agents.json` should be served from the store's primary domain (not the `myshopify.com` subdomain). Many Shopify stores have a custom domain configured; use that.

**Agent Token Endpoint:** Shopify does not have a native agent token concept. Implement this as a custom app proxy or a thin endpoint in a Shopify Functions extension.

**Payment:** Shopify Payments (Hydrogen) and third-party payment gateways are supported. Use Shopify's Checkout API for the actual payment redirect flow.

**Implementation Path:**
1. Create a Shopify private app with Storefront API and Admin API read access.
2. Implement a thin webhook or Functions extension to emit `agents.json` from your domain.
3. Map Storefront API product variants to the `agents.json` product schema.
4. Use Shopify's Cart API (which is session-cookie based) and adapt it to the `X-Session-ID` header approach by storing session-to-cart-id mappings in your extension.

### 11.2 WooCommerce (WordPress)

WooCommerce stores are self-hosted (`.well-known/agents.json` is served from the store's document root). Use a custom WordPress plugin or a mu-plugin to:

1. Register a REST API endpoint at `/wp-json/agentbridge/v1/agents.json` as the root document.
2. Implement rewrite rules to redirect `/.well-known/agents.json` to the REST endpoint.
3. Map WooCommerce products (`WC_Product`) to the `Product` schema using `wc_get_products()` and `WC_Product::get_data()`.
4. Use WooCommerce's cart session management and extend it with `X-Session-ID` header support.
5. Use the WooCommerce REST API (`/wp-json/wc/v3/`) for the underlying cart and checkout endpoints.

**Recommended Plugin Structure:**

```
/wp-content/mu-plugins/agentbridge/
  agentbridge.php           — Main bootstrap
  class-agents-json.php     — Root document generation
  class-catalog-api.php     — Catalog/search endpoints
  class-cart-api.php        — Cart endpoints
  class-checkout-api.php    — Checkout endpoints
  class-auth.php            — Agent token handling
  class-rate-limiter.php    — Rate limiting
  class-policy-endpoints.php — Returns/shipping/privacy
```

**CORS:** WooCommerce REST API responses require appropriate CORS headers. Add:

```php
add_filter('rest_pre_serve_request', function($response) {
    header('Access-Control-Allow-Origin: *');
    header('Access-Control-Allow-Methods: GET, POST, PATCH, DELETE, OPTIONS');
    header('Access-Control-Allow-Headers: Authorization, X-Agent-Token, X-Session-ID, X-Agent-ID, Content-Type');
    return $response;
});
```

### 11.3 BigCommerce

BigCommerce provides a robust REST API (`/api/v3/`). Implement `agents.json` via a BigCommerce Single-Click App or a proxy layer:

1. **Discovery:** The `/.well-known/agents.json` should be served from the store's CDN-fronted custom domain, not the `*.bigcommerce.com` subdomain.
2. **Catalog:** Use BigCommerce's Catalog API (`/catalog/products`) for product data.
3. **Cart:** Use the Server-to-Server Cart API. Map the cart ID to `X-Session-ID`.
4. **Checkout:** BigCommerce's checkout is multi-step. Use the Checkout API (`/checkouts`) and redirect to BigCommerce's hosted checkout for payment.
5. **Authentication:** Implement agent token as a separate endpoint; BigCommerce does not natively support agent tokens.

### 11.4 Squarespace

Squarespace is a closed platform with limited API access. However, Squarespace Version 7.1 supports:

1. **Commerce API:** Limited to inventory and order management via the Squarespace Developer Platform.
2. **Scheduling and Member Areas:** Can be leveraged for basic authentication.
3. **Custom REST API:** Squarespace does not expose a public REST API for catalog access for third-party use.

**Recommendation for Squarespace:** Use Squarespace's Developer Platform to build a Squarespace Extension (iframe app) that exposes the `agents.json` endpoint. Alternatively, serve `agents.json` from an external proxy (e.g., Cloudflare Worker) that aggregates Squarespace's Commerce API responses into the standard schema.

### 11.5 Magento / Adobe Commerce

Magento 2 has a comprehensive REST API (`/rest/V1/`). To implement `agents.json`:

1. Create a dedicated Magento integration token for agent access.
2. Use the `GET /products` and `GET /categories` endpoints for catalog data.
3. Use the `POST /guest-carts` and subsequent cart endpoints for cart management.
4. Use the `POST /guest-carts/{cartId}/payment-information` and `PUT /guest-carts/{cartId}/order` for checkout.
5. Implement a `di.xml` plugin to intercept requests and enforce `X-Agent-Token` and rate limiting.
6. Use Magento's Webhooks or Queue system to handle asynchronous order confirmations.

### 11.6 Commerce.js (Headless Commerce)

Commerce.js stores are API-first by design. The `agents.json` implementation is straightforward:

1. Serve the root `agents.json` from your front-end host or CDN.
2. Use the Commerce.js Products API (`GET /products`, `GET /products/{id}`) for catalog.
3. Use the Commerce.js Cart API (`POST /carts`, `POST /carts/{id}/items`) for cart.
4. Use the Commerce.js Checkout API (`GET /checkout`, `POST /checkout`) for checkout.
5. Map Commerce.js's `cart.friendly_id` to `X-Session-ID`.

### 11.7 Saleor (Open Source)

Saleor is an open-source GraphCommerce platform with a GraphQL API. For `agents.json` compliance:

1. Serve the root `agents.json` from the Saleor storefront host.
2. Use the GraphQL API for all catalog, cart, and checkout operations (the primary API).
3. Saleor Dashboard does not have a native `agents.json` emitter — implement a thin webhook or middleware that generates the document from Saleor's database.
4. Use Saleor's `checkoutCreate`, `checkoutLinesAdd`, `checkoutComplete` mutations.
5. Implement an `X-Session-ID` to `checkout.id` mapping in a thin middleware layer.

### 11.8 Shopify Hydrogen (React-Based Storefront)

Shopify Hydrogen uses Remix-based routing. To expose `agents.json`:

1. Add a route handler for `/.well-known/agents.json` that calls the Storefront API and transforms the response.
2. Use Hydrogen's `storefront` client for all data fetching.
3. For cart operations, Hydrogen uses the Cart API; adapt it to the `X-Session-ID` header model.
4. Agent authentication is handled via Shopify's Customer Accounts API.

### 11.9 General Platform-Agnostic Notes

**Reverse Proxy Approach:** The cleanest implementation for any platform is to run a thin reverse proxy (e.g., Cloudflare Worker, nginx, or a serverless function) in front of the existing store API. The proxy:
- Serves `agents.json` at `/.well-known/agents.json`
- Translates the `agents.json` schema into the store's native API format
- Enforces `X-Agent-Token` and rate limiting
- Maps `X-Session-ID` to the store's native session/cart model

**Schema Mapping Table:**

| agents.json Field | Shopify Field | WooCommerce Field | BigCommerce Field |
|---|---|---|---|
| `product_id` | `node.id` | `product.id` | `product.id` |
| `name` | `node.title` | `product.name` | `product.name` |
| `price.amount` | `node.priceRange.minVariantPrice.amount` | `product.price` | `product.price` |
| `inventory.quantity` | `node.quantityAvailable` | `product.stock_quantity` | `product.inventory_level` |
| `availability_status` | derived from quantity | derived from stock_status | `product.inventory_tracked` + level |

**Testing:** Use the official AgentBridge compliance test suite at `https://github.com/Petec79/agentbridge/testing/compliance/` to validate your implementation.

---

## Appendix A: HTTP Status Codes

| Code | Meaning |
|------|---------|
| `200 OK` | Request succeeded. |
| `201 Created` | Resource created (e.g., cart, order). |
| `400 Bad Request` | Invalid request body or parameters. |
| `401 Unauthorized` | Missing or invalid agent token. |
| `403 Forbidden` | Agent lacks permission for this action. Also used for policy violations. |
| `404 Not Found` | Resource does not exist. |
| `409 Conflict` | State conflict (e.g., cart already contains item). |
| `410 Gone` | Resource was permanently deleted. |
| `422 Unprocessable Entity` | Validation error (e.g., item out of stock). |
| `429 Too Many Requests` | Rate limit exceeded. |
| `500 Internal Server Error` | Unexpected server error. |
| `503 Service Unavailable` | Store's agent API is temporarily down. |

## Appendix B: Error Response Schema

All error responses MUST use this format:

```json
{
  "error": {
    "code": "string (machine-readable error code)",
    "message": "string (human-readable message for debugging, never PII)",
    "field": "string (optional — field that caused the error)",
    "policy_violation": "string (optional — present when 403 is due to a usage policy)"
  },
  "request_id": "string (opaque request ID for support tickets)"
}
```

**Standard Error Codes:**

| Code | Description |
|------|-------------|
| `INVALID_PRODUCT_ID` | Product does not exist. |
| `INVALID_VARIANT_ID` | Variant does not exist for this product. |
| `OUT_OF_STOCK` | Item is out of stock. |
| `INSUFFICIENT_INVENTORY` | Not enough inventory for requested quantity. |
| `INVALID_TOKEN` | Agent token is missing, expired, or invalid. |
| `RATE_LIMIT_EXCEEDED` | Too many requests. |
| `POLICY_VIOLATION` | Request violates store usage policy. |
| `CART_EXPIRED` | Cart session has expired. |
| `CHECKOUT_CLOSED` | Checkout session is no longer active. |
| `INVALID_ADDRESS` | Shipping or billing address is invalid. |
| `PAYMENT_FAILED` | Payment processing failed. |
| `ITEM_NOT_ELIGIBLE_FOR_RETURN` | This item cannot be returned per policy. |

## Appendix C: IANA Considerations

This specification requests the registration of the well-known URI suffix `agents.json` in the "Well-Known URI Suffixes" registry as defined by RFC 8615.

**URI Suffix:** `agents.json`  
**Change Controller:** AgentBridge Working Group  
**Specification:** (this document)

## Appendix D: Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024-06-01 | Initial draft specification |

---

*This specification is maintained by the AgentBridge Working Group. Feedback and contributions are welcome at https://github.com/agentbridge/spec*
