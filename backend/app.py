from flask import Flask, jsonify,request, Response, render_template
from typing import Dict, Any, List
from recipe_wiki import RecipeWiki, Recipe
import requests
import os
from dotenv import load_dotenv #load the .env to get the api keys
from datetime import datetime
import uuid
import json
from flask_cors import CORS
#get the joke api key from the environment variable
load_dotenv()
API_KEY= os.environ.get("SPOONACULAR_API_KEY")
SPOONACULAR_API = "https://api.spoonacular.com"

app = Flask(
    __name__,
    template_folder='../frontend/templates',
    static_folder='../frontend/static'
)
CORS(app)


#this database is to store the favorite recipes
favorite_recipes_database: RecipeWiki= RecipeWiki("favorite_recipes.json") 
favorite_recipes_database.load_favorites() #load the favorite recipes from the json file

#get the seasonal file path
seasonal_file= os.path.join(os.path.dirname(__file__), "seasonal_food.json")
favorite_recipes_database.load_seasonal_data(seasonal_file) #load the seasonal data from the json file

#endpoints
CREATE_ENTRY_RECIPE_ENDPOINT = "/recipewiki/favorites"
GET_FAVORITE_RECIPES_ENDPOINT= "/recipewiki/favorites"
GET_SEASONAL_FOODS_ENDPOINT = "/recipewiki/suggestions/seasonal"

@app.route('/')
def home():
    """
    A simple home page to confirm the backend is running.
    """
    return render_template('index.html')

#health check endpoint
@app.route('/health') 
def health_check()-> Response:
    """
    ensure that the backend is running
    """
    return 'OK', 200

##### helper functions #####

def get_country_from_ip(ip_address: str)-> str:
    """
    helper function returns the country from the ip address

    Para:
      ip_address (str): the ip address to get the country from
    
    returns:
        str: the country from the ip address or "Unknown Country" if the country is not found
    """
    #ip 127.0.0.1 is the defult ip for the local machine
    if ip_address== "127.0.0.1":  
        return "Netherlands" #return the country for the local machine when testing locally
    try:
        response= requests.get(f"http://ip-api.com/json/{ip_address}")
        response.raise_for_status() #raise an exception if the request fails
        data= response.json()
        return data.get("country", "Unknown Country") #return the country or "NA" if the country is not found
    except requests.exceptions.RequestException as e:
        print(f"Error getting country from this ip: {ip_address}: {e}")
        return "Unknown Country" #return "NA" if the country is not found

### CRUD endpoints ###

@app.route('/recipewiki/favorites', methods=['Post'])
def add_recipe_to_favorites()-> Response:
    """
    This endpoint adds a recipe to the favorites list

     returns:
        Response: Json containing a message and the status code
    """
    data= request.get_json()

    #extarct the recipe data from the request 
    new_recipe_to_add: Recipe= Recipe(
    recipe_id=data.get("recipe_id"),
    title=data.get("title"),
    instructions=data.get("instructions"),
    ingredients=data.get("ingredients"),
    image=data.get("image"),
    ready_in_minutes=data.get("ready_in_minutes"),
    calories=data.get("calories"),
    cuisines=data.get("cuisines"),
    diets=data.get("diets"),
    is_gluten_free=data.get("is_gluten_free"),
    is_dairy_free=data.get("is_dairy_free"),
    is_vegan=data.get("is_vegan"),
    nutrition=data.get("nutrition")
)
    #check if the recipe has all the required fields
    if not new_recipe_to_add.recipe_id:
        return jsonify({"Error": "ID is required to add a recipe to favorites"}), 400 #bad request
    if not new_recipe_to_add.title:
        return jsonify({"Error": "Title is required to add a recipe to favorites"}), 400 
    if not new_recipe_to_add.instructions:
        return jsonify({"Error": "Instructions are required to add a recipe to favorites"}), 400 
    if not new_recipe_to_add.ingredients:
        return jsonify({"Error": "Ingredients are required to add a recipe to favorites"}), 400 
    if not new_recipe_to_add.image:
        return jsonify({"Error": "Image is required to add a recipe to favorites"}), 400 
    #store the recipe in the db, where the key is the recipe_id and full recipe data is the value
    success=favorite_recipes_database.add_recipe(new_recipe_to_add) #use the add_recipe method to add the recipe
    if not success:
        return jsonify({"Error": "Recipe already exists in favorites"}), 409 # conflict
    
    #this a default joke in case the api call fails
    joke= "Error fetching a joke at the moment"
    try:
        param= {"apiKey": API_KEY} #the joke endpoint requires only the apiKey
        joke_response= requests.get(f"https://api.spoonacular.com/food/jokes/random", params=param) #get the joke
        if joke_response.status_code== 200:
            joke_data = joke_response.json()
            #Spoonacular joke api fromat: {"text": "Any salad can be a Caesar salad if you stab it enough."}
            joke= f"{joke_data['text']}"
    except requests.exceptions.RequestException as e:
        # in case the api call fails, log the error and use the error message instead of the api's joke
        print(f"Not able to fetch a joke: {e}")

    #return both the success message and the joke
    return_response={"message": "Recipe added to favorites successfully.", "joke": joke}
    return jsonify(return_response), 201

@app.route('/recipewiki/favorites', methods=['Get'])
def get_all_favorites()-> Response:
    """
    This endpionts returns all recipes in the favorites

     returns:
        Response: Json containing all recipes in favorites and the status code
    """
    return jsonify(favorite_recipes_database.get_all_favorites()), 200 #use the get_all_favorites method to get all recipes

@app.route('/recipewiki/favorites/<recipe_id>', methods=['Get'])
def get_favorite_recipe_by_id(recipe_id)-> Response:
    """
    This endpoint returns a recipe from the favorites list using the recipe id

    Para:
      recipe_id (str): the id of the recipe to get
    
    returns:
        Response: Json containing the recipe info and the status code
    """
    recipe= favorite_recipes_database.get_favorite_recipe_by_id(recipe_id) #use the get_favorite_recipe_by_id method to get the recipe by its id
    if not recipe:
        return jsonify({"Error": "Recipe does not exist in favorites"}), 404 #not found
    
    return jsonify(recipe), 200 #ok

@app.route('/recipewiki/favorites/<recipe_id>', methods=['DELETE'])
def delete_recipe_from_favorites(recipe_id)-> Response:
    """
    This endpoint deletes a recipe from the favorites list using the recipe id

    Para:
      recipe_id (str): the id of the recipe to delete
    
    returns:
        Response: Json containing a message and the status code
    """
    success= favorite_recipes_database.delete_recipe(recipe_id) #use the delete_recipe method to delete the recipe
    if not success:
        return jsonify({"Error": "Recipe does not exist in favorites"}), 404 #not found
    return jsonify({"message": "Recipe deleted from favorites successfully."}), 200 #ok

@app.route('/recipewiki/favorites/<recipe_id>', methods=['PUT'])
def update_recipe(recipe_id)-> Response:
    """
    This endpoint updates a recipe in the favorites list using the recipe id
    """
    data= request.get_json()
    success= favorite_recipes_database.update_recipe(recipe_id, data) #use the update_recipe method to update the recipe
    if not success:
        return jsonify({"Error": "Recipe does not exist in favorites."}), 404 #not found
    return jsonify({"message": "Recipe updated successfully."}), 200 #ok




@app.route('/recipewiki/suggestions/seasonal', methods=['GET'])
def get_seasonal_food_suggestions()-> Response:
    """
    This endpoint returns a list of seasonal foods for a given country and month
    """
    user_ip= request.remote_addr #get the ip address of the user
    country= get_country_from_ip(user_ip) #get the country from the ip address

    now = datetime.now()
    month= now.strftime("%B") #get the full month name
    

    seasonal_ingredients= favorite_recipes_database.get_seasonal_food(country, month) #get the seasonal foods
    suggestion= {   #the response format 
        "country": country,
        "month": month,
        "seasonal_ingredients": seasonal_ingredients
    }
    return jsonify(suggestion), 200 #ok



FOOD_INGREDIENTS = "https://api.spoonacular.com/recipes/findByIngredients"
@app.route('/recipewiki/search', methods=['Get'])
def ingredients_search():
    """
    This function uses the spoonacular to get recipes based on parameters.
    """
    ingredients = request.args.get("ingredients")

    if not ingredients:
        return jsonify({"Error": "The 'ingredients' query parameter is required."}), 400
    try:
        params ={"apiKey": API_KEY, "ingredients": ingredients, "number": 10, "ranking": 2, "ignorePantry": True}
        response = requests.get(FOOD_INGREDIENTS, params)
        response.raise_for_status() 
        response.status_code == 200
        data = response.json()
        return jsonify(data)
    except requests.exceptions.RequestException as e:
        print(f"Not able to fetch the recipes: {e}")
        return jsonify({"Error": "Failed to fetch recipes from external API"}), 503        


def get_calories_from_data(data):
  nutrition_data = data.get('nutrition', {})
  nutrients_list = nutrition_data.get('nutrients', [])

  for nutrient in nutrients_list:
    if nutrient.get('name') == 'Calories':
      return nutrient.get('amount', 0)
  return 0

@app.route('/recipewiki/recipe/<int:recipe_id>/information', methods=['GET'])
def recipe_info(recipe_id: int):
    """
    This function given info on each recipe based on their id.
    """
    try:
       
        information_response = requests.get(f"https://api.spoonacular.com/recipes/{recipe_id}/information", {"apiKey": API_KEY, "includeNutrition": True})
        information_response.raise_for_status() 
        # common_allergies = ["Peanuts", "Almonds", "Walnuts", "Cashews", "Milk", "Eggs", "Wheat", "Soy", "Fish", "Shrimp", "Crab", "Lobster"]

        # allergies_found = []
        # ingredient = []

        # for ingredient in information_response.get('extendedIngredients', []):
        #     ingredient.append(ingredient["name"])
        #     if ingredient["name"] in common_allergies:
        #         allergy.append(ingredient["name"])

        spoonacular_data = information_response.json()

        recipe_object = Recipe(
            recipe_id=str(spoonacular_data.get('id')),
            title=spoonacular_data.get('title'),
            instructions=spoonacular_data.get('instructions'),
            ingredients=[ing.get('original') for ing in spoonacular_data.get('extendedIngredients', [])],
            image=spoonacular_data.get('image'),
            ready_in_minutes=spoonacular_data.get('readyInMinutes'),
            calories=get_calories_from_data(spoonacular_data),
            cuisines=spoonacular_data.get('cuisines', []),
            diets=spoonacular_data.get('diets', []),
            is_gluten_free=spoonacular_data.get('glutenFree'),
            is_dairy_free=spoonacular_data.get('dairyFree'),
            is_vegan=spoonacular_data.get('vegan'),
            nutrition=spoonacular_data.get('nutrition', {})
            )
        return jsonify(recipe_object.__dict__), 200

        

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Not able to fetch the recipes: {e}"}), 503






# store the shopping lists with id and info
shared_shoppinglist = {}

FX_RATES = {
        "United Kingdom": {"currency": "GBP", "symbol": "£", "rate": 0.741}, 
        "United States": {"currency": "USD", "symbol": "$", "rate": 1.000}, 
        "Canada": {"currency": "CAD", "symbol": "$", "rate": 1.360}, 
        "Netherlands": {"currency": "EUR", "symbol": "€", "rate": 0.868}, 
        "Australia": {"currency": "AUD", "symbol": "A$", "rate": 1.538},
    }


def get_ingredient_price(ingredient_name) -> float:
    """
    Gets the price of the given ingredient in USD using Spoonacular's ingredient endpoint.
    """
    # spoonacular link to ingredient search
    url = f"https://api.spoonacular.com/food/ingredients/search"
    params = {"apiKey": API_KEY, "query": ingredient_name}

    response = requests.get(url, params=params)
    data = response.json()
    
    # extract the id of the ingredient to get more information about the ingredient
    if data["results"]:
        id = data["results"][0]["id"]
        # spoonacular link to get ingredient information
        ingredient_url = f"https://api.spoonacular.com/food/ingredients/{id}/information"
        ingredient_params = {"apiKey": API_KEY, "amount": 1}
        ingredient_response = requests.get(ingredient_url, params=ingredient_params).json()
        return ingredient_response.get("estimatedCost", {}).get("value", 0) /100 # convert cents to dollars


def detect_country_from_request():
    """
    Detects the country of the client using the ip address.
    """
    ip_address = request.remote_addr or "127.0.0.1"
    return get_country_from_ip(ip_address)


@app.route("/recipewiki/shopping-list", methods= ["POST"])
def create_shoppinglist() -> Response:
    """
    Generates a shopping list with all the missing ingredients for a selected recipe based on the user's current ingredients.
    """
    data = request.get_json()
    recipe_id = data.get("recipe_id")

    # get the ingredients the user already has
    user_ingredients = [ingredient.lower() for ingredient in data.get("ingredients", [])]
    print(f"User ingredients: {user_ingredients}")

    # return an error if the user did not select a recipe or enter ingredients
    if not recipe_id or not user_ingredients:
        return jsonify({"error": "Missing recipe_id or ingredients"}), 400

    try: #
    # get the recipe info from Spoonacular
        params = {"apiKey": API_KEY}
    # spoonacular link to the recipe
        response = requests.get(f"https://api.spoonacular.com/recipes/{recipe_id}/information", params=params)
        response.raise_for_status()
        print(f"Spoonacular API Status Code: {response.status_code}") # DEBUG
        recipe_data = response.json()
        print(f"Spoonacular API Response: {recipe_data}") # DEBUG
    except requests.exceptions.RequestException as e:
        print(f"Error fetching from Spoonacular in create_shoppinglist: {e}")
        return jsonify({"error": "Could not retrieve recipe data from the external API."}), 503
    
    recipe_title = recipe_data.get("title", "untitled recipe")
    # get all the ingredients needed for the recipe
    all_ingredients = [ingredient["name"].lower() for ingredient in recipe_data.get("extendedIngredients", [])]
    print(f"All recipe ingredients: {all_ingredients}") # DEBUG
    # compare all_ingredients and the user_ingredients and filter missing ingredients
    missing_ingredients = [ingredient for ingredient in all_ingredients if ingredient not in user_ingredients]
    print(f"Missing ingredients: {missing_ingredients}") # DEBUG
    # get the country of the client
    country = detect_country_from_request()
    fx = FX_RATES.get(country, FX_RATES["Netherlands"]) # default currency is EUR
    rate = fx["rate"]
    symbol = fx["symbol"]
    currency = fx["currency"]

    # get the local markets for the detected country
    with open("supermarkets_by_country.json", "r") as file:
        LOCAL_MARKETS = json.load(file)
    local_markets = LOCAL_MARKETS.get(country, [])

    # start with an empty shopping list and add the missing ingredients
    shopping_list = []
    for ingredient in missing_ingredients:
        try:
            usd_price = get_ingredient_price(ingredient)
            local_price = round(usd_price*rate, 2)
            shopping_list.append({
                "ingredient": ingredient,
                "price": f"{symbol}{local_price}"
            })
        # if there is no price available, print an error message
        except Exception as e:
            print(f"Error getting the price for {ingredient}: {e}")
            shopping_list.append({
                "ingredient": ingredient,
                "price": "Unavailable"
            })

    # create an unique shopping list id
    shoppinglist_id = str(uuid.uuid4()) 
    shared_data = {
        "recipe_title": recipe_title,
        "country": country,
        "currency": currency,
        "shopping_list": shopping_list,
        "local_markets": local_markets,
    }
    # store the data in memory with a dictionary
    shared_shoppinglist[shoppinglist_id] = shared_data
    # create the shareable url to the shoppinglist
    shareable_url = f"{request.host_url}recipewiki/shopping-list/{shoppinglist_id}"
    return jsonify({**shared_data, "shareable_url": shareable_url}), 200


@app.route("/recipewiki/shopping-list/<shoppinglist_id>", methods= ["GET"])
def get_shared_shoppinglist(shoppinglist_id):
    """
    This endpoint returns the shared shopping list.
    """
    # get the shopping list by shopping list id
    shoppinglist = shared_shoppinglist.get(shoppinglist_id)
    # return an error message if the shopping list id does not exist
    if not shoppinglist:
        return jsonify({"error": "Shopping list not found"}), 404
    return render_template("shopping_list.html", list_data=shoppinglist)

@app.route("/recipewiki/shopping-list/markets", methods= ["POST"])
def get_local_markets():
    """
    This endpoint gets the local markets of the client's country. 
    """
    data = request.get_json()
    country = detect_country_from_request()

    # get the local markets for the detected country
    with open("supermarkets_by_country.json", "r") as file:
        LOCAL_MARKETS = json.load(file)
    market_names = LOCAL_MARKETS.get(country, [])
    
    # transform the list of markets into a list of dictionaries with "name" and "address"
    detailed_markets = []
    for market_name in market_names:
        detailed_markets.append({
            "name": market_name,
            "address": f"{market_name} (various locations in {country})" # placeholder address
        })
    return jsonify({"country": country, "markets": detailed_markets}), 200




@app.route('/recipewiki/recipes', methods=['GET'])
def recipes():
    """
    Outputs all recipes, takes user entry to 
    """
    cuisine= request.args.get("cuisine")
    max_ready_time= request.args.get("maxReadyTime")
    exclude_ingredients= request.args.get("excludeIngredients")
    user_ingredients= request.args.get("ingredients")

    if not user_ingredients:
        return jsonify({"Error": "The 'ingredients' query parameter is required."}), 400
    
    try:
        url = f"{SPOONACULAR_API}/recipes/complexSearch"
        params = {"apiKey": API_KEY, "number": 10, "includeIngredients": user_ingredients, "addRecipeInformation": True} # initiialises params
    
        if cuisine:
            params["cuisine"]= cuisine
        if max_ready_time:
            params["maxReadyTime"]= max_ready_time
        if exclude_ingredients:
            params["excludeIngredients"]= exclude_ingredients

        response = requests.get(url, params=params)
        data= response.json()
        return jsonify(data.get("results", []))

    except requests.exceptions.RequestException as e:
        print(f"Not able to fetch the recipes: {e}")
        return jsonify({"Error": "Failed to fetch recipes from external API"}), 503
    
if __name__ == '__main__':
    app.run(debug=True, port=5000)