const express = require('express');
const cors = require('cors');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 3334;
const DATA_DIR = path.join(__dirname, 'data');
const STORES_FILE = path.join(DATA_DIR, 'stores.json');

// Ensure data directory exists
if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR, { recursive: true });
if (!fs.existsSync(STORES_FILE)) fs.writeFileSync(STORES_FILE, JSON.stringify({}));

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// ─── Helpers ─────────────────────────────────────────────────────────────────

function loadStores() {
  return JSON.parse(fs.readFileSync(STORES_FILE, 'utf8'));
}

function saveStores(stores) {
  fs.writeFileSync(STORES_FILE, JSON.stringify(stores, null, 2));
}

function slugify(url) {
  try {
    const u = new URL(url);
    return u.hostname.replace(/[^a-z0-9]/gi, '-').toLowerCase();
  } catch {
    return url.replace(/[^a-z0-9]/gi, '-').toLowerCase();
  }
}

async function shopifyGraphQL(storeUrl, token, query, variables = {}) {
  const endpoint = `${storeUrl.replace(/\/$/, '')}/api/2024-01/graphql.json`;
  const r = await fetch(endpoint, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Shopify-Storefront-Access-Token': token,
    },
    body: JSON.stringify({ query, variables }),
  });
  if (!r.ok) throw new Error(`Shopify API error: ${r.status} ${r.statusText}`);
  const json = await r.json();
  if (json.errors) throw new Error(json.errors[0].message);
  return json.data;
}

// ─── agents.json endpoint ─────────────────────────────────────────────────────

app.get('/stores/:slug/agents.json', async (req, res) => {
  try {
    const { slug } = req.params;
    const stores = loadStores();
    const store = stores[slug];

    if (!store) {
      return res.status(404).json({ error: 'Store not found. Register at /dashboard' });
    }

    // ── Discovery: store info ──────────────────────────────────────────────
    const discoveryQuery = `
      query {
        shop {
          name
          description
          primaryDomain { url }
        }
      }
    `;
    const shopData = await shopifyGraphQL(store.storeUrl, store.token, discoveryQuery);
    const shop = shopData.shop;

    // ── Catalog: products ──────────────────────────────────────────────────
    const catalogQuery = `
      query($first: Int!) {
        products(first: $first) {
          edges {
            node {
              id
              title
              description
              handle
              priceRange { minVariantPrice { amount currencyCode } }
              featuredImage { url altText }
              images(first: 1) { edges { node { url altText } } }
              variants(first: 10) {
                edges {
                  node {
                    id
                    title
                    price { amount currencyCode }
                    availableForSale
                  }
                }
              }
              tags
              productType
            }
          }
        }
      }
    `;
    const catalogData = await shopifyGraphQL(store.storeUrl, store.token, catalogQuery, { first: 50 });
    const products = catalogData.products.edges.map(({ node: p }) => {
      const img = p.images.edges[0]?.node;
      return {
        product_id: p.id.split('/').pop(),
        name: p.title,
        description: p.description?.slice(0, 500) || '',
        url: `${shop.primaryDomain.url}/products/${p.handle}`,
        image: img?.url || null,
        price: {
          amount: p.priceRange.minVariantPrice.amount,
          currency: p.priceRange.minVariantPrice.currencyCode,
        },
        variants: p.variants.edges.map(({ node: v }) => ({
          variant_id: v.id.split('/').pop(),
          name: v.title !== 'Default Title' ? v.title : p.title,
          price: { amount: v.price.amount, currency: v.price.currencyCode },
          in_stock: v.availableForSale,
        })),
        tags: p.tags.filter(t => !t.startsWith('_')),
        category: p.productType || null,
      };
    });

    // ── policies ───────────────────────────────────────────────────────────
    const policiesQuery = `
      query {
        shop {
          refundPolicy {
            title
            body
          }
          privacyPolicy {
            title
            body
          }
          termsOfService {
            title
            body
          }
        }
      }
    `;
    let policies = {};
    try {
      const polData = await shopifyGraphQL(store.storeUrl, store.token, policiesQuery);
      policies = {
        refund: polData.shop.refundPolicy?.body || null,
        privacy: polData.shop.privacyPolicy?.body || null,
        terms: polData.shop.termsOfService?.body || null,
      };
    } catch {}

    // ── Assemble agents.json ────────────────────────────────────────────────
    const agentsJson = {
      protocol: 'https://agentbridge.org/spec/v1',
      version: '1.0.0',
      store: {
        name: shop.name,
        url: shop.primaryDomain.url,
        description: shop.description || null,
      },
      capabilities: ['discovery', 'browse', 'cart', 'checkout'],
      endpoints: {
        catalog: `/stores/${slug}/catalog`,
        search: `/stores/${slug}/search`,
        cart: {
          create: `POST /stores/${slug}/cart`,
          add: `POST /stores/${slug}/cart/items`,
          remove: `DELETE /stores/${slug}/cart/items`,
          view: `GET /stores/${slug}/cart`,
        },
        checkout: {
          init: `POST /stores/${slug}/checkout`,
          confirm: `POST /stores/${slug}/checkout/confirm`,
        },
      },
      products,
      policies,
      metadata: {
        generated_at: new Date().toISOString(),
        proxy_url: `http://62.171.140.140:${PORT}/stores/${slug}`,
      },
    };

    res.json(agentsJson);
  } catch (err) {
    console.error(`[/stores/${req.params.slug}/agents.json]`, err.message);
    res.status(500).json({ error: err.message });
  }
});

// ─── Catalog endpoint ─────────────────────────────────────────────────────────
app.get('/stores/:slug/catalog', (req, res) => {
  // Redirect to agents.json
  res.redirect(`/stores/${req.params.slug}/agents.json`);
});

// ─── Search endpoint ──────────────────────────────────────────────────────────
app.get('/stores/:slug/search', async (req, res) => {
  try {
    const { slug } = req.params;
    const { q } = req.query;
    const stores = loadStores();
    const store = stores[slug];
    if (!store) return res.status(404).json({ error: 'Store not found' });

    const searchQuery = `
      query($query: String!) {
        products(first: 20, query: $query) {
          edges {
            node {
              id
              title
              handle
              description
              priceRange { minVariantPrice { amount currencyCode } }
              images(first: 1) { edges { node { url altText } } }
            }
          }
        }
      }
    `;
    const data = await shopifyGraphQL(store.storeUrl, store.token, searchQuery, { query: q || '' });
    const results = data.products.edges.map(({ node: p }) => {
      const img = p.images.edges[0]?.node;
      return {
        product_id: p.id.split('/').pop(),
        name: p.title,
        description: p.description?.slice(0, 300) || '',
        url: `${store.storeUrl}/products/${p.handle}`,
        image: img?.url || null,
        price: { amount: p.priceRange.minVariantPrice.amount, currency: p.priceRange.minVariantPrice.currencyCode },
      };
    });
    res.json({ query: q, count: results.length, products: results });
  } catch (err) {
    console.error(`[/stores/${req.params.slug}/search]`, err.message);
    res.status(500).json({ error: err.message });
  }
});

// ─── Cart endpoints ───────────────────────────────────────────────────────────
// In-memory cart store (per proxy instance)
const carts = new Map();

app.post('/stores/:slug/cart', (req, res) => {
  const { slug } = req.params;
  const { items = [] } = req.body;
  const cartId = `${slug}-${Date.now()}`;
  carts.set(cartId, { slug, items, created_at: new Date().toISOString() });
  res.json({ cart_id: cartId, items, total: items.length });
});

app.post('/stores/:slug/cart/items', (req, res) => {
  const { slug } = req.params;
  const { cart_id, product_id, quantity = 1 } = req.body;
  const cart = carts.get(cart_id);
  if (!cart || cart.slug !== slug) return res.status(404).json({ error: 'Cart not found' });
  const existing = cart.items.find(i => i.product_id === product_id);
  if (existing) {
    existing.quantity += quantity;
  } else {
    cart.items.push({ product_id, quantity });
  }
  res.json({ cart_id, items: cart.items, total: cart.items.length });
});

app.get('/stores/:slug/cart', (req, res) => {
  const { slug } = req.params;
  const { cart_id } = req.query;
  const cart = carts.get(cart_id);
  if (!cart || cart.slug !== slug) return res.status(404).json({ error: 'Cart not found' });
  res.json({ cart_id, items: cart.items, total: cart.items.length });
});

app.delete('/stores/:slug/cart/items', (req, res) => {
  const { slug } = req.params;
  const { cart_id, product_id } = req.body;
  const cart = carts.get(cart_id);
  if (!cart || cart.slug !== slug) return res.status(404).json({ error: 'Cart not found' });
  cart.items = cart.items.filter(i => i.product_id !== product_id);
  res.json({ cart_id, items: cart.items, total: cart.items.length });
});

// ─── Checkout endpoint ────────────────────────────────────────────────────────
app.post('/stores/:slug/checkout', async (req, res) => {
  try {
    const { slug } = req.params;
    const { cart_id, email } = req.body;
    const stores = loadStores();
    const store = stores[slug];
    if (!store) return res.status(404).json({ error: 'Store not found' });
    if (!cart_id) return res.status(400).json({ error: 'cart_id required' });

    const cart = carts.get(cart_id);
    if (!cart || cart.slug !== slug) return res.status(404).json({ error: 'Cart not found or expired' });

    // Build Shopify checkout URL — uses /cart/{variant_id}:{qty} format
    // cart.items stores product_id (numeric Shopify ID). For single-variant products
    // this works directly. For multi-variant products the agent should pass variant_id.
    const variantParts = cart.items.map(item => `${item.product_id}:${item.quantity}`);
    const checkoutUrl = new URL(`${store.storeUrl}/cart/${variantParts.join(',')}`);
    if (email) checkoutUrl.searchParams.append('email', email);

    const confirmation = `ORD-${Date.now().toString(36).toUpperCase()}`;
    carts.delete(cart_id);

    res.json({
      checkout_id: confirmation,
      checkout_url: checkoutUrl.toString(),
      confirmation_number: confirmation,
      status: 'redirect_to_store_checkout',
    });
  } catch (err) {
    console.error(`[/stores/${req.params.slug}/checkout]`, err.message);
    res.status(500).json({ error: err.message });
  }
});

// ─── Dashboard & API ─────────────────────────────────────────────────────────

app.get('/dashboard', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'dashboard.html'));
});

app.get('/api/stores', (req, res) => {
  const stores = loadStores();
  const list = Object.entries(stores).map(([slug, s]) => ({
    slug,
    store_name: s.storeName,
    store_url: s.storeUrl,
    registered_at: s.registeredAt,
    products_count: s.productsCount || null,
  }));
  res.json(list);
});

app.get('/api/stores/:slug', (req, res) => {
  const stores = loadStores();
  const store = stores[req.params.slug];
  if (!store) return res.status(404).json({ error: 'Not found' });
  res.json({ slug: req.params.slug, ...store });
});

app.delete('/api/stores/:slug', (req, res) => {
  const stores = loadStores();
  if (!stores[req.params.slug]) return res.status(404).json({ error: 'Not found' });
  delete stores[req.params.slug];
  saveStores(stores);
  res.json({ ok: true });
});

app.post('/api/stores', async (req, res) => {
  try {
    const { storeUrl, token, storeName } = req.body;
    if (!storeUrl || !token) {
      return res.status(400).json({ error: 'storeUrl and token are required' });
    }

    // Normalize store URL
    let baseUrl = storeUrl.replace(/\/$/, '');
    if (!baseUrl.startsWith('http')) baseUrl = 'https://' + baseUrl;

    // Generate slug from hostname
    const slug = slugify(baseUrl);

    // Validate token by fetching shop info
    try {
      await shopifyGraphQL(baseUrl, token, `{ shop { name } }`);
    } catch (e) {
      return res.status(401).json({ error: 'Invalid Storefront API token or store URL', detail: e.message });
    }

    const stores = loadStores();
    if (stores[slug]) {
      // Update existing
      stores[slug] = { storeUrl: baseUrl, token, storeName: storeName || baseUrl, registeredAt: stores[slug].registeredAt, updatedAt: new Date().toISOString() };
    } else {
      stores[slug] = { storeUrl: baseUrl, token, storeName: storeName || baseUrl, registeredAt: new Date().toISOString() };
    }
    saveStores(stores);

    res.json({ slug, store_url: baseUrl, agents_json_url: `http://62.171.140.140:${PORT}/stores/${slug}/agents.json` });
  } catch (err) {
    console.error('[/api/stores POST]', err.message);
    res.status(500).json({ error: err.message });
  }
});

// ─── Health ───────────────────────────────────────────────────────────────────
app.get('/health', (req, res) => res.json({ status: 'ok', stores: Object.keys(loadStores()).length }));

app.listen(PORT, '0.0.0.0', () => {
  console.log(`AgentBridge Shopify Proxy running at http://62.171.140.140:${PORT}`);
  console.log(`Dashboard: http://62.171.140.140:${PORT}/dashboard`);
});
