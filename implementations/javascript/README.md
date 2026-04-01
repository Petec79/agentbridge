# agents.json JavaScript Client

Reference implementation of the agents.json client for Node.js and browser environments.

## Installation

```bash
npm install @agentbridge/js-client
```

## Usage

```javascript
import { AgentBridgeClient } from '@agentbridge/js-client';

// Connect to any agents.json-compliant store
const store = new AgentBridgeClient('https://shop.example.com');

// Fetch store info and capabilities
const info = await store.getStoreInfo();
console.log(`${info.name} supports ${info.capabilities.join(', ')}`);

// Search products
const results = await store.search({ query: 'wireless headphones', maxPrice: 100 });
for (const product of results.products) {
  console.log(`${product.name} — $${product.price}`);
}

// Add to cart
const cart = await store.addToCart({ productId: results.products[0].product_id, quantity: 1 });

// Checkout
const order = await store.checkout({ cartId: cart.cart_id, paymentMethodId: 'pm_card_visa' });
console.log(`Order confirmed: ${order.confirmation_number}`);
```

## API

### `new AgentBridgeClient(storeDomain, options?)`

- `storeDomain`: The base domain of the store (e.g. `https://shop.example.com`)
- `options.agentId`: Your agent's identifier (default: auto-detected from User-Agent)
- `options.sessionId`: Optional session ID for tracking across requests

### Methods

| Method | Description |
|--------|-------------|
| `getStoreInfo()` | Returns store metadata and declared capabilities |
| `getCatalog(page?)` | Returns paginated product catalog |
| `getProduct(productId)` | Returns full product details |
| `search(query)` | Search with natural language or structured filters |
| `getCart()` | Get current cart |
| `addToCart({ productId, quantity })` | Add item to cart |
| `removeFromCart({ productId })` | Remove item from cart |
| `updateCartItem({ productId, quantity })` | Update item quantity |
| `clearCart()` | Empty the cart |
| `initCheckout()` | Initialize checkout session |
| `confirmCheckout({ paymentMethodId })` | Confirm and pay |
| `getOrderHistory()` | Returns past orders (requires authentication) |

## Agent Identification

When making requests, the client sets the following headers automatically:

```
User-Agent: agentbridge-js/1.0 (agentic-commerce-client)
X-Agent-ID: <agent-id>
X-Session-ID: <session-id>
```

Stores use these to identify agent vs. human traffic, apply appropriate rate limits, and track agent purchase behavior for analytics.

## License

Apache 2.0
