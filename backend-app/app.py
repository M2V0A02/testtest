from flask import Flask, jsonify
from flask_cors import CORS
import os
import socket

app = Flask(__name__)
CORS(app)

@app.route('/api/info', methods=['GET'])
def get_info():
    version = os.getenv('APP_VERSION', 'v1.0')
    message = os.getenv('APP_MESSAGE', 'Hello from Flask Backend!')

    return jsonify({
        'version': version,
        'message': message,
        'hostname': socket.gethostname(),
        'status': 'healthy'
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
