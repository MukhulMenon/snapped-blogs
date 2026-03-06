from flask import Flask, jsonify,request,url_for,redirect,current_app
from werkzeug.utils import secure_filename
import gridfs
from bson import ObjectId

from connections import db
from business import read_travel_blogs, get_travel_blog_by_id ,add_travel_blog,delete_travel_blog

app = Flask(__name__)
fs = gridfs.GridFS(db)

ALLOWED = {"png","jpg","jpeg","gif","webp"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED

@app.route('/')
def home():
    return "Welcome to the Flask API!"

@app.route("/create-blog", methods=["POST"])
def create_blog_api():
    try:
        data = request.get_json(force=True)
        created = add_travel_blog(data)
        return jsonify(created), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@app.route("/create-blog/submit", methods=["POST"])
def create_blog_submit():
    try:
        name = request.form.get("name", "").strip()
        summary = request.form.get("summary", "").strip()
        description = request.form.get("description", "").strip()
        date = request.form.get("date", "").strip()

        image = request.files.get("image")
        if not all([name, summary, description, date]):
            return jsonify({"error": "Missing required text fields"}), 400
        if not image or image.filename == "":
            return jsonify({"error": "Image is required"}), 400
        if not allowed_file(image.filename):
            return jsonify({"error": "Invalid image type"}), 400

        filename = secure_filename(image.filename)
        # store in GridFS; image.stream is a file-like object
        file_id = fs.put(image.stream, filename=filename, content_type=image.mimetype)

        created = add_travel_blog({
            "name": name,
            "summary": summary,
            "description": description,
            "date": date,
            "image_file_id": str(file_id),
        })

        # Return JSON with created doc (frontend expects JSON)
        return jsonify(created), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/blog-list', methods=['GET'])
def blog_list():
    # business.read_travel_blogs() now returns list
    data = read_travel_blogs()
    # wrap for compatibility
    return jsonify({"message": "Data received", "data": data})

@app.route('/blog-list/<string:blog_id>', methods=['GET'])
def api_blog(blog_id):
    try:
        blog = get_travel_blog_by_id(blog_id)
        return jsonify({"message": "Blog found", "data": blog})
    except ValueError:
        return jsonify({"message": "Blog not found"}), 404
    except FileNotFoundError as e:
        return jsonify({"message": str(e)}), 500

@app.route("/blog-list/<string:blog_id>", methods=["POST"])
def delete_blog(blog_id):
    try:
        delete_travel_blog(blog_id)
        return redirect(url_for("blog_list"))
    except Exception as e:
        return str(e), 400

@app.route("/image/<file_id>", methods=["GET"])
def get_image(file_id):
    try:
        grid_out = fs.get(ObjectId(file_id))
        # Flask response class with the correct mimetype
        return current_app.response_class(grid_out.read(), mimetype=grid_out.content_type)
    except Exception:
        return jsonify({"error": "Image not found"}), 404

if __name__ == '__main__':
    app.run(port=8000,host='0.0.0.0', debug=True)