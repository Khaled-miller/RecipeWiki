
import pytest
from context import app, favorite_recipes_database #import the app and the database
from typing import Dict, Any
from recipe_wiki.wiki import Recipe, RecipeWiki
from unittest.mock import patch, MagicMock, mock_open #these are used to mock the api calls for the joke test
import json
from io import StringIO
from app import favorite_recipes_database


GET_SEASONAL_FOODS_ENDPOINT = "/recipewiki/suggestions/seasonal"
CREATE_ENTRY_RECIPE_ENDPOINT = "/recipewiki/favorites"
GET_FAVORITE_RECIPES_ENDPOINT= "/recipewiki/favorites"


@pytest.fixture
def client():
    """
    setup a test client for the Flaskapp
    """
    app.config['TESTING'] = True
    with app.test_client() as client:
        favorite_recipes_database.clear_favorites() #clean the db before each test
        yield client
#################################################
##               Test CREATE+JOKE             ###
#################################################


###### Test for adding a favorite recipe and returning a joke ######

@patch('app.requests.get')
def test_add_favorite_recipe_and_joke(mock_get: MagicMock, client)-> None:
    """
    Test case for successfully adding a new recipe to the favorites list.
    """
    #mocking the joke api
    
    mock_response= {"text": "Any salad can be a Caesar salad if you stab it enough."}
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_response

    # the first recipe
    first_new_recipe_data: Recipe = Recipe(
        "111",
        "Vegan Chili",
        "1. Chop vegetables. 2. Cook in a large pot. 3. Simmer for 1 hour.",
        "Beans, Tomatoes, Onions, Spices",
        "http://example.com/vegan-chili.jpg",
        30,
        200,
        ["Mexican"],
        ["Vegan"],
        True,
        True,
        True,
        {"calories": 200, "protein": 10, "carbs": 20, "fat": 10})
    

    response= client.get(GET_FAVORITE_RECIPES_ENDPOINT)
    # asserting a good respone and empty db
    assert response.status_code== 200
    # getting the number of recipes that in favorites before adding any new recipe
    recipes_before_add: Dict[str, Any] = response.get_json()
    num_recipes_before_add = len(recipes_before_add)
    # asserting the number of recipes before adding a new one
    assert num_recipes_before_add == 0
    #  create the new recipe
    response = client.post(CREATE_ENTRY_RECIPE_ENDPOINT, json=first_new_recipe_data.__dict__)

    # asserting the response is correct and the message of successful creation
    assert response.status_code == 201  # 201 Created
    response_data = response.get_json()
    
    assert "message" in response_data
    assert response_data["message"] == "Recipe added to favorites successfully."

    #assert joke after adding a recipe
    assert response.status_code == 201
    assert "joke" in response_data
    assert response_data["joke"] == f"{mock_response['text']}"

    # asserting the number of recipes has increased by 1
    response= client.get(GET_FAVORITE_RECIPES_ENDPOINT)
    response_data_after_add: Dict[str, Any] = response.get_json()
    num_recipes_after_add = len(response_data_after_add)
    assert num_recipes_after_add == num_recipes_before_add + 1

    #  Sending a GET request to verify the recipe was actually added
    assert response.status_code == 200 
    recipe= response_data_after_add["111"]
    assert recipe["title"] == "Vegan Chili"
    assert recipe["instructions"] == "1. Chop vegetables. 2. Cook in a large pot. 3. Simmer for 1 hour."
    assert recipe["ingredients"]== "Beans, Tomatoes, Onions, Spices"
    assert recipe["image"]== "http://example.com/vegan-chili.jpg"

    # Adding a recipe to a non empty favorites list
    second_new_recipe_data: Recipe = Recipe(
    "222",
    "Gluten-Free Pancakes",
    "1. Mix dry ingredients. 2. Whisk in wet ingredients. 3. Cook on a hot griddle until golden brown.",
    "Gluten-Free Flour, Eggs, Milk, Baking Powder, Maple Syrup, Salt, Sugar",
    "http://example.com/gluten-free-pancakes.jpg",
    20,
    150,
    ["American"],
    ["Gluten-Free"],
    True,
    True,
    True,
    {"calories": 150, "protein": 5, "carbs": 20, "fat": 5})
    
    response= client.post(CREATE_ENTRY_RECIPE_ENDPOINT, json=second_new_recipe_data.__dict__)
    # asserting correct response (created)
    assert response.status_code == 201

    # asserting the number of recipes has increased by 1 
    response= client.get(GET_FAVORITE_RECIPES_ENDPOINT)
    response_data_after_add: Dict[str, Any] = response.get_json()
    new_num_recipes: int= len(response_data_after_add)
    assert new_num_recipes == num_recipes_after_add + 1
    #asserting second recipe exists in the favorites list
    assert "222" in response_data_after_add

###### Test for adding an existing recipe #######

def test_add_existing_recipe(client)-> None:
    """
    tset if the app can handle adding an existing recipe
    """
    #adding a prexisiting recipe
    recipe: Recipe= Recipe("123", "example recipe", "exampel instruction", "exampel ingrediecnts", "exampel image", 20, 150,
                            ["American"], ["Gluten-Free"], True, True, True, {"calories": 150, "protein": 5, "carbs": 20, "fat": 5})
    response= client.post(CREATE_ENTRY_RECIPE_ENDPOINT, json= recipe.__dict__) #add this recipe

    assert response.status_code== 201 #assert the code (created)

    #adding the same recipe again
    recipe: Recipe= Recipe("123", "example recipe", "exampel instruction", "exampel ingrediecnts", "exampel image", 20, 150,
                            ["American"], ["Gluten-Free"], True, True, True, {"calories": 150, "protein": 5, "carbs": 20, "fat": 5})
    response= client.post(CREATE_ENTRY_RECIPE_ENDPOINT, json= recipe.__dict__) #add this recipe

    response_data= response.get_json() #get the response data

    assert response.status_code== 409 #assert the code (conflict)

    assert "Error" in response_data #assert the error message is in the response
    assert response_data["Error"]== "Recipe already exists in favorites" #assert the error message is the  same as the one returned by the app

#####################################################
##                TEST DELETE                      ##
##################################################

####### Test for Deleteing a favorite recipe #######

def test_delete_favorite_recipe(client)-> None:
    """
    test deleteing a recipe from favorites using the recipe id
    """
    #create a recipe
    recipe: Recipe= Recipe("123", "delete title", "delete instructions", "delete ingredients", "delete image", 20, 150,
                            ["American"], ["Gluten-Free"], True, True, True, {"calories": 150, "protein": 5, "carbs": 20, "fat": 5})
    response= client.post(CREATE_ENTRY_RECIPE_ENDPOINT, json= recipe.__dict__) #add this recipe
    assert response.status_code== 201 #assert the code (created)

    response= client.delete(f"/recipewiki/favorites/{recipe.recipe_id}") #delete this recipe
    assert response.status_code== 200 #assert the code (ok)
    assert "message" in response.get_json() #assert the message is in the response
    assert response.get_json()["message"]== "Recipe deleted from favorites successfully." #assert the message is the same as the one returned by the app

    response_after_delete= client.get(f"/recipewiki/favorites/{recipe.recipe_id}") #try toget the recipe after deleting it
    assert response_after_delete.status_code== 404 #assert the code (not found)
    assert "Error" in response_after_delete.get_json() #assert the error message is in the response
    assert response_after_delete.get_json()["Error"]== "Recipe does not exist in favorites" #assert the error message is the same as the one returned by the app

###### Test for deleting a non existing recipe #######

def test_delete_non_existing_recipe(client)-> None:
    """
    test deleteing a non existing recipe from favorites
    """
    
    response= client.delete("/recipewiki/favorites/123") #try to delete a non existing recipe
    assert response.status_code== 404 #assert the code (not found)
    assert "Error" in response.get_json() #assert the error message is in the response
    assert response.get_json()["Error"]== "Recipe does not exist in favorites" #assert the error message is the same as the one returned by the app

#############################################################
##               TEST GET                                  ##
#############################################################

####### Test for getting a favorite recipe by id #######

def test_get_favorite_recipe_by_id(client)-> None:
    """
    test retrieving a recipe from favorites by id
    """
    #create two recipes
    recipe_1: Recipe= Recipe("123", "example recipe", "exampel instruction", "exampel ingrediecnts", "exampel image", 20, 150,
                            ["American"], ["Gluten-Free"], True, True, True, {"calories": 150, "protein": 5, "carbs": 20, "fat": 5})
    recipe_2: Recipe= Recipe("124", "example recipe2", "exampel instruction2", "exampel ingrediecnts2", "exampel image2", 20, 150,
                            ["American"], ["Gluten-Free"], True, True, True, {"calories": 150, "protein": 5, "carbs": 20, "fat": 5})
    response= client.post(CREATE_ENTRY_RECIPE_ENDPOINT, json= recipe_1.__dict__)
    assert response.status_code== 201

    response= client.post(CREATE_ENTRY_RECIPE_ENDPOINT, json= recipe_2.__dict__)
    assert response.status_code== 201

    new_response= client.get(f"/recipewiki/favorites/{recipe_2.recipe_id}") #get the recipe by id
    assert new_response.status_code== 200 #assert the code (ok)

    data= new_response.get_json() #get the data from the response

    assert data["title"]== recipe_2.title #assert the title from the responseis the same as the one in the recipe

###### Test for getting all favorite recipes #######

def test_get_all_favorite_recipes(client)-> None:
    """"
    test retrieving all recipes from favorites
    """
    #create two recipes
    recipe_1: Recipe= Recipe("123", "example recipe", "exampel instruction", "exampel ingrediecnts", "exampel image", 20, 150,
                            ["American"], ["Gluten-Free"], True, True, True, {"calories": 150, "protein": 5, "carbs": 20, "fat": 5})
    recipe_2: Recipe= Recipe("124", "example recipe2", "exampel instruction2", "exampel ingrediecnts2", "exampel image2", 20, 150,
                            ["American"], ["Gluten-Free"], True, True, True, {"calories": 150, "protein": 5, "carbs": 20, "fat": 5})
    response= client.post(CREATE_ENTRY_RECIPE_ENDPOINT, json= recipe_1.__dict__)
    assert response.status_code== 201
    response= client.post(CREATE_ENTRY_RECIPE_ENDPOINT, json= recipe_2.__dict__)
    assert response.status_code== 201

    new_response= client.get(GET_FAVORITE_RECIPES_ENDPOINT) #get all recipes
    assert new_response.status_code== 200 #assert the code (ok)

    data= new_response.get_json() #get the data from the response
    assert len(data)== 2 #assert the that we have two recipes in the favorites
    assert data["123"]["title"]== recipe_1.title
    assert data["124"]["instructions"]== recipe_2.instructions

###### Test for getting a non existing recipe by id #######

def test_get_non_existing_recipe_by_id(client)-> None:
    """
    test retrieving a non existing recipe from favorites by id
    """
    response= client.get("/recipewiki/favorites/123") #try to get a non existing recipe
    assert response.status_code== 404 #assert the code (not found)
    assert "Error" in response.get_json() #assert the error message is in the response
    assert response.get_json()["Error"]== "Recipe does not exist in favorites" #assert the error message is the same as the one returned by the app

###### Test for getting all favorite recipes with no recipes in the favorites #######

def test_get_empty_favorites(client)-> None:
    """
    test retrieving an empty dictionary when there are no recipes in the favorites
    """
    response= client.get(GET_FAVORITE_RECIPES_ENDPOINT)# get all recipes
    assert response.status_code== 200 #assert the code (ok)

    data= response.get_json() 
    assert len(data)== 0 # assert the number of recipes in the favorites db is 0

#############################################################
####          TEST UPDATE                               #####
#############################################################

###### Test for updating a favorite recipe #######

def test_update_favorite_recipe(client)-> None:
    """
    test updating a recipe in favorites
    """
    #adding the recipe that will be updated
    recipe: Recipe = Recipe(
    "222",
    "Gluten-Free Pancakes",
    "1. Mix dry ingredients. 2. Whisk in wet ingredients. 3. Cook on a hot griddle until golden brown.",
    "Gluten-Free Flour, Eggs, Milk, Baking Powder, Maple Syrup, Salt, Sugar",
    "http://example.com/gluten-free-pancakes.jpg",
    20,
    150,
    ["American"],
    ["Gluten-Free"],
    True,
    True,
    True,
    {"calories": 150, "protein": 5, "carbs": 20, "fat": 5})

    response= client.post(CREATE_ENTRY_RECIPE_ENDPOINT, json= recipe.__dict__)

    assert response.status_code == 201

    #adding the recipe that will not be updated
    recipe_2: Recipe= Recipe("124", "example recipe2", "exampel instruction2", "exampel ingrediecnts2", "exampel image2", 20, 150,
                            ["American"], ["Gluten-Free"], True, True, True, {"calories": 150, "protein": 5, "carbs": 20, "fat": 5})
    
    response= client.post(CREATE_ENTRY_RECIPE_ENDPOINT, json= recipe_2.__dict__)
    assert response.status_code == 201
    
    #data to update the recipe
    updated_data_recipe: Dict[str, Any]= {"recipe_id": "222", "title": "The Best Recipe", "instructions": "my new instructions",
                                          "image": "new photo", "ingredients": "non-vegan ingredients", "is_vegan": False}
    
    update_response= client.put(f"/recipewiki/favorites/{recipe.recipe_id}", json= updated_data_recipe) #update the recipe using the updated_data_recipe
    assert update_response.status_code== 200
    
    update_data= update_response.get_json()
    assert "message" in update_data
    assert update_data["message"] == "Recipe updated successfully."# assert the success message

    #check if the recipe was updated
    new_response= client.get(f"/recipewiki/favorites/{recipe.recipe_id}")
    assert new_response.status_code== 200

    #assert the new updated recipe matches the updated_data_recipe
    updated_recipe_data= new_response.get_json()
    assert updated_recipe_data["title"]== "The Best Recipe"
    assert updated_recipe_data["instructions"]== "my new instructions"
    assert updated_recipe_data["image"]== "new photo"
    assert updated_recipe_data["is_vegan"]== False

    #asserting the recipe that we did not update (recipe_2) is not updated
    new_response= client.get(f"/recipewiki/favorites/{recipe_2.recipe_id}")
    assert new_response.status_code == 200
    data= new_response.get_json()
    assert data["title"]== recipe_2.title
    assert data["instructions"]== recipe_2.instructions
    assert data["image"]== recipe_2.image
    assert data["is_vegan"]== recipe_2.is_vegan

###### Test for updating a non existing recipe #######
def test_update_non_existing_recipe(client):
    """
    test updating a non existing recipe in favorites
    """

    #adding a recipe that will not be updated
    recipe: Recipe = Recipe(
    "222",
    "Gluten-Free Pancakes",
    "1. Mix dry ingredients. 2. Whisk in wet ingredients. 3. Cook on a hot griddle until golden brown.",
    "Gluten-Free Flour, Eggs, Milk, Baking Powder, Maple Syrup, Salt, Sugar",
    "http://example.com/gluten-free-pancakes.jpg",
    20,
    150,
    ["American"],
    ["Gluten-Free"],
    True,
    True,
    True,
    {"calories": 150, "protein": 5, "carbs": 20, "fat": 5})

    response= client.post(CREATE_ENTRY_RECIPE_ENDPOINT, json= recipe.__dict__)

    assert response.status_code == 201

    #data to update the recipe
    updated_data_recipe: Dict[str, Any] = {"recipe_id": "222", "title": "The Best Recipe", "instructions": "my new instructions",
                                          "image": "new photo", "ingredients": "non-vegan ingredients", "is_vegan": False}
    
    non_existing_recipe_id= "111"
    
    #try to update a non existing recipe
    update_response= client.put(f"/recipewiki/favorites/{non_existing_recipe_id}", json= updated_data_recipe)

    assert update_response.status_code == 404 #assert the code (not found)

    response_data= update_response.get_json()
    assert "Error" in response_data #assert the error message is in the response
    assert response_data["Error"]== "Recipe does not exist in favorites." #assert the error message is the same as the one returned by the app


################################################
####          TEST SEASONAL FOODS             ###
################################################
@patch('app.get_country_from_ip')
def test_get_seasonal_foods_suggestion_endpoint(mock_get: MagicMock, client):
    """
    Test that we can get a list of seasonal foods for a given country and month.
    """
    #mocking the json data
    favorite_recipes_database.seasonal_food ={
        "Netherlands": {
            "June": ["Strawberries", "Asparagus"]
        }
    }
   
    mock_get.return_value = "Netherlands" #mock the response value of the get_country_from_ip function
  
    response = client.get(GET_SEASONAL_FOODS_ENDPOINT)
    assert response.status_code == 200
    response_data= response.get_json()

    assert response_data["country"] == "Netherlands"
    assert response_data["seasonal_ingredients"] == ["Strawberries", "Asparagus"]
    assert "month" in response_data # assert the month is included


@patch('app.requests.get')
def test_ingredients_search(mock_get: MagicMock, client):
    """
    This function uses the spoonacular to get recipes.
    """
    # This is what our input is when searching for recipes
    mock_response = [{"id": 123, "title": "example"}]
    mock_get.return_value.json.return_value = mock_response
    mock_get.return_value.status_code = 200

    search_params = {
        'ingredients': 'apples,flour,sugar'
    }

    response = client.get("/recipewiki/search", query_string=search_params)

    response_data= response.get_json()
    assert response.status_code == 200
    

    assert len(response_data) == len(mock_response)

    assert response_data[0]["id"] == 123 

@patch('app.requests.get')
def test_recpie_info(mock_get: MagicMock, client):

    """
    this function will test the information of a recipe that the user select
    
    """
    mock_response = {
        "id": 716429,
        "title": "Pasta with Garlic",
        "readyInMinutes": 45,
        "image": "https://example.com/pasta.jpg",
        "instructions": "Follow these steps...",
        "extendedIngredients": [{"original": "cauliflower"}, {"original": "pasta"}],
        "nutrition": {"nutrients": [{"name": "Calories", "amount": 500}]},
        "cuisines": ["Mediterranean"],
        "diets": ["Vegetarian"],
        "glutenFree": False,
        "dairyFree": True,
        "vegan": True
    }

    mock_get.return_value.json.return_value = mock_response
    mock_get.return_value.status_code = 200

    response= client.get('/recipewiki/recipe/111/information')

    assert response.status_code == 200
    response_data = response.get_json()

    # Verify that your app correctly mapped the Spoonacular data to your Recipe object structure
    assert response_data['image'] == "https://example.com/pasta.jpg"
    assert response_data['ingredients'] == ["cauliflower", "pasta"]

    assert response_data['image'] == "https://example.com/pasta.jpg"
