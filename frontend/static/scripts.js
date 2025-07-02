document.addEventListener('DOMContentLoaded', () => {
    // --- DOM ELEMENT REFERENCES ---
    const searchForm = document.getElementById('search-form');
    const searchInput = document.getElementById('search-input');
    const cuisineFilter = document.getElementById('cuisine-filter');
    const timeFilter = document.getElementById('time-filter');
    const excludeFilter = document.getElementById('exclude-filter');
    const recipeGrid = document.getElementById('recipe-grid');
    const favoritesGrid = document.getElementById('favorites-grid');
    const seasonalContainer = document.getElementById('seasonal-container');
    const favoritesLink = document.getElementById('favorites-link');
    const recipeModal = document.getElementById('recipe-modal');
    const modalContentArea = document.getElementById('modal-content-area');
    const modalCloseBtn = document.getElementById('modal-close-btn');
    const modalImage = document.getElementById('modal-image');
    const modalTitle = document.getElementById('modal-title');
    const modalMeta = document.getElementById('modal-meta');
    const modalButtonsContainer = document.getElementById('modal-buttons-container');
    const modalIngredients = document.getElementById('modal-ingredients');
    const modalInstructions = document.getElementById('modal-instructions');
    const modalTags = document.getElementById('modal-tags');
    const modalDetailsSection = document.getElementById('modal-details-section');
    const updateTitleInput = document.getElementById('update-title');
    const updateImageInput = document.getElementById('update-image');
    const updateIngredientsInput = document.getElementById('update-ingredients');
    const updateInstructionsInput = document.getElementById('update-instructions');
    const updateIsVeganCheckbox = document.getElementById('update-is-vegan');
    const updateIsDairyFreeCheckbox = document.getElementById('update-is-dairy-free');
    const updateIsGlutenFreeCheckbox = document.getElementById('update-is-gluten-free');
    const shoppingFormSection = document.getElementById('shopping-form-section');
    const shoppingListForm = document.getElementById('shopping-list-form');
    const shoppingListRecipeId = document.getElementById('shopping-list-recipe-id');
    const shoppingFormTitle = document.getElementById('shopping-form-title');
    const userIngredientsInput = document.getElementById('user-ingredients');
    const shoppingListDisplaySection = document.getElementById('shopping-list-display-section');
    const shoppingListRecipeTitle = document.getElementById('shopping-list-recipe-title');
    const missingIngredientsList = document.getElementById('missing-ingredients-list');
    const localMarketsList = document.getElementById('local-markets-list');
    const shareButton = document.getElementById('share-button');

    // --- NEW: References for the stylish joke modal ---
    const jokeModal = document.getElementById('joke-modal');
    const jokeModalCloseBtn = document.getElementById('joke-modal-close-btn');
    const jokeModalOkBtn = document.getElementById('joke-modal-ok-btn');
    const jokeModalMessage = document.getElementById('joke-modal-message');
    const jokeModalJoke = document.getElementById('joke-modal-joke');


    const API_BASE_URL = 'http://127.0.0.1:5000/recipewiki';
    let currentRecipeData = {};

    const populateFilters = () => {
        const cuisines = ["African", "Asian", "American", "British", "Cajun", "Caribbean", "Chinese", "Eastern European", "European", "French", "German", "Greek", "Indian", "Irish", "Italian", "Japanese", "Jewish", "Korean", "Latin American", "Mediterranean", "Mexican", "Middle Eastern", "Nordic", "Southern", "Spanish", "Thai", "Vietnamese"];
        cuisines.forEach(c => { const option = document.createElement('option'); option.value = c; option.textContent = c; cuisineFilter.appendChild(option); });
    };

    const createRecipeCard = (recipe, isFavorite = false) => {
        const card = document.createElement('div');
        card.className = 'recipe-card';
        const recipeId = recipe.recipe_id || recipe.id;
        card.dataset.recipeId = recipeId;
        card.dataset.isFavorite = isFavorite;

        const imageUrl = recipe.image || 'https://via.placeholder.com/300x200.png?text=No+Image';
        
        let caloriesDisplay = (recipe.calories !== null && recipe.calories !== undefined) ? recipe.calories : 'N/A';
        let minutesDisplay = recipe.ready_in_minutes || 'N/A';

        card.innerHTML = `<div class="recipe-image" style="background-image: url('${imageUrl}')"></div><div class="recipe-content"><h3 class="recipe-title">${recipe.title}</h3><div class="recipe-meta" id="meta-${recipeId}"><span><i class="fas fa-clock"></i> ${minutesDisplay} mins</span><span><i class="fas fa-fire"></i> ${caloriesDisplay} cal</span></div></div>`;

        if (!isFavorite && (recipe.calories === undefined || recipe.ready_in_minutes === undefined)) {
             fetch(`${API_BASE_URL}/recipe/${recipeId}/information`)
                 .then(response => response.json())
                 .then(details => {
                     const metaContainer = card.querySelector(`#meta-${recipeId}`);
                     const finalCalories = (details.calories !== null && details.calories !== undefined) ? details.calories : 'N/A';
                     const finalMinutes = details.ready_in_minutes || 'N/A';
                     metaContainer.innerHTML = `<span><i class="fas fa-clock"></i> ${finalMinutes} mins</span><span><i class="fas fa-fire"></i> ${finalCalories} cal</span>`;
                 });
        }
        
        card.addEventListener('click', () => openRecipeModal(recipeId, isFavorite));
        return card;
    };

    const displayRecipes = (recipes, container, isFavoriteList = false) => {
        container.innerHTML = '';
        if (!recipes || recipes.length === 0) {
            container.innerHTML = '<p>No matching recipes found. Try adjusting your filters.</p>';
            return;
        }
        recipes.forEach(recipe => {
            container.appendChild(createRecipeCard(recipe, isFavoriteList));
        });
    };
    
// In frontend/static/scripts.js, replace the entire searchForm event listener with this:

// In frontend/static/scripts.js

    searchForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        // --- FIX: Added .trim() to remove accidental spaces from user input ---
        const ingredients = searchInput.value.trim();
        const cuisine = cuisineFilter.value;
        const maxReadyTime = timeFilter.value;
        const exclude = excludeFilter.value.trim();

        if (!ingredients) {
            alert("Please enter at least one ingredient to search.");
            return;
        }

        let endpoint = '/search';
        let queryParams = new URLSearchParams({ ingredients: ingredients });

        const hasFilters = cuisine || maxReadyTime || exclude;

        if (hasFilters) {
            endpoint = '/recipes';
            queryParams = new URLSearchParams();
            queryParams.set('ingredients', ingredients); 
            if (cuisine) queryParams.append('cuisine', cuisine);
            if (maxReadyTime) queryParams.append('maxReadyTime', maxReadyTime);
            if (exclude) queryParams.append('excludeIngredients', exclude);
        }

        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}?${queryParams.toString()}`);
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.Error || 'Search request failed');
            }
        
            const data = await response.json();
        
            const recipes = data.results ? data.results : data;

            displayRecipes(recipes, recipeGrid, false);
            document.getElementById('recipes-section').scrollIntoView({ behavior: 'smooth' });

        } catch (error) {
            console.error("Failed to fetch search results:", error);
            recipeGrid.innerHTML = `<p>Error loading recipes: ${error.message}. Please try again later.</p>`;
        }
    });

    const loadSeasonalSuggestions = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/suggestions/seasonal`);
            const suggestions = await response.json();
            seasonalContainer.innerHTML = `<h2 class="section-title">Seasonal Suggestions</h2><div class="seasonal-content"><div class="seasonal-info"><div class="seasonal-tag">${suggestions.month} in ${suggestions.country}</div><h3>Fresh & In-Season</h3><p>Based on your location, these ingredients are currently at their peak and perfect for your next meal.</p><div class="seasonal-ingredients">${suggestions.seasonal_ingredients.map(ing => `<div class="ingredient">${ing}</div>`).join('')}</div></div><div class="seasonal-image"></div></div>`;
        } catch (error) {
            console.error("Failed to fetch seasonal suggestions:", error);
            seasonalContainer.innerHTML = '<p>Could not load seasonal suggestions.</p>';
        }
    };

    const loadFavorites = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/favorites`);
            const favoritesData = await response.json();
            const favoritesArray = Object.values(favoritesData);
            displayRecipes(favoritesArray, favoritesGrid, true);
        } catch (error) {
            console.error("Failed to fetch favorites:", error);
            favoritesGrid.innerHTML = '<p>Could not load your favorites.</p>';
        }
    };
    
    favoritesLink.addEventListener('click', (e) => {
        e.preventDefault();
        loadFavorites();
        document.getElementById('favorites-section').scrollIntoView({ behavior: 'smooth' });
    });
    
    const openRecipeModal = async (recipeId, isFavorite) => {
        try {
            const fetchUrl = isFavorite ? `${API_BASE_URL}/favorites/${recipeId}` : `${API_BASE_URL}/recipe/${recipeId}/information`;
            const response = await fetch(fetchUrl);
            if (!response.ok) throw new Error(`Failed to fetch from ${fetchUrl}`);
            
            currentRecipeData = await response.json();
            exitUpdateMode(isFavorite);
            recipeModal.style.display = 'block'; // Keep the original, working method
            document.body.style.overflow = 'hidden';
        } catch (error) {
            console.error("Failed to fetch recipe details:", error);
            alert('Error: Could not load recipe details.');
        }
    };
    
    const populateViewMode = (recipe) => {
        modalImage.style.backgroundImage = `url('${recipe.image}')`;
        modalTitle.textContent = recipe.title;
        const caloriesDisplay = (recipe.calories !== null && recipe.calories !== undefined) ? recipe.calories : 'N/A';
        modalMeta.innerHTML = `<span><i class="fas fa-clock"></i> ${recipe.ready_in_minutes || 'N/A'} mins</span><span><i class="fas fa-fire"></i> ${caloriesDisplay} calories</span>`;
        const ingredientsList = Array.isArray(recipe.ingredients) ? recipe.ingredients.map(ing => `<li>${ing}</li>`).join('') : (recipe.ingredients || '').split(',').map(i => `<li>${i.trim()}</li>`).join('');
        modalIngredients.innerHTML = ingredientsList;
        
        const instructionsHtml = (recipe.instructions || "").split('\n').filter(line => line.trim() !== '').map(step => `<li>${step.replace(/^\d+\.\s*/, '')}</li>`).join('');
        modalInstructions.innerHTML = instructionsHtml;
        
        let tagsHtml = (recipe.diets || []).map(diet => `<div class="tag">${diet}</div>`).join('');
        if (recipe.is_vegan) tagsHtml += `<div class="tag is_vegan">Vegan</div>`;
        if (recipe.is_dairy_free) tagsHtml += `<div class="tag">Dairy-Free</div>`;
        if (recipe.is_gluten_free) tagsHtml += `<div class="tag">Gluten-Free</div>`;

        if (tagsHtml.trim() === '') {
            modalDetailsSection.style.display = 'none';
        } else {
            modalDetailsSection.style.display = 'block';
            modalTags.innerHTML = tagsHtml;
        }
    };

    const enterUpdateMode = () => {
        const recipe = currentRecipeData;
        updateTitleInput.value = recipe.title;
        updateImageInput.value = recipe.image;
        updateIngredientsInput.value = Array.isArray(recipe.ingredients) ? recipe.ingredients.join('\n') : recipe.ingredients;
        updateInstructionsInput.value = recipe.instructions;
        updateIsVeganCheckbox.checked = recipe.is_vegan;
        updateIsDairyFreeCheckbox.checked = recipe.is_dairy_free;
        updateIsGlutenFreeCheckbox.checked = recipe.is_gluten_free;

        modalContentArea.classList.add('edit-mode-active');
        
        modalButtonsContainer.innerHTML = `<button id="modal-save-btn"><i class="fas fa-save"></i> Save Changes</button><button id="modal-cancel-btn" class="delete-btn"><i class="fas fa-times"></i> Cancel</button>`;
        document.getElementById('modal-save-btn').addEventListener('click', () => saveChanges(recipe.recipe_id));
        document.getElementById('modal-cancel-btn').addEventListener('click', () => exitUpdateMode(true));
    };

    const exitUpdateMode = (isFavorite) => {
        const recipe = currentRecipeData;
        const recipeId = recipe.recipe_id || recipe.id;
        populateViewMode(recipe);
        modalContentArea.classList.remove('edit-mode-active');
        modalButtonsContainer.innerHTML = '';

        if (isFavorite) {
            modalButtonsContainer.innerHTML = `<button id="modal-update-btn"><i class="fas fa-edit"></i> Update</button><button id="modal-delete-btn" class="delete-btn"><i class="fas fa-trash"></i> Delete</button><button id="modal-create-shopping-list-btn"><i class="fas fa-shopping-cart"></i> Shopping List</button>`;
            document.getElementById('modal-delete-btn').addEventListener('click', () => deleteFavorite(recipeId));
            document.getElementById('modal-update-btn').addEventListener('click', enterUpdateMode);
        } else {
            modalButtonsContainer.innerHTML = `<button id="modal-add-to-favorites-btn"><i class="fas fa-heart"></i> Add to Favorites</button><button id="modal-create-shopping-list-btn"><i class="fas fa-shopping-cart"></i> Shopping List</button>`;
            document.getElementById('modal-add-to-favorites-btn').addEventListener('click', () => addToFavorites(recipeId));
        }
        document.getElementById('modal-create-shopping-list-btn').addEventListener('click', () => setupShoppingList(recipeId, recipe.title));
    };

    const saveChanges = async (recipeId) => {
        const updatedData = {
            title: updateTitleInput.value, image: updateImageInput.value,
            ingredients: updateIngredientsInput.value.split('\n').filter(i => i.trim() !== ''),
            instructions: updateInstructionsInput.value, is_vegan: updateIsVeganCheckbox.checked,
            is_dairy_free: updateIsDairyFreeCheckbox.checked, is_gluten_free: updateIsGlutenFreeCheckbox.checked,
        };
        const response = await fetch(`${API_BASE_URL}/favorites/${recipeId}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(updatedData) });
        const result = await response.json();
        alert(result.message || result.Error);
        if (response.ok) {
            currentRecipeData = {...currentRecipeData, ...updatedData};
            exitUpdateMode(true);
            loadFavorites();
        }
    };

    // --- MODIFIED: This function now shows the stylish pop-up instead of an alert ---
    const addToFavorites = async (recipeId) => {
        // We get the full recipe info first
        const infoResponse = await fetch(`${API_BASE_URL}/recipe/${recipeId}/information`);
        if (!infoResponse.ok) {
            alert('Error: Could not get recipe details to save.');
            return;
        }
        const recipeData = await infoResponse.json();

        // Then we send it to be saved in favorites
        const response = await fetch(`${API_BASE_URL}/favorites`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(recipeData)
        });
        const result = await response.json();
    
        if (response.ok) {
            // --- This is the updated part ---
        
            // 1. Set the main success message
            jokeModalMessage.textContent = result.message; 
        
            // 2. Create our new intro sentence
            const creativeIntro = "Great choice! Here's a little chuckle on the house:";
        
            // 3. Combine the intro and the joke, adding line breaks and italics for style
            //    We use .innerHTML here to allow for the <br> and <em> tags.
            jokeModalJoke.innerHTML = `${creativeIntro}<br><br><em>"${result.joke}"</em>`;
        
            // 4. Show the modal
            jokeModal.classList.remove('hidden');

        } else {
            alert(result.Error);
        }

        if (response.ok) {
            loadFavorites(); 
        }
    };
    
    const deleteFavorite = async (recipeId) => {
        if (!confirm('Are you sure you want to delete this recipe?')) return;
        const response = await fetch(`${API_BASE_URL}/favorites/${recipeId}`, { method: 'DELETE' });
        const result = await response.json();
        alert(result.message || result.Error);
        if (response.ok) { closeModal(); loadFavorites(); }
    };
    
    // This is the original, working close function for the main recipe modal
    const closeModal = () => {
        recipeModal.style.display = 'none';
        document.body.style.overflow = 'auto';
    };

    // --- NEW: Function to close the stylish joke modal ---
    const closeJokeModal = () => {
        jokeModal.classList.add('hidden');
    };

    modalCloseBtn.addEventListener('click', closeModal);
    window.addEventListener('click', (e) => {
        if (e.target === recipeModal) {
            closeModal();
        }
        // --- NEW: Add background click listener for joke modal ---
        if (e.target === jokeModal) {
            closeJokeModal();
        }
    });

    // --- NEW: Add event listeners for the joke modal buttons ---
    jokeModalCloseBtn.addEventListener('click', closeJokeModal);
    jokeModalOkBtn.addEventListener('click', closeJokeModal);


    const setupShoppingList = (recipeId, recipeTitle) => {
        closeModal();
        shoppingListRecipeId.value = recipeId;
        shoppingFormTitle.textContent = `For Recipe: ${recipeTitle}`;
        shoppingFormSection.classList.remove('hidden');
        shoppingListDisplaySection.classList.add('hidden');
        shoppingFormSection.scrollIntoView({ behavior: 'smooth' });
    };
    
    shoppingListForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const recipeId = shoppingListRecipeId.value;
        const userIngredients = userIngredientsInput.value.split(',').map(s => s.trim()).filter(s => s);
        try {
            const response = await fetch(`${API_BASE_URL}/shopping-list`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ recipe_id: recipeId, ingredients: userIngredients }) });
            const data = await response.json();
            if (data.error) { alert(`Error: ${data.error}`); return; }
            shoppingListRecipeTitle.textContent = `Shopping List for ${data.recipe_title}`;
            if (data.shopping_list && data.shopping_list.length > 0) {
                 missingIngredientsList.innerHTML = data.shopping_list.map(item => `<li class="shopping-item"><span class="item-name">${item.ingredient}</span><span class="item-price">${item.price}</span></li>`).join('');
            } else {
                 missingIngredientsList.innerHTML = `<li class="shopping-item"><span class="item-name">You have all the ingredients needed!</span></li>`;
            }
            if (data.local_markets && data.local_markets.length > 0) {
                 localMarketsList.innerHTML = data.local_markets.map(market => `<li class="shopping-item"><span class="item-name">${market}</span></li>`).join('');
            } else {
                 localMarketsList.innerHTML = '';
            }
            shareButton.dataset.shareUrl = data.shareable_url;
            shoppingListDisplaySection.classList.remove('hidden');
            shoppingListDisplaySection.scrollIntoView({ behavior: 'smooth' });
        } catch(error) {
            console.error('Error creating shopping list:', error);
            alert('Could not generate shopping list.');
        }
    });
    
    shareButton.addEventListener('click', (e) => {
        const url = e.currentTarget.dataset.shareUrl;
        if (url) {
            navigator.clipboard.writeText(url).then(() => alert('Shareable link copied to clipboard!')).catch(err => alert('Could not copy link.'));
        }
    });

    // --- INITIALIZATION ---
    populateFilters();
    loadSeasonalSuggestions();
    loadFavorites();

    // --- Add this game logic to the end of your scripts.js file, inside the DOMContentLoaded listener ---

    const scraps = document.querySelectorAll('.food-scrap');
    const bins = document.querySelectorAll('.waste-bin');
    const scrapsContainer = document.getElementById('scraps-container');
    const scoreEl = document.getElementById('game-score');
    const messageEl = document.getElementById('game-message');
    const resetBtn = document.getElementById('reset-game-btn');

    let score = 0;
    let itemsSorted = 0;
    const totalItems = scraps.length;

    // --- Dragging Events for Food Scraps ---

    scraps.forEach(scrap => {
        scrap.addEventListener('dragstart', (e) => {
            e.dataTransfer.setData('text/plain', e.target.id);
            setTimeout(() => {
                scrap.classList.add('dragging');
            }, 0);
        });

        scrap.addEventListener('dragend', () => {
            scrap.classList.remove('dragging');
        });
    });

    // --- Drop Zone Events for Bins ---

    bins.forEach(bin => {
        bin.addEventListener('dragover', (e) => {
            e.preventDefault(); // This is necessary to allow a drop
            bin.classList.add('drag-over');
        });

        bin.addEventListener('dragleave', () => {
            bin.classList.remove('drag-over');
        });

        bin.addEventListener('drop', (e) => {
            e.preventDefault();
            bin.classList.remove('drag-over');
        
            const id = e.dataTransfer.getData('text/plain');
            const draggable = document.getElementById(id);
        
            const itemCategory = draggable.dataset.category;
            const binCategory = bin.dataset.category;

            // Check if the drop is correct
            if (itemCategory === binCategory) {
                score += 10;
                scoreEl.textContent = score;
                messageEl.textContent = `Correct! "${draggable.textContent}" belongs in ${binCategory}.`;
                messageEl.style.color = 'green';
            
                // Move item visually and disable it
                draggable.style.display = 'none'; // Hide the item
                itemsSorted++;

            } else {
                messageEl.textContent = `Not quite! Think about where "${draggable.textContent}" should really go.`;
                messageEl.style.color = 'red';
            }
        
            // Check if the game is over
            if (itemsSorted === totalItems) {
                messageEl.textContent = `Game Over! Your final score is ${score}. You're a waste-sorting pro!`;
                messageEl.style.color = 'var(--primary)';
                resetBtn.style.visibility = 'visible';
            }
        });
    });


    // --- Reset Game Logic ---

    resetBtn.addEventListener('click', () => {
        // Reset scores and messages
        score = 0;
        itemsSorted = 0;
        scoreEl.textContent = score;
        messageEl.textContent = "Let's play again!";
        messageEl.style.color = 'var(--dark-gray)';
        resetBtn.style.visibility = 'hidden';

        // Move all scraps back to the container and make them visible
        scraps.forEach(scrap => {
            scrapsContainer.appendChild(scrap);
            scrap.style.display = 'inline-flex';
        });
    });
});