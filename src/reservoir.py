import numpy as np 
from src.confi import dt,input_scaling,dephasing_rate,relaxation_rate,n_qubits_lo,n_qubits_mc

def create_pauli_operators(n_qubits):
    """
    Creates expanded 2^N x 2^N Pauli matrices for each qubit using Kronecker products.
    """
    I = np.eye(2, dtype=complex)
    X = np.array([[0, 1], [1, 0]], dtype=complex)
    Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
    Z = np.array([[1, 0], [0, -1]], dtype=complex)
    
    paulis = {'X': [], 'Y': [], 'Z': []}
    
    for qubit in range(n_qubits):
        for pauli_name, pauli_mat in [('X', X), ('Y', Y), ('Z', Z)]:
            op = np.eye(1, dtype=complex)
            for q in range(n_qubits):
                if q == qubit:
                    op = np.kron(op, pauli_mat)
                else:
                    op = np.kron(op, I)
            paulis[pauli_name].append(op)
            
    return paulis
def create_ising_reservoir(n_qubits, paulis, J=-1.0, Gamma=0.5):
    """
    H_sys: Constant background energy landscape of the 1D Ising chain.
    """
    dim = 2 ** n_qubits
    H_sys = np.zeros((dim, dim), dtype=complex)
    
    # 1. Nearest-Neighbor Z-Z Interactions (Memory & Scrambling Core)
    for i in range(n_qubits - 1):
        H_sys += J * (paulis["Z"][i] @ paulis["Z"][i + 1])
        
    # 2. Global Transverse Field along X (Forces Quantum Tunneling/Oscillations)
    for i in range(n_qubits):
        H_sys += Gamma * paulis["X"][i]
        
    return H_sys
    #input hamiltonian
def compute_ising_input_hamiltonian(vec, paulis, input_scaling=input_scaling):
    
    dim = paulis["Z"][0].shape[0]
    H_in = np.zeros((dim, dim), dtype=complex)
    
    num_inputs = min(len(vec), len(paulis["Z"]))
    for q in range(num_inputs):
        H_in += vec[q] * paulis["Z"][q]
        
    return input_scaling * H_in

def create_lindblad_operators(n_qubits, dephasing_rate=dephasing_rate, relaxation_rate=relaxation_rate):
    """
    Creates jump operators simulating natural environmental loss (dephasing & decay).
    Includes fixed sigma_minus to correctly relax states towards ground state |0>.
    """
    paulis = create_pauli_operators(n_qubits)
    lindblad_ops = []
    
    # 1. Dephasing (Loss of quantum phase over time)
    for Z_op in paulis['Z']:
        lindblad_ops.append(np.sqrt(dephasing_rate) * Z_op)
        
    # 2. Fixed Relaxation (Energy loss pulling qubits back down to |0>)
    # Top-right element [0, 1]=1 maps transition state |1><0| down to |0><0|
    sigma_minus = np.array([[0, 1], [0, 0]], dtype=complex) 
    
    for qubit in range(n_qubits):
        op = np.eye(1, dtype=complex)
        for q in range(n_qubits):
            if q == qubit:
                op = np.kron(op, sigma_minus)
            else:
                op = np.kron(op, np.eye(2))
        lindblad_ops.append(np.sqrt(relaxation_rate) * op)
        
    return lindblad_ops


# ============================================================================
def enforce_density_matrix(rho):
    
    # Force exact Hermiticity
    rho = (rho + rho.conj().T) / 2
    
    # Spectral decomposition to clip unphysical negative probability noise
    eigvals, eigvecs = np.linalg.eigh(rho)
    eigvals[eigvals < 0] = 0
    
    # Reconstruct matrix
    rho = eigvecs @ np.diag(eigvals) @ eigvecs.conj().T
    
    # Enforce unit trace
    trace_val = np.real(np.trace(rho))
    if trace_val > 0:
        rho /= trace_val
        
    return rho

def expectation(rho, op):
    """
    Calculates the standard quantum mechanical expectation value: <A> = Tr(ρA)
    """
    return np.real(np.trace(rho @ op))
def lindblad_rhs(rho, H, lindblad_ops):
    """
    Computes the right-hand side derivative (dρ/dt) of the Lindblad Master Equation.
    """
    # Unitary parts: -i[H, ρ]
    drho = -1j * (H @ rho - rho @ H)
    
    # Dissipative parts: Σ (LρL† - 0.5 * {L†L, ρ})
    for L in lindblad_ops:
        Ldag = L.conj().T
        drho += L @ rho @ Ldag - 0.5 * (Ldag @ L @ rho + rho @ Ldag @ L)
        
    return drho

def rk4_lindblad_step(rho, H, lindblad_ops, dt):
    """
    Advances the density matrix over time interval dt using 4th-order Runge-Kutta.
    """
    k1 = lindblad_rhs(rho, H, lindblad_ops)
    k2 = lindblad_rhs(rho + 0.5 * dt * k1, H, lindblad_ops)
    k3 = lindblad_rhs(rho + 0.5 * dt * k2, H, lindblad_ops)
    k4 = lindblad_rhs(rho + dt * k3, H, lindblad_ops)
    
    rho_new = rho + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
    
    return enforce_density_matrix(rho_new)
def run_quantum_reservoir_simulation(lorenz_sequence, n_qubits=n_qubits_lo, dt=dt, J=-1.0, Gamma=0.5, input_scaling=input_scaling, dephasing_rate=dephasing_rate, relaxation_rate=relaxation_rate):
    """
    Executes full continuous data feeding over time and records trajectory states.
    """
    dim = 2 ** n_qubits
    
    # Initialize stable hardware primitives
    paulis = create_pauli_operators(n_qubits)
    H_sys = create_ising_reservoir(n_qubits, paulis, J=J, Gamma=Gamma)
    lindblad_ops = create_lindblad_operators(n_qubits, dephasing_rate=dephasing, relaxation_rate=relation_rate)
    
    # Initialize state vector to clear vacuum ground-state |0000><0000|
    rho = np.zeros((dim, dim), dtype=complex)
    rho[0, 0] = 1.0
    
    # Setup history trajectories arrays
    rho_history = []
    observable_history = []
    
    # --- Execute Sequence Timeline Loop ---
    for step, vec in enumerate(lorenz_sequence):
        # 1. Store full current quantum state configuration copies
        rho_history.append(rho.copy())
        
        # 2. Extract standard local Z observable expectations features
        z_features = []
        for q in range(n_qubits):
            z_features.append(expectation(rho, paulis["Z"][q]))
        observable_history.append(z_features)
        
        # 3. Form dynamic data tracking field
        H_in = compute_ising_input_hamiltonian(vec, paulis, input_scaling=input_scaling)
        H_total = H_sys + H_in
        
        # 4. Numerically propagate step forward via high-accuracy RK4
        rho = rk4_lindblad_step(rho, H_total, lindblad_ops, dt)
        
    # Wrap results up into the dictionary schema requested
    results = {
        "rho_history": np.array(rho_history),
        "observable_history": np.array(observable_history),
        "H_sys": H_sys,
        "lindblad_ops": lindblad_ops
    }
    
    return results
