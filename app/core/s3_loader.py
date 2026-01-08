import json

def load_categories():
    with open("app/data/categories.json", "r") as f:
        return json.load(f)
    