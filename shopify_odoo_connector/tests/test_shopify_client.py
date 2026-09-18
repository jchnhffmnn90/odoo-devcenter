from unittest.mock import MagicMock, patch

import pytest

from src.connector.shopify_client import ShopifyClient


@pytest.fixture
def mock_shopify_session():
    with patch('shopify.Session') as mock_session, \
         patch('shopify.ShopifyResource.activate_session') as mock_activate:
        yield mock_session, mock_activate

def test_shopify_client_init(mock_shopify_session):
    client = ShopifyClient('shop.myshopify.com', 'token')
    assert client.shop_url == 'shop.myshopify.com'
    assert client.access_token == 'token'
    mock_session, mock_activate = mock_shopify_session
    mock_session.assert_called_once_with('shop.myshopify.com', '2024-01', 'token')
    mock_activate.assert_called_once()

@patch('shopify.Product.find')
def test_get_products(mock_find, mock_shopify_session):
    client = ShopifyClient('shop', 'token')
    mock_find.return_value = ['product1', 'product2']
    products = client.get_products(limit=10)
    assert products == ['product1', 'product2']
    mock_find.assert_called_once_with(limit=10)

@patch('shopify.Product')
@patch('shopify.Variant')
def test_create_product(mock_variant, mock_product_class, mock_shopify_session):
    client = ShopifyClient('shop', 'token')
    
    mock_product_instance = MagicMock()
    mock_product_class.return_value = mock_product_instance
    
    mock_variant_instance = MagicMock()
    mock_variant.return_value = mock_variant_instance

    product = client.create_product('Test', 'Desc', 'Vendor', 'Type', '10.00')
    
    assert mock_product_instance.title == 'Test'
    assert mock_product_instance.body_html == 'Desc'
    assert mock_product_instance.variants == [mock_variant_instance]
    assert mock_variant_instance.price == '10.00'
    
    mock_product_instance.save.assert_called_once()
    assert product == mock_product_instance
