from flask import Flask, jsonify, make_response


app = Flask(__name__)


@app.route('/api/similar_documents/<int:article_id>', methods=['GET'])
def get_similar_documents(article_id):
    return jsonify({"id": article_id})


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == "__main__":
    app.run(debug=True, host="localhost", port=3000)
