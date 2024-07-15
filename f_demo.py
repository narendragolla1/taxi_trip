import sqlite3
from flask import Flask, jsonify, request, abort

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

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': str(error.description)}), 404


# ENDPOINTS
@app.route('/yellow_trips', methods=['GET', 'POST'])
@app.route('/yellow_trips/<int:VendorID>', methods=['GET', 'PUT', 'DELETE'])
def handle_yellow_trips(VendorID=None):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'GET':
        if VendorID:  # Fetch a specific trip
            cursor.execute('SELECT * FROM feb_yellow_tripdata WHERE VendorID = ? LIMIT 10', (VendorID,))
            trip = cursor.fetchone()
            if trip is None:
                abort(404, description="Yellow trip not found")
            return jsonify(dict(trip))
        else:  # Fetch all trips
            cursor.execute('SELECT * FROM feb_yellow_tripdata LIMIT 10 ')
            trips = cursor.fetchall()
            return jsonify([dict(trip) for trip in trips])

    elif request.method == 'POST':
        data = request.get_json()
        required_fields = ["VendorID", "tpep_pickup_datetime", "total_amount"]
        for field in required_fields:
            if field not in data:
                abort(400, description=f"Missing field: {field}")
        cursor.execute(
            'INSERT INTO feb_yellow_tripdata (VendorID, tpep_pickup_datetime, total_amount) VALUES (?, ?, ?)',
            (data['VendorID'], data['tpep_pickup_datetime'], data['total_amount'])
        )
        conn.commit()
        return jsonify({'message': 'Yellow trip added successfully'}), 201

    elif request.method == 'PUT':
        if not VendorID:
            abort(400, description="Trip ID is required for update")

        data = request.get_json()
        update_fields = []
        update_values = []
        for key, value in data.items():
            update_fields.append(f"{key} = ?")
            update_values.append(value)
        update_values.append(VendorID)

        query = f"UPDATE feb_yellow_tripdata SET {', '.join(update_fields)} WHERE VendorID = ?"
        cursor.execute(query, update_values)
        conn.commit()

        if cursor.rowcount == 0:
            abort(404, description="Yellow trip not found")

        return jsonify({'message': 'Yellow trip updated successfully'}), 200

    elif request.method == 'DELETE':
        if not VendorID:
            abort(400, description="Trip ID is required for deletion")

        cursor.execute('DELETE FROM feb_yellow_tripdata WHERE VendorID = ?', (VendorID,))
        conn.commit()

        if cursor.rowcount == 0:
            abort(404, description="Yellow trip not found")

        return jsonify({'message': 'Yellow trip deleted successfully'}), 200

    conn.close()


if __name__ == '__main__':
    app.run(debug=True,port=5001)
