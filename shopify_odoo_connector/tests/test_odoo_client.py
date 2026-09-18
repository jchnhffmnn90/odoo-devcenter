from unittest.mock import MagicMock, patch

import pytest

from src.connector.odoo_client import OdooClient


@pytest.fixture
def mock_odoorpc():
    with patch("odoorpc.ODOO") as mock_odoo_class:
        mock_instance = MagicMock()
        mock_odoo_class.return_value = mock_instance
        yield mock_odoo_class, mock_instance


def test_odoo_client_init(mock_odoorpc):
    mock_class, mock_instance = mock_odoorpc

    OdooClient("localhost", 8069, "test_db", "admin", "pass")

    mock_class.assert_called_once_with("localhost", port=8069, protocol="jsonrpc")
    mock_instance.login.assert_called_once_with("test_db", "admin", "pass")


def test_get_products(mock_odoorpc):
    _, mock_instance = mock_odoorpc

    mock_env = MagicMock()
    mock_instance.env = {"product.template": mock_env}
    mock_env.search.return_value = [1, 2]
    mock_env.read.return_value = [{"name": "Product 1"}, {"name": "Product 2"}]

    client = OdooClient("localhost", 8069, "test_db", "admin", "pass")
    products = client.get_products(limit=10)

    assert len(products) == 2
    mock_env.search.assert_called_once_with([], limit=10)
    mock_env.read.assert_called_once_with(
        [1, 2], ["name", "list_price", "default_code", "type"]
    )


def test_create_sale_order(mock_odoorpc):
    _, mock_instance = mock_odoorpc

    mock_env = MagicMock()
    mock_instance.env = {"sale.order": mock_env}
    mock_env.create.return_value = 100

    client = OdooClient("localhost", 8069, "test_db", "admin", "pass")

    order_id = client.create_sale_order(
        partner_id=5, order_lines=[{"product_id": 10, "quantity": 2, "price": 15.0}]
    )

    assert order_id == 100
    mock_env.create.assert_called_once_with(
        {
            "partner_id": 5,
            "order_line": [
                (0, 0, {"product_id": 10, "product_uom_qty": 2, "price_unit": 15.0})
            ],
        }
    )
