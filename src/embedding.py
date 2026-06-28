import numpy as np
from scipy.signal import argrelmin
from scipy.spatial import cKDTree
from sklearn.preprocessing import StandardScaler
def time_delay_embedding(series, delay, dimension):
    

    series = np.asarray(series)

    n_vectors = len(series) - (dimension - 1) * delay

    if n_vectors <= 0:
        raise ValueError(
            "Time series too short for requested embedding."
        )

    embedded = np.empty((n_vectors, dimension))

    for j in range(dimension):
        embedded[:, j] = series[
            j * delay:
            j * delay + n_vectors
        ]

    return embedded



# AVERAGE MUTUAL INFORMATION


def mutual_information(series, lag, n_bins=32):

    x = series[:-lag]
    y = series[lag:]

    hist_2d, _, _ = np.histogram2d(
        x,
        y,
        bins=n_bins
    )

    pxy = hist_2d / np.sum(hist_2d)

    px = np.sum(pxy, axis=1)
    py = np.sum(pxy, axis=0)

    mi = 0.0

    for i in range(n_bins):
        for j in range(n_bins):

            if (
                pxy[i, j] > 0
                and px[i] > 0
                and py[j] > 0
            ):
                mi += pxy[i, j] * np.log2(
                    pxy[i, j] / (px[i] * py[j])
                )

    return mi


def find_optimal_delay(
    series,
    max_delay=100,
    n_bins=32
):


    mis = []

    for lag in range(1, max_delay + 1):
        mis.append(
            mutual_information(
                series,
                lag,
                n_bins
            )
        )

    mis = np.array(mis)

    minima = argrelmin(mis)[0]

    if len(minima) > 0:
        return minima[0] + 1

    return np.argmin(mis) + 1



# FALSE NEAREST NEIGHBORS


def false_nearest_neighbors(
    series,
    delay,
    dim,
    r_tol=15.0,
    a_tol=2.0,
    theiler_window=None
):
   

    if theiler_window is None:
        theiler_window = delay

    emb_m = time_delay_embedding(
        series,
        delay,
        dim
    )

    emb_m1 = time_delay_embedding(
        series,
        delay,
        dim + 1
    )

    n = len(emb_m1)

    emb_m = emb_m[:n]

    sigma = np.std(series)

    tree = cKDTree(emb_m)

    fnn_count = 0
    valid_count = 0

    for i in range(n):

        k = 20

        dists, idxs = tree.query(
            emb_m[i],
            k=k
        )

        neighbor = None
        dist_m = None

        for dist, idx in zip(dists[1:], idxs[1:]):

            if abs(idx - i) > theiler_window:
                neighbor = idx
                dist_m = dist
                break

        if neighbor is None:
            continue

        if dist_m < 1e-12:
            continue

        valid_count += 1

        extra_coord = abs(
            emb_m1[i, -1]
            -
            emb_m1[neighbor, -1]
        )

        ratio = extra_coord / dist_m

        dist_m1 = np.sqrt(
            dist_m**2 + extra_coord**2
        )

        fnn = (
            ratio > r_tol
            or
            (dist_m1 / sigma) > a_tol
        )

        if fnn:
            fnn_count += 1

    if valid_count == 0:
        return 0.0

    return fnn_count / valid_count


def find_optimal_embedding_dim(
    series,
    delay,
    max_dim=15,
    threshold=0.01
):
    """
    Smallest dimension where
    FNN fraction drops below threshold
    """

    fnn_curve = []

    for dim in range(1, max_dim + 1):

        fnn = false_nearest_neighbors(
            series,
            delay,
            dim
        )

        fnn_curve.append(fnn)

    fnn_curve = np.array(fnn_curve)

    idx = np.where(
        fnn_curve < threshold
    )[0]

    if len(idx) > 0:
        return idx[0] + 1

    return np.argmin(fnn_curve) + 1



# NORMALIZATION FOR QUANTUM ENCODING


def normalize_embedding(embedded):

    scaler = StandardScaler()
    z = scaler.fit_transform(embedded)

    global_min = z.min()
    global_max = z.max()

    z = ((z - global_min) /
         (global_max - global_min + 1e-12))

    z *= np.pi

    return z, scaler



# COMPLETE PHASE SPACE PIPELINE


def reconstruct_phase_space(
    series,
    max_delay=100,
    max_dim=15
):
    

    tau = find_optimal_delay(
        series,
        max_delay=max_delay
    )

    m = find_optimal_embedding_dim(
        series,
        tau,
        max_dim=max_dim
    )

    X = time_delay_embedding(
        series,
        tau,
        m
    )

    X_norm, scaler = normalize_embedding(X)

    return {
        "tau": tau,
        "dimension": m,
        "embedded": X,
        "normalized": X_norm,
        "scaler": scaler
    }
