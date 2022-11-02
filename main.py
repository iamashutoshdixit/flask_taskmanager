from flask import Flask, request
import models
from datetime import datetime

app = Flask(__name__)


@app.route("/")
def home():
    return "Server is up and running!"



if __name__ == "__main__":
    app.run(debug=True)