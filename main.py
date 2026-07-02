
    
import numpy as np
import matplotlib.pyplot as plt
from src.reservoir import create_pauli_operators, run_quantum_reservoir_simulation
from src.embedding import reconstruct_phase_space, time_delay_embedding, normalize_embedding
from src.confi import dt, input_scaling, dephasing_rate, relaxation_rate, n_qubits_lo

from src.dynamicindicator import (
    quantum_susceptibility_indicator, 
    magnetization_variance, 
    fidelity_autocorrelation_indicator, 
    quantum_speed_indicator
)

# Target the dynamic Lorenz integration script completed in the prior step
from src.lorenze_dynamics import runge_kutta4_dynamic, regime_drift_validated

def collect_ensemble_metrics(n_trials=5, window=200, is_control=False):
   
    n_qubits = n_qubits_lo
    paulis = create_pauli_operators(n_qubits)
    
    trial_suscep = []
    trial_mag_var = []
    trial_speed_var = []
    trial_fid_corr = []
    
    # 1. Establish embedding parameters from baseline chaotic dynamics
    base_raw = runge_kutta4_dynamic(n_steps=20000, rho_sequence=np.full(20000, 28.0))
    pipeline = reconstruct_phase_space(base_raw[:, 0])
    tau, dim = pipeline["tau"], pipeline["dimension"]
    offset = (dim - 1) * tau
    
    print(f"Starting Ensemble Loop (Control={is_control}) | Detected Tau={tau}, Dim={dim}...")
    
    for trial in range(n_trials):
        print(f"  -> Executing trial iteration {trial+1}/{n_trials}...")
        
        if is_control:
            # Control runs completely stationary at chaotic state Rho=28
            total_steps = 20000
            raw_series = runge_kutta4_dynamic(n_steps=total_steps, rho_sequence=np.full(total_steps, 28.0))
            start_drift, end_drift = 6000, 14000  # Mirror window shapes for control alignment
        else:
            # Transition drifts nonlinearly across the subcritical Hopf bifurcation point
            raw_series, start_drift, end_drift = regime_drift_validated(
                nstep=20000, 
                drift_window=8000, 
                rho1=28.0, 
                rho2=5.0, 
                profile="smoothstep"
            )
            
        # 2. Phase-space reconstruction pipeline
        X = time_delay_embedding(raw_series[:, 0], tau, dim)
        X_norm, _ = normalize_embedding(X)
        
        # Adjust physical markers to match post-embedding geometry truncation
        adjusted_start = start_drift - offset
        adjusted_end = end_drift - offset
        
        # 3. Simulate reservoir state dynamics
        sim_data = run_quantum_reservoir_simulation(X_norm, n_qubits=n_qubits)
        rho_history = sim_data["rho_history"]
        
        # 4. Extract EWS indicators
        sus_res = quantum_susceptibility_indicator(rho_history, paulis, window=window)
        _, mag_var = magnetization_variance(rho_history, paulis, window=window)
        speed_res = quantum_speed_indicator(rho_history, window=window)
        fid_res = fidelity_autocorrelation_indicator(rho_history, window=window)
        
        trial_suscep.append(sus_res["lambda_max"])
        trial_mag_var.append(mag_var)
        trial_speed_var.append(speed_res["variance_speed"])
        trial_fid_corr.append(fid_res["autocorrelation"])
        
    return {
        "lambda_max": np.array(trial_suscep),
        "mag_variance": np.array(trial_mag_var),
        "speed_variance": np.array(trial_speed_var),
        "fidelity_corr": np.array(trial_fid_corr),
        "start_trigger": adjusted_start,
        "end_trigger": adjusted_end,
        "length": len(X_norm)
    }

def compute_bounds(matrix):
    mean = np.nanmean(matrix, axis=0)
    std = np.nanstd(matrix, axis=0)
    return mean, std

def main():
    n_trials = 10  # Set to a robust ensemble sample size
    window_size = 20# initally 50
    
    
    print("PROCESSING TRANSITION GROUP DATA GENERATION")
  
    trans = collect_ensemble_metrics(n_trials=n_trials, window=window_size, is_control=False)
    
    print("\n==")
    print("PROCESSING CONTROL BASELINE GROUP DATA GENERATION")
   
    ctrl = collect_ensemble_metrics(n_trials=n_trials, window=window_size, is_control=True)
    
 
    # VISUALIZATION MATRIX WITH TWO-POINT PLOT ALIGNMENT
   
    fig, axs = plt.subplots(4, 2, figsize=(16, 14), sharex=False, sharey=False)
    
    metrics_keys = ["lambda_max", "mag_variance", "speed_variance", "fidelity_corr"]
    titles = [
        "Quantum Susceptibility $\\lambda_{\\max}(C)$",
        "Magnetization Variance $\\text{Var}(M)$",
        "Quantum Speed Variance $\\text{Var}(V_{\\text{rel}})$",
        "Fidelity Lag-1 Autocorrelation"
    ]
    colors = ["darkred", "chocolate", "darkblue", "purple"]
    bg_colors = ["crimson", "orange", "royalblue", "orchid"]

    for idx, key in enumerate(metrics_keys):
        m_trans, s_trans = compute_bounds(trans[key])
        m_ctrl, s_ctrl = compute_bounds(ctrl[key])
        
       
        # DYNAMIC HORIZONTAL ALIGNMENT FIX (Eliminates flat trailing lines)
       
        # Determine the maximum actual valid size produced by your rolling window indicators
        actual_max_steps = min(len(m_trans), len(m_ctrl))
        
        # Slice arrays exactly to match the actual true data horizon
        m_trans = m_trans[:actual_max_steps]
        s_trans = s_trans[:actual_max_steps]
        m_ctrl = m_ctrl[:actual_max_steps]
        s_ctrl = s_ctrl[:actual_max_steps]
        
        t_axis_trans = np.arange(actual_max_steps)
        t_axis_ctrl = np.arange(actual_max_steps)
        
        # Rescale boundary markers relative to the precise tracking timeline length
        adj_trans_start = int((trans["start_trigger"] / trans["length"]) * actual_max_steps)
        adj_trans_end = int((trans["end_trigger"] / trans["length"]) * actual_max_steps)
        
        adj_ctrl_start = int((ctrl["start_trigger"] / ctrl["length"]) * actual_max_steps)
        adj_ctrl_end = int((ctrl["end_trigger"] / ctrl["length"]) * actual_max_steps)
        # =========================================================================
        
        # --- Column 0: Transition Group Axis ---
        axs[idx, 0].plot(t_axis_trans, m_trans, color=colors[idx], lw=2, label='Ensemble Mean')
        axs[idx, 0].fill_between(t_axis_trans, m_trans - s_trans, m_trans + s_trans, color=bg_colors[idx], alpha=0.15)
        
        # Structural boundary markers
        axs[idx, 0].axvline(adj_trans_start, color='orange', linestyle='--', lw=2, label='Drift Begins')
        axs[idx, 0].axvline(adj_trans_end, color='red', linestyle='--', lw=2, label='Transition Complete')
        axs[idx, 0].axvspan(adj_trans_start, adj_trans_end, color='gold', alpha=0.08, label='Warning Zone')
        
        axs[idx, 0].set_ylabel(titles[idx], fontweight='bold')
        axs[idx, 0].grid(True, linestyle=":", alpha=0.6)
        axs[idx, 0].set_xlim(0, actual_max_steps)  # Lock tightly to valid steps
        
        if idx == 0:
            axs[idx, 0].set_title("Transition Group: $\\rho_L = 28 \\rightarrow 5$ (Smoothstep Drift)", fontsize=11, fontweight='bold')
            axs[idx, 0].legend(loc='upper right')

        # --- Column 1: Control Baseline Group Axis ---
        axs[idx, 1].plot(t_axis_ctrl, m_ctrl, color='teal', lw=2, label='Control Baseline')
        axs[idx, 1].fill_between(t_axis_ctrl, m_ctrl - s_ctrl, m_ctrl + s_ctrl, color='mediumaquamarine', alpha=0.15)
        
        # Reference markers for stationary comparison
        axs[idx, 1].axvline(adj_ctrl_start, color='black', linestyle=':', lw=1.5, label='Reference Window')
        axs[idx, 1].axvline(adj_ctrl_end, color='black', linestyle=':', lw=1.5)
        
        axs[idx, 1].grid(True, linestyle=":", alpha=0.6)
        axs[idx, 1].set_xlim(0, actual_max_steps)  # Lock tightly to valid steps
        
        if idx == 0:
            axs[idx, 1].set_title("Control Group: Stationary Chaos ($\\rho_L = 28$)", fontsize=11, fontweight='bold')
            axs[idx, 1].legend(loc='upper right')

    axs[3, 0].set_xlabel("Simulation Timeline Steps (Post-Embedding)", fontweight='bold')
    axs[3, 1].set_xlabel("Simulation Timeline Steps (Post-Embedding)", fontweight='bold')
    
    plt.suptitle("Quantum Reservoir Early Warning Signal (EWS) Evaluation Matrix\n"
                 "Statistical Verification of Custom Information Metrics Over Continuous Transitions", 
                 fontsize=14, fontweight='bold', y=0.97)
    
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    output_png = "ews_custom_indicators_matrix.png"
    plt.savefig(output_png, dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    main()
