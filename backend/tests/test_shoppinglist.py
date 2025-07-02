import pytest
from context import app
from flask import json
from unittest.mock import patch


@pytest.fixture()
def client():
    """
    setup a test client for the Flaskapp
    """
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@patch("app.requests.get")
def test_extra_ingredients(mock_get, client):
    """
    Test if the recipe JSON response contains the suggested extra ingredients.
    This simulates adding ingredients and checks if those ingredients are included in the final dictionary.
    """
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "title": "Banana Pancakes",
        "extendedIngredients": [
            {"name": "banana"},
            {"name": "eggs"},
            {"name": "milk"}  # extra ingredient
        ]
    }

    # example ingredients the client enters
    payload = {
        "recipe_id": 157514,
        "ingredients": ["banana", "eggs"]
    }
    response = client.post("/recipewiki/shopping-list", json=payload)

    assert response.status_code == 200 # successful request
    data = response.get_json()

    # example extra ingredient for the recipe
    expected_extra_ingredient = "milk"

    # assert it contains extra ingredients not in the client's request
    assert any("ingredient" in item for item in data["shopping_list"])
    assert any(item.get("ingredient") == expected_extra_ingredient for item in data["shopping_list"])


def test_local_prices_shoppinglist(client):
    """
    Test if the prices of the ingredients in the shopping list are valid and have a currency.
    """
    # example recipe ingredients
    payload = {
        "recipe_id": 157514,
        "ingredients": ["banana", "eggs", "milk"]
    }

    response = client.post("/recipewiki/shopping-list", json=payload)
    assert response.status_code == 200 # successful request
    data = response.get_json()

    # assert the ingredient has a valid price
    assert "shopping_list" in data
    for item in data["shopping_list"]:
        assert "price" in item
        assert isinstance(item["price"], str)
        # assert the data has a currency
        assert data["currency"] in ["EUR", "USD", "GBP", "CAD", "AUD"]
    

def test_sharing_shoppinglist(client):
    """
    Test if a URL is created to share the shopping list.
    """
    # example ingredients in the shopping list
    payload = {
        "recipe_id": 157514,
        "ingredients": ["banana", "eggs", "milk"]
    }
    response = client.post("/recipewiki/shopping-list", json=payload)

    assert response.status_code == 200 # successful request
    data = response.get_json()

    # assert a sharable URL is generated
    assert "shareable_url" in data
    assert data["shareable_url"].startswith("http")


def test_nearby_local_market(client):
    """
    Test if a list of nearby local markets is generated that sell the missing ingredients. 
    """
    # example ingredients and location of the client
    payload = {
        "ingredients": ["banana", "eggs"],
        "location": "Netherlands"
    }
    response = client.post('recipewiki/shopping-list/markets', json=payload)

    assert response.status_code == 200 # successful request
    data = response.get_json()

    # assert a list of markets is returned
    assert "markets" in data
    assert isinstance(data["markets"], list)
    
    # assert each market has a name and address
    for market in data["markets"]:
        assert "address" in market
        assert "Netherlands" in market["address"] # check that the market is really nearby

