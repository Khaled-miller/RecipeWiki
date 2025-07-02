### first backend tests file ###
from flask import Flask, Response, jsonify
import requests
import pytest
from context import app
from typing import Dict, Union
from context import app
from unittest.mock import patch, MagicMock

@pytest.fixture
def client():
    """
    setup a test client for the Flaskapp
    """
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client



def test_filter_allergies(client):

    """
    Test that recipes with allergens are not selected to be shown
    """
    first_test_allergen = "Egg"
    first_test_data = [{
        "recipe_id": "111",
        "title": "Vegan Chili",
        "instructions": "1. Chop vegetables. 2. Cook in a large pot. 3. Simmer for 1 hour.",
        "ingredients": "Beans, Tomatoes, Onions, Spices",
        "image": "http://example.com/vegan-chili.jpg"
    },
    {
        "recipe_id" : "222",
        "title" : "Gluten-Free Pancakes",
        "instructions" : "1. Mix dry ingredients. 2. Whisk in wet ingredients. 3. Cook on a hot griddle until golden brown.",
        "ingredients" : "Gluten-Free Flour, Eggs, Milk, Baking Powder, Maple Syrup, Salt, Sugar",
        "image" : "http://example.com/gluten-free-pancakes.jpg"
    }]
    output_recipes = []
    for data in first_test_data:
        if first_test_allergen not in data["ingredients"]:
            output_recipes.append(data)
    assert first_test_allergen not in output_recipes[0]["ingredients"], f"{first_test_allergen} in recipe" # asserts that egg is not in the first recipe selected


    """
    checks and presents all allergens in the chosen recipe
    """
    second_test_allergen = ["Egg", "Milk", "Peanuts"]

    second_test_recipe_data = {
    "recipe_id": "444",
    "title": "Quinoa Salad",
    "instructions": "1. Cook quinoa. 2. Mix with chopped veggies and dressing. 3. Chill before serving.",
    "ingredients": "Quinoa, Cucumber, Cherry Tomatoes, Peanuts, Milk, Lemon Juice, Salt",
    "image": "http://example.com/quinoa-salad.jpg"
}
    found_allergens = []
    for allergens in second_test_allergen:
        if allergens in second_test_recipe_data["ingredients"]:
            found_allergens.append(allergens)
    assert found_allergens != [], f"{found_allergens} in recipe" # asserts that the allergenic ingredients are in the recipe selected

#test_filter_allergies(client=client())

def test_get_cook_time(client):
    first_test_data = {
        "id": 715538,
        "image": "https://img.spoonacular.com/recipes/715538-556x370.jpg",
        "imageType": "jpg",
        "title": "What to make for dinner tonight?? Bruschetta Style Pork & Pasta",
        "readyInMinutes": 35,
        "preparationMinutes": 5,
        "cookingMinutes": 30,
    }

    cook_time = first_test_data['readyInMinutes']
    assert cook_time > 0, "Incorrect/Unavailable cook time"
    
    """
    Checks that when a user selects a range (0-15 or 15-45) of time they want their overall time to be 
    Recipes above that time are filtered out
    """
    second_test_data = [{
        "id": 550505,
        "image": "https://img.spoonacular.com/recipes/550505-556x370.jpg",
        "imageType": "jpg",
        "title": "Grilled Salmon with Lemon-Dill Sauce",
        "readyInMinutes": 35,
        "preparationMinutes": 10,
        "cookingMinutes": 25},  
    {
        "id": 920202,
        "image": "https://img.spoonacular.com/recipes/920202-556x370.jpg",
        "imageType": "jpg",
        "title": "Creamy Garlic Mushroom Chicken",
        "readyInMinutes": 10,
        "preparationMinutes": 5,
        "cookingMinutes": 5},
    {
        "id": 820101,
        "image": "https://img.spoonacular.com/recipes/820101-556x370.jpg",
        "imageType": "jpg",
        "title": "Spicy Chickpea & Spinach Stew",
        "readyInMinutes": 40,
        "preparationMinutes": 10,
        "cookingMinutes": 30},
    {
        "id": 640404,
        "image": "https://img.spoonacular.com/recipes/640404-556x370.jpg",
        "imageType": "jpg",
        "title": "Thai Peanut Chicken Wraps",
        "readyInMinutes": 15,
        "preparationMinutes": 5,
        "cookingMinutes": 10}]
    
    user_defined_time = 15
    chosen_recipes = []
    for recipe in second_test_data:
        if recipe["readyInMinutes"] <= user_defined_time:
            chosen_recipes.append(recipe)

    assert len(chosen_recipes) > 0, "No recipe's found" # asserts that there is at least one recipe less than/equal to 15 minutes


