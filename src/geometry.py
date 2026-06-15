def von_neumann_entropy(rho):
    eigvals = np.linalg.eigvalsh(rho)

    eigvals = np.real(eigvals)
    eigvals = eigvals[eigvals > 1e-12]

    if len(eigvals) == 0:
        return 0.0

    return -np.sum(eigvals * np.log(eigvals))

#bures distance -----
def matrix_sqrt(mat):

    eigvals, eigvecs = np.linalg.eigh(mat)

    eigvals = np.clip(eigvals, 0, None)

    return eigvecs @ np.diag(np.sqrt(eigvals)) @ eigvecs.conj().T
def bures_distance(rho, sigma):

    sqrt_rho = matrix_sqrt(rho)

    middle = sqrt_rho @ sigma @ sqrt_rho

    fidelity = np.real(
        np.trace(
            matrix_sqrt(middle)
        )
    ) ** 2

    fidelity = np.clip(fidelity, 0, 1)

    return np.sqrt(
        max(
            0,
            2 - 2*np.sqrt(fidelity)
        )
    )
#quntum fisher information metric
def quantum_fisher_information(rho, generator):

    eigvals, eigvecs = np.linalg.eigh(rho)

    qfi = 0.0

    for i in range(len(eigvals)):
        for j in range(len(eigvals)):

            denom = eigvals[i] + eigvals[j]

            if denom < 1e-12:
                continue

            Aij = (
                eigvecs[:, i].conj().T
                @ generator
                @ eigvecs[:, j]
            )

            qfi += (
                2
                *
                ((eigvals[i]-eigvals[j])**2)
                /
                denom
                *
                np.abs(Aij)**2
            )

    return np.real(qfi)

#state space curvature
def state_space_curvature(d_prev, d_next, d_skip):

    denom = d_prev * d_next

    if denom < 1e-12:
        return 0.0

    return (
        d_prev
        +
        d_next
        -
        d_skip
    ) / denom
#complete pipeline of geometric analysis
def compute_quantum_geometry(
    rho_history,
    paulis
):

    entropy_series = []

    bures_series = []

    qfi_series = []

    curvature_series = []

    generator = np.zeros_like(paulis["Z"][0])

    for z in paulis["Z"]:
        generator += z

    # -------------------------
    # Entropy + QFI
    # -------------------------

    for rho in rho_history:

        entropy_series.append(
            von_neumann_entropy(rho)
        )

        qfi_series.append(
            quantum_fisher_information(
                rho,
                generator
            )
        )

    # -------------------------
    # Bures Motion
    # -------------------------

    for i in range(len(rho_history)-1):

        d = bures_distance(
            rho_history[i],
            rho_history[i+1]
        )

        bures_series.append(d)

    bures_series.append(
        bures_series[-1]
    )

    # -------------------------
    # Curvature
    # -------------------------

    curvature_series.append(0)

    for i in range(
        1,
        len(rho_history)-1
    ):

        d_prev = bures_distance(
            rho_history[i-1],
            rho_history[i]
        )

        d_next = bures_distance(
            rho_history[i],
            rho_history[i+1]
        )

        d_skip = bures_distance(
            rho_history[i-1],
            rho_history[i+1]
        )

        curvature_series.append(
            state_space_curvature(
                d_prev,
                d_next,
                d_skip
            )
        )

    curvature_series.append(0)

    return {
        "entropy": np.array(entropy_series),
        "bures": np.array(bures_series),
        "qfi": np.array(qfi_series),
        "curvature": np.array(curvature_series)
    }
