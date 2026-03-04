from flask import Flask, jsonify,request
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
def api():
    data=read_travel_blogs()
    
    return jsonify({"message": "Data received", "data": data})

@app.route('/blog-list/<int:id>', methods=['GET'])
def api_blog(id):
    blog = get_travel_blog_by_id(id)
    if blog:
        return jsonify({"message": "Blog found", "data": blog})
    else:
        return jsonify({"message": "Blog not found"}), 404

@app.route("/blog-list/<int:blog_id>", methods=["DELETE"])
def delete_blog(blog_id):
    try:
        result = delete_travel_blog(blog_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(port=8000,host='0.0.0.0', debug=True)