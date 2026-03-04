import json
import os

def read_travel_blogs():

    DATA_FILE = 'travel-blogs.txt'

    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError("Data file not found")

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        content = file.read().strip()

    # Assuming the file contains a JSON array
    data = json.loads(content)

    if not isinstance(data, list):
        raise ValueError("Invalid format: expected a list of blog objects")

    return data

def get_travel_blog_by_id(blog_id):
    DATA_FILE = 'travel-blogs.txt'

    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError("Data file not found")

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        content = file.read().strip()

    data = json.loads(content)

    if not isinstance(data, list):
        raise ValueError("Invalid format: expected a list of blog objects")

    # Find blog by ID
    for blog in data:
        if blog.get("id") == blog_id:
            return blog

    raise ValueError(f"Blog with id {blog_id} not found")

def add_travel_blog(new_blog):
    DATA_FILE = 'travel-blogs.txt'

    if not isinstance(new_blog, dict):
        raise ValueError("New blog entry must be a dictionary")

    # required fields based on your HTML form
    required = ["name", "summary", "description", "date", "image_url"]
    missing = [k for k in required if not new_blog.get(k)]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")

    # load existing list (or init)
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            data = json.loads(content) if content else []
    else:
        data = []

    if not isinstance(data, list):
        raise ValueError("Invalid format: expected a list of blog objects")

    # auto-generate next id
    max_id = 0
    for b in data:
        try:
            max_id = max(max_id, int(b.get("id", 0)))
        except (TypeError, ValueError):
            pass

    new_entry = {
        "id": max_id + 1,
        "name": new_blog["name"],
        "summary": new_blog["summary"],
        "description": new_blog["description"],
        "date": new_blog["date"],
        "image_url": new_blog["image_url"],
    }

    data.append(new_entry)

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return new_entry

def delete_travel_blog(blog_id):
    DATA_FILE = "travel-blogs.txt"

    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError("Data file not found")

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        content = f.read().strip()
        data = json.loads(content) if content else []

    if not isinstance(data, list):
        raise ValueError("Invalid format: expected a list of blog objects")

    original_len = len(data)
    data = [b for b in data if str(b.get("id")) != str(blog_id)]

    if len(data) == original_len:
        raise ValueError(f"Blog with id {blog_id} not found")

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return {"deleted_id": blog_id}