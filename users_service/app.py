from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
import requests
import hashlib

app = Flask(__name__)
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql://postgres:qwerty123@postgres-service/users"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    surname = db.Column(db.String)
    email = db.Column(db.String, unique=True)
    phone = db.Column(db.String)
    balance = db.Column(db.Integer)

    def __init__(self, name, surname, email, phone, balance):
        self.name = name
        self.surname = surname
        self.email = email
        self.phone = phone
        self.balance = balance


# Використання контексту додатку для створення таблиці
with app.app_context():
    inspector = inspect(db.engine)
    if not inspector.has_table("users"):
        db.create_all()


@app.route("/users", methods=["POST"])
def create_user():
    data = request.json
    new_user = User(
        name=data["name"],
        surname=data["surname"],
        email=data["email"],
        phone=data["phone"],
        balance=data["balance"],
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created successfully"}), 201


@app.route("/users", methods=["GET"])
def get_all_users():
    users = User.query.all()
    result = []
    for user in users:
        user_data = {
            "id": user.id,
            "name": user.name,
            "surname": user.surname,
            "email": user.email,
            "phone": user.phone,
            "balance": user.balance,
        }
        result.append(user_data)

    return jsonify(result), 200


@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = User.query.get(user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    user_data = {
        "id": user.id,
        "name": user.name,
        "surname": user.surname,
        "email": user.email,
        "phone": user.phone,
        "balance": user.balance,
        "account_history": []
    }
    return jsonify(user_data), 200


@app.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    user = User.query.get(user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    data = request.json
    user.name = data.get("name", user.name)
    user.surname = data.get("surname", user.surname)
    user.email = data.get("email", user.email)
    user.phone = data.get("phone", user.phone)
    user.balance = data.get("balance", user.balance)
    db.session.commit()

    return jsonify({"message": "User updated successfully"}), 200


@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "User deleted successfully"}), 200


@app.route("/users/<int:user_id>/update-balance", methods=["POST"])
def update_user_balance(user_id):
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    balance_modifier = request.json["modifier"]

    user.balance += balance_modifier

    if user.balance < 0:
        return jsonify({"error": "User has insufficient balance."}), 400

    db.session.commit()
    return jsonify({"message": "Balance was updated successfully."}), 200

@app.route("/users/test-scaling", methods=["POST"])
def simulate_load():
    for _ in range(100000000):
        hashlib.sha256(b"test").hexdigest()
    return jsonify({"detail": "Performed 100000000 iters of sha256 hashing."}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=80)
