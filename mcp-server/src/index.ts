import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

// agents.json MCP Server
// Implements the agents.json open standard as MCP tools

interface StoreConfig {
  baseUrl: string;
  agentId: string;
  sessionId?: string;
}

async function fetchAgentsJson(baseUrl: string, path: string = "/agents.json") {
  const url = `${baseUrl.replace(/\/$/, '')}${path}`;
  const res = await fetch(url, {
    headers: {
      "Accept": "application/json",
      "User-Agent": "agentbridge-mcp/0.1.0 (agentic-commerce-server)"
    }
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}: ${url}`);
  return res.json();
}

async function apiRequest(baseUrl: string, endpoint: string, options: RequestInit = {}) {
  const url = `${baseUrl.replace(/\/$/, '')}${endpoint}`;
  const res = await fetch(url, {
    ...options,
    headers: {
      "Accept": "application/json",
      "Content-Type": "application/json",
      "User-Agent": "agentbridge-mcp/0.1.0 (agentic-commerce-client)",
      ...options.headers
    }
  });
  if (!res.ok) {
    const error = await res.text();
    throw new Error(`HTTP ${res.status}: ${error}`);
  }
  return res.json();
}

const server = new Server(
  {
    name: "agentbridge-mcp-server",
    version: "0.1.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "agents_json_get_store_info",
        description: "Get store identity, branding, and declared capabilities from an agents.json-compliant store",
        inputSchema: {
          type: "object",
          properties: {
            storeUrl: { type: "string", description: "Store domain or full agents.json URL" }
          },
          required: ["storeUrl"]
        }
      },
      {
        name: "agents_json_search",
        description: "Search products at an agents.json-compliant store using natural language or structured filters",
        inputSchema: {
          type: "object",
          properties: {
            storeUrl: { type: "string", description: "Store domain or full agents.json URL" },
            query: { type: "string", description: "Natural language search query" },
            category: { type: "string", description: "Filter by category" },
            minPrice: { type: "number", description: "Minimum price" },
            maxPrice: { type: "number", description: "Maximum price" },
            limit: { type: "number", description: "Max results (default 20)" }
          },
          required: ["storeUrl"]
        }
      },
      {
        name: "agents_json_get_product",
        description: "Get full product details by product ID",
        inputSchema: {
          type: "object",
          properties: {
            storeUrl: { type: "string", description: "Store domain or full agents.json URL" },
            productId: { type: "string", description: "Product ID from search results" }
          },
          required: ["storeUrl", "productId"]
        }
      },
      {
        name: "agents_json_add_to_cart",
        description: "Add a product to the shopping cart",
        inputSchema: {
          type: "object",
          properties: {
            storeUrl: { type: "string", description: "Store domain or full agents.json URL" },
            productId: { type: "string", description: "Product ID" },
            quantity: { type: "number", description: "Quantity (default 1)" }
          },
          required: ["storeUrl", "productId"]
        }
      },
      {
        name: "agents_json_get_cart",
        description: "View the current shopping cart",
        inputSchema: {
          type: "object",
          properties: {
            storeUrl: { type: "string", description: "Store domain or full agents.json URL" }
          },
          required: ["storeUrl"]
        }
      },
      {
        name: "agents_json_checkout",
        description: "Complete the purchase with a payment method",
        inputSchema: {
          type: "object",
          properties: {
            storeUrl: { type: "string", description: "Store domain or full agents.json URL" },
            paymentMethodId: { type: "string", description: "Payment method ID (e.g. card token)" }
          },
          required: ["storeUrl", "paymentMethodId"]
        }
      }
    ]
  };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case "agents_json_get_store_info": {
        const root = await fetchAgentsJson(args.storeUrl as string);
        return {
          content: [{
            type: "text" as const,
            text: JSON.stringify(root, null, 2)
          }]
        };
      }

      case "agents_json_search": {
        const root = await fetchAgentsJson(args.storeUrl as string);
        const searchEndpoint = root.endpoints?.search;
        if (!searchEndpoint) throw new Error("Store does not support search");

        const params = new URLSearchParams();
        if (args.query) params.set("q", args.query as string);
        if (args.category) params.set("category", args.category as string);
        if (args.minPrice) params.set("min_price", String(args.minPrice));
        if (args.maxPrice) params.set("max_price", String(args.maxPrice));
        if (args.limit) params.set("limit", String(args.limit));

        const results = await apiRequest(args.storeUrl as string, `${searchEndpoint}?${params}`);
        return {
          content: [{ type: "text" as const, text: JSON.stringify(results, null, 2) }]
        };
      }

      case "agents_json_get_product": {
        const root = await fetchAgentsJson(args.storeUrl as string);
        const catalogEndpoint = root.endpoints?.product;
        if (!catalogEndpoint) throw new Error("Store does not expose products");

        const results = await apiRequest(args.storeUrl as string, `${catalogEndpoint.replace('{productId}', args.productId as string)}`);
        return {
          content: [{ type: "text" as const, text: JSON.stringify(results, null, 2) }]
        };
      }

      case "agents_json_add_to_cart": {
        const root = await fetchAgentsJson(args.storeUrl as string);
        const cartEndpoint = root.endpoints?.cart?.add;
        if (!cartEndpoint) throw new Error("Store does not support cart operations");

        const result = await apiRequest(args.storeUrl as string, cartEndpoint, {
          method: "POST",
          body: JSON.stringify({
            product_id: args.productId,
            quantity: args.quantity ?? 1
          })
        });
        return {
          content: [{ type: "text" as const, text: JSON.stringify(result, null, 2) }]
        };
      }

      case "agents_json_get_cart": {
        const root = await fetchAgentsJson(args.storeUrl as string);
        const cartEndpoint = root.endpoints?.cart?.get;
        if (!cartEndpoint) throw new Error("Store does not support cart operations");

        const result = await apiRequest(args.storeUrl as string, cartEndpoint);
        return {
          content: [{ type: "text" as const, text: JSON.stringify(result, null, 2) }]
        };
      }

      case "agents_json_checkout": {
        const root = await fetchAgentsJson(args.storeUrl as string);
        const checkoutEndpoint = root.endpoints?.checkout?.initiate;
        if (!checkoutEndpoint) throw new Error("Store does not support checkout");

        // Step 1: Init checkout
        const checkout = await apiRequest(args.storeUrl as string, checkoutEndpoint, {
          method: "POST"
        });

        // Step 2: Confirm with payment
        const confirmEndpoint = root.endpoints?.checkout?.confirm;
        if (!confirmEndpoint) throw new Error("Store checkout does not support confirmation");

        const order = await apiRequest(args.storeUrl as string, confirmEndpoint, {
          method: "POST",
          body: JSON.stringify({
            checkout_id: checkout.checkout_id,
            payment_method_id: args.paymentMethodId
          })
        });

        return {
          content: [{ type: "text" as const, text: JSON.stringify(order, null, 2) }]
        };
      }

      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error: any) {
    return {
      content: [{ type: "text" as const, text: `Error: ${error.message}` }],
      isError: true
    };
  }
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("AgentBridge MCP Server running on stdio");
}

main().catch(console.error);
