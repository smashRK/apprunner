from flask import Flask, request, render_template, jsonify
from models import db, User
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import time
import logging
from sqlalchemy import text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DB_NAME = 'apprunner'
DB_USER = 'postgres'
DB_PASSWORD = '155MFOsWwh5F'
DB_HOST = 'demo-database-instance-1.cl84q2gowr55.ap-south-1.rds.amazonaws.com'
DB_PORT = '5432'
SSL_MODE = 'require'

# Common database parameters
DB_PARAMS = {
    'dbname': DB_NAME,
    'user': DB_USER,
    'password': DB_PASSWORD,
    'host': DB_HOST,
    'port': DB_PORT,
    'sslmode': SSL_MODE
}

# SQLAlchemy URI
DB_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode={SSL_MODE}"

app = Flask(__name__)

def check_db_connection():
    """Check if database is accessible"""
    try:
        # First check if we can connect directly with psycopg2
        conn = psycopg2.connect(**DB_PARAMS)
        conn.close()
        logger.info("Direct database connection successful")
        
        # Then check SQLAlchemy connection
        with app.app_context():
            # Use text() to create a SQL expression
            result = db.session.execute(text('SELECT 1'))
            result.scalar()  # Actually execute the query
            logger.info("SQLAlchemy database connection successful")
            return True
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return False

def wait_for_db(max_retries=5, delay_seconds=5):
    """Wait for database to become available"""
    retries = 0
    while retries < max_retries:
        try:
            # Use postgres database for initial connection
            params = DB_PARAMS.copy()
            params['dbname'] = 'postgres'
            conn = psycopg2.connect(**params)
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
    try:
        # Use postgres database to create new database
        params = DB_PARAMS.copy()
        params['dbname'] = 'postgres'
        conn = psycopg2.connect(**params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", 
                      (DB_NAME,))
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(f'CREATE DATABASE {DB_NAME}')
            logger.info(f"Database '{DB_NAME}' created successfully!")
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
logger.info(f"Connecting to database with URI: {DB_URI.replace(DB_PASSWORD, '****')}")
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
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
    try:
        db_connected = check_db_connection()
        health_status = {
            'status': 'healthy' if db_connected else 'degraded',
            'database': db_connected,
            'database_url': f"postgresql://{DB_USER}:****@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        }
        
        if not db_connected:
            return jsonify(health_status), 503
        
        return jsonify(health_status)
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'database': False
        }), 500

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/status')
def status():
    return jsonify({
        'status': 'ok'
    })

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