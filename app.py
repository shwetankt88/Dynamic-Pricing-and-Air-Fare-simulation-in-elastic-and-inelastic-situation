from flask import Flask, render_template, request
import os
from simulation.pricing_model import run_simulation

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs("static/results", exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["file"]

        if file.filename == "":
            return "No file selected"

        filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filepath)

        graph_path = run_simulation(filepath)

        return render_template("result.html", graph=graph_path)

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
