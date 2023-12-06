from urllib.parse import urljoin

from flask import Flask, jsonify, request
import requests
from dataclasses import dataclass

app = Flask(__name__)

app.config["USERS_SERVICE_BASE_URL"] = "http://127.0.0.1:5000"
app.config["TRANSACTIONS_SERVICE_BASE_URL"] = "http://127.0.0.1:3000"


@dataclass
class Transfer:
    sender_id: int
    receiver_id: int
    amount: int
    title: str


@app.route("/transfer-funds", methods=["POST"])
def transfer_funds():
    transfer = Transfer(**request.json)

    if transfer.sender_id == transfer.receiver_id:
        return jsonify({"error": "You cannot send funds to yourself."}), 400

    transaction = {
        "sender_id": transfer.sender_id,
        "receiver_id": transfer.receiver_id,
        "status": "pending",
        "type": "p2p",
        "amount": transfer.amount,
        "title": transfer.title,
        "failure_reason": None,
    }

    response = requests.post(
        urljoin(app.config["TRANSACTIONS_SERVICE_BASE_URL"], "transactions"), data=transaction
    )

    if response.status_code not in (200, 201):
        return jsonify({"error": "Error creating transaction."}), 400

    transaction_id = response.json()["id"]

    sender_balance_update = requests.post(
        urljoin(
            app.config["USERS_SERVICE_BASE_URL"],
            f"/users/{transfer.sender_id}/update-balance",
        ),
        json={"modifier": -1 * transfer.amount},
    )

    receiver_balance_update = requests.post(
        urljoin(
            app.config["USERS_SERVICE_BASE_URL"],
            f"/users/{transfer.receiver_id}/update-balance",
        ),
        json={"modifier": transfer.amount},
    )

    balance_update_failed = False
    failure_reason = ""
    if sender_balance_update.status_code != 200:
        failure_reason = sender_balance_update.json()["error"]
        balance_update_failed = True

        if receiver_balance_update.status_code == 200:
            requests.post(
                urljoin(
                    app.config["USERS_SERVICE_BASE_URL"],
                    f"/users/{transfer.receiver_id}/update-balance",
                ),
                data={"modifier": -1 * transfer.amount},
            )

    if receiver_balance_update.status_code != 200:
        failure_reason = sender_balance_update.json()["error"]
        balance_update_failed = True

        if sender_balance_update.status_code == 200:
            requests.post(
                urljoin(
                    app.config["USERS_SERVICE_BASE_URL"],
                    f"/users/{transfer.sender_id}/update-balance",
                ),
                data={"modifier": transfer.amount},
            )

    if balance_update_failed:
        transaction["status"] = "failed"
        transaction["failure_reason"] = failure_reason

        requests.put(
            urljoin(app.config["TRANSACTIONS_SERVICE_BASE_URL"], f"transactions/{transaction_id}"),
            data=transaction,
        )
        return jsonify({"error": "Transfer failed. " + failure_reason}), 400

    transaction["status"] = "success"
    requests.put(
        urljoin(app.config["TRANSACTIONS_SERVICE_BASE_URL"], f"transactions/{transaction_id}"),
        data=transaction,
    )

    return jsonify({"error": "Transfer succeeded. "}), 200


if __name__ == "__main__":
    app.run(debug=True, port=5001)
