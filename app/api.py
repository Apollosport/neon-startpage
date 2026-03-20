from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import json
import os

app = FastAPI()

# --- FILE PATHS ---
CONFIG_PATH = '/data/config.json'

# --- MODELS ---
class DeleteBookmarkAction(BaseModel):
    category: str
    name: str

class ReorderBookmarksAction(BaseModel):
    bookmarks: List[Dict]

class AddBookmarkAction(BaseModel):
    category: str
    name: str
    url: str
    icon: str = "🌐"

# ==========================================
# BOOKMARK ENDPOINTS
# ==========================================

@app.post("/api/bookmarks/delete")
def delete_bookmark(action: DeleteBookmarkAction):
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)

        for cat in config.get('bookmarks', []):
            if cat['category'] == action.category:
                cat['links'] = [link for link in cat['links'] if link['name'] != action.name]

        # Filter out any categories that have 0 links
        config['bookmarks'] = [cat for cat in config.get('bookmarks', []) if len(cat.get('links', [])) > 0]

        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)

        return {"status": "success", "message": f"Deleted {action.name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/bookmarks/reorder")
def reorder_bookmarks(action: ReorderBookmarksAction):
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)

        config['bookmarks'] = action.bookmarks

        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)

        return {"status": "success", "message": "Layout saved!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/bookmarks/add")
def add_bookmark(action: AddBookmarkAction):
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)

        category_found = False
        for cat in config.get('bookmarks', []):
            if cat['category'].strip().lower() == action.category.strip().lower():
                cat['links'].append({
                    "name": action.name,
                    "url": action.url,
                    "icon": action.icon
                })
                category_found = True
                break

        if not category_found:
            config.setdefault('bookmarks', []).append({
                "category": action.category,
                "links": [{
                    "name": action.name,
                    "url": action.url,
                    "icon": action.icon
                }]
            })

        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)

        return {"status": "success", "message": f"Added {action.name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))