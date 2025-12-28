from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import pandas as pd
from simulation.pricing_model import run_simulation
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_routes(file_path):
    df = pd.read_csv(file_path)
    return sorted(df['Source'].unique().tolist()), sorted(df['Destination'].unique().tolist())

@app.route('/')
def index():
    files = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith('.csv')]
    return render_template('index.html', files=files)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files: return redirect(request.url)
    file = request.files['file']
    if file.filename == '': return redirect(request.url)
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return redirect(url_for('index'))

@app.route('/get_options/<filename>')
def get_options(filename):
    sources, dests = get_routes(os.path.join(UPLOAD_FOLDER, filename))
    return jsonify({'sources': sources, 'destinations': dests})

@app.route('/simulate', methods=['POST'])
def simulate():
    file_name = request.form.get('file_name')
    source = request.form.get('source')
    dest = request.form.get('destination')

    # Check if a file was actually selected
    if not file_name:
        files = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith('.csv')]
        return render_template('index.html', files=files, error_msg="Please select a dataset first.")

    csv_path = os.path.join(UPLOAD_FOLDER, file_name)

    try:
        # We TRY to run the simulation
        results = run_simulation(
            csv_path, source, dest,
            float(request.form['elastic_val']),
            float(request.form['inelastic_val'])
        )
        return render_template('result.html', results=results, s=source, d=dest)

    except ValueError as e:
        # If the ValueError happens, we CATCH it here.
        # This stops the system from crashing (no white error screen).
        files = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith('.csv')]

        # We reload the dropdown data so the user can try again
        sources, dests = get_routes(csv_path)

        return render_template('index.html',
                               files=files,
                               sources=sources,
                               destinations=dests,
                               error_msg=str(e)) # This sends the text to the red box
if __name__ == '__main__':
    # Use the port assigned by the cloud provider, default to 5000
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
