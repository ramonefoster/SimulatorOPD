from flask import Flask, request, jsonify
from flask_cors import CORS

FlaskApp = Flask(__name__)

CORS(FlaskApp, resources={r"/api/*": {"origins": "http://127.0.0.1:5500"}})

@FlaskApp.route('/api/telescope/position', methods=['GET'])
def get_telescope_position():
    global data
    return data

@FlaskApp.route('/api/telescope/position', methods=['POST'])
def set_telescope_position():
    global data
    data = request.get_json()
        
    return jsonify({'status': 200})
