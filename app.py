from flask import Flask, request, render_template, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/greet', methods=['GET'])
def greet():
    name = request.args.get('name')
    if name:
        return jsonify({"message": f"Hello, {name}!"})
    return jsonify({"message": "Please enter a name"}), 400

if __name__ == '__main__':
    # run app in port 8080
    app.run(host='0.0.0.0', port=8080)