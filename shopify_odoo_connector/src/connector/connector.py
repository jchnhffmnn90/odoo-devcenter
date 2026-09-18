import logging

from src.connector.odoo_client import OdooClient
from src.connector.shopify_client import ShopifyClient

logger = logging.getLogger(__name__)


class OdooShopifyConnector:
    def __init__(self, shopify_client: ShopifyClient, odoo_client: OdooClient):
        self.shopify = shopify_client
        self.odoo = odoo_client

    def sync_products_odoo_to_shopify(self, limit: int = 50) -> int:
        """Synchronize products from Odoo to Shopify."""
        synced_count = 0
        odoo_products = self.odoo.get_products(limit=limit)

        for odoo_product in odoo_products:
            # We use default_code as a unique identifier. Skip if it doesn't have one.
            if not odoo_product.get("default_code"):
                logger.warning(
                    f"Skipping Odoo product '{odoo_product['name']}' without default_code."
                )
                continue

            # Creating a simple product in Shopify.
            # In a real scenario, you'd check if it exists first and update, or map more fields.
            try:
                self.shopify.create_product(
                    title=odoo_product["name"],
                    body_html=f"Product from Odoo. SKU: {odoo_product['default_code']}",
                    vendor="Odoo Sync",
                    product_type=odoo_product.get("type", "Unknown"),
                    price=str(odoo_product["list_price"]),
                )
                synced_count += 1
                logger.info(f"Synced product '{odoo_product['name']}' to Shopify.")
            except Exception as e:  # noqa: BLE001
                logger.error(f"Failed to sync product '{odoo_product['name']}': {e}")

        return synced_count

    def sync_orders_shopify_to_odoo(self, partner_id: int, limit: int = 50) -> int:
        """Synchronize orders from Shopify to Odoo."""
        synced_count = 0
        shopify_orders = self.shopify.get_orders(limit=limit)

        for order in shopify_orders:
            order_lines = []

            # Map Shopify line items to Odoo format
            for line_item in order.line_items:
                # Typically, you'd find the Odoo product ID by matching SKU (default_code).
                sku = getattr(line_item, "sku", None)
                if not sku:
                    logger.warning(
                        f"Shopify line item '{line_item.title}' has no SKU. Skipping."
                    )
                    continue

                odoo_product = self.odoo.get_product_by_ref(sku)
                if not odoo_product:
                    logger.warning(
                        f"No matching Odoo product found for SKU '{sku}'. Skipping."
                    )
                    continue

                # The Odoo product_id is the actual ID in product.product model,
                # but for simplicity in this example we'll assume the template ID maps directly
                # or we just use the ID we got from product.template.
                # In a real setup you'd query 'product.product' instead of 'product.template'
                # for sale order lines. Let's assume ID works for this prototype.
                product_id = odoo_product["id"]

                order_lines.append(
                    {
                        "product_id": product_id,
                        "quantity": float(line_item.quantity),
                        "price": float(line_item.price),
                    }
                )

            if order_lines:
                try:
                    self.odoo.create_sale_order(
                        partner_id=partner_id, order_lines=order_lines
                    )
                    synced_count += 1
                    logger.info(f"Synced Shopify order '{order.name}' to Odoo.")
                except Exception as e:  # noqa: BLE001
                    logger.error(f"Failed to sync order '{order.name}': {e}")
            else:
                logger.warning(f"Order '{order.name}' has no valid lines to sync.")

        return synced_count
