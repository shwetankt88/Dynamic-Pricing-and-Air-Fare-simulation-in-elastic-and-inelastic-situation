import matplotlib
matplotlib.use('Agg')  # <--- ADD THIS LINE FIRST
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline

def load_real_data(file_path, source, destination):
    df = pd.read_csv(file_path)
    df['Date_of_Journey'] = pd.to_datetime(df['Date_of_Journey'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Date_of_Journey'])

    df_route = df[
        (df['Source'].str.strip().str.lower() == source.lower()) &
        (df['Destination'].str.strip().str.lower() == destination.lower())
    ].copy()

    if df_route.empty:
        raise ValueError(f"No data found for {source} to {destination}.")

    df_route = df_route.sort_values('Date_of_Journey').reset_index(drop=True)
    start_date = df_route['Date_of_Journey'].min()
    df_route['time'] = (df_route['Date_of_Journey'] - start_date).dt.days

    # Grouping by day
    df_daily = df_route.groupby('time')['Price'].mean().reset_index()

    # --- ADD THIS CHECK HERE ---
    if len(df_daily) < 2:
        raise ValueError(f"The route {source} to {destination} only has {len(df_daily)} unique date(s). Simulation requires at least 2 different dates to calculate price trends.")

    return df_daily

class DynamicPricingSimulation:
    def __init__(self, elasticity, price_data, Q0=100.0, dt=0.1):
        self.elasticity = elasticity
        self.Q0 = Q0
        self.dt = dt
        self._setup_price_functions(price_data)

    def _setup_price_functions(self, price_data):
        t_data, p_data = price_data['time'].values, price_data['Price'].values
        t_u, idx = np.unique(t_data, return_index=True)
        p_u = p_data[idx]
        self.T = np.arange(t_u.min(), t_u.max() + self.dt, self.dt)
        self.price_function = CubicSpline(t_u, p_u)
        self.price_derivative = self.price_function.derivative()

    def run(self):
        Q = np.zeros_like(self.T)
        Q[0] = self.Q0
        for i in range(1, len(self.T)):
            t_prev = self.T[i - 1]
            p = max(self.price_function(t_prev), 1e-6)
            dQ_dt = self.elasticity * (Q[i - 1] / p) * self.price_derivative(t_prev)
            Q[i] = max(0, Q[i - 1] + dQ_dt * self.dt)
        P = self.price_function(self.T)
        return self.T, P, Q, P * Q

def run_simulation(csv_path, source, dest, el_val, in_val):
    price_data = load_real_data(csv_path, source, dest)

    # Run both simulations
    T_el, P_el, Q_el, R_el = DynamicPricingSimulation(el_val, price_data).run()
    T_in, P_in, Q_in, R_in = DynamicPricingSimulation(in_val, price_data).run()

    output_path = "static/results/output.png"
    plt.figure(figsize=(12, 10), facecolor='#0f172a')
    plt.rcParams.update({'text.color': "white", 'axes.labelcolor': "white", 'xtick.color': "white", 'ytick.color': "white"})

    ax1 = plt.subplot(3, 1, 1); ax1.plot(T_el, P_el, color='#6366f1', lw=3); ax1.set_title("Price Trend"); ax1.set_facecolor('#1e293b')
    ax2 = plt.subplot(3, 1, 2); ax2.plot(T_el, Q_el, color='#f59e0b', label='Elastic'); ax2.plot(T_in, Q_in, color='#10b981', label='Inelastic'); ax2.legend(); ax2.set_facecolor('#1e293b')
    ax3 = plt.subplot(3, 1, 3); ax3.plot(T_el, R_el, color='#f59e0b'); ax3.plot(T_in, R_in, color='#10b981'); ax3.set_facecolor('#1e293b')

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

    return {
    "img": output_path,
    "total_rev_el": f"{np.sum(R_el * 0.1):,.0f}",
    "total_rev_in": f"{np.sum(R_in * 0.1):,.0f}",
    "max_price_el": f"{np.max(P_el):,.0f}",
    "max_price_in": f"{np.max(P_in):,.0f}"  # <--- CHANGE THIS FROM P_el TO P_in
}
