from flask import current_app as app

class Category:
    def __init__(self, name, description):
        self.name = name
        self.description = description

    @staticmethod
    def get_category(category):
        rows = app.db.execute('''
SELECT *
FROM Categories
WHERE name=:category
''',
                              category=category)
        return Category(*(rows[0])) if rows is not None else None
    
    @staticmethod
    def get_categories():
        rows = app.db.execute('''
SELECT *
FROM Categories
''')
        return [Category(*row) for row in rows]

    @staticmethod
    def get_category_names():
        rows = app.db.execute('''
SELECT name
FROM Categories
''')
        return [row[0] for row in rows]