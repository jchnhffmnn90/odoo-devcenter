import os
from typing import Any

import odoorpc


class OdooClient:
    def __init__(self, host: str, port: int, db: str, user: str, password: str, protocol: str = 'jsonrpc'):
        """Initialize Odoo RPC connection."""
        self.odoo = odoorpc.ODOO(host, port=port, protocol=protocol)
        self.odoo.login(db, user, password)

    @classmethod
    def from_env(cls) -> 'OdooClient':
        """Create a client from environment variables."""
        return cls(
            host=os.environ.get("ODOO_HOST", "localhost"),
            port=int(os.environ.get("ODOO_PORT", "8069")),
            db=os.environ.get("ODOO_DB", "odoo"),
            user=os.environ.get("ODOO_USER", "admin"),
            password=os.environ.get("ODOO_PASSWORD", "admin")
        )

    def get_products(self, limit: int = 50) -> list[dict[str, Any]]:
        """Fetch products from Odoo."""
        Product = self.odoo.env['product.template']
        product_ids = Product.search([], limit=limit)
        return Product.read(product_ids, ['name', 'list_price', 'default_code', 'type'])

    def get_product_by_ref(self, default_code: str) -> dict[str, Any] | None:
        """Fetch a single product by its internal reference."""
        Product = self.odoo.env['product.template']
        product_ids = Product.search([('default_code', '=', default_code)])
        if product_ids:
            return Product.read(product_ids[0], ['name', 'list_price', 'default_code', 'type'])[0]
        return None

    def create_product(self, name: str, list_price: float, default_code: str, type: str = 'consu') -> int:
        """Create a product in Odoo."""
        Product = self.odoo.env['product.template']
        product_id = Product.create({
            'name': name,
            'list_price': list_price,
            'default_code': default_code,
            'type': type
        })
        return product_id

    def create_sale_order(self, partner_id: int, order_lines: list[dict[str, Any]]) -> int:
        """Create a sale order in Odoo."""
        SaleOrder = self.odoo.env['sale.order']
        
        lines = []
        for line in order_lines:
            lines.append((0, 0, {
                'product_id': line['product_id'],
                'product_uom_qty': line['quantity'],
                'price_unit': line['price']
            }))
            
        order_id = SaleOrder.create({
            'partner_id': partner_id,
            'order_line': lines
        })
        return order_id
