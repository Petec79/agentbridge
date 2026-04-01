"""
AgentBridge FastAPI Server
Implements the agents.json Open Standard for Agentic Commerce
Version: 1.0.0
"""

import uuid
import hashlib
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, Header, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI(
    title="AgentBridge Server",
    description="Implementation of agents.json Open Standard for Agentic Commerce",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# IN-MEMORY DATA STORE
# =============================================================================

class DataStore:
    def __init__(self):
        # Sample categories
        self.categories = [
            {"category_id": "cat_001", "name": "Electronics", "slug": "electronics", "parent_id": None},
            {"category_id": "cat_002", "name": "Clothing", "slug": "clothing", "parent_id": None},
            {"category_id": "cat_003", "name": "Home & Garden", "slug": "home-garden", "parent_id": None},
            {"category_id": "cat_004", "name": "Accessories", "slug": "accessories", "parent_id": "cat_002"},
        ]
        
        # Sample products
        self.products = [
            {
                "product_id": "prod_001",
                "name": "Wireless Noise-Canceling Headphones",
                "description": "Premium over-ear headphones with 30-hour battery life and adaptive noise cancellation.",
                "sku": "WH-1000XM5",
                "category_id": "cat_001",
                "price": 299.99,
                "currency": "USD",
                "availability": "in_stock",
                "inventory_quantity": 45,
                "images": [
                    {"url": "https://example.com/headphones.jpg", "alt": "Headphones front view"}
                ],
                "variants": [
                    {"variant_id": "var_001a", "name": "Black", "sku": "WH-1000XM5-BLK", "price": 299.99, "inventory_quantity": 15},
                    {"variant_id": "var_001b", "name": "Silver", "sku": "WH-1000XM5-SLV", "price": 299.99, "inventory_quantity": 20},
                    {"variant_id": "var_001c", "name": "Midnight Blue", "sku": "WH-1000XM5-BLU", "price": 319.99, "inventory_quantity": 10},
                ],
                "specifications": {
                    "battery_life": "30 hours",
                    "connectivity": "Bluetooth 5.2",
                    "weight": "250g",
                    "drivers": "40mm"
                },
                "created_at": "2024-01-15T10:00:00Z"
            },
            {
                "product_id": "prod_002",
                "name": "Smart Fitness Watch",
                "description": "Advanced fitness tracker with GPS, heart rate monitoring, and 7-day battery.",
                "sku": "FIT-PRO-2024",
                "category_id": "cat_001",
                "price": 199.99,
                "currency": "USD",
                "availability": "in_stock",
                "inventory_quantity": 120,
                "images": [
                    {"url": "https://example.com/watch.jpg", "alt": "Fitness watch"}
                ],
                "variants": [
                    {"variant_id": "var_002a", "name": "Black / 42mm", "sku": "FIT-PRO-BLK-42", "price": 199.99, "inventory_quantity": 60},
                    {"variant_id": "var_002b", "name": "Silver / 42mm", "sku": "FIT-PRO-SLV-42", "price": 199.99, "inventory_quantity": 40},
                    {"variant_id": "var_002c", "name": "Rose Gold / 38mm", "sku": "FIT-PRO-RSG-38", "price": 229.99, "inventory_quantity": 20},
                ],
                "specifications": {
                    "battery_life": "7 days",
                    "water_resistance": "5ATM",
                    "gps": "Yes",
                    "heart_rate": "Yes"
                },
                "created_at": "2024-02-20T14:30:00Z"
            },
            {
                "product_id": "prod_003",
                "name": "Ergonomic Office Chair",
                "description": "Premium mesh office chair with lumbar support, adjustable armrests, and headrest.",
                "sku": "CHR-ERG-001",
                "category_id": "cat_003",
                "price": 449.99,
                "currency": "USD",
                "availability": "in_stock",
                "inventory_quantity": 15,
                "images": [
                    {"url": "https://example.com/chair.jpg", "alt": "Office chair"}
                ],
                "variants": [
                    {"variant_id": "var_003a", "name": "Black Mesh", "sku": "CHR-ERG-BLK", "price": 449.99, "inventory_quantity": 8},
                    {"variant_id": "var_003b", "name": "Gray Mesh", "sku": "CHR-ERG-GRY", "price": 449.99, "inventory_quantity": 7},
                ],
                "specifications": {
                    "material": "Mesh",
                    "weight_capacity": "300 lbs",
                    "adjustments": "4D armrests, lumbar, tilt",
                    "warranty": "10 years"
                },
                "created_at": "2024-03-10T09:15:00Z"
            },
            {
                "product_id": "prod_004",
                "name": "Organic Coffee Beans (1kg)",
                "description": "Premium single-origin Ethiopian coffee beans, medium roast.",
                "sku": "COF-ETH-1KG",
                "category_id": "cat_003",
                "price": 24.99,
                "currency": "USD",
                "availability": "in_stock",
                "inventory_quantity": 200,
                "images": [
                    {"url": "https://example.com/coffee.jpg", "alt": "Coffee beans"}
                ],
                "variants": [
                    {"variant_id": "var_004a", "name": "Whole Bean", "sku": "COF-ETH-WB", "price": 24.99, "inventory_quantity": 100},
                    {"variant_id": "var_004b", "name": "Ground", "sku": "COF-ETH-GR", "price": 22.99, "inventory_quantity": 100},
                ],
                "specifications": {
                    "origin": "Ethiopia",
                    "roast": "Medium",
                    "weight": "1kg",
                    "organic": "Yes"
                },
                "created_at": "2024-04-05T11:00:00Z"
            },
            {
                "product_id": "prod_005",
                "name": "Mechanical Keyboard (Cherry MX)",
                "description": "TKL mechanical keyboard with Cherry MX Red switches, RGB backlight.",
                "sku": "KEY-MECH-TKL",
                "category_id": "cat_001",
                "price": 159.99,
                "currency": "USD",
                "availability": "in_stock",
                "inventory_quantity": 67,
                "images": [
                    {"url": "https://example.com/keyboard.jpg", "alt": "Mechanical keyboard"}
                ],
                "variants": [
                    {"variant_id": "var_005a", "name": "Cherry MX Red", "sku": "KEY-MECH-RED", "price": 159.99, "inventory_quantity": 25},
                    {"variant_id": "var_005b", "name": "Cherry MX Blue", "sku": "KEY-MECH-BLU", "price": 159.99, "inventory_quantity": 22},
                    {"variant_id": "var_005c", "name": "Cherry MX Brown", "sku": "KEY-MECH-BRN", "price": 159.99, "inventory_quantity": 20},
                ],
                "specifications": {
                    "switches": "Cherry MX Red",
                    "layout": "TKL",
                    "backlight": "RGB",
                    "frame": "Aluminum"
                },
                "created_at": "2024-05-12T16:45:00Z"
            },
        ]
        
        # Cart storage
        self.carts: Dict[str, Dict] = {}
        
        # Orders storage
        self.orders: Dict[str, Dict] = {}
        
        # Agent tokens
        self.agent_tokens: Dict[str, Dict] = {}
        
        # Sessions
        self.sessions: Dict[str, Dict] = {}

db = DataStore()

# =============================================================================
# MODELS
# =============================================================================

class AddToCartRequest(BaseModel):
    product_id: str
    variant_id: Optional[str] = None
    quantity: int = 1

class UpdateCartItemRequest(BaseModel):
    quantity: int

class CustomerInfo(BaseModel):
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None

class ShippingAddress(BaseModel):
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    postal_code: str
    country: str

class PaymentMethod(BaseModel):
    type: str
    token: Optional[str] = None

class CheckoutRequest(BaseModel):
    cart_id: str
    session_id: str
    customer: Optional[CustomerInfo] = None
    shipping_address: Optional[ShippingAddress] = None
    payment_method: Optional[PaymentMethod] = None
    shipping_method: Optional[str] = None
    coupon_code: Optional[str] = None

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def detect_agent(request: Request) -> Optional[Dict]:
    """Detect AI agents from request headers."""
    user_agent = request.headers.get("user-agent", "")
    
    agents = {
        "Claude": {"name": "Anthropic Claude", "capabilities": ["web_search", "code_execution", "vision"]},
        "ChatGPT": {"name": "OpenAI GPT", "capabilities": ["web_search", "code_execution", "vision"]},
        "Gemini": {"name": "Google Gemini", "capabilities": ["web_search", "vision", "deep_research"]},
        "Grok": {"name": "xAI Grok", "capabilities": ["web_search", "vision"]},
    }
    
    for pattern, info in agents.items():
        if pattern.lower() in user_agent.lower():
            return {"detected": True, "agent": pattern, **info}
    
    return None

def calculate_cart_totals(cart: Dict) -> Dict:
    """Calculate cart subtotal, tax, shipping, and total."""
    subtotal = sum(item["subtotal"] for item in cart["items"])
    tax = round(subtotal * 0.08, 2)  # 8% tax
    shipping = 5.99 if subtotal < 50 and len(cart["items"]) > 0 else 0
    total = subtotal + tax + shipping
    
    return {
        "subtotal": round(subtotal, 2),
        "tax": tax,
        "shipping": shipping,
        "total": round(total, 2)
    }

# =============================================================================
# AGENTS.JSON DISCOVERY ENDPOINTS
# =============================================================================

@app.get("/.well-known/agents.json")
@app.get("/agents.json")
async def get_agents_json(request: Request):
    """Return the agents.json discovery document."""
    base_url = str(request.base_url).rstrip("/")
    
    return {
        "version": "1.0.0",
        "store_id": "store_001",
        "name": "AgentBridge Demo Store",
        "domain": base_url.replace("http://", "https://"),
        "description": "Demo store implementing the agents.json standard",
        "currency": "USD",
        "weight_unit": "KG",
        "dimension_unit": "CM",
        "contact_email": "support@agentbridge-demo.com",
        "terms_url": f"{base_url}/policies/terms",
        "privacy_url": f"{base_url}/policies/privacy",
        "supported_locales": ["en"],
        "created_at": "2024-01-01T00:00:00Z",
        "endpoints": {
            "store_info": f"{base_url}/store",
            "catalog": f"{base_url}/catalog",
            "product": f"{base_url}/products/{{product_id}}",
            "search": f"{base_url}/search",
            "cart": f"{base_url}/cart",
            "checkout": f"{base_url}/checkout",
            "orders": f"{base_url}/orders",
            "auth": {
                "login": f"{base_url}/auth/login",
                "logout": f"{base_url}/auth/logout",
                "register": f"{base_url}/auth/register",
                "agent_token": f"{base_url}/auth/agent/token"
            },
            "policies": {
                "returns": f"{base_url}/policies/returns",
                "shipping": f"{base_url}/policies/shipping",
                "privacy": f"{base_url}/policies/privacy",
                "terms": f"{base_url}/policies/terms",
                "payments": f"{base_url}/policies/payments"
            }
        },
        "rate_limits": {
            "requests_per_minute": 60,
            "burst": 10
        },
        "cache_max_age": 300,
        "user_agent_required": True
    }

# =============================================================================
# STORE INFO
# =============================================================================

@app.get("/store")
async def get_store_info(request: Request):
    """Return store information and branding."""
    base_url = str(request.base_url).rstrip("/")
    
    return {
        "store_id": "store_001",
        "name": "AgentBridge Demo Store",
        "domain": base_url.replace("http://", "https://"),
        "logo_url": f"{base_url}/images/logo.png",
        "description": "Demo store for the agents.json standard",
        "currency": "USD",
        "weight_unit": "KG",
        "dimension_unit": "CM",
        "contact_email": "support@agentbridge-demo.com",
        "terms_url": f"{base_url}/policies/terms",
        "privacy_url": f"{base_url}/policies/privacy",
        "supported_locales": ["en"],
        "created_at": "2024-01-01T00:00:00Z"
    }

# =============================================================================
# CATALOG & PRODUCTS
# =============================================================================

@app.get("/catalog")
async def get_catalog(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=250),
    category_id: Optional[str] = None,
    sort: Optional[str] = None,
    availability: str = Query("in_stock", regex="^(in_stock|out_of_stock|all)$")
):
    """Return paginated product catalog."""
    products = db.products.copy()
    
    # Filter by category
    if category_id:
        products = [p for p in products if p["category_id"] == category_id]
    
    # Filter by availability
    if availability != "all":
        products = [p for p in products if p["availability"] == availability]
    
    # Sort
    if sort == "price_asc":
        products.sort(key=lambda x: x["price"])
    elif sort == "price_desc":
        products.sort(key=lambda x: x["price"], reverse=True)
    elif sort == "name_asc":
        products.sort(key=lambda x: x["name"])
    elif sort == "newest":
        products.sort(key=lambda x: x["created_at"], reverse=True)
    
    # Pagination
    total_items = len(products)
    total_pages = (total_items + per_page - 1) // per_page
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    return {
        "products": products[start_idx:end_idx],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "total_items": total_items,
            "has_next": page < total_pages,
            "has_prev": page > 1
        },
        "categories": db.categories
    }

@app.get("/products/{product_id}")
async def get_product(product_id: str):
    """Return full product details."""
    for product in db.products:
        if product["product_id"] == product_id:
            return product
    
    raise HTTPException(status_code=404, detail="Product not found")

# =============================================================================
# SEARCH
# =============================================================================

@app.get("/search")
async def search_products(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=250),
    category_id: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    availability: str = Query("in_stock", regex="^(in_stock|out_of_stock|all)$"),
    sort: Optional[str] = None
):
    """Full-text search across product catalog."""
    query_lower = q.lower()
    results = []
    
    for product in db.products:
        # Score by relevance
        score = 0
        if query_lower in product["name"].lower():
            score += 10
        if query_lower in product["description"].lower():
            score += 5
        if query_lower in product["sku"].lower():
            score += 3
        
        if score > 0:
            results.append({**product, "relevance_score": score})
    
    # Filter by category
    if category_id:
        results = [p for p in results if p["category_id"] == category_id]
    
    # Filter by price
    if min_price is not None:
        results = [p for p in results if p["price"] >= min_price]
    if max_price is not None:
        results = [p for p in results if p["price"] <= max_price]
    
    # Filter by availability
    if availability != "all":
        results = [p for p in results if p["availability"] == availability]
    
    # Sort
    if sort == "price_asc":
        results.sort(key=lambda x: x["price"])
    elif sort == "price_desc":
        results.sort(key=lambda x: x["price"], reverse=True)
    elif sort == "name_asc":
        results.sort(key=lambda x: x["name"])
    elif sort == "relevance" or sort is None:
        results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
    
    # Pagination
    total_items = len(results)
    total_pages = (total_items + per_page - 1) // per_page
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    return {
        "products": results[start_idx:end_idx],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "total_items": total_items,
            "has_next": page < total_pages,
            "has_prev": page > 1
        },
        "categories": db.categories
    }

# =============================================================================
# CART
# =============================================================================

def get_session_id(authorization: Optional[str] = Header(None), x_session_id: Optional[str] = Header(None)) -> str:
    """Get or create session ID."""
    if x_session_id:
        return x_session_id
    if authorization:
        # Use token hash as session ID for authenticated requests
        return hashlib.sha256(authorization.encode()).hexdigest()[:16]
    return str(uuid.uuid4())

@app.get("/cart")
async def get_cart(
    authorization: Optional[str] = Header(None),
    x_session_id: Optional[str] = Header(None)
):
    """Get current cart."""
    session_id = get_session_id(authorization, x_session_id)
    
    if session_id not in db.carts:
        return {
            "cart_id": f"cart_{session_id[:8]}",
            "session_id": session_id,
            "items": [],
            "subtotal": 0,
            "tax": 0,
            "shipping": 0,
            "total": 0,
            "currency": "USD",
            "item_count": 0,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.utcnow().isoformat() + "Z"
        }
    
    cart = db.carts[session_id]
    totals = calculate_cart_totals(cart)
    
    return {
        **cart,
        **totals
    }

@app.post("/cart/items")
async def add_to_cart(
    item: AddToCartRequest,
    authorization: Optional[str] = Header(None),
    x_session_id: Optional[str] = Header(None)
):
    """Add item to cart."""
    session_id = get_session_id(authorization, x_session_id)
    
    # Find product
    product = None
    for p in db.products:
        if p["product_id"] == item.product_id:
            product = p
            break
    
    if not product:
        raise HTTPException(status_code=400, detail="Invalid product ID")
    
    # Find variant
    variant = None
    if item.variant_id:
        for v in product.get("variants", []):
            if v["variant_id"] == item.variant_id:
                variant = v
                break
    
    # Check inventory
    available_qty = variant["inventory_quantity"] if variant else product["inventory_quantity"]
    if available_qty < item.quantity:
        raise HTTPException(status_code=422, detail="Insufficient inventory")
    
    # Create or update cart
    if session_id not in db.carts:
        db.carts[session_id] = {
            "cart_id": f"cart_{session_id[:8]}",
            "session_id": session_id,
            "items": [],
            "currency": "USD",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.utcnow().isoformat() + "Z"
        }
    
    cart = db.carts[session_id]
    
    # Check if item already in cart
    item_id = f"{item.product_id}_{item.variant_id}" if item.variant_id else item.product_id
    for existing_item in cart["items"]:
        if existing_item["item_id"] == item_id:
            existing_item["quantity"] += item.quantity
            existing_item["subtotal"] = existing_item["quantity"] * (variant["price"] if variant else product["price"])
            cart["updated_at"] = datetime.utcnow().isoformat() + "Z"
            totals = calculate_cart_totals(cart)
            return {**cart, **totals}
    
    # Add new item
    price = variant["price"] if variant else product["price"]
    cart["items"].append({
        "item_id": item_id,
        "product_id": item.product_id,
        "variant_id": item.variant_id,
        "quantity": item.quantity,
        "unit_price": price,
        "currency": product["currency"],
        "subtotal": price * item.quantity,
        "product_name": product["name"],
        "variant_name": variant["name"] if variant else None,
        "image_url": product["images"][0]["url"] if product["images"] else None
    })
    
    cart["updated_at"] = datetime.utcnow().isoformat() + "Z"
    totals = calculate_cart_totals(cart)
    
    return {**cart, **totals}

@app.patch("/cart/items/{item_id}")
async def update_cart_item(
    item_id: str,
    item: UpdateCartItemRequest,
    authorization: Optional[str] = Header(None),
    x_session_id: Optional[str] = Header(None)
):
    """Update cart item quantity."""
    session_id = get_session_id(authorization, x_session_id)
    
    if session_id not in db.carts:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    cart = db.carts[session_id]
    
    for cart_item in cart["items"]:
        if cart_item["item_id"] == item_id:
            if item.quantity == 0:
                cart["items"].remove(cart_item)
            else:
                cart_item["quantity"] = item.quantity
                cart_item["subtotal"] = cart_item["quantity"] * cart_item["unit_price"]
            cart["updated_at"] = datetime.utcnow().isoformat() + "Z"
            totals = calculate_cart_totals(cart)
            return {**cart, **totals}
    
    raise HTTPException(status_code=404, detail="Item not found in cart")

@app.delete("/cart/items/{item_id}")
async def remove_cart_item(
    item_id: str,
    authorization: Optional[str] = Header(None),
    x_session_id: Optional[str] = Header(None)
):
    """Remove item from cart."""
    session_id = get_session_id(authorization, x_session_id)
    
    if session_id not in db.carts:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    cart = db.carts[session_id]
    
    for i, cart_item in enumerate(cart["items"]):
        if cart_item["item_id"] == item_id:
            cart["items"].pop(i)
            cart["updated_at"] = datetime.utcnow().isoformat() + "Z"
            totals = calculate_cart_totals(cart)
            return {**cart, **totals}
    
    raise HTTPException(status_code=404, detail="Item not found in cart")

@app.delete("/cart")
async def clear_cart(
    authorization: Optional[str] = Header(None),
    x_session_id: Optional[str] = Header(None)
):
    """Clear all items from cart."""
    session_id = get_session_id(authorization, x_session_id)
    
    if session_id in db.carts:
        db.carts[session_id]["items"] = []
        db.carts[session_id]["updated_at"] = datetime.utcnow().isoformat() + "Z"
    
    return {
        "cart_id": f"cart_{session_id[:8]}",
        "session_id": session_id,
        "items": [],
        "subtotal": 0,
        "tax": 0,
        "shipping": 0,
        "total": 0,
        "currency": "USD",
        "item_count": 0,
        "message": "Cart cleared"
    }

# =============================================================================
# CHECKOUT
# =============================================================================

@app.post("/checkout/initiate")
async def initiate_checkout(
    checkout: CheckoutRequest,
    authorization: Optional[str] = Header(None),
    x_session_id: Optional[str] = Header(None)
):
    """Initiate checkout process."""
    session_id = get_session_id(authorization, x_session_id)
    
    # Validate cart - use session_id to find cart
    if session_id not in db.carts or not db.carts[session_id].get("items"):
        raise HTTPException(status_code=400, detail="Cart is empty")
    cart = db.carts[session_id]
    
    # Calculate totals
    totals = calculate_cart_totals(cart)
    
    # Create order
    order_id = f"ord_{uuid.uuid4().hex[:12]}"
    checkout_id = f"chk_{uuid.uuid4().hex[:12]}"
    
    order = {
        "order_id": order_id,
        "checkout_id": checkout_id,
        "cart_id": cart["cart_id"],
        "session_id": session_id,
        "customer": checkout.customer.dict() if checkout.customer else None,
        "shipping_address": checkout.shipping_address.dict() if checkout.shipping_address else None,
        "items": cart["items"],
        "subtotal": totals["subtotal"],
        "tax": totals["tax"],
        "shipping": totals["shipping"],
        "total": totals["total"],
        "currency": cart["currency"],
        "status": "pending_payment",
        "created_at": datetime.utcnow().isoformat() + "Z"
    }
    
    db.orders[order_id] = order
    
    # Return checkout response
    return {
        "checkout_id": checkout_id,
        "status": "pending_payment",
        "order_id": order_id,
        "payment_instructions": {
            "type": "card",
            "amount": totals["total"],
            "currency": cart["currency"],
            "provider": "stripe",
            "hosted_page_url": f"https://checkout.agentbridge-demo.com/{checkout_id}"
        },
        "order_summary": {
            "subtotal": totals["subtotal"],
            "tax": totals["tax"],
            "shipping": totals["shipping"],
            "total": totals["total"],
            "currency": cart["currency"],
            "item_count": len(cart["items"])
        }
    }

# =============================================================================
# ORDERS
# =============================================================================

@app.get("/orders")
async def list_orders(
    authorization: Optional[str] = Header(None),
    x_session_id: Optional[str] = Header(None)
):
    """List orders for session."""
    session_id = get_session_id(authorization, x_session_id)
    
    user_orders = [o for o in db.orders.values() if o["session_id"] == session_id]
    
    return {
        "orders": user_orders,
        "count": len(user_orders)
    }

# =============================================================================
# AUTH
# =============================================================================

@app.post("/auth/agent/token")
async def create_agent_token(
    request: Request,
    agent_name: str = Query(...),
    agent_version: str = Query("1.0"),
    capabilities: str = Query("")
):
    """Create agent token for authentication."""
    agent_info = detect_agent(request)
    
    token = f"agt_{uuid.uuid4().hex}"
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    
    db.agent_tokens[token_hash] = {
        "agent_name": agent_name,
        "agent_version": agent_version,
        "capabilities": capabilities.split(",") if capabilities else [],
        "created_at": datetime.utcnow().isoformat() + "Z",
        "expires_at": (datetime.utcnow() + timedelta(days=30)).isoformat() + "Z"
    }
    
    return {
        "token": token,
        "token_type": "Bearer",
        "expires_in": 2592000,
        "scope": "read_products write_cart checkout"
    }

@app.post("/auth/login")
async def login(username: str = Query(...), password: str = Query(...)):
    """Login endpoint."""
    # Demo - always succeed
    session_id = str(uuid.uuid4())
    db.sessions[session_id] = {
        "username": username,
        "created_at": datetime.utcnow().isoformat() + "Z"
    }
    
    return {
        "session_id": session_id,
        "token": f"sess_{session_id}",
        "expires_in": 86400
    }

@app.post("/auth/logout")
async def logout(
    authorization: Optional[str] = Header(None),
    x_session_id: Optional[str] = Header(None)
):
    """Logout endpoint."""
    session_id = get_session_id(authorization, x_session_id)
    
    if session_id in db.sessions:
        del db.sessions[session_id]
    
    return {"message": "Logged out successfully"}

@app.post("/auth/register")
async def register(
    email: str = Query(...),
    password: str = Query(...),
    first_name: Optional[str] = Query(None),
    last_name: Optional[str] = Query(None)
):
    """Register new user."""
    # Demo - always succeed
    return {
        "user_id": f"user_{uuid.uuid4().hex[:8]}",
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "message": "Registration successful"
    }

# =============================================================================
# POLICIES
# =============================================================================

@app.get("/policies/returns")
async def get_returns_policy():
    """Return returns policy."""
    return {
        "policy_id": "returns_001",
        "return_window_days": 30,
        "conditions": [
            "Items must be unused and in original packaging",
            "Original receipt or proof of purchase required",
            "Customer pays for return shipping unless item is defective"
        ],
        "refund_methods": ["original_payment", "store_credit"],
        "exchange_options": ["same_product", "different_size", "different_color"],
        "restocking_fee": 0,
        "special_items": {
            "electronics": {"return_window_days": 14, "opened": False},
            " intimates": {"return_window_days": 0, "note": "Not returnable for hygiene reasons"}
        }
    }

@app.get("/policies/shipping")
async def get_shipping_policy():
    """Return shipping policy."""
    return {
        "policy_id": "shipping_001",
        "free_shipping_threshold": 50,
        "methods": [
            {"id": "standard", "name": "Standard Shipping", "price": 5.99, "estimated_days": "5-7"},
            {"id": "express", "name": "Express Shipping", "price": 12.99, "estimated_days": "2-3"},
            {"id": "overnight", "name": "Overnight Shipping", "price": 24.99, "estimated_days": "1"}
        ],
        "international": {
            "available": True,
            "methods": [
                {"id": "international_standard", "name": "International Standard", "price": 19.99, "estimated_days": "10-14"}
            ],
            "restrictions": ["Some items may not be available for international shipping"]
        },
        "free_shipping_message": "Free shipping on orders over $50"
    }

@app.get("/policies/privacy")
async def get_privacy_policy():
    """Return privacy policy."""
    return {
        "policy_id": "privacy_001",
        "data_collected": [
            "Email and shipping address for order fulfillment",
            "Payment information (processed by payment provider)",
            "Browsing behavior for analytics"
        ],
        "data_usage": [
            "Process and fulfill orders",
            "Communicate about orders",
            "Improve our services"
        ],
        "data_sharing": [
            "Payment processors for transaction processing",
            "Shipping carriers for delivery"
        ],
        "user_rights": [
            "Access personal data",
            "Request deletion of personal data",
            "Opt-out of marketing communications"
        ],
        "contact_email": "privacy@agentbridge-demo.com"
    }

@app.get("/policies/terms")
async def get_terms():
    """Return terms of service."""
    return {
        "policy_id": "terms_001",
        "effective_date": "2024-01-01",
        "sections": [
            {"title": "Acceptance of Terms", "content": "By accessing and using this store, you accept and agree to be bound by the terms and provision of this agreement."},
            {"title": "Product Information", "content": "We attempt to be accurate in product descriptions. However, we do not warrant that product descriptions are accurate, complete, or error-free."},
            {"title": "Ordering", "content": "We reserve the right to refuse or cancel any order for any reason."},
            {"title": "Pricing", "content": "Prices are subject to change without notice."}
        ],
        "contact_email": "support@agentbridge-demo.com"
    }

@app.get("/policies/payments")
async def get_payments_policy():
    """Return payments policy."""
    return {
        "policy_id": "payments_001",
        "supported_methods": [
            {"type": "card", "providers": ["stripe"], "currencies": ["USD", "EUR", "GBP"]},
            {"type": "paypal", "providers": ["paypal"]},
            {"type": "bank_transfer", "note": "Processing time: 2-3 business days"}
        ],
        "currency": "USD",
        "secure_processing": "All payments processed via Stripe",
        " PCI_compliant": True
    }

# =============================================================================
# HEALTH & AGENT DETECTION
# =============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat() + "Z"}

@app.get("/v1/agent-detect")
async def detect_agent_endpoint(request: Request):
    """Detect AI agents visiting the store."""
    agent_info = detect_agent(request)
    
    if agent_info:
        return {
            "detected": True,
            "agent": agent_info,
            "message": "AI agent detected"
        }
    
    return {
        "detected": False,
        "agent": None,
        "message": "No AI agent detected"
    }

# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import sys
    port = 8080
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    
    print(f"🚀 Starting AgentBridge Server on port {port}...")
    print(f"📡 Server available at http://localhost:{port}")
    print(f"📋 agents.json at http://localhost:{port}/agents.json")
    uvicorn.run(app, host="0.0.0.0", port=port)