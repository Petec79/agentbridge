# agents.json — The Open Standard for Agentic Commerce

<p align="center">
  <strong>agents.json is to shopping what robots.txt is to search.</strong>
</p>

<p align="center">
  A machine-readable contract that lets any AI agent — Claude, GPT, Gemini, Grok, or any other — discover products, browse catalogs, and complete purchases at any compliant store, without store-specific integration code.
</p>

<p align="center">
  <a href="https://github.com/Petec79/agentbridge/stargazers"><img src="https://img.shields.io/github/stars/Petec79/agentbridge?style=flat&label=Stars" alt="GitHub Stars"></a>
  <a href="https://github.com/Petec79/agentbridge/releases/tag/v1.0.0">v1.0.0</a> ·
  <a href="https://github.com/Petec79/agentbridge/blob/main/SPEC.md">Specification</a> ·
  <a href="https://agentbridge.org">Website</a> ·
  <a href="https://discord.gg/agentbridge">Discord</a>
</p>

---

## The Problem

AI shopping agents today must be hard-coded to each store's unique API, payment processor, and checkout flow. A Shopify store, a WooCommerce boutique, and a Squarespace retailer all require separate integrations. This fragmentation prevents AI agents from acting as general-purpose shopping assistants.

## The Solution

`agents.json` is a JSON document published at a store's root domain (or `/.well-known/agents.json`). It declares:

- **Store identity** — name, branding, contact
- **API endpoints** — catalog, search, cart, checkout
- **Authentication** — how agents identify themselves vs. humans
- **Product schema** — structured product data any agent can parse
- **Policies** — returns, refunds, shipping, privacy
- **Rate limits** — so agents behave responsibly

Any compliant agent can shop any compliant store. Implement once, access the entire network.

## Status

**v1.0.0 — Published (Stable).** The spec is considered stable and suitable for production use. We welcome feedback from agent developers and e-commerce platform maintainers.

## Quick Start

### For Store Operators

Add `agents.json` to your store's root:

```
https://yourstore.com/agents.json
```

Or for RFC 8615 compliance:

```
https://yourstore.com/.well-known/agents.json
```

See the [full specification](SPEC.md) for the schema.

### For Agent Developers

Any agent that makes HTTP requests can implement agents.json support in a day. Fetch the root document, parse the endpoints, start shopping.

Reference clients:
- [agents.json JavaScript client](implementations/javascript/) — Node.js / browser
- [agents.json Python client](implementations/python/) — Python 3.10+

## Implementations

| Platform | Status | Link |
|----------|--------|------|
| Python/FastAPI Server | Live — Running demo at `127.0.0.1:5000` | `implementations/python/` |
| MCP Server (TypeScript) | Reference | `mcp-server/` |
| Shopify App | Planned | `implementations/shopify/` |
| WooCommerce Plugin | Planned | `implementations/woocommerce/` |

## Live Demo

The reference Python/FastAPI server is running at `http://127.0.0.1:5000`:

```bash
curl http://127.0.0.1:5000/agents.json  # discovery doc
curl http://127.0.0.1:5000/catalog       # product catalog
curl http://127.0.0.1:5000/search?q=...  # search
curl -X POST http://127.0.0.1:5000/cart/items -d '{"product_id":"prod_001"}'  # add to cart
```

An AI agent can complete a full purchase flow: discover → browse → add to cart → checkout → pay.

## Why Open Source the Spec?

The moat is not the specification — it's the **adoption**. If every store speaks agents.json, every agent uses it. If every agent checks for it, every store must publish it. This is the SSL/robots.txt model: the standard creates the network effect, not the implementation.

We publish under [Apache 2.0](LICENSE) with [W3C CLA](CONTRIBUTING.md) for contributions. No company owns agents.json. Everyone can implement it.

## Contributing

We welcome contributions from:
- **Agent developers** who want to shop the network
- **Store platform maintainers** who want their merchants discoverable by agents
- **E-commerce operators** who want early agent traffic
- **Standards engineers** who want to harden the spec

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to propose changes to the spec.

## The Strategic Thesis

> Every $1 spent on software, $6 is spent on services. The next legendary company sells the work — not the tool.
> 
> *— Sequoia Capital, ["Services: The New Software"](https://sequoiacap.com/article/services-the-new-software/)*

AgentBridge applies this thesis to commerce. The work is "make a purchase at the best price from a trusted store." The tool is the store's website. The agent that does this work for the consumer captures the full commerce budget — not the SaaS subscription.

`agents.json` is the protocol layer that makes this work. The spec is the moat.

## License

Apache 2.0 — see [LICENSE](LICENSE)
