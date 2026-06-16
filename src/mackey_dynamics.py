
import numpy as np
def generate_mackey_glass_dynamic_regime(n_steps=5000, dt=0.02, beta=0.2, gamma=0.1, n=10):
    """Generates a time series where tau changes dynamically halfway through."""
    total_steps = n_steps + 1000  # including transient
    series = np.zeros(total_steps)
    
    # Start with a safe history length based on maximum tau
    max_tau = 18
    history_length = int(max_tau / dt) + 1
    history = 1.2 + 0.05 * np.random.randn(history_length)
    
    def rhs(x_t, x_tau):
        return beta * x_tau / (1 + x_tau**n) - gamma * x_t

    # Define the exact index where the regime change is triggered
    regime_change_step = total_steps // 2 

    for step in range(total_steps):
        # DYNAMIC REGIME SWITCH:
        # Before halfway: tau = 10 (Perfect, stable, predictable periodic waves)
        # After halfway:  tau = 18 (Crosses the 16.8 bifurcation threshold into Chaos)
        tau = 10.0 if step < regime_change_step else 18.0
        delay_steps = int(tau / dt)

        current_idx = step % history_length
        delay_idx = (step - delay_steps) % history_length

        x_t = history[current_idx]
        x_tau = history[delay_idx]

        k1 = rhs(x_t, x_tau)
        k2 = rhs(x_t + 0.5 * dt * k1, x_tau)
        k3 = rhs(x_t + 0.5 * dt * k2, x_tau)
        k4 = rhs(x_t + dt * k3, x_tau)

        x_new = x_t + (dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)
        history[(current_idx + 1) % history_length] = x_new
        series[step] = x_new

    # Return the series and the exact relative index of the regime change
    return series[1000:], (regime_change_step - 1000)
