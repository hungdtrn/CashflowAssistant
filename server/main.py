import os
import sys
import shutil
from flask import Flask, jsonify, request, render_template, Response

from utils import query_data, connect_db

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../")))
from ai.main import get_result

app = Flask(__name__)



@app.route("/chat", methods=["POST"])
def chat():
    userId = request.json["userId"]
    query = request.json["message"]

    # data = query_data(userId)
    # output = get_result(query, data)
    db = connect_db()
    try:
        output = get_result(query, db=db, userID=userId)
    except Exception as e:
        output = "We encounter an error, please try again later."
        print("Internal Error:", e)
    return {
        "response": output
    }

if __name__ == "__main__":
    "Create dummy data"


    app.run(host='0.0.0.0', debug="True", port=8080)
