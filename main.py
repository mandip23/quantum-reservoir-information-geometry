import matplotlib.pyplot as plt
from src.mackey_dynamics import generate_mackey_glass_dynamic_regime
from src.embedding import reconstruct_phase_space
from src.reservoir import run_quantum_reservoir_simulation, create_pauli_operators
from src.geometry import compute_quantum_geometry
from src.lorenze_dynamics import regim_change
from src.confi import dt,input_scaling,dephasing_rate ,relaxation_rate
def run_pipeline(sequence, title_name, save_filename, true_split_index):
    # Reconstructing phase space via Takens Embedding
    embedded_data = reconstruct_phase_space(sequence)
    normalized_sequence = embedded_data["normalized"]

    # Simulating Quantum Ising Reservoir
    sim_results = run_quantum_reservoir_simulation(
        normalized_sequence, 
        dt=dt,
        input_scaling=input_scaling,
        dephasing_rate=dephasing_rate,
        relaxation_rate=relaxation_rate,
        n_qubits=n_qubits
    )

    # Computing Quantum Information Geometry metrics
    paulis = create_pauli_operators(n_qubits)
    geometry = compute_quantum_geometry(sim_results["rho_history"], paulis)

    # Plotting and saving geometric signatures...
    fig, ax = plt.subplots(4, 1, figsize=(12, 10), sharex=True)
    
    metrics = ["entropy", "bures", "qfi", "curvature"]
    labels = ["Von Neumann Entropy", "Bures Distance", "Quantum Fisher Info (QFI)", "State Curvature"]
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]

    for i, metric in enumerate(metrics):
        ax[i].plot(geometry[metric], color=colors[i], lw=1.5)
        ax[i].axvline(true_split_index, color='r', linestyle='--', alpha=0.8, label="Regime Change Trigger")
        ax[i].set_ylabel(labels[i], fontsize=10, fontweight='bold')
        ax[i].grid(True, linestyle=":", alpha=0.6)
        if i == 0:
            ax[i].legend(loc="upper right")

    ax[-1].set_xlabel("Simulation Steps", fontsize=12)
    plt.suptitle(f"Information-Geometric Signatures ({title_name})", fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    plt.savefig(save_filename, dpi=300)
    print(f" Saved: {save_filename}")
    plt.close() # Closes figure to clean up memory before next run

def main():
    # =========================================================================
    # 1. RUN LORENZ ATTRACTOR PIPELINE
    # =========================================================================
    # Using the regim_change function from your lorenze_dynamics.py
    lorenz_series, nstep = regim_change(nstep=5000, rho1=28, rho2=15)
    
    # We pass lorenz_series[:, 0] to process the X-coordinate channel
    run_pipeline(
        sequence=lorenz_series[:, 0], 
        title_name="Lorenz Attractor", 
        save_filename="lorenz_quantum_signatures.png",
        true_split_index=nstep
        n_qubits=n_qubits_lo
    )

    
    # 2. RUN MACKEY-GLASS PIPELINE
    
    mackey_series, mackey_split_idx = generate_mackey_glass_dynamic_regime(n_steps=5000, dt=dt)
    
    run_pipeline(
        sequence=mackey_series, 
        title_name="Mackey-Glass System", 
        save_filename="mackey_quantum_signatures.png",
        true_split_index=mackey_split_idx,
        n_qubits=n_qubits_mc
    )
    
    

if __name__ == "__main__":
    main()
