from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

app = Flask(__name__, template_folder='templates')
CORS(app, resources={r"/api/*": {"origins": ["http://127.0.0.1:5500", "*", "https://irsa.ipac.caltech.edu"]}})

@app.route('/')
def home():
    return render_template('160.html')

@app.route('/iag')
def iag():
    return render_template('iag.html')

@app.route('/aladin')
def set_aladin():
    return render_template('aladin.html')

@app.route('/set_target', methods=['POST'])
def set_target():
    global data
    data = request.get_json()
    # target = data.get('target', 'M 31')  # Default target is M31
    # fov = data.get('fov', 0.5)  # Default fov is 0.5 degrees
    return jsonify({'status': 200})

@app.route('/aladin/get_target', methods=['GET'])
def get_target():
    global data
    return data
    # print(data)
    # target = data.get('target', 'M 31')  # Default target is M31
    # fov = data.get('fov', 0.5)  # Default fov is 0.5 degrees
    # return jsonify({'message': 'Success', 'target': target, 'fov': fov})

if __name__ == '__main__':
    app.run(port=5500)