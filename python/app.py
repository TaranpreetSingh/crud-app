from flask import Flask, request, jsonify, render_template
import mysql.connector
from mysql.connector import Error
import os
from prometheus_client import Counter, Histogram, Info, generate_latest, REGISTRY, start_http_server
import time

app = Flask(__name__)

# Prometheus metrics
request_counter = Counter('app_request_count', 'Application Request Count', ['method', 'endpoint', 'status'])
request_latency = Histogram('app_request_latency_seconds', 'Application Request Latency', ['method', 'endpoint'])
db_info = Info('app_database_info', 'Database Information')
db_info.info({'host': os.environ.get('DB_HOST', 'localhost')})

# Database connection function
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.environ.get('DB_HOST', 'localhost'),
            user=os.environ.get('DB_USER', 'root'),
            password=os.environ.get('DB_PASSWORD', 'password'),
            database=os.environ.get('DB_NAME', 'crud_app')
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# Create users table if not exists
def initialize_db():
    try:
        connection = get_db_connection()
        if connection and connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            connection.commit()
            cursor.close()
            connection.close()
            print("Database initialized successfully")
    except Error as e:
        print(f"Error initializing database: {e}")

# Initialize the database on startup
initialize_db()

# UI routes
@app.route('/')
def index():
    return render_template('index.html')

# Prometheus metrics endpoint
@app.route('/metrics')
def metrics():
    return generate_latest(REGISTRY)

# CRUD operations with metrics
@app.route('/users', methods=['POST'])
def create_user():
    start_time = time.time()
    try:
        data = request.get_json()
        connection = get_db_connection()
        if connection and connection.is_connected():
            cursor = connection.cursor()
            query = "INSERT INTO users (name, email) VALUES (%s, %s)"
            cursor.execute(query, (data['name'], data['email']))
            connection.commit()
            cursor.close()
            connection.close()
            response = jsonify({'message': 'User created successfully'}), 201
            request_counter.labels('POST', '/users', '201').inc()
        else:
            response = jsonify({'error': 'Database connection failed'}), 500
            request_counter.labels('POST', '/users', '500').inc()
    except Exception as e:
        response = jsonify({'error': str(e)}), 400
        request_counter.labels('POST', '/users', '400').inc()
    
    request_latency.labels('POST', '/users').observe(time.time() - start_time)
    return response

@app.route('/users', methods=['GET'])
def get_all_users():
    start_time = time.time()
    try:
        connection = get_db_connection()
        if connection and connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()
            cursor.close()
            connection.close()
            response = jsonify(users), 200
            request_counter.labels('GET', '/users', '200').inc()
        else:
            response = jsonify({'error': 'Database connection failed'}), 500
            request_counter.labels('GET', '/users', '500').inc()
    except Exception as e:
        response = jsonify({'error': str(e)}), 400
        request_counter.labels('GET', '/users', '400').inc()
    
    request_latency.labels('GET', '/users').observe(time.time() - start_time)
    return response

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    start_time = time.time()
    try:
        connection = get_db_connection()
        if connection and connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            cursor.close()
            connection.close()
            
            if user:
                response = jsonify(user), 200
                request_counter.labels('GET', '/users/<id>', '200').inc()
            else:
                response = jsonify({'error': 'User not found'}), 404
                request_counter.labels('GET', '/users/<id>', '404').inc()
        else:
            response = jsonify({'error': 'Database connection failed'}), 500
            request_counter.labels('GET', '/users/<id>', '500').inc()
    except Exception as e:
        response = jsonify({'error': str(e)}), 400
        request_counter.labels('GET', '/users/<id>', '400').inc()
    
    request_latency.labels('GET', '/users/<id>').observe(time.time() - start_time)
    return response

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    start_time = time.time()
    try:
        data = request.get_json()
        connection = get_db_connection()
        if connection and connection.is_connected():
            cursor = connection.cursor()
            query = "UPDATE users SET name = %s, email = %s WHERE id = %s"
            cursor.execute(query, (data['name'], data['email'], user_id))
            connection.commit()
            
            if cursor.rowcount > 0:
                response = jsonify({'message': 'User updated successfully'}), 200
                request_counter.labels('PUT', '/users/<id>', '200').inc()
            else:
                response = jsonify({'error': 'User not found'}), 404
                request_counter.labels('PUT', '/users/<id>', '404').inc()
            
            cursor.close()
            connection.close()
        else:
            response = jsonify({'error': 'Database connection failed'}), 500
            request_counter.labels('PUT', '/users/<id>', '500').inc()
    except Exception as e:
        response = jsonify({'error': str(e)}), 400
        request_counter.labels('PUT', '/users/<id>', '400').inc()
    
    request_latency.labels('PUT', '/users/<id>').observe(time.time() - start_time)
    return response

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    start_time = time.time()
    try:
        connection = get_db_connection()
        if connection and connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            connection.commit()
            
            if cursor.rowcount > 0:
                response = jsonify({'message': 'User deleted successfully'}), 200
                request_counter.labels('DELETE', '/users/<id>', '200').inc()
            else:
                response = jsonify({'error': 'User not found'}), 404
                request_counter.labels('DELETE', '/users/<id>', '404').inc()
            
            cursor.close()
            connection.close()
        else:
            response = jsonify({'error': 'Database connection failed'}), 500
            request_counter.labels('DELETE', '/users/<id>', '500').inc()
    except Exception as e:
        response = jsonify({'error': str(e)}), 400
        request_counter.labels('DELETE', '/users/<id>', '400').inc()
    
    request_latency.labels('DELETE', '/users/<id>').observe(time.time() - start_time)
    return response

if __name__ == '__main__':
    # Start Prometheus metrics server on port 8000
    start_http_server(8000)
    print("Prometheus metrics server started on port 8000")
    
    # Start Flask app on port 5000
    app.run(host='0.0.0.0', port=8080)