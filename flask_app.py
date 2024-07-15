import sqlite3
from flask import Flask, jsonify, request, abort, render_template_string

app = Flask(__name__)

# Database Helper Functions
def get_db_connection():
    conn = sqlite3.connect('tripdata.db')
    conn.row_factory = sqlite3.Row
    return conn

# Error Handling
@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': str(error.description)}), 400

@app.route('/')
def index():
   return render_template_string("<h1>Welcome to Taxi Trip Website</h1>")

@app.route('/api/tables', methods=['GET'])
def get_table_list():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Query to fetch table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]

    conn.close()
    return jsonify(tables)

# API Endpoint to Get Data by Table Name
@app.route('/api/data/<table_name>', methods=['GET'])
def get_table_data(table_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    print(table_name)

    try:
        # Fetch limited rows to avoid large responses
        cursor.execute(f'SELECT * FROM {table_name}')  
        rows = cursor.fetchall()
    except sqlite3.Error as e:
        abort(500, description=f"Error querying database: {e}")
    finally:
        conn.close()

    return jsonify([dict(row) for row in rows])

# POST
@app.route('/data/<table_name>', methods=['POST'])
def insert_data(table_name):
  print('---------------- Im called -------------')
  # Get data from the request body
  data = request.get_json()
  conn = get_db_connection()
  cursor = conn.cursor()
  # Extract relevant data from the request (modify as needed)
  column_names = ','.join(data.keys())
  placeholders = ','.join(['?' for _ in data.values()])

  # Construct the INSERT INTO statement
  insert_query = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"

  try:
    # Execute the query with data
    
    cursor.execute(insert_query, data.values())
    cursor.commit()
    print('--------my work done')
    return jsonify({'message': 'Data inserted successfully'}), 201  # Created status code
  except Exception as e:
    # Handle errors (e.g., database errors, validation errors)
    return jsonify({'message': f'Error inserting data: {str(e)}'}), 400  # Bad Request status code



# All tables dont have id's
@app.route('/data/<table_name>/<int:id>', methods=['PUT'])
def update_data(table_name,id):
  # Get data from the request body
  data = request.get_json()
  conn = get_db_connection()
  cursor = conn.cursor()
  # Extract relevant data and update statement parts (modify as needed)
  update_data = []
  for key, value in data.items():
    update_data.append(f"{key} = ?")

  update_clause = ','.join(update_data)
  update_query = f"UPDATE {table_name} SET {update_clause} WHERE id = {id}"

  try:
    # Execute the update query with data
    cursor.execute(update_query, [*data.values(), id])
    cursor.commit()
    return jsonify({'message': 'Data updated successfully'}), 200  # OK status code
  except Exception as e:
    # Handle errors (e.g., database errors, validation errors)
    return jsonify({'message': f'Error updating data: {str(e)}'}), 400  # Bad Request status code


@app.route('/data/<table_name>/<int:id>', methods=['DELETE'])
def delete_data(table_name,id):
  # Construct the DELETE query with the ID
  delete_query = f"DELETE FROM feb_yellow_tripdata WHERE id = {id}"
  conn = get_db_connection()
  cursor = conn.cursor()
  try:
    # Execute the delete query
    cursor.execute(delete_query)
    cursor.commit()
    return jsonify({'message': 'Data deleted successfully'}), 204  # No Content status code
  except Exception as e:
    # Handle errors (e.g., database errors)
    return jsonify({'message': f'Error deleting data: {str(e)}'}), 400  # Bad Request status code


if __name__ == '__main__':
    app.run(debug=True,port=5010)
