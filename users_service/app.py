from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
import requests

app = Flask(__name__)
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql://postgres:ilya20122018@localhost/user_service"
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


@app.route("/users/<int:user_id>/transactions", methods=["GET"])
def get_user_transactions(user_id):
    # URL ендпоінту сервісу transactions
    transactions_service_url = "http://localhost:3000/transactions/user/" + str(user_id)

    try:
        # Виконання GET-запиту до сервісу transactions для отримання транзакцій конкретного користувача
        response = requests.get(transactions_service_url)

        # Перевірка статусу відповіді
        if response.status_code == 200:
            transactions = response.json()
            return jsonify(transactions)
        else:
            return (
                jsonify({"message": "Помилка отримання транзакцій"}),
                response.status_code,
            )
    except requests.RequestException as e:
        return jsonify({"message": "Помилка з'єднання з сервісом транзакцій"}), 500


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


if __name__ == "__main__":
    app.run(debug=True)
