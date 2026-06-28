
import numpy as np


import matplotlib.pyplot as plt
def matrix_sqrt(mat):
    
    # Enforce strict Hermiticity to prevent complex eigenvalue artifacts
    mat = 0.5 * (mat + mat.conj().T)
    eigvals, eigvecs = np.linalg.eigh(mat)
    eigvals = np.clip(eigvals, 0.0, None)
    return eigvecs @ np.diag(np.sqrt(eigvals)) @ eigvecs.conj().T

def create_ZZ_operators(paulis, n_qubits):

    ZZ_ops = []

    for i in range(n_qubits - 1):

        ZZ_ops.append(
            paulis["Z"][i] @ paulis["Z"][i+1]
        )

    return ZZ_ops
def quantum_susceptibility_indicator(
        rho_history,
        paulis,
        window=100):

    n_qubits = len(paulis["Z"])

    # ---------------------------------
    # Observable Set
    # Xi, Zi, ZiZi+1
    # ---------------------------------

    operators = []

    operators.extend(paulis["X"])
    operators.extend(paulis["Z"])

    ZZ_ops = create_ZZ_operators(
        paulis,
        n_qubits
    )

    operators.extend(ZZ_ops)

    n_obs = len(operators)

    # ---------------------------------
    # Observable History
    # ---------------------------------

    observable_history = []

    for rho in rho_history:

        obs = []

        for O in operators:

            obs.append(
                np.real(
                    np.trace(rho @ O)
                )
            )

        observable_history.append(obs)

    observable_history = np.array(
        observable_history
    )

    # ---------------------------------
    # Rolling Covariance
    # ---------------------------------

    lambda_max_series = np.full(
        len(rho_history),
        np.nan
    )

    trace_series = np.full(
        len(rho_history),
        np.nan
    )

    for t in range(
        window,
        len(rho_history)
    ):

        block = observable_history[
            t-window:t
        ]

        C = np.cov(
            block,
            rowvar=False
        )

        eigvals = np.linalg.eigvalsh(C)

        lambda_max_series[t] = np.max(
            eigvals
        )

        trace_series[t] = np.trace(C)

    return {
        "lambda_max": lambda_max_series,
        "susceptibility": trace_series,
        "observable_history": observable_history
    }

#mahnetized variance 
def magnetization_variance(
        rho_history,
        paulis,
        window=100):

    magnetization = []

    for rho in rho_history:

        M = 0.0

        for Z in paulis["Z"]:

            M += np.real(
                np.trace(rho @ Z)
            )

        magnetization.append(M)

    magnetization = np.array(
        magnetization
    )

    variance = np.full(
        len(magnetization),
        np.nan
    )

    for t in range(
        window,
        len(magnetization)
    ):

        variance[t] = np.var(
            magnetization[
                t-window:t
            ]
        )

    return magnetization, variance
# qyntum speed indicator 

# 
def quantum_speed_indicator(
        rho_history,
        window=100):

    total_steps = len(rho_history)
    
    # Pre-allocate speed series to match rho_history length (N) exactly
    speed_series = np.full(total_steps, np.nan)

    # Calculate speeds starting from index 1
    for t in range(1, total_steps):
        delta = rho_history[t] - rho_history[t-1]

        # Relative Dynamical Activity Normalization
        norm_current = np.linalg.norm(rho_history[t], ord='fro')
        
        if norm_current > 1e-12:
            speed = np.linalg.norm(delta, ord='fro') / norm_current
        else:
            speed = 0.0

        speed_series[t] = speed

    # Allocate rolling calculation series with the exact same base length (N)
    mean_speed = np.full(total_steps, np.nan)
    variance_speed = np.full(total_steps, np.nan)

    # Calculate moving windows safely
    for t in range(window, total_steps):
        block = speed_series[t-window:t]

        mean_speed[t] = np.mean(block)
        variance_speed[t] = np.var(block)

    # Return directly without downstream padding functions
    return {
        "speed": speed_series,
        "mean_speed": mean_speed,
        "variance_speed": variance_speed
    }
# fidelity indicator
def quantum_fidelity(rho, sigma):

    sqrt_rho = matrix_sqrt(rho)

    middle = sqrt_rho @ sigma @ sqrt_rho

    fidelity = np.real(
        np.trace(
            matrix_sqrt(middle)
        )
    ) ** 2

    return np.clip(
        fidelity,
        0,
        1
    )
def fidelity_autocorrelation_indicator(
        rho_history,
        window=100):

    # --------------------------------
    # Fidelity series
    # --------------------------------

    fidelity_series = []

    for t in range(1, len(rho_history)):

        F = quantum_fidelity(
            rho_history[t],
            rho_history[t-1]
        )

        fidelity_series.append(F)

    fidelity_series = np.array(
        fidelity_series
    )

    # --------------------------------
    # Lag-1 autocorrelation
    # --------------------------------

    autocorr_series = np.full(
        len(fidelity_series),
        np.nan
    )

    for t in range(
        window,
        len(fidelity_series)
    ):

        block = fidelity_series[
            t-window:t
        ]

        x = block[:-1]
        y = block[1:]

        if np.std(x) < 1e-12:
            continue

        autocorr_series[t] = np.corrcoef(
            x,
            y
        )[0,1]

    return {
        "fidelity": fidelity_series,
        "autocorrelation": autocorr_series
    }

