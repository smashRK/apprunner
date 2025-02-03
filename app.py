from flask import Flask, request, render_template, jsonify
from models import db, User
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def check_db_connection():
    """Check if database is accessible"""
    try:
        with app.app_context():
            db.session.execute('SELECT 1')
            return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False

def wait_for_db(max_retries=5, delay_seconds=5):
    """Wait for database to become available"""
    retries = 0
    while retries < max_retries:
        try:
            conn = psycopg2.connect(
                dbname='postgres',
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', 'postgres'),
                host=os.getenv('DB_HOST', 'localhost'),
                port=os.getenv('DB_PORT', '5432')
            )
            conn.close()
            return True
        except psycopg2.OperationalError as e:
            retries += 1
            logger.warning(f"Database connection attempt {retries} failed: {e}")
            if retries < max_retries:
                time.sleep(delay_seconds)
    return False

def create_database():
    """Create database if it doesn't exist"""
    db_params = {
        'dbname': 'postgres',
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'postgres'),
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432')
    }
    
    try:
        conn = psycopg2.connect(**db_params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", 
                      (os.getenv('DB_NAME', 'apprunner'),))
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute('CREATE DATABASE ' + os.getenv('DB_NAME', 'apprunner'))
            logger.info(f"Database '{os.getenv('DB_NAME', 'apprunner')}' created successfully!")
    except Exception as e:
        logger.error(f"Error in database creation: {e}")
        raise
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

# Wait for database to be available
if not wait_for_db():
    logger.error("Could not connect to database after maximum retries")
    # Don't raise error here, let the application start anyway
    # It will return errors for database operations but won't crash

try:
    # Create database if it doesn't exist
    create_database()
except Exception as e:
    logger.error(f"Failed to create database: {e}")
    # Continue running the application

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.getenv('DB_USER', 'postgres')}:{os.getenv('DB_PASSWORD', 'postgres')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME', 'apprunner')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

# Create tables
try:
    with app.app_context():
        db.create_all()
        logger.info("Database tables created successfully")
except Exception as e:
    logger.error(f"Error creating database tables: {e}")

@app.route('/health')
def health_check():
    """Health check endpoint"""
    health_status = {
        'status': 'healthy',
        'database': check_db_connection()
    }
    
    if not health_status['database']:
        health_status['status'] = 'degraded'
        return jsonify(health_status), 503
    
    return jsonify(health_status)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/greet', methods=['GET'])
def greet():
    name = request.args.get('name')
    if name:
        # Also save the name to database
        new_user = User(name=name)
        try:
            db.session.add(new_user)
            db.session.commit()
        except Exception as e:
            logger.error(f"Error saving name: {e}")
            db.session.rollback()
        return jsonify({"message": f"Hello, {name}!"})
    return jsonify({"message": "Please enter a name"}), 400

@app.route('/api/name', methods=['POST'])
def add_name():
    data = request.get_json()
    
    if not data or 'name' not in data:
        return jsonify({'error': 'Name is required'}), 400
    
    new_user = User(name=data['name'])
    
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify(new_user.to_dict()), 201
    except Exception as e:
        logger.error(f"Error adding name: {e}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/names', methods=['GET'])
def get_names():
    try:
        users = User.query.all()
        return jsonify([user.to_dict() for user in users])
    except Exception as e:
        logger.error(f"Error retrieving names: {e}")
        return jsonify({'error': 'Database error'}), 500

@app.route('/api/name/<int:user_id>', methods=['GET'])
def get_name(user_id):
    try:
        user = User.query.get_or_404(user_id)
        return jsonify(user.to_dict())
    except Exception as e:
        logger.error(f"Error retrieving name {user_id}: {e}")
        return jsonify({'error': 'Database error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)