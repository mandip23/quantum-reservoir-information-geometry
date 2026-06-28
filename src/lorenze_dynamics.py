import numpy as np

def lorenz_equations(state, sigma=10, rho=28.0, beta=8/3):
    x, y, z = state
    return np.array([sigma * (y - x), x * (rho - z) - y, x * y - beta * z])

def runge_kutta4_dynamic(n_steps=20000, dt1=0.001, rho_sequence=None):
    
    series = []
    
    # Generate a randomized initial state near the attractor locus
    state = np.array([1.0, 1.0, 1.0]) + 0.5 * np.random.randn(3)
    
    # Burn away transients using the starting chaotic rho value
    starting_rho = rho_sequence[0] if rho_sequence is not None else 28.0
    for _ in range(5000):
        k1 = lorenz_equations(state, rho=starting_rho)
        k2 = lorenz_equations(state + 0.5 * dt1 * k1, rho=starting_rho)
        k3 = lorenz_equations(state + 0.5 * dt1 * k2, rho=starting_rho)
        k4 = lorenz_equations(state + dt1 * k3, rho=starting_rho)
        state = state + (dt1 / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)

    # Main simulation loop tracking dynamic parameter evolution
    for i in range(n_steps):
        current_rho = rho_sequence[i] if rho_sequence is not None else 28.0
        
        k1 = lorenz_equations(state, rho=current_rho)
        k2 = lorenz_equations(state + 0.5 * dt1 * k1, rho=current_rho)
        k3 = lorenz_equations(state + 0.5 * dt1 * k2, rho=current_rho)
        k4 = lorenz_equations(state + dt1 * k3, rho=current_rho)
        state = state + (dt1 / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
        series.append(state.copy())
    
    return np.array(series)

def regime_drift_validated(nstep=10000, drift_window=8000, rho1=28.0, rho2=5.0, profile="smoothstep"):
    
    total_steps = nstep * 2
    rho_sequence = np.zeros(total_steps)
    
    # Define expanded boundaries to allow slow parameter deceleration
    start_drift_idx = nstep - (drift_window // 2)
    end_drift_idx = nstep + (drift_window // 2)
    
    # 1. Pre-drift stable chaotic phase
    rho_sequence[:start_drift_idx] = rho1
    
    # Generate normalized coordinate space [0, 1] for nonlinear profiles
    window_length = end_drift_idx - start_drift_idx
    x = np.linspace(0, 1, window_length)
    
    # 2. Smooth nonlinear parameter drift profiles
    if profile == "quadratic":
        # Accelerates progress toward the target regime
        drift_profile = rho1 + (rho2 - rho1) * (x**2)
    elif profile == "smoothstep":
        # Smooth zero-derivative anchors at both boundaries (3x^2 - 2x^3)
        drift_profile = rho1 + (rho2 - rho1) * (3 * x**2 - 2 * x**3)
    else:
        # Fallback to linear
        drift_profile = np.linspace(rho1, rho2, window_length)
        
    rho_sequence[start_drift_idx:end_drift_idx] = drift_profile
    
    # 3. Post-drift stable phase
    rho_sequence[end_drift_idx:] = rho2
    
    # Integrate continuously over the modified vector
    time_series = runge_kutta4_dynamic(n_steps=total_steps, rho_sequence=rho_sequence)
    
    return time_series, start_drift_idx, end_drift_idx
