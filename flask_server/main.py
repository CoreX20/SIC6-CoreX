from flask import Flask, jsonify, request
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
from pytz import timezone
from bson.json_util import dumps

app = Flask(__name__)

uri = "mongodb+srv://kornel:70QTPEPQnmJHID5x@cluster-corex.tdrd8.mongodb.net/?retryWrites=true&w=majority&appName=Cluster-CoreX"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi("1"))

db = client["sensor_db"]
collection = db["sensor_data"]


@app.route("/sensor_data", methods=["GET"])
def get_sensor_data():
    sensor_data = collection.find()
    return dumps(sensor_data)


@app.route("/sensor_data", methods=["POST"])
def add_sensor_data():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    if not all(field in data for field in ["sensor_id", "sensor_type", "value"]):
        return jsonify({"error": "Missing sensor data fields"}), 400

    data["timestamp"] = datetime.now(timezone("Asia/Jakarta")).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    result = collection.insert_one(data)
    return (
        jsonify(
            {
                "status": "success",
                "message": "Sensor data added",
                "id": str(result.inserted_id),
            }
        ),
        201,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
