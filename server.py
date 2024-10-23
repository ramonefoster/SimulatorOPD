from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

import logging

log = logging.getLogger('werkzeug')
log.disabled = True

DisplayFlask = Flask(__name__, template_folder='templates')
CORS(DisplayFlask, resources={r"/api/*": {"origins": ["http://127.0.0.1:5500", "*", "https://irsa.ipac.caltech.edu"]}})

@DisplayFlask.route('/')
def home():
    return render_template('160.html')

@DisplayFlask.route('/iag')
def iag():
    return render_template('iag.html')

@DisplayFlask.route('/asa80')
def asa80():
    return render_template('asa80.html')

@DisplayFlask.route('/robo40')
def robo40():
    return render_template('robo40.html')

@DisplayFlask.route('/zeiss')
def zeiss():
    return render_template('zeiss.html')

@DisplayFlask.route('/aladin')
def set_aladin():
    return render_template('aladin.html')

@DisplayFlask.route('/aladin/set_target', methods=['POST'])
def set_target():
    global data
    data = request.get_json()
    print(data)
    # target = data.get('target', 'M 31')  # Default target is M31
    # fov = data.get('fov', 0.5)  # Default fov is 0.5 degrees
    return jsonify({'status': 200})

@DisplayFlask.route('/aladin/get_target', methods=['GET'])
def get_target():
    global data
    return data
    # print(data)
    # target = data.get('target', 'M 31')  # Default target is M31
    # fov = data.get('fov', 0.5)  # Default fov is 0.5 degrees
    # return jsonify({'message': 'Success', 'target': target, 'fov': fov})

# if __name__ == '__main__':
#     DisplayFlask.run(port=5500)