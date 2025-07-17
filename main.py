from scraper import check_new_listings
from flask import Flask, jsonify
import time
import warnings
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
warnings.filterwarnings("ignore")

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    try:
        check_new_listings()
        time.sleep(30)
        return jsonify({"status": "success", "message": "Listings checked successfully"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)