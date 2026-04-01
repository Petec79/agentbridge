# agents.json Python Client

Reference implementation of the agents.json client for Python 3.10+.

## Installation

```bash
pip install agentbridge
```

## Usage

```python
from agentbridge import AgentBridgeClient

# Connect to any agents.json-compliant store
store = AgentBridgeClient("https://shop.example.com")

# Fetch store info and capabilities
info = store.get_store_info()
print(f"{info['name']} supports {', '.join(info['capabilities'])}")

# Search products
results = store.search(query="wireless headphones", max_price=100)
for product in results["products"]:
    print(f"{product['name']} — ${product['price']}")

# Add to cart
cart = store.add_to_cart(product_id=results["products"][0]["product_id"], quantity=1)

# Checkout
order = store.checkout(cart_id=cart["cart_id"], payment_method_id="pm_card_visa")
print(f"Order confirmed: {order['confirmation_number']}")
```

## Agent Identification

The client automatically sets:
- `User-Agent: agentbridge-python/1.0 (agentic-commerce-client)`
- `X-Agent-ID: <agent-id>`
- `X-Session-ID: <session-id>`

## License

Apache 2.0
