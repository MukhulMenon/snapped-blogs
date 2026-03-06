from connections import collection,db
from bson import ObjectId
import gridfs
import logging

logger = logging.getLogger(__name__)

fs = gridfs.GridFS(db)  # default bucket name "fs"

def read_travel_blogs():

    if collection is None:
        raise FileNotFoundError("Mongo DB collection not found")

    data = list(collection.find())

    # Convert ObjectId to string for every document
    for doc in data:
        if "_id" in doc and isinstance(doc["_id"], ObjectId):
            doc["_id"] = str(doc["_id"])

        if "image_file_id" in doc:
            doc["image_url"] = f"/image/{doc['image_file_id']}"

    return data

def get_travel_blog_by_id(blog_id):
    if collection is None:
        raise FileNotFoundError("Mongo DB collection not found")

    if not ObjectId.is_valid(blog_id):
        raise ValueError("Invalid blog ID format")

    doc = collection.find_one({"_id": ObjectId(blog_id)})
    if not doc:
        raise ValueError("Blog not found")

    doc["_id"] = str(doc["_id"])
    if "image_file_id" in doc:
        doc["image_url"] = f"/image/{doc['image_file_id']}"
    return doc

def add_travel_blog(new_blog):
    # ensure mongo collection exists (same pattern as read_travel_blogs)
    if collection is None:
        raise FileNotFoundError("Mogo DB collection not found")

    if not isinstance(new_blog, dict):
        raise ValueError("New blog entry must be a dictionary")

    # required fields based on your HTML form
    required = ["name", "summary", "description", "date", "image_file_id"]
    missing = [k for k in required if not new_blog.get(k)]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")

    # document to insert
    doc = {
        "name": new_blog["name"],
        "summary": new_blog["summary"],
        "description": new_blog["description"],
        "date": new_blog["date"],
        "image_file_id": new_blog["image_file_id"],
    }

    # insert into mongo
    result = collection.insert_one(doc)

    # return inserted doc (make _id JSON serializable)
    inserted = collection.find_one({"_id": result.inserted_id})
    if inserted and isinstance(inserted.get("_id"), ObjectId):
        inserted["_id"] = str(inserted["_id"])
    if inserted and "image_file_id" in inserted:
        inserted["image_url"] = f"/image/{inserted['image_file_id']}"
    return inserted

def delete_travel_blog(blog_id):
    if collection is None:
        raise FileNotFoundError("Mongo DB collection not found")

    if not ObjectId.is_valid(blog_id):
        raise ValueError("Invalid blog ID format")

    doc = collection.find_one({"_id": ObjectId(blog_id)})
    if not doc:
        raise ValueError("Blog not found")

    # delete GridFS file if present
    image_file_id = doc.get("image_file_id")
    if image_file_id and ObjectId.is_valid(image_file_id):
        try:
            fs.delete(ObjectId(image_file_id))
        except Exception as e:
            logger.exception("Failed deleting gridfs file: %s", e)

    result = collection.delete_one({"_id": ObjectId(blog_id)})
    if result.deleted_count == 0:
        raise ValueError("Blog not found")
    return True