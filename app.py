from flask import Flask, request, render_template, jsonify
from models import db, User
import os

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/apprunner')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()

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
        except Exception:
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
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/names', methods=['GET'])
def get_names():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@app.route('/api/name/<int:user_id>', methods=['GET'])
def get_name(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)