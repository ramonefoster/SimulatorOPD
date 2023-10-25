from flask import Flask, render_template

app = Flask(__name__, template_folder='templates')
# CORS(app, resources={r"/api/*": {"origins": "http://127.0.0.1:5500"}})

@app.route('/')
def home():    

    return render_template('index.html')

if __name__ == '__main__':
    app.run(port=5500)