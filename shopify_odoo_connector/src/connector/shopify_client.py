import os

import shopify


class ShopifyClient:
    def __init__(self, shop_url: str, access_token: str, api_version: str = "2024-01"):
        """Initialize Shopify API session."""
        self.shop_url = shop_url
        self.access_token = access_token
        self.api_version = api_version
        
        session = shopify.Session(self.shop_url, self.api_version, self.access_token)
        shopify.ShopifyResource.activate_session(session)

    @classmethod
    def from_env(cls) -> 'ShopifyClient':
        """Create a client from environment variables."""
        return cls(
            shop_url=os.environ.get("SHOPIFY_SHOP_URL", ""),
            access_token=os.environ.get("SHOPIFY_ACCESS_TOKEN", ""),
            api_version=os.environ.get("SHOPIFY_API_VERSION", "2024-01")
        )

    def get_products(self, limit: int = 50) -> list[shopify.Product]:
        """Fetch products from Shopify."""
        return shopify.Product.find(limit=limit)

    def get_orders(self, status: str = "any", limit: int = 50) -> list[shopify.Order]:
        """Fetch orders from Shopify."""
        return shopify.Order.find(status=status, limit=limit)

    def create_product(self, title: str, body_html: str, vendor: str, product_type: str, price: str) -> shopify.Product:
        """Create a simple product in Shopify."""
        new_product = shopify.Product()
        new_product.title = title
        new_product.body_html = body_html
        new_product.vendor = vendor
        new_product.product_type = product_type
        
        variant = shopify.Variant()
        variant.price = price
        new_product.variants = [variant]
        
        new_product.save()
        return new_product

    def update_product_inventory(self, variant_id: int, location_id: int, available: int) -> bool:
        """Update inventory level for a specific variant at a location."""
        return shopify.InventoryLevel.set(location_id=location_id, inventory_item_id=variant_id, available=available)
