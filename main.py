import subprocess

# Start the Flask server in a separate process
flask_process = subprocess.Popen(['python', 'server.py'])

# Start your PyQt application in this process
subprocess.call(['python', 'app.py'])