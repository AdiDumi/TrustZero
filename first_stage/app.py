from flask import Flask, request, jsonify


app = Flask(__name__)


servers = [1, 2, 3, 4, 5]


@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    # Simulate a login check (for demo purposes)
    if username != 'admin' or password != 'password':
        return jsonify({"message": "Login failed"}), 403

    status_code = 200
    response_data = {"message": "Login successful"}
    return jsonify(response_data), status_code


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=88)

