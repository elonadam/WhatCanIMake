# utilities.py
import unicodedata
import re
import json
import os
from PySide6.QtCore import QPropertyAnimation, QRect

from PySide6.QtCore import QPropertyAnimation, QRect


def slide_transition(stack, new_index):
    """
    Animate a smooth slide transition between widgets in a QStackedWidget.

    Parameters:
    -----------
    stack : QStackedWidget
        The stacked widget managing multiple screens.
    new_index : int
        The index of the widget to slide into view.

    Behavior:
    ---------
    - If the new index is the same as the current one, does nothing.
    - Animates the current screen sliding out to the left.
    - Animates the next screen sliding in from the right.
    - Updates the current index when animation completes.
    """
    current_index = stack.currentIndex()
    if new_index == current_index:
        return

    current_widget = stack.currentWidget()
    next_widget = stack.widget(new_index)

    w, h = stack.width(), stack.height()

    # Position the incoming screen off-screen to the right
    next_widget.setGeometry(QRect(w, 0, w, h))
    next_widget.show()

    # Animate current screen moving left
    anim_out = QPropertyAnimation(current_widget, b"geometry")
    anim_out.setDuration(300)
    anim_out.setStartValue(QRect(0, 0, w, h))
    anim_out.setEndValue(QRect(-w, 0, w, h))

    # Animate new screen moving in from the right
    anim_in = QPropertyAnimation(next_widget, b"geometry")
    anim_in.setDuration(300)
    anim_in.setStartValue(QRect(w, 0, w, h))
    anim_in.setEndValue(QRect(0, 0, w, h))

    # When done, update the current index
    def finalize():
        stack.setCurrentIndex(new_index)
        # Clear references
        stack._anim_in = None
        stack._anim_out = None

    anim_in.finished.connect(finalize)

    # Save animations to prevent GC
    stack._anim_in = anim_in
    stack._anim_out = anim_out

    anim_out.start()
    anim_in.start()


def get_inventory_hash(inventory_cache):
    """
    Compute a hash of the inventory cache. We convert the dictionary to a
    JSON string with sorted keys to ensure consistent ordering.
    """
    inventory_json = json.dumps(inventory_cache, sort_keys=True)
    return hash(inventory_json)


def get_recipe_hash(cocktail_cache):
    """
    Similar idea as get_inventory_hash, but for the cocktail (recipe) cache.
    Convert the cocktail_cache to a JSON string (sorted by keys) and hash it.
    """
    # Example: the cache is a dict of { cocktail_name: { info... }, ... }
    # We need consistent ordering, so use sort_keys=True
    recipe_json = json.dumps(cocktail_cache, sort_keys=True)
    return hash(recipe_json)


def load_hashes(filepath="hashes_cache.json"):
    """
    Loads the stored hashes from a small JSON file. Returns (inventory_hash, recipe_hash).
    If file doesn't exist, returns (None, None).
    """
    if not os.path.exists(filepath):
        return None, None
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("inventory_hash"), data.get("recipe_hash")


def save_hashes(inventory_hash, recipe_hash, filepath="hashes_cache.json"):
    """
    Saves the given hashes to a JSON file, so they persist across runs.
    """
    data = {
        "inventory_hash": inventory_hash,
        "recipe_hash": recipe_hash
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f)


def remove_diacritics(text: str) -> str:
    """
    Removes all diacritic marks (accents) from a given text.
    For example, "Beyoncé" becomes "Beyonce".
    """
    # Normalize text to separate diacritics from characters (NFD = Normal Form Decomposition)
    normalized = unicodedata.normalize('NFD', text)
    # Encode to ASCII bytes, ignoring non-ASCII characters (i.e., the diacritics)
    ascii_bytes = normalized.encode('ascii', 'ignore')
    # Decode back to a regular string
    return ascii_bytes.decode('utf-8')


def canonicalize(ingredient: str) -> str:
    """
    A comprehensive canonicalize function that:
    1. Removes diacritics.
    2. Converts to lowercase.
    3. Applies regex replacements for partial matches (optional).
    4. Looks up final synonyms in a dictionary.
    """

    # Step 1: Remove diacritics
    text = remove_diacritics(ingredient)

    # Step 2: Convert to lowercase
    text = text.lower().strip()

    # Step 3: Regex or substring replacements for partial matches
    #    For example, capturing "freshly squeezed lime" or "champagne" -> "sparkling wine".
    #    You can expand or adjust these patterns as needed.
    pattern_synonyms = [
        (r"(freshly\s*squeezed\s*)?lime(\s*juice)?", "lime juice"),
        (r"(freshly\s*squeezed\s*)?lemon(\s*juice)?", "lemon juice"),
        (r"chilled champagne", "sparkling wine"),
        (r"champagne", "sparkling wine"),
        (r"prosecco", "sparkling wine"),
        (r"(freshly\s*squeezed\s*)?pineapple(\s*juice)?", "pineapple juice"),
    ]
    for pattern, replacement in pattern_synonyms:
        text = re.sub(pattern, replacement, text)

    # Step 4: Final dictionary lookup for exact synonyms
    #    This dictionary is case-insensitive since we've already lowercase the input.
    synonyms = {
        # Fruits & vegetables / garnish
        "lemon twist": "lemon garnish",
        "fresh basil leaves": "basil leaves",
        "fresh lemon juice": "lemon",
        "lemon juice": "lemon",
        "fresh lime juice": "lime",
        "lime juice": "lime",

        # Alcoholic synonyms
        "tennessee whiskey": "bourbon",
        "scotch whisky": "blended scotch whisky",
        "old tom gin": "gin",
        "grenadine syrup": "grenadine",
        "passion fruit purֳ©e": "passion fruit puree",  # older accent form
        "passion fruit puree": "passion fruit puree",
        "St-Germain Elderflower Liqueur": "elderflower liqueur",
        "tonic Water": "tonic",
        "orange Curaçao": "orange liqueur",
        "light rum": "white rum",
        "malibu rum": "coconut rum",
        "triple sec": "orange liqueur",

        # Coffee/Tea
        "freshly brewed espresso": "espresso",
        "Half-and-Half Cream": "cooking cream",

        # Sugar & sweeteners
        "sugar cube": "white sugar",
        "sugar": "white sugar",
        "honey syrup": "honey",
        "sugar syrup": "simple syrup",

        # Others
        "club soda": "soda",
        "soda water": "soda",
        "ç": "c",
        "è": "e"
    }

    # Use the synonym dictionary if there's a direct match, otherwise return as is.
    return synonyms.get(text, text)


def canonicalize_regex(ingredient: str) -> str:
    """
    An alternative approach that uses purely regex with expansions for partial matches.
    """
    text = remove_diacritics(ingredient).lower().strip()

    pattern_synonyms = [
        (r"(freshly\s*squeezed\s*)?lime(\s*juice)?", "lime juice"),
        (r"(freshly\s*squeezed\s*)?lemon(\s*juice)?", "lemon juice"),
        (r"champagne", "sparkling wine"),
        # Add more patterns as needed
    ]

    for pattern, replacement in pattern_synonyms:
        text = re.sub(pattern, replacement, text)

    return text


def canonicalize_partial(ingredient: str) -> str:
    """
    A substring-based approach: if a substring is in the text, replace it.
    Useful for simpler partial matches without complex regex.
    """
    text = remove_diacritics(ingredient).lower()

    substring_synonyms = {
        "freshly squeezed lime": "lime juice",
        "fresh lime": "lime juice",
        "lime juice": "lime juice",  # final canonical form
        "freshly squeezed lemon": "lemon juice",
        "fresh lemon": "lemon juice",
        "lemon juice": "lemon juice",  # final canonical form
        "champagne": "sparkling wine",
        # etc.
    }

    for pattern, canonical_form in substring_synonyms.items():
        if pattern in text:
            text = text.replace(pattern, canonical_form)

    return text.strip()
