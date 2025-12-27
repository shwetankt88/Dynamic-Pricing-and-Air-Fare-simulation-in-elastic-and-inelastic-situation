import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline


# ============================
# Load and preprocess data
# ============================
def load_real_data(file_path, source='Delhi', destination='Cochin'):
    df = pd.read_csv(file_path)
    df['Date_of_Journey'] = pd.to_datetime(df['Date_of_Journey'], dayfirst=True)

    df_route = df[
        (df['Source'].str.lower() == source.lower()) &
        (df['Destination'].str.lower() == destination.lower()) &
        (df['Total_Stops'].str.lower() == 'non-stop') &
        (df['Airline'].str.lower() == 'jet airways')
    ].copy()

    if df_route.empty:
        raise ValueError(f"No data found for {source} → {destination}")

    df_route = df_route.sort_values('Date_of_Journey').reset_index(drop=True)
    start_date = df_route['Date_of_Journey'].min()
    df_route['time'] = (df_route['Date_of_Journey'] - start_date).dt.days

    df_daily = df_route.groupby('time')['Price'].mean().reset_index()
    return df_daily


# ============================
# Simulation class
# ============================
class DynamicPricingSimulation:
    def __init__(self, elasticity, price_data, Q0=100.0, dt=0.1):
        self.elasticity = elasticity
        self.Q0 = Q0
        self.dt = dt
        self._setup_price_functions(price_data)

    def _setup_price_functions(self, price_data):
        t_data = price_data['time'].values
        p_data = price_data['Price'].values

        self.T = np.arange(t_data.min(), t_data.max() + self.dt, self.dt)
        self.price_function = CubicSpline(t_data, p_data)
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


# ============================
# Plotting (Saved to file)
# ============================
def plot_combined(
    T_el, P_el, Q_el, R_el,
    T_in, P_in, Q_in, R_in,
    source_df,
    save_path
):
    fig, axs = plt.subplots(3, 1, figsize=(14, 15), sharex=True)

    # Price evolution
    axs[0].plot(source_df['time'], source_df['Price'], 'ko', label='Source Data', alpha=0.6)
    axs[0].plot(T_el, P_el, label='Interpolated Price', linewidth=2.5)
    axs[0].set_ylabel("Price (₹)")
    axs[0].set_title("Air Fare Evolution Over Time")
    axs[0].legend()
    axs[0].grid(True, linestyle='--', alpha=0.6)

    # Demand
    axs[1].plot(T_el, Q_el, label='Elastic Demand (ε = -1.5)', linewidth=2.5)
    axs[1].plot(T_in, Q_in, label='Inelastic Demand (ε = -0.5)', linewidth=2.5)
    axs[1].set_ylabel("Quantity (Tickets)")
    axs[1].set_title("Demand Response")
    axs[1].legend()
    axs[1].grid(True, linestyle='--', alpha=0.6)

    # Revenue
    axs[2].plot(T_el, R_el, label='Revenue (Elastic)', linewidth=2.5)
    axs[2].plot(T_in, R_in, label='Revenue (Inelastic)', linewidth=2.5)

    idx_el = np.argmax(R_el)
    idx_in = np.argmax(R_in)

    axs[2].plot(T_el[idx_el], R_el[idx_el], 'b*', markersize=15)
    axs[2].plot(T_in[idx_in], R_in[idx_in], 'g*', markersize=15)

    axs[2].set_xlabel("Time (Days)")
    axs[2].set_ylabel("Revenue (₹)")
    axs[2].set_title("Revenue Over Time")
    axs[2].legend()
    axs[2].grid(True, linestyle='--', alpha=0.6)

    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()


# ============================
# Flask-facing function
# ============================
def run_simulation(csv_path):
    price_data = load_real_data(csv_path)

    sim_elastic = DynamicPricingSimulation(-1.5, price_data)
    T_el, P_el, Q_el, R_el = sim_elastic.run()

    sim_inelastic = DynamicPricingSimulation(-0.5, price_data)
    T_in, P_in, Q_in, R_in = sim_inelastic.run()

    output_path = "static/results/output.png"

    plot_combined(
        T_el, P_el, Q_el, R_el,
        T_in, P_in, Q_in, R_in,
        price_data,
        output_path
    )

    return output_path


def run_simulation(csv_path):
    price_data = load_real_data(csv_path)

    sim_elastic = DynamicPricingSimulation(-1.5, price_data)
    T_el, P_el, Q_el, R_el = sim_elastic.run()

    sim_inelastic = DynamicPricingSimulation(-0.5, price_data)
    T_in, P_in, Q_in, R_in = sim_inelastic.run()

    output_path = "static/results/output.png"

    plot_combined(
        T_el, P_el, Q_el, R_el,
        T_in, P_in, Q_in, R_in,
        price_data,
        output_path
    )

    # Metrics
    idx_el = np.argmax(R_el)
    idx_in = np.argmax(R_in)

    results = {
        "elastic": {
            "max_revenue": float(R_el[idx_el]),
            "optimal_price": float(P_el[idx_el]),
            "quantity": float(Q_el[idx_el])
        },
        "inelastic": {
            "max_revenue": float(R_in[idx_in]),
            "optimal_price": float(P_in[idx_in]),
            "quantity": float(Q_in[idx_in])
        },
        "image": output_path
    }

    return results

