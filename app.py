from flask import Flask, render_template, request, redirect, url_for
import os
import pandas as pd
from simulation.pricing_model import run_simulation

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'

@app.route('/')
def index():
    # List all CSV files in the uploads folder
    files = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith('.csv')]

    if not files:
        return "No CSV files found in 'uploads' folder. Please add some."

    # Get unique sources/destinations from the first file to populate defaults
    df = pd.read_csv(os.path.join(UPLOAD_FOLDER, files[0]))
    sources = sorted(df['Source'].unique())
    destinations = sorted(df['Destination'].unique())
    return render_template('index.html', files=files, sources=sources, destinations=destinations)

# CHANGE: Added 'GET' to methods and a check for request.method
@app.route('/simulate', methods=['GET', 'POST'])
def simulate():
    if request.method == 'GET':
        # If someone tries to visit /simulate directly, send them back home
        return redirect(url_for('index'))

    # Process the form data (POST request)
    file_name = request.form.get('file_name')
    source = request.form.get('source')
    dest = request.form.get('destination')
    elastic_val = float(request.form.get('elastic_val'))
    inelastic_val = float(request.form.get('inelastic_val'))

    csv_path = os.path.join(UPLOAD_FOLDER, file_name)

    try:
        results = run_simulation(csv_path, source, dest, elastic_val, inelastic_val)
        return render_template('result.html', results=results, source=source, dest=dest)
    except Exception as e:
        return f"Error: {str(e)}. Please check if the Route exists in the selected CSV."

if __name__ == '__main__':
    app.run(debug=True)
