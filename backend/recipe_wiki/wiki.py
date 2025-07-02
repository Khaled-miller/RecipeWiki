from typing import Dict, Any, List
import json


class Recipe:
    """
    Initialize a recipe

    Attributes:
        recipe_id: str 
        title: str
        instructions: str
        ingredients: List[str]
        image: str
        ready_in_minutes: int   cooking time
        calories: int
        cuisines: List[str]
        diets: List[str]
        is_gluten_free: bool allergy information
        is_dairy_free: bool  allergy information
        is_vegan: bool
        nutrition: Dict[str, Any] 
    """
    def __init__(self, recipe_id: str, title: str, instructions: str, ingredients: str, image: str):
        self.recipe_id = recipe_id
        self.title = title
        self.instructions = instructions
        self.ingredients = ingredients
        self.image = image
        
    def __init__(self, recipe_id: str, title: str, instructions: str, ingredients: str, image: str, ready_in_minutes: int,
                  calories: int, cuisines: List[str], diets: List[str], is_gluten_free: bool, is_dairy_free: bool,
                    is_vegan: bool, nutrition: Dict[str, Any]):
        self.recipe_id= recipe_id
        self.title= title
        self.instructions= instructions
        self.ingredients= ingredients
        self.image= image
        self.ready_in_minutes= ready_in_minutes
        self.calories= calories
        self.cuisines= cuisines
        self.diets= diets
        self.is_gluten_free= is_gluten_free
        self.is_dairy_free= is_dairy_free
        self.is_vegan= is_vegan
        self.nutrition= nutrition
        
    def __str__(self)-> str:
        return f"Recipe(recipe_id={self.recipe_id}, title={self.title}, instructions={self.instructions}, ingredients={self.ingredients}, image={self.image})"

class RecipeWiki:
    """
    Initialize Recipewiki app

    Attributes:
        favorite_recipes: dict of the favorite recipes. this dict looks like: Dict[str, Recipe]
        seasonal_food Dict[str, Any]: dict of the seasonal foods
        
        storage_path: str the file path to save the recipes
    """
    def __init__(self, file_path: str):
        self.favorite_recipes: Dict[str, Recipe] = {}
        self.seasonal_food: Dict[str, Any] = {}
        self.storage_path= file_path
    
    def add_recipe(self, recipe: Recipe)-> bool:
        """
        Adds a recipe to favorites_recipes

        Para:
            recipe (Dict[str, Any]): the recipe to add

        Returns:
            bool: True if the recipe was added successfully, False otherwise
        """
        recipe_id= recipe.recipe_id
        if recipe_id in self.favorite_recipes or not recipe_id:
            return False
        self.favorite_recipes[recipe_id]= recipe
        self.save_favorites()
        return True
    
    def get_all_favorites(self)-> Dict[str, Any]:
        """"
        Returns all recipes in favorites_recipes

        """
        recipes_dict: Dict[str, Any]= {}
        for recipe_id, recipe in self.favorite_recipes.items():
            recipes_dict[recipe_id]= recipe.__dict__ #convert from Dict[str, Recipe] to Dict[str, Any] so that it can be returned as a json, making jsonify able to handle it
        return recipes_dict
    
    def get_favorite_recipe_by_id(self, recipe_id: str)-> Dict[str, Any]:

        """
        Returns a recipe from favorites_recipes by recipe_id

        Para:
            recipe_id (str): the id of a recipe to retrieve
        
        returns:
            Dict[str, Any]: the recipe data if found
        """
        if recipe_id not in self.favorite_recipes:
            return None
        return self.favorite_recipes[recipe_id].__dict__ #return the recipe data as a dictionary


    def delete_recipe(self, recipe_id: str)-> bool:
        """
        Deletes a recipe from favorites_recipes by recipe_id

        Para:
            recipe_id (str): the id of the recipe to delete

        Returns:
            bool: True if the recipe was deleted successfully, False otherwise
        """
        if recipe_id not in self.favorite_recipes:
            return False
        del self.favorite_recipes[recipe_id]
        self.save_favorites()
        return True
    
    def update_recipe(self, recipe_id: str, updated_data: Dict[str, Any])-> bool:
        """
        Updates a recipe in favorites_recipes by recipe_id

        Para:
            recipe_id (str): the id of the recipe to update
            updated_data (Dict[str, Any]): the updated data for the recipe

        Returns:
            bool: True if the recipe was updated successfully, False otherwise
        """
        if recipe_id not in self.favorite_recipes:
            return False
        
        recipe_to_update= self.favorite_recipes[recipe_id] #store the recipe to be updated in this variable

        #update the recipe based on the user input
        if "title" in updated_data:
            recipe_to_update.title= updated_data["title"]
        
        if "instructions" in updated_data:
            recipe_to_update.instructions= updated_data["instructions"]

        if "image" in updated_data:
            recipe_to_update.image= updated_data["image"]   
            
        if "ingredients" in updated_data:
            recipe_to_update.ingredients= updated_data["ingredients"]
            
        if "ready_in_minutes" in updated_data:
            recipe_to_update.ready_in_minutes= updated_data["ready_in_minutes"]
            
        if "calories" in updated_data:
            recipe_to_update.calories= updated_data["calories"]
            
        if "cuisines" in updated_data:
            recipe_to_update.cuisines= updated_data["cuisines"]
            
        if "diets" in updated_data:
            recipe_to_update.diets= updated_data["diets"]
            
        if "is_gluten_free" in updated_data:
            recipe_to_update.is_gluten_free= updated_data["is_gluten_free"]
            
        if "is_dairy_free" in updated_data:
            recipe_to_update.is_dairy_free= updated_data["is_dairy_free"]
            
        if "is_vegan" in updated_data:
            recipe_to_update.is_vegan= updated_data["is_vegan"]
            
        if "nutrition" in updated_data:
            recipe_to_update.nutrition= updated_data["nutrition"]

        
        self.save_favorites()
        return True
    


    def get_seasonal_food(self, country: str, month: str) -> List[str]:
        """
        get seasonal food by country and month

        Para:
            country str: the country to get the seasonal food for
            month str: the month to get the seasonal food for

        Returns:
            List[str]: the seasonal food/ingredients for the given country and month or an empty list if the country or month is not found
        """
        if country in self.seasonal_food:
            months_data= self.seasonal_food[country]

            if month in months_data:
                return months_data[month]

        return []  

    #### helper functions ####

    def load_favorites(self)-> None:
        """
        Loads the favorite recipes from the JSON file into memory.

        """
        try:
            with open(self.storage_path, 'r') as f:
                data_from_disk= json.load(f)
           
                for recipe_id, recipe_data in data_from_disk.items():
                    self.favorite_recipes[recipe_id]= Recipe(**recipe_data) #convert the raw dictionaries back into Recipe objects
        except (FileNotFoundError, json.JSONDecodeError):
           
            self.favorite_recipes= {}

    def save_favorites(self)-> None:
        """
        Saves the current list of favorite recipes to the JSON file.

        """
        data_to_save= {recipe_id: recipe_object.__dict__ for recipe_id, recipe_object in self.favorite_recipes.items()} #turn the recipe objects into dict

        with open(self.storage_path, 'w') as f:
            json.dump(data_to_save, f, indent=4)


    def load_seasonal_data(self, seasonal_file_path: str):
        """
        loads the seasonal data
        """
        try:
            with open(seasonal_file_path, 'r') as f:
                self.seasonal_food= json.load(f)
        except FileNotFoundError:
            print(f"Error: seasonal_food file not found at {seasonal_file_path}")
            self.seasonal_food= {}
        except json.JSONDecodeError:
            print(f"Error: Could not decode jSON from {seasonal_file_path}")
            self.seasonal_food = {}


    def clear_favorites(self)->None:
        """
        Helper function deletes all recipes from favorites_recipes before each test
        """
        self.favorite_recipes.clear()

