# RecipeWiki - Functional Requirements

## 1. Core Recipe & Ingredient Functionality
- **Search by Ingredients**: The application must allow users to find recipes based on a list of ingredients they already have. The results should prioritize recipes that use the maximum number of provided ingredients.
- **Recipe Filtering**: Users must be able to filter recipes based on:
    - Cuisine type (e.g., Italian, Mexican).
    - Allergies (by excluding specific ingredients).
    - Cooking Time (e.g., quick meals under 15 minutes, more involved meals under 35 minutes).
- **Detailed Recipe View**: When a user selects a recipe, the application must display detailed information, including:
    - Calories and the prep time.
    - A full list of ingredients.
    - Step-by-step preparation instructions.
    - A list of common another details (Vegan, gluten-free..etc).

## 2. Favorites Management (CRUD)
- **Add to Favorites**: Users must be able to add a recipe to their personal, persistent favorites list.
- **View Favorites**: Users must be able to retrieve and view their complete list of favorite recipes.
- **Update Favorites**: Users must be able to update the information for a recipe in their favorites list.
- **Remove from Favorites**: Users must be able to remove a recipe from their favorites list.

## 3. Shopping List & Local Integration
- **Generate Shopping List**: When a user chooses a recipe, the application will compare the recipe's required ingredients against a list of ingredients the user has. It will then generate a shopping list of only the missing items.
- **Localized Pricing**: The generated shopping list will display the estimated price for each missing ingredient, converted to the user's local currency based on their location.
- **Suggest Nearby Markets**: The application will suggest nearby markets or grocery stores based on the user's detected country.
- **Shareable List**: The generated shopping list must have a unique, shareable URL that can be sent to others.

## 4. Sustainability & Engagement Features
- **Seasonal Suggestions**: The application will detect the user's country and the current month to provide a list of ingredients that are currently in season, promoting local and sustainable food choices.
- **Food Joke**: When a user adds a recipe to their favorites, the confirmation message will include a random food-related joke from an external API.
- **Sorting Game**: The application includes an interactive "Food Waste Sorting Challenge" game where users drag and drop food items into the correct bins (e.g., compost, trash) to learn about waste management.