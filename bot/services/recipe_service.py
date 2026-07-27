"""
Сервис рецептов для бота Эпплджек.
Хранит и выдает деревенские рецепты из SQLite.

Автор: MADAO81
Версия: 1.3 — поиск по корню слова
"""

import sqlite3
import random
import re
from typing import Optional, List, Dict
from bot.config import Config

class RecipeService:
    def __init__(self):
        self.db_path = Config.RECIPES_DB
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                ingredients TEXT NOT NULL,
                instructions TEXT NOT NULL,
                tip TEXT,
                source TEXT DEFAULT 'Эпплджек'
            )
        """)
        conn.commit()
        conn.close()

    def _get_root(self, word: str) -> str:
        """Возвращает корень слова (убирает окончания)."""
        word = word.lower().strip()
        endings = [
            'ый', 'ой', 'ое', 'ая', 'ые', 'ого', 'ому', 'ым', 'ом',
            'ая', 'яя', 'ие', 'ее', 'ий', 'ей', 'ям', 'ях',
            'ный', 'ная', 'ное', 'ные', 'ного', 'ному', 'ным', 'ном',
            'чный', 'чная', 'чное', 'чные', 'чного', 'чному', 'чным', 'чном',
            'ский', 'ская', 'ское', 'ские', 'ского', 'скому', 'ским', 'ском',
            'ной', 'ное', 'ные', 'ного', 'ному', 'ным', 'ном',
            'а', 'я', 'е', 'и', 'о', 'у', 'ю'
        ]
        for ending in endings:
            if word.endswith(ending):
                return word[:-len(ending)]
        return word

    def get_random_recipe(self) -> Optional[Dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM recipes ORDER BY RANDOM() LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def search_recipes(self, query: str) -> List[Dict]:
        """Ищет рецепты по названию или категории (по корням слов)."""
        query = query.lower().strip()
        query_roots = [self._get_root(w) for w in query.split()]
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM recipes")
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            recipe = dict(row)
            name = recipe['name'].lower()
            category = recipe['category'].lower()
            
            # Получаем корни для названия и категории
            name_roots = [self._get_root(w) for w in name.split()]
            category_roots = [self._get_root(w) for w in category.split()]
            
            score = 0
            for qr in query_roots:
                # Проверяем в названии
                for nr in name_roots:
                    if qr in nr or nr in qr:
                        score += 2
                        break
                # Проверяем в категории
                for cr in category_roots:
                    if qr in cr or cr in qr:
                        score += 1
                        break
            
            if score > 0:
                recipe['_score'] = score
                results.append(recipe)
        
        # Сортируем по убыванию релевантности
        results.sort(key=lambda x: x.get('_score', 0), reverse=True)
        return results

    def get_recipe_by_name(self, name: str) -> Optional[Dict]:
        results = self.search_recipes(name)
        return results[0] if results else None

    def get_recipes_by_category(self, category: str) -> List[Dict]:
        results = self.search_recipes(category)
        return results

    def get_categories(self) -> List[str]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT category FROM recipes ORDER BY category")
        rows = cursor.fetchall()
        conn.close()
        return [row[0] for row in rows]

    def format_recipe(self, recipe: Dict) -> str:
        text = (
            f"🥧 *{recipe['name']}*\n\n"
            f"📌 *Категория:* {recipe['category']}\n\n"
            f"🧺 *Ингредиенты:*\n{recipe['ingredients']}\n\n"
            f"📝 *Приготовление:*\n{recipe['instructions']}\n"
        )
        if recipe.get('tip'):
            text += f"\n💡 *Совет от Эпплджек:* {recipe['tip']}"
        return text
