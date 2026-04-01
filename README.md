# agents.json — The Open Standard for Agentic Commerce

<p align="center">
  <strong>AI agents can't shop online — not because they're not smart enough, but because no standard lets them.</strong>
</p>

<p align="center">
  agents.json changes that. It's a machine-readable contract published by any online store — like robots.txt, but for commerce. Any AI agent that supports it can immediately browse, cart, and checkout at any compliant store, without a single line of store-specific code.
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

Right now, if you want an AI agent to buy something from a Shopify store, someone has to write a custom Shopify adapter. For WooCommerce, another adapter. For BigCommerce, another. And for every new store, start over.

This is the situation web search was in before robots.txt — every crawler needed custom rules for every site. Then the standard emerged, and suddenly all search engines and all websites spoke the same language.

**E-commerce is waiting for its robots.txt moment.** agents.json is that standard.

## What You Get

```
Any compliant agent  +  Any compliant store  =  General-purpose AI shopping
```

Once a store publishes `agents.json`, any supporting agent can:
- Discover the store's catalog without a per-store integration
- Search products with structured, machine-readable results
- Add items to a cart and checkout using a standard API
- Read policies (returns, shipping, privacy) automatically

The same agent that shops your store can shop any other store. No new code required.

## Status

**v1.0.0 — Published and Stable.** The spec is frozen and suitable for production. Reference implementations are live.

## Quick Start

### Store Operators

Add `agents.json` to your root domain:

```
https://yourstore.com/agents.json
```

Or use the RFC 8615 well-known path:

```
https://yourstore.com/.well-known/agents.json
```

See the [full specification](SPEC.md) for the schema.

### Agent Developers

Any agent that makes HTTP requests can implement agents.json support in a day:

```bash
curl https://any-store.com/agents.json  # discovery
curl https://any-store.com/catalog       # browse products
curl https://any-store.com/search?q=...  # search
POST https://any-store.com/cart/items    # add to cart
POST https://any-store.com/checkout      # purchase
```

Reference clients:
- [JavaScript client](implementations/javascript/) — Node.js / browser
- [Python client](implementations/python/) — Python 3.10+

## Live Demo

The reference Python/FastAPI server is running:

```bash
curl http://127.0.0.1:5000/agents.json   # discovery doc
curl http://127.0.0.1:5000/catalog        # product catalog
curl http://127.0.0.1:5000/search?q=shoes # search
```

## Reference Implementations

| Platform | Status | Link |
|----------|--------|------|
| Python/FastAPI Server | Live demo at `127.0.0.1:5000` | `implementations/python/` |
| MCP Server (TypeScript) | Reference implementation | `mcp-server/` |
| Shopify Storefront Proxy | Live | `implementations/shopify-proxy/` |
| Cloudflare Worker | Planned | — |
| Shopify App | Planned | — |
| WooCommerce Plugin | Planned | — |

## Why Open Source the Spec?

The moat is not the specification — it's **adoption**. If every store speaks agents.json, every agent uses it. If every agent checks for it, every store must publish it.

This is the SSL/robots.txt model: the standard creates the network effect, not the implementation.

We publish under Apache 2.0 with W3C CLA for contributions. No company owns agents.json. Everyone can implement it.

## Contributing

We welcome contributions from:
- **Agent developers** who want to shop the network
- **Store platform maintainers** who want their merchants discoverable by agents
- **E-commerce operators** who want early agent traffic
- **Standards engineers** who want to harden the spec

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to propose changes.

## The Strategic Thesis

> Every $1 spent on software, $6 is spent on services. The next legendary company sells the work — not the tool.
>
> *— Sequoia Capital, ["Services: The New Software"](https://sequoiacap.com/article/services-the-new-software/)*

AgentBridge applies this thesis to commerce. The work is "make a purchase at the best price from a trusted store." The tool is the store's website. The agent that does this work for the consumer captures the full commerce budget.

`agents.json` is the protocol layer that makes this work. The spec is the moat.

## License

Apache 2.0 — see [LICENSE](LICENSE)
