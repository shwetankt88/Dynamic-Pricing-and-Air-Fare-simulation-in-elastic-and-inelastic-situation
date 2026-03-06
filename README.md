# Dynamic Pricing & Air Fare Simulation

A Flask web application that simulates and compares **elastic vs inelastic** demand behaviour for airline pricing using real flight price data.

🌐 **Live Demo:** [https://dynamic-pricing-and-air-fare-simulation.onrender.com/](https://dynamic-pricing-and-air-fare-simulation.onrender.com/)

---

## Features

- Upload your own CSV dataset of flight prices
- Select source and destination routes from the data
- Adjust elasticity sliders for elastic and inelastic demand scenarios
- Visualise **Price Trend**, **Demand Comparison**, and **Revenue Comparison** charts
- View summary statistics: total revenue and peak fare for each scenario

---

## How It Works

The simulation engine (`simulation/pricing_model.py`) uses **CubicSpline interpolation** on the uploaded flight price data to build a continuous price function. Demand response is modelled using an ODE-style equation:

```
dQ/dt = elasticity × (Q / P) × dP/dt
```

This is integrated forward in time to produce demand `Q(t)` and revenue `R(t) = P(t) × Q(t)` for both the elastic and inelastic parameter sets. Charts are generated with Matplotlib and served as unique PNG files per request.

---

## CSV Format

The uploaded CSV must contain at least these columns:

| Column            | Description                         |
|-------------------|-------------------------------------|
| `Source`          | Origin city/airport                 |
| `Destination`     | Destination city/airport            |
| `Date_of_Journey` | Date in DD/MM/YYYY format           |
| `Price`           | Ticket price (numeric)              |

---

## Project Structure

```
├── app.py                    # Flask web server
├── simulation/
│   ├── __init__.py           # Package marker
│   └── pricing_model.py      # Core simulation engine
├── templates/
│   ├── index.html            # Main page with upload & config
│   └── result.html           # Results display page
├── static/
│   ├── style.css             # CSS styles
│   └── results/              # Generated chart images (gitignored)
├── uploads/                  # User-uploaded CSV datasets
├── requirements.txt          # Python dependencies
└── .gitignore
```

---

## Tech Stack

| Tool        | Purpose                              |
|-------------|--------------------------------------|
| Python      | Core language                        |
| Flask       | Web framework                        |
| NumPy       | Numerical computation                |
| Pandas      | CSV loading and data manipulation    |
| Matplotlib  | Chart generation                     |
| SciPy       | CubicSpline interpolation            |
| Gunicorn    | Production WSGI server               |

---

## Local Setup

```bash
# 1. Clone the repository
git clone https://github.com/shwetankt88/Dynamic-Pricing-and-Air-Fare-simulation-in-elastic-and-inelastic-situation.git
cd Dynamic-Pricing-and-Air-Fare-simulation-in-elastic-and-inelastic-situation

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the development server
python app.py
```

Visit [http://localhost:5000](http://localhost:5000) in your browser.

---

## Deployment (Render)

The app is configured for Render. It reads the `PORT` environment variable automatically:

```python
port = int(os.environ.get("PORT", 5000))
app.run(host='0.0.0.0', port=port)
```

Both the `uploads/` and `static/results/` directories are created automatically on startup if they do not exist.
