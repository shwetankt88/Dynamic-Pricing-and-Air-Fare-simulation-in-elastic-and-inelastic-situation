from flask import Flask, render_template, request
import os
from simulation.pricing_model import run_simulation

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/", methods=["GET", "POST"])
def index():
    results = None

    if request.method == "POST":
        file = request.files["file"]

        if file and file.filename.endswith(".csv"):
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(filepath)

            # 🔥 THIS is where the upgrade happens
            results = run_simulation(filepath)

    return render_template("index.html", results=results)


if __name__ == "__main__":
    app.run(debug=True)
