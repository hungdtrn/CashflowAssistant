import os
import sys
import shutil
from flask import Flask, jsonify, request, render_template, Response

from utils import query_data, connect_db
from ai.main import AIApplication

app = Flask(__name__)

sessions = {}
def get_or_create_session(userID):
    if userID not in sessions:
        db = connect_db()
        sessions[userID] = {
            "db": db,
            "userID": userID,
            "ai": AIApplication(db=db, userID=userID),
            "history": [],
        }
    return sessions[userID]

def clear_session(userID):
    if userID in sessions:
        del sessions[userID]

@app.route("/data", methods=["GET"])
def data():
    userID = request.args.get("userID")
    session = get_or_create_session(userID)
    db = session["db"]
    query = "SELECT * FROM DATA WHERE DATE >= date('now', '-7 days')"
    if userID:
        query += " AND Client_ID = {}".format(userID)

    query += " ORDER BY DATE DESC"

    data = db.run(query, include_columns=True)
    return {
        "response": data
    }

@app.route("/history", methods=["GET"])
def history():
    userID = request.args.get("userID")
    session = get_or_create_session(userID)
    return {
        "response": session["history"]
    }

@app.route("/clear_history", methods=["POST"])
def clear_history():
    clear_session(request.json["userID"])
    return {
        "response": "Done"
    }

@app.route("/chat", methods=["POST"])
def chat():
    userId = request.json["userId"]
    query = request.json["message"]

    session = get_or_create_session(userId)
    session["history"].append({
        "role": "user",
        "content": query
    })
    ai = session["ai"]

    def _fn(retries):
        try:
            output = ai.run(query)
        except Exception as e:
            if retries > 0:
                return _fn(retries-1)
            else:
                output = "We encounter an error, please try again later."
                print("Internal Error:", e)
        return output

    output = _fn(1)
    session["history"].append({
        "role": "assistant",
        "content": output
    })
    return {
        "response": output
    }

if __name__ == "__main__":
    "Create dummy data"
    import argparse
    parser = argparse.ArgumentParser()

    app.run(host='0.0.0.0', debug="True", port=8080)
