from flask import Flask, jsonify,request,url_for,redirect
from business import read_travel_blogs, get_travel_blog_by_id ,add_travel_blog,delete_travel_blog

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to the Flask API!"

@app.route("/create-blog", methods=["POST"])
def create_blog():
    try:
        data = request.get_json(force=True)
        created = add_travel_blog(data)
        return jsonify(created), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/blog-list', methods=['GET'])
def blog_list():
    data=read_travel_blogs()
    
    return jsonify({"message": "Data received", "data": data})

@app.route('/blog-list/<string:blog_id>', methods=['GET'])
def api_blog(blog_id):
    try:
        blog = get_travel_blog_by_id(blog_id)  # expects Mongo _id string
        return jsonify({"message": "Blog found", "data": blog})
    except ValueError:
        return jsonify({"message": "Blog not found"}), 404
    except FileNotFoundError as e:
        return jsonify({"message": str(e)}), 500

@app.route("/blog-list/<string:blog_id>", methods=["POST"])
def delete_blog(blog_id):
    try:
        delete_travel_blog(blog_id)
        return redirect(url_for("blog_list"))  # redirect back to list page
    except Exception as e:
        return str(e), 400

if __name__ == '__main__':
    app.run(port=8000,host='0.0.0.0', debug=True)