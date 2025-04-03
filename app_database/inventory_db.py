# inventory_db.py
import sqlite3
import json
from utilities import canonicalize


class InventoryDB:
    def __init__(self, db_path='app_database/inventory.db'):
        self.db_path = db_path
        self.connection = sqlite3.connect(self.db_path)
        self.create_table()
        self.cache = {}  # In-memory cache of ingredients.

    def create_table(self):
        """Creates the inventory table with the new schema."""
        cursor = self.connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bottle_name TEXT NOT NULL,
                type TEXT NOT NULL,
                category TEXT,
                unit TEXT NOT NULL,
                quantity REAL NOT NULL,
                abv REAL,
                is_open INTEGER DEFAULT 1,
                curr_amount REAL
            )
        ''')
        self.connection.commit()

    def load_cache(self):
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT bottle_name, type, quantity, unit, category, abv, is_open, curr_amount 
            FROM inventory
        ''')
        rows = cursor.fetchall()
        self.cache = {
            canonicalize(row[0]): {
                'type': row[1],
                'quantity': row[2],
                'unit': row[3],
                'category': row[4],
                'abv': row[5],
                'is_open': row[6],
                'curr_amount': row[7]
            }
            for row in rows
        }
        return self.cache

    def add_ingredient(self, bottle_name, type, category, abv, unit, quantity, is_open, curr_amount):
        """
        Inserts an ingredient into the database and updates the cache.
        The bottle_name is stored in its canonical form.
        """
        canonical_name = canonicalize(bottle_name)
        cursor = self.connection.cursor()
        cursor.execute('''
            INSERT INTO inventory (bottle_name, type, category, abv, unit, quantity, is_open, curr_amount)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (canonical_name, type, category, abv, unit, quantity, is_open, curr_amount))
        self.connection.commit()

        self.cache[canonical_name] = {
            'type': type,
            'quantity': quantity,
            'unit': unit,
            'category': category,
            'abv': abv,
            'is_open': is_open,
            'curr_amount': curr_amount,

        }
        # print(f"Inserted: {canonical_name}")

    # def update_ingredient(self, bottle_name, quantity, curr_amount):
    #     """
    #     Updates the quantity and current amount of an ingredient (using its canonical bottle_name)
    #     in both the database and the in-memory cache.
    #     """
    #     canonical_name = canonicalize(bottle_name)
    #     cursor = self.connection.cursor()
    #     cursor.execute('''
    #         UPDATE inventory
    #         SET quantity = ?, curr_amount = ?
    #         WHERE bottle_name = ?
    #     ''', (quantity, curr_amount, canonical_name))
    #     self.connection.commit()
    #     if canonical_name in self.cache:
    #         self.cache[canonical_name]['quantity'] = quantity
    #         self.cache[canonical_name]['curr_amount'] = curr_amount
    #         print(f"Updated: {canonical_name}")

    # !!!!!!!!!!!!!!!! old import, still works but without update

    # def import_from_json(self, json_file):
    #     """
    #     Imports ingredients from a JSON file into the inventory database.
    #     Each JSON object should include keys: bottle_name, type, category, abv, unit, quantity, is_open.
    #     If curr_amount is not provided, it defaults to the quantity.
    #     """
    #     with open(json_file, 'r', encoding='utf-8') as file:
    #         ingredients = json.load(file)
    #     for item in ingredients:
    #         self.add_ingredient(
    #             bottle_name=item["bottle_name"],
    #             type=item["type"],
    #             category=item["category"],
    #             abv=item["abv"],
    #             unit=item["unit"],
    #             quantity=item["quantity"],
    #             is_open=item["is_open"],
    #             curr_amount=item.get("curr_amount", item["quantity"])
    #         )

    def import_from_json(self, json_file):
        """
        Imports ingredients from a JSON file into the inventory database.
        For each JSON object, if an entry with the same bottle_name (raw) exists,
        it updates the record; otherwise, it inserts a new record.
        """
        with open(json_file, 'r', encoding='utf-8') as file:
            ingredients = json.load(file)

        cursor = self.connection.cursor()
        for item in ingredients:
            bottle_name = item["bottle_name"]
            curr_amount = item.get("curr_amount", item["quantity"])

            # Check if an ingredient with the same bottle_name exists
            cursor.execute("SELECT id FROM inventory WHERE bottle_name = ?", (bottle_name,))
            existing = cursor.fetchone()

            if existing:
                # Update the existing record
                cursor.execute('''
                    UPDATE inventory
                    SET type = ?, category = ?, abv = ?, unit = ?, quantity = ?, is_open = ?, curr_amount = ?
                    WHERE bottle_name = ?
                ''', (item["type"], item["category"], item["abv"], item["unit"],
                      item["quantity"], item["is_open"], curr_amount, bottle_name))
                self.connection.commit()
                print(f"Updated: {bottle_name}")
                # Update the in-memory cache as well
                self.cache[bottle_name] = {
                    'type': item["type"],
                    'quantity': item["quantity"],
                    'unit': item["unit"],
                    'category': item["category"],
                    'abv': item["abv"],
                    'is_open': item["is_open"],
                    'curr_amount': curr_amount
                }
            else:
                # Insert a new record
                self.add_ingredient(
                    bottle_name=item["bottle_name"],
                    type=item["type"],
                    category=item["category"],
                    abv=item["abv"],
                    unit=item["unit"],
                    quantity=item["quantity"],
                    is_open=item["is_open"],
                    curr_amount=curr_amount
                )

    def count_ingredients(self):
        """
        Returns the total number of ingredients in the inventory.
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT COUNT(DISTINCT bottle_name) FROM inventory")
        result = cursor.fetchone()
        return result[0] if result else 0

    def close(self):
        self.connection.close()
