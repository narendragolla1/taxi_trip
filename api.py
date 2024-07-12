from flask import Flask, jsonify, request
import sqlite3
import base64  # For encoding bytes data




app = Flask(__name__)

# Database Connection (Single Connection)
def get_db_connection():
    conn = sqlite3.connect('tripdata.db')
    conn.row_factory = sqlite3.Row
    return conn

# Helper Function to Query the Database (with Error Handling)
def query_db(query, args=(), one=False):
    conn = get_db_connection()
    cursor = conn.execute(query, args)
    rv = [dict(row) for row in cursor.fetchall()]  # Convert rows to dictionaries
    cursor.close()
    conn.close()
    return (rv[0] if rv else None) if one else rv

# API Routes

@app.route('/<table>', methods=['GET'])
def get_items(table):
    items = query_db(f'SELECT * FROM {table} limit 10')
    for item in items:
        for key, value in item.items():
            if isinstance(value, bytes):
                item[key] = base64.b64encode(value).decode('utf-8')
    return jsonify(items) 


@app.route('/<table>', methods=['POST'])
def create_item(table):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON data'}), 400

    columns = ', '.join(data.keys())
    placeholders = ', '.join(['?'] * len(data))
    values = list(data.values())

    query_db(f'INSERT INTO {table} ({columns}) VALUES ({placeholders})', values)
    return jsonify({'message': 'Item created successfully'}), 201

# @app.route('/<table>/<int:item_id>', methods=['PUT'])
# def update_item(table, item_id):
  

# @app.route('/<table>/<int:item_id>', methods=['DELETE'])
# def delete_item(table, item_id):
  


if __name__ == '__main__':
    app.run(debug=True)