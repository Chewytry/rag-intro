from flask import Flask, request, jsonify, Response
from services.database_functions import populate_database, clear_database, show_data_files, show_database_contents, add_file_to_data, remove_file_from_data, populate_database_alt
from services.query_data import query_rag

app = Flask(__name__)

@app.route('/update_database', methods=['POST'])
def process():
    populate_database()
    return "Database updated", 200

@app.route('/update_database2', methods=['POST'])
def process_alt():
    populate_database_alt()
    return "Database updated, multimodal", 200

@app.route('/clear_database', methods=['POST'])
def clear_db():
    clear_database()
    return "Database cleared.", 200

@app.route('/show_data_files', methods=['GET'])
def show_files():
    files = show_data_files()
    return jsonify(files), 200

@app.route('/show_database_contents', methods=['GET'])
def show_db_contents():
    documents = show_database_contents()
    return jsonify(documents), 200

@app.route('/add_file', methods=['POST'])
def add_file():
    file_path = request.json.get('file_path')
    if file_path:
        result = add_file_to_data(file_path)
        return result, 200
    else:
        return "No file path provided.", 400

@app.route('/remove_file', methods=['POST'])
def remove_file():
    file_name = request.json.get('file_name')
    if file_name:
        result = remove_file_from_data(file_name)
        return result, 200
    else:
        return "No file name provided.", 400

@app.route('/query', methods=['POST'])
def query():
    data = request.get_json()
    query_text = str(data.get('query'))
    if query_text:
        return Response((query_rag(query_text)), mimetype='text/event-stream')
    else:
        return jsonify({"response": "Error: no query"}), 400


if __name__ == '__main__':
    app.run(debug=True)