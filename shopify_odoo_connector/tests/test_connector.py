from unittest.mock import MagicMock

from src.connector.connector import OdooShopifyConnector


def test_sync_products_odoo_to_shopify():
    mock_shopify = MagicMock()
    mock_odoo = MagicMock()
    
    mock_odoo.get_products.return_value = [
        {'name': 'Test1', 'default_code': 'SKU1', 'list_price': 10.0, 'type': 'product'},
        {'name': 'Test2', 'default_code': '', 'list_price': 20.0, 'type': 'product'},  # Missing code
        {'name': 'Test3', 'default_code': 'SKU3', 'list_price': 15.0, 'type': 'consu'},
    ]
    
    connector = OdooShopifyConnector(shopify_client=mock_shopify, odoo_client=mock_odoo)
    
    synced = connector.sync_products_odoo_to_shopify(limit=10)
    
    assert synced == 2
    assert mock_shopify.create_product.call_count == 2
    
    # Check calls
    calls = mock_shopify.create_product.call_args_list
    assert calls[0].kwargs['title'] == 'Test1'
    assert calls[0].kwargs['price'] == '10.0'
    assert calls[1].kwargs['title'] == 'Test3'

def test_sync_orders_shopify_to_odoo():
    mock_shopify = MagicMock()
    mock_odoo = MagicMock()
    
    # Mock Shopify order with lines
    mock_order = MagicMock()
    mock_order.name = "#1001"
    
    mock_line1 = MagicMock()
    mock_line1.sku = 'SKU1'
    mock_line1.quantity = 2
    mock_line1.price = '10.00'
    
    mock_line2 = MagicMock()
    mock_line2.sku = 'SKU2'
    mock_line2.quantity = 1
    mock_line2.price = '20.00'
    
    mock_order.line_items = [mock_line1, mock_line2]
    mock_shopify.get_orders.return_value = [mock_order]
    
    # Mock Odoo product lookup
    def mock_get_product(sku):
        if sku == 'SKU1':
            return {'id': 1}
        return None  # SKU2 not found
        
    mock_odoo.get_product_by_ref.side_effect = mock_get_product
    
    connector = OdooShopifyConnector(shopify_client=mock_shopify, odoo_client=mock_odoo)
    
    synced = connector.sync_orders_shopify_to_odoo(partner_id=5, limit=10)
    
    assert synced == 1
    mock_odoo.create_sale_order.assert_called_once_with(
        partner_id=5, 
        order_lines=[{'product_id': 1, 'quantity': 2.0, 'price': 10.0}]
    )
