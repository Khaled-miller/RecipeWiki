# back-end/tests/context.py
import sys
from pathlib import Path

# Add the root directory to the Python path
root_dir = str(Path(__file__).parent.parent)
sys.path.append(root_dir)
try:
    from app import app, favorite_recipes_database
    from recipe_wiki import RecipeWiki, Recipe
except ImportError:
    print("Error: Could not import app or recipe_wiki modules")
    print(f"Current sys.path: {sys.path}")
    raise
