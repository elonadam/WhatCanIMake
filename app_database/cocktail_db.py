# cocktail_db.py
import sqlite3
import json
import utilities


class CocktailDB:
    def __init__(self, db_path='app_database/cocktails.db'):
        self.db_path = db_path
        self.connection = sqlite3.connect(self.db_path)
        self.create_tables()
        self.cache = {}  # This dictionary holds the cocktail data for fast lookups.
        # Cache for the makeable cocktails result
        self.last_inventory_hash = None
        self.last_recipe_hash = None
        self.last_makeable_cocktails = None

    def create_tables(self):
        cursor = self.connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cocktails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                abv REAL,
                is_easy_to_make INTEGER,  -- 0 for False, 1 for True
                ingredients TEXT,         -- JSON string storing the list of ingredients
                instructions TEXT,
                personal_notes TEXT,
                is_favorite INTEGER,      -- 0 for False, 1 for True
                times_made INTEGER,
                prep_method TEXT,
                made_from TEXT,           -- Optional field; can be NULL
                flavor TEXT,
                glass_type TEXT,
                garnish TEXT
            )
        ''')
        self.connection.commit()

    def load_cache(self):
        """Load cocktail data from the database into the cache."""
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT id, name, abv, is_easy_to_make, ingredients, instructions, personal_notes, 
                   is_favorite, times_made, prep_method, made_from, flavor, glass_type, garnish
            FROM cocktails
        ''')
        rows = cursor.fetchall()
        self.cache = {}
        for row in rows:
            (cocktail_id, name, abv, is_easy_to_make, ingredients_json, instructions, personal_notes,
             is_favorite, times_made, prep_method, made_from, flavor, glass_type, garnish) = row

            self.cache[name] = {
                'id': cocktail_id,
                'name': name,
                'abv': abv,
                'is_easy_to_make': is_easy_to_make,
                'ingredients': json.loads(ingredients_json),  # Convert JSON string back to a list
                'instructions': instructions,
                'personal_notes': personal_notes,
                'is_favorite': is_favorite,
                'times_made': times_made,
                'prep_method': prep_method,
                'made_from': made_from,
                'flavor': flavor,
                'glass_type': glass_type,
                'garnish': garnish
            }
        return self.cache

    def add_cocktail(self, name, abv, is_easy_to_make, ingredients, instructions, personal_notes,
                     is_favorite, times_made, prep_method, made_from, flavor, glass_type, garnish):
        """
        Adds a new cocktail to the 'cocktails' table and updates the in-memory cache.
        If a cocktail with the same 'name' already exists (due to the UNIQUE constraint),
        this will raise an IntegrityError unless you handle it (try/except).
        """
        ingredients_json = json.dumps(ingredients)
        cursor = self.connection.cursor()
        try:
            cursor.execute('''
                INSERT INTO cocktails (name, abv, is_easy_to_make, ingredients, instructions, personal_notes,
                                       is_favorite, times_made, prep_method, made_from, flavor, glass_type, garnish)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, abv, is_easy_to_make, ingredients_json, instructions, personal_notes,
                  is_favorite, times_made, prep_method, made_from, flavor, glass_type, garnish))
            self.connection.commit()
        except sqlite3.IntegrityError:
            print(f"Error: Cocktail '{name}' already exists in the database!")

        # Update in-memory cache
        self.cache[name] = {
            'abv': abv,
            'is_easy_to_make': is_easy_to_make,
            'ingredients': ingredients,
            'instructions': instructions,
            'personal_notes': personal_notes,
            'is_favorite': is_favorite,
            'times_made': times_made,
            'prep_method': prep_method,
            'made_from': made_from,
            'flavor': flavor,
            'glass_type': glass_type,
            'garnish': garnish
        }
        # print(f"Inserted cocktail: {name}")

    def ingredient_available_by_type(self, inventory_cache, canonical_ing):
        """
        Checks if an ingredient (canonical_ing) is available in the inventory_cache.
        First, it attempts to match canonical_ing against the inventory item's type.
        If no type match is found, it then checks for a match against the bottle_name.
        """

        # Check by type first:
        for key, item in inventory_cache.items():
            inv_type = item.get("type", "")
            if canonical_ing == utilities.canonicalize(inv_type) and item.get("curr_amount", 0) > 0:
                return True
        # If no type match, check by bottle_name (exact match):
        if canonical_ing in inventory_cache and inventory_cache[canonical_ing].get("curr_amount", 0) > 0:
            return True
        # Optionally, do a substring check:
        for key, item in inventory_cache.items():
            if canonical_ing in key and item.get("curr_amount", 0) > 0:
                return True
        return False

    def get_makeable_cocktails(self, inventory_cache):
        """
        Returns a list of cocktail recipes (from self.cache) that can be made with the current inventory.

        This function first examines the "made_from" attribute of each cocktail. It ensures that
        if "made_from" is provided (as a list or a string), it processes it as a list of required main ingredients.
        For each required ingredient, it first attempts to match it against the inventory item's type.
        Only if that fails does it compare against the bottle_name.

        Then, it checks the recipe’s ingredients, handling alternatives (e.g., "gin or vodka") similarly.
        Implements caching: if the inventory hasn’t changed (based on hash comparison), returns a cached result.
        """
        current_inventory_hash = utilities.get_inventory_hash(inventory_cache)
        current_recipe_hash = utilities.get_recipe_hash(self.cache)
        # If these match our stored hashes, skip recalculating
        if (current_inventory_hash == self.last_inventory_hash
                and current_recipe_hash == self.last_recipe_hash):
            print("Returning cached makeable cocktails (inventory & recipes unchanged).")
            return self.last_makeable_cocktails

        # current_hash = utilities.get_inventory_hash(inventory_cache)
        # if self.last_inventory_hash is not None and current_hash == self.last_inventory_hash:
        #     print("Returning cached makeable cocktails.")
        #     return self.last_makeable_cocktails

        makeable = []
        for cocktail in self.cache.values():

            can_make = True

            # made_from = cocktail.get("made_from")

            # Then, check the recipe's ingredients.
            if can_make:
                # Instead of using cocktail.get("ingredients", []), use "made_from".
                made_from_field = cocktail.get("made_from", "")
                if isinstance(made_from_field, str):
                    # Split the string by commas and strip extra whitespace.
                    recipe_ingredients = [ing.strip() for ing in made_from_field.split(",") if ing.strip()]
                else:
                    recipe_ingredients = made_from_field  # Assume it's already a list

                for ingredient in recipe_ingredients:
                    # Check for alternatives in the ingredient string (e.g., "gin or vodka")
                    if " or " in ingredient.lower():
                        alternatives = [alt.strip() for alt in ingredient.lower().split(" or ") if alt.strip()]
                        found_alternative = False
                        for alt in alternatives:
                            canonical_alt = utilities.canonicalize(alt)
                            if self.ingredient_available_by_type(inventory_cache, canonical_alt):
                                found_alternative = True
                                break
                        if not found_alternative:
                            can_make = False
                            break
                    else:
                        canonical_ing = utilities.canonicalize(ingredient)
                        if not self.ingredient_available_by_type(inventory_cache, canonical_ing):
                            can_make = False
                            break
                if can_make:
                    makeable.append(cocktail)

        # self.last_inventory_hash = current_hash
        # self.last_makeable_cocktails = makeable

        # store new hashes + new result
        self.last_inventory_hash = current_inventory_hash
        self.last_recipe_hash = current_recipe_hash
        self.last_makeable_cocktails = makeable

        # persist them to disk so we can remember next time
        utilities.save_hashes(current_inventory_hash, current_recipe_hash)

        return makeable

    # def ingredient_available(self, inventory_cache, canonical_ing):
    #     """
    #     Checks if an ingredient (canonical_ing) is available in the inventory_cache.
    #     If canonical_ing is a generic type (e.g., 'whiskey', 'gin', etc.), it checks whether any inventory
    #     item has a matching category.
    #     Otherwise, it does an exact and partial match on the inventory keys.
    #     """
    #     generic_types = {"whiskey", "gin", "rum", "vodka", "tequila", "mezcal", "cognac", "brandy", "liqueur",
    #                      "aperitif"}
    #
    #     # If the ingredient is generic, search by category.
    #     if canonical_ing in generic_types:
    #         for key, item in inventory_cache.items():
    #             # Compare the category from the inventory (lowercased) to the generic term.
    #             if item.get("category", "").lower() == canonical_ing and item.get("curr_amount", 0) > 0:
    #                 return True
    #         return False
    #
    #     # Otherwise, check for an exact match.
    #     if canonical_ing in inventory_cache and inventory_cache[canonical_ing].get('curr_amount', 0) > 0:
    #         return True
    #
    #     # Fall back: Check for a partial match within the inventory keys.
    #     for key, item in inventory_cache.items():
    #         if canonical_ing in key and item.get("curr_amount", 0) > 0:
    #             return True
    #
    #     return False

    def import_cocktails_from_json(self, json_file):
        """
        Imports cocktail recipes from a JSON file (e.g. 'cocktail_book.json')
        into the 'cocktails' table. The JSON is expected to have a structure
        similar to your original 'import_recipes.py' example, where the top-level
        is a dictionary, with each key being a unique ID/string, and each value
        holding the recipe info.
        """
        with open(json_file, 'r', encoding='utf-8') as file:
            cocktails_data = json.load(file)

        # Loop through each item in the JSON and insert into DB
        for key, recipe in cocktails_data.items():
            name = recipe.get("name")
            abv = recipe.get("abv")
            is_easy_to_make = 1 if recipe.get("is_easy_to_make", False) else 0
            # Convert the list of ingredients to a Python list (will re-JSONify below)
            ingredients = recipe.get("ingredients", [])
            instructions = recipe.get("instructions", "")
            personal_notes = recipe.get("personal_notes", "")
            is_favorite = 1 if recipe.get("is_favorite", False) else 0
            times_made = recipe.get("times_made", 0)
            prep_method = recipe.get("method")
            made_from = recipe.get("made_from")
            flavor = recipe.get("flavor", None)
            glass_type = recipe.get("glass_type", None)
            garnish = recipe.get("garnish", None)

            self.add_cocktail(
                name=name,
                abv=abv,
                is_easy_to_make=is_easy_to_make,
                ingredients=ingredients,
                instructions=instructions,
                personal_notes=personal_notes,
                is_favorite=is_favorite,
                times_made=times_made,
                prep_method=prep_method,
                made_from=made_from,
                flavor=flavor,
                glass_type=glass_type,
                garnish=garnish
            )

        print("Cocktail recipes have been successfully imported from JSON.")

    def close(self):
        self.connection.close()
