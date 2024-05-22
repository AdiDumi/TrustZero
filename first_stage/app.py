from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    # Simulate a login check (for demo purposes)
    if username == 'admin' and password == 'password':
        response_data = {"message": "Login successful"}
        status_code = 200
    else:
        response_data = {"message": "Login failed"}
        status_code = 403

    return jsonify(response_data), status_code


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=88)

