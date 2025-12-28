import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline
import os

def load_real_data(file_path, source, destination):
    df = pd.read_csv(file_path)
    df['Date_of_Journey'] = pd.to_datetime(df['Date_of_Journey'], dayfirst=True)

    # Filtering based on user selection
    df_route = df[
        (df['Source'].str.lower() == source.lower()) &
        (df['Destination'].str.lower() == destination.lower())
    ].copy()

    if df_route.empty:
        raise ValueError(f"No data found for {source} → {destination} in this file.")

    df_route = df_route.sort_values('Date_of_Journey').reset_index(drop=True)
    start_date = df_route['Date_of_Journey'].min()
    df_route['time'] = (df_route['Date_of_Journey'] - start_date).dt.days

    df_daily = df_route.groupby('time')['Price'].mean().reset_index()
    return df_daily

class DynamicPricingSimulation:
    def __init__(self, elasticity, price_data, Q0=100.0, dt=0.1):
        self.elasticity = elasticity
        self.Q0 = Q0
        self.dt = dt
        self._setup_price_functions(price_data)

    def _setup_price_functions(self, price_data):
        t_data = price_data['time'].values
        p_data = price_data['Price'].values
        # Ensure unique t_data for spline
        t_unique, idx = np.unique(t_data, return_index=True)
        p_unique = p_data[idx]

        self.T = np.arange(t_unique.min(), t_unique.max() + self.dt, self.dt)
        self.price_function = CubicSpline(t_unique, p_unique)
        self.price_derivative = self.price_function.derivative()

    def run(self):
        Q = np.zeros_like(self.T)
        Q[0] = self.Q0
        for i in range(1, len(self.T)):
            t_prev = self.T[i - 1]
            p = max(self.price_function(t_prev), 1e-6)
            dp_dt = self.price_derivative(t_prev)
            dQ_dt = self.elasticity * (Q[i - 1] / p) * dp_dt
            Q[i] = max(0, Q[i - 1] + dQ_dt * self.dt)

        P = self.price_function(self.T)
        R = P * Q
        return self.T, P, Q, R

def run_simulation(csv_path, source, dest, elastic_val, inelastic_val):
    price_data = load_real_data(csv_path, source, dest)

    sim_el = DynamicPricingSimulation(elastic_val, price_data)
    T_el, P_el, Q_el, R_el = sim_el.run()

    sim_in = DynamicPricingSimulation(inelastic_val, price_data)
    T_in, P_in, Q_in, R_in = sim_in.run()

    # Save Plot
    output_path = "static/results/output.png"
    plt.figure(figsize=(12, 10))

    plt.subplot(3, 1, 1)
    plt.plot(T_el, P_el, color='#6366f1', lw=2)
    plt.title(f"Price Trend: {source} to {dest}")
    plt.ylabel("Price (₹)")

    plt.subplot(3, 1, 2)
    plt.plot(T_el, Q_el, label=f'Elastic ({elastic_val})', color='#f59e0b')
    plt.plot(T_in, Q_in, label=f'Inelastic ({inelastic_val})', color='#10b981')
    plt.legend()
    plt.ylabel("Demand")

    plt.subplot(3, 1, 3)
    plt.plot(T_el, R_el, color='#f59e0b')
    plt.plot(T_in, R_in, color='#10b981')
    plt.ylabel("Revenue (₹)")
    plt.xlabel("Days")

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

    return {
        "img": output_path,
        "max_rev_el": f"{np.max(R_el):,.2f}",
        "max_rev_in": f"{np.max(R_in):,.2f}",
        "total_rev_el": f"{np.sum(R_el * 0.1):,.2f}", # Area under curve
        "total_rev_in": f"{np.sum(R_in * 0.1):,.2f}"
    }
