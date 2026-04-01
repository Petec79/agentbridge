# AgentBridge MCP Server

Model Context Protocol (MCP) server that implements the `agents.json` open standard. Any MCP-compatible AI client (Claude Desktop, Cursor, etc.) can use this to shop any `agents.json`-compliant store natively.

## What This Does

This MCP server exposes the full `agents.json` commerce API as MCP tools:

- `agents_json_get_store_info` — Store identity and capabilities
- `agents_json_search` — Natural language product search  
- `agents_json_get_product` — Full product details
- `agents_json_get_catalog` — Browse product catalog (paginated)
- `agents_json_add_to_cart` — Add item to cart
- `agents_json_get_cart` — View current cart
- `agents_json_checkout` — Complete purchase

When an AI agent has this server installed, it can shop at any `agents.json`-compliant store the same way it would query a database or filesystem.

## Architecture

```
AI Agent (Claude/Cursor/etc.)
        │
        │ MCP protocol
        ▼
AgentBridge MCP Server
        │
        │ agents.json HTTP API
        ▼
Any agents.json-compliant store
(Shopify, WooCommerce, custom, etc.)
```

## Setup

```bash
# Install dependencies
npm install

# Configure (add your store's agents.json endpoint, or use the demo)
cp .env.example .env

# Start the server
npm run start
```

## MCP Configuration

Add to your MCP client config (e.g. Claude Desktop):

```json
{
  "mcpServers": {
    "agentbridge": {
      "command": "node",
      "args": ["/path/to/agentbridge/mcp-server/dist/index.js"],
      "env": {
        "AGENT_ID": "your-agent-name"
      }
    }
  }
}
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `AGENT_ID` | Yes | Unique identifier for this agent |
| `DEFAULT_STORE_URL` | No | Default store to connect to |
| `RATE_LIMIT_MAX` | No | Max requests per minute (default: 60) |

## Example Conversation

**User:** Find me wireless headphones under $100

**Claude (via AgentBridge MCP):**
```
Tool: agents_json_search
Input: { "query": "wireless headphones", "maxPrice": 100 }
```
```
Tool: agents_json_get_product  
Input: { "productId": "prod_12345" }
```
```
Added Sennheiser HD 350BT Wireless Headphones ($89) to your cart.

Order confirmed: ORD-2026-0401-8834
```

## Status

**Alpha** — Reference implementation. The agents.json spec is v1.0.0-draft. This server tracks the spec closely.

## License

Apache 2.0
