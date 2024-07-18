from flask import Flask, request, jsonify
from services.populate_database import populate_database
from services.query_data import query_rag

app = Flask(__name__)

@app.route('/update_database', methods=['POST'])
def process():
    populate_database()
    return "Ok", 200

@app.route('/query', methods=['POST'])
def query():
    data = request.get_json()
    query_text = str(data.get('query'))
    if query_text:
        response = query_rag(query_text)
        return jsonify({response})
    else:
        return jsonify({"response": "Error: no query"}), 400



if __name__ == '__main__':
    app.run(debug=True)